#!/usr/bin/env python3
"""Offline verification of the exact quartet identity and resonance locations.

Floating-point checks are diagnostics only; the proof is algebraic and recorded
in candidate_lemmas.md and li_exact_analysis.md.
"""

from __future__ import annotations

import cmath
import math


def direct_q(n: int, beta: float, gamma: float) -> float:
    roots = (
        complex(beta, gamma), complex(beta, -gamma),
        complex(1.0 - beta, gamma), complex(1.0 - beta, -gamma),
    )
    return sum(1.0 - (1.0 - 1.0 / rho) ** n for rho in roots).real


def parameters(beta: float, gamma: float) -> tuple[float, float]:
    r2 = (gamma * gamma + (1.0 - beta) ** 2) / (gamma * gamma + beta * beta)
    lam = 0.5 * math.log(r2)
    theta = cmath.phase(complex(gamma * gamma - beta * (1.0 - beta), gamma))
    return lam, theta


def exact_q(n: int, beta: float, gamma: float) -> float:
    lam, theta = parameters(beta, gamma)
    return 4.0 - 4.0 * math.cosh(n * lam) * math.cos(n * theta)


def is_negative(n: int, beta: float, gamma: float) -> bool:
    lam, theta = parameters(beta, gamma)
    x = abs(n * lam)
    threshold = 0.0 if x > 40.0 else 1.0 / math.cosh(x)
    return math.cos(n * theta) > threshold


def first_negative(beta: float, gamma: float, limit: int = 200_000) -> int | None:
    for n in range(1, limit + 1):
        if is_negative(n, beta, gamma):
            return n
    return None


def main() -> None:
    max_relative_error = 0.0
    for beta in (0.10, 0.25, 0.40, 0.49, 0.50, 0.73):
        for gamma in (1.0, 10.0, 30.0, 100.0):
            for n in (1, 2, 7, 31, 100, 257):
                direct = direct_q(n, beta, gamma)
                closed = exact_q(n, beta, gamma)
                scale = max(1.0, abs(direct), abs(closed))
                max_relative_error = max(max_relative_error, abs(direct - closed) / scale)
    print("DIAGNOSTIC ONLY: floating-point identity check; not a proof of RH")
    print(f"maximum scaled direct-vs-closed-form error: {max_relative_error:.3e}")
    if max_relative_error > 1e-12:
        raise SystemExit("identity check exceeded tolerance")

    print("beta,gamma,first_negative,n/gamma,q_n")
    for beta in (0.10, 0.25, 0.40, 0.49):
        for gamma in (10.0, 30.0, 100.0):
            n = first_negative(beta, gamma)
            if n is None:
                print(f"{beta:.2f},{gamma:.1f},NONE,N/A,N/A")
            else:
                print(f"{beta:.2f},{gamma:.1f},{n},{n/gamma:.6f},{exact_q(n,beta,gamma):.12g}")

    # On the critical line lambda=0, so q_n=4-4cos(n theta) is nonnegative.
    critical_min = min(exact_q(n, 0.5, 30.0) for n in range(1, 10_001))
    print(f"critical-line minimum over n<=10000: {critical_min:.12g}")
    if critical_min < -1e-12:
        raise SystemExit("critical-line nonnegativity check failed")


if __name__ == "__main__":
    main()
