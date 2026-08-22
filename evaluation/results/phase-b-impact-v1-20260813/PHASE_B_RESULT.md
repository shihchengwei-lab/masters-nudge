# Phase B V1 result

## Outcome

**Positive pilot signal: no.** Treatment tied control at 13/18 full-task passes and 64/69 components. Across 18 matched pairs, treatment recorded one win and one loss, for net zero.

All 36 rows were valid, so the negative gate result is not an authentication, transport, timeout, or grader-execution artifact.

## Gates

| Gate | Result | Measurement |
|---|---|---|
| Run integrity | Pass | 36/36 rows; 36/36 agent-valid; 36/36 grader-valid |
| Treatment not lower | Pass | treatment 13/18; control 13/18 |
| Paired net benefit | **Fail** | 1 win; 1 loss; net 0 (required at least +3) |
| Benefit spans tasks | **Fail** | 0/6 tasks with positive net benefit (required at least 2) |
| No majority harm | Pass | no task lost at least 2/3 treatment pairs |

## Task discrimination

- `clean-install-proof`, `cold-start-cli`, `csv-scope-control`, and `discount-policy-home`: both conditions passed 3/3. These tasks were ceiling-saturated.
- `last-query-wins`: treatment had one win, one loss, and one both-fail pair. It was the only task with paired discrimination, but netted to zero.
- `onboarding-problem-location`: both conditions passed 0/3 and 3/4 components each time. Every run corrected phone normalization; the only failed component required deleting `reminder_service.py`, while the agents reverted it to the baseline placeholder with no reminder mechanism. The frozen score remains unchanged, but this oracle should be repaired before reuse.

## Diagnostics

Relative to control, treatment used USD 0.240309 more (+9.7%), averaged 0.44 more turns (+4.2%), and averaged 3.276 seconds more wall time (+11.2%). These are diagnostics, not preregistered gates.

## Decision

Do not advance the current task set as evidence that the injection improves main-agent outcomes. Preserve this run as the V1 null pilot. The next iteration should improve task discrimination before changing the General prompt again: reduce ceiling tasks, replace or harden the floor task, and keep enough matched repeats to distinguish prompt effects from run variance.

The machine-readable analysis, raw rows, and all 36 workspaces are preserved in
the verified
[`evidence-archive-2026-08-22`](https://github.com/shihchengwei-lab/masters-nudge/releases/tag/evidence-archive-2026-08-22)
release.
