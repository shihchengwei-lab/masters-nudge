# Historical prerelease benchmark snapshot

This directory retains one historical prerelease benchmark snapshot:
[`final02.json`](final02.json). It was produced from plugin source commit
`ac090a9f34ff76b826ceedb10361f7d7a3bd4ed3` and does not validate the current
source tree.

## Result

`final02` is a fixed-order, descriptive A/B run over four additional,
previously unused SWE-bench Verified tasks. Both arms used `gpt-5.6-sol` at
medium reasoning in fresh workspaces from the same frozen task trees. Arm A
disabled plugin hooks; Arm B enabled that historical plugin snapshot with
Anthropic `claude-opus-5` as reviewer.

| Task | Arm A | Arm B | B findings / injected / observed |
|---|---:|---:|---:|
| `django__django-16631` | pass | pass | 2 / 2 / 2 |
| `pytest-dev__pytest-6197` | pass | pass | 2 / 2 / 2 |
| `sphinx-doc__sphinx-9229` | fail | pass | 1 / 1 / 1 |
| `sympy__sympy-18199` | fail | fail | 1 / 1 / 1 |

Arm A passed 2/4 and Arm B passed 3/4. Six Arm B reviewer findings were
generated, injected, and followed by a recorded response observation. T03
differed by arm; T04 failed the same hidden test in both arms.

## Exclusion

The first T04 scoring invocation omitted the runtime executable and was marked
as an infrastructure error. The invalid score files were discarded, then both
unchanged run outputs were scored again with the same frozen 114 test nodes.

## Claim boundary

This sample has a one-task descriptive difference between arms. It is not a
concurrent randomized trial and does not establish a stable effect size, prove
generalization, or causally attribute T03 or any later action to a Nudge. The
injected receipts and response observations establish delivery order only.
