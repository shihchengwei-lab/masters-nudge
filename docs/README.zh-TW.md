# 文件索引

日常使用先看 README；修改工具時對照 SPEC、現行原始碼與生成外掛；效果判斷看模型配置對比的條件與結果。

## 現行文件

| 文件 | 用途 |
|---|---|
| [繁體中文首頁](../README.zh-TW.md)／[英文首頁](../README.md) | 工具用途、四欄回饋、使用限制、隱私與測試結果 |
| [工具規格](../SPEC.zh-TW.md) | 責任、兩步選題、五條準則、資料、額度與故障行為 |
| [開發說明](DEVELOPMENT.zh-TW.md) | 原始碼責任、外掛入口、設定與驗證流程 |
| [測試方法與原始數據](../benchmark/README.zh-TW.md) | 模型配置對比的條件、結果與原始證據入口 |
| [模型配置對比報告](../benchmark/model-comparison-20261004/REPORT.zh-TW.md) | 契約完成、品味、時間與 Token |
| [測試 harness](../benchmark/model-comparison-20261004/HARNESS.zh-TW.md) | 執行流程、固定驗收、盲評與離線重建 |
| [Element 有／無工具案例](examples/element-sessions.zh-TW.md) | 同配置 A1／B1 的原始提醒、採納前後程式與匿名評審依據 |

管理技能位於 `plugins/masters-nudge/skills/`：`doctor` 查安裝條件，`select-provider` 查詢或設定 Provider，`recent-nudges` 讀取已記錄嘗試。它們按使用者請求執行，沒有改變選題或接管 Actor。

## 測試與重現紀錄

[事件生命週期紀錄](../experiments/champion-vs-preserved-result-20260920/CODEX-POSTTOOLUSE-LIFECYCLE-SPEC.md)與[最小重現](../experiments/champion-vs-preserved-result-20260920/minimal-repro/README.md)保留當時 Host 行為；它們不取代目前工具規格。

對比資料包內的 `protocol/` 與 `harness/` 保存測試當時的條件與程式，用於查驗結果；日常工具以現行原始碼與 SPEC 為準。
