# Numerical experiments (not proof)

## NE1. Freedman coordinate-kernel point-Gram scan

`experiments/freedman_kernel_gram_scan.py` evaluates the original coordinate
kernel by adaptive quadrature and tests finite point-Gram matrices. For
`omega=0.49`, 18 points in `[-3,3]`, one uniform grid and eight seeded random
grids, the smallest eigenvalue normalized by the spectral norm ranged down to
`-4.42e-14`; all negative values were at floating-point/ill-conditioning
scale. This is consistent with positivity but neither interval-certified nor
uniform in the number/configuration of points, so it is not used in WD3 or any
proof ledger. Its purpose is only to check that the analytic normalization and
sign in WD1 do not immediately conflict with the paper's finite observations.

As a route discriminator, the same script was run on model kernels. Gaussian
and a symmetric Gaussian bimodal kernel showed only roundoff-scale negative
eigenvalues, while `exp(-|t|)` gave order `1e-1` negative directions. More
decisively, the analytic strictly log-concave model
`exp(-t^2)(1+0.1 cos t)` gave a normalized minimum `-2.43e-5` at
`omega=.49`, 24 points in `[-6,6]`. WD6 proves independently that this model's
Fourier transform has nonreal zeros, so the numerical failure is expected.
This rules out a generic log-concavity heuristic but says nothing by itself
about the Riemann kernel.
## DN30 vertical-phase sign certificate (2026-08-16)

`experiments/certify_dn30_vertical_phase_failure.py` uses 320-bit Arb series for the completed
zeta function at Arb-enclosed zeta zeros. It rigorously proves

```text
J(x_1)<0<J(x_35),
J=H'H''-HH'''.
```

The positive ball at `x_35=223.749318353985274...` is centered at
`3.8297432059114923e-73` with radius below `2.42e-163`. This is a proof certificate, not a
floating observation. It falsifies only fixed-sign vertical phase velocity; it neither falsifies RH nor
the DN27 collision-degree identity. Full output and interpretation are in
`experiments/results_dn30_vertical_phase_failure_2026-08-16.md`.

## Theta-mode Arb certificates (2026-08-16)

`certify_first_theta_mode_nonreal_zero.py` rigorously encloses a unique simple
nonreal zero of the first theta-mode cosine transform near
`20.6253460059+2.69715184234i`. It uses 256-bit Arb integration, analytic
incomplete-gamma tails, and strict complex interval-Newton inclusion.

`certify_two_theta_mode_collision.py` proves a regular double zero in the
amplitude homotopy `T_1+lambda T_2`, at `x=22.142377661...` and
`lambda=0.916291688...`. These are proof certificates, not floating scans.
Their outputs are recorded in the two corresponding `results_*` files. They
do not test RH; they falsify first-mode and finite-mode homotopy producers.
