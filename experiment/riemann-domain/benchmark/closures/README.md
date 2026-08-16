# Curated closed-route certificates

> **Disclaimer:** These are AI-generated claims and reproducibility artifacts,
> not peer review or an endorsed mathematical result. RH remains unsolved. The
> curator only organized and published the material; see the
> [full bilingual disclaimer](../../README.md#disclaimer--免責聲明).

The full handoff contains many “closed” labels with very different evidentiary
weight. This folder keeps four consequential closures whose narrow claims can
be independently checked from a short argument and a standalone Python file.

“Closed” always means the stated auxiliary implication or mechanism is false.
It never means RH is false, RH is proved, or every route in the broader family
has been eliminated.

The scripts reproduce the finite algebra or interval certificate stated in the
paired argument. A passing script does not independently peer-review the
reduction from the original research question to that certificate; a serious
audit must read both the argument and verifier.

These four were selected because each closes a consequential mechanism, states
a narrow falsifiable claim, preserves the argument that connects the claim to
the research route, and has a standalone exact-arithmetic or interval-arithmetic
verifier. They are examples of the strongest reproducible closures in the log,
not an assertion that every other route was exhaustively audited.

Commands below run from the repository root.

## 1. Cubic/J12 information does not lift to all Jensen degrees

**In plain language.** Success for degree three cannot automatically be
promoted into a theorem for every degree.

**Closed claim.** Hyperbolicity of the shifted cubics, even together with the
global J12 covariance corridor, does not imply quartic hyperbolicity. Adding
complete monotonicity of the J12 sequence still does not imply all-degree
hyperbolicity.

**Why this matters.** A large part of the early experiment established degree-3
Jensen control. Without this counterexample, it was easy to keep treating that
progress as the seed of an automatic all-degree induction.

**Certificate.** `verify_degree3_not_degree4.py` uses exact integer resultants
and discriminants. It constructs an infinite positive J12-compatible sequence
whose first two shifted cubics have positive discriminant while the quartic has
negative discriminant. `verify_complete_monotone_j12_not_uniform.py` gives the
stronger Hausdorff-moment sequence `C_k=1/[4(k+2)]`; an exact rational Sturm
chain finds only 6 real roots in its degree-10 Jensen polynomial.

**Does not close.** Direct all-degree structure special to the actual Xi
coefficient array, such as a genuinely stronger total-positivity theorem.

Argument: [`arguments/xi_jensen_route.md`](arguments/xi_jensen_route.md)
(especially the internally numbered J58 and J61 steps).

```powershell
python experiment/riemann-domain/benchmark/closures/verifiers/verify_degree3_not_degree4.py
python experiment/riemann-domain/benchmark/closures/verifiers/verify_complete_monotone_j12_not_uniform.py
```

## 2. Two natural Nyman Gram-matrix shortcuts are false

**In plain language.** Two tempting matrix-positivity shortcuts fail on exact
counterexamples, so numerical conditioning alone cannot supply this proof step.

**Closed claim.** The relevant Gram matrix is not diagonally dominant in the
needed sense and is not totally positive via the tested `2,3,4` minor.

**Why this matters.** Either property would have supplied an elementary
positivity/conditioning path around the signed same-scale Nyman obstruction.
The exact counterexamples stop that shortcut before further numerical Gram
optimization is mistaken for a proof mechanism.

**Certificate.** `verify_nyman_gram_counterexamples.py` uses only rational
arithmetic. Finite partial sums plus an exact `1/(M+1)` tail enclosure prove a
positive diagonal-dominance violation and a strictly negative upper bound for
the total-positivity minor.

**Does not close.** The Nyman–Beurling criterion itself, a different basis, or a
nonlocal signed cancellation theorem.

Argument:
[`arguments/nyman_cholesky_positivity_audit.md`](arguments/nyman_cholesky_positivity_audit.md).

```powershell
python experiment/riemann-domain/benchmark/closures/verifiers/verify_nyman_gram_counterexamples.py
```

## 3. The actual Riemann kernel is not PF5

**In plain language.** A concrete fifth-order total-positivity condition fails
for the actual Riemann kernel, closing that particular classical route.

**Closed claim.** The actual kernel fails Pólya-frequency order 5: a specified
`5x5` ordered translation determinant at `(u0,h)=(0.01,0.05)` is strictly
negative.

**Why this matters.** PF5—and therefore PF-infinity—would have provided a
classical Schoenberg total-positivity route toward higher Jensen
hyperbolicity. This is a counterexample in the actual kernel, not a toy model.

**Certificate.** `verify_phi_pf5_arb.py` evaluates the determinant twice, using
Arb's matrix determinant and the explicit 120-term Leibniz formula. The theta
tail is enclosed by the bound documented in the file and argument; both
intervals are strictly negative and overlap.

**Does not close.** Lower PF orders, non-Toeplitz positivity, or another
all-degree mechanism not implying PF5.

Argument: [`arguments/phi_pf5_audit.md`](arguments/phi_pf5_audit.md).

```powershell
python -m pip install "python-flint==0.9.0"
python experiment/riemann-domain/benchmark/closures/verifiers/verify_phi_pf5_arb.py
```

## 4. The T11 determinant-pushforward positivity conjecture is false

**In plain language.** The surviving rank-7 construction eventually becomes
negative, so it cannot represent the positive measure that this route needs.

**Closed claim.** The specific rank-7 determinant pushforward in T11 cannot be
a positive measure. Its left-tail coefficient `C_7` is strictly negative, so
the pushforward density is negative on a sufficiently far-left interval.

**Why this matters.** T11 was the surviving attempt to recover positivity only
after a determinant pushforward, after pointwise derivative-kernel positivity
had failed. A rigorous negative asymptotic coefficient closes that precise
escape rather than merely showing an unstable finite sample.

**Certificate.** `certify_t11_asymptotic_obstruction.py` combines an exact
asymptotic reduction with 192-bit Arb enclosures, analytic theta/u tail bounds,
and composite-midpoint error bounds. The default run certifies an upper bound
for `C_7` below zero.

**Does not close.** Every determinant identity, every possible pushforward, or
all nonstationary positivity constructions.

Argument:
[`arguments/toeplitz_uniform_route.md`](arguments/toeplitz_uniform_route.md)
(the internally numbered T11–T13 steps).

```powershell
python -m pip install "python-flint==0.9.0"
python experiment/riemann-domain/benchmark/closures/verifiers/certify_t11_asymptotic_obstruction.py
```

The default T11 certificate takes roughly ten seconds on the machine used for
this snapshot. All scripts exit nonzero when their asserted certificate fails.
Hashes are recorded in `SHA256SUMS`.
