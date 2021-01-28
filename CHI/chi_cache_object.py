"""
NAME
====
**ccxx.rampage.chi_cache_object** — Модуль упаковки и распаковки данных.

VERSION
=======
0.13.0

SYNOPSIS
========

    from ccxx.rampage.chi_cache_object import CHICacheObject

    chi_object = CHICacheObject(key)

DESCRIPTION
===========
Модуль **ccxx.rampage.chi_cache_object** используется для обёртки данных Rampage в бинарную структуру.

**CHICacheObject** - класс для объектов-обёрток данных. Объект помимо данных содержит время истечения ключа,
информацию о сжатии данных, находятся ли строки их в юникоде и т.д.

CLASSES
=======
"""

import gzip
from datetime import datetime
import random

T_SERIALIZED = 1
T_UTF8_ENCODED = 2
T_COMPRESSED = 4
CHI_MAX_TIME = 0xffffffff


class CHICacheObject:
    """Объект для обёртки данных ключей Rampage."""

    # pylint: disable=too-many-instance-attributes

    def __init__(self, key,
                 value=None,
                 is_compressed=False):
        """Конструктор.

        Args:

        * key (Строка): Ключ хранилища.
        * value (Строка или структура): Данные. Необязательный.
        * is_compressed (Логический): Сжимать данные gzip-ом. Необязательный. По умолчанию: False

        Returns:

            Конструктор в питоне всегда возвращает self.
        """
        self.key = key
        self.value = value
        self.is_transformed = None
        self.is_compressed = is_compressed
        self.is_serialized = False
        self.is_utf8_encoded = False
        self.created_at = None
        self.expires_at = None
        self.early_expires_at = None
        self.is_transformed = None
        self.cache_version = 1

    def is_expired(self):
        """Объект просрочен.

        Returns:

            Метод возвращает истину, если объект просрочен. Логическое.
        """
        today = datetime.today()
        return today >= self.early_expires_at and (
            today >= self.expires_at or (
                random.random() < (today - self.early_expires_at) / (self.expires_at - self.early_expires_at)
            )
        )

    def unpack_from_data(self, data, serializer):
        """Распаковывает бинарные данные и заполняет свои свойства.

        Args:

        * data (Байты): Бинарное представление объекта CHICacheObject.
        * serializer (Объект): Сериализатор для структуры данных.

        Returns:

            Метод возвращает self.
        """
        self.created_at = datetime.fromtimestamp(int.from_bytes(data[0:4], byteorder='little', signed=False))
        self.early_expires_at = datetime.fromtimestamp(int.from_bytes(data[4:8], byteorder='little', signed=False))
        self.expires_at = datetime.fromtimestamp(int.from_bytes(data[8:12], byteorder='little', signed=False))
        self.is_transformed = int.from_bytes(data[12:13], byteorder='little', signed=False)
        self.cache_version = int.from_bytes(data[13:14], byteorder='little', signed=False)

        self.is_compressed = bool(self.is_transformed & T_COMPRESSED)
        self.is_serialized = bool(self.is_transformed & T_SERIALIZED)
        self.is_utf8_encoded = bool(self.is_transformed & T_UTF8_ENCODED)

        value = data[14:]

        if self.is_compressed:
            value = gzip.decompress(value)

        if self.is_serialized:
            value = serializer.loads(value)
        elif self.is_utf8_encoded:
            value = str(value, encoding='utf8')

        self.value = value

        return self

    def pack_to_data(self, expires_in, early_expires_in, expires_variance, serializer, compress, compress_threshold):
        """Пакует данные в объект.

        Args:

        * expires_in (Целое): Время жизни ключа в секундах по умолчанию.
        * early_expires_in (Целое): Интервал в секундах преждевременного истечения срока жизни ключа.
        * expires_variance (Вещественное): Коеффициент преждевременного истечения срока жизни ключа.
            Служит для расчёта early_expires_in если тот не указан. Число от 0 до 1.
        * compress (Логическое): Сжимать данные gzip-ом.
        * serializer (Объект): Сериализатор данных.
        * compress_threshold (Целое): Максимальная длина данных в байтах после которой будет происходить сжатие gzip-ом.

        Returns:

            Метод возвращает бинарное представление себя для хранилища. Байты.
        """
        value = self.value
        self.is_transformed = 0

        if type(value) == bytes:
            pass
        elif type(value) == str:
            value = value.encode('utf8')
            self.is_utf8_encoded = True
            self.is_transformed |= T_UTF8_ENCODED
        else:
            value = serializer.dumps(value)
            value = value.encode('utf8')
            self.is_serialized = True
            self.is_transformed |= T_SERIALIZED

        if compress is None and len(value)>compress_threshold or compress is True:
            value = gzip.compress(value)
            self.is_compressed = True
            self.is_transformed |= T_COMPRESSED

        self.created_at = datetime.today()
        today = int(self.created_at.timestamp())
        chi_max_time = datetime.fromtimestamp(CHI_MAX_TIME)
        self.expires_at = chi_max_time if expires_in == CHI_MAX_TIME else datetime.fromtimestamp(today + expires_in)

        if early_expires_in is not None and CHI_MAX_TIME == early_expires_in \
                or early_expires_in is None and expires_in == CHI_MAX_TIME:
            self.early_expires_at = chi_max_time
        elif early_expires_in is None:
            expires_at = int(self.expires_at.timestamp())
            self.early_expires_at = datetime.fromtimestamp(expires_at - (expires_at - today) * expires_variance)
        else:
            self.early_expires_at = datetime.fromtimestamp(today + early_expires_in)

        return b"".join([
            int(self.created_at.timestamp()).to_bytes(4, byteorder="little", signed=False),
            int(self.early_expires_at.timestamp()).to_bytes(4, byteorder="little", signed=False),
            int(self.expires_at.timestamp()).to_bytes(4, byteorder="little", signed=False),
            self.is_transformed.to_bytes(1, byteorder="little", signed=False),
            self.cache_version.to_bytes(1, byteorder="little", signed=False),
            value,
        ])
