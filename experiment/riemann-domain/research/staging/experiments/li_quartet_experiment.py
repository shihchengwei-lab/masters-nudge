#!/usr/bin/env python3
"""Offline stress test for the finite Li-positivity barrier.

Numerical output is diagnostic only and is not evidence proving RH.
"""

from __future__ import annotations


def li_term(n: int, rho: complex) -> complex:
    return 1.0 - (1.0 - 1.0 / rho) ** n


def quartet_contribution(n: int, beta: float, gamma: float) -> float:
    roots = (
        complex(beta, gamma),
        complex(beta, -gamma),
        complex(1.0 - beta, gamma),
        complex(1.0 - beta, -gamma),
    )
    value = sum((li_term(n, rho) for rho in roots), 0j)
    if abs(value.imag) > 1e-9 * max(1.0, abs(value.real)):
        raise ArithmeticError(f"unexpected imaginary residue: {value.imag}")
    return value.real


def scan(beta: float, gamma: float, limit: int) -> tuple[int, float, int, float]:
    values = [(n, quartet_contribution(n, beta, gamma)) for n in range(1, limit + 1)]
    n_min, v_min = min(values, key=lambda item: item[1])
    negatives = sum(v < 0.0 for _, v in values)
    return n_min, v_min, negatives, values[-1][1]


def main() -> None:
    print("DIAGNOSTIC ONLY: finite floating-point experiment; not a proof of RH")
    print("beta,gamma,N,n_at_min,min_q,negative_count,q_N,asymptotic_q_N,ratio")
    for beta in (0.10, 0.25, 0.40):
        for gamma in (10.0, 30.0, 100.0, 300.0):
            for limit in (10, 50, 100):
                n_min, v_min, negatives, q_last = scan(beta, gamma, limit)
                asymptotic = 2.0 * limit * limit / (gamma * gamma)
                ratio = q_last / asymptotic
                print(
                    f"{beta:.2f},{gamma:.1f},{limit},{n_min},{v_min:.12g},"
                    f"{negatives},{q_last:.12g},{asymptotic:.12g},{ratio:.8g}"
                )


if __name__ == "__main__":
    main()

