# Workflow observation scenes — round 3 length trial

Executed on 2026-08-13 through the production OpenAI reviewer path
(`gpt-5.6-sol`, `codex-cli 0.147.0`).

## Bottom line

The prompt-only 36–42-character target and terminal-punctuation instruction did
**not** prevent hard-cap truncation. All 18 paid calls returned findings and all
six lenses retained 3/3 semantic alignment, but five findings hit exactly 52
characters. Three ended mid-thought and two formed complete thoughts without
the required final punctuation.

Fifteen of 18 findings were semantically complete, 13/18 ended in terminal
punctuation, only one landed inside the 36–42 target range, and two additional
complete findings were shorter than 36 characters. The mean was 46.7
characters. The automated differentiation gates passed, but the preregistered
completion gate failed.

## Comparison

| Metric | Scene round 2 | Length trial |
|---|---:|---:|
| Semantically stable lenses | 6/6 | **6/6** |
| Lens-aligned repeats | 18/18 | **18/18** |
| Complete thoughts | **17/18** | 15/18 |
| Terminal punctuation | not separately scored | 13/18 |
| Exact 52-character hits | **2/18** | 5/18 |
| Findings delivered | 18/18 | **18/18** |
| Persona names in findings | 0 | 0 |

## Exact-cap outputs

- Beck 2: `local-json 尚未端到端驗證，範圍已擴到三個未使用 backend；pilot 的停止條件在哪裡`
- Beck 3: `local-json 尚未端到端試跑，範圍已擴到三個未用 stub 與 cloud，關鍵假設仍沒得到回饋`
- Lamport 3: `search index 已更新但 version state 未寫入就 timeout，retry 時`
- Carmack 1: `benchmark只量同一程序的熱路徑，尚無冷啟動CLI基線，擴充cloud前仍不知道pilot的真實瓶`
- Carmack 2: `local-json 尚未端到端實跑，也沒有 cold CLI 基準，擴充 cloud 的決定仍缺少所需`

The raw structured outputs already ended at 52 characters, so the production
sanitizer did not cause these cuts. A textual instruction is therefore not a
reliable closure mechanism under the schema's hard decoder limit.

## Claim boundary

This is a post-hoc length experiment on the same development fixture. It shows
that the proposed prompt wording is insufficient; it does not change the prior
fixed-packet differentiation finding or establish holdout reliability.

Raw outputs, manifest, automated analysis, selection, and human adjudication are
under `execution-v3/`.
