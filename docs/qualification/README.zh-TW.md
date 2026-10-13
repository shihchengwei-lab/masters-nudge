# Windows 安裝與中斷驗證

2026-10-13，版本 `0.6.3+codex.20261013`。支援的安裝平台限定 **Windows 11 x64**。

| 實際安裝流程 | 結果 |
| --- | --- |
| 正常任務 | 完成；提醒送達；新增功能的前後狀態驗證通過。 |
| Provider 正在執行時呼叫 `turn/interrupt` | 該輪回報 `interrupted`；Provider 無殘留程序；紀錄為中斷故障，未交付提醒。 |
| Hook 事件 | `Interrupt` hook 完成；該次未收到原 `PostToolUse` 的完成事件，沿用 [Codex #46765](https://github.com/openai/codex/issues/46765) 追蹤。 |

條件：Windows 11 x64（10.0.26300）、Python 3.12.10、Codex 0.162.0-alpha.17.2、`mxc` 沙箱；寫程式模型與 Provider 均為 `gpt-6.1-sol` medium。使用隔離的 Codex 設定與合成 Git 專案。

自動測試覆蓋 MCP 取消與斷線、程序樹回收、建立失敗、逾時、正常退出、紀錄寫入中斷、重啟恢復、晚到結果、競爭寫入與儲存故障。測試會啟動及終止真正的 Python 程序；模型回覆採固定測試資料。

[機器可讀紀錄與實測程式指紋](windows-20261013.json)；[生命週期測試](../../tests/spec/test_lifecycle.py)。
