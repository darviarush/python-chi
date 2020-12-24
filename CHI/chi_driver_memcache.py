"""
    Чи-Драйвер редиса
"""

from pymemcache.client import base
from .chi_driver import CHIDriver
from .excheption import CHIMethodIsNotSupportedException

class CHIDriverMemcache(CHIDriver):
    """Драйвер Memcache."""

    def __init__(self, *av, **kw):
    	"""Конструктор."""
        super().__init__(*av, **kw)

        self.client = base.Client((self.server[0]["host"], self.server[0]["port"]))

    def driver_set(self, key, packed_chi_object, ttl):
    	"""Переопределение для установки драйвера - в редисе используются две команды, а тут - одна."""
        self.client.set(key, packed_chi_object, ttl)

    def keys(self, mask):
        """Возвращает ключи по маске."""
        raise CHIMethodIsNotSupportedException("Метод keys для мемкеша не поддерживается.")

    def erase(self, mask):
        """Удаление ключей по маске."""
		raise CHIMethodIsNotSupportedException("Метод erase для мемкеша не поддерживается.")