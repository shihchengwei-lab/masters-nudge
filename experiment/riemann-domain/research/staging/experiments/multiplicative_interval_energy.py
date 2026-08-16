#!/usr/bin/env python3
"""Offline finite-range QA for the S4 multiplicative-interval energy."""

from __future__ import annotations

import math


def mangoldt(limit: int) -> list[float]:
    result = [0.0] * (limit + 1)
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, limit + 1):
        if sieve[p]:
            lp = math.log(p)
            power = p
            while power <= limit:
                result[power] = lp
                if power > limit // p:
                    break
                power *= p
            if p * p <= limit:
                sieve[p * p : limit + 1 : p] = b"\x00" * (((limit - p * p) // p) + 1)
    return result


def main() -> None:
    limit = 1_000_000
    lam = mangoldt(limit)
    prefix = [0.0] * (limit + 1)
    psi = 0.0
    for k in range(1, limit + 1):
        psi += lam[k]
        prefix[k] = psi - k

    s_energy = 0.0
    d_energy = 0.0
    checkpoints = {2**j for j in range(10, 20)} | {limit}
    print("DIAGNOSTIC ONLY: finite prime data cannot prove the asymptotic bound or RH")
    print("N,S_N,D_N,D/S,S/(N^2 log^4N),D/(N^2 log^4N)")
    for k in range(1, limit + 1):
        b = prefix[k]
        delta = b - prefix[k // 2]
        s_energy += b * b
        d_energy += delta * delta
        if k in checkpoints:
            scale = k * k * math.log(k) ** 4
            print(
                f"{k},{s_energy:.12g},{d_energy:.12g},{d_energy/s_energy:.9g},"
                f"{s_energy/scale:.12g},{d_energy/scale:.12g}"
            )


if __name__ == "__main__":
    main()

