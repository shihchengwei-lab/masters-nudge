# Claude Opus 5 Provider Smoke A/B

日期：2026-08-29
樣本：1 題 paired SWE-bench smoke（`sympy__sympy-24443`）

## 設定

- 主模型固定：`gpt-5.6-sol`，medium。
- A：無 Nudge。
- B：positive-examples-v5 Nudge，Provider=`anthropic`，model=`claude-opus-5`，medium。
- 沿用先前已通過的同題乾淨基線 preflight 與官方 test patch。
- B_then_A：先確認 Opus 權限與結構化輸出可用，再花費對照組。
- 品味評分沿用正式 A/B 已凍結的 rubric；同一對材料正反交換 X/Y 各盲評一次。

## 結果

- 執行：A、B 都正常完成，0 timeout、0 executor error。
- 官方安全評分：A pass、B pass。
- 品味盲評：正向順序 tie、反向順序 tie，兩次 confidence 都是 high。
- B 機制：1 finding、1 injected receipt、1 response observation。
- Provider：`anthropic / claude-opus-5`，Linus lens，0 error、0 contract deviation。
- Provider latency：21.395 秒；Router + Generator API duration 合計 17.992 秒。
- Claude CLI 回報 Router + Generator cost 合計約 USD 0.436605；這是 CLI 回報值，不代表已確認的實際帳單扣款。

## 跨家族內容差異

舊 Sol reviewer：

> 收窄為正生成元查表、冪次負責方向；別另建反向映像，因為會形成雙重控制。

Opus 5 reviewer：

> 把生成元正規化成單一 images 鍵；別留 gens.index 轉譯層，因為雙重查表只生例外。

兩者不是逐字重複，但收斂到同一核心：移除 `gens.index(...)` 的逐字母轉譯，建立單一生成元到 image 的責任邊界。Sol 強調「正生成元／冪次分工」；Opus 強調「單一 key／移除雙重查表」。

## 主模型反應

B 在第一個 patch 後收到 Opus Nudge。注入前，主模型已辨識 inverse generator 與雙索引問題；注入後，主模型明確說：

> build a single map from presentation generators to their target images once ... removes the fragile per-letter `gens.index(...)` translation entirely.

接著又修改 production patch，建立 `rel_images` 並移除 `gens.index(...)`。時間順序與用詞高度吻合，支持「Nudge 影響了 B 的後續收斂」這個推論；但因為主模型也可能自行二次簡化，不能宣稱已證明因果。

A 沒有 Nudge，卻在第一次 patch 前就自行選擇把 `images` 一次轉成 presentation-generator mapping，並保留原本 generic inverse handling。最終兩組都採取單一 mapping，只是 patch 形狀不同：

- A：直接重建 `images`，刪除 permutation-specific 分支，較小且保留既有 inverse lookup。
- B：另建 `rel_images`，同時顯式正規化 inverse letter，改動較多。

盲評認為兩者都具體、承重且實際塑造 patch；A 的保守性與 B 的顯式正規化不足以形成兩個維度以上的實質勝差，因此判 tie。

## 成本

- A wall time：105.031 秒；B：165.047 秒，單題 B 約增加 57.1%。
- A main-model output tokens：2,735；B：3,873，約增加 41.6%。

單題變異很大，不能把這些百分比當成穩定成本估計。

## 結論與限制

這次確認：現有 adapter 可以成功使用 Claude Opus 5，跨家族 Provider 會產生措辭與關注角度不同的 Nudge，而且 B 的後續修改與 Nudge 有明顯對齊。但在這題上，A 主模型已自行找到同一個承重設計，因此最終安全性與盲評品味仍為平手。

這是 1 題 smoke，只能證明整條 Opus pipeline 可運作並提供一個具體反應案例；不能判定 Opus reviewer 普遍有效，也不足以決定是否全面取代 Sol reviewer。
