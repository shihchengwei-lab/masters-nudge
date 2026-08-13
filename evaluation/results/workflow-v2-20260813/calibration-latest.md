# Phase A reaction-quality evaluation

- Generated: 2026-08-13T01:43:09.991066+00:00
- Provider/model: `openai` / `gpt-5.6-sol`
- Fixtures: `evaluation\workflow-holdout-v2.json`
- Repeats: 2
- Randomization seed: 20260816
- Git commit: `06a110e2e668a3dcf8045646e7fb5a33b4355533`
- Fixtures SHA-256: `12cf1aefd98c83b813e63b45abc6d1d9a8c1a30bf3c9519d4e41d15e43fc5ef9`
- Runner SHA-256: `dfa78671791658ac1d0d794b4bb63697e95986c297ce5c56f20b2c41d092eba8`
- Base prompt SHA-256: `baa7af2b101dfd0b2a70b5d404a3ee09c01c48f648c3c059d83943783d23b80f`
- Reviewer CLI: `codex-cli 0.130.0`
- Interpretation: calibration only; not a formal product-impact claim.

## Condition summary

| Condition | Calls | Provider success | Raw schema | Status | Issue match | Correct silence | Avg chars | At 52 | Sentence ended | Oracle match | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 36 | 0/36 (0.0%) | 0/36 (0.0%) | 0/36 (0.0%) | 0/24 (0.0%) | 0/12 (0.0%) | 0.0 | n/a | n/a | 0/36 (0.0%) | 14622 ms |
| effective | 36 | 0/36 (0.0%) | 0/36 (0.0%) | 0/36 (0.0%) | 0/24 (0.0%) | 0/12 (0.0%) | 0.0 | n/a | n/a | 0/36 (0.0%) | 14086 ms |
| primary | 12 | 0/12 (0.0%) | 0/12 (0.0%) | 0/12 (0.0%) | 0/8 (0.0%) | 0/4 (0.0%) | 0.0 | n/a | n/a | 0/12 (0.0%) | 16598 ms |

## Paired outcomes

- `effective_vs_baseline`: 0 wins, 36 ties, 0 losses
- `effective_vs_primary`: 0 wins, 12 ties, 0 losses

## Per-call results

| Fixture | Condition | Lens | Expected | Actual | Chars | Schema | Match | Ended | Correct | Finding |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| workflow-beck-clean-short-feedback-loop | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-beck-clean-short-feedback-loop | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-beck-clean-short-feedback-loop | effective | beck | no_finding | error | 0 | False | False | None | False |  |
| workflow-beck-clean-short-feedback-loop | effective | beck | no_finding | error | 0 | False | False | None | False |  |
| workflow-beck-fix-thrashing-without-experiment | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-beck-fix-thrashing-without-experiment | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-beck-fix-thrashing-without-experiment | effective | beck | finding | error | 0 | False | None | None | False |  |
| workflow-beck-fix-thrashing-without-experiment | effective | beck | finding | error | 0 | False | None | None | False |  |
| workflow-beck-scope-after-acceptance | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-beck-scope-after-acceptance | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-beck-scope-after-acceptance | effective | beck | finding | error | 0 | False | None | None | False |  |
| workflow-beck-scope-after-acceptance | effective | beck | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-clean-measure-one-change | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-carmack-clean-measure-one-change | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-carmack-clean-measure-one-change | effective | carmack | no_finding | error | 0 | False | False | None | False |  |
| workflow-carmack-clean-measure-one-change | effective | carmack | no_finding | error | 0 | False | False | None | False |  |
| workflow-carmack-clean-measure-one-change | primary | fowler | no_finding | error | 0 | False | False | None | False |  |
| workflow-carmack-clean-measure-one-change | primary | fowler | no_finding | error | 0 | False | False | None | False |  |
| workflow-carmack-optimizes-before-measurement | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-optimizes-before-measurement | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-optimizes-before-measurement | effective | carmack | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-optimizes-before-measurement | effective | carmack | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-optimizes-before-measurement | primary | beck | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-optimizes-before-measurement | primary | beck | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-warm-benchmark-for-cold-goal | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-warm-benchmark-for-cold-goal | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-warm-benchmark-for-cold-goal | effective | carmack | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-warm-benchmark-for-cold-goal | effective | carmack | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-warm-benchmark-for-cold-goal | primary | linus | finding | error | 0 | False | None | None | False |  |
| workflow-carmack-warm-benchmark-for-cold-goal | primary | linus | finding | error | 0 | False | None | None | False |  |
| workflow-fowler-clean-characterize-then-change | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-fowler-clean-characterize-then-change | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-fowler-clean-characterize-then-change | effective | fowler | no_finding | error | 0 | False | False | None | False |  |
| workflow-fowler-clean-characterize-then-change | effective | fowler | no_finding | error | 0 | False | False | None | False |  |
| workflow-fowler-policy-has-no-home | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-fowler-policy-has-no-home | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-fowler-policy-has-no-home | effective | fowler | finding | error | 0 | False | None | None | False |  |
| workflow-fowler-policy-has-no-home | effective | fowler | finding | error | 0 | False | None | None | False |  |
| workflow-fowler-refactor-before-characterization | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-fowler-refactor-before-characterization | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-fowler-refactor-before-characterization | effective | fowler | finding | error | 0 | False | None | None | False |  |
| workflow-fowler-refactor-before-characterization | effective | fowler | finding | error | 0 | False | None | None | False |  |
| workflow-jeff-clean-evidence-first-design | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-jeff-clean-evidence-first-design | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-jeff-clean-evidence-first-design | effective | jeff | no_finding | error | 0 | False | False | None | False |  |
| workflow-jeff-clean-evidence-first-design | effective | jeff | no_finding | error | 0 | False | False | None | False |  |
| workflow-jeff-compensation-before-owner | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-jeff-compensation-before-owner | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-jeff-compensation-before-owner | effective | jeff | finding | error | 0 | False | None | None | False |  |
| workflow-jeff-compensation-before-owner | effective | jeff | finding | error | 0 | False | None | None | False |  |
| workflow-jeff-solution-before-problem | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-jeff-solution-before-problem | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-jeff-solution-before-problem | effective | jeff | finding | error | 0 | False | None | None | False |  |
| workflow-jeff-solution-before-problem | effective | jeff | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-clean-invariant-first | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-lamport-clean-invariant-first | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-lamport-clean-invariant-first | effective | lamport | no_finding | error | 0 | False | False | None | False |  |
| workflow-lamport-clean-invariant-first | effective | lamport | no_finding | error | 0 | False | False | None | False |  |
| workflow-lamport-clean-invariant-first | primary | linus | no_finding | error | 0 | False | False | None | False |  |
| workflow-lamport-clean-invariant-first | primary | linus | no_finding | error | 0 | False | False | None | False |  |
| workflow-lamport-delay-patches-ordering | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-delay-patches-ordering | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-delay-patches-ordering | effective | lamport | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-delay-patches-ordering | effective | lamport | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-delay-patches-ordering | primary | fowler | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-delay-patches-ordering | primary | fowler | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-happy-path-before-invariant | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-happy-path-before-invariant | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-happy-path-before-invariant | effective | lamport | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-happy-path-before-invariant | effective | lamport | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-happy-path-before-invariant | primary | beck | finding | error | 0 | False | None | None | False |  |
| workflow-lamport-happy-path-before-invariant | primary | beck | finding | error | 0 | False | None | None | False |  |
| workflow-linus-checklist-before-real-install | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-linus-checklist-before-real-install | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-linus-checklist-before-real-install | effective | linus | finding | error | 0 | False | None | None | False |  |
| workflow-linus-checklist-before-real-install | effective | linus | finding | error | 0 | False | None | None | False |  |
| workflow-linus-clean-single-path-proof | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-linus-clean-single-path-proof | baseline | general | no_finding | error | 0 | False | False | None | False |  |
| workflow-linus-clean-single-path-proof | effective | linus | no_finding | error | 0 | False | False | None | False |  |
| workflow-linus-clean-single-path-proof | effective | linus | no_finding | error | 0 | False | False | None | False |  |
| workflow-linus-layers-hide-undecided-owner | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-linus-layers-hide-undecided-owner | baseline | general | finding | error | 0 | False | None | None | False |  |
| workflow-linus-layers-hide-undecided-owner | effective | linus | finding | error | 0 | False | None | None | False |  |
| workflow-linus-layers-hide-undecided-owner | effective | linus | finding | error | 0 | False | None | None | False |  |

## Scoring boundary

`issue_match` is a deterministic concept-group check. A miss can therefore be either a true miss or a defensible wording that needs blind human adjudication. `Sentence ended` only checks final punctuation and is a review queue, not proof that wording is complete or incomplete. Raw JSONL is retained for both reviews. Correct silence is objective for these seeded clean cases.
