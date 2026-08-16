#!/usr/bin/env python3
"""Offline high-precision diagnostic for the exact Li decomposition.

The output checks algebra and cancellation only. Finite computed positivity is
not evidence for RH.
"""

from __future__ import annotations

import argparse
import math
import mpmath as mp


def eta_coefficients(count: int) -> list[mp.mpf]:
    # A(x)=x*zeta(1+x)=1+sum_{k>=1} a[k] x^k.
    a = [mp.mpf(1)] + [
        (-1) ** (k - 1) * mp.stieltjes(k - 1) / mp.factorial(k - 1)
        for k in range(1, count + 1)
    ]
    b = [mp.mpf(0)] * (count + 1)
    for k in range(1, count + 1):
        correction = mp.fsum(j * b[j] * a[k - j] for j in range(1, k))
        b[k] = a[k] - correction / k
    return [k * b[k] for k in range(1, count + 1)]


def components(n: int, eta: list[mp.mpf]) -> tuple[mp.mpf, mp.mpf, mp.mpf]:
    base = 1 - mp.mpf(n) * (mp.euler + mp.log(4 * mp.pi)) / 2
    gamma_sum = mp.fsum(
        math.comb(n, k) * (-1) ** k * (1 - mp.power(2, -k)) * mp.zeta(k)
        for k in range(2, n + 1)
    )
    eta_sum = mp.fsum(math.comb(n, k) * eta[k - 1] for k in range(1, n + 1))
    return base, gamma_sum, eta_sum


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--dps", type=int, default=100)
    args = parser.parse_args()
    if args.limit < 1 or args.dps < 30:
        raise SystemExit("require --limit >= 1 and --dps >= 30")
    mp.mp.dps = args.dps
    limit = args.limit
    eta = eta_coefficients(limit)
    print("DIAGNOSTIC ONLY: finite high-precision values do not prove RH")
    print("n,lambda_n,base,gamma_sum,eta_sum,cancellation_ratio")
    for n in range(1, limit + 1):
        base, gamma_sum, eta_sum = components(n, eta)
        value = base + gamma_sum + eta_sum
        scale = abs(base) + abs(gamma_sum) + abs(eta_sum)
        ratio = abs(value) / scale if scale else mp.mpf(0)
        print(
            f"{n},{mp.nstr(value,18)},{mp.nstr(base,12)},"
            f"{mp.nstr(gamma_sum,12)},{mp.nstr(eta_sum,12)},{mp.nstr(ratio,8)}"
        )

    expected_lambda_1 = 1 + mp.euler / 2 - mp.log(4 * mp.pi) / 2
    actual_lambda_1 = sum(components(1, eta))
    if abs(actual_lambda_1 - expected_lambda_1) > mp.mpf("1e-80"):
        raise SystemExit("lambda_1 identity check failed")


if __name__ == "__main__":
    main()
