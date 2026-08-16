#!/usr/bin/env python3
"""Offline finite-cutoff QA for the shifted Abel–prime–Laguerre identity."""

from __future__ import annotations

import math
import mpmath as mp


def von_mangoldt_table(limit: int) -> list[float]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, int(limit**0.5) + 1):
        if sieve[p]:
            sieve[p * p : limit + 1 : p] = b"\x00" * (((limit - p * p) // p) + 1)
    values = [0.0] * (limit + 1)
    for p in range(2, limit + 1):
        if sieve[p]:
            power = p
            lp = math.log(p)
            while power <= limit:
                values[power] = lp
                if power > limit // p:
                    break
                power *= p
    return values


def laguerre1(n_minus_1: int, x: mp.mpf) -> mp.mpf:
    n = n_minus_1 + 1
    return mp.fsum(
        math.comb(n, j + 1) * (-x) ** j / mp.factorial(j)
        for j in range(n)
    )


def direct_shifted(n: int, delta: mp.mpf) -> mp.mpf:
    def h(s: mp.mpf) -> mp.mpf:
        return 1 / (s - 1) + mp.diff(mp.zeta, s) / mp.zeta(s)

    s = 1 + delta
    return mp.fsum(
        math.comb(n, k) * mp.diff(h, s, k - 1) / mp.factorial(k - 1)
        for k in range(1, n + 1)
    )


def tail_bound(n: int, delta: mp.mpf, cutoff: int) -> mp.mpf:
    # Lambda(m)<=log(m), and at this cutoff all powers below are decreasing.
    total = mp.mpf(0)
    logx = mp.log(cutoff)
    for j in range(n):
        coefficient = mp.mpf(math.comb(n, j + 1)) / mp.factorial(j)
        power = j + 1
        integral = mp.gammainc(power + 1, delta * logx, mp.inf) / delta ** (power + 1)
        first = logx**power / mp.mpf(cutoff) ** (1 + delta)
        total += coefficient * (integral + first)
    return total


def main() -> None:
    mp.mp.dps = 60
    cutoff = 200_000
    mangoldt = von_mangoldt_table(cutoff)
    print("DIAGNOSTIC ONLY: finite-cutoff QA; the D7 proof is analytic")
    print("delta,n,direct,truncated,residual,rigorous_tail_bound")
    for delta in (mp.mpf(1), mp.mpf(2)):
        for n in range(1, 5):
            prime_sum = mp.fsum(
                mangoldt[m]
                * mp.mpf(m) ** (-1 - delta)
                * laguerre1(n - 1, mp.log(m))
                for m in range(2, cutoff + 1)
                if mangoldt[m]
            )
            truncated = 1 - (1 - 1 / delta) ** n - prime_sum
            direct = direct_shifted(n, delta)
            residual = abs(direct - truncated)
            bound = tail_bound(n, delta, cutoff)
            print(
                f"{delta},{n},{mp.nstr(direct,15)},{mp.nstr(truncated,15)},"
                f"{mp.nstr(residual,8)},{mp.nstr(bound,8)}"
            )
            if residual > bound * mp.mpf("1.000001"):
                raise SystemExit("prime tail exceeded the analytic bound")


if __name__ == "__main__":
    main()

