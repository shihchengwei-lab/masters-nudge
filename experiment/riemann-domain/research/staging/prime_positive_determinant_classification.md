# Classification of positive Euler determinant realizations

Assume that in a right half-plane

```text
K(s)=sum_p p^(-s) A_p                              (PDC1)
```

converges in trace norm, every `A_p` is positive trace class, and

```text
det(I-K(s))=product_p(1-p^(-s)).                   (PDC2)
```

No orthogonal prime grading is assumed.

For large real s, expand `log det(I-K)=-sum_(m>=1)Tr(K^m)/m` and compare
absolutely convergent Dirichlet coefficients.

At the integer p, PDC2 gives

```text
Tr A_p=1.                                         (PDC3)
```

At `p^2`, only the second cumulant contributes, so

```text
Tr(A_p^2)=1.                                      (PDC4)
```

If the eigenvalues of positive `A_p` are `lambda_j>=0`, PDC3--4 say
`sum lambda_j=sum lambda_j^2=1`.  Hence exactly one eigenvalue is 1 and all
others vanish: `A_p` is a rank-one orthogonal projection.

For distinct primes p,q, the coefficient at `pq` is

```text
-Tr(A_p A_q).
```

Euler's logarithm has coefficient zero there, so

```text
Tr(A_p A_q)=Tr(A_p^(1/2) A_q A_p^(1/2))=0.        (PDC5)
```

The operator inside the last trace is positive; it must vanish.  Thus the
ranges of `A_p` and `A_q` are orthogonal.

Therefore every positive trace-class Dirichlet realization PDC1--2 is
unitarily equivalent to the obvious diagonal prime operator.  Positivity and
exact Euler coefficients leave no nonorthogonal cross-prime freedom.

Combined with P41--P43, this closes the ordinary positive determinant escape:
the unique realization has the fixed `-1/2` defect drift; modewise arch
pairing has zero accumulation; and any attempted positive mixing would create
forbidden composite cumulants.  Signed/super determinants evade positivity
but return to the P22 energy-degeneracy obstruction; regularized determinants
return to P31--P33 scalar counterterms.
