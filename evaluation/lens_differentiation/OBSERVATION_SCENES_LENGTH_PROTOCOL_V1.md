# Workflow observation scenes length protocol v1

Frozen before round-3 reviewer calls on 2026-08-13.

## Round-2 evidence

Procedural observation scenes produced semantic alignment in all 18 findings,
but one finding ended mid-thought at exactly 52 characters. Seventeen of 18
findings were complete, and two findings hit the hard cap. The run is preserved
under `evaluation/results/lens-observation-scenes-20260813/execution-v2/`.

## Hypothesis

A soft 36–42-character target range plus an explicit terminal-punctuation
instruction will encourage the model to close the sentence before the unchanged
52-character hard cap. The range is not a minimum: a shorter complete finding
is valid.

## Single intervention

- Replace the 42-character completion target with a 36–42-character target
  range.
- Require `finding` to end with `。`, `？`, `！`, or the corresponding English
  terminal punctuation; punctuation counts toward the hard cap.
- Keep the 52-character schema cap, parser behavior, sanitizer, personas,
  procedural scenes, packet, provider, model, and runner unchanged.
- Do not reject an otherwise valid finding, retry the model, or add another
  paid call when the punctuation instruction is missed.

## Fixed execution and gates

- Packet SHA-256: `557e5e0c798d8c097b7a4cf33d797ca3b29334db1c716dc94bed10ab65234e4f`
- Provider/model: `openai` / `gpt-5.6-sol`
- Reviewer CLI: `codex-cli 0.147.0`
- Three repeats per lens; 18 calls; seed `20260824`; two workers
- Output: `evaluation/results/lens-observation-scenes-20260813/execution-v3/`

Primary gates are 18/18 delivered findings, 18/18 complete findings ending in
terminal punctuation, no finding over 52 characters, Fowler alignment at 2/3
or better, every other lens at 2/3 or better, and no persona imitation. Exact
52-character hits are reported but are not independently a failure when the
sentence is complete.

This reuses a post-hoc development fixture and therefore tests the length
intervention only; it does not replace the planned holdout reliability test.
