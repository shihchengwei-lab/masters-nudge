import contextlib
import io
import time

import tool


def warm_samples(count=20):
    samples = []
    for _ in range(count):
        output = io.StringIO()
        started = time.perf_counter()
        with contextlib.redirect_stdout(output):
            tool.main(["--version"])
        samples.append((time.perf_counter() - started) * 1000)
    return samples
