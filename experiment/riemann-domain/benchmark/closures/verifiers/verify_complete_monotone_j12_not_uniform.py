"""Exact counterexample to a natural uniform strengthening of J12.

Let C_k=1/[4(k+2)] and construct gamma from
    r_1=1,
    r_(k+1)=r_k(1-C_k),
    gamma_0=gamma_1=1,
    gamma_(k+1)=gamma_k r_(k+1).

C is a completely monotone (Hausdorff moment) sequence and satisfies the
full J12 corridor for every k.  Nevertheless J_(10,0) has only six real
roots.  The root count below uses an exact rational Sturm chain.
"""

from fractions import Fraction
from math import comb


def trim(poly: list[Fraction]) -> list[Fraction]:
    while len(poly) > 1 and poly[-1] == 0:
        poly.pop()
    return poly


def derivative(poly: list[Fraction]) -> list[Fraction]:
    return [Fraction(k) * poly[k] for k in range(1, len(poly))]


def remainder(dividend: list[Fraction], divisor: list[Fraction]) -> list[Fraction]:
    result = dividend[:]
    divisor = trim(divisor[:])
    while len(result) >= len(divisor) and result != [0]:
        quotient = result[-1] / divisor[-1]
        shift = len(result) - len(divisor)
        for k, coefficient in enumerate(divisor):
            result[k + shift] -= quotient * coefficient
        trim(result)
    return result


def sturm_chain(poly: list[Fraction]) -> list[list[Fraction]]:
    chain = [trim(poly[:]), trim(derivative(poly))]
    while len(chain[-1]) > 1:
        next_poly = [-value for value in remainder(chain[-2], chain[-1])]
        chain.append(trim(next_poly))
    return chain


def sign(value: Fraction) -> int:
    return (value > 0) - (value < 0)


def variations(signs: list[int]) -> int:
    nonzero = [value for value in signs if value]
    return sum(nonzero[k] != nonzero[k - 1] for k in range(1, len(nonzero)))


def main() -> None:
    degree = 10
    gamma = [Fraction(1), Fraction(1)]
    ratio = Fraction(1)
    for k in range(1, degree):
        c_k = Fraction(1, 4 * (k + 2))
        ratio *= 1 - c_k
        gamma.append(gamma[-1] * ratio)

    for k in range(1, degree):
        recovered = 1 - gamma[k - 1] * gamma[k + 1] / gamma[k] ** 2
        assert recovered == Fraction(1, 4 * (k + 2))

    # For all k>=1:
    # C_(k+1)-C_k(1-4C_k)=1/[4(k+3)(k+2)^2] > 0,
    # and C_(k+1)<C_k<=C_1=1/12.  These finite checks guard indexing.
    for k in range(1, 100):
        c_k = Fraction(1, 4 * (k + 2))
        c_next = Fraction(1, 4 * (k + 3))
        assert 0 < c_k <= Fraction(1, 12)
        assert c_k * (1 - 4 * c_k) < c_next < c_k
        assert c_next - c_k * (1 - 4 * c_k) == Fraction(
            1, 4 * (k + 3) * (k + 2) ** 2
        )

    # C_k = integral_0^1 t^(k-1) (t^2/4) dt, so C is a Hausdorff
    # moment sequence and hence completely monotone at every order.
    polynomial = [Fraction(comb(degree, k)) * gamma[k] for k in range(degree + 1)]
    chain = sturm_chain(polynomial)
    assert len(chain) == degree + 1  # squarefree

    signs_plus_infinity = [sign(item[-1]) for item in chain]
    signs_minus_infinity = [
        sign(item[-1]) * (-1 if (len(item) - 1) % 2 else 1) for item in chain
    ]
    variations_plus = variations(signs_plus_infinity)
    variations_minus = variations(signs_minus_infinity)
    real_roots = variations_minus - variations_plus

    assert variations_minus == 8
    assert variations_plus == 2
    assert real_roots == 6 < degree
    print("C_k = 1/[4(k+2)]: global J12 and completely monotone")
    print("J_(10,0) Sturm variations at -infinity,+infinity:", variations_minus, variations_plus)
    print("J_(10,0) distinct real roots:", real_roots, "of", degree)
    print("J12 + complete monotonicity of C => all-degree: REFUTED")


if __name__ == "__main__":
    main()
