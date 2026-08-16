# Audit of the Nyman--Cholesky positivity conjecture

## NC1. External conjecture

Bellemare--Langlois--Ransford define

\[
 f_k(x)=k^{-1}[1/x]-[1/(kx)]
\]

and their Gram--Schmidt vectors `e_j`. Conjecture 9 is

\[
 L_{kj}:=\langle f_k,e_j\rangle>0\qquad(2\le j\le k). \tag{NC1.1}
\]

Equivalently, all indicated bordered Gram determinants are positive. This is
a genuine all-size determinant conjecture. The paper reports extensive
computations, but explicitly leaves open whether it implies RH or follows from
RH.

The Nyman distance is

\[
 d_n^2=1-\sum_{j=2}^n|\langle1,e_j\rangle|^2,
\]

and RH is equivalent to `d_n->0`. Cholesky positivity concerns `L`; closure
concerns the norm of `E=L^{-1}F`, where `F_k=<1,f_k>=log(k)/k`.

## NC2. Exact abstract counterexample to the missing implication

Entrywise positivity of the whole Cholesky factor, even with a strictly
positive right side, does not force closure. Let

\[
 \mathcal H=\ell^2(\mathbb N)\oplus\mathbb R u
\]

with `u` orthogonal to `ell^2`. Choose the bounded invertible lower-triangular
operator

\[
 L=I+\eta T,\qquad (Tx)_k=\sum_{j<k}2^{-(k-j)}x_j,\qquad 0<\eta<1/2. \tag{NC2.1}
\]

All entries on and below its diagonal are strictly positive. Let `e_j` be the
standard basis and `f_k=sum_(j<=k)L_kj e_j`. Gram--Schmidt recovers `e_j`, so
the Cholesky entries are exactly those of `L`. Choose a strictly positive
`c in ell^2` and put `v=u+c`. Then

\[
 \langle v,f_k\rangle=(Lc)_k>0, \tag{NC2.2}
\]

but the distance from `v` to the closed span of all `f_k` is `||u||>0`.
Therefore (NC1.1) plus positive data does not abstractly imply closure.

## NC3. The special remote column is an unbounded boundary functional

Put

\[
 a_k={k-1\over k},\qquad F_k={\log k\over k},\qquad
 A=L^{-1}a,qquad E=L^{-1}F. \tag{NC3.1}
\]

The Mellin formula from the paper gives, for every fixed `j`,

\[
 {\rm Res}_{s=0}\int_0^1e_j(x)x^{s-1}\,dx={A_j\over2},
 \qquad
 \lim_{k\to\infty}{2k\over\log k}L_{kj}=A_j. \tag{NC3.2}
\]

Indeed the residue on `f_i` is `(i-1)/(2i)`, and `e=L^{-1}f` is a
finite triangular relation in each row.  Thus Conjecture 9 implies at most
`A_j>=0`: it is positivity of the Mellin boundary functional at `s=0` on
the Gram--Schmidt basis.

This boundary vector is necessarily not square summable.  If `A in ell^2`,
then `w=sum A_j e_j` would be an `L2` vector and

\[
 \langle w,f_k\rangle=(LA)_k=a_k\longrightarrow1. \tag{NC3.3}
\]

But `0<=f_k<1` and `f_k(x)->0` for every fixed `x>0`; dominated convergence
gives `||f_k||_2->0`, contradicting (NC3.3).  Hence

\[
 \sum_{j\ge2}A_j^2=\infty. \tag{NC3.4}
\]

So the fixed-column asymptotic does not produce a bounded functional with
which one can control the Hilbert energy `sum E_j^2`.

## NC4. Exact countermodel retaining the Nyman right side and remote asymptotic

The preceding discontinuity is not merely a failure of Cauchy--Schwarz.
There exists an abstract Hilbert model having all of the following properties:

\[
 L_{kj}>0,\quad LA=a,\quad LE=F,\quad E_j>0,\quad
 \lim_{k\to\infty}{2L_{kj}\over F_k}=A_j,quad
 ||f_k||\to0, \tag{NC4.1}
\]

for every fixed `j`, while `||E||_2<1` and the target has a nonzero
orthogonal residual.

Here is a direct construction.  Write

\[
 \eta_k={F_k\over a_k}={\log k\over k-1}
\]

and choose `0<alpha<1/2` and a sufficiently small `epsilon>0`.  Set
`A_j=epsilon*j^alpha`.  Let the reservoir indices be powers of two (from
`4` onward), put `x_2=eta_2`,

\[
 x_j=2\eta_j\quad(j\hbox{ a reservoir}),\qquad
 x_j={\epsilon^2 2^{-j}\over A_j^2}\quad(j\hbox{ otherwise}),
 \qquad E_j=A_jx_j. \tag{NC4.2}
\]

Because `alpha<1/2`, both

\[
 {1\over2}\sum A_j^2x_j<\infty,qquad \sum A_j^2x_j^2<\infty. \tag{NC4.3}
\]

They can be made respectively `<1/4` and `<1` by reducing `epsilon`.
For each sufficiently large `k`, take `J(k)=floor(k^delta)` with
`0<delta<1/(2alpha+1)` and prescribe probability weights

\[
 w_{kj}={\eta_k A_j^2\over2}\qquad(j\le J(k)). \tag{NC4.4}
\]

Their total mass is `o(1)` and their `x`-mean is at most `eta_k/4`.
Give every remaining non-anchor index an arbitrarily small positive total
mass `o(eta_k)`.  The last power of two `h<=k` has
`x_h=2eta_h>=2eta_k`, whereas a non-reservoir index `l` near `k` has
`x_l=o(eta_k)`.  The two remaining positive weights on `h,l` can therefore
be chosen uniquely so that

\[
 \sum_{j\le k}w_{kj}=1,\qquad
 \sum_{j\le k}w_{kj}x_j=\eta_k. \tag{NC4.5}
\]

The finitely many initial rows are filled in the same way using the running
high and low values of `x`.  Define

\[
 L_{kj}={a_kw_{kj}\over A_j}. \tag{NC4.6}
\]

Then (NC4.5) gives `LA=a` and `LE=F`, and every entry including the
diagonal is strictly positive.  For fixed `j`, eventually (NC4.4) applies,
so `L_kj=F_kA_j/2` exactly.  Moreover

\[
 ||f_k||^2=\sum_{j\le k}L_{kj}^2
 =a_k^2\sum_{j\le k}{w_{kj}^2\over A_j^2}\longrightarrow0: \tag{NC4.7}
\]

the fixed block is
`O(F_k^2 J(k)^(2alpha+1))=o(1)`, the tiny mass is negligible, and the
two anchors tend to infinity so their `A`-denominators diverge.

Finally take
`H=ell^2({2,3,...}) direct-sum R u`, let `e_j` be its standard basis,
`f_k=sum_(j<=k)L_kj e_j`, and

\[
 v=\sum E_je_j+\sqrt{1-||E||_2^2}\,u. \tag{NC4.8}
\]

Gram--Schmidt recovers `e_j`, `<v,f_k>=F_k`, but the distance from `v` to
the closed span of the `f_k` is the positive last coefficient in (NC4.8).
Thus even positivity plus the exact Nyman right side, the exact remote-column
law, and `||f_k||->0` do not force closure.  This does not copy the full
Nyman Gram kernel; it proves that any successful implication must use that
full arithmetic kernel, not merely the listed Cholesky data.

## NC5. Ehm's q=2 Gram decomposition does not close the tail

Ehm (arXiv:2405.06349) derives explicit `q=1,2` Nyman Gram kernels and
Muentz-series decompositions.  The extra factor `|s|^-4` for `q=2` gives
stronger high-frequency damping, but the paper proves that vanishing of this
distance is still equivalent to RH.  In its quadratic-form decomposition one
decisive uncancelled term is the truncated Moebius inversion error

\[
E_a^{(q)}(N)=\sum_{m\le N}{a_m\over m}
 \left(\sum_{n\le N}a_nS_q(n/m)-R_q(1/m)\right). \tag{NC5.1}
\]

The exact inversion identity also gives

\[
 \sum_{n\le N}a_nS_q(n/m)-R_q(1/m)
 =\sum_{n\le N}(a_n-\mu(n))S_q(n/m)
  -\sum_{n>N}\mu(n)S_q(n/m). \tag{NC5.2}
\]

There is a rigorous absolute-value barrier in the second term.  The source's
large-`x` expansions show that, at sufficiently large integer `r`,
`S_1(r)>0` and `S_2(r)>0`: the leading terms are respectively proportional
to `B_2(0)r^-2>0` and `-B_4(0)r^-4>0`.  By continuity, there is a fixed ratio
interval `I` on which `|S_q(x)|>=c_q>0`.  Choose fixed positive intervals of
`m/N` and `n/N`, with `m<=N<n`, whose ratios lie in `I`.  The elementary
asymptotic density of square-free integers then gives

\[
 \sum_{m\asymp N}{|\mu(m)|\over m}
 \sum_{\substack{n\asymp N\\ n>N}}|\mu(n)S_q(n/m)|\gg_q N. \tag{NC5.3}
\]

For the Levinson--Selberg coefficient
`a_m=mu(m)(1-log(m)/log(N))`, the same fixed-fraction box gives
`>>N/log(N)`.  Thus extra `q=2` decay at `n/m->infinity` is irrelevant to
the moving boundary `n/m=Theta(1)`.  Any proof that takes absolute values of
the Moebius tail before summing cannot make (NC5.1) small; a valid estimate
must preserve two-variable arithmetic phase cancellation (and cancellation
with the first term in (NC5.2)).

The strongest directly relevant external cancellation theorem found does not
reach this boundary.  Maier--Rassias (arXiv:1806.05070, Theorem 2.1) prove,
for a cotangent/Wilton kernel `g`,

\[
 \sum_{k^D\le n<2k^D}\mu(n)g(n/k)
 \ll_\epsilon k^{D-z_0+\epsilon},\qquad D\ge2,\ z_0>0. \tag{NC5.4}
\]

This is a genuine fixed-power saving, but it is a far-ratio theorem
`n>=k^2`.  The kernel is related to, but is not identical with, Ehm's `S_q`;
even granting the needed integral transfer, (NC5.4) says nothing about
`n/k=Theta(1)`.  No primary extension to the `D=1` same-scale regime was
found.  Thus the literature input can at most help with a remote part of
(NC5.2), not its dominant moving boundary.

Ehm's reciprocity does not bridge the scale gap.  Corollary 3.1 has the form

\[
 S_q(1/r)=rS_q(r)+P_q(r,\log r), \tag{NC5.5}
\]

with an explicit elementary `P_q`.  It maps every compact ratio interval
away from zero and infinity to another such interval, so `r=Theta(1)` remains
same-scale.  Inserting `P_q` into the quadratic form produces precisely the
Landau/Mertens-type products already isolated in the paper, not a far-ratio
sum to which (NC5.4) applies.  Reciprocity is useful algebraically but cannot
turn the missing `D=1` estimate into the known `D>=2` theorem.

Finally, the exact Mellin diagonalization fixes the logical strength of any
successful recombination.  On `s=1/2+it`,

\[
 G_{m,n}^{(q)}={1\over2\pi\sqrt{mn}}
 \int_{\mathbb R}(n/m)^{it}{|\zeta(1/2+it)|^2\over
 |1/2+it|^{2q}}\,dt, \tag{NC5.6}
\]

and hence

\[
 \sum_{m,n\le N}a_ma_nG_{m,n}^{(q)}
 ={1\over2\pi}\int_{\mathbb R}
 \left|\zeta(s)\sum_{n\le N}a_nn^{-s}\right|^2
 {|ds|\over|s|^{2q}}. \tag{NC5.7}
\]

Thus the `S_q` moving boundary plus all elementary Landau/Mertens pieces,
when exactly recombined, are the original critical mollifier norm.  Proving
their required joint limit for the Levinson--Selberg coefficients is the
Nyman closure detector itself, not an upstream consequence of positivity or
reciprocity.  A noncircular proof would still need a genuinely new same-scale
arithmetic cancellation theorem established without critical continuation of
`1/zeta`.

The source explicitly calls its estimation a major challenge and sets it
aside.  Several centered Landau/Mertens products are also not proved
negligible; their plotted high correlation is only exploratory.  Thus the
decomposition does not establish closure.  Increasing the Sobolev weight is
another RH-equivalent detector unless these moving-tail terms receive new
uniform arithmetic bounds.

Primary source: https://arxiv.org/abs/2405.06349
Related far-ratio estimate: https://arxiv.org/abs/1806.05070

## NC6. Consequence

Proving the external conjecture would be an independent total-positivity
result, but not an RH proof. One still needs

\[
 \sum_{j\ge2}|(L^{-1}F)_j|^2=1, \tag{NC6.1}
\]

which is precisely the Nyman/RH endpoint. Entrywise signs, finite bordered
minors, and larger numerical batches do not control the orthogonal residual.
No later primary source proving the conjecture or this quantitative bridge was
found.

Primary source: https://arxiv.org/abs/2011.02847
