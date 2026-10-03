# 文件索引

本索引按 2026-10-03 工作樹整理。日常使用先看 README；修改工具時對照 SPEC、現行原始碼與生成外掛；效果判斷看對應版本的 benchmark。

## 現行文件

| 文件 | 用途 |
|---|---|
| [繁體中文首頁](../README.zh-TW.md)／[英文首頁](../README.md) | 工具用途、四欄回饋、使用限制、隱私與最新保留結果 |
| [工具規格](../SPEC.zh-TW.md) | 責任、兩步選題、五條準則、資料、額度與故障行為 |
| [開發說明](DEVELOPMENT.zh-TW.md) | 原始碼責任、外掛入口、設定與驗證流程 |
| [本次整理紀錄](REPOSITORY-STATUS.zh-TW.md) | 文件對齊範圍與本次實際驗證 |
| [測試索引](../benchmark/README.zh-TW.md) | 最新六臂研究與歷史測試的版本定位 |
| [六臂完整報告](../benchmark/sol61-six-arm-20261002/REPORT.zh-TW.md) | 契約完成、品味、時間與 Token |
| [六臂 harness](../benchmark/sol61-six-arm-20261002/HARNESS.zh-TW.md) | 執行流程、固定驗收、盲評與離線重建 |
| [Element 有／無工具案例](examples/element-sessions.zh-TW.md) | 同配置 A1／B1 的原始提醒、採納前後程式與匿名評審依據 |

管理技能位於 `plugins/masters-nudge/skills/`：`doctor` 查安裝條件，`select-provider` 查詢或設定 Provider，`recent-nudges` 讀取已記錄嘗試。它們按使用者請求執行，沒有改變選題或接管 Actor。

## 歷史與本機文件

[事件生命週期紀錄](../experiments/champion-vs-preserved-result-20260920/CODEX-POSTTOOLUSE-LIFECYCLE-SPEC.md)與[最小重現](../experiments/champion-vs-preserved-result-20260920/minimal-repro/README.md)保留當時 Host 行為；它們不取代目前工具規格。

較早 benchmark 與評測協定保留原模型、提示、題目及數值，使用[測試索引](../benchmark/README.zh-TW.md)辨識版本。六臂包內的 `protocol/` 與 `harness/` 是凍結來源，不是另一套需要同步維護的現行程式。

`HANDOFF.md` 是忽略的本機交接；`docs/spec-refactor-progress.zh-TW.md`、`docs/model-communication-protocol-handoff.zh-TW.md` 與 `docs/codex-post-tool-batch-issue-draft.md` 也是本機保留的歷史記錄／草案，不屬 clone 後必備文件。撤回的三題提示改寫與相關研究已移入回收桶，不列為現行方案或可用的效果證據。
