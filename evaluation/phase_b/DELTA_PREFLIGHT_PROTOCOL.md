# Phase B candidate delta preflight

Frozen before calls on 2026-08-13 (Asia/Taipei).

## Purpose

Phase A passed before the general prompt gained this soft target:

> 優先在 42 字內完成回答閉環，為 52 字硬上限保留約 20% 緩衝。

This is a bounded version preflight, not a reopened Phase A. It checks that the Phase B candidate still emits a grounded, self-contained workflow Nudge and that the soft target does not turn into truncation.

## Cases and execution

One seeded positive is selected for each lens, plus the second Carmack case that previously produced a long baseline answer:

- `workflow-jeff-solution-before-problem`
- `workflow-beck-fix-thrashing-without-experiment`
- `workflow-fowler-policy-has-no-home`
- `workflow-linus-checklist-before-real-install`
- `workflow-lamport-delay-patches-ordering`
- `workflow-carmack-optimizes-before-measurement`
- `workflow-carmack-warm-benchmark-for-cold-goal`

Run every existing comparison route once with the frozen Phase A runner (17 calls total), seed `20260818`, two workers, OpenAI `gpt-5.6-sol`, isolated Codex CLI 0.147.0. Only the seven `effective` outputs decide the preflight; comparison routes are retained as diagnostics.

## Pass rule

- 7/7 effective calls return schema-valid findings.
- 7/7 are grounded, workflow-level, target-relevant, lens-aligned, and semantically complete.
- No effective output reaches the 52-character hard cap.
- At least 6/7 effective outputs finish within the 42-character soft target. A longer complete answer is not a failure by itself.

No selective retry or prompt change is allowed after calls begin.

## Frozen hashes (SHA-256)

```text
d79ac82a7608c73b38f4321abf21c756cbdf4b73b071e564d1c4bc5e8b251878  buddy-prompt.txt
af8f749348b40fa59097665bafbde81c116a522082b26f35bcd81d268d5c4023  buddy.py
03100643dc4042c439021fb976d6134218b387d3dd2788ca527f8f44479cc86b  reaction-schema.json
5d81c9461fbe5da1916a2371336aafb082654592b3006c6548ecb8f8e201d1eb  personas/beck.txt
53c36e02e7988cb872781a4cb298eb7d7513f92c81c88f89c4690d7222492317  personas/carmack.txt
f17ce3cf18a9bf34256bcf107bc1a70af883d933a779542d8c15b83f59175ad9  personas/fowler.txt
e23ba98b4a59447bd1756f6ba239970641891e7a0e4067c3e7019ae823b5a115  personas/jeff.txt
913b8870e8a1c565daeee78e8774747b1f6faa9a874c0dc35dfa2854611d5b9a  personas/lamport.txt
2dcf5c369e96d87cb0980d625e6d656a886e8c0406da48443ea942db98689df8  personas/linus.txt
```
