# Metaflow：完整固定驗收已通過

2026-10-17，從歷史 K1 續解，參考 K2 的成功部分。**最終9/9組固定檢查通過，相關測試92項通過。** 原兩次獨立探索仍為[0/2](../../metaflow/REPORT.zh-TW.md)。

## 實作與交付

- 精確基底：`d7c0640016ec199a0620a296fbb45f3fc1ebadb7`。
- [完整 patch](final.patch)，SHA-256：`5b618d896439cd9325505b399681dd85933bf7308ffb28603cc42005457babf4`。
- [本次增量 patch](continuation-only.patch)，相對歷史 K1。
- [Actor 實作報告](continuation-report.zh-TW.md)，保留反例、命令與測試結果。

相對 K1 的實作只有兩個修改位置：在函式參數邊界保留明確的 `None` 型別；`Annotated` metadata 沿用既有安全值格式化工具，將 runtime-only 值輸出為合法的 `...`。`_exploit_annotation(None)` 所要求的空字串行為不變。

保留 K1 的 property／setter、多載、NamedTuple、TypedDict、self-alias、動態成員、匯入與模組重設行為。新增12項回歸測試，既有213個測試檔未改。

## 固定驗收與其他測試

| 檢查 | 重現 K1 | 最終交付 |
|---|---|---|
| reserved | pass，45項 | pass，45項 |
| annotation-api | pass | pass |
| class-api | pass | pass |
| function-api | pass | pass |
| metaflow_docquotes_input.py | pass | pass |
| metaflow_members_input.py | fail | pass |
| metaflow_review_members_input.py | fail | pass |
| metaflow_typed_dict_keys_input.py | pass | pass |
| reset-api | pass | pass |

[起始驗收](baseline-evaluation/evidence.json)、[最終驗收](actor-evaluation-1/evidence.json)及各項日誌均保留。最終驗收的 patch 指紋與交付一致，18個巢狀 `passed` 旗標全為 true。

新增測試最初[10失敗、2通過](continuation-regressions-before-1.txt)；修補後[92項通過](continuation-tests-after-1.txt)，包含45項固定保留、35項 K1 回歸與12項本次新增測試。使用既有離線 Docker 映像與依賴，沒有安裝套件或連線下載。原有依賴警告保留；`...` 保持合法描述檔語法，沒有重建 runtime-only 物件身分。

## 歷史材料與 Nudge

K1 提供已通過保留測試的起點，K2 提供 `None` 與 metadata 的成功處理作參考，避免帶回 K2 的其他退步。本輪 Provider 兩次皆回傳 `feedback:null`，沒有新增提醒；兩項修補方向來自歷史反例與成功部分。

原始回傳見 [nudge-attempts.json](nudge-attempts.json)，實際修改見 [file-changes.json](file-changes.json)與 [Actor 回應](actor-messages.json)。

## 模型、成本與查驗

Actor／Provider 均為 **gpt-6.1-sol／xhigh**，實際程序核對1個 Actor、2個 Provider。Actor 沒有總時限，用時440.343秒，包含 Provider 31.078秒及測試／驗收等待。共0則提醒、2次沉默、0故障。Actor＋Provider：未快取輸入181,172、快取輸入2,419,968、輸出21,376 Token。

增量匯出時，CRLF 基底與 LF 歷史 patch 曾造成比較 index 的 context 差異；只在私有 index 重建時容忍空白差異，未改交付與測試。增量已實際套用並核對與最終 checkout 的內容一致，換行另作正規化比較。

[實際模型](actual-models.json)、[稽核摘要](audit-summary.json)、[交付完整性](delivery-integrity.json)、[命令及輸出](commands.json)、[來源索引](source-index.json)與[證據包](evidence.zip)保留可追查材料。這是知悉歷史材料的續解，與原獨立比較分開；整體條件與離線查驗見[三題總報告](../README.zh-TW.md)。
