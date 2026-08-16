#!/usr/bin/env python3
"""Exact-rational certificates for the two NB12 Gram counterexamples."""

from fractions import Fraction


def partial_gram(n: int, k: int, cutoff: int) -> Fraction:
    return sum(
        (
            Fraction(m % n, n)
            * Fraction(m % k, k)
            * Fraction(1, m * (m + 1))
            for m in range(1, cutoff + 1)
        ),
        Fraction(),
    )


def main() -> None:
    diagonal_cutoff = 50
    tail = Fraction(1, diagonal_cutoff + 1)
    off_lower = partial_gram(2, 3, diagonal_cutoff) + partial_gram(
        2, 4, diagonal_cutoff
    )
    diagonal_upper = partial_gram(2, 2, diagonal_cutoff) + tail
    diagonal_margin = off_lower - diagonal_upper
    assert diagonal_margin > 0

    minor_cutoff = 200
    tail = Fraction(1, minor_cutoff + 1)
    g23 = partial_gram(2, 3, minor_cutoff)
    g34 = partial_gram(3, 4, minor_cutoff)
    g24 = partial_gram(2, 4, minor_cutoff)
    g33 = partial_gram(3, 3, minor_cutoff)
    minor_upper = (g23 + tail) * (g34 + tail) - g24 * g33
    assert minor_upper < 0

    print("PASS diagonal dominance counterexample")
    print(f"  exact positive margin > {float(diagonal_margin):.12e}")
    print("PASS total positivity counterexample")
    print(f"  exact determinant upper bound < {float(minor_upper):.12e}")


if __name__ == "__main__":
    main()
