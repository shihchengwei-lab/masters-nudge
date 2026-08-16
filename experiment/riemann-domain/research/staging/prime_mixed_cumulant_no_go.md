# Positive mixed-cumulant no-go

Let `H=direct_sum_p H_p` be an orthogonal prime grading. In the Euler
half-plane suppose `K(s)` is trace class, self-adjoint for real s, and

```text
K(s)_(p,q)=exp[-s(log p+log q)/2] B_(p,q),
B_(q,p)=B_(p,q)^*.                                (PMC1)
```

Ask that `det(I-K(s))=product_p(1-p^(-s))`, with the diagonal one-prime
blocks fixed by the local Euler data. The convergent logarithm is

```text
log det(I-K)=-sum_(m>=1) Tr(K^m)/m.               (PMC2)
```

For distinct primes p,q, the length `log(pq)` contribution in `Tr(K^2)` is

```text
Tr(B_(p,q)B_(q,p))=||B_(p,q)||_HS^2 >=0.          (PMC3)
```

Euler's logarithm has only lengths `m log r`; its coefficient at a distinct
product `pq` is zero. Unique factorization excludes a one-prime repetition
of this length, and a cycle of at least three positive prime lengths cannot
have product `pq`. Thus PMC3 cannot be cancelled. Exact determinant equality
forces

```text
B_(p,q)=0 for every p!=q.                         (PMC4)
```

Positive semigroup-covariant determinant realizations therefore cannot mix
prime sectors. P42 proves that blockwise prime--arch pairing without such
mixing has infinite spectral accumulation at zero. Hence local spectral
finiteness and exact Euler determinant are incompatible in this
determinant-class, length-covariant framework.

An escape must abandon ordinary trace-class determinants, orthogonal positive
prime grading, or semigroup length covariance. Scalar zeta regularization
abandons determinant class, but P31--P33 show that it supplies no positive
spectral projectors and moves the divisor into scalar counterterms.
