# Prime defect drift audit

## Exact positive local model

Fix a prime `p`, put `ell=log p` and `r=p^(-1/2)=exp(-ell/2)`.  On

```text
H_p=L2([0,ell], exp(t)dt)
```

let `A_p f=f'` with boundary `f(ell)=r f(0)`.  Integration by parts gives

```text
< (A_p+1/2)f,g > + < f,(A_p+1/2)g >
 =exp(ell)f(ell)conj(g(ell))-f(0)conj(g(0))=0.    (PD1)
```

The boundary condition is maximal, hence

```text
K_p=A_p+1/2 is skew-adjoint,
A_p=-1/2 I+K_p.                                  (PD2)
```

Solving `A_p f=lambda f` gives

```text
spec(A_p)={-1/2+2*pi*i*k/log p : k in Z}.         (PD3)
```

These are exactly the zero locations of the local defect
`1-p^(-1/2-x)`, up to the harmless sign convention for `k`.

## Uniform projector obstruction

For every finite prime cutoff, and for any closed reducing positive subspace,
PD2 descends unchanged:

```text
Re A_reduced=-1/2 I.                              (PD4)
```

The same is true for a positive Hilbert cohomology quotient when the
differential intertwines `A` and the adjoint structure descends.  Thus no
orthogonal/nonlocal projector inside the prime defect space can turn the
local Euler divisor into imaginary-axis spectrum.  The obstruction already
holds for one prime and is uniform in the number of primes.

Shifting to `A_p+1/2` makes the generator conservative, but changes the
characteristic factor from `1-p^(-1/2-x)` to `1-p^(-x)`.  It therefore removes
the exact critical weight one was required to preserve.

## What remains

A larger unitary dilation can make the full generator conservative, as in
P28, but then the Euler zeros are resonances of a dissipative compression,
not eigenvalues of the positive dilation.  P31 already separates these two
notions.  Promoting the resonances to spectrum requires a singular
archimedean--prime cohomology that does not inherit PD4; P22 and P25 exclude
ordinary energy-preserving Hilbert differentials and bounded atomic--continuum
intertwiners.

Therefore the proposed nonlocal projector on the prime space is closed.  A
surviving construction must explicitly couple an opposite archimedean drift,
define a new positive completed norm, and prove that the induced generator is
self-adjoint while retaining the absolute determinant rather than only its
scattering ratio.
