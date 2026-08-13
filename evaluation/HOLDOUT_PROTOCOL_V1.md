# Phase A holdout protocol v1

## Frozen inputs

- Fixtures: `evaluation/holdout-fixtures-v1.json`
- Fixture count: 16 unique packets — 10 seeded findings, 6 verified-clean cases
- Conditions per repeat: 36
- Repeats: 2
- Total planned calls: 72
- Randomization seed: `20260815`
- Provider/model: `openai/gpt-5.6-sol`
- Reviewer CLI: `codex-cli 0.147.0`
- Live gating: off
- Finding minimum length: none
- Finding hard limit: 52 characters

SHA-256 values frozen before any reviewer call:

- `evaluation/holdout-fixtures-v1.json`: `2d4e0b8a2afa34f829bd6df2138b9f3b60acc525b3405b2ea1eedddbd2d923c7`
- `buddy-prompt.txt`: `f76a64c860bd9a1c8c52542cc7957fcfddcada3a8787535bca4ffafe767897ba`
- `evaluation/quality_eval.py`: `dfa78671791658ac1d0d794b4bb63697e95986c297ce5c56f20b2c41d092eba8`
- `reaction-schema.json`: `03100643dc4042c439021fb976d6134218b387d3dd2788ca527f8f44479cc86b`

No fixture, oracle concept group, prompt, scorer, or schema may be changed after calls begin. A wording mismatch is adjudicated separately and remains visible in the automatic score.

## Coverage

- Lifecycle findings: Design, Build, Evolve, Review
- Specialist findings: Lamport and Carmack
- General high-risk findings: destructive scope, failed verification claim, secret logging, missing release artifacts
- Clean silence: one case for each lifecycle lens and each specialist
- Stop and checkpoint evidence packets

## Predeclared round gate

This is a holdout round gate, not yet the full roadmap Phase A promotion gate.

For the effective-lens condition:

1. Raw schema compliance: `32/32`.
2. Provider success: at least `31/32`.
3. Known-issue status recall: at least `18/20`.
4. Correct silence: at least `11/12`.
5. Human-adjudicated issue target and packet grounding: at least `30/32` overall.
6. No unsupported high-severity finding on a clean packet.

For specialist takeovers:

- Compare each effective specialist output with its lifecycle-primary control.
- No more than one human-adjudicated paired loss across the 8 matched pairs.

Diagnostics that are not gates:

- Finding length, hitting the 52-character ceiling, punctuation, latency, token use, and diff-like wording.
- Acknowledgement or stylistic preference is not evidence of quality.

## Adjudication boundary

- Automatically correct seeded issue matches and correct silence need no manual override.
- Automatic mismatches and alternative findings receive condition-blind semantic and grounding review.
- Manual review cannot add vocabulary to this frozen oracle.
- Because fixtures and adjudication are authored by the same agent, results remain a pilot until independently authored cases or a second blind rater are added.
