"""
    Утилиты
"""

import re

def mask_to_regex(mask):
    """Переводит маску в регулярное выражение.

    Args:

    * mask (Строка): маска с *.

    Returns:

        Регулярное выражение. Строка.
    """
    regex = re.escape(mask)
    regex = regex.replace("\\*", "[^:]*")
    regex = f"^{regex}$"
    return regex
