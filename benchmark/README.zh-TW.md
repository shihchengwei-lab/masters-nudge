# 模型配置對比測試

這份測試比較：直接讓 AI 修改程式，或在實作途中加入 Masters’ Nudge 結構提醒，對完整交付、程式結構與成本有什麼影響；也比較 Actor 與 Provider 的模型、思考深度。

Actor 是寫程式並驗證結果的模型，Provider 是唯讀程式並提出提醒的模型。測試使用 **12 道程式修改任務、七種配置，每題每配置各跑兩次，共 168 份交付**，執行日期為 2026-09-30 至 10-04。每次從相同題目基底獨立開始，使用固定驗收與匿名程式碼評審。配置、題目、執行檔差異與評分限制均列於報告。

| 材料 | 用途 |
|---|---|
| [對比報告](model-comparison-20261004/REPORT.zh-TW.md) | 各配置條件、逐題完成度、品味、時間與 Token |
| [測試方法與審計說明](model-comparison-20261004/HARNESS.zh-TW.md) | 啟動、固定驗收、匿名評審、補查與統計重建 |
| [彙整程式](model-comparison-20261004/aggregate.py) | 從凍結原始證據離線重建統計 |
| [完整數據](model-comparison-20261004/results-summary.json)／[CSV](model-comparison-20261004/deliveries.csv) | 168 份交付及評審原票的統計 |
| [原始證據](model-comparison-20261004/evidence.zip)／[來源索引](model-comparison-20261004/source-index.json) | 追查任務、程式修改、驗收、盲評與檔案指紋 |

從 repo 根目錄執行：

```powershell
python -X utf8 .\benchmark\model-comparison-20261004\aggregate.py --verify
```

這個指令不呼叫模型，只用資料包內的材料重建統計並核對指紋，不需要原研究電腦的磁碟。`protocol/`、`harness/` 與工具程式保留測試當時的快照，用於查驗實際條件；日常工具的行為以 [SPEC](../SPEC.zh-TW.md) 與現行原始碼為準。重新執行模型測試還需要題目專案、依賴與 Codex CLI，這些不包含在資料包內。

完整交付為 **C13 = I13 > F11 > E10 > B8 = D8 > A6**，各配置分母為 24。I 對 C 的匿名品味為九勝零敗、兩持平，對 F 為五勝兩敗、兩持平。成本與共同樣本的分母見報告，不能把不同共同完成樣本的品味結果串成總排名。

這份對比沒有逐則一致的誤報、內容品質與採納標註，不能由提醒送達數推算那些比率、F1 或準確率。[Element 案例](../docs/examples/element-sessions.zh-TW.md)提供一組可追溯的提醒、程式修改與評審依據。
