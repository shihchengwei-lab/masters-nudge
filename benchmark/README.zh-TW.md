# 模型配置對比測試

這份測試比較：直接讓 AI 修改程式，或在實作途中加入 Masters’ Nudge 結構提醒，對完整交付、程式結構與成本有什麼影響；也比較 Actor 與 Provider 的模型、思考深度。

Actor 是寫程式並驗證結果的模型，Provider 是唯讀程式並提出提醒的模型。測試使用 **12 道程式修改任務、七種配置，每題每配置各跑兩次，共 168 份交付**，執行日期為 2026-09-30 至 10-04。每次從相同題目基底獨立開始，使用固定驗收。程式碼品味保留匿名盲評為初評，另以完整流程的維護成本覆核為複評；最終採用複評結果。

## 結果：初評與複評

完整交付為 **C13 = I13 > F11 > E10 > B8 = D8 > A6**，各配置分母為 24。覆核沒有改動契約完成、時間或 Token，品味只比較雙方都完成契約的同題／同次序，共 71 組配對。

下表由前者看後者，數字為「勝／敗／持平」。Sol 指 GPT-6.1 Sol，Astra 指 GPT-6 Astra；完整七臂條件見對比報告。

| 比較條件 | 初評：匿名盲評 | 複評：程式碼覆核，最終結果 |
|---|---|---|
| B 對 A：Sol medium＋Sol medium 對直接做 | 5／1／0 | 5／1／0 |
| F 對 C：Sol xhigh＋Sol medium 對直接做 | 3／3／2 | 3／3／2 |
| I 對 C：Sol xhigh＋Sol xhigh 對直接做 | 9／0／2 | **7／0／4** |
| I 對 F：Provider medium→xhigh | 5／2／2 | **5／0／4** |

初評由 GPT-6 Astra medium 匿名比較 X/Y，交換順序評兩次，分歧時加第三票。複評由 Codex 已知組別與初評結果，核對實際程式與呼叫路徑，將新增狀態、轉接、同步及相容責任扣回整體收益；不是新增匿名評審票。71 組中 65 組保留、6 組由勝出改為持平，沒有改判另一方勝出。完整十組比較、六項改判與逐組理由見[覆核報告](model-comparison-20261004/taste-review/README.zh-TW.md)。

各組共同完成樣本不同，不能把品味結果串成總排名；「相對勝出」也不等於答案已達絕對高品味。成本與共同樣本的分母見對比報告。

## 方法與審計材料

| 材料 | 用途 |
|---|---|
| [對比報告](model-comparison-20261004/REPORT.zh-TW.md) | 各配置條件、逐題完成度、品味初評、時間與 Token |
| [覆核報告](model-comparison-20261004/taste-review/README.zh-TW.md)／[逐組複評](model-comparison-20261004/taste-review/reassessment.json) | 品味最終結果、改判理由與程式依據 |
| [測試方法與審計說明](model-comparison-20261004/HARNESS.zh-TW.md) | 啟動、固定驗收、匿名評審、補查與統計重建 |
| [彙整程式](model-comparison-20261004/aggregate.py) | 從凍結原始證據離線重建交付、成本與初評統計 |
| [完整數據](model-comparison-20261004/results-summary.json)／[CSV](model-comparison-20261004/deliveries.csv) | 168 份交付及初評原票的統計，保持原始內容 |
| [複評查驗程式](model-comparison-20261004/taste-review/verify.py)／[覆核程式來源](model-comparison-20261004/taste-review/sources.zip) | 核對 71 組複評彙總、原證據及還原程式指紋 |
| [原始證據](model-comparison-20261004/evidence.zip)／[來源索引](model-comparison-20261004/source-index.json) | 追查任務、程式修改、驗收、盲評與檔案指紋 |

從 repo 根目錄執行：

```powershell
python -X utf8 .\benchmark\model-comparison-20261004\aggregate.py --verify
python -X utf8 .\benchmark\model-comparison-20261004\taste-review\verify.py
```

兩個指令都不呼叫模型，只用資料包內的材料核對統計與指紋，不需要原研究電腦的磁碟。第一個重建初評與原交付統計，第二個核對已記錄的複評判斷與彙總；不會自動重新判斷品味。`protocol/`、`harness/` 與工具程式保留測試當時的快照，用於查驗實際條件；日常工具的行為以 [SPEC](../SPEC.zh-TW.md) 與現行原始碼為準。重新執行模型測試還需要題目專案、依賴與 Codex CLI，這些不包含在資料包內。

這份對比沒有逐則一致的誤報、內容品質與採納標註，不能由提醒送達數推算那些比率、F1 或準確率。[Element 案例](../docs/examples/element-sessions.zh-TW.md)提供一組可追溯的提醒、程式修改與評審依據。
