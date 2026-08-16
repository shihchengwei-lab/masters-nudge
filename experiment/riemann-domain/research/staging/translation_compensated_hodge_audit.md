# Translation-compensated arch--prime Hodge candidate

## 1. Candidate: change the representation, not the label

Let `P` denote the primes and let

```text
F = exterior l2(P),                 e_S, S a finite prime set,
H_F e_S = (sum_(p in S) log p)e_S,
A = L2(R,dt),                       (M f)(t)=t f(t),
(U_p f)(t)=f(t+log p).
```

Write `a_p^*` for fermionic creation. On `F tensor A` put

```text
H = H_F tensor I + I tensor M,
Q_(sigma,P0) = sum_(p<=P0) p^(-sigma) a_p^* tensor U_p.       (1.1)
```

This differs from P21's diagonal determinant: the archimedean coordinate
translates whenever a prime is created. Since

```text
[H_F,a_p^*]=(log p)a_p^*,
M U_p=U_p M-(log p)U_p,
```

the changes cancel and `[H,Q_(sigma,P0)]=0` on the algebraic core. Thus P22's
unique-energy obstruction does not apply: different prime subsets are coupled
at the same total energy.

## 2. Exact finite-cutoff calculation

Set `b_p^*=a_p^* tensor U_p`. The translations commute, so the
`b_p,b_p^*` obey the CAR. Consequently, for every finite cutoff,

```text
Q_(sigma,P0)^2=0,
{Q_(sigma,P0),Q_(sigma,P0)^*}=C_(sigma,P0) I,
C_(sigma,P0)=sum_(p<=P0) p^(-2sigma).                         (2.1)
```

Equation (2.1) is an exact Hodge identity and supplies a positive norm and an
explicit differential.

## 3. Infinite-prime pressure test

### 3.1 `sigma>1/2`: well-defined but acyclic

Here `C_sigma=sum_p p^(-2sigma)<infinity`. The partial sums converge in
operator norm to a bounded differential `Q_sigma`, and (2.1) passes to the
limit. The contracting homotopy is `Q_sigma^*/C_sigma`; hence every closed
vector is exact and the Hilbert cohomology is zero. Moreover `H` contains the
full multiplication continuum `M`, so this region supplies neither nonzero
cohomology nor a compact-resolvent spectral model.

### 3.2 `sigma=1/2`: the natural critical sum has no dense domain

Let `Q_X` be (1.1) with `sigma=1/2` and primes `p<=X`, and define the natural
maximal strong-sum domain by convergence of `Q_X psi`. Let `P_0,P_1` be the
vacuum and one-particle fermion projections. If `P_0 psi=1 tensor f`, then

```text
P_1 Q_X psi=sum_(p<=X) p^(-1/2)e_p tensor U_p f,
||P_1 Q_X psi||^2=(sum_(p<=X)1/p)||f||^2.                    (3.1)
```

The summands are orthogonal in the prime label and the prime harmonic sum
diverges. No higher fermion component can cancel (3.1), since creation sends
it to degree at least two. Thus convergence forces `f=0`:

```text
Dom(strong-sum Q_(1/2)) subset ker P_0.
```

`ker P_0` is a proper closed subspace, so the domain is not dense. The
critical formal differential therefore has no Hilbert adjoint or Hodge
operator. For `sigma<1/2` the same obstruction is stronger.

### 3.3 Cutoff normalization does not repair the target

For each finite `X`, division by
`sqrt(C_X)`, `C_X=sum_(p<=X)1/p`, makes the Hodge Laplacian exactly `I`. But
every fixed local coefficient becomes

```text
p^(-1/2)/sqrt(C_X) -> 0,
```

while the vacuum image retains norm one and escapes through new orthogonal
prime directions. Hence the normalized cutoffs have no coefficient-faithful
strong limit; taking `X->infinity` and normalizing do not commute, and fixed
local Euler weights are lost.

## 4. Verdict and exact scope

The candidate survives the algebraic tests that killed ordinary Hodge
pairing: it is nilpotent, energy preserving, positive and archimedean-nonlocal.
Its first failure is later and exact:

```text
finite cutoff:       exact positive Hodge identity and acyclic;
infinite sigma>1/2: bounded, exact, but acyclic and continuous-spectrum;
critical sigma=1/2: natural differential is not densely defined;
normalized cutoff:  loses each fixed prime coefficient and has no strong limit.
```

Translation compensation is therefore excluded as a critical Hilbert Hodge
realization. This does not exclude all singular cohomologies: a future
candidate needs a specified renormalized dense domain whose limit retains the
local prime weights, plus a self-adjoint induced operator with locally finite
spectrum. Subtracting the scalar `C_X I` is insufficient because the
obstruction occurs before the adjoint exists.

## 5. Minimal finite-prime compatibility audit

The three requested properties are not contradictory for one prime. Let
`ell=log p`, take `A=l2(Z)`, and set

```text
M e_n=n ell e_n,                 U e_n=e_(n-1),
H=H_F tensor I+I tensor M,       Q=p^(-1/2)a_p^* tensor U.
```

Then `Dom M` is dense, `M` and `H` have compact resolvent, the coefficient is
unchanged, and `Q` is bounded with `Q^2=0`, `[H,Q]=0`, and
`{Q,Q^*}=p^(-1)I`.

The minimal obstruction appears at two distinct primes. Suppose a
self-adjoint `M` with locally finite pure-point spectrum admits global
unitaries satisfying

```text
M U_r=U_r M-(log r)U_r,           r=p,q.            (5.1)
```

If `M f=lambda f`, then `U_p^m U_q^n f` is a nonzero eigenvector with
eigenvalue

```text
lambda-m log p-n log q,           m,n in Z.          (5.2)
```

The ratio `log p/log q` is irrational: otherwise `p^a=q^b` for some positive
integers `a,b`. Hence (5.2) is dense in `R`, contradicting local finiteness.

Thus the sharp finite-prime dichotomy is

```text
one prime:  dense domain + exact weight + compact resolvent coexist;
two primes: exact global translations force non-locally-finite spectrum.
```

This is independent of `sigma` and precedes the prime-harmonic divergence.
Escaping it requires partial or nonunitary maps, after which positivity, the
CAR identity and closability all need new proofs.

## 6. Executable unilateral repair: algebra survives, Euler data cancels

Replace each unitary `U_p` by the backward shift `L_p` on a bosonic ladder
`l2(N_0)`. Then `M_p L_p=L_p M_p-(log p)L_p`; the one-sided semigroup avoids
the dense two-prime orbit and has locally finite spectrum. With

```text
Q=sum_p c_p a_p^* tensor L_p
```

the commuting ladders still give `Q^2=0` and `[H,Q]=0`. The infinite complex
has only the joint vacuum in its Hodge kernel. This apparent repair has an
exact partition-function cost: per prime,

```text
(fermion supertrace) x (boson trace)
=(1-p^(-s))/(1-p^(-s))=1.                         (6.1)
```

For a finite ladder `0<=n_p<=N`, exact cohomology consists of the vacuum plus
top-boundary corners and its supertrace is

```text
product_p (1-p^(-(N+1)s)) -> 1.                   (6.2)
```

`experiments/probe_unilateral_prime_hodge.py` verifies `Q^2`, energy
commutation, the full Hodge matrix, kernel dimension and (6.2) using exact
rational arithmetic for one, two and three primes. Thus the nonunitary repair
does not fail on domain or local finiteness; it fails by cancelling precisely
the Euler factor it was meant to retain. Finite-box extra cohomology is a
moving upper-boundary artifact.

The cancellation is not a consequence of `[H,Q]=0` alone. A finite ladder of
length `N+1` is already a counterexample: its combined factor is
`1-p^(-(N+1)s)`, not `1`. Exact cancellation is forced only for the complete
one-sided tensor ladder with one state at every nonnegative prime energy.
