"""Arb enclosure for the leading S -> -infinity coefficient in T12.

The mathematical reduction is exact.  If
  f_ij(y) = exp((2j+1)y) Phi^(2i)(exp(y)),
then the bilateral Laplace transform has its first possible pole at s=1.
Its coefficient, equivalently a direct dominated-convergence argument in
the convolution expansion, gives
  lim_{S -> -infinity} exp(-S) g_r(S) = r! C_r,
where C_r is the determinant assembled below.  Thus C_r < 0 rigorously
disproves positivity of the T11 pushforward for that rank.

Odd moments are enclosed by the composite midpoint rule, with its error bounded
from interval enclosures of the second derivative on every subinterval.  No
floating quadrature enters the certificate.  The omitted theta and u tails are
covered by conservative balls; their analytic bounds are documented in T13.
"""

from __future__ import annotations

import argparse
import math

from flint import arb, arb_mat, ctx, fmpq


def certify_analytic_tails() -> None:
    pi = arb.pi()
    # On u >= 0 the positive first component of each theta summand decreases.
    # For n >= 9, consecutive terms are bounded by this geometric ratio.
    ratio0 = (arb(10) / 9) ** 4 * (-19 * pi).exp()
    tail0 = 4 * pi**2 * 9**4 * (-81 * pi).exp() / (1 - ratio0)
    assert tail0.upper() < arb("1e-105")

    # Absolute tails for Phi, Phi', Phi'' on [0,2].  The order-two
    # polynomial majorant also covers orders zero and one.
    q9 = 81 * pi
    first2 = 4 * pi**2 * 9**4 * (-q9).exp() * (2 * q9 + arb("6.5")) ** 2
    second2 = 6 * pi * 9**2 * (-q9).exp() * (2 * q9 + arb("4.5")) ** 2
    ratio2 = (arb(10) / 9) ** 8 * (-19 * pi).exp()
    assert ((first2 + second2) / (1 - ratio2)).upper() < arb("1e-98")

    # At u=0, derivative orders through 14: q|P'_m| <= m R_m(q)
    # gives |P_14(q)| <= (2q+a+28)^14.  The n >= 13 tail is tiny.
    q13 = 169 * pi
    first14 = 4 * pi**2 * 13**4 * (-q13).exp() * (2 * q13 + arb("32.5")) ** 14
    second14 = 6 * pi * 13**2 * (-q13).exp() * (2 * q13 + arb("30.5")) ** 14
    ratio14 = (arb(14) / 13) ** 32 * (-27 * pi).exp()
    assert ((first14 + second14) / (1 - ratio14)).upper() < arb("1e-100")

    # For p <= 13 and u >= 2, the logarithmic derivative of the positive
    # majorant is at most 11-2*pi*e^4 < -300.  Integrate that exponential
    # envelope; n=1..8 already dominate the theta sum.
    two = arb(2)
    exp4 = arb(4).exp()
    decay = 2 * pi * exp4 - 11
    head = arb(0)
    for n in range(1, 9):
        head += 4 * pi**2 * n**4 * two**13 * arb(9).exp() * (-pi * n * n * exp4).exp()
    assert (head / decay + arb("1e-100")).upper() < arb("1e-60")


def phi_ball(u: arb) -> arb:
    total = arb(0)
    for n in range(1, 9):
        n2 = n * n
        # Positive factorization of the half-scale classical Xi kernel.
        total += (
            2 * arb.pi() * n2
            * (arb("2.5") * u).exp()
            * (2 * arb.pi() * n2 * (2 * u).exp() - 3)
            * (-arb.pi() * n2 * (2 * u).exp()).exp()
        )
    # n >= 9 contributes less than 1e-104 uniformly on [0,2].
    return total + arb(0, "1e-103")


def phi_derivative_balls(u: arb) -> tuple[arb, arb, arb]:
    out = [arb(0), arb(0), arb(0)]
    for n in range(1, 9):
        n2 = n * n
        q = arb.pi() * n2 * (2 * u).exp()
        base = (-q).exp()
        for coefficient, alpha in (
            (4 * arb.pi() ** 2 * n2 * n2, arb("4.5")),
            (-6 * arb.pi() * n2, arb("2.5")),
        ):
            coeffs = [arb(1)]
            for order in range(3):
                value = arb(0)
                for c in reversed(coeffs):
                    value = value * q + c
                out[order] += coefficient * (alpha * u).exp() * base * value
                nxt = [arb(0) for _ in range(len(coeffs) + 1)]
                for k, c in enumerate(coeffs):
                    nxt[k] += (alpha + 2 * k) * c
                    nxt[k + 1] -= 2 * c
                coeffs = nxt
    return tuple(value + arb(0, "1e-98") for value in out)  # type: ignore[return-value]


def odd_moments(subintervals: int, max_power: int) -> dict[int, arb]:
    h = arb(fmpq(2, subintervals))
    powers = list(range(1, max_power + 1, 2))
    totals = {p: arb(0) for p in powers}
    second_bounds = {p: arb(0) for p in powers}
    for m in range(subintervals):
        midpoint = fmpq(2 * m + 1, subintervals)
        radius = fmpq(1, subintervals)
        point = arb(midpoint)
        ph_point = phi_ball(point)
        for p in powers:
            totals[p] += h * point**p * ph_point

        interval = arb(point, arb(radius))
        ph0, ph1, ph2 = phi_derivative_balls(interval)
        for p in powers:
            second = 2 * p * interval ** (p - 1) * ph1 + interval**p * ph2
            if p >= 2:
                second += p * (p - 1) * interval ** (p - 2) * ph0
            bound = arb(second.abs_upper())
            if bound > second_bounds[p]:
                second_bounds[p] = bound

    # Composite-midpoint error on an interval of length 2.
    for p in powers:
        midpoint_error = second_bounds[p] * h * h / 12
        totals[p] += arb(0, str(midpoint_error.upper()))
    # For p <= 13, the u >= 2 tail is < 1e-60 by logarithmic-derivative
    # domination; this ball also absorbs the theta n >= 9 tail.
    for p in totals:
        totals[p] += arb(0, "1e-59")
    return totals


def phi_even_derivatives_zero(max_index: int) -> list[arb]:
    out: list[arb] = []
    for index in range(max_index + 1):
        order = 2 * index
        total = arb(0)
        for n in range(1, 13):
            n2 = n * n
            q = arb.pi() * n2
            for coefficient, alpha in (
                (4 * arb.pi() ** 2 * n2 * n2, arb("4.5")),
                (-6 * arb.pi() * n2, arb("2.5")),
            ):
                coeffs = [arb(1)]
                for _ in range(order):
                    nxt = [arb(0) for _ in range(len(coeffs) + 1)]
                    for k, c in enumerate(coeffs):
                        nxt[k] += (alpha + 2 * k) * c
                        nxt[k + 1] -= 2 * c
                    coeffs = nxt
                value = arb(0)
                for c in reversed(coeffs):
                    value = value * q + c
                total += coefficient * (-q).exp() * value
        # n >= 13 is far below this bound even at derivative order 14.
        out.append(total + arb(0, "1e-100"))
    return out


def coefficient(rank: int, moments: dict[int, arb], derivatives: list[arb]) -> arb:
    entries: list[list[arb]] = [[arb(0) for _ in range(rank)] for _ in range(rank)]
    for i in range(rank):
        entries[i][0] = derivatives[i]
        for j in range(1, rank):
            factorial = math.factorial(2 * j - 1)
            if i >= j:
                entries[i][j] = factorial * derivatives[i - j]
            else:
                d = j - i
                entries[i][j] = (
                    arb(factorial) / math.factorial(2 * d - 1) * moments[2 * d - 1]
                )
    return arb_mat(entries).det()


def run() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--subintervals", type=int, default=20000)
    parser.add_argument("--prec", type=int, default=192)
    args = parser.parse_args()
    ctx.prec = args.prec
    certify_analytic_tails()
    moments = odd_moments(args.subintervals, 13)
    derivatives = phi_even_derivatives_zero(7)
    print(f"Arb midpoint certificate: N={args.subintervals}, prec={args.prec}")
    for rank in (6, 7, 8):
        c = coefficient(rank, moments, derivatives)
        print(f"C_{rank} = {c}; lower={c.lower()}; upper={c.upper()}")
        if rank == 7:
            assert c.upper() < 0, "C_7 enclosure does not prove negativity"
    print("CERTIFIED: C_7 < 0 (using the analytic tail bounds proved in T13).")


if __name__ == "__main__":
    run()
