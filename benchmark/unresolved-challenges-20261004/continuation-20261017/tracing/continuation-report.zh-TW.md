已完成 L2 續作；原始完整固定驗收與相關功能檢查全部通過，沒有已知未解決的驗收缺口。這是已知悉歷史失敗的續作紀錄，不能據此推論 Nudge 的因果產品效果。

本次增量修改涉及 6 個既有實作檔及 1 個新測試檔；完整交付 patch 同時保留 L2 的既有實作與回歸測試。

- `filter/layer_filters.rs`：在 enabled、callsite interest、max-level hint 三條路徑保留內層全域限制；局部 filter 只限制消費者分支。即使局部拒絕，也查詢內層的全域否決。
- `layer.rs`、`registry/mod.rs`、`registry/sharded.rs`、`registry/stack.rs`：filtered current 使用仍在進入狀態的 span，跳過不可見項；Registry 使用既有堆疊，自訂 subscriber 的 Layered 邊界補記進入與離開。Context 的 current、lookup 與 contextual event scope 使用同一視圖。保留既有重複進入排序及非依序離開行為；不把未進入的父 span 當作 current。
- `layer.rs`、`reload.rs`、`filter/layer_filters.rs`：以 reload 實例的版本記號追蹤真正的修改；相同 interest 的一般重新註冊不再使待派送決策失效。舊 span 保存的過濾視圖仍不受 reload 改寫。
- 新增 `tracing-subscriber/tests/filter_continuation_regressions.rs`，共 8 項測試，涵蓋動態／靜態全域否決、局部接受／拒絕、巢狀包裝、全域 hints、純全域 filter、Registry 與 opaque subscriber 的 current 視圖、重入、無關快取重建及 interest 不變的動態 reload。

先寫測試再修正：`regressions-red.txt` 記錄最初 4 個語意失敗；`regressions-reentrancy-red.txt` 記錄重入 current 的失敗；`regressions-cache-red.txt` 穩定重現一般重建造成動態求值 2 次而非 1 次。初次 registry-only 並行執行另在 `registry-only-tests.txt` 發現 L2 的動態快取測試求值 5 次而非 3 次；單獨執行通過的診斷紀錄在 `cache-isolated.txt`。這個問題已修正，並保留所有失敗證據。

最終驗證如下；表中測試數量不互相加總。

| 檢查 | 結果 | 證據 |
| --- | --- | --- |
| 指定完整測試，預設功能加 env-filter、registry、regex/unicode | 184 通過、0 失敗、3 個原有忽略 | `full-tests-final.txt` |
| 無預設功能、registry，受影響的 library／layer／固定／回歸測試 | 88 通過、0 失敗 | `registry-only-final.txt` |
| 無預設功能，library 與公開 layering 測試 | 15 通過、0 失敗 | `std-only-tests.txt` |
| 無預設功能、registry+env-filter+regex/unicode，完整 --tests | 141 通過、0 失敗、3 個原有忽略 | `registry-env-final.txt` |
| 無預設功能 cargo check | exit 0 | `no-default-check.txt` |
| 修改檔的 rustfmt --check 與 git diff --check | exit 0 | `format-final.txt`、`diff-check-final.txt` |
| 第二版 canonical evaluator 保留測試 | 148 通過、0 失敗 | `actor-evaluation-2/evidence.json` |
| 三組固定 contract 探針 | 10 項全部 passed:true，三組均 pass | `actor-evaluation-2/contract_*.txt` |

實際使用的主要命令如下，工作目錄為本次 checkout；輸出保存在本報告所在目錄。Cargo.toml 沒有獨立的 `std` feature，無預設功能的 library 檢查即涵蓋 std 基本組合。

```powershell
cargo test --offline --locked -p tracing-subscriber --features env-filter,registry,regex/unicode --tests
cargo test --offline --locked -p tracing-subscriber --no-default-features --features registry --lib --test per_layer_filters --test filter_continuation_regressions --test benchmark_public_layer_tests --test contract_tracing_contract_v2_rs --test contract_tracing_hint_bounds_rs --test contract_tracing_judge_concerns_rs --test layer_filter_interests_are_cached --test multiple_layer_filter_interests_cached --test cached_layer_filters_dont_break_other_layers --test hinted_layer_filters_dont_break_other_layers --test unhinted_layer_filters_dont_break_other_layers
cargo check --offline --locked -p tracing-subscriber --no-default-features
cargo test --offline --locked -p tracing-subscriber --no-default-features --lib --test benchmark_public_layer_tests
cargo test --offline --locked -p tracing-subscriber --no-default-features --features registry,env-filter,regex/unicode --tests
rustfmt --check --edition 2018 --config skip_children=true tracing-subscriber/src/filter/layer_filters.rs tracing-subscriber/src/layer.rs tracing-subscriber/src/registry/mod.rs tracing-subscriber/src/registry/sharded.rs tracing-subscriber/src/registry/stack.rs tracing-subscriber/src/reload.rs tracing-subscriber/tests/filter_continuation_regressions.rs
git diff --check
```

調查固定探針與第一輪回歸測試時，另使用：

```powershell
cargo test --offline --locked -p tracing-subscriber --features env-filter,registry,regex/unicode --test filter_continuation_regressions --test contract_tracing_contract_v2_rs --test contract_tracing_hint_bounds_rs --test contract_tracing_judge_concerns_rs -- --nocapture --test-threads=1
```

Canonical evaluator 執行兩次，各使用新的輸出目錄。第一版已通過所有固定驗收，後續因 registry-only 檢查揭露快取問題而繼續修正。最終驗收命令如下：

```powershell
python "<STUDY_ROOT>\tracing-l2-continuation-20261017\continuation.py" export --output "<STUDY_ROOT>\tracing-l2-continuation-20261017\continuation-candidate-2.patch"
python "<STUDY_ROOT>\tracing-l2-continuation-20261017\continuation.py" evaluate --patch "<STUDY_ROOT>\tracing-l2-continuation-20261017\continuation-candidate-2.patch" --output "<STUDY_ROOT>\tracing-l2-continuation-20261017\actor-evaluation-2"
```

`continuation-final.patch` 與已驗收的第二版 patch 位元組相同，SHA-256 為 `03aa139826be0e426a5b6a52f368051bdbf899112e96fbe14468102b4f28b486`。完整 patch 含新原始碼；`continuation-implementation.diff` 只呈現相對於 L2 的實作增量，已逐項檢視。Evaluator 在獨立 checkout 使用固定保留測試；本次新增測試另在目前 checkout 驗證。

本次收到 3 則 Nudge，另有 1 次無回饋。原始紀錄保存在 `continuation-nudge-attempts.json`。

| Nudge／attempt ID 前綴 | 採納或拒絕 | 對應修改與驗證 |
| --- | --- | --- |
| `8293e944`：current_span_filtered 無呼叫點，要求仍可查得進入中的可見根 | 採納 | 將 Context.current_span 接到 Registry／自訂 subscriber 的 entered stack；兩種 current-view 回歸測試及固定 current_view_retains_visible_entered_root 全通過。 |
| `6141bc40`：inner.enter 先於 stack.push，重入可能讀到舊 current | 採納需求及先更新再派送的順序；未採跨任意 subscriber 共用唯一堆疊的額外結構 | Layered.enter 在呼叫 inner.enter 前先 push，exit 在派送前先 pop；同一 subscriber 邊界的 Context 與其子樹共用該邊界的堆疊。保留 subscriber 邊界，避免混用自訂 subscriber 的 span ID 與生命週期。新增重入測試先失敗，修正後通過。 |
| `a1615413`：再次指出相同 enter 順序，要求 on_enter 重入可見新 span | 同上，採納行為要求與更新順序，未擴大為跨 subscriber 共享狀態 | 同一修正與 custom_subscriber_updates_current_before_reentrant_callbacks 驗證；最終完整及各 feature 測試亦通過。 |

Provider 執行期設定已讀回確認為 `gpt-6.1-sol`／`xhigh`／strict。未切換 Actor／Provider 模型、未委派、未建立其他 agent，未提交、推送、建立 PR、安裝套件或使用網路查詢。

`immutability-final.json` 驗證原始清單中的 208 個歷史／固定測試／evaluator 輸入檔與 24 個 checkout 既有測試檔，內容全部未變；本次未修改其他既有測試。所有編輯使用 apply_patch。`continuation-verification.json` 彙整最終計數、日誌雜湊與 evaluator 結果。

剩餘缺口：無已知的固定合約或相關 feature 檢查缺口。驗證範圍是本次要求的功能與既有測試；沒有額外的效能或形式化證明主張。
