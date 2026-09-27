# Benchmark 評測規格

這份評測包把任務、驗收、品味判斷與判分程式放在一起。**所有比較中的交付使用同一版本。**

本包為 `round-10-contract-v3`。12 題任務、契約條款、品味規則與環境沿用封存標準；補測按行為判分，接受契約允許的等價表示。修正內容：

- Tracing：移除額外的 `Debug` 限制，保留過濾行為斷言。
- Metaflow：按型別語義處理帶引號的必填屬性，接受 property 欄位，載入生成器記錄的 import。
- Proton：以電子郵件與偏好的關聯判斷序列化結果，允許群組代號重新編號。
- Flipt：解析契約禁止修改的原始呼叫；註解、字串與其他快取模組的同名方法不列為違約。
- NodeBB：沿用 v2 的上傳 API 測資修正。

各項依據見 [revision.json](revision.json)。

原版保存在 [formal-v10/evaluation](../../formal-v10/evaluation/README.zh-TW.md)，前版保存在 [v2](../evaluation/README.zh-TW.md)。舊分數保留；新版結果另存，不能混用版本比較。封存版本與檔案指紋見 `manifest.json`，使用前由 `evaluate.py verify` 核對。信箱題的既有時序定義見[契約釐清紀錄](cases/proton-mailbox-retry/contract-resolution.json)。

## 從哪裡看

- [評分與版本規則](PROTOCOL.zh-TW.md)：完成率、品味、成本怎麼算；如何處理更正。
- [逐題契約與驗收](CONTRACTS.zh-TW.md)：12 題、64 組要求，連到完整原文與檢查。
- [品味盲評指示](blind-rubric.txt)：六項準則、匿名比較及輸出格式。
- [驗收審查紀錄](oracle-review.json)：移除的額外限制與保留檢查的依據。

```mermaid
flowchart LR
    A[任務契約] --> B[逐條對應驗收]
    B --> C[固定題目、測試、環境與評分規則]
    C --> D[保存 A/B 原始交付]
    D --> E[同版驗收]
    E --> F[匿名品味比較]
    F --> G[完成率、品味、成本報告]
```

## 固定的判分方式

| 項目 | 判定方式 |
|---|---|
| 固定驗收 | 該題全部登錄檢查通過；缺少結果不算通過 |
| 任務完成 | 固定驗收通過，且同份交付的執行紀錄符合修改範圍等明訂限制 |
| 環境故障 | 留下故障紀錄，不能直接當作程式違約 |
| 品味 | 共同完成任務的配對，依六項結構準則盲評 |
| 只有一方完成 | 單獨列出，保留完成任務的差異 |
| 成本 | Actor 與 Provider 的實際時間及 token，列明分母 |
| 新發現的反例 | 先作診斷；改評測需另立版本，全部比較對象一起重評 |

題目沒有指定的內部資料結構、字串引號或除錯 trait，不能成為失敗理由。原始碼中明訂的介面與限制仍須遵守。共用測試失敗時，報告保留實際失敗斷言；不能把它涵蓋的所有條款都寫成已違反。

## 執行與封存

`evaluate.py audit` 檢查條文引用與檢查對照。`container_checks.py`、`native_checks.py` 接收題目與交付 patch，不接收 A／B 標籤；使用隔離環境，換上固定測試，保存完整輸出。

校準完成後，`evaluate.py seal` 產生 `manifest.json`，固定本包每個檔案的 SHA-256。`verify` 與 `score` 會拒絕修改過的評測包、錯誤的交付指紋或額外插入的判分項目。已存在的結果檔不能覆寫。

`--calibration` 僅用於封存前校準，輸出的識別碼帶有 `calibration:`，不能交給正式 `score` 冒充封存版結果。校準結果不更新任何歷史 A/B 分數。

容器以映像 SHA 固定；原生工具版本記錄在 [environment.json](environment.json)，Rust 依賴由各題的 `Cargo.lock` 固定。原始交付與完整執行日誌保存在評測工作目錄，正式比較需附同一評測指紋及原始交付指紋。
