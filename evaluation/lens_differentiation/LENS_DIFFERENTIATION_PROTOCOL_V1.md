# Six-lens differentiation protocol v1

Frozen before reviewer calls on 2026-08-13.

## Question and claim boundary

Given exactly the same checkpoint evidence, do the six Masters' Nudge lens
overlays reliably direct attention to different workflow concerns?

This is an exploratory differentiation check. It does not measure downstream
agent benefit, how often each concern occurs in production, or whether the named
people themselves would write these lines. The names represent concepts and
attention areas; imitation is forbidden by the shared prompt.

## Fixed comparison

- One stop-event packet exposes six independent, visible tensions: system
  boundary, experimental scope, duplicated knowledge, unnecessary transfer
  layers, retry/order state, and unrepresentative performance measurement.
- The evidence packet, base prompt, provider, model, schema, and output limit are
  identical for all calls. Only the persona header and overlay change.
- Lenses: Jeff Dean, Kent Beck, Martin Fowler, Linus Torvalds, Leslie Lamport,
  and John Carmack.
- Three repeats per lens: 18 calls total.
- Provider/model: production default `openai` / `gpt-5.6-sol`.
- Randomized job order; seed `20260823`; two workers.
- No output rewriting. The hero uses the lowest-numbered repeat with a valid
  finding for each lens.

## Preregistered checks

Automated checks require:

1. 18 unique expected rows and valid schema transport for all calls;
2. at least two findings per lens;
3. six non-empty, pairwise-exact-unique hero lines;
4. at least one preregistered theme term in at least two repeats per lens;
5. no master name in the selected lines and no line over 52 characters.

A human semantic audit then checks each selected line for visible grounding,
workflow-level framing, a complete thought, and alignment with its declared
attention area. Differentiation passes only if all six selected lines primarily
address six distinct declared concerns. Keyword matching is diagnostic and
cannot substitute for this audit.

## Real UI evidence

The selected results are written, unchanged, as ordinary reaction JSONL entries.
`tk_capture.py` creates six real `BuddyWindow` instances, lets each instance read
its entry through the production `_read_new` path, and captures the live Windows
desktop pixels with Pillow `ImageGrab`. It saves six individual screenshots and
one six-window hero. The hero is not AI-generated and its Nudge text is not
retypeset or edited after the reviewer call.

## Frozen SHA-256

| Artifact | SHA-256 |
|---|---|
| `buddy-prompt.txt` | `d79ac82a7608c73b38f4321abf21c756cbdf4b73b071e564d1c4bc5e8b251878` |
| `reaction-schema.json` | `03100643dc4042c439021fb976d6134218b387d3dd2788ca527f8f44479cc86b` |
| `buddy_window.py` | `7d308d88606042629c7f4f758e546e9c12ff363ebed2b3cb3d0862533a5a337d` |
| fixture | `e970256ebeca34d67c26f4e53a065cf540cf3c8f59e6c1c58dfb25f588ff2be3` |
| runner | `dad625bade4c8ec0acef669f3f832a08556d3b09f95cda6b715f5f4e4635ce76` |
| analyzer | `5a3a7803ea76a439196740554348bb76e56e2fae3fbe1cfdf9c294a2b739011c` |
| Tk capture | `665660cd9d577af23cc486932393089b47e92e384c21023fe79cbeee5caf7fa7` |
| Jeff overlay | `e23ba98b4a59447bd1756f6ba239970641891e7a0e4067c3e7019ae823b5a115` |
| Beck overlay | `5d81c9461fbe5da1916a2371336aafb082654592b3006c6548ecb8f8e201d1eb` |
| Fowler overlay | `f17ce3cf18a9bf34256bcf107bc1a70af883d933a779542d8c15b83f59175ad9` |
| Linus overlay | `2dcf5c369e96d87cb0980d625e6d656a886e8c0406da48443ea942db98689df8` |
| Lamport overlay | `913b8870e8a1c565daeee78e8774747b1f6faa9a874c0dc35dfa2854611d5b9a` |
| Carmack overlay | `53c36e02e7988cb872781a4cb298eb7d7513f92c81c88f89c4690d7222492317` |
