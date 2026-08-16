# Prime--arch drift pairing audit

## Finite block: the positivity requirement is nonempty

Pair a prime mode of drift `-a` with an archimedean mode of drift `+a` and
use the real block

```text
L(q)=[[-a, q],[-q, a]],  a=1/2.                  (PA1)
```

For `q>a`, put `c=-a/q` and

```text
G(q)=[[1,c],[c,1]].                               (PA2)
```

Then `G(q)>0` and direct multiplication gives

```text
L(q)^T G(q)+G(q)L(q)=0.                           (PA3)
```

The eigenvalues are `+/- i sqrt(q^2-a^2)`.  Thus opposite drift can genuinely
be neutralized in a positive norm at every finite cutoff; the P41 acceptance
condition is not vacuous.

## Infinite prime lattice: local finiteness fails

The p-th defect circle has frequencies

```text
omega_(p,k)=2*pi*k/log p,  k in Z.                (PA4)
```

Apply PA1 with an arbitrary prime-dependent `q_p>a` uniformly to all modes of
that circle.  The paired frequencies become

```text
omega_(p,k) +/- c_p,
c_p=sqrt(q_p^2-a^2).                              (PA5)
```

For every real `c_p`, choose an integer k nearest to
`-c_p log(p)/(2*pi)`.  Then

```text
|omega_(p,k)+c_p| <= pi/log p.                    (PA6)
```

As `p->infinity`, the right side tends to zero.  Hence every neighborhood of
zero contains eigenvalues from infinitely many prime blocks, regardless of
how fast `q_p` grows.  The infinite direct sum has non-discrete spectrum with
an accumulation at zero; its resolvent is not compact and no ordinary
Fredholm spectral determinant can equal Xi.

This is a uniform-in-prime failure hidden by every finite cutoff.  Moving the
blocks by larger couplings cannot fix it because the lattice spacing itself
is `2*pi/log p -> 0`.

## Verdict

Modewise opposite-drift pairing is a valid finite-dimensional positive toy
but not an infinite arithmetic operator.  A surviving singular coupling must
mix different primes/frequencies strongly enough to destroy the local lattices
before taking the limit.  Such mixing must also avoid the forbidden
distinct-prime orbit terms of PS3/P40 and retain the exact Euler determinant;
no explicit construction with these three properties is currently present.
