# 七臂研究資料包

此資料包收錄 2026-09-30 至 10-04 的 A–F 加 I 七臂研究：12 題各兩次、共 168 份交付。原 A–F 材料保留，I 的原答案、原票、工具與 harness 快照一併加入。沿用原資料夾名稱以保持既有連結；報告、統計與審計說明已更新為七臂。

先讀[完整報告](REPORT.zh-TW.md)，審計方法見 [HARNESS](HARNESS.zh-TW.md)。從 repo 根目錄執行：

```powershell
python -X utf8 .\benchmark\sol61-six-arm-20261002\aggregate.py --verify
```

這只重建統計並核對原始證據，不呼叫模型。`evidence.zip`、`source-index.json`、`data/`、`harness/` 與 `protocol/` 保留完整；專案檢出、依賴映像與 CLI 二進位仍在原研究環境，沒有加入 repo。

`package.json` 記錄現行七臂範圍、證據包指紋與可攜驗證，並另列原六臂外層壓縮包的歷史指紋。repo 直接提供可審計內容，不需要外層 `BENCHMARK-AUDIT.zip` 或原 D/E 槽。I 的 xhigh Provider 是實驗工具覆寫，正式產品仍固定 medium。

最新工具與其他版本的關係見[測試索引](../README.zh-TW.md)，現行規格見 [SPEC](../../SPEC.zh-TW.md)。
