# Masters' Nudge taste-v3：Reviewer-only replay

日期：2026-08-29

這不是新的 SWE-bench A/B。測試沒有重跑主模型、沒有產生新 patch，也沒有重新評分；只把目前 commit `226f449` 的 Automatic Router 與單一 Persona Generator，套到上一輪十題 B-arm 保存的決策現場。

## 結果

- 10 題全部進入 Router：5 個 `finding`、4 個 `no_finding`、1 個 Generator `invalid_output`。
- 5 個 finding 的 Lens 為 Linus 4、Lamport 1；沒有 Beck。
- 5 個 finding 全部符合 `<優先選擇>；別<替代方案>，因為<理由>。`，長度為 34–47 字元。
- 4 個 `no_finding` 都在 Router 結束，沒有為了交付意見而呼叫 Generator。
- t09 的 Router 選 Linus，但 Generator 輸出未通過 52 字品味契約，因此保留為 error，不選擇性重跑。
- 人工閱讀五則 finding：內容都在選擇資料表示、責任邊界、控制順序或變更範圍；沒有純粹要求跑測試、補測試或確認完成。

## 逐題輸出

| 題目 | 結果 | Lens | 字數 | Finding |
|---|---|---|---:|---|
| t01 | finding | Lamport | 47 | 先修正標記跳過的位置；別讓 --runxfail 提前短路，因為它只應屏蔽 xfail 處理。 |
| t02 | finding | Linus | 34 | 保留未求值的 Mod；別把公因數硬設為 1，因為求值失敗不代表互質。 |
| t03 | no_finding | none | 0 | Router 選擇沉默。 |
| t04 | finding | Linus | 36 | 只記錄主鍵是否由預設產生；別保存預設值再比對，因為值相同不代表來源相同。 |
| t05 | finding | Linus | 42 | 只在預設值語境補元組括號；別讓所有 Tuple 一律加括號，因為會擴大既有輸出變更。 |
| t06 | no_finding | none | 0 | Router 選擇沉默。 |
| t07 | no_finding | none | 0 | Router 選擇沉默。 |
| t08 | no_finding | none | 0 | Router 選擇沉默。 |
| t09 | error | none | 0 | Router 提出「例外鏈屬性應直接存取，還是保留 getattr() 的防禦性介面」；Generator 輸出無效。 |
| t10 | finding | Linus | 34 | 只在欄位名稱側拆分參數；別讓型別逗號共用拆分機制，因為兩側責任不同。 |

## 與 routing-v2 replay 的描述性差異

| 指標 | routing-v2 | taste-v3 reviewer-only |
|---|---:|---:|
| finding | 8 | 5 |
| no_finding | 1 | 4 |
| 未觸發／error | 1 未觸發 | 1 invalid output |
| Lens | Beck 6、Linus 2 | Linus 4、Lamport 1 |
| 純測試／驗證導向 finding | 6 | 0 |

這個差異支持「Reviewer 的敘述已從 review 動作轉向工程取捨」；不支持成功率提高，也不證明主模型會採納 Nudge。兩次測試的輸入機制也不完全相同：上一輪是 live Hook；這次是保存軌跡 replay。

## 輸入與限制

- t01–t09：使用保存的 `.turn.json`，只保留到第一筆 `change` 為止。
- t10：舊版 Hook 沒辨識檔案變更；本次從保存的 rollout 抽取第一次 `apply_patch`，用目前 evidence contract 重建。結果必須和九個原生 checkpoint 分開解讀。
- `inputs.json` 在 Provider 呼叫前寫入，保存完整 source packet、SHA-256 與 provenance。
- `results.json` 分別保存 Router 與 Generator 的 schema、輸入／prompt hash、解析結果、usage 與 latency。
- 共有 16 次 Reviewer 呼叫：10 Router、6 Generator。Provider 回報合計 283,298 input tokens、3,084 output tokens、2,309 reasoning tokens。
- 未進行人工盲評、重複 replay、主模型 response replay 或正式 task scoring。

完整鎖定條件見 [contract.json](./contract.json)，輸入見 [inputs.json](./inputs.json)，機器結果見 [results.json](./results.json)。
