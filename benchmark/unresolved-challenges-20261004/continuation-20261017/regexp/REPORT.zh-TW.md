# Regexp：完整固定驗收已通過

2026-10-17，從歷史 J2 續解，帶入 J1／J2 的原始修改、失敗反例與成功部分。**最終4/4組固定檢查通過，全部規則1,730項測試通過。** 原兩次獨立探索仍為[0/2](../../regexp/REPORT.zh-TW.md)。

## 實作與交付

- 精確基底：`9a780beaa03b66e2d0bce27954a5711cb6b1e1db`。
- [完整 patch](final.patch)，SHA-256：`8de6e0a1a944cfe07389bf69929f2ba1e0195641c036367c2389a9657ae1e8c5`。
- [本次增量 patch](continuation-only.patch)，相對歷史 J2。
- [Actor 實作報告](continuation-report.zh-TW.md)，保留反例、命令與測試結果。

修正巢狀診斷壓掉既有效能警告、相等誤稱嚴格子集，以及捕獲／反向參照下的不安全刪除；保留 J2 已通過的量詞與 lookbehind 行為。新增37項回歸測試，既有109個測試檔未改。

## 固定驗收與其他測試

| 檢查 | 重現 J2 | 最終交付 |
|---|---|---|
| reserved | pass，77項 | pass，77項 |
| regexp_contract.js | pass | pass |
| regexp_direction.js | fail | pass |
| regexp_judge_concerns.js | fail | pass |

[起始驗收](baseline-evaluation/evidence.json)、[最終驗收](actor-evaluation-1/evidence.json)及各項日誌均保留。最終驗收的 patch 指紋與交付一致，4個 `passed` 探針旗標全為 true；既有效能警告保留，捕獲引用反例不再被錯誤建議刪除，相等使用 already-covered 診斷。

[全部規則](continuation-all-rules-final.log)1,730項、[相關回歸](continuation-regressions-final.log)74項通過，範圍重疊，不相加。正式程式型別檢查、修改檔 ESLint 與差異檢查通過。未略過外部宣告的全庫型別檢查仍失敗，唯一錯誤是預裝依賴缺少 `jest-resolve`；另以 skipLibCheck 通過，沒有安裝套件，詳見[原始型別檢查](continuation-all-types-1.log)。

## 反例與 Nudge

最初三項修補方向來自歷史反例。新增回歸最初20失敗、9通過；第一輪修補後相關測試143項通過。

本輪提醒 `681da6ce` 指出整支分支的捕獲保護過度保守：`(?:a+|(?:[ab]|(c)))\1` 中，無關兄弟捕獲不應封鎖安全的元素診斷。Actor 重現後採納，分別保留候選與覆蓋路徑的捕獲依賴，再判斷相容性；原例、對稱例、前綴、lookbehind、可選與重複量詞均有回歸測試。

Nudge 衍生測試最初3項失敗，其中2項是真正漏報，另1項是本次新增測試錯誤禁止既有整段分支警告，只修正該新增測試的預期。原有與固定測試未改。其餘兩次 Provider 回傳沉默。

完整提醒與送達紀錄見 [nudge-attempts.json](nudge-attempts.json)，對應修改見 [nudge-batches.json](nudge-batches.json)、[Actor 回應](actor-messages.json)及 [file-changes.json](file-changes.json)。

## 模型、成本與查驗

Actor／Provider 均為 **gpt-6.1-sol／xhigh**，實際程序核對1個 Actor、3個 Provider。Actor 沒有總時限，用時771.578秒，包含 Provider 166.438秒及測試／驗收等待。共1則提醒、1則送達、2次沉默、0故障。Actor＋Provider：未快取輸入230,895、快取輸入5,213,056、輸出41,332 Token。

[實際模型](actual-models.json)、[稽核摘要](audit-summary.json)、[交付完整性](delivery-integrity.json)、[命令及輸出](commands.json)、[來源索引](source-index.json)與[證據包](evidence.zip)保留可追查材料。這是知悉歷史材料的續解，與原獨立比較分開；整體條件與離線查驗見[三題總報告](../README.zh-TW.md)。
