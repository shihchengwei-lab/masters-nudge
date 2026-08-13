# No-minimum prompt regression comparison

## Decision

保留「不設最低字數」的修改。這輪沒有出現 finding 命中或 correct silence 退步，輸出長度分布則明顯離開 52 字邊界。52 字硬上限暫時不需要修改。

兩輪都使用相同 12 個 fixtures、2 次 repeat、randomization seed `20260814`、`openai/gpt-5.6-sol` 與 Codex CLI `0.147.0`。修改前結果來自 `validation-20260813`；修改後只移除 48–52 字目標與最低字數，保留 52 字硬上限。因 fixtures 已參與 prompt 調整，這是 regression comparison，不是新的 holdout benchmark。

| 全條件合計 | 修改前 | 取消最低字數後 |
|---|---:|---:|
| Calls | 56 | 56 |
| Provider／schema success | 56/56 | 56/56 |
| Status correctness | 54/56 | 56/56 |
| Correct silence | 20/20 | 20/20 |
| 單人非盲語意＋grounding 判定 | 54/56 | 55/56 |
| Finding 數 | 34 | 36 |
| Finding 平均長度 | 50.9 | 46.2 |
| 剛好 52 字 | 25/34（73.5%） | 12/36（33.3%） |
| 有自然句末 | 10/34（29.4%） | 25/36（69.4%） |
| 平均 latency | 8.97 s | 7.99 s |

句末只用來觀察是否撞上字數邊界，不是 finding 有效性的判定條件。

## By condition

| Condition | 平均字數（前→後） | 52 字（前→後） | 自然句末（前→後） | 人工語意＋grounding（前→後） |
|---|---:|---:|---:|---:|
| General baseline | 51.5 → 45.4 | 11/14 → 3/16 | 4/14 → 13/16 | 22/24 → 23/24 |
| Effective lens | 51.0 → 46.2 | 13/16 → 8/16 | 4/16 → 10/16 | 24/24 → 24/24 |
| Specialist 前的 primary lens | 48.5 → 49.5 | 1/4 → 1/4 | 2/4 → 2/4 | 8/8 → 8/8 |

## Interpretation

- 取消最低字數達成預期：模型不再普遍把 finding 填到上限，而且沒有因此增加 `no_finding`。General 先前兩次漏掉的三模組折扣規則，本輪兩次都命中。
- Effective lens 仍有 8/16 則剛好 52 字，主要集中在包含英文 identifier 或較完整因果鏈的案例；其中數則雖然句尾截斷，問題與位置仍足以形成 Nudge。
- 修改後唯一的人工作業失敗是 General 在一個 forwarding-layer 案例改挑「測試未驗版本值」，但 packet 沒有足夠證據支持「未驗」；這是 grounding 問題，不是字數問題。
- 本輪有效支持保留新 prompt，但不足以證明 lifecycle 或 specialist lens 的普遍增益。下一輪應使用未參與這次調整的 holdout fixtures。

## Next evaluation gate

1. 不再加入任何 finding 最低字數，也不把句末標點當成品質門檻。
2. 新增獨立 holdout cases，重點評分 `issue target`、`packet grounding`、`correct silence` 與 cue 是否足以定位。
3. 對 alternative finding 做 blind adjudication；像本輪「測試未驗版本值」這類缺直接證據的提示應判失敗。
4. 等 Phase A 在 holdout set 達到預先宣告的品質門檻後，再做 Phase B downstream-impact study。
