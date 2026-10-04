# Astra max 雙模型：Tracing 兩次挑戰結果

日期：2026-10-04。Actor、Provider 都是 GPT-6 Astra max；兩次從同一基底獨立開始，Actor 不限時。

**完整交付：0/2。** 原七臂此題為0/14；本輪同時改模型、深度與解題時限，不將差異單獨歸因於工具或模型，亦不併入七臂排名。

| 次數 | 完整交付 | 功能／執行契約 | Actor 分鐘（含 Provider 等待） | 提醒／送達／故障 |
|---|---|---|---:|---|
| L1 | False | fail／pass | 31.32 | 3／3／0 |
| L2 | False | fail／pass | 53.63 | 3／3／0 |

## 固定驗收、提醒與程式結構

### L1

固定檢查：{"reserved": "pass", "tracing_contract_v2.rs": "fail", "tracing_hint_bounds.rs": "fail", "tracing_judge_concerns.rs": "fail"}。

執行契約：執行契約通過：以 apply_patch 修改產品原始碼與新增測試；完整命令未見提交、套件安裝、歷史變更、網路或委派。既有測試未修改，指定 cargo 測試、功能開關檢查與最終差異檢視均完成。Actor 不限時，31.32 分鐘不構成失敗；功能契約另由固定驗收判定為失敗。

程式品質：有實質行為修補與回歸測試，但尚非完整、可靠的交付；不能因新增抽象與測試量就評為高品味。固定補充探針 6/10 通過，兩份都另通過保留的 148 項測試。

Context、SpanRef、Scope 攜帶累積篩選視圖，且 current 使用已進入 span 堆疊，這些結構直接對應不同的關係需求。另一方面，__is_filtered 的單一布林分類不足以區分全域門檻與實際接收者；combine_enabled／combine_hint 的分支規則仍把純全域篩選器當接收者。快照、弱世代、識別值轉移和額外 entered stack 各自有理由，但留下跨層同步責任，並未讓錯誤狀態難以表達。

- 全域 LevelFilter 允許、所有實際觀察者拒絕時仍啟用 span 且計算欄位：all_observers_reject_under_global_filter 的 field_evaluations=2、span_disabled=false；pure_global_filter_does_not_enable_rejected_items 的 fields=1、span_disabled=false。
- INFO 接收者外加 TRACE 全域門檻，max_level_hint 回傳 TRACE，應為 INFO；全域門檻被錯算為額外接收者。
- 自訂 Veto 被 with_filter(true) 包裝後，其拒絕不能阻止兄弟接收事件；wrapped_custom_global_veto_rejects_every_consumer 的 events=1，應為0。Filtered.enabled 將內層拒絕壓為分支拒絕，再被兄弟的 OR 接收蓋過。
- current_view_retains_visible_entered_root 通過：仍進入中的可見 root 不會因另一個無親屬關係的隱藏 root 被漏掉。快取重載、Arc、欄位重入與 Context.enabled 補查亦通過。

提醒採納：三次提醒均有實際結構採納；不等於完整契約已解決。提醒1要求 Context→SpanRef→Scope 累積視圖與跳過拒絕祖先，最終實作與 nested_filters 測試可見此結構；提醒2要求每次發送獨立決策快照以保護重入，最終 FilterState、EnabledGuard 與 snapshot 及 reentrant_delivery 測試相符；提醒3要求 entered stack 而非 parent chain 求 current，最終 Registry.current_span_filtered／自訂 subscriber ThreadLocalSpanStack 與兩個不同 root 測試相符，固定 current-view 探針也通過。Actor L37、L41、L63-L82 可見對應工作。但 Actor 本已計畫其中部分需求，不能將全部成果因果歸功於 Provider。

來源：[Actor 說明](runs/tracing-1523/L1/actor-final.txt)、[原始修改](runs/tracing-1523/L1/final.patch)、[提醒](runs/tracing-1523/L1/provider-attempts.json)、[執行覆核](runs/tracing-1523/L1/execution-review.json)。

### L2

固定檢查：{"reserved": "pass", "tracing_contract_v2.rs": "fail", "tracing_hint_bounds.rs": "pass", "tracing_judge_concerns.rs": "fail"}。

執行契約：執行契約通過：以 apply_patch 修改產品原始碼與新增測試，並刪除自身暫存驗證日誌；完整命令未見提交、套件安裝、歷史變更、網路或委派。既有測試未修改，指定 cargo 測試及後續受影響測試、功能開關與最終差異檢視完成。Actor 不限時，53.63 分鐘不構成失敗；功能契約另由固定驗收判定為失敗。

程式品質：相較第一份，固定補充探針缺口較少（8/10 通過），但仍有核心語意錯誤，尚不宜判為完整或高品味交付。兩次是獨立嘗試，通過數差異不是模型能力的統計結論。

FilterResult 明確分開 global 與 consumers，分別 AND 與 OR，比單一 filtered 布林能更精確表達合併責任；Option::None 的空接收者也有直接表示。但 Filtered.__enabled 又對內層結果呼叫 result()，把全域拒絕與分支拒絕壓成同一布林，再回傳 global=true，所以核心區分未跨越包裝邊界。LevelFilter／EnvFilter 特例、四個 TLS 通道、owner 型別／位址與 revision 快取仍需共同維持一致；新增層次本身不能證明減少了完整流程的維護責任。

- 與第一份相同，自訂全域 Veto 經 with_filter 包裝後被降為分支拒絕，兄弟仍收到一筆事件；wrapped_custom_global_veto_rejects_every_consumer 的 events=1，應為0。
- Context.current_span 只沿目前 span 的父鏈找可見祖先，不能取代 entered stack。另一個隱藏 root 已進入時，仍進入中的可見 root 被漏掉：current_view_retains_visible_entered_root observations=[["",""]]，應為 [["visible","visible"]]。
- 全部實際接收者拒絕時的欄位停用、純全域門檻與 max-level-hint 均通過；相較第一份改善了這些具體情況。
- boxed/reload、同篩選器重載保留舊 span 隱藏、Arc、欄位重入與 Context.enabled 補查通過；自身測試只檢查 current 的親屬鏈案例，漏掉兩個獨立 entered root。

提醒採納：三次提醒均有實際採納；仍漏掉包裝邊界與 current 的關係語意。提醒1要求公開 registry 下的 Filter、函式篩選器與 with_filter，最終公開匯出與建構 API 已接通；提醒2要求快取世代與 pending 決策綁定，最終 revision、Weak 世代及 pending 檢查、reload 首筆事件與整個 Filtered 替換回歸測試對應；提醒3要求 Option::None 為空消費者，最終 false／never／OFF 三組 overrides 與 absent_layers 測試直接採納，global AND／consumer OR 也被明確建模。Actor L46、L59 回報對應修補。這些建議部分與原任務／Actor 既有規劃重疊，採納證據不支持單一因果歸因。

來源：[Actor 說明](runs/tracing-1523/L2/actor-final.txt)、[原始修改](runs/tracing-1523/L2/final.patch)、[提醒](runs/tracing-1523/L2/provider-attempts.json)、[執行覆核](runs/tracing-1523/L2/execution-review.json)。

## 用量與方法

| 次數 | Actor＋Provider 輸入（含快取） | 快取輸入 | 未快取輸入 | 輸出 |
|---|---:|---:|---:|---:|
| L1 | 6,283,333 | 6,015,872 | 267,461 | 78,942 |
| L2 | 5,956,318 | 5,674,624 | 281,694 | 81,904 |

以下為各次原始 Token 用量；缺值保留 null，Provider 呼叫不存在時才是0。Actor 的輸入包含 Provider 送達後續上下文；Provider 模型本身另記，不能只看 Actor 費用。reasoning output 是 output 的子集，不重複加總。

```json
[
  {
    "arm": "L1",
    "actor_usage": {
      "input_tokens": 5904012,
      "cached_input_tokens": 5746176,
      "output_tokens": 63467
    },
    "provider_usage": {
      "input_tokens": 379321,
      "cached_input_tokens": 269696,
      "output_tokens": 15475
    }
  },
  {
    "arm": "L2",
    "actor_usage": {
      "input_tokens": 5677348,
      "cached_input_tokens": 5485440,
      "output_tokens": 67623
    },
    "provider_usage": {
      "input_tokens": 278970,
      "cached_input_tokens": 189184,
      "output_tokens": 14281
    }
  }
]
```

本輪執行契約與程式碼由 Codex 閱讀原始行動及程式作語意覆核，已知組別；沒有新增匿名品味評審票。原七臂沒有合格的 Tracing 答案，因此不作與失敗交付的品味勝負排名。

條件、harness、傳輸等待與來源見 [MATERIALS](evidence.zip)、[計畫](evidence.zip)；完整數據見 [results-summary.json](results-summary.json)，檔案指紋與原材料保全見 [final-integrity.json](evidence.zip)。

公開副本：本機路徑已匿名化；原始指紋與公開指紋見 [來源索引](source-index.json)。完整事件、執行證據、固定驗收與工具快照位於 [證據包](evidence.zip)。原始 final.patch 未修改。
