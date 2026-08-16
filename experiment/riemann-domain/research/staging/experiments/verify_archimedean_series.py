#!/usr/bin/env python3
"""Offline diagnostic for D3/D5 Archimedean identities and bounds."""

from __future__ import annotations

import math
import mpmath as mp


def finite_formula(n: int) -> mp.mpf:
    return (
        1
        - mp.mpf(n) * (mp.euler + mp.log(4 * mp.pi)) / 2
        + mp.fsum(
            math.comb(n, k) * (-1) ** k * (1 - mp.power(2, -k)) * mp.zeta(k)
            for k in range(2, n + 1)
        )
    )


def odd_series(n: int, cutoff: int) -> tuple[mp.mpf, mp.mpf]:
    total = 1 - mp.mpf(n) * (mp.euler + mp.log(4 * mp.pi)) / 2
    for m in range(1, cutoff + 1, 2):
        total += mp.power(1 - mp.mpf(1) / m, n) - 1 + mp.mpf(n) / m
    # For m>cutoff, each term is <= n(n-1)/(2m^2). Bound all integers,
    # which safely dominates the odd-only tail.
    tail_bound = mp.mpf(n * (n - 1)) / (2 * cutoff)
    return total, tail_bound


def lower_bound(n: int) -> mp.mpf:
    return mp.mpf(n) / 2 * (
        mp.log(n + 1) - 1 - mp.euler - mp.log(4 * mp.pi)
    ) + mp.mpf("0.5")


def main() -> None:
    # The finite binomial form contains cancellation on an approximately 2^n
    # scale.  Use enough guard digits for the n=300 diagnostic.
    mp.mp.dps = 180
    print("DIAGNOSTIC ONLY: finite checks do not prove the asymptotic theorem")
    print("n,A_n,series_error,tail_bound,proved_lower_bound,A/(0.5*n*log(n))")
    for n in (1, 2, 5, 10, 30, 100, 300):
        exact = finite_formula(n)
        partial, tail_bound = odd_series(n, 200_001)
        error = exact - partial
        ratio = exact / (mp.mpf(n) * mp.log(n) / 2) if n > 1 else mp.nan
        print(
            f"{n},{mp.nstr(exact,16)},{mp.nstr(error,8)},"
            f"{mp.nstr(tail_bound,8)},{mp.nstr(lower_bound(n),12)},"
            f"{mp.nstr(ratio,10)}"
        )
        if error < -mp.mpf("1e-60") or error > tail_bound:
            raise SystemExit("odd-series tail check failed")
        if exact + mp.mpf("1e-60") < lower_bound(n):
            raise SystemExit("D3 lower bound check failed")


if __name__ == "__main__":
    main()
