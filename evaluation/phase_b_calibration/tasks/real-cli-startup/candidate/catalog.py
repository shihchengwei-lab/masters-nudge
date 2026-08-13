import time
from functools import lru_cache


time.sleep(0.22)


@lru_cache(maxsize=1)
def build_catalog():
    return {"alpha": 5, "beta": 4}


def lookup(name):
    return build_catalog()[name]
