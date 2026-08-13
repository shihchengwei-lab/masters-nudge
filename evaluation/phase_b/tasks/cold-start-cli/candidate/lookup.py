import time
from functools import lru_cache

time.sleep(0.25)


@lru_cache(maxsize=1)
def build_lookup():
    return {"alpha": 5, "beta": 4, "gamma": 5}


LOOKUP = build_lookup()
