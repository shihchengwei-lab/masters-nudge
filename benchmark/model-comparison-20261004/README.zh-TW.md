# 模型配置對比資料包

這份資料包比較直接實作與加入 Masters’ Nudge 提醒，以及不同模型與思考深度的交付、程式結構與成本。測試日期為 2026-09-30 至 10-04，包含 12 題、七種配置，每題每配置各兩次，共 **168 份交付**。

先讀[對比報告](REPORT.zh-TW.md)，查驗方法見[測試 harness 與審計說明](HARNESS.zh-TW.md)。從 repo 根目錄執行：

```powershell
python -X utf8 .\benchmark\model-comparison-20261004\aggregate.py --verify
```

這只重建統計並核對原始證據，不呼叫模型。`evidence.zip`、`source-index.json`、`data/`、`harness/` 與 `protocol/` 保存答案、評審原票、執行紀錄及測試快照；檔案指紋可核對內容是否變動。離線查驗不依賴原研究磁碟。重新跑模型則需要另備題目專案、依賴與 CLI 二進位，這些未加入 repo。

測試中的 xhigh Provider 使用實驗設定；日常產品的 Provider 仍固定 medium。配置與產品設定差異見報告，工具行為見 [SPEC](../../SPEC.zh-TW.md)。[測試材料入口](../README.zh-TW.md)列出報告、數據與查驗程式。
