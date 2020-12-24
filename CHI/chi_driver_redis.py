"""
    Чи-Драйвер редиса
"""

from redis import Redis


from CHI.chi_driver import CHIDriver

class CHIDriverRedis(CHIDriver):
    """Драйвер RedisCluster."""

    def __init__(self, *av, **kw):
        """Конструктор."""
        super().__init__(*av, **kw)

        self.client = Redis(host=self.server[0]["host"], port=self.server[0]["port"])