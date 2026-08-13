# Workflow Holdout V2 — R2 Result

## Outcome

The rewritten workflow-review prompt **passes all 8 preregistered pilot gates**. In the `effective` condition, all 24 seeded workflow blind spots produced grounded, target-relevant, lens-aligned, workflow-level, complete Nudges; none collapsed into local code-only critique and none hit the 52-character cap.

This establishes a Phase A pilot quality floor. It does **not** establish downstream task impact: fixtures are synthetic, repeats are limited to two, and condition-blind adjudication used one author-rater.

## Design

- 18 unique packets: two workflow blind spots and one seeded clean workflow for each of six lenses.
- Two repeats; 36 baseline + 36 effective + 12 specialist-primary calls = 84.
- Provider/model: OpenAI `gpt-5.6-sol`; isolated Codex CLI 0.147.0.
- Fixed 52-character maximum; no minimum.
- All outputs were shuffled and adjudicated before condition identities were opened.
- Full preregistration and frozen hashes: [WORKFLOW_HOLDOUT_PROTOCOL_V2.md](../../WORKFLOW_HOLDOUT_PROTOCOL_V2.md).

The first 84-row batch is excluded in full: the unchanged resolver ignored the attempted `BUDDY_CODEX_BIN` override and selected global CLI 0.130.0, which exited before generation on current `max` reasoning metadata. R2 prepended the isolated CLI directory to PATH and passed a non-holdout transport preflight. See [WORKFLOW_HOLDOUT_PROTOCOL_V2_R2.md](../../WORKFLOW_HOLDOUT_PROTOCOL_V2_R2.md).

## Preregistered gates (`effective`)

| Gate | Floor | Result | Pass |
|---|---:|---:|:---:|
| Provider / raw schema | ≥35/36 / 36/36 | 36/36 / 36/36 | ✓ |
| Finding recall | ≥21/24 | 24/24 | ✓ |
| Seeded correct silence | ≥11/12 | 11/12 | ✓ |
| Human-valid workflow warning | ≥20/24 | 24/24 | ✓ |
| Intended-lens alignment | ≥20/24 | 24/24 | ✓ |
| Local-artifact-only critique | ≤2/24 | 0/24 | ✓ |
| Invalid-decision delta vs baseline | ≤+2 | −2; 2 wins, 0 losses | ✓ |
| Specialist losses vs lifecycle primary | ≤1/12 | 0/12 | ✓ |

## Condition comparison

| Condition | Positive recall | Seeded silence | Human-valid positives | Complete positives | Local-only | Cap hits |
|---|---:|---:|---:|---:|---:|---:|
| Baseline (general only) | 24/24 | 10/12 | 22/24 | 22/24 | 0/24 | 2 |
| Effective routed lens | 24/24 | 11/12 | 24/24 | 24/24 | 0/24 | 0 |
| Lifecycle primary on specialist cases | 8/8 | 4/4 | 8/8 | 8/8 | 0/8 | 1 |

The general rewrite itself already shifted outputs to workflow review: blind adjudication found 24/24 baseline positives workflow-level and 0/24 local-only. The overlays preserved that direction and removed both incomplete baseline answers in the matched comparison (34 ties, 2 effective wins, 0 losses).

Representative `effective` outputs:

| Lens | Nudge |
|---|---|
| Jeff | canonical owner 未定卻讓三方都能改角色；同步與修復是在替責任邊界未定還債。 |
| Beck | 驗收與既有測試都已通過，後續重構是在替哪個尚未出現的需求工作？ |
| Fowler | 先擴張 430 行再補特性測試，JSON 不變的邊界已被延後驗證。 |
| Linus | 完成宣告已越過必要驗證：Windows 與 Linux 的乾淨安裝都未執行。 |
| Lamport | 若扣款後、寫 marker 前中斷，retry 時「最多一次」還成立嗎？ |
| Carmack | 沒有 baseline 與 profiler 就續調 thread pool，現在量到的瓶頸是什麼？ |

## 52-character inspection

Only three of 59 findings reached exactly 52 characters; none came from the effective routed-lens condition.

| Condition | Complete | Output |
|---|:---:|---|
| Baseline | No | 沒有 baseline、profiler 與等價檢查，現在調 thread pool 是在改善哪個已確認 |
| Baseline | No | 同一程序內的 benchmark 無法驗證 cold start，也未涵蓋首次輸出一致性，完成宣告跑在驗 |
| Lifecycle primary | Yes | 三種優化已疊上去，卻還沒量 baseline 或確認輸出等價，thread pool 的下一步要驗證哪個 |

So 52 characters **can** be insufficient, but it was not a failure mode of the rewritten effective prompt in this sample. A cap hit is not automatically incomplete: the third output remains a self-contained interrogative despite lacking final punctuation. Keep the cap for now and monitor natural traces; do not optimize toward shorter text merely to avoid the diagnostic.

## Seeded-clean contamination

The only `effective` seeded-silence miss was this Fowler output:

> 只用一個 YAML 案例，還看不出純資料模型是否真能承接兩種格式的共同知識。

The packet itself says YAML has only one minimal case. The same concern appeared in both baseline repeats and one effective repeat. Blind adjudication therefore marked all three findings grounded and workflow-valid, while retaining the original `no_finding` oracle for the preregistered silence score. The fixture is not clean enough for a confirmatory benchmark; the next version should either supply representative YAML validation evidence or relabel/replace the case before freezing.

## Audit artifacts

- Raw R2 rows SHA-256: `d4ce3ede1cc652e9055461c8b425f2f5c6f6dac1d53e21b9a269f355f7d211dc`
- Blind packet SHA-256: `ef659fb7c71e7849da6efcd7c571600ad5516d40bd16232d409bb68f1a72c957`
- Frozen judgments SHA-256: `3343102f36900413badec57319c7acdfc811ea41635fead9e9bee73b2aec743d`
- Machine-readable metrics: [workflow-summary.json](workflow-summary.json)
- Condition-blind judgments: [blind-judgments.json](blind-judgments.json)
- Fully joined adjudication: [adjudicated.json](adjudicated.json)

## Next evaluation

Treat the current prompt as the candidate rather than rewriting it again from this pilot. First run a confirmatory Phase A set with the contaminated clean case repaired, natural project traces added, and at least one independent rater. If that preserves grounding, silence, workflow level, and completeness, proceed to the preregistered Phase B comparison: identical agent tasks with Nudge injected versus withheld, scored on executable acceptance evidence rather than whether the agent merely acknowledges the Nudge.
