# Shader live-evidence end-to-end test V3

狀態：執行中。

## 目的

驗證修正版 Masters' Nudge 是否能在 `benchmark/candidate-results.json`
尚未更新時，直接從 `Evidence/LongTail/<candidate>/result.json` 或
`failure.json` 偵測新研究材料、更新 fingerprint，並在後續 hook 形成可交付
的 Shader Finding。

這是工具端到端測試，不是 Nudge 因果證明，也不沿用任何舊 Shader
效能結論。

## 全新隔離環境

- 工作區：`E:\projects\shader-long-tail-v3`
- Unity：`6000.0.80f1`
- URP：`17.0.4`
- D3D11、1920×1080、Intel UHD 接受硬體
- 新程式碼、新 BaselineV0、新候選、新 Evidence、新 Git 歷史
- 專案記憶讀取與產生均停用
- 禁止讀取舊工作區、舊候選、舊 Nudge 與舊停止結論

## 主模型 Goal

> 交付在固定契約下經實證建立、可重現的最佳 Shader Pareto 前沿。

## 執行階段

1. 建立可重現的 Lean Impact Shield URP BaselineV0 與固定 benchmark。
2. 每個候選先登錄假設與機制，再做單一可歸因改動與量測。
3. 每個候選完成後先落檔逐候選 Evidence，再同步 aggregate ledger。
4. 正式停止只能是 formal-long-tail-v1 飽和、50 個有效候選格或真實外部阻塞。

## 早期管線門檻

第一次出現真實候選 Evidence 後，必須在下一個合適 hook 看到：

1. research fingerprint 改變；
2. 投影焦點為該候選，而非仍停在 planned 候選；
3. 留下 finding、no_finding 或 provider error 紀錄；
4. 若有 Finding，delivery 可追蹤 pending 至 injected／expired／failed。

任一真實候選 Evidence 已落檔、但連續兩個合適 hook 完全沒有 semantic
review 紀錄，判定接線回歸並停止本輪。

## 效果觀察邊界

- 至少 10 則可評估的成功注入；
- 至少完成 12 個技術上不同的候選格；
- 若完成 20 格仍不足 10 則可評估注入，判定管線證據不足；
- 反應分類沿用 explicit uptake、reinterpretation、possible influence、
  temporal only、no observable response；只接受有時間順序及內容對應的判讀。

監看只讀，不手動注入、不切換 Persona、不額外呼叫 Provider。
