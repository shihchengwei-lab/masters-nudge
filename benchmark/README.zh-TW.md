# Benchmark 索引

更新：2026-10-04。目前保留的完整效益比較是 [GPT-6.1 Sol 七臂研究](sol61-six-arm-20261002/REPORT.zh-TW.md)。本頁區分現行提示的效果證據、歷史研究與提示診斷；不以最新單次重播覆寫完整研究。

## 最新保留的完整研究

2026-09-30 至 10-04：12 題，每題每臂兩次，A–F 加 I 共七臂、168 份交付。工具提示採現行定稿，Provider 使用五條準則與四欄回饋。七臂實際配置、CLI 差異、共同分母與相容性補查均在報告中列出。

| 材料 | 用途 |
|---|---|
| [完整報告](sol61-six-arm-20261002/REPORT.zh-TW.md) | 契約、逐題結果、品味、花費與效益 |
| [Harness 與審計說明](sol61-six-arm-20261002/HARNESS.zh-TW.md) | 啟動、固定驗收、匿名評審、補查與重建 |
| [彙整程式](sol61-six-arm-20261002/aggregate.py) | 從凍結原始證據離線重建統計 |
| [完整數據](sol61-six-arm-20261002/results-summary.json)／[CSV](sol61-six-arm-20261002/deliveries.csv) | 168 份交付及原票投影 |
| [原始證據](sol61-six-arm-20261002/evidence.zip)／[來源索引](sol61-six-arm-20261002/source-index.json) | 沿要求、實作、驗收、盲評與統計核對 |

從 repo 根目錄執行：

```powershell
python -X utf8 .\benchmark\sol61-six-arm-20261002\aggregate.py --verify
```

資料包保留原始指紋與來源；`protocol/`、`harness/` 與工具程式都是封存快照。I 的 24 份結果、C-I/F-I 原票、xhigh 工具覆寫與執行修復紀錄一併收入，彙整可離線重建。沒有收錄預裝依賴映像、專案檢出或 CLI 二進位；重建統計不需要它們，重新跑模型需要。重複打包的 `BENCHMARK-AUDIT.zip` 未再複製，`evidence.zip` 與其餘可審計材料完整保留。

本批完整交付為 **C13 = I13 > F11 > E10 > B8 = D8 > A6**，分母各 24。I 對 C 品味九勝零敗、兩持平，對 F 五勝兩敗、兩持平；時間相對 C 增加 26.9%、相對 F 減少 0.6%，共同 19 份的未快取輸入分別增加 73.1%／14.5%。七臂共 187 則建議，沒有一致的誤報／品質／採納標註，不提供這些比率排名；Element A1/B1 是可追溯單一案例。分類指標 F1 與一般準確率不能由送達數推得。

## 歷史報告

| 材料 | 定位 |
|---|---|
| [第十一輪](formal-v11/ROUND-11-REPORT.zh-TW.md) | 較早模型／提示下的 12 題 A/B/C 完整研究；不與本頁七臂臂名混用 |
| [第十輪](formal-v10/ROUND-10-REPORT.zh-TW.md) | 當時 A/B 與額度對比；保留其驗收條件與限制 |
| [第九輪](formal-v9/ROUND-9-REPORT.zh-TW.md)／[B 重測](formal-v9/ROUND-9-B-RERUN-REPORT.zh-TW.md) | 當時正式結果與後續診斷分開閱讀 |
| [第八輪](formal-v8/ROUND-8-REPORT.zh-TW.md) | 六題兩次、Express 結構改善案例；當時使用三欄回饋 |
| [第六輪](formal-v6/RESULTS.zh-TW.md) | 更早的固定題組與當時工具邊界 |

`formal-v10/evaluation/`、`formal-v11/evaluation/` 與 `formal-v11/evaluation-v3/` 保存原題目、驗收與研究協定。凍結任務的文字和基底不能改成現行模型設定；本次七臂實際條件以包內計畫、啟動紀錄及主報告為準。

現行效益以七臂完整研究為準。原 12 題本機測試環境與各臂封存來源保留；repo 的資料包可獨立核對 168 份結果，不需連回原研究磁碟。
