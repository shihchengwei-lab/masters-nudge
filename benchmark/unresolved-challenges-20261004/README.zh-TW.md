# 三題挑戰歷程：已全部完成契約

**Regexp、Metaflow、Tracing 已於 2026-10-17 全部通過完整固定驗收。** 這份資料保留最初未解時的六次探索，並公開後續成功解答，讓讀者追查失敗反例、修正內容、提醒與成本。先讀[三題成功續解](continuation-20261017/README.zh-TW.md)。

| 題目 | 原七臂，2026-09-30～10-04 | Astra max 探索，2026-10-04 | Sol xhigh 續解，2026-10-17 |
|---|---:|---:|---|
| [Regexp](continuation-20261017/regexp/REPORT.zh-TW.md) | 0/14 | [0/2](regexp/REPORT.zh-TW.md) | **完整通過，4/4 組檢查**；從 J2 續解 |
| [Metaflow](continuation-20261017/metaflow/REPORT.zh-TW.md) | 0/14 | [0/2](metaflow/REPORT.zh-TW.md) | **完整通過，9/9 組檢查**；從 K1 續解 |
| [Tracing](continuation-20261017/tracing/REPORT.zh-TW.md) | 0/14 | [0/2](tracing/REPORT.zh-TW.md) | **完整通過，4/4 組檢查**；從 L2 續解 |

原七臂與 Astra max 的欄位是完成份數／嘗試份數；續解欄位是固定檢查組數，分母不同。續解使用先前反例與成功部分，每題各一份最終解答；Actor 與 Provider 都是 GPT-6.1 Sol xhigh，Actor 沒有總時限。三份交付皆與全數通過驗收的 patch 指紋一致，原固定驗收與既有測試未修改。

原六次探索與本次知悉歷史材料的續解分開呈現，不據此推算模型或 Masters’ Nudge 的因果效果。[十二題主要比較](../model-comparison-20261004/REPORT.zh-TW.md)納入原三題失敗與成本，[九題事後子集](../model-comparison-20261004/PRIMARY.zh-TW.md)列為補充；原答案、判分及71組最終品味配對不變。原資料夾路徑保留以維持既有連結。

## 原六次探索

三題在本研究的七臂測試中均為 **0/14**。後續每題以 GPT-6 Astra max 同時擔任 Actor 與 Provider，從相同基底獨立嘗試兩次，取消 Actor 的30分鐘截止，完整交付仍各為 **0/2**。六份均通過執行規則覆核，功能契約仍未全部通過。

當時「未解」表示本研究尚未找到通過完整契約的實作。維護者確認先前對原作者實作的完整契約檢查亦未全數通過；原六次探索沒有把原作者實作當成已驗證的完整答案。本次續解已補上三題完整解答。

| 題目／完整報告 | 本輪完成 | 主要失敗 |
|---|---:|---|
| [Regexp](regexp/REPORT.zh-TW.md) | 0/2 | 分析與刪除建議未完整保留匹配方向、捕獲引用及既有效能診斷 |
| [Metaflow](metaflow/REPORT.zh-TW.md) | 0/2 | 成員與型別生成仍有資訊遺失、非法輸出或遞迴問題 |
| [Tracing](tracing/REPORT.zh-TW.md) | 0/2 | 全域拒絕在包裝後失效，部分 span 視圖與層級推導錯誤 |

六次探索都有局部改善與實際提醒採納，但均未完成全部契約。各題報告保留成功部分、具體反例、程式結構分析及 Actor 加 Provider 的用量，讓後續嘗試能辨認已解決與尚未解決的責任。複評由已知配置的 Codex 閱讀原任務、完整修改、執行與提醒紀錄，不以關鍵詞掃描代替語意判斷；沒有新增匿名模型評審票，也不拿失敗答案作合格品味勝負排名。

本輪同時改變模型、思考深度與解題時限，沒有相應的不限時直接實作對照，因此不據此推算 Masters’ Nudge 的效果，也不併入七臂排名。Actor 整體不限時；Provider1200秒與 hook1320秒的傳輸等待仍保留。每次最多三則提醒或兩次沉默，其他任務、禁止行為與固定驗收沿用封存條件。CLI 為0.159.2；工具快照使用 max Provider，日常產品設定未改。

## 如何閱讀與查驗

目前解答見 [continuation-20261017/](continuation-20261017/README.zh-TW.md)，包含三份完整及增量 patch、修補前後驗收、提醒紀錄與成本。

原六次探索仍位於 `regexp/`、`metaflow/`、`tracing/`：各題 `REPORT.zh-TW.md`、`results-summary.json` 與 `code-review.json` 保留逐次數據與判斷；`runs/` 可直接閱讀六份實際 patch、Actor 說明、提醒與執行覆核。每題 `evidence.zip` 保存原任務、基底與啟動條件、完整 Actor 事件、執行證據、固定驗收輸入及日誌、工具快照與完整性紀錄；`source-index.json` 對照原始與公開副本的指紋。

公開副本將本機使用者目錄與研究磁碟前綴匿名化，保留相對檔名、事件行號與判斷內容；原始 `final.patch` 位元組不變。原完整性紀錄中的指紋對應未匿名化原檔，公開副本須使用來源索引的 `public_sha256` 查驗。原始實驗紀錄在本機完整保留；封存執行器只供審計，不是從任意電腦直接重跑的入口。題目專案、依賴與 CLI 二進位未打包。

從 repo 根目錄執行：

```powershell
python -X utf8 benchmark/unresolved-challenges-20261004/verify.py
python -X utf8 benchmark/unresolved-challenges-20261004/continuation-20261017/verify.py
```

第一個指令核對原六份探索；第二個核對本次三份成功續解，包括最終 patch 與全通過驗收的對應、實際模型、用量與公開檔案指紋。兩者都離線執行，不呼叫模型、不重新判分。各題原專案授權保留在證據包的 `frozen-evaluation/cases/<題目>/upstream-licenses/`；來源與基底見 `plan.json`，七臂題目來源見[原始報告](../model-comparison-20261004/REPORT.zh-TW.md)。

要繼續改進解答，可從本次完整 patch 與基底版本開始，沿用相同固定驗收，並保留實際測試紀錄。
