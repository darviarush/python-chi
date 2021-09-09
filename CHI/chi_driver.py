"""
    Базовый драйвер
"""

import json, re
from CHI.chi_cache_object import CHICacheObject
from .chi_util import mask_to_regex


class CHIDriver:
    """Базовый класс драйверов."""

    def __init__(self,
                 server,
                 expires_in=60,
                 early_expires_in=None,
                 expires_variance=0.5,
                 compress_threshold=1024*64,
                 connect_timeout=1,
                 request_timeout=10,
                 strategy_of_erase='lua',
                 serializer=json,
                 ):
        """Конструктор.

        Args:

        * server (Список словарей): Список серверов кластера redis в виде {"host": "хост", "port": "порт"}.
        * expires_in (Целое): Время жизни ключа в секундах.
        * early_expires_in (Целое): Интервал в секундах преждевременного истечения срока жизни ключа. Необязательный.
        * expires_variance (Вещественное от 0 до 1): Коеффициент преждевременного истечения срока жизни ключа.
            Служит для расчёта early_expires_in если тот не указан.
            Необязательный. По умолчанию: 0.5.
        * connect_timeout (Целое): Таймаут коннекта к хранилищу в секундах. Необязательный. По умолчанию: 1.
        * request_timeout (Целое): Таймаут запроса к хранилищу в секундах. Необязательный. По умолчанию: 10.
        * strategy_of_erase (Одно из: 'lua' или 'keys'): Стратегия удаления объектов. Необязательный.
            По умолчанию: 'lua'.

        Для предотвращения конкуренции за ресурсы, когда ключ истекает и несколько запросивших его процессов начинают
        одновременно генерировать для него данные, CHI обманыевает один из процессов, что ключ уже удалён. Тогда
        обманутый процесс сможет сгенерировать данные и поместить их в ключ прежде, чем ключ реально будет удалён.
        Обман произойдёт в интервале от `early_expires_in` до `expires_in`.

        `early_expires_in` рассчитывается как `expires_in * (1 - expires_variance)`. Поэтому если `expires_variance=1`,
        то обман может произойти на протяжении всей жизни ключа, а `expires_variance=0` отменяет борьбу с конкуренцией
        за ресурсы.

        Returns:

            Конструктор в питоне всегда возвращает self.
        """

        server = [dict(host=s.split(":")[0], port=int(s.split(":")[1])) for s in server.split(",")]

        self.server = server
        self.compress_threshold = compress_threshold
        self.connect_timeout = connect_timeout
        self.request_timeout = request_timeout
        self.serializer = serializer
        self.expires_in = expires_in
        self.early_expires_in = early_expires_in
        self.expires_variance = expires_variance
        self.strategy_of_erase = strategy_of_erase

    def get_object(self, key):
        """Возвращает объект CHICacheObject из хранилища."""
        reply = self.client.get(key)

        if reply is None:
            return None

        chi_object = CHICacheObject(key).unpack_from_data(reply, self.serializer)

        if chi_object.is_expired():
            return None

        return chi_object

    def get(self, key, builder=None, ttl=None, compress=None):
        """Возвращает данные из хранилища."""
        chi_object = self.get_object(key)

        if chi_object is None and builder:
            chi_object = self.set_object(key, builder(), ttl, compress)

        if chi_object is None:
            return None

        return chi_object.value

    def set_object(self, key, data, ttl=None, compress=None):
        """Устанавливает данные в хранилище."""

        expires_in = self.expires_in if ttl is None else ttl

        chi_object = CHICacheObject(key, value=data)
        packed_chi_object = chi_object.pack_to_data(
            expires_in=expires_in,
            early_expires_in=self.early_expires_in,
            expires_variance=self.expires_variance,
            serializer=self.serializer,
            compress=compress,
            compress_threshold=self.compress_threshold,
        )
        self.driver_set(key, packed_chi_object, expires_in)
        return chi_object

    def driver_set(self, key, packed_chi_object, ttl):
        self.client.set(key, packed_chi_object)
        self.client.expire(key, ttl)

    def set(self, key, data, ttl=None, compress=None):
        """Устанавливает данные в хранилище."""
        self.set_object(key, data, ttl, compress)
        return self

    def remove(self, key):
        """Удаляет ключ из хранилища."""
        self.client.delete(key)
        return self

    def keys(self, mask):
        """Возвращает ключи по маске."""
        mask, regex = mask_to_regex(mask)

        regex = re.compile(regex, re.S)
        keys = []
        for key in self.client.keys(mask):
            key = key.decode('utf-8')
            if regex.match(key):
                keys.append(key)
        return keys

    def erase(self, mask):
        """Удаление ключей по маске."""
        counter = 0
        for key in self.keys(mask):
            self.remove(key)
            counter += 1
        return counter

