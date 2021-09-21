"""
    Утилиты
"""

import re


RE_QUESTION = re.compile(r'.\?', re.S)
RE_ONCE = re.compile(r'\*{2,}')


def mask_to_regex(mask):
    """Переводит маску в регулярное выражение.

    Маска может иметь специальные символы:
    
    * * - заменяет регулярку [^:]*.
    * ** - все символы.
    * символ? - этот символ может быть, а может и нет.

    Args:

    * mask (Строка): маска с * и **.

    Returns:

        Регулярное выражение. Строка.
    """
    regex = re.escape(mask)
    regex = regex.replace("\\*\\*", ".*")
    regex = regex.replace("\\*", "[^:]*")
    regex = regex.replace("\\?", "?")
    regex = f"^{regex}$"
    
    mask = RE_QUESTION.sub('*', mask)
    mask = RE_ONCE.sub('*', mask)
    return mask, regex


def redis_mask_to_regex(mask):
    """Для тестов переводит маску редиса в регулярку
    Замена не полная - только для звёздочки
    """
    regex = re.sub(r'\*', '.*', mask)
    return f"^{regex}$"

    
def mask_to_redis_regex(mask):
    """Для тестов переводит маску редиса в регулярку
    Замена не полная - только для звёздочки
    """
    mask, _ = mask_to_regex(mask)
    return redis_mask_to_regex(mask)
