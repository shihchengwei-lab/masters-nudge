# 模型配置對比資料包

這份資料包比較直接實作與加入 Masters’ Nudge 提醒，以及不同模型與思考深度的交付、程式結構與成本。測試日期為 2026-09-30 至 10-04，包含 12 題、七種配置，每題每配置各兩次，共 **168 份交付**。

品味最終結果見[覆核複評](taste-review/README.zh-TW.md)，七臂條件、逐題完成、成本及匿名初評見[對比報告](REPORT.zh-TW.md)。初評保留原票；複評核對同一批程式的整體維護成本，共 71 組中保留 65 組、將 6 組勝出改為持平。I 對 C 由初評 9／0／2 改為最終 **7／0／4**，I 對 F 由 5／2／2 改為 **5／0／4**；數字均由 I 看對方，順序為勝／敗／持平。

複評已知組別與初評結果，並非新增盲評。契約完成、耗時、Token 與 Actor 答案維持不變。查驗原測試方法見[測試 harness 與審計說明](HARNESS.zh-TW.md)。從 repo 根目錄執行：

```powershell
python -X utf8 .\benchmark\model-comparison-20261004\aggregate.py --verify
python -X utf8 .\benchmark\model-comparison-20261004\taste-review\verify.py
```

第一個指令重建原交付、成本與初評；第二個核對已記錄的複評與程式來源，兩者都不呼叫模型。`evidence.zip`、`source-index.json`、`data/`、`harness/` 與 `protocol/` 保存答案、初評原票、執行紀錄及測試快照；`taste-review/` 保存最終複評、逐組理由與還原程式。離線查驗不依賴原研究磁碟。重新跑模型則需要另備題目專案、依賴與 CLI 二進位，這些未加入 repo。

測試中的 xhigh Provider 使用實驗設定；日常產品的 Provider 仍固定 medium。配置與產品設定差異見報告，工具行為見 [SPEC](../../SPEC.zh-TW.md)。[測試材料入口](../README.zh-TW.md)列出報告、數據與查驗程式。
