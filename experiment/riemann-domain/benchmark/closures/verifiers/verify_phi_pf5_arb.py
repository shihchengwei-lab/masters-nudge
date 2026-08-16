"""Independent Arb certificate for the published PF5 witness of Phi.

This is a counterexample certificate, not evidence for RH.  It evaluates the
5x5 Toeplitz determinant at (u0,h)=(0.01,0.05) twice: with Arb's matrix
determinant and with the explicit 120-term Leibniz formula.  The theta series
is truncated at n=50 and each value is widened by 1e-70.  For |u|<=0.21 the
paper's elementary geometric estimate bounds the omitted tail by 1e-70.
"""

from itertools import permutations

from flint import arb, arb_mat, ctx


ctx.prec = 320
TAIL = arb(0, "1e-70")


def phi_ball(u):
    u = abs(u)
    e4 = (arb(4) * u).exp()
    e5 = (arb(5) * u).exp()
    e9 = (arb(9) * u).exp()
    pi = arb.pi()
    ans = arb(0)
    for n in range(1, 51):
        n2 = arb(n * n)
        n4 = arb(n**4)
        ans += (arb(2) * pi**2 * n4 * e9 - arb(3) * pi * n2 * e5) * (
            -pi * n2 * e4
        ).exp()
    return ans + TAIL


def permutation_sign(p):
    inversions = sum(p[i] > p[j] for i in range(5) for j in range(i + 1, 5))
    return -1 if inversions % 2 else 1


u0, h = arb("0.01"), arb("0.05")
entries = [phi_ball(u0 + arb(k) * h) for k in range(-4, 5)]
rows = [[entries[(i - j) + 4] for j in range(5)] for i in range(5)]

det_arb = arb_mat(rows).det()
det_leibniz = arb(0)
for p in permutations(range(5)):
    term = arb(permutation_sign(p))
    for i in range(5):
        term *= rows[i][p[i]]
    det_leibniz += term

print("Arb matrix determinant:", det_arb)
print("Leibniz determinant:   ", det_leibniz)
print("overlap:", det_arb.overlaps(det_leibniz))
print("matrix det strictly negative:", det_arb < 0)
print("Leibniz det strictly negative:", det_leibniz < 0)

if not (det_arb < 0 and det_leibniz < 0 and det_arb.overlaps(det_leibniz)):
    raise SystemExit("PF5 certificate failed")
