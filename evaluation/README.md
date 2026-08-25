# Final benchmark evidence

This directory intentionally retains only the final benchmark result:
[`final01.json`](final01.json).

## Result

`final01` is a fixed-order, descriptive A/B run over four previously unused
SWE-bench Verified tasks. Both arms used `gpt-5.6-sol` at medium reasoning in
fresh workspaces from the same frozen task trees. Arm A disabled plugin hooks;
Arm B enabled the plugin snapshot built from commit `e1a35d4` with Anthropic
`claude-opus-5` as reviewer.

| Task | Arm A | Arm B | B findings / injected / observed |
|---|---:|---:|---:|
| `pytest-dev__pytest-10051` | pass | pass | 1 / 1 / 1 |
| `django__django-17084` | pass | pass | 2 / 2 / 2 |
| `sphinx-doc__sphinx-9591` | pass | pass | 1 / 1 / 1 |
| `sympy__sympy-17630` | pass | pass | 1 / 1 / 1 |

Arm A passed 4/4 and Arm B passed 4/4. Five Arm B reviewer findings were
generated, injected, and followed by a recorded response observation. Only the
Beck and Linus lenses appeared, so the preregistered six-lens condition for a
hero image was not met and no hero was created.

## Exclusions

- `astropy__astropy-13579` failed preflight because the retained runtime lacked
  required in-place compiled extensions. No main-model run started, and the
  candidate is outside the denominator.
- The first T03/T04 attempts used each task's `ISSUE.md` directly instead of the
  frozen common task prompt. All four attempts were excluded before analysis;
  official T03/T04 runs were repeated from exactly rematerialized baseline
  commits with the frozen prompt.

## Claim boundary

This sample shows no outcome difference between arms. It is not a concurrent
randomized trial and does not establish a stable effect size, prove
generalization, or causally attribute any result or later action to a Nudge.
The injected receipts and response observations establish delivery order only.
