# Workflow observation scenes differentiation protocol v2

Frozen before round-2 reviewer calls on 2026-08-13.

## Round-1 evidence

The first scene draft preserved the prior 5/6 semantic stability result. Fowler
again aligned in 1/3 repeats, while two repeats selected Beck's more salient
feedback or stopping concern. Nine findings hit 52 characters and seven were
incomplete. The run is preserved under
`evaluation/results/lens-observation-scenes-20260813/execution-v1/`.

## Revision hypothesis

Concrete imagery alone does not control candidate selection. Scenes should be
procedural: when their distinctive evidence operation succeeds, that candidate
should take priority over adjacent non-urgent lens concerns. Scene detail must
remain internal and must not add material to the Nudge body.

## Changes from round 1

- The shared persona header says to complete the scene's evidence operation and
  prioritize a directly supported, lens-specific tension unless a shared
  stop-the-line condition applies.
- It explicitly says scene imagery is not output material and must not increase
  Nudge length.
- Fowler says that visible duplication across two or more locations should be
  followed through as change propagation rather than replaced by generic
  feedback, scope, or system-boundary concerns.
- The six observation scenes, V2 packet, base prompt, schema, model, seed,
  repeats, workers, and runner remain otherwise unchanged.

## Fixed execution and gates

- Packet SHA-256: `557e5e0c798d8c097b7a4cf33d797ca3b29334db1c716dc94bed10ab65234e4f`
- Provider/model: `openai` / `gpt-5.6-sol`
- Reviewer CLI: `codex-cli 0.147.0`
- Three repeats per lens; 18 calls; seed `20260824`; two workers
- Output: `evaluation/results/lens-observation-scenes-20260813/execution-v2/`

Primary gates remain Fowler alignment at 2/3 or better, every other lens at 2/3
or better, no persona imitation, and all findings complete within 52 characters.
The prior no-scene V2 result remains the product comparison baseline.
