# Shader 修正版端到端任務單 V2

狀態：契約修正後執行中；Codex CLI session `01a01910-685c-7a01-9bff-340e5a1e2e9e`。

## 一、這次要驗證什麼

驗證修正版 Masters' Nudge 能否在真實 Shader 研究中：

1. 從當下研究材料選到應關注的 Persona；
2. 保留 trajectory Finding，不因研究方向剛轉變就浪費；
3. 在候選仍可深化時成功注入；
4. 指出主模型尚未處理的盲點，讓既有修正比注入前計畫推得更遠；
5. 不破壞固定契約、可重現性與既有 Pareto 前沿。

這是修正版工具的短期端到端驗證，不是 30%／50%／70% GPU 門檻重測，也不是 Nudge 因果效果證明。

## 二、隔離起點

- 建議新工作區：`E:\projects\shader-long-tail-v2`
- 種子 commit：`10839d137e6b49e2f22d48d9d71946a37462da8f`
- 該 commit 已有固定合約與新鮮 `BaselineV0` 證據，但尚未放入長尾候選。
- 新工作區開始前，`git status --short` 必須為空。
- 不得讀取或複製 `shader-long-tail-v1` 的 LT001–LT050、舊 Nudge、舊結果或停止結論。
- Codex 專案記憶維持停用；權威材料只來自新工作區的程式碼、合約、台帳與量測。

## 三、主模型只接收這個 Goal

> 交付在固定契約下經實證建立、可重現的最佳 Shader Pareto 前沿。

Goal 不提 Masters' Nudge、Persona、Router、注入、10 則樣本、評分方式或預期反應。

## 四、固定研究契約

- Unity `6000.0.80f1`
- URP `17.0.4`
- D3D11、1920×1080、Intel UHD 接受硬體
- `ShieldGalleryV1`
- 畫面覆蓋目標 60%，只允許 1 像素光柵化邊界容差；不得以容差放寬 SSIM 或色差
- 300 warmup frames、1,200 sampled frames、5 repetitions
- 每個候選都要有父前沿、可否證假設、機制家族、預期消除工作、實際證據與判定
- 每個候選格最多細修 2 次
- 不得以三次無新增 Pareto、時間、token、已有可交付候選或單輪無改善宣告研究完成
- 接受候選不得支配其父前沿，也不得放寬畫質、時間、資源或量測契約

## 五、Masters' Nudge 固定設定

- 使用啟動時實際安裝的修正版；run manifest 記錄完整版本與雜湊
- Shader domain、Grok medium
- checkpoint timeout 90 秒；stop timeout 120 秒
- 自動 structured-material routing，不手動輪替 Persona
- 不設 Persona 配額、平衡、cooldown 或固定比例
- 六類材料路由：
  - executed work → Carmack
  - visibility work → Akenine-Möller
  - procedural representation → Quilez
  - cross-pass material semantics → Karis
  - spatiotemporal stability → Lottes
  - platform generality → Tatarchuk
- trajectory Finding 在研究 fingerprint 改變後保留到下一個合適 hook；candidate Finding 仍可隨來源候選失效
- 相同 gap 且證據未變時去重；新證據或新盲點才可再產生 Finding

## 六、外部觀察邊界

監看不修改 Shader 專案、不手動注入、不切換 Persona，也不額外呼叫 Provider。

第一次同時具備以下條件時做 GO／NO-GO：

1. 至少 10 則成功注入的 Nudge；
2. 每則 Nudge 注入後都有至少一個仍可深化的研究決策；
3. 已能比較注入前計畫與注入後最多兩個研究決策；
4. 至少完成 12 個技術上不同的候選格。

若完成 20 個候選格仍不足 10 則可評估注入，判定本輪管線證據不足，對「進入完整長尾重測」作 NO-GO；不得把結果描述成已證明 Nudge 無效。

到達觀察邊界只代表工具驗證階段收樣，不代表 Shader Goal、正式飽和或 50 格研究完成。是否繼續長尾由使用者另行決定。

## 七、反應判定

以每則 Nudge 的 injected 時點為基線：

- `explicit_uptake`：主模型直接接住同一盲點並改寫假設、解釋或決策。
- `reinterpretation`：保留原候選，但因盲點改變結果解讀、限制或外推範圍。
- `possible_influence`：新增注入前計畫沒有的控制變因、邊界案例、量測、機制分解、修正深化或 follow-up。
- `temporal_only`：只是時間相鄰，或後續行為原本就在計畫內。
- `no_observable_response`：後續決策沒有內容對應。

Nudge 不需要在候選選擇前出現，也不需要發明下一個方向。材料出現後指出盲點，並把尚未結束的修正推得更遠，就屬於可評估作用。

## 八、GO／NO-GO 門檻

只有全部成立才判 GO，進入新的完整長尾測試：

1. 10 則可評估注入中，至少 3 則形成內容對應的深化，且後續決策為 `F1` 或 `F2`；
2. 沒有 trajectory Finding 因 `shader-research-state-changed` 被 superseded；
3. 明確材料出現時，沒有經人工確認的錯誤 Persona 路由；
4. 合格待注入 Finding 的成功傳遞率至少 80%；
5. Provider timeout／error 比例不高於 20%，並保留在分母；
6. 候選父節點、機制、證據與判定完整率 100%；
7. 固定契約 fingerprint 不變，前沿沒有退步，`B = 0`。

任一門檻不成立即對「進入完整長尾重測」判 NO-GO，並把失敗歸到材料、路由、Provider、傳遞、主模型接取或研究契約其中一層，不混成單一工具失敗。

## 九、必留證據

- 新工作區路徑、Git commit、乾淨狀態
- Codex CLI、主模型、reasoning effort
- Masters' Nudge 版本、Prompt／Persona／Router 雜湊
- Grok CLI 版本、實際模型、medium effort、timeout
- 所有 Provider attempt、Finding、no_finding、error 與 latency
- pending、injected、expired、superseded delivery 時間線
- 每則 Nudge 的 Persona、route basis、finding scope、gap key、材料完整度
- 注入前計畫、注入後兩個決策與反應分類
- 候選台帳、Pareto 前沿、`F2/F1/N/B` 與契約 fingerprint

## 十、這份任務單不允許的結論

- 沒有對照組，不宣稱 Nudge 已證明造成改善。
- 10 則短期樣本不代表長尾 26–50 的穩定效果。
- Router 測試通過不代表 Provider 一定產生高品質 Finding。
- 單一 GPU、場景或工作區結果不代表 Asset Store 市場普遍成立。
