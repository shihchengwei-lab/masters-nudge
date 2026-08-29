# Formal A/B — Positive Examples v5

日期：2026-08-29
樣本：10 題 SWE-bench、20 個 paired arms
A：無 Nudge；B：凍結版 positive-examples-v5 Nudge

## 結論

這次正式 A/B **沒有觀察到可辨識的品味增量**。

- 安全結果：A 5/10、B 5/10；10 題逐題 pass/fail 完全相同。
- 主要品味結果：A 勝 0、B 勝 0、平手 10。
- 機制確實運作：B 有 9 次 review 嘗試、7 次 finding、7 次注入、7 次主模型回應觀察。
- 7 次 finding 中，Linus 6 次、Lamport 1 次；沒有 provider error 或輸出契約偏差。

因此，不能把結果解讀成「Nudge 沒有送到」。比較符合證據的說法是：在這 10 題與 `gpt-5.6-sol` 主模型上，Nudge 產生的取捨沒有讓最後可觀察的工程判斷與實作路徑優於對照組。

## 主要品味指標

正式契約在 arm 執行前已定義主要構念：比較問題 framing、明確偏好、invariant／責任選擇、拒絕方案、實作形狀與 review friction；persona 名稱、泛用建議、測試次數與 benchmark pass/fail 不算品味證據。

盲評規則要求一方至少在兩個正向維度明顯較強，而且必須包含 `trajectory_influence`，才可判勝；否則判平手。X/Y 以 SHA-256 排序固定成 A/B 各占 X 五題，評分完成後才解盲。

| 結果 | A | B |
|---|---:|---:|
| 勝場 | 0 | 0 |
| 平手 | 10 | 10 |
| `choice_specificity` 總分 | 20/20 | 20/20 |
| `load_bearing_principle` 總分 | 20/20 | 20/20 |
| `trajectory_influence` 總分 | 20/20 | 20/20 |
| `review_friction` 總分（越低越好） | 0 | 0 |

10 題的獨立評分信心皆為 high，但 A、B 每一題、每一個維度都同分。這同時表示明顯的**天花板效應**：對照組本身已在這把尺上滿分，現有任務與量尺無法顯示細微增量。

## 安全結果

| Task | A | B | Nudge 注入 | Lens |
|---|---:|---:|---:|---|
| t01 | pass | pass | 1 | Linus |
| t02 | fail | fail | 1 | Linus |
| t03 | fail | fail | 1 | Linus |
| t04 | pass | pass | 1 | Lamport |
| t05 | pass | pass | 1 | Linus |
| t06 | fail | fail | 0 | — |
| t07 | pass | pass | 1 | Linus |
| t08r1 | pass | pass | 0 | — |
| t09 | fail | fail | 0 | — |
| t10 | fail | fail | 1 | Linus |

原 t08 `pytest-dev__pytest-5262` 在任何 model arm 開始前因乾淨基線無法重現而排除，依預先規則換成同 repo 下一題 `pytest-dev__pytest-5809`（t08r1）。最終 10 題全部通過 preflight。

## 運作成本

- A 總執行時間：1350.484 秒；B：1695.549 秒（B 約增加 25.5%）。
- A 中位數：130.031 秒；B：160.039 秒。
- A output tokens：39,834；B：46,015（B 約增加 15.5%）。
- Nudge provider latency：中位數 17.886 秒、最大 22.497 秒。

時間與 token 是本次執行的描述值；樣本小且任務時間變異大，不能當成穩定成本估計。

## 監看與完整性

- 20/20 arms 都持續監看至正常結束。
- 0 timeout、0 executor error。
- 10/10 arms pairs 完成官方 test-patch 安全評分。
- 凍結 plugin tree SHA-256：`cd3aa25d5319dccc348cbd6ad0538a5c1a3b47c2d1c912a2ffef760214e1627c`。
- 品味 rubric SHA-256：`a00d27006426fdba2b2771d6a4b1b933132d3387d5dfc8fef4dd599d762727f3`。
- 盲化 map SHA-256：`63a32f9c8e98be6215971f776997c9b4a3957c5c24e0da3a077a7a85a9f7f9ec`。

## 限制

- n=10 只能提供描述性配對證據，不能估計穩定效果，也不能推論所有任務都無效。
- 品味 rubric 在正式 arm 執行後、盲評前凍結；不過主要構念與排除項目已在 arm 執行前寫入 `contract.json`。
- 為確認 trace schema，rubric 作者在凍結前曾看到 t01 的部分 A/B raw trace；實際評分由沒有先前脈絡的獨立程序，以去識別 X/Y 材料完成。這降低評分污染，但不能宣稱整個分析流程完全 outcome-blind。
- 第一次尚未送評的隨機 X/Y 分配為 2/8；在任何有效 rating 產生前，改成預先可重現的 5/5 平衡分配，理由記錄於 `taste-blind-metadata.json`。
- 盲評材料不含命令與測試結果，能避免把「更會測試」當品味；代價是無法評估只存在於未對外說明之內部推理的變化。

目前最窄、證據足夠的判斷是：**Nudge pipeline 已能動態產生並注入短取捨，但在這批高能力主模型的 SWE-bench 修補工作上，內容沒有改變可觀察的工程品味，卻增加了執行成本。**
