# Workflow observation scenes local-closure protocol v1

Frozen before round-4 reviewer calls on 2026-08-13.

## Round-3 evidence

The prompt-only 36–42-character target and terminal-punctuation instruction
returned findings for all 18 paid calls and preserved 6/6 lens stability, but
five findings hit exactly 52 characters. Three ended mid-thought and two lacked
the required terminal punctuation. The run is preserved under
`evaluation/results/lens-observation-scenes-20260813/execution-v3/`.

## Hypothesis

Prompt wording cannot reliably prevent a constrained structured output from
reaching its maximum length. A deterministic local fallback can preserve every
paid finding while closing a capped output at its last available clause
boundary, without widening the delivered limit or making another provider call.

## Single intervention

- Keep a finding unchanged when it already ends in terminal punctuation.
- Append suitable terminal punctuation when the finding is below 52 characters
  and has room.
- When a finding reaches 52 characters without terminal punctuation, keep the
  longest prefix ending at a comma or semicolon and replace that boundary with
  a full stop, provided the prefix contains at least 12 characters.
- If no usable clause boundary exists, compact optional CJK/Latin spacing,
  reserve the final character for terminal punctuation, and still deliver the
  finding.
- Keep the prompt, schema, parser acceptance, personas, procedural scenes,
  packet, provider, model, seed, repeats, workers, and runner unchanged.
- Never reject, retry, or make an additional paid call for closure.

## Fixed execution and gates

- Packet SHA-256: `557e5e0c798d8c097b7a4cf33d797ca3b29334db1c716dc94bed10ab65234e4f`
- Provider/model: `openai` / `gpt-5.6-sol`
- Reviewer CLI: `codex-cli 0.147.0`
- Three repeats per lens; 18 calls; seed `20260824`; two workers
- Output: `evaluation/results/lens-observation-scenes-20260813/execution-v4/`

Primary gates are 18/18 delivered findings, 18/18 complete findings ending in
terminal punctuation, no delivered finding over 52 characters, Fowler alignment
at 2/3 or better, every other lens at 2/3 or better, and no persona imitation.
The report separates raw hard-cap hits from delivered lengths and records every
finding changed by the fallback.

This reuses a post-hoc development fixture and therefore tests the deterministic
delivery behavior only; it does not replace the planned holdout reliability test.
