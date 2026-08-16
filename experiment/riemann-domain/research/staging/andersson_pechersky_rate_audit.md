# Andersson--Pechersky effective-support audit

## Scope

This audit addresses only the named gap `(SC16.8)` / `(Handoff-1)`: whether the
bounded-coordinate density argument of Andersson can provide a finite
polynomial-in-window coefficient cost. The primary sources checked are
arXiv:1207.4624 (especially Theorem 3) and arXiv:1207.5337. The downloaded
source is at `external_inputs/andersson_1207_source/Ramachandra.tex`.

## AP1. The published density proof has no stopping-rate output

Let `X=L2(0,H)` and `x_n=A_n exp(-i lambda_n t)`. The proof invokes

```text
for every x != 0,  sum_n |<x,x_n>| = infinity
    => finite coefficient-bounded sums are dense in X.             (AP1.1)
```

This has the wrong quantifier order for a support bound. For every finite `J`,
because `X` is infinite-dimensional there is a unit `x_J` orthogonal to
`span{x_1,...,x_J}`. Hence

```text
inf_(||x||=1) sum_(n<=J) |<x,x_n>| = 0.                (AP1.2)
```

Pointwise divergence cannot therefore be uniformized by compactness; the unit
sphere is not compact and the separating direction may change with `J`.

The proof of Theorem 3 fixes a single `f`, proves divergence of
`sum A_n |fhat(lambda_n)|`, and invokes Pechersky. Its Hadamard-product and
logarithmic-integral constants depend on that fixed `f`; no modulus uniform
over moving separating/residual directions is obtained.

There is also severe explicit `H` dependence before Pechersky. The source sets
`delta_H=1/(8eH)` and chooses `X_1` with `epsilon(X_1)<delta_H/2`. In the
classical specialization `epsilon(x)=(log(x+1))^(-1-eta)`, so its displayed
choice only ensures

```text
log(X_1+1) > (16 e H)^(1/(1+eta)),
lambda_n=log(n+1) >= X_1.                              (AP1.3)
```

This is a proof threshold, not a lower bound for the true optimal support. It
does show that a literal reading supplies no polynomial window bound; the
subsequent divergence and Pechersky steps remain qualitative.

The announced follow-up arXiv:1207.5337 makes non-vanishing lower bounds for
Dirichlet series explicit. It does not give a partial-support stopping rule for
the coefficient-bounded density theorem.

**Verdict.** The attempted extraction fails at

```text
for every direction f there exists N(f,R)
    -/-> there exists N(T,R) working for all relevant directions.  (AP1.4)
```

This closes only the present proof as a producer of `(SC16.8)`; it does not
prove that polynomial-cost approximants do not exist.

## AP2. Correct target-specific finite-window dual

Put `s=1/2+it`, `y_m(t)=W_m(s)`, and, for `n>=2`,

```text
a_(m,n)(t)=W_m(s) zeta(s) (n^(-s)-n^(-1)).             (AP2.1)
```

For finite coefficients set `c_1=-sum_(n>=2)c_n/n` and
`q(c)=sum_(n>=2)|c_n|/sqrt(n)`. Then `C(1)=0` and

```text
W_m(s)(1+zeta(s)C(s))=y_m+sum_(n>=2)c_n a_(m,n),       (AP2.2)
q(c) <= K(C) <= 2q(c).                                 (AP2.3)
```

For a fixed prefix `2<=n<=N`, Hahn--Banach separation of the closed balanced
convex set `A_N{q<=K}+delta B` gives the exact equivalence

```text
exists c supported in [2,N] with q(c)<=K and
       ||y_m+A_N c||_2<=delta

iff, for every f in L2(-T,T),

|<y_m,f>| <= delta||f||_2
              + K max_(2<=n<=N) sqrt(n)|<a_(m,n),f>|.  (AP2.4)
```

The union of finite prefixes gives the closure version with `sup_(n>=2)`.

### Stress tests

1. Taking `f=P_(span atoms)^perp y_m` recovers
   `dist(y_m,span)<=delta`; no finite prefix has an all-direction lower frame
   bound. The target term is essential.
2. The desired theorem must prove (AP2.4) for each expanding `T` with one
   `K<=T^A` and `delta(T)->0`. Fixed-direction divergence is insufficient.
3. Critical-zero localization forces `K` to diverge (the bounded-norm no-go)
   but does not presently force super-polynomial growth. AP2 survives.
4. AP2 allows remote finite support; the beta tail theorem depends on `K` (or
   `K B_T`), not maximum support, so no unnecessary support bound is added.

## Result and next obligation

- **Closed:** Andersson's qualitative proof cannot itself supply a polynomial
  stopping rate; the minimal failure is (AP1.4).
- **Still open:** `(SC16.8)` / `(Handoff-1)`.
- **AP2.5:** prove (AP2.4), with `sup_(n>=2)`, for some fixed `m`, finite
  `A`, `K=T^A`, and `delta(T)->0`, using the special target `y_m` and atoms
  (AP2.1). A theorem uniform over all targets/directions is unnecessary and is
  contradicted at finite prefixes.

## AP3. Numerical extreme-parameter check (non-rigorous)

`experiments/results_ap2_dual_cost_2026-08-16.md` records an interlaced-grid
ridge/SVD test. For `m=0,N=128`, the best observed relative residual stays near
`10^-6` through `T=12`, then rises to `3.9e-3` at `T=14` and `6.4e-2` at
`T=16`, while q-cost rises from about 204 to about `10^6`. Increasing N from
64 to 512 at `T=16` improves the residual only from 0.067 to 0.057. With `m=4`
the residual is about `4e-4`, reflecting the smaller `W_m` near the first zero.

This is consistent with, but does not strengthen, the rigorous critical-zero
lower bound. Fixed-window density rules out interpreting the observed plateau
as a basis no-go; ridge is not q-optimal and the computation is not certified.
It does identify the next stress point: any proof of AP2.5 must quantify
simultaneous near-zero interpolation/cancellation, while retaining polynomial
q-cost. Kernel order only changes the fixed-zero constants and cannot remove
the requirement as `delta(T)->0`.

### AP3.1 endpoint-to-zero cost is only polynomial (proved)

Let `rho=1/2+i gamma` have multiplicity r. Fix a small real neighborhood in
which

```text
|zeta(1/2+it)| <= M |t-gamma|^r,   |W_m(1/2+it)|>=w>0. (AP3.1)
```

Let the right endpoint be `T=gamma-d`, `d>=0`, and suppose `|C|<=K`. Put
`R=(2 M K)^(-1/r)`. If `R>d`, then throughout
`[gamma-R,gamma-d]` one has `|zeta C|<=1/2`, so

```text
||W_m(1+zeta C)||_L2(-T,T)^2 >= (w^2/4)(R-d).          (AP3.2)
```

Consequently, error at most delta implies

```text
K >= 1 / {2 M (d+4 delta^2/w^2)^r}.                   (AP3.3)
```

When the zero lies inside the window, take `d=0` and one side. Thus the local
zero geometry forces polynomial growth in inverse distance/error; for a simple
zero, `K` is at least a constant times `(d+delta^2)^(-1)`. It does not by
itself force exponential cost. The sharper numerical deterioration can only
be evidence about global one-sided interpolation/conditioning.

## AP4. A generic real-Sobolev producer is impossible

A tempting continuation is to regularize `-1/zeta` on the real line, use
ordinary two-sided Fourier approximation, and then replace its frequencies by
the one-sided Dirichlet frequencies `-log n`. The last step is not harmless.

### AP4.1 one-sided Hardy lower bound (proved)

Let `omega>0`, `T>0`, and let

```text
F(z)=sum_j d_j exp(-i lambda_j z),  lambda_j>=0,
sum_j |d_j|<=K,  K>=1.                                (AP4.1)
```

Thus F is analytic in the lower half-plane and `||F||_Hinf(C_-)<=K`. Put
`delta=||F-exp(i omega t)||_(L2(-T,T))` and

```text
y=log(2K)/omega,   mu=(2/pi) arctan(T/y).              (AP4.2)
```

If `y<T`, then

```text
delta >= sqrt(pi*y*mu) 2^(-1/mu)
         (1+K)^(-(1-mu)/mu).                           (AP4.3)
```

**Proof.** Set `H(z)=1-exp(-i omega z)F(z)`. In the lower half-plane
`|H|<=1+K`. At `z=-iy`, (AP4.2) gives
`|exp(-i omega z)F(z)|<=K exp(-omega y)=1/2`, hence
`|H(-iy)|>=1/2`.

Apply the Poisson/subharmonic inequality for `log|H|` at `-iy`. The Poisson
mass of `[-T,T]` is mu. On its complement use `|H|<=1+K`; on the interval,
weighted Jensen and `P_y(x)<=1/(pi y)` give

```text
integral_[-T,T] P_y log|H|
 <= mu log(delta/sqrt(pi*y*mu)).                       (AP4.4)
```

Consequently

```text
log(1/2) <= mu log(delta/sqrt(pi*y*mu))
              +(1-mu)log(1+K),
```

which is (AP4.3). Zeros of H are handled by the standard regularization of
`log|H|`; the value at `-iy` is nonzero. QED.

Since `1-mu=(2/pi)arctan(y/T)<=2y/(pi T)` and `mu>=1/2` for `y<=T`, (AP4.3)
implies

```text
delta >= c_omega sqrt(log(2K))
         exp(-C_omega (log(2K))^2/T).                  (AP4.5)
```

In particular, for every fixed finite A, `K<=T^A` makes the right side bounded
away from zero (indeed growing like `sqrt(log T)`), so absolute L2 error cannot
tend to zero.

For a Dirichlet polynomial `C(1/2+it)`, take
`d_n=c_n/sqrt(n)`, `lambda_n=log n`; then (AP4.1) is exactly controlled by
`K(C)`. Hence real-axis smoothness, finite Sobolev order, or a two-sided Fourier
polynomial with polynomial coefficient norm does **not** generically transfer
to a polynomial-cost one-sided Dirichlet approximant.

### Consequence for AP2.5

AP4.1 is a producer no-go, not a counterexample to the special zeta target.
Any surviving proof must exploit the lower-half-plane analytic/arithmetic
structure of `-1/zeta(1/2+iz)` (with the boundary zeros and `C(1)=0` treated
exactly). Bounds only on real derivatives of a regularized reciprocal are
insufficient. This strengthens the earlier SC14 warning without assuming any
off-line zero.

## AP5. Explicit surviving producer: logarithmic Riesz--Möbius mollifier

For fixed integer `k>=1`, real `B>0`, and `X>1`, put

```text
w_(X,k)(n)=(1-log(n)/log(X))^k  (1<=n<=X),
M_(X,k)(s)=sum_(n<=X) mu(n) w_(X,k)(n)n^(-s),
a_(X,k)=M_(X,k)(1),
C_(X,k)(s)=a_(X,k)-M_(X,k)(s).                         (AP5.1)
```

Because `w(1)=1`,

```text
C_(X,k)(1)=0,
K(C_(X,k)) << sqrt(X)+log X.                           (AP5.2)
```

No Mertens estimate is used. Define, for `s=1/2+it`,

```text
E_(m,k,B)(T)=integral_(-T)^T |W_m(s)|^2
 |1+zeta(s)C_(T^B,k)(s)|^2 dt.                        (AP5.3)
```

### MB1 (live, unproved)

Prove that there exist fixed `m,k,B`, with `2m+1>B`, and an unbounded sequence
`T_j`, such that

```text
E_(m,k,B)(T_j) -> 0.                                   (MB1)
```

This is sufficient. By (AP5.2), `K^2<<T^B`; SC16.3 controls the complement by

```text
O_m(T^(-2m-1)+T^(B-2m-1)log T)=o(1).                  (AP5.4)
```

Thus MB1 gives global beta-kernel closure and RH. The quantifiers are fixed:
m, k, and B do not vary with j.

### Pressure audit

1. `C(1)=0` is exact, not asymptotic.
2. Coefficient cost is polynomial before any arithmetic estimate.
3. L48's zero-neighborhood bound is compatible with `K<<T^(B/2)`.
4. Fixed-length mollifier lower bounds on `[T,2T]` do not refute MB1 after the
   fixed beta weight; their shell contribution decays as in AP5.4.
5. PNT control near `Re s=1` does not prove AP5.3 on the critical line. A proof
   must retain signed Möbius arithmetic in the weighted mean.

MB1 is the next concrete theorem. Qualitative density, generic H-infinity
approximation, and unconstrained numerical optimization do not address it.

## AP8. Quantifier correction: AP2.5 itself is RH-equivalent

The earlier label "AP2 survives" meant only that no counterexample to the
special target was found. It did not check whether AP2.5 was weaker than RH.
In fact it is not. Fix any `A>0` and a beta kernel order `m_0`.

If AP2.5 holds, SC16.5--SC16.8 raise the kernel order once and use the
unconditional zeta mean-square tail to obtain global closure; SC16.2a then
gives RH.

Conversely assume RH. The strong Nyman--Beurling closure used in SC16.2 gives
finite `C_j`, with `C_j(1)=0`, such that

```text
epsilon_j=||W_(m_0)(1+zeta C_j)||_(L2(R)) -> 0.
```

Every cost `K_j=K(C_j)` and support endpoint is finite. Choose increasing
thresholds `T_j` after the approximants so that `T_j^A>=K_j`. For
`T_j<=T<T_(j+1)` use `C_T=C_j`. Then

```text
K(C_T)<=T^A,
||W_(m_0)(1+zeta C_T)||_(L2(|t|<=T))<=epsilon_j -> 0. (AP8.1)
```

The same proof works if AP2.5 is requested only along an unbounded sequence.
By AP2.4 it also proves the dual formulation. Thus, with unrestricted remote
finite support and no prescribed decay rate for delta,

```text
AP2.5  iff  SC16.8  iff  RH.                          (AP8.2)
```

This is the same reparameterization already noted in SC8/SC10 and later lost
in the handoff. A genuine scale-sensitive strengthening must tie the support or
an explicit coefficient formula to T, or prescribe an error rate that cannot
be achieved by choosing T after a qualitative global approximant. Merely
proving a polynomial K in a freely delayed window is an RH-equivalent endpoint,
not an independent norming lemma.

## AP6. Exact physical-space/divisor expansion of MB1

Let

```text
R_X(s)=1+zeta(s)C_X(s)=sum_(r>=1)q_X(r)r^(-s)          (AP6.1)
```

in the Abel sense. In `Re s>1`,

```text
q_X(r)=1_(r=1)+a_X-b_X(r),
b_X(r)=sum_(d|r,d<=X)mu(d)w_X(d).                      (AP6.2)
```

Put

```text
A_m(Y)=sum_(ell<=Y) ell(1-ell/Y)^m,
S_(X,m)(y)=sum_(r<=y)q_X(r)r(1-r/y)^m.                 (AP6.3)
```

For `h_m(v)=exp(-3v/2)(1-exp(-v))^m 1_(v>=0)`,
`W_m(1/2+it)` is its Fourier transform. Therefore Mellin--Plancherel gives the
exact global identity

```text
(1/(2pi)) integral_R |W_m(s)R_X(s)|^2dt
 = integral_1^infinity |S_(X,m)(y)|^2 dy/y^4.          (AP6.4)
```

Indeed, the inverse Fourier transform is
`exp(-3v/2)S_(X,m)(exp(v))`. This also supplies an Abel justification: at each
fixed v the physical sum contains only `r<=exp(v)`.

Changing `r=d ell` in (AP6.2) gives, for every y,

```text
S_(X,m)(y)=(1-1/y)^m+a_X A_m(y)
 -sum_(d<=min(X,y))mu(d)w_X(d)d A_m(y/d).              (AP6.5)
```

### AP6.1 exact k=1 bulk identity

For `k=1` and `1<=y<=X`, use

```text
sum_(d|n)mu(d)=1_(n=1),
sum_(d|n)mu(d)log d=-Lambda(n).                        (AP6.6)
```

Writing

```text
P_m(y)=sum_(n<=y)n Lambda(n)(1-n/y)^m,
D_m(y)=P_m(y)-A_m(y),
L=log X,
```

(AP6.5) becomes

```text
S_(X,m)(y)=a_X A_m(y)-P_m(y)/L
          =(a_X-1/L)A_m(y)-D_m(y)/L.                  (AP6.7)
```

Thus MB1 contains the explicit necessary bulk condition

```text
integral_1^X |(a_X-1/logX)A_m(y)
              -D_m(y)/logX|^2 dy/y^4 ->0.             (AP6.8)
```

This is a centered prime-square energy with the Abel boundary `a_X-1/logX`
kept in the same square. PNT gives pointwise `D_m(y)=o(y^2)` and
`a_X~1/logX`, but its known error after insertion in an interval of length X
does not imply (AP6.8). Taking absolute values destroys the possible joint
cancellation. Conversely, the `y^(rho+1)` scale from a zero with
`Re rho>1/2` is exactly large enough to obstruct the energy, consistent with
MB1 implying RH.

For comparison, `k=0` gives `S=a_X A_m(y)` throughout `y<=X`; since
`A_m(y)>=c_m y^2`, global closure would force
`sqrt(X)|sum_(n<=X)mu(n)/n|->0`. The first logarithmic Riesz smoothing is
therefore structural, not cosmetic.

The remaining exact task is to expand (AP6.5) on `y>X` and decide whether that
tail is controlled by the same centered quantity or creates a second
independent RH-scale term.

## AP7. The `y>X` tail is the same-scale Möbius obstruction

For general fixed k, add and subtract the unrestricted divisor sum in
(AP6.5). With `L=log X` this leaves the exact moving tail

```text
H_(X,k,m)(y)=sum_(X<d<=y)mu(d)(1-log(d)/L)^k
              d A_m(y/d),                    y>X.     (AP7.1)
```

The remaining full-divisor part is a finite combination of the Selberg
convolutions generated by `mu(d)(log d)^j`; for k=1 it is precisely the
centered prime expression (AP6.7). Thus

```text
S_(X,1,m)(y)=(a_X-1/L)A_m(y)-D_m(y)/L
             +H_(X,1,m)(y),                 y>X.      (AP7.2)
```

On the first moving block `X<y<2X`, `1<y/d<2`, so only ell=1 occurs in
`A_m(y/d)` and

```text
H_(X,k,m)(y)=sum_(X<d<=y)mu(d)
 (1-log(d)/L)^k d(1-d/y)^m.                           (AP7.3)
```

Here

```text
|1-log(d)/L|^k=(log(d/X)/L)^k <=(log 2/L)^k.           (AP7.4)
```

This is only a fixed logarithmic gain. Partial summation with the classical
PNT zero-free-region bound for `M(u)` gives at best

```text
|H_(X,k,m)(y)| <<_(k,m)
 X^2 exp(-c(log X)^alpha)/(log X)^k                  (AP7.5)
```

uniformly on this block (with the standard admissible alpha<1). Squaring and
inserting into `integral_X^(2X)|H|^2y^(-4)dy` yields an upper bound of order

```text
X exp(-2c(log X)^alpha)/(log X)^(2k),                 (AP7.6)
```

which does not tend to zero. Increasing any fixed k cannot bridge the missing
power `X^(1/2)`. Letting k grow with X would violate MB1's fixed-parameter
quantifier and the fixed-kernel lifting logic.

This does not prove H itself is large: separating it from (AP7.2) by triangle
inequality may discard a real cancellation. It proves the narrower and useful
negative result that finite logarithmic Riesz smoothing plus PNT cannot close
MB1. The exact candidate has returned to the already identified moving
same-scale signed Möbius obligation; a proof needs square-root-scale joint
cancellation of (AP7.2), not a better absolute envelope.

**Route verdict.** MB1 remains logically possible but supplies no independent
producer beyond the Nyman same-scale gap. It is archived as an explicit test
form rather than treated as a new lever.

## AP9. MB1 window quantifiers collapse to one explicit global norm

For fixed `m,k`, set

```text
G_(m,k)(X)=integral_R |W_m(1/2+it)R_X(1/2+it)|^2dt.   (AP9.1)
```

If `X=T^B` and `0<B<2m+1`, AP5.4 gives

```text
0 <= G_(m,k)(T^B)-E_(m,k,B)(T)
   <<_m T^(-2m-1)+T^(B-2m-1)log T=o(1).              (AP9.2)
```

Consequently MB1 is equivalent to `G_(m,k)(X_j)->0` along an unbounded
sequence `X_j`: one direction uses (AP9.2), and conversely choose
`T_j=X_j^(1/B)` and use `E<=G`.  The exponent `B` contains no arithmetic rate;
it only makes the frequency cutoff exhaust the global norm.  By AP6.4 this is
also exactly

```text
integral_1^infinity |S_(X,m)(y)|^2dy/y^4 ->0.         (AP9.3)
```

The standard Nyman--Beurling/Burnol distance lower bound gives
`G_(m,k)(X)>=c/log X` up to normalization for every support-`X` approximant.
Thus no prescribed power decay can be imposed to create an L79-style rate
producer; the natural possible scale is at best logarithmic.

### Targeted literature check

Báez-Duarte's 2002 paper explicitly records the same Selberg logarithmic
weight `mu(n)(1-log n/log N)` but does not prove its `L2` convergence from RH;
its proved construction instead uses an `N`-dependent power tilt.  Conrey--
Myerson prove uniform convergence of the associated sawtooth sum, but their
Remark 1 identifies the missing small-variable weighted-`L2` term as a Riesz--
Möbius scalar; their introduction reports full convergence only with RH plus
an extra zero-separation hypothesis.  See arXiv:math/0205003 and
arXiv:math/0002254.

Our Abel correction `a_X` is not identical to their uncorrected mollifier, so
these papers neither prove nor refute MB1.  They do rule out citing pointwise
uniform convergence or RH alone as the missing producer.  The remaining claim
is still the whole signed square (AP7.2), with prime, Abel, and moving Möbius
terms kept together.

## AP10. inverse-zero-derivative residue estimates are not multiplicity-uniform

Bettin--Conrey--Farmer (arXiv:1211.5191) obtain the conjectural optimal
Nyman--Beurling scale under RH together with

```text
sum_(|Im rho|<=T) 1/|zeta'(rho)|^2 << T^(3/2-delta).  (AP10.1)
```

Condition (AP10.1) already implies that every zero in the sum is simple: a
multiple zero has `zeta'(rho)=0`.  RH itself says nothing about multiplicity.
Hence this residue method cannot supply an RH-only converse for MB1, much less
an unconditional producer.  Replacing simple residues by the Laurent
principal part at a zero of multiplicity `r` introduces derivatives through
order `r` and requires corresponding uniform bounds; it does not remove the
hidden dependence.

## AP11. exact log-Cesaro representation; generic scale monotonicity is false

Write `L=log X` and

```text
P_v(s)=sum_(n<=exp(v)) mu(n)n^(-s).
```

The vanishing of the logarithmic Riesz weight at the moving endpoint gives,
without a boundary term,

```text
L M_(exp L)(s)=integral_0^L P_v(s)dv,
L C_(exp L)(s)=integral_0^L [P_v(1)-P_v(s)]dv.        (AP11.1)
```

Consequently the full residual is exactly

```text
R_(exp L)(s)=(1/L)integral_0^L Q_v(s)dv,
Q_v(s)=1+zeta(s)[P_v(1)-P_v(s)].                     (AP11.2)
```

Thus AP7.2 is a cross-scale cancellation problem, not a hidden pointwise
estimate. In the Hilbert space with norm `||W_m times||_2`, put
`A_L=L^(-1)integral_0^L Q_vdv`. At regular L,

```text
d/dL ||A_L||^2=(2/L)(Re<A_L,Q_L>-||A_L||^2).         (AP11.3)
```

There is no generic sign. A scalar step path taking successively the values
`1,-1,1` makes the Cesaro energy decrease and then increase. Jensen only gives
`||A_L||^2 <= L^(-1)integral_0^L||Q_v||^2dv`, which asks for control of the
sharper residuals and loses the only possible cancellation.

Therefore the sole internally generated candidate is a Möbius-specific signed
cross-scale correlation theorem for `Re<Q_u,Q_v>`. Without an identity or
inequality for that correlation, it is exactly equivalent to AP7.2 and is not
a producer.

This does not refute fixed-log mollifier convergence.  It closes only the
proposal to import the known optimal-polynomial theorem while suppressing its
simplicity/inverse-derivative hypothesis.
