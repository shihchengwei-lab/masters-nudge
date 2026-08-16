# Prime point-scatterer representation audit

## Candidate

Keep one exponential-wall channel, so the archimedean Weyl density is not
multiplied. Put an energy-independent self-adjoint point scatterer at
`L_p=(1/2)log p` for each prime. A boundary-to-scatterer round trip then has
length `2L_p=log p`, matching the first Euler orbit. Self-adjointness would
protect the spectrum from nonreal collisions.

## Exact two-scatterer obstruction

For two real delta couplings `g_p,g_q`, the relative determinant is exactly

```text
det(I+G_k V)
 =(1+g_p G_pp)(1+g_q G_qq)-g_p g_q G_pq^2.       (PS1)
```

This is the two-by-two matrix determinant lemma. The same mixed path occurs
for any local scatterers having nonzero reflection amplitudes. At large
positive evanescent parameter `k`, the one-dimensional Green kernel has

```text
G_k(L_p,L_q)=c(k,L_p,L_q) exp(-k|L_q-L_p|),
c nonzero and algebraic in k.                     (PS2)
```

The exponential wall changes the algebraic WKB prefactor, not the shortest
path length. Consequently the logarithm of PS1 contains the nonzero mixed
orbit

```text
-g_p g_q c(k,L_p,L_q)^2 exp(-2k|L_q-L_p|).        (PS3)
```

For `p=2,q=3`, PS3 has length `2(L_3-L_2)=log(3/2)`. Euler's logarithm has
only lengths `m log r`, with `r` prime and `m>=1`. There is no `log(3/2)`
term; moreover `log(3/2)<log 2`, so PS3 precedes every Euler correction and
cannot be hidden in a tail or cancelled by later prime scatterers. Its
coefficient vanishes only if one of the two reflection channels vanishes,
which also removes the corresponding prime orbit.

## Verdict and dependency

The single-channel local point-scatterer candidate is refuted already by the
primes 2 and 3. This uses only the exact two-point determinant and
shortest-path asymptotic, not zero locations or RH.

Putting primes on separate channels removes mixed paths, but P9--P10 already
prove that the channel count changes the Weyl density from the single Xi
phase volume to `Theta(lambda^(3/4))`, and positive Weyl residues cannot
cancel it. A surviving domain construction must therefore be genuinely
nonlocal: suppress every distinct-prime mixed orbit while retaining one
archimedean phase volume and every same-prime repetition.
