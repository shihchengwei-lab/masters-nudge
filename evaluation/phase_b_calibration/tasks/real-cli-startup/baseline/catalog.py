import time


time.sleep(0.22)


def build_catalog():
    return {"alpha": 5, "beta": 4}


def lookup(name):
    return build_catalog()[name]
