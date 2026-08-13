# Phase A holdout v1 結果

## 結論

本輪達到預先登記的數值門檻，但只算 **provisional pass**，不據此升級 Phase B。

取消 finding 最低字數應保留；這輪沒有任何證據支持恢復下限。真正暴露的問題是 **52 字硬上限**：effective condition 的 21 則 finding 中，16 則原始字串正好 52 字，7 則明顯未完成，而且這 7 則全都撞到上限。

人工裁決在看過 condition label 後進行，不符合 protocol 原先希望的 condition-blind review；fixtures 與裁決也出自同一位作者。因此人工數字只能作工程判斷，不能當正式獨立驗證。

## 預先登記門檻

| Effective-lens gate | 結果 | 判定 |
|---|---:|---|
| Raw schema | 32/32 | 通過 |
| Provider success | 32/32 | 通過 |
| Known-issue status recall | 20/20 | 通過（門檻 18/20） |
| Correct silence | 11/12 | 通過邊界（門檻 11/12） |
| 人工 issue target＋packet grounding | 31/32 | 數值通過；非盲，暫定 |
| Clean packet 無 unsupported high-severity finding | 0 | 通過；但有 1 個非高嚴重度誤報 |
| Specialist 相對 primary 的 paired loss | 0/8 | 通過（8 組全平手） |

唯一 effective 語意失敗是 clean plan-revocation case 的誤報：輸出推測舊 session 失效會連基礎功能一起登出，但 packet 沒有這項證據。General baseline 的唯一漏報則是第一次沒有發現三處 VAT 規則重複。

## Lens 比較

經人工語意與 grounding 裁決：

| Condition | 正確 |
|---|---:|
| General baseline | 31/32 |
| Effective lens | 31/32 |
| Specialist 前的 primary lens | 8/8 |

Effective 對 baseline 是 **1 win、30 ties、1 loss**；specialist 對 primary 是 **0 wins、8 ties、0 losses**。因此這批 holdout 支持「lens 沒有造成整體退步」，但沒有顯示淨增益，也不能證明 specialist takeover 比 lifecycle primary 更好。

## 52 字上限診斷

| Condition | Finding | 原始字串正好 52 字 | 人工判定已清楚說完 |
|---|---:|---:|---:|
| General baseline | 19 | 8/19 | 14/19 |
| Effective lens | 21 | 16/21 | 14/21 |
| Specialist primary | 4 | 2/4 | 2/4 |

「清楚說完」只要求形成自足的提醒，不要求給修法或寫成 code-review 長評。即使採這個寬鬆標準，effective 仍有 7/21 沒完成；例如：

- `make_thumbnail 與 compute_histogram 重複解碼同一份 bytes，合計耗`
- `debug_request.py 直接記錄所有 headers，已把 Authorization 的實際`
- `CLI 仍把 --legacy-cache 轉成相容模式並成功執行，違反必須回報 unknown、移`

這些輸出都已定位到真正問題，所以 semantic＋grounding 仍可通過；但它們不是清楚完成的 Nudge。這直接回答了先前的疑問：**提醒不需要最低字數，但有些具 identifier、位置與因果鏈的提醒，52 字確實說不完。**

## 決策與下一輪

1. 保留「沒有 finding 最低字數」；沒發現就回 `no_finding`，有發現則講清楚就停。
2. 不恢復 48–52 字目標，也不把句末標點本身當品質門檻。
3. 暫不開始 Phase B。下一輪先做 hard-cap ablation：同一批 regression packets 比較 52 與較寬上限，另留新 holdout 驗證，主要看清楚完成率、grounding、silence 與長度分布。
4. 正式 Phase A promotion 仍需 condition-blind 的第二位裁決者或獨立 fixture 作者，並補足更多 repeat／真實 repository packet。

自動報告保留原 deterministic scorer 分數，不以人工裁決覆寫；完整逐筆裁決見 `adjudication.json`。
