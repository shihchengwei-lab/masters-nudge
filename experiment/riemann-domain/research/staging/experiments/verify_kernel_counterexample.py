#!/usr/bin/env python3
"""Offline diagnostic for the exact positive-kernel counterexample."""

from __future__ import annotations

import cmath
import math


def main() -> None:
    x = (-5.0 - 3.0 * math.sqrt(3.0)) / 2.0
    y = math.acosh(-x)
    z = math.pi + 1j * y
    f = cmath.cos(z) + 0.1 * cmath.cos(2.0 * z)
    gaussian_factor = cmath.exp(-0.5 * z * z)
    print("DIAGNOSTIC ONLY: the counterexample proof uses exact algebra")
    print(f"x={x:.15g}, z={z.real:.15g}+{z.imag:.15g}i")
    print(f"|cos(z)+0.1 cos(2z)|={abs(f):.3e}")
    print(f"Gaussian-smoothed transform residual={abs(gaussian_factor*f):.3e}")
    if not (x < -1.0 and abs(f) < 1e-11):
        raise SystemExit("counterexample diagnostic failed")


if __name__ == "__main__":
    main()

