from .exception import *
from .chi_cache_object import CHI_MAX_TIME

import importlib


def CHI(server, driver="redis-cluster", **kw):
    """Служит для загрузки драйвера."""
    driver = driver.replace("-", "_")
    driver_path = "CHI.chi_driver_" + driver
    driver_module = importlib.import_module(driver_path)
    class_name = "CHIDriver" + "".join([s[0].upper() + s[1:] for s in driver.split("_")])
    driver_class = getattr(driver_module, class_name)
    return driver_class(server, **kw)
