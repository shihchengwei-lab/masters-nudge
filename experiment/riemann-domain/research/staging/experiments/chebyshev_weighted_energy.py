#!/usr/bin/env python3
"""Offline finite-range diagnostic for the weighted Chebyshev energy.

The midpoint quadrature and finite cutoff do not establish convergence.
"""

from __future__ import annotations

import math


def mangoldt(limit: int) -> list[float]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, int(limit**0.5) + 1):
        if sieve[p]:
            sieve[p * p : limit + 1 : p] = b"\x00" * (((limit - p * p) // p) + 1)
    result = [0.0] * (limit + 1)
    for p in range(2, limit + 1):
        if sieve[p]:
            lp = math.log(p)
            power = p
            while power <= limit:
                result[power] = lp
                if power > limit // p:
                    break
                power *= p
    return result


def main() -> None:
    limit = 1_000_000
    weights = mangoldt(limit)
    psi = 0.0
    block_start = 2
    block_energy = 0.0
    cumulative = 0.0
    exact_mean_square = 0.0
    print("DIAGNOSTIC ONLY: finite midpoint quadrature cannot prove convergence or RH")
    print("block_start,block_end,weighted_energy,cumulative,exact_M,M/(X^2 log(X)^4)")
    for m in range(2, limit):
        psi += weights[m]
        x = m + 0.5
        error = psi - x
        term = error * error / (x * x * math.log(x) ** 6)
        block_energy += term
        centered = psi - m - 0.5
        exact_mean_square += centered * centered + 1.0 / 12.0
        if m + 1 == min(2 * block_start, limit):
            cumulative += block_energy
            end = m + 1
            normalized = exact_mean_square / (end * end * math.log(end) ** 4)
            print(
                f"{block_start},{end},{block_energy:.12g},{cumulative:.12g},"
                f"{exact_mean_square:.12g},{normalized:.12g}"
            )
            block_start *= 2
            block_energy = 0.0
    if block_energy:
        cumulative += block_energy
        normalized = exact_mean_square / (limit * limit * math.log(limit) ** 4)
        print(
            f"{block_start},{limit},{block_energy:.12g},{cumulative:.12g},"
            f"{exact_mean_square:.12g},{normalized:.12g}"
        )


if __name__ == "__main__":
    main()
