import subprocess
import sys
import time
from pathlib import Path


def fresh_samples(count=5):
    script = Path(__file__).with_name("tool.py")
    samples = []
    for _ in range(count):
        started = time.perf_counter()
        subprocess.run(
            [sys.executable, str(script), "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        samples.append((time.perf_counter() - started) * 1000)
    return samples
