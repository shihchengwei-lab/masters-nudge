# Workflow observation scenes — round 2

Executed on 2026-08-13 through the production OpenAI reviewer path
(`gpt-5.6-sol`, `codex-cli 0.147.0`).

## Bottom line

Procedural observation scenes improved differentiation on the fixed V2 packet
from **5/6 stable lenses to 6/6**. Every lens aligned with its declared concern
in all three repeats, including Fowler, which improved from 1/3 to 3/3.

The unchanged automated differentiation gates all passed. No finding named or
imitated a persona, and all findings stayed within the 52-character hard cap.

The stricter completeness gate narrowly failed: one Jeff finding ended mid-thought
at exactly 52 characters. Seventeen of 18 findings were complete. This result
supports improved differentiation on the fixed packet, not general six-lens
reliability.

## Comparison

| Metric | No-scene V2 baseline | Scene round 1 | Scene round 2 |
|---|---:|---:|---:|
| Semantically stable lenses | 5/6 | 5/6 | **6/6** |
| Fowler aligned repeats | 1/3 | 1/3 | **3/3** |
| Automated theme-aligned lenses | 4/6 | 5/6 | **6/6** |
| Complete findings | 15/18 | 11/18 | **17/18** |
| Exact 52-character hits | 4/18 | 9/18 | **2/18** |
| Persona names in findings | 0 | 0 | 0 |

## What changed after round 1

The six scene texts stayed unchanged. The shared overlay header made the scene's
evidence operation control candidate selection when directly supported, instead
of treating the scene as atmosphere. Fowler also explicitly prioritizes visible
knowledge propagation over adjacent generic feedback, scope, or system-boundary
concerns. Scene imagery remains internal and is not output material.

## Claim boundary

The result is an A/B-style comparison against a preserved run using the same
packet, provider, model, schema, cap, repeats, seed, workers, and production
runner. Round 2 was refined after observing round 1 on this fixture, so the 6/6
result requires a new holdout packet before supporting a general reliability
claim.

Raw outputs, manifest, automated analysis, selection, and human adjudication are
under `execution-v2/`.
