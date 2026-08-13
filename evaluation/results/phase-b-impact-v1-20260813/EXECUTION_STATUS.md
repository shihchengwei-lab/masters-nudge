# Phase B V1 execution status

## Completed

- Executed 2026-08-13 with the frozen Phase B V1 protocol.
- Main agent: Claude Code 2.1.215, `sonnet`, effort `medium`.
- 36/36 expected rows completed; 36/36 agent transports and graders were valid.
- No timeout, agent error, continuation, steering, retry, or manual rescue occurred.
- Runtime: approximately 9 minutes 22 seconds with two workers.
- Artifacts: 36 final-workspace archives plus the manifest, raw rows, and analysis.

## Preregistered outcome

The batch did **not** produce a positive pilot signal.

| Measure | Control | Treatment |
|---|---:|---:|
| Full-task passes | 13/18 | 13/18 |
| Components passed | 64/69 | 64/69 |
| Total cost (USD) | 2.469823 | 2.710132 |
| Mean turns | 10.39 | 10.83 |
| Mean wall time | 29.228 s | 32.504 s |

Matched pairs: 1 treatment win, 1 treatment loss, 12 both-pass, and 4 both-fail; net benefit 0. The exact one-sided sign/binomial diagnostic is 0.75.

Passed gates: run integrity, treatment not lower than control, and no task majority harm. Failed gates: paired net benefit and benefit spanning at least two tasks.

## Interpretation boundary

This frozen result is evidence of **no measured benefit in this pilot**, not evidence that the Nudge is harmful. Four tasks were ceiling-saturated in both conditions, one task was floor-saturated, and only `last-query-wins` produced discordant pairs.

The `onboarding-problem-location` floor also exposed an oracle-semantic issue: all six runs fixed phone normalization and removed the reminder implementation, but retained the baseline placeholder module. The frozen grader requires the file itself to be absent, so all six failed its final component. This observation does not change the preregistered score.

See [analysis.json](execution-v1/analysis.json), [runs.jsonl](execution-v1/runs.jsonl), and [PHASE_B_RESULT.md](PHASE_B_RESULT.md).
