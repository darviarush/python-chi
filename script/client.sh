#!/bin/bash

# Тестирование реальных сервисов

server=127.0.0.1:11211
driver=memcache

x_chi() {
	PYTHONPATH=. bin/chi -D $driver -S $server $*
}


x_chi set t:k1 -d Привет!

x_chi get t:k1

x_chi keys "t:*"

x_chi erase "t:*"

echo "Ключ удалён"
x_chi get t:k1

x_chi remove t:k1

x_chi get t:k1
