#!/usr/bin/env python3
"""Finite consistency checks for the accompanying Riemann derivation.

This program deliberately uses only the Python standard library.  Its output is
diagnostic evidence, never a proof of a statement quantified over all zeros.
"""

from __future__ import annotations

import argparse
import cmath
import json
import math
from pathlib import Path
from typing import Callable


def theta(x: float, tol: float = 1e-16) -> float:
    if x <= 0:
        raise ValueError("x must be positive")
    total = 1.0
    for n in range(1, 10_000):
        term = 2.0 * math.exp(-math.pi * n * n * x)
        total += term
        if term < tol:
            return total
    raise RuntimeError("theta series did not converge")


def psi(x: float, tol: float = 1e-17) -> float:
    if x <= 0:
        raise ValueError("x must be positive")
    total = 0.0
    for n in range(1, 10_000):
        term = math.exp(-math.pi * n * n * x)
        total += term
        if term < tol:
            return total
    raise RuntimeError("psi series did not converge")


def kernel(u: float, tol: float = 1e-17) -> float:
    """The positive kernel K(u) in equation (6.3), for u >= 0."""
    if u < 0:
        raise ValueError("kernel is represented on u >= 0")
    e2u = math.exp(2.0 * u)
    total = 0.0
    for n in range(1, 10_000):
        y = math.pi * n * n * e2u
        term = 4.0 * y * (2.0 * y - 3.0) * math.exp(0.5 * u - y)
        total += term
        if term < tol:
            return total
    raise RuntimeError("kernel series did not converge")


def simpson_complex(
    fn: Callable[[float], complex], start: float, stop: float, panels: int
) -> complex:
    if panels <= 0 or panels % 2:
        raise ValueError("panels must be a positive even integer")
    h = (stop - start) / panels
    total = fn(start) + fn(stop)
    total += 4.0 * sum(fn(start + j * h) for j in range(1, panels, 2))
    total += 2.0 * sum(fn(start + j * h) for j in range(2, panels, 2))
    return total * h / 3.0


def xi_from_theta(s: complex, panels: int = 12_000) -> complex:
    """Equation (3.5), after x=exp(u) in J(s)."""

    def integrand(u: float) -> complex:
        value = psi(math.exp(u))
        return value * (cmath.exp(0.5 * s * u) + cmath.exp(0.5 * (1.0 - s) * u))

    j_value = simpson_complex(integrand, 0.0, 5.0, panels)
    return 0.5 + 0.5 * s * (s - 1.0) * j_value


def xi_from_kernel(t: complex, panels: int = 12_000) -> complex:
    """Equation (6.2)."""
    return simpson_complex(
        lambda u: kernel(u) * cmath.cos(t * u), 0.0, 5.0, panels
    )


def symmetric_polynomial(s: complex) -> complex:
    alpha = 0.75 + 1.0j
    roots = (alpha, alpha.conjugate(), 1.0 - alpha, 1.0 - alpha.conjugate())
    result = 1.0 + 0.0j
    for root in roots:
        result *= s - root
    return result


def check(name: str, value: float, tolerance: float) -> dict[str, object]:
    return {
        "name": name,
        "value": value,
        "tolerance": tolerance,
        "passed": math.isfinite(value) and value <= tolerance,
    }


def run_checks() -> dict[str, object]:
    checks: list[dict[str, object]] = []

    theta_error = max(
        abs(theta(x) - x ** -0.5 * theta(1.0 / x))
        for x in (0.2, 0.5, 1.0, 2.0, 5.0)
    )
    checks.append(check("theta modular identity", theta_error, 2e-13))

    # Beyond about u=2.5 the positive double-exponential tail underflows to
    # zero in binary64, so the floating-point positivity check stops at u=2.
    kernel_min = min(kernel(j / 20.0) for j in range(0, 41))
    checks.append(
        {
            "name": "sampled K(u) positivity on 0 <= u <= 2",
            "value": kernel_min,
            "tolerance": 0.0,
            "passed": kernel_min > 0.0,
        }
    )

    representation_error = max(
        abs(xi_from_theta(0.5 + 1j * t) - xi_from_kernel(t))
        for t in (0.0, 5.0, 10.0, 14.134725141734693)
    )
    checks.append(check("theta/kernel Xi agreement", representation_error, 2e-10))

    xi_zero_approximations = (
        14.134725141734693,
        21.022039638771555,
        25.01085758014569,
        30.424876125859512,
        32.93506158773919,
    )
    zero_residuals = {}
    for t in xi_zero_approximations:
        absolute = abs(xi_from_kernel(t))
        neighbor_scale = max(
            abs(xi_from_kernel(t - 0.05)), abs(xi_from_kernel(t + 0.05))
        )
        zero_residuals[f"{t:.15f}"] = {
            "absolute": absolute,
            "relative_to_neighbors": absolute / neighbor_scale,
        }
    checks.append(
        check(
            "five finite zero residuals relative to t +/- 0.05",
            max(item["relative_to_neighbors"] for item in zero_residuals.values()),
            1e-8,
        )
    )

    xi_zero = xi_from_kernel(0.0).real
    checks.append(check("Xi(0) reference value", abs(xi_zero - 0.4971207781883141), 2e-12))

    samples = (0.2 + 0.7j, -1.3 + 2.0j, 0.5 + 3.0j)
    polynomial_symmetry_error = max(
        abs(symmetric_polynomial(s) - symmetric_polynomial(1.0 - s))
        for s in samples
    )
    polynomial_reality_error = max(
        abs(symmetric_polynomial(s.conjugate()) - symmetric_polynomial(s).conjugate())
        for s in samples
    )
    checks.append(check("off-line polynomial functional symmetry", polynomial_symmetry_error, 2e-13))
    checks.append(check("off-line polynomial conjugation symmetry", polynomial_reality_error, 2e-13))

    imaginary_axis_min = min(xi_from_kernel(1j * b).real for b in (0.1, 0.25, 0.49))
    checks.append(
        {
            "name": "sampled Xi(ib) positivity",
            "value": imaginary_axis_min,
            "tolerance": 0.0,
            "passed": imaginary_axis_min > 0.0,
        }
    )

    return {
        "status": "pass" if all(item["passed"] for item in checks) else "fail",
        "scope_warning": (
            "Finite floating-point checks validate formulas only; they do not prove "
            "the Riemann hypothesis or exclude zeros outside the sampled points."
        ),
        "checks": checks,
        "zero_residuals": zero_residuals,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = run_checks()
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
