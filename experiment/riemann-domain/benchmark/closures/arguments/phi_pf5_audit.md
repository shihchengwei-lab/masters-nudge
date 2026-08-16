# Actual Riemann-kernel PF5 counterexample audit

Date: 2026-08-15

Primary source: Wojciech Michałowski, *On the Pólya Frequency Order of the
de Bruijn--Newman Kernel: Certified Failure at Order Five*,
arXiv:2602.20313v2 (20 Jul 2026).

Independent verifier: `experiments/verify_phi_pf5_arb.py`.

## PF1. Statement and relevance

Let

`K(u)=Phi(|u|)`

with the classical de Bruijn--Newman theta kernel (the normalization in the
paper differs from other Xi conventions only by positive scaling/dilation,
which preserves PF order).  PF5 would require every ordered translation minor
of size at most five to be non-negative.  The Toeplitz configuration

`M_ij=K(0.01+(i-j)0.05),  i,j=0,...,4`

has negative determinant.  Therefore the actual Riemann kernel is not PF5 and
in particular not PF-infinity/totally positive.

This is stronger than the previous generic cubic-to-quartic no-lifting
counterexample: it refutes the proposed uniform total-positivity mechanism for
the actual theta kernel itself.  It does not refute K0/Weyl/Weil positivity,
which uses a different signed derivative/correlation kernel and remains
equivalent to RH.

## PF2. Independent ball-arithmetic verification

The local script evaluates each of the nine distinct theta values with
python-flint/Arb at 320-bit precision.  It sums `n=1,...,50` and widens every
value by `+/-1e-70`.  On `0<=u<=0.21`, the elementary bound

`sum_(n>=51) (2*pi^2*e^1.89*n^4+3*pi*e^1.05*n^2)e^(-pi*n^2) < 1e-70`

contains the omitted tail; hence the input balls rigorously contain the exact
kernel values.

Two independent determinant evaluations gave

`Arb matrix det = [-1.8472360734426587333101372414183523967e-9 +/- 3.68e-72]`

and

`120-term Leibniz = [-1.8472360734426587333101372414183523967e-9 +/- 4.31e-69]`.

The balls overlap and are strictly negative.  Thus, modulo the standard
correctness of Arb directed ball arithmetic, this is a computer-assisted
counterexample with an analytic truncation bound, not an uncertified floating-
point observation.  It is used only to disprove a candidate lemma, never as
evidence for RH.

## PF3. Version-control warning

Version 2 responsibly withdraws its version-1 claims about a globally negative
small-spacing coefficient, a unique threshold and Gaussian healing: the old
derivative tail was controlled only through order 10 although the size-five
coefficient needs derivatives through order 14.  The GitHub README still
contains some stale claims that those derivative calculations are certified.
They are not used here.  The direct finite witness uses no derivatives and was
independently rechecked above.

## PF4. Strategy consequence

The requested all-degree route cannot be ordinary Schoenberg total positivity
of `Phi(|x-y|)`: it is false already at degree 5.  Positivity at degrees 2--4
for one configuration, and any existing degree-3 certificate, therefore
contains no hidden uniform lift.  Degree 3 remains an independent finite
result.

Any viable uniform theorem must concern the exact Xi Bezoutian/K0/Weyl or the
folded Thorin/Weil form, and must use a Riemann-specific arithmetic
cancellation.  Replacing that form by raw translation minors of the positive
Phi kernel is now a closed route.
