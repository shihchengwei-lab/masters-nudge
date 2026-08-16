# P21 prime-operator trichotomy

P21 gives the exact Euler-half-plane identity

```text
det(I-exp(-s H_P))=1/zeta(s),
H_P e_p=(log p)e_p.
```

The currently explicit ways to promote this scalar identity to a spectral
construction fall into three classes.

## 1. Ordinary positive determinant

P44 classifies every trace-norm positive Dirichlet realization of the exact
Euler determinant.  Its prime coefficients are mutually orthogonal rank-one
projections, so it is unitarily the diagonal prime model.  P41 then gives the
fixed `-1/2` drift; P42 gives zero accumulation for modewise arch pairing;
P43 forbids positive cross-prime mixing by the second cumulant.

Verdict: this whole ordinary positive determinant class is closed.

## 2. Graded/super determinant

The fermionic Fock supertrace gives `1/zeta` exactly.  Unique factorization
makes every energy eigenspace one-dimensional with fixed parity.  P22 proves
that an odd energy-preserving differential is zero.  P25 extends the no-go to
closed strong spectral intertwiners and to bounded atomic--continuum maps.
A parity-reversed duplicate cancels the whole Euler determinant rather than
leaving Xi cohomology.

Verdict: ordinary Hilbert-complex/Hodge implementations are closed.  A rigged
nonclosable differential is not an operator candidate until a new positive
topology and closed induced generator are specified.

## 3. Schatten/zeta regularization

P32--P33 show that `det_q` contains only the easy `m>=q` prime-power tail.
The low cumulants removed by regularization contain `log zeta` itself and its
divisor.  P31 distinguishes the continued scalar determinant from an operator
determinant whose zeros have spectral projectors.

Verdict: standard regularization is an exact scalar identity but not a
positive spectral realization.

## Handoff boundary

All currently explicit P21 operatorizations are therefore closed at a
checkable minimal failure.  The phrase "singular arithmetic cohomology" is
only an acceptance specification unless it supplies, before using the zeta
divisor:

1. a concrete positive completed norm;
2. a closed densely defined differential/domain;
3. a self-adjoint induced generator with locally finite spectrum;
4. an ordinary or rigorously controlled relative determinant whose divisor
   equals that spectrum.

Without these data it is not an active route and should not be renamed or
counted as progress.  This trichotomy does not exclude an unknown construction
outside P21; it closes the strongest currently explicit prime-operator route.
