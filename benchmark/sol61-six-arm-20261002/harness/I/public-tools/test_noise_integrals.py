"""The eight numerical cases printed in the public SymPy issue, unchanged."""
import pytest
from sympy import I, S, integrate, oo, pi, symbols


@pytest.mark.parametrize('q', [1, 2, 10, 100])
@pytest.mark.parametrize('bandpass', [False, True])
def test_published_noise_integral(q, bandpass):
    s = symbols('s')
    f = symbols('f', real=True)
    wp, qp = symbols('omega_p, q_p', positive=True)
    numerator = wp*s if bandpass else wp**2
    transfer = numerator/(s**2 + wp/qp*s + wp**2)
    spectrum = (abs(transfer.subs(s, I*2*pi*f))**2).simplify()
    result = integrate(spectrum.subs(wp, 1).subs(qp, q), (f, 0, oo))
    assert abs(complex(result.evalf()) - float(S(q)/4)) < 1e-10
