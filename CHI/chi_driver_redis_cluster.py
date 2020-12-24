"""
    Предоставляет низкоуровневые методы для доступа к хранилищу Redis Cluster
"""

from rediscluster import RedisCluster

from .chi_driver import CHIDriver
from .exception import CHIStrategyOfEraseException
from .chi_util import mask_to_regex


LUA_ERASE_ON_ONE_NODE = """
local ext_mask = ARGV[1]
local regex = ARGV[2]
local keys = redis.call("keys", ext_mask)
local count = 0
local skeys = {}

for i=1, #keys do
    local key = keys[i]
    if key:find(regex) then
        redis.call("del", key)
        count = count + 1
    end
end
return count
"""


class CHIDriverRedisCluster(CHIDriver):
    """Драйвер RedisCluster."""

    def __init__(self, *av, **kw):
        """Конструктор."""
        super().__init__(*av, **kw)

        if self.strategy_of_erase == "lua":
            setattr(self, "erase", self.erase_by_lua_on_all_nodes)
        elif self.strategy_of_erase == "keys":
            pass
        else:
            raise CHIStrategyOfEraseException(f"Недействительная стратегия удаления \"{self.strategy_of_erase}\".")

        self.client = RedisCluster(
            startup_nodes=self.server,
            decode_responses=False,
            socket_connect_timeout=self.connect_timeout,
        )

    def run(self, *av, server_type="slave"):
        """Выполняет команду на каждом слейве."""
        result = []
        for _, node in self.client.connection_pool.nodes.nodes.items():
            if node['server_type'] == server_type:
                connection = self.client.connection_pool.get_connection_by_node(node)
                connection.send_command(*av)
                result.append(self.client.parse_response(connection, av[0]))
        return result

    def keys(self, key):
        """Возвращает ключи по маске."""
        result = []
        for src_keys in self.run("keys", key):
            result += src_keys
        return result

    def erase_by_lua_on_all_nodes(self, mask):
        """Отправляет на каждую ноду кластера lua-скрипт, который затем удаляет подходящие ключи на ноде."""
        regex = mask_to_regex(mask)
        # В регулярках lua вместо бэкслешей используется процент перед управляющими символами.
        regex = regex.replace("\\", "%")
        regex = regex.replace("(?s::.*)?", ".*")

        result = self.run("eval", LUA_ERASE_ON_ONE_NODE, 0, f"{mask}*", regex, server_type="master")
        return sum(result)
