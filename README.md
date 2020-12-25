# chi

# NAME

chi - Унифицированный интерфейс обработки кэша

# VERSION

0.1.0

# DESCRIPTION

```python
from chi import CHI

chi = CHI(
	server="127.0.0.1:7001,127.0.0.1:7002,127.0.0.1:7003", 
	driver='redis_cluster',

)

chi.set("k1", "Привет Мир!", ttl=10)

print(chi.get("k1"))	# -> "Привет Мир!"

print(chi.keys("k*"))	# -> ["k1"]

print(chi.erase("k*"))	# -> 1

chi.remove("k1")

```

# SYNOPSIS

В языке perl есть унифицированный интерфейс обработки кэша. Он реализуется модулем https://metacpan.org/pod/CHI.

Данные ключа запаковываются в бинарную структуру определённого формата и даже могут сжиматься gzip-ом.

Аргументы конструктора `CHI(...)`:

- server - адрес сервера или серверов (`для redis-cluster`). Адрес имеет формат: `"хост1:порт1,хост2:порт2..."`;
- driver="redis-cluster" - часть имени модуля, который будет подгружен. Дополняется так: `"CHI.chi_driver_" + driver.replace("-", "_")`. В текущем пакете есть `redis-cluster`, `redis` и `memcache`;
- expires_in=60 - время жизни ключа в секундах;
- early_expires_in=None - интервал в секундах преждевременного истечения срока жизни ключа. Для отключения используется константа `from CHI import CHI_MAX_TIME`;
- expires_variance=0.5 - (от 0 до 1): коеффициент преждевременного истечения срока жизни ключа;
            Служит для расчёта early_expires_in если тот не указан;
- compress_threshold= - сжимать данные если они больше этого числа байт;
- connect_timeout=1 - таймаут коннекта к хранилищу в секундах;
- request_timeout=10 - таймаут запроса к хранилищу в секундах;
- strategy_of_erase='lua' - стратегия удаления для метода `erase(mask)` (только для `redis-cluster`). Значения: `lua` - рассылает на все ноды кластера скрипт на lua, который удаляет ключи. И `keys` - получает ключи по маске, а затем - удаляет.


Для предотвращения конкуренции за ресурсы, когда ключ истекает и несколько запросивших его процессов начинают
одновременно генерировать для него данные, CHI обманыевает один из процессов, что ключ уже удалён. Тогда
обманутый процесс сможет сгенерировать данные и поместить их в ключ прежде, чем ключ реально будет удалён.
Обман произойдёт в интервале от `early_expires_in` до `expires_in`.

`early_expires_in` рассчитывается как `expires_in * (1 - expires_variance)`. Поэтому если `expires_variance=1`,
то обман может произойти на протяжении всей жизни ключа, а `expires_variance=0` отменяет борьбу с конкуренцией
за ресурсы.

Методы:

- `get(key, builder=None, ttl=None)` - получить данные. builder - функция для создания ключа, если ключ не найден. ttl - время жизни ключа в секундах, если не указан, то используется self.expires_in;
- `get_object(key, builder=None, ttl=30)` - получить объект `CHI.chi_cache_object.CHICacheObject`;
- `set(key, data, ttl=None, compress=None)` - установить данные. compress - сжать их gzip-ом, если не указан - берётся `self.compress_threshold`;
- `set_object(key, data, ttl=None, compress=None)` - установить данные и вернуть объект чи сформированный для установки;
- `remove(key)` - удалить ключ;
- `keys(mask)` - получить ключи соответствующие маске (`*` - ноль или более символов);
- `erase(mask)` - удалить ключи соответствующие маске.

# SCRIPT

```sh

# Помещаем в ключ t:k1 структуру python. Данные сжимать gzip-ом. Время жизни ключа - 30 секунд
$ chi -S 127.0.0.1:7001,127.0.0.1:7002,127.0.0.1:7003 set t:k1 -с '{"x": 6}' -z -t 30

# В кластер можно передавать только адрес одной ноды. Так же укажем драйвер явно
$ chi -S 127.0.0.1:7001 -D redis_cluster get t:k1
{
	"x": 6
}

# Информацию об остальных командах можно получить так:
$ chi --help
$ chi <команда> --help

```

# INSTALL

```sh
$ pip install chi
```

# REQUIREMENTS

* argparse
* data-printer
* json
* gzip
* redis-py-cluster
* redis
* pymemcache

# LICENSE

Copyright (C) Yaroslav O. Kosmina.

This library is free software; you can redistribute it and/or modify
it under the same terms as Python itself.

# AUTHOR

Yaroslav O. Kosmina <darviarush@mail.ru>

# LICENSE

MIT License

Copyright (c) 2020 Yaroslav O. Kosmina

