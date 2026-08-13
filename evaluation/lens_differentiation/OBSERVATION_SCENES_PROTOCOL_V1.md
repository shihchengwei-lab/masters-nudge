# Workflow observation scenes differentiation protocol v1

Frozen before reviewer calls on 2026-08-13.

## Hypothesis

Adding one distinct, evidence-bounded observation scene to each persona overlay
will improve procedural separation between the six lenses without turning the
Nudge into persona imitation or code review.

The main known weakness is Fowler: the prior V2 run aligned with its declared
duplicated-knowledge concern in 1/3 repeats and otherwise converged on Jeff's
broader boundary concern.

## Intervention

- Keep the V2 checkpoint fixture, base prompt, schema, model, output cap,
  repeats, random seed, worker count, and runner unchanged.
- Add `### 觀察場景` to every persona with a distinct evidence operation:
  causal backtracking, feedback-card reduction, change propagation tracing,
  layer removal, event reordering, or execution counting.
- Extend the shared persona header to define scenes as internal observation
  procedures, not biographical claims, evidence, or output style.

## Fixed execution

- Fixture: `lens-fixture-v2.json`
- Packet SHA-256: `557e5e0c798d8c097b7a4cf33d797ca3b29334db1c716dc94bed10ab65234e4f`
- Provider/model: `openai` / `gpt-5.6-sol`
- Reviewer CLI: `codex-cli 0.147.0`
- Three repeats per lens; 18 calls
- Random seed `20260824`; two workers
- Output: `evaluation/results/lens-observation-scenes-20260813/execution-v1/`

## Gates

The frozen automated V2 gates remain diagnostic and unchanged. The primary
semantic comparison is:

1. Fowler aligns with duplicated knowledge/change propagation in at least 2/3
   repeats rather than converging on Jeff.
2. Every other lens remains aligned in at least 2/3 repeats.
3. No finding names or imitates a persona.
4. Every finding remains a complete workflow Nudge within 52 characters.

Passing all four supports an improvement from the prior human-audited 5/6
stable result to 6/6 on this fixed packet. This single fixture does not establish
general six-lens reliability.
