"""
NAME
====
**CHI.exception** — Исключения CHI.

SYNOPSIS
========

    from CHI.exception import CHIStrategyOfEraseException

    try:
        ...
    except CHIEraseStrategyException as e:
        ...

DESCRIPTION
===========
Модуль **CHI.exception** содержит исключения CHI.

CLASSES
=======
"""


class CHIException(Exception):
    """Базовое исключение CHI."""
    pass


class CHIStrategyOfEraseException(CHIException):
    """Исключение: нет такой стратегии."""
    pass

class CHIMethodIsNotSupportedException(CHIException):
    """Исключение: метод не поддерживается."""
    pass
