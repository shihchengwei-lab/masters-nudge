# Six-lens differentiation result

Executed 2026-08-13 with the production OpenAI reviewer path
(`gpt-5.6-sol`, `codex-cli 0.147.0`).

## Bottom line

The six overlays **can produce six meaningfully different workflow Nudges from
the same checkpoint**, but the differentiation is not equally reliable yet.
Five lenses stayed on their declared concern in 3/3 repeats. Fowler produced the
distinct duplicated-knowledge concern in 1/3 repeats and otherwise converged on
Jeff's broader responsibility-boundary concern.

Therefore:

- demonstration claim: supported — six unedited, grounded, distinct
  representatives exist from one fixed packet;
- reliability claim: not yet supported — the preregistered six-of-six stability
  gate failed (5/6 stable).

## Controlled result

All 18 calls used the same evidence packet, model, base prompt, schema, and
52-character limit. Only the persona header and overlay differed.

| Lens | Aligned repeats | Primary attention in the run | Hero repeat |
|---|---:|---|---:|
| Jeff Dean | 3/3 | Early multi-backend boundary creates downstream abstraction cost | 3 |
| Kent Beck | 3/3 | Scope expands before the first end-to-end feedback loop | 1 |
| Martin Fowler | 1/3 | The same rules are duplicated across three entry paths | 3 |
| Linus Torvalds | 3/3 | Transfer layers and unused stubs lack necessary behavior | 1 |
| Leslie Lamport | 3/3 | Index-before-version state breaks retry ordering | 1 |
| John Carmack | 3/3 | A warm best-of loop is not a cold CLI baseline | 3 |

Integrity and schema transport were 18/18. Every run returned a finding; all 18
wordings were distinct and none imitated or named a master. The automated theme
gate failed, consistent with the semantic audit rather than hidden by exact-text
uniqueness.

## Length finding

Four of 18 responses reached exactly 52 characters. Three ended as incomplete
thoughts despite the 42-character soft target. This does not change the hard cap
in this work, but it is evidence that dense packets can still consume the entire
buffer. The hero excludes incomplete lines through a separately documented
editorial rule; it does not rewrite them.

## Why the first comparison converged

The first fixture was a stop event whose completion claim lacked evidence for an
explicit delivery condition. The shared stop-the-line rule correctly took
priority, so Jeff, Beck, Fowler, and Linus mostly surfaced the same validation
contradiction. That run is preserved under
`evaluation/results/lens-differentiation-v1-20260813/execution-v2/`; it shows
expected convergence in urgent conditions, not a failed overlay implementation.

V2 removed the completion claim and tested an ordinary in-progress checkpoint.
No product prompt or overlay changed between those comparisons.

## Real Tk hero

The editorial selection chooses the lowest complete, lens-aligned result that
keeps the six concerns distinct. Every line is byte-for-byte identical to its
recorded model result. Six real `BuddyWindow` instances read ordinary JSONL log
entries through the production `_read_new` path; the hero is a direct Windows
desktop capture, not an AI-generated mockup.

- Hero: `docs/images/masters-nudge-six-lenses-hero.png`
- Six individual captures: `execution-v1/screenshots/`
- Formal selection: `execution-v1/hero-selection.json`
- Editorial selection: `execution-v1/hero-selection-editorial.json`
- Automated analysis: `execution-v1/analysis.json`
- Human audit: `execution-v1/human-adjudication.json`
- Raw outputs: `execution-v1/runs.json`

| Artifact | SHA-256 |
|---|---|
| hero PNG | `c840680a71103ff4eaeb7ccfc7e57a3a0c9985c5a9be0052874c897e7fda6960` |
| raw runs | `416793894ee72fb94d622540ce0f5f943744df821b436eb914c3fd6cb0cf3bc4` |
| automated analysis | `1a5ef01fc0f4bd5a75cc4ec90a1493c479ddd5055f553cd413e06c49c1ccf319` |
| human audit | `7b1d343098479e2f024182d4e9611a019d186bb65f092a6b01c2d34f81bc7f25` |
| editorial selection | `ea6b2a3c00b418be4c8d5d3a05cdd259d94dfea2aae16a3eb83f675a7735311d` |

## Tooling incident found during the run

The installed npm Codex CLI was `0.130.0` and could not parse current `ultra` /
`max` reasoning levels, making the production OpenAI provider return transport
errors. It was upgraded to `0.147.0`; a production-path preflight then returned a
valid schema result before the complete batch ran. The failed transport batch is
retained as `evaluation/results/lens-differentiation-v1-20260813/execution-v1/`.
