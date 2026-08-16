# Toeplitz / Jacobi--Trudi uniform route

Date: 2026-08-15.  This file records only all-rank identities and their
quantifier audit.  Finite numerical minors are not used as proof.

## T1. Consecutive Toeplitz minors are an all-degree criterion

Put

```text
G(z)=sum_(n>=0) a_n z^n
    =(1/8) xi(1/2+sqrt(z)/2),       a_n>0, a_n=0 for n<0,
D_(r,k)=det[a_(k+j-i)]_(0<=i,j<r).
```

Since `G` has genus zero, the Aissen--Schoenberg--Whitney--Edrei
criterion and the strict consecutive-minor criterion give

```text
RH  <=>  (a_n) is PF_infinity
    <=>  D_(r,k)>=0 for every r,k.                         (T1.1)
```

This is genuinely uniform in rank.  It is not the same finite object as
the shifted Jensen cubic proved in J55: `D_(r,k)` is a rectangular Schur
minor of the ordinary coefficients `a_n`, whereas J55 is the cubic
discriminant of four consecutive exponential coefficients
`gamma_n=n!a_n`.  In particular J55 does not even supply the full row
`D_(3,k)`.

## T2. Exact Desnanot--Jacobi / discrete-Toda elevation

Applying the Desnanot--Jacobi identity to the first and last rows and
columns of the Toeplitz block gives, for `r>=2`,

```text
D_(r,k) D_(r-2,k)
 = D_(r-1,k)^2-D_(r-1,k-1)D_(r-1,k+1).             (T2.1)
```

The index check is exact: the two off-corner minors have shifts `k-1`
and `k+1`, while the central minor retains shift `k`.  Also
`D_(0,k)=1` and `D_(r,0)=a_0^r`.

Consequently, once rows `r-2,r-1` are positive,

```text
D_(r,k)>0
 <=> k |-> D_(r-1,k) is strictly log-concave at k.          (T2.2)
```

Thus (T2.1) is a clean rank-elevation mechanism, but not a free
induction: its induction hypothesis is precisely the next contiguous
minor.  Equivalently,

```text
D_(r,k)=L(D_(r-1,.))_k / D_(r-2,k),
L(x)_k=x_k^2-x_(k-1)x_(k+1).                              (T2.3)
```

Proving that this nonlinear condensation stays positive for every
iterate is another coordinate for PF-infinity.  Degree 3 supplies no
invariant cone preserved by (T2.3).

## T3. Rectangular Jacobi--Trudi duality freezes one dimension

Normalize `b_n=a_n/a_0` and define the reciprocal coefficients

```text
H(z)=sum_(n>=0)b_n z^n,
E(z)=1/H(-z)=sum_(n>=0)e_n z^n.                            (T3.1)
```

The first determinant in (T1.1) is the rectangular Schur specialization
`s_((k^r))` with complete functions `b_n`.  Dual Jacobi--Trudi for the
conjugate rectangle `(r^k)` gives the exact identity

```text
D_(r,k)/a_0^r
 = det[e_(r+j-i)]_(0<=i,j<k).                             (T3.2)
```

For fixed shift `k`, an expanding `r x r` determinant has therefore
become a fixed `k x k` determinant whose coefficient index tends to
infinity.  This is a real all-rank reduction, not a finite-rank
certificate.

If the first `k` poles of `E` are simple negative-axis poles with nodes
`x_1>...>x_k>0`, residue calculus gives

```text
e_n=sum_(j=1)^k c_j x_j^n + tail_n.                       (T3.3)
```

The determinant of the leading part factors into two Vandermonde
determinants and `prod c_j x_j^r`.  For certified critical-line zeta
zeros, the residue alternation cancels the Vandermonde orientation and
the leading determinant is positive.  A contour bound with
`||Q_r^(-1)E_r||<1` then proves eventual positivity for that fixed `k`.

The quantifier obstruction is decisive: letting `k` grow requires a
uniform lower control on a growing confluent Vandermonde packet and a
tail bound beyond the first `k` poles.  Supplying real ordered poles for
all `k` is already the unknown real-zero structure.  Thus (T3.2) proves
fixed-shift eventual mechanisms but does not cover the balanced
two-parameter cone `k comparable to r`.

## T4. External uniform cubic wedge and its exact limitation

Micha\l{}owski, arXiv:2607.16795v1, proves the claimed uniform tail
theorem

```text
D_(r,k)>0 whenever r>=2 and k>=10^18 r^3.                 (T4.1)
```

The source was downloaded to
`external_inputs/michalowski_2607_source/main.tex`.  Its exact algebraic
input is the `q`-Vandermonde factorization

```text
V=[q^(ij)]=L D L^T,
R_alpha=L^(-1)diag(q^(alpha i))L,
R_alpha R_beta=R_(alpha+beta),                            (T4.2)
```

with a bidiagonal formula for `R_1`.  For the actual Xi block it takes
`q=q_k=a_(k-1)a_(k+1)/a_k^2` and writes the entries as the model times
`exp(h_s)`.  The perturbation estimate closes only when the dimensionless
quantity `r^3/k` is small.

This is not a shift flow.  `R_alpha` acts inside the fixed-`q`, fixed-`r`
comparison matrix; it neither maps `D_(r,k)` to `D_(r,k-1)` nor controls
the change `q_k -> q_(k-1)`.  Hence it cannot propagate (T4.1) into
`k=O(r)`.  The paper itself explicitly identifies that complementary
region as untouched.

Combining (T3.2) and (T4.1) explains the geometry of the remaining
problem:

```text
direct saddle/q-Pascal:      k >> r^3,
dual fixed-pole mechanism:   r -> infinity for each fixed k,
RH-critical region:          both r,k grow, especially k asymp r.   (T4.3)
```

A useful new theorem would have to control this balanced cone, for
example by a theta-specific invariant cone for the Toda map (T2.3), or
by a two-parameter Jacobi--Trudi pole/tail estimate that does not assume
the unknown poles are real.  Neither is currently available.

## T5. Latest contour-Hankel dynamics is an exact equivalence, not the missing cone

Deng--Yang--Lue, arXiv:2608.11520v1, define contour moments

```text
m_l=(1/(2 pi i)) int_Gamma phi(z)^l Xi'(z)/Xi(z) dz
   =sum_j omega_j zeta_j^l,
H_m=[m_(p+q)].                                             (T5.1)
```

Thus `H_m=V W V^T`.  For a conjugation-compatible contour, each real
node contributes one positive direction and each nonreal conjugate pair
contributes one positive and one negative direction once the matrix is
large enough.  Between zero crossings their moving-contour equation is
a congruence flow, so it preserves inertia; a nonreal conjugate pair
crossing produces exactly a rank-two indefinite jump.

Therefore the proposed positivity has no arithmetic source independent
of the zeros:

```text
all contour Hankel matrices PSD
 <=> no nonreal crossing events
 <=> RH.                                                   (T5.2)
```

The source is archived at
`external_inputs/deng_2608_source/Riemann_Xi_contour_Hankel_revised.tex`.
This framework is useful for localization and inertia bookkeeping, but
its continuous congruence cannot remove the only events that matter.

## T6. Order-one-half counterexample: even the whole tail cone is insufficient

The failure of reverse transport is not merely a weakness of the constant in
(T4.1).  For any `A>1`, define

```text
G_A(z)=cosh(sqrt(z))+A
      =(1+A)+sum_(n>=1) z^n/(2n)!.                    (T6.1)
```

This is a real entire function of order `1/2` with strictly positive
coefficients.  It nevertheless has explicit nonreal zeros.  If
`alpha=arcosh(A)>0`, then

```text
z_(m,+)=[alpha+(2m+1)pi i]^2,
z_(m,-)=[-alpha+(2m+1)pi i]^2                         (T6.2)
```

satisfy `cosh(sqrt(z))+A=0`; their imaginary parts are nonzero.

On the other hand `B(z)=cosh(sqrt(z))` has the canonical product

```text
B(z)=product_(m>=0)(1+4z/[pi^2(2m+1)^2]),             (T6.3)
```

so its coefficient sequence is PF-infinity.  Its compatible consecutive
minors are in fact strict: by the rectangular Schur specialization they are
Schur polynomials in infinitely many positive variables.  The coefficients of
`G_A` and `B` agree at every index `n>=1`.  Whenever `k>=r`, every entry of
`D_(r,k)` has index at least `k-r+1>=1`; hence

```text
D_(r,k;G_A)=D_(r,k;B)>0  for every k>=r.              (T6.4)
```

Thus even a hypothetical strengthening of (T4.1) from `k>>r^3` to the entire
tail cone `k>=r` would not imply real-rootedness, despite matching the order,
positivity and genus scale relevant here.  The missing theorem must transmit
Xi-specific information from the head-touching minors `k<r` (uniformly as both
indices grow), or equivalently control the growing reciprocal-pole packet in
(T3.2).  Tail positivity by itself has no such implication.

## T7. Exact derivative-kernel Andreief identity; naive pointwise Gram fails

There is nevertheless an Xi-specific all-rank identity. Positive geometric
rescaling of coefficients does not change any Toeplitz-minor sign, so write

```text
c_n=int_0^infinity Phi(u)u^(2n)/(2n)! du,  n>=0,
c_n=0, n<0.                                             (T7.1)
```

Extend `Phi` evenly to the line. Its odd jets vanish at zero and every
derivative decays at infinity. Repeated integration by parts therefore gives,
for all `i,j,k>=0` (including `k+j-i<0`),

```text
c_(k+j-i)=1/[2(k+j)]!
 int_0^infinity u^(2(k+j)) Phi^(2i)(u)du.              (T7.2)
```

When the left index is negative, the derivative order exceeds the monomial
degree by a positive even number; the remaining integral is an odd boundary
jet at zero and is exactly zero. Thus (T7.2), unlike an ordinary tail
asymptotic, retains the one-sided Toeplitz boundary.

Andreief's identity now yields

```text
det[c_(k+j-i)]
 = prod_j 1/[2(k+j)]! / r!
   int_(0,infinity)^r det[Phi^(2i)(u_l)]
      det[u_l^(2(k+j))] prod_l du_l.                  (T7.3)
```

On `0<u_1<...<u_r`, the second determinant is
`prod_l u_l^(2k) prod_(p<q)(u_q^2-u_p^2)>0`. Hence total positivity of the
single derivative kernel `Phi^(2i)(u)` would prove all `D_(r,k)>=0` at once.

That tempting pointwise Gram is false already at rank three. Directed
decimal intervals using the exact theta series and rigorous `n>=5` tails give

```text
det[Phi^(2i)(u_j)]_(i,j=0..2)
 in [-17.22362622207346, -17.22362610808933] < 0,
(u_0,u_1,u_2)=(0.05,0.10,0.16).                       (T7.4)
```

The certificate is
`experiments/verify_phi_even_derivative_kernel_failure.py`. Therefore T7.3
is a useful exact all-rank transport, but its integrand is signed; any proof
through it needs a global symmetrization/cancellation identity, not pointwise
total positivity of even derivatives.

## Status

The new external inputs provide genuine all-rank structures, but no uniform
bridge from the completed cubic theorem to arbitrary degree.  T6 shows that
tail-minor positivity, even for all `k>=r`, is logically insufficient.  The
sharp coefficient-side target is therefore an Xi-specific theorem for the
growing head/balanced cone `k<r` (together with the uncovered intermediate
cone), or a genuine reverse-shift invariant—not more finite batches.

## T8. Standard theta involution does not cancel the signed T7 integrand

The modular involution in logarithmic theta coordinates is `u -> -u`.
On the full-line version of (T7.3), every even derivative `Phi^(2i)` and every
monomial `u^(2(k+j))` is invariant. Consequently both determinants, Lebesgue
measure, and the Vandermonde in `u_l^2` are unchanged by coordinate sign flips.
Permutations reverse both determinants by the same sign, so their product is
again invariant. The whole signed-permutation group therefore acts with sign
`+1` on the Andreief integrand.

The positive chamber `0<u_1<...<u_r` has already quotiented out these
symmetries. In particular, the negative rank-three patch in (T7.4) is mapped
to copies having the same negative sign and Vandermonde weight; the standard
theta involution cannot pair it with a positive patch or turn it into a square.
Any viable global cancellation must use a genuinely new measure-preserving
transformation or integrated theta/Poisson identity that mixes derivative
order or theta indices, with its Jacobian and Vandermonde factor proved
explicitly. No such identity is presently known.

## T9. Moving all derivatives to the Vandermonde is exact but still signed

Let

```text
A_r=det[d_(u_l)^(2i)]_(i,l=0..r-1),
V_(r,k)=det[u_l^(2(k+j))]_(j,l=0..r-1).
```

Then `det[Phi^(2i)(u_l)]=A_r prod_l Phi(u_l)`.  Termwise integration by
parts in every variable has no boundary terms: at zero, each boundary product
contains either an odd jet of the even function `Phi` or an odd jet of the even
polynomial `V`; infinity is killed by theta decay.  Therefore (T7.3) also has
the exact all-rank form

```text
int det[Phi^(2i)(u_l)] V_(r,k)(u)du
 = int prod_l Phi(u_l) [A_r V_(r,k)](u)du.             (T9.1)
```

This does not yield a positive polynomial ensemble.  Already for `r=2`, put
`lambda_m=(2m)(2m-1)`.  Direct differentiation gives

```text
A_2 V_(2,k)
=(u_1u_2)^(2k-2)
 [2lambda_(k+1)u_1^2u_2^2-lambda_k(u_1^4+u_2^4)].   (T9.2)
```

For `k=1`, `(u_1,u_2)=(1,4)`, the bracket is exactly `-130`.  Thus the
Capelli/derivative-principle rearrangement merely moves the signed region; it
does not create a pointwise square.  A useful theorem would have to control
the **integral** of these signed symmetric polynomials under the special iid
measure `Phi(u)du` uniformly in `r,k`, which is another exact form of the
unresolved Xi-specific head/balanced-cone problem.

## T10. Random-matrix identification of the failed local kernel

The radial derivative operator used for Pólya ensembles is
`D_nu=x^nu d_x x^(1-nu)d_x`. With `x=u^2` and `nu=-1/2`,
`D_(-1/2)=u^-1 d_u^2 u/4`. Hence, for
`omega(x)=x^-1/2 Phi(sqrt(x))`, the standard size-`r`
derivative-type polynomial-ensemble density, including `dx=2u du`,

```text
Delta(x) det[D_(-1/2)^i omega(x_j)] prod_j dx_j
```

is T7's derivative determinant times its positive `u^2` Vandermonde, up to
positive row constants. Thus pointwise closure of T7 is precisely the claim
that this one weight defines Pólya ensembles of every matrix size. The
certified negative size-three patch (T7.4) rules this out. Known convolution
and spherical/Hankel-transform closure theorems require the joint density to
be nonnegative and cannot repair this signed weight. See ES76.

## T11. Live global target: positivity only after determinant pushforward

T7.4 rules out positivity of the full joint density, but that is stronger than
needed. Define on `(0,infinity)^r` the signed symmetric measure

```text
d sigma_r(u)=det[Phi^(2i)(u_l)]
              prod_(p<q)(u_q^2-u_p^2) prod_l du_l,
tau(u)=prod_l u_l^2,
nu_r=tau_# sigma_r.                                  (T11.1)
```

(One may equivalently use the `nu=-1/2` Pólya-ensemble variables in T10.)
Since the monomial alternant is
`prod_l u_l^(2k) prod_(p<q)(u_q^2-u_p^2)`, T7 gives the exact identity

```text
r! prod_(j=0)^(r-1)[2(k+j)]! D_(r,k)
   = int_0^infinity t^k d nu_r(t).                   (T11.2)
```

Therefore the single uniform statement `nu_r>=0 for every r` would prove all
consecutive Toeplitz minors at every shift, despite the local signed patches.
It is a genuine integrated-cancellation target and is not implied by standard
theta reflection (T8) or Pólya-ensemble positivity (T10).

The external derivative-principle theorems do not prove (T11.1): they start
from an already positive invariant matrix density. Here that density is signed
at size three. A valid proof must instead construct a positive one-dimensional
formula for the pushforward itself, for example a Mellin convolution or a
sum-of-squares on each product level set. Positivity of its sampled moments is
not enough to establish positivity of `nu_r`.

## T12. Exact convolution determinant and a high-r obstruction to T11

Put `u_l=exp(y_l)` and `S=sum_l y_l`, so that `tau=exp(2S)`. Define

```text
f_(i,j)(y)=exp((2j+1)y) Phi^(2i)(exp y),   0<=i,j<r.
```

Expanding the two alternants in (T11.1), relabelling the integration
variables, and collecting additive convolutions gives the exact identity

```text
g_r(S)=r! det_*[f_(i,j)](S),               (T12.1)
```

where `g_r(S)dS` is the pushforward of `sigma_r` under `sum log u_l` and
`det_*` means that determinant multiplication is additive convolution.
Equivalently,

```text
d nu_r/dt = g_r((log t)/2)/(2t),
Fourier(g_r)(xi)=r! det[Fourier(f_(i,j))(xi)].       (T12.2)
```

Thus T11 is a pointwise sign claim for one explicit one-dimensional inverse
Fourier transform, rather than a collection of moment inequalities.

Finite-precision route screening strongly contradicts that sign claim. On
windows `[-10,1.5]`, `[-13,1.7]`, and `[-16,2]`, with 1024--4096 samples,
the convolution determinant stabilizes near

```text
g_7(-7.65) = -4.2454e21,
g_8(-6.90) = -7.7170e33.
```

The respective magnitudes are about `1.09e-2` and `9.08e-2` of the maximum
absolute density on the scanned range. An independent 60-decimal-place
radix-2 FFT and Gaussian-elimination determinant gives, at 256 samples,
`-4.2452059652e21` and `-7.7132127063e33`, with negligible imaginary
residual. These computations are **not a proof of negativity**: truncation
and discretization errors have not been enclosed. They are, however, stable
enough that T11 must no longer be treated as a live positivity conjecture.
The only useful continuation of T11 is a rigorous interval enclosure of one
negative value; further moment batches cannot address (T12.1).

## T13. Rigorous rank-seven asymptotic obstruction to T11

The numerical obstruction in T12 can be made rigorous without enclosing a
high-dimensional fiber.  Use the bilateral Laplace transform

```text
F_(i,j)(s)=int_R exp(-sy) f_(i,j)(y)dy
           =int_0^infinity u^(2j-s) Phi^(2i)(u)du.   (T13.1)
```

The Taylor expansion of the even entire kernel at zero meromorphically
continues these entries.  The first possible pole is `s=1`, and it occurs
only in column `j=0`.  Put

```text
A_m=Phi^(2m)(0),       mu_p=int_0^infinity u^p Phi(u)du,
B_(i,0)=A_i,
B_(i,j)=(2j-1)! A_(i-j)                         if i>=j>=1,
B_(i,j)=(2j-1)! mu_(2(j-i)-1)/(2(j-i)-1)!      if j>i,
C_r=det B.                                             (T13.2)
```

The last two formulas follow by integrating
`int u^(2j-1)Phi^(2i)(u)du` by parts.  Thus
`det F(s)=C_r/(1-s)+holomorphic` at `s=1`.

A real-variable argument supplies the needed asymptotic without any hidden
contour constant.  Expand the convolution determinant in permutations.  In
every term exactly one factor has column `j=0`; write that term as
`f_(i,0)*h`.  Then

```text
exp(-S)(f_(i,0)*h)(S)
 = int [exp(-(S-x))f_(i,0)(S-x)] [exp(-x)h(x)]dx.
```

The first bracket tends pointwise to `A_i` and is uniformly bounded: at the
left this follows from the even Taylor expansion of `Phi^(2i)`, and at the
right from double-exponential decay.  The second bracket is absolutely
integrable because every remaining column has `j>=1`, hence left exponent
at least `3`, and all right tails are double exponential.  Dominated
convergence and the permutation sum therefore give

```text
lim_(S->-infinity) exp(-S)g_r(S)=r! C_r.             (T13.3)
```

Indeed, the weighted integrals of the remaining factors are precisely
`F_(i,j)(1)=B_(i,j)`, so the sum of the limits is `r!det B`.

The script `experiments/certify_t11_asymptotic_obstruction.py` encloses the
quantities in (T13.2) using 192-bit Arb arithmetic.  Odd moments through
`mu_13` use 10000 exact rational subintervals and the composite-midpoint
error

```text
|E_p| <= 2 h^2 sup_[0,2] |(u^p Phi(u))''| / 24.
```

The second-derivative suprema are themselves interval-enclosed on every
subinterval.  Elementary geometric/logarithmic-derivative bounds, checked
in Arb, cover the theta `n>=9` tail, the `u>=2` integral tail, and the
`n>=13` tail in the derivatives at zero.  The reproducible enclosure is

```text
-3.156096567895524060757e21
    <= C_7 <=
-2.883510345549506883157e21 < 0.                    (T13.4)
```

Since (T13.3) has a strictly negative limit after division by `exp(S)>0`,
there exists `S_0` such that `g_7(S)<0` for every `S<S_0`; by (T12.2),
`nu_7` has a negative-density interval.  **T11 is therefore rigorously
false.**  This is a counterexample to the auxiliary pushforward-positivity
proposal only.  It neither gives a negative Toeplitz minor nor bears against
RH: a signed density may still have all the particular nonnegative integer
moments appearing in (T11.2).
