# 六臂研究資料包

此資料包是 2026-09-30 至 10-02 六臂研究的原封存副本，2026-10-03 收入 repo。內容對應目前回退後的定稿提示；包內歷史協定與程式保存當時條件，不另作現行維護。

先讀[完整報告](REPORT.zh-TW.md)，審計方法見 [HARNESS](HARNESS.zh-TW.md)。從 repo 根目錄執行：

```powershell
python -X utf8 .\benchmark\sol61-six-arm-20261002\aggregate.py --verify
```

這只重建統計並核對原始證據，不呼叫模型。`evidence.zip`、`source-index.json`、`data/`、`harness/` 與 `protocol/` 保留完整；專案檢出、依賴映像與 CLI 二進位仍在原研究環境，沒有加入 repo。

`package.json` 記錄原研究電腦上外層 `BENCHMARK-AUDIT.zip` 的指紋與當時可攜驗證；該重複壓縮包未複製進 repo。repo 內直接提供其可審計內容，使用 `aggregate.py --verify`，不需要外層壓縮包或原 D/E 槽。

最新工具與其他版本的關係見[測試索引](../README.zh-TW.md)，現行規格見 [SPEC](../../SPEC.zh-TW.md)。
