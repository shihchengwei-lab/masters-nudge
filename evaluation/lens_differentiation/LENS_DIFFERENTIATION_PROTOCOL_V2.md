# Six-lens differentiation protocol v2

Frozen before v2 reviewer calls on 2026-08-13.

V1 used a completion claim whose stated acceptance evidence was missing. The
shared stop-the-line contract correctly dominated four lifecycle overlays, so V1
answers convergence under a delivery contradiction rather than differentiation
during ordinary work. Its successful execution remains unchanged at
`evaluation/results/lens-differentiation-v1-20260813/execution-v2/`.

V2 asks the original question at a non-terminal first-large-change checkpoint.
The task is explicitly still exploring; no completion or success is claimed.

## Fixed comparison

- One checkpoint packet, six visible non-urgent tensions, six lens overlays.
- Same packet, base prompt, schema, provider, model, and 52-character cap.
- Three repeats per lens; 18 calls; randomized seed `20260824`; two workers.
- Production reviewer: `openai` / `gpt-5.6-sol` through `codex-cli 0.147.0`.
- Only the persona header and overlay differ.
- Hero rule: lowest repeat with a valid finding; no wording edits.
- Automated and human gates are unchanged from V1: all transports valid, at
  least two findings per lens, six unique selected lines, repeated theme signal,
  no imitation, hard-cap compliance, then six-of-six human semantic alignment.

## Frozen SHA-256

| Artifact | SHA-256 |
|---|---|
| checkpoint fixture | `7578e35293715c76909e4a6ca625249726162b9945e653d85c898abdd3b8986f` |
| v2 runner | `69bff3ae9a3e3bce92af165ebfe3eb980d99ff78bc9e09942b8d7b570c71fe3d` |
| v2 analyzer entry point | `a59e673f8cf430de4beea13f7b790db57a32a57f44f00782dd3ff76728f82504` |
| shared call implementation | `dad625bade4c8ec0acef669f3f832a08556d3b09f95cda6b715f5f4e4635ce76` |
| shared analysis rubric | `5a3a7803ea76a439196740554348bb76e56e2fae3fbe1cfdf9c294a2b739011c` |
| base prompt | `d79ac82a7608c73b38f4321abf21c756cbdf4b73b071e564d1c4bc5e8b251878` |
| output schema | `03100643dc4042c439021fb976d6134218b387d3dd2788ca527f8f44479cc86b` |

Persona overlay hashes remain those frozen in
`LENS_DIFFERENTIATION_PROTOCOL_V1.md`; no product prompt or overlay changed
between V1 and V2.
