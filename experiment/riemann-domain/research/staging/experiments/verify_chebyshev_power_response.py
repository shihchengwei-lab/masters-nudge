#!/usr/bin/env python3
"""Offline QA for the exact Laguerre response to A(x)=x^theta."""

from __future__ import annotations

import math
import mpmath as mp


def laguerre2(n_minus_1: int, t: mp.mpf) -> mp.mpf:
    n = n_minus_1 + 1
    return mp.fsum(
        math.comb(n + 1, j + 2) * (-t) ** j / mp.factorial(j)
        for j in range(n)
    )


def closed(n: int, theta: mp.mpf) -> mp.mpf:
    return theta + (1 - theta) * (-theta / (1 - theta)) ** (n + 1)


def quadrature(n: int, theta: mp.mpf) -> mp.mpf:
    a = 1 - theta
    return -n + mp.quad(lambda t: mp.exp(-a * t) * laguerre2(n - 1, t), [0, mp.inf])


def main() -> None:
    mp.mp.dps = 60
    print("DIAGNOSTIC ONLY: the power-response identity is proved by generating functions")
    print("theta,n,quadrature,closed,error")
    maximum = mp.mpf(0)
    for theta in map(mp.mpf, ("0.25", "0.5", "0.6", "0.75")):
        for n in (1, 2, 5, 10):
            q = quadrature(n, theta)
            c = closed(n, theta)
            error = abs(q - c)
            maximum = max(maximum, error)
            print(f"{theta},{n},{mp.nstr(q,15)},{mp.nstr(c,15)},{mp.nstr(error,5)}")
    print(f"maximum error={mp.nstr(maximum,8)}")
    if maximum > mp.mpf("1e-45"):
        raise SystemExit("power-response QA exceeded tolerance")


if __name__ == "__main__":
    main()

