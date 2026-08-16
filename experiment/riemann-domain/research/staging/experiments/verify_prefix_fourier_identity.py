#!/usr/bin/env python3
"""Offline finite-dimensional QA for the M7 Fourier identity."""

from __future__ import annotations

import cmath
import math


def mangoldt(limit: int) -> list[float]:
    values = [0.0] * (limit + 1)
    sieve = [True] * (limit + 1)
    sieve[0:2] = [False, False]
    for p in range(2, limit + 1):
        if sieve[p]:
            lp = math.log(p)
            power = p
            while power <= limit:
                values[power] = lp
                if power > limit // p:
                    break
                power *= p
            if p * p <= limit:
                for q in range(p * p, limit + 1, p):
                    sieve[q] = False
    return values


def main() -> None:
    n = 256
    grid = 2048
    lam = mangoldt(n)
    b = [0.0] + [lam[m] - 1.0 for m in range(1, n)]
    prefix = []
    running = 0.0
    for m in range(1, n):
        running += b[m]
        prefix.append(running)
    direct = sum(value * value for value in prefix)
    spectral = 0.0
    maximum_factorization_error = 0.0
    for j in range(grid):
        z = cmath.exp(2j * math.pi * j / grid)
        f = sum(prefix[k - 1] * z**k for k in range(1, n))
        s = sum(b[m] * z**m for m in range(1, n))
        p = s - prefix[-1] * z**n
        maximum_factorization_error = max(
            maximum_factorization_error, abs((1 - z) * f - p)
        )
        spectral += abs(f) ** 2
    spectral /= grid
    print("DIAGNOSTIC ONLY: finite polynomial Parseval check; not evidence for RH")
    print(f"N={n}, direct_prefix_energy={direct:.15g}")
    print(f"spectral_grid_average={spectral:.15g}")
    print(f"relative_Parseval_error={abs(spectral-direct)/max(1,direct):.3e}")
    print(f"maximum_factorization_error={maximum_factorization_error:.3e}")
    if abs(spectral - direct) > 1e-10 * max(1.0, direct):
        raise SystemExit("Parseval QA failed")
    if maximum_factorization_error > 1e-9:
        raise SystemExit("polynomial factorization QA failed")


if __name__ == "__main__":
    main()

