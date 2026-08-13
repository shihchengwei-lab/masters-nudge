# Phase A pilot validation summary

## Outcome

這輪足以證明評估鏈路可用，也得到一個可重現的 lifecycle-lens 訊號；但還不足以宣告正式 Phase A 過關，更不能開始 Phase B。

正式統計只使用 scorer 凍結後的新 run：12 個 synthetic fixtures、2 次 repeat、56 次 reviewer calls。較早的 28-call run 用來校準 oracle 詞表，排除於本表之外。所有條件固定使用 `openai/gpt-5.6-sol`、相同 evidence packet 與 output schema；lensed condition 只增加對應 overlay。

| 指標 | General baseline | Effective lens | Specialist 前的 primary lens |
|---|---:|---:|---:|
| Calls | 24 | 24 | 8 |
| Provider success | 24/24 | 24/24 | 8/8 |
| Raw schema compliance | 24/24 | 24/24 | 8/8 |
| 已知問題回傳 finding | 14/16 | 16/16 | 4/4 |
| Correct silence | 8/8 | 8/8 | 4/4 |
| 人工語意判定正確 | 22/24 | 24/24 | 8/8 |
| 有 finding 時完整句末 | 4/14 | 4/16 | 2/4 |
| 平均 latency | 8.23 s | 9.65 s | 9.19 s |

人工判定只處理 frozen scorer 標出的 13 筆 mismatch：11 筆是正確 finding 的同義措辭或截斷，2 筆是真正漏報。這是單人、非盲判定，因此只能校正 deterministic scorer，不能當正式人評證據。

## What the pilot shows

- 所有 56 次呼叫成功且 schema 合法；沒有 provider error 或 timeout。
- 四個 clean fixtures 在所有適用條件與 repeat 均保持沉默，共 20/20。
- `evolve-duplicated-discount-rule` 的 General baseline 兩次都回傳 `no_finding`，Fowler lens 兩次都正確指出同一規則散落三個模組。以 paired run 計為 effective lens 2 wins、22 ties、0 losses；實際上是同一個 unique fixture 重現兩次。
- Lamport／Carmack 的四組 specialist-vs-primary paired runs 經人工判定全是 ties，這批資料尚未證明 specialist takeover 增加命中率。
- Effective lens 平均比 General baseline 多 1.42 秒（約 17%）；樣本小且 cache 命中不均，只能視為診斷資料。

## Main quality problem

52 字上限正在破壞輸出完整性：34 則 finding 中有 25 則剛好 52 字，其中 23 則沒有自然句末；低於上限的 9 則中，8 則有自然句末。整體只有 10/34 有完整句末，且多則明顯停在「與」、「的」、「目」或尚未完成的宣告中。

這不影響多數 finding 的核心問題辨識，但不符合穩定、可直接交付的迷你 finding 品質。正式 benchmark 前應先把目標長度降到離 hard cap 有餘裕的位置，並把語句完整性列入 quality gate。

## Why this is not the Phase A gate

- 只有 12 個人工合成案例，且問題相對明顯。
- scorer 詞表用先前 calibration run 校準，只有 validation run 是 holdout output。
- 只有 4 個 unique silence cases。
- 人工 adjudication 非盲、單一 reviewer。
- 每個 fixture 僅兩次 validation repeat。
- 尚未使用真實 repository states、獨立 fixture 作者或預先登記的正式門檻。

## Recommended next gate

1. 2026-08-13 已移除 48–52 字目標與最低字數，只保留 52 字硬上限；重跑本批案例確認截斷顯著下降，且命中與 silence 不退步。本報告結果來自修改前 prompt。
2. 擴充到 roadmap 預定的 40 個 fixtures，保留一組從未用於 prompt／oracle 校準的 holdout set。
3. 每個條件至少跑 3 次；模糊 finding 交給兩位 blind raters，報告分歧率。
4. 只有在預先宣告的 grounding、issue match、correct silence 與完整性門檻全部通過後，才開始小型 Phase B paired task study。
