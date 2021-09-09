"""
    Утилиты
"""

import re

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
    return mask.replace("?", "*").replace("**", "*"), regex
