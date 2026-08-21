# Shader Nudge Interaction V1 Result

Session: `01a00b40-3d9d-7e42-a5f1-83ad83516c01`

## 三個圖表

1. 交付漏斗：147 次產生 finding，120 次成功注入（81.6%）；固定人工評註 cohort 有 9 次可評註後續，其中 3 次有內容對應。
2. 反應分類：9 次可評註注入中，明確接住 0、重新詮釋 0、可能影響 0、僅時間／內容相關 3、無可觀察反應 6。
3. 六位大師調用率：260 次 Shader reviewer 呼叫中，Carmack 142（54.6%）、Akenine-Moller 58（22.3%）、Lottes 52（20.0%）、Karis 4（1.5%）、Tatarchuk 4（1.5%）、Quilez 0（0.0%）。分母包含 finding、no_finding 與 error。

## 判讀

路由明顯集中在 Carmack，Quilez 完全沒有被調用，Karis 與 Tatarchuk 也接近缺席。這組數據足以支持下一輪檢查 route trigger 與 override 優先序，但尚不足以直接決定六位應該平均分配；不同工作階段本來就可能需要不同比例。

反應分類的固定 cohort 只有成功注入的 9 則，占整個 session 120 則成功注入的 7.5%。這 9 則沒有觀察到明確接住、重新詮釋或行為轉向；3 則內容相符的後續都在注入前已開始或排定，因此只能列為相關。

## 證據與限制

- 調用率來源：`review-telemetry.jsonl` 中指定 session、`domain=shader` 的 260 筆呼叫。
- 交付來源：指定 session reaction log 的 147 筆 `review` 與後續 `delivery_receipt`；另有 19 筆 expired、8 筆沒有 receipt。
- 反應來源：2026-08-17 05:04–06:15（Asia/Taipei）的固定最近 10 則快照；1 則 expired 排除，9 則依當時 heartbeat 的後續觀察人工評註。
- 沒有無 Nudge 對照組；本結果只能描述互動軌跡，不能證明或估算因果效果。

## 重建

```powershell
python -m evaluation.nudge_interaction.generate `
  --telemetry "$env:USERPROFILE\.masters-nudge\data\review-telemetry.jsonl" `
  --reaction-log "$env:USERPROFILE\.masters-nudge\data\codex_cli--01a00b40-3d9d-7e42-a5f1-83ad83516c01.log" `
  --annotations "evaluation\results\shader-nudge-interaction-v1-20260818\annotations.json" `
  --session-id "01a00b40-3d9d-7e42-a5f1-83ad83516c01" `
  --output-dir "evaluation\results\shader-nudge-interaction-v1-20260818"
```
