# Shader Nudge Interaction Annotation Protocol V1

這份規格把三種不同證據分開：review telemetry 記錄「有沒有呼叫」、delivery receipt 記錄「有沒有注入」、人工評註記錄「注入後可觀察到什麼」。三者不得互相代替。

## 統計單位

- **調用率**：指定 Shader session 的全部 reviewer 呼叫，包含 `finding`、`no_finding` 與 `error`。六位 persona 必須全部列出，零次也不能省略。
- **交付漏斗**：`review` finding → `injected` receipt → 已人工評註且有後續行為 → finding 與後續內容相符。
- **反應分類**：只統計已成功注入且有後續可觀察行為的固定 cohort。每則 Nudge 只能有一個分類。

## 五種反應分類

1. `explicit_uptake`：主模型明確提到 Nudge 的觀察，且內容相符。
2. `reinterpretation`：主模型沒有照抄，而是把同一盲點重組成自己的問題框架。
3. `possible_influence`：先注入，後出現內容相符且相較前段可觀察到的行為轉向；只能說可能影響。
4. `temporal_only`：後續內容相符，但相同行動在注入前已開始或已排定，不能算行為轉向。
5. `no_observable_response`：存在可評註的後續行為，但看不到內容對應或行為改變。

`delayed` 是獨立布林欄位，不是第六種分類。逾時、未注入或沒有後續行為的 finding 不進反應分類分母。

## 因果限制

這是 C-only 的觀察資料，沒有暫停 Nudge 的對照組。時間順序與內容對應只能描述互動軌跡，不能證明 Nudge 造成後續改變；圖表不得使用「因果成功率」等名稱。
