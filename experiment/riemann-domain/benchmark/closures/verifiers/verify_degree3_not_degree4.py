"""Exact counterexamples: cubic/J12 control need not imply degree 4."""

from fractions import Fraction


def bareiss(matrix):
    a = [row[:] for row in matrix]
    n = len(a)
    sign = 1
    previous = 1
    for k in range(n - 1):
        if a[k][k] == 0:
            pivot = next(j for j in range(k + 1, n) if a[j][k])
            a[k], a[pivot] = a[pivot], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                numerator = a[i][j] * pivot - a[i][k] * a[k][j]
                assert numerator % previous == 0
                a[i][j] = numerator // previous
        previous = pivot
    return sign * a[-1][-1]


def resultant(p, q):
    """Resultant for descending integer coefficient lists."""
    p, q = list(p), list(q)
    n, m = len(p) - 1, len(q) - 1
    matrix = []
    for shift in range(m):
        matrix.append([0] * shift + p + [0] * (m - 1 - shift))
    for shift in range(n):
        matrix.append([0] * shift + q + [0] * (n - 1 - shift))
    return bareiss(matrix)


def discriminant(p):
    n = len(p) - 1
    derivative = [p[j] * (n - j) for j in range(n)]
    return (-1) ** (n * (n - 1) // 2) * resultant(p, derivative) // p[0]


def main():
    gamma = (25, 78, 143, 76, 29)
    cubic0 = (gamma[3], 3 * gamma[2], 3 * gamma[1], gamma[0])
    cubic1 = (gamma[4], 3 * gamma[3], 3 * gamma[2], gamma[1])
    quartic = (
        gamma[4],
        4 * gamma[3],
        6 * gamma[2],
        4 * gamma[1],
        gamma[0],
    )
    d0 = discriminant(cubic0)
    d1 = discriminant(cubic1)
    d4 = discriminant(quartic)
    assert d0 > 0 and d1 > 0
    assert d4 < 0
    print("gamma:", gamma)
    print("shifted cubic discriminants:", d0, d1)
    print("quartic discriminant:", d4)
    print("degree-3-to-degree-4 implication: REFUTED")

    # Stronger audit: this initial block extends to an infinite positive
    # sequence satisfying the sufficient J12 corridor at every index.
    # Set C1=61/1000, C2=49/1000, and Ck=6/125 for every k>=3; define
    # r1=1, r_(k+1)=r_k(1-Ck), gamma_0=gamma_1=1 and
    # gamma_(k+1)=gamma_k r_(k+1).  The common scaling below clears the
    # denominators of gamma_0,...,gamma_4.
    gamma_j12 = (
        125000000000000000,
        125000000000000000,
        117375000000000000,
        104814583875000000,
        89105553458834661,
    )
    c_values = [
        Fraction(1) - Fraction(gamma_j12[k - 1] * gamma_j12[k + 1], gamma_j12[k] ** 2)
        for k in range(1, 4)
    ]
    assert c_values == [Fraction(61, 1000), Fraction(49, 1000), Fraction(6, 125)]
    assert all(0 < c <= Fraction(1, 12) for c in c_values)
    assert c_values[0] * (1 - 4 * c_values[0]) <= c_values[1] <= c_values[0]
    assert c_values[1] * (1 - 4 * c_values[1]) <= c_values[2] <= c_values[1]
    # The constant continuation C_k=6/125 satisfies the same recurrence
    # forever, so this is an actual infinite-sequence construction.
    assert c_values[2] * (1 - 4 * c_values[2]) <= c_values[2]

    cubic0_j12 = (
        gamma_j12[3], 3 * gamma_j12[2], 3 * gamma_j12[1], gamma_j12[0]
    )
    cubic1_j12 = (
        gamma_j12[4], 3 * gamma_j12[3], 3 * gamma_j12[2], gamma_j12[1]
    )
    quartic_j12 = (
        gamma_j12[4],
        4 * gamma_j12[3],
        6 * gamma_j12[2],
        4 * gamma_j12[1],
        gamma_j12[0],
    )
    dc0 = discriminant(cubic0_j12)
    dc1 = discriminant(cubic1_j12)
    dq = discriminant(quartic_j12)
    assert dc0 > 0 and dc1 > 0 and dq < 0
    print("global-J12 C_1,C_2,C_3:", *c_values)
    print("global-J12 first two cubic discriminants:", dc0, dc1)
    print("global-J12 initial quartic discriminant:", dq)
    print("global-J12-to-degree-4 implication: REFUTED")


if __name__ == "__main__":
    main()
