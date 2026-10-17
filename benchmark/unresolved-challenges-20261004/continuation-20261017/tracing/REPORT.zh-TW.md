# Tracing：完整固定驗收已通過

2026-10-17，從歷史 L2 續解，帶入 L1／L2 的原始修改、失敗反例與成功部分。**最終4/4組固定檢查通過，預設功能測試184項通過。** 原兩次獨立探索仍為[0/2](../../tracing/REPORT.zh-TW.md)。

## 實作與交付

- 精確基底：`ac4a8dd27c0b28c36b9cf77cdc52b595168d1c5f`。
- [完整 patch](final.patch)，SHA-256：`03aa139826be0e426a5b6a52f368051bdbf899112e96fbe14468102b4f28b486`。
- [本次增量 patch](continuation-only.patch)，相對歷史 L2。
- [Actor 實作報告](continuation-report.zh-TW.md)，保留命令、修正與回歸測試說明。

修正三項行為：全域拒絕與層級上限穿過局部包裝仍生效；filtered current、lookup 與 contextual event scope 使用仍進入中的可見 span 視圖；一般快取重建保留待派送決策，真正 reload 才使其失效。

Registry 使用原有 entered stack，自訂 subscriber 在 Layered 邊界追蹤；enter／exit 先更新，再派送回呼，以處理重入。新增8項回歸測試，既有69個測試檔未改。

## 固定驗收與功能組合

| 檢查 | 重現 L2 | 最終交付 |
|---|---|---|
| reserved | pass，148項 | pass，148項 |
| tracing_contract_v2.rs | fail | pass，5個探針 |
| tracing_hint_bounds.rs | pass | pass，1個探針 |
| tracing_judge_concerns.rs | fail | pass，4個探針 |

[起始驗收](baseline-evaluation/evidence.json)、[最終驗收](actor-evaluation-2/evidence.json)及各項日誌均保留。最終驗收的 patch 指紋與交付一致，10個探針 `passed` 全為 true。

| 最終功能檢查 | 通過 | 失敗 | 原有忽略 |
|---|---:|---:|---:|
| [指定完整預設功能測試](full-tests-final.txt) | 184 | 0 | 3 |
| [registry，無預設功能](registry-only-final.txt) | 88 | 0 | 0 |
| [registry＋env-filter＋regex/unicode，無預設功能](registry-env-final.txt) | 141 | 0 | 3 |
| [無預設功能的 library／公開 layering](std-only-tests.txt) | 15 | 0 | 0 |

各組範圍重疊，不相加。無預設功能編譯、修改檔格式與差異檢查皆 exit 0，摘要見 [continuation-verification.json](continuation-verification.json)。第一版已通過固定驗收，後續功能組合檢查發現快取重複求值，Actor 新增穩定反例並修正至最終第二版；失敗日誌保留。

## 歷史反例與 Nudge

歷史 L1／L2 提供全域拒絕、current span 與 hint 的反例及局部成功部分。本輪4次 Provider 呼叫，3則提醒送達、1次沉默、0故障：

- `8293e944` 指出 `current_span_filtered` 尚無呼叫點。Actor 接上 Context 與 entered stack；此接線也在原計畫內。
- `6141bc40` 指出 `inner.enter` 先於 stack.push，重入事件會讀到舊 current。Actor 採納先更新再派送回呼的順序；每個 subscriber 邊界仍保留自身堆疊。
- `a1615413` 再次指出相同更新順序問題，與前則對應同一項修正，不算另一項獨立改善。

原始提醒與送達見 [nudge-attempts.json](nudge-attempts.json)，對應修改見 [nudge-batches.json](nudge-batches.json)、[Actor 回應](actor-messages.json)及 [file-changes.json](file-changes.json)。快取重建問題來自功能組合測試，另由 Actor 修正。

## 模型、成本與查驗

Actor／Provider 均為 **gpt-6.1-sol／xhigh**，實際程序核對1個 Actor、4個 Provider。Actor 沒有總時限，用時1,047.297秒，包含 Provider 205.922秒及測試／驗收等待。Actor＋Provider：未快取輸入296,756、快取輸入7,219,712、輸出49,325 Token。

[實際模型](actual-models.json)、[稽核摘要](audit-summary.json)、[交付完整性](delivery-integrity.json)、[命令及輸出](commands.json)、[來源索引](source-index.json)與[證據包](evidence.zip)保留可追查材料。這是知悉歷史材料的續解，與原獨立比較分開；整體條件與離線查驗見[三題總報告](../README.zh-TW.md)。

原協調端報告在證據包中命名為 `source-report.zh-TW.md`，來源索引保留其原檔名；原交付完整性紀錄內 `REPORT.zh-TW.md` 的指紋對應該封存檔。本頁是公開資料的閱讀入口。
