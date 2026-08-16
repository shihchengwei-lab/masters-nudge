#!/usr/bin/env python3
"""Offline scaling diagnostic for the nonnegative PNT-like countermodel."""

from __future__ import annotations

import math


def short_energy(n: int, h: int, theta: float) -> float:
    return sum(((k + h) ** theta - k**theta) ** 2 for k in range(1, n - h + 1))


def main() -> None:
    theta = 0.75
    print("DIAGNOSTIC ONLY: abstract countermodel scaling; not data about zeta zeros")
    print("N,alpha,h,J,J/(h^2*N^(2theta-1)),J/(h*N)")
    for n in (10_000, 100_000, 1_000_000):
        for alpha in (0.25, 0.50, 0.75):
            h = max(1, int(n**alpha))
            value = short_energy(n, h, theta)
            asymptotic_scale = h * h * n ** (2 * theta - 1)
            print(
                f"{n},{alpha:.2f},{h},{value:.12g},"
                f"{value/asymptotic_scale:.9g},{value/(h*n):.9g}"
            )

    # Exact telescoping/PNT-like checks for the nonnegative weights.
    n = 1_000_000
    minimum_weight = min(
        1 - (k**theta - (k - 1) ** theta) for k in range(1, 10_001)
    )
    centered_prefix = -n**theta
    coefficient_energy = sum(
        (k**theta - (k - 1) ** theta) ** 2 for k in range(1, n + 1)
    )
    prefix_energy = sum(k ** (2 * theta) for k in range(1, n + 1))
    print(f"minimum first-10000 weight={minimum_weight:.12g}")
    print(f"centered prefix at N={n}: {centered_prefix:.12g}")
    print(f"coefficient energy={coefficient_energy:.12g}")
    print(f"prefix energy={prefix_energy:.12g}")
    if minimum_weight < -1e-15:
        raise SystemExit("countermodel lost nonnegativity")


if __name__ == "__main__":
    main()

