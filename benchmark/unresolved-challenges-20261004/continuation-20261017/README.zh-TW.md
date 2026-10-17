# 三題成功續解：2026-10-17

**Regexp、Metaflow、Tracing 三題都已通過完整固定驗收。** Actor 與 Nudge Provider 均為 **GPT-6.1 Sol xhigh**，每題各進行一次知悉歷史材料的續解，Actor 沒有總時限。原題、固定驗收及既有測試未修改；交付的完整 patch 指紋與全通過的驗收紀錄相同。

| 題目／報告 | 續解起點 | 起始固定驗收 | 最終固定驗收 | 其他最終測試 | Actor 用時，含等待 |
|---|---|---:|---:|---|---:|
| [Regexp](regexp/REPORT.zh-TW.md) | J2，參考 J1／J2 | 2/4 組 | **4/4 組**，保留測試77項 | 全部規則1,730項通過 | 12分52秒 |
| [Metaflow](metaflow/REPORT.zh-TW.md) | K1，參考 K2 成功部分 | 7/9 組 | **9/9 組**，保留測試45項 | 相關測試92項通過 | 7分20秒 |
| [Tracing](tracing/REPORT.zh-TW.md) | L2，參考 L1／L2 | 2/4 組 | **4/4 組**，保留測試148項 | 預設功能184項通過，3項原有忽略 | 17分27秒 |

固定檢查組數與測試項數分母不同；表中測試範圍重疊，不相加。Regexp 未略過外部宣告的全庫型別檢查仍因預裝依賴缺少 `jest-resolve` 而失敗；正式程式型別檢查及全部規則測試通過，詳見逐題報告。

## 歷史反例與 Nudge 各自的幫助

- **Tracing：** 先前反例指出包裝後全域拒絕與 current span 視圖的缺口。Nudge 提醒將尚未接線的查找接入實際呼叫，另指出 enter／exit 應先更新堆疊再派送回呼，避免重入讀到舊 span；後兩則提醒針對同一個順序問題。功能組合測試另找出快取重建造成的重複求值，Actor 補上修正。
- **Regexp：** 先前材料指出效能警告被抑制、相等誤稱嚴格子集、捕獲引用下的不安全刪除。Nudge 再指出修補過度保守：無關兄弟捕獲不應封鎖安全的元素診斷。Actor 重現後改為依候選與覆蓋路徑處理捕獲依賴。
- **Metaflow：** 保留 K1 已通過的成員與型別行為，參考 K2 的成功部分，只在參數邊界及 metadata 格式化處修補 `None` 與 runtime-only 值。本輪 Provider 兩次都回傳沉默，沒有新增建議。

本次使用既有實作、失敗反例與歷史提醒，成果屬於知悉歷史材料的續解。原每題七臂 **0/14**、Astra max 探索 **0/2** 的結果保留在[挑戰歷程](../README.zh-TW.md)；本次不併入原九題／七臂比較，也不由三份續解推算模型或 Nudge 的因果效果。

## 時間與用量

| 題目 | Actor 秒數，含 Provider | Provider 秒數，已含於 Actor | 未快取輸入 Token | 快取輸入 Token | 輸出 Token | 提醒／送達／沉默／故障 |
|---|---:|---:|---:|---:|---:|---|
| Regexp | 771.578 | 166.438 | 230,895 | 5,213,056 | 41,332 | 1／1／2／0 |
| Metaflow | 440.343 | 31.078 | 181,172 | 2,419,968 | 21,376 | 0／0／2／0 |
| Tracing | 1,047.297 | 205.922 | 296,756 | 7,219,712 | 49,325 | 3／3／1／0 |

三個 Actor 合計 **2,259.218秒，約37分39秒**。時間包含同步等待 Provider 與 Actor 內測試／驗收，不含啟動前準備及桌面協調工作；Provider 時間不另相加。Token 包含 Actor 與 Provider 的累計上下文，未快取輸入合計708,823、快取輸入14,852,736、輸出112,033；不含歷史嘗試與桌面協調 session。機器可讀數據見 [results-summary.json](results-summary.json)。

## 程式與證據

| 題目 | 完整 patch | 相對歷史起點的增量 | 證據包／來源索引 |
|---|---|---|---|
| Regexp | [final.patch](regexp/final.patch) | [continuation-only.patch](regexp/continuation-only.patch)，相對 J2 | [evidence.zip](regexp/evidence.zip)／[source-index.json](regexp/source-index.json) |
| Metaflow | [final.patch](metaflow/final.patch) | [continuation-only.patch](metaflow/continuation-only.patch)，相對 K1 | [evidence.zip](metaflow/evidence.zip)／[source-index.json](metaflow/source-index.json) |
| Tracing | [final.patch](tracing/final.patch) | [continuation-only.patch](tracing/continuation-only.patch)，相對 L2 | [evidence.zip](tracing/evidence.zip)／[source-index.json](tracing/source-index.json) |

完整 patch 可套用到各題報告所列的精確基底，包含沿用的歷史實作與新增測試，排除固定驗收安裝造成的測試差異。每題目錄可直接讀取實作報告、修補前後驗收、測試日誌、`audit-summary.json`、`actual-models.json`、`commands.json` 及 `nudge-attempts.json`。完整 Actor 事件、啟動命令、實際程序、歷史材料、凍結評估器與工具快照位於各題 `evidence.zip`。

公開副本匿名化使用者目錄與研究磁碟前綴；所有 patch 維持原始位元組。來源索引同時保存原檔與公開副本 SHA-256；原稽核紀錄中的指紋對應未匿名化原檔，公開副本以 `public_sha256` 查驗。封存程式與匿名化命令供審計，重新執行題目另需專案、依賴與 CLI 二進位；這些未打包。各題上游授權位於證據包的 `frozen-evaluation/cases/<題目>/upstream-licenses/`。

從 repo 根目錄執行：

```powershell
python -X utf8 benchmark/unresolved-challenges-20261004/continuation-20261017/verify.py
```

此指令以 repo 內的資料離線核對898個封存檔、三份交付與全通過驗收的對應、固定探針內容、歷史起點與固定材料指紋、實際模型及用量彙總；不呼叫模型、不重新執行題目或判分。原六份探索另由上一層的 `verify.py` 查驗。
