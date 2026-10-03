# Benchmark 索引

更新：2026-10-03。目前保留的完整效益比較是 [GPT-6.1 Sol 六臂研究](sol61-six-arm-20261002/REPORT.zh-TW.md)。本頁區分現行提示的效果證據、歷史研究與提示診斷；不以最新單次重播覆寫完整研究。

## 最新保留的完整研究

2026-09-30 至 10-02：12 題，每題每臂兩次，六臂共 144 份交付。工具提示對應目前回退後的定稿，Provider 使用五條準則與四欄回饋。六臂實際配置、CLI 差異、共同分母與相容性補查均在報告中列出。

| 材料 | 用途 |
|---|---|
| [完整報告](sol61-six-arm-20261002/REPORT.zh-TW.md) | 契約、逐題結果、品味、花費與效益 |
| [Harness 與審計說明](sol61-six-arm-20261002/HARNESS.zh-TW.md) | 啟動、固定驗收、匿名評審、補查與重建 |
| [彙整程式](sol61-six-arm-20261002/aggregate.py) | 從凍結原始證據離線重建統計 |
| [完整數據](sol61-six-arm-20261002/results-summary.json)／[CSV](sol61-six-arm-20261002/deliveries.csv) | 144 份交付及原票投影 |
| [原始證據](sol61-six-arm-20261002/evidence.zip)／[來源索引](sol61-six-arm-20261002/source-index.json) | 沿要求、實作、驗收、盲評與統計核對 |

從 repo 根目錄執行：

```powershell
python -X utf8 .\benchmark\sol61-six-arm-20261002\aggregate.py --verify
```

資料包保留原始指紋與來源，移入 repo 後不改內部歷史文件；其中 `protocol/`、`harness/` 與工具程式都是封存快照。沒有收錄預裝依賴映像、專案檢出或 CLI 二進位；重建統計不需要它們，重新跑模型需要。重複打包的 `BENCHMARK-AUDIT.zip` 未再複製，`evidence.zip` 與其餘可審計材料完整保留。

本批完整交付為 **C13 > F11 > E10 > B8 = D8 > A6**，分母各 24。品味只列直接比較；B 對 C 為 4：4，F 對 C 為 3：3、兩組持平。六臂沒有對 147 則建議做一致的誤報／品質／採納標註，不提供這些比率排名；F1 Element 的可確認採納只是單一案例。分類指標 F1 與一般準確率也不能由送達數推得。

## 歷史報告

| 材料 | 定位 |
|---|---|
| [第十一輪](formal-v11/ROUND-11-REPORT.zh-TW.md) | 較早模型／提示下的 12 題 A/B/C 完整研究；不與本頁六臂臂名混用 |
| [第十輪](formal-v10/ROUND-10-REPORT.zh-TW.md) | 當時 A/B 與額度對比；保留其驗收條件與限制 |
| [第九輪](formal-v9/ROUND-9-REPORT.zh-TW.md)／[B 重測](formal-v9/ROUND-9-B-RERUN-REPORT.zh-TW.md) | 當時正式結果與後續診斷分開閱讀 |
| [第八輪](formal-v8/ROUND-8-REPORT.zh-TW.md) | 六題兩次、Express 結構改善案例；當時使用三欄回饋 |
| [第六輪](formal-v6/RESULTS.zh-TW.md) | 更早的固定題組與當時工具邊界 |

`formal-v10/evaluation/`、`formal-v11/evaluation/` 與 `formal-v11/evaluation-v3/` 保存原題目、驗收與研究協定。凍結任務的文字和基底不能改成現行模型設定；本次六臂實際條件以包內計畫、啟動紀錄及主報告為準。

較早的校準、方向改寫與 B-only 重播屬診斷，不自動變成一般效果證據。為 Metaflow、Tracing、Regexp 三題追加的研究及後續六題驗證已按使用者決定移到回收桶；相應選題改寫已撤回。原 12 題本機測試環境與六臂封存來源仍保留，本 repo 的可審計包可獨立重建六臂統計。
