# Phase A reaction-quality evaluation

- Generated: 2026-08-13T01:51:22.051012+00:00
- Provider/model: `openai` / `gpt-5.6-sol`
- Fixtures: `evaluation\workflow-holdout-v2.json`
- Repeats: 2
- Randomization seed: 20260816
- Git commit: `06a110e2e668a3dcf8045646e7fb5a33b4355533`
- Fixtures SHA-256: `12cf1aefd98c83b813e63b45abc6d1d9a8c1a30bf3c9519d4e41d15e43fc5ef9`
- Runner SHA-256: `dfa78671791658ac1d0d794b4bb63697e95986c297ce5c56f20b2c41d092eba8`
- Base prompt SHA-256: `baa7af2b101dfd0b2a70b5d404a3ee09c01c48f648c3c059d83943783d23b80f`
- Reviewer CLI: `codex-cli 0.147.0`
- Interpretation: calibration only; not a formal product-impact claim.

## Condition summary

| Condition | Calls | Provider success | Raw schema | Status | Issue match | Correct silence | Avg chars | At 52 | Sentence ended | Oracle match | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 36 | 36/36 (100.0%) | 36/36 (100.0%) | 34/36 (94.4%) | 6/24 (25.0%) | 10/12 (83.3%) | 37.9 | 2/26 (7.7%) | 24/26 (92.3%) | 16/36 (44.4%) | 8135 ms |
| effective | 36 | 36/36 (100.0%) | 36/36 (100.0%) | 35/36 (97.2%) | 10/24 (41.7%) | 11/12 (91.7%) | 36.4 | 0/25 (0.0%) | 25/25 (100.0%) | 21/36 (58.3%) | 8377 ms |
| primary | 12 | 12/12 (100.0%) | 12/12 (100.0%) | 12/12 (100.0%) | 2/8 (25.0%) | 4/4 (100.0%) | 41.1 | 1/8 (12.5%) | 7/8 (87.5%) | 6/12 (50.0%) | 8533 ms |

## Paired outcomes

- `effective_vs_baseline`: 8 wins, 25 ties, 3 losses
- `effective_vs_primary`: 3 wins, 7 ties, 2 losses

## Per-call results

| Fixture | Condition | Lens | Expected | Actual | Chars | Schema | Match | Ended | Correct | Finding |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| workflow-beck-clean-short-feedback-loop | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-beck-clean-short-feedback-loop | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-beck-clean-short-feedback-loop | effective | beck | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-beck-clean-short-feedback-loop | effective | beck | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-beck-fix-thrashing-without-experiment | baseline | general | finding | finding | 26 | True | False | True | False | 同一失敗已跨三層換修法，仍缺少能排除假設的聚焦實驗。 |
| workflow-beck-fix-thrashing-without-experiment | baseline | general | finding | finding | 27 | True | False | True | False | 同一斷言下已連換三層修法，仍缺少能排除假設的聚焦實驗。 |
| workflow-beck-fix-thrashing-without-experiment | effective | beck | finding | finding | 25 | True | False | True | False | 同一失敗已換三種修法，仍缺少能排除假設的最小重現。 |
| workflow-beck-fix-thrashing-without-experiment | effective | beck | finding | finding | 27 | True | False | True | False | 同一失敗已跨三層改動，卻還沒有最小實驗能排除任一原因。 |
| workflow-beck-scope-after-acceptance | baseline | general | finding | finding | 37 | True | False | True | False | 驗證已對齊需求後仍擴張序列化重構，交付範圍已離開 task anchor。 |
| workflow-beck-scope-after-acceptance | baseline | general | finding | finding | 47 | True | False | True | False | 驗證已涵蓋需求，後續抽框架與改 JSON helper 的依據是順手，而非新增需求或失敗回饋。 |
| workflow-beck-scope-after-acceptance | effective | beck | finding | finding | 31 | True | False | True | False | 驗收與既有測試都已通過，後續重構是在替哪個尚未出現的需求工作？ |
| workflow-beck-scope-after-acceptance | effective | beck | finding | finding | 33 | True | True | True | True | 驗收與既有測試已全綠，後續重構卻沒有新需求或失敗回饋作為停止條件。 |
| workflow-carmack-clean-measure-one-change | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-carmack-clean-measure-one-change | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-carmack-clean-measure-one-change | effective | carmack | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-carmack-clean-measure-one-change | effective | carmack | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-carmack-clean-measure-one-change | primary | fowler | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-carmack-clean-measure-one-change | primary | fowler | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-carmack-optimizes-before-measurement | baseline | general | finding | finding | 52 | True | False | False | False | 沒有 baseline、profiler 與等價檢查，現在調 thread pool 是在改善哪個已確認 |
| workflow-carmack-optimizes-before-measurement | baseline | general | finding | finding | 37 | True | False | True | False | 還沒量瓶頸與輸出等價，就連疊三種優化，現在無法判斷哪個改動有效或破壞內容。 |
| workflow-carmack-optimizes-before-measurement | effective | carmack | finding | finding | 51 | True | True | True | True | 尚無 baseline、profiler 與等價檢查，調 thread pool 量到的會是哪個瓶頸？ |
| workflow-carmack-optimizes-before-measurement | effective | carmack | finding | finding | 50 | True | True | True | True | 沒有 baseline 與 profiler 就續調 thread pool，現在量到的瓶頸是什麼？ |
| workflow-carmack-optimizes-before-measurement | primary | beck | finding | finding | 52 | True | False | False | False | 三種優化已疊上去，卻還沒量 baseline 或確認輸出等價，thread pool 的下一步要驗證哪個 |
| workflow-carmack-optimizes-before-measurement | primary | beck | finding | finding | 38 | True | False | True | False | 三種優化已疊上去，卻還沒用 baseline 與輸出等價檢查確認方向和邊界。 |
| workflow-carmack-warm-benchmark-for-cold-goal | baseline | general | finding | finding | 37 | True | False | True | False | 完成宣告依賴熱程序迴圈，尚未驗證 cold start 與首次輸出一致性。 |
| workflow-carmack-warm-benchmark-for-cold-goal | baseline | general | finding | finding | 52 | True | False | False | False | 同一程序內的 benchmark 無法驗證 cold start，也未涵蓋首次輸出一致性，完成宣告跑在驗 |
| workflow-carmack-warm-benchmark-for-cold-goal | effective | carmack | finding | finding | 47 | True | True | True | True | 同一 process 的熱態快 40%，仍沒量到 cold start，也沒驗證首次輸出一致。 |
| workflow-carmack-warm-benchmark-for-cold-goal | effective | carmack | finding | finding | 31 | True | False | True | False | 量到的是同一程序內的熱路徑，如何支持冷啟動變快且首次輸出一致？ |
| workflow-carmack-warm-benchmark-for-cold-goal | primary | linus | finding | finding | 37 | True | False | True | False | 量到的是暖機後迴圈，卻用來宣告 cold start 與首次輸出都已完成。 |
| workflow-carmack-warm-benchmark-for-cold-goal | primary | linus | finding | finding | 39 | True | True | True | True | 把已載入狀態的加速當成完成，仍無法證明 cold start 與首次輸出要求。 |
| workflow-fowler-clean-characterize-then-change | baseline | general | no_finding | finding | 41 | True | False | True | False | JSON 以三種輸出鎖定，YAML 卻只有最小案例；完成條件是否被既有行為主導了？ |
| workflow-fowler-clean-characterize-then-change | baseline | general | no_finding | finding | 41 | True | False | True | False | JSON 用三種輸出固定行為，YAML 卻只有最小案例；完成條件是否仍偏向舊路徑？ |
| workflow-fowler-clean-characterize-then-change | effective | fowler | no_finding | finding | 38 | True | False | True | False | 只用一個 YAML 案例，還看不出純資料模型是否真能承接兩種格式的共同知識。 |
| workflow-fowler-clean-characterize-then-change | effective | fowler | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-fowler-policy-has-no-home | baseline | general | finding | finding | 30 | True | False | True | False | 五處同步改完且測試通過，但重複規則讓下次調整仍得靠逐處對齊。 |
| workflow-fowler-policy-has-no-home | baseline | general | finding | finding | 29 | True | True | True | True | 五處同步改動顯示折扣規則沒有單一來源，下次調整仍可能漏改。 |
| workflow-fowler-policy-has-no-home | effective | fowler | finding | finding | 25 | True | True | True | True | 五處同步修改顯示學生折扣規則仍沒有單一的知識歸屬。 |
| workflow-fowler-policy-has-no-home | effective | fowler | finding | finding | 26 | True | True | True | True | 五處同步同一比例與資格判斷，下一次調整仍得重走五處。 |
| workflow-fowler-refactor-before-characterization | baseline | general | finding | finding | 32 | True | False | True | False | 先改 430 行再補測試，JSON 輸出不變已失去可比對的基準。 |
| workflow-fowler-refactor-before-characterization | baseline | general | finding | finding | 44 | True | False | True | False | 在鎖定既有 JSON 行為前就累積 430 行重構，之後的測試還能分辨回歸來自哪一步嗎？ |
| workflow-fowler-refactor-before-characterization | effective | fowler | finding | finding | 33 | True | False | True | False | 先擴張 430 行再補特性測試，JSON 不變的邊界已被延後驗證。 |
| workflow-fowler-refactor-before-characterization | effective | fowler | finding | finding | 37 | True | False | True | False | 430 行重構先於 JSON 行為基線，之後測試還能分辨回歸來自哪一步嗎？ |
| workflow-jeff-clean-evidence-first-design | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-jeff-clean-evidence-first-design | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-jeff-clean-evidence-first-design | effective | jeff | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-jeff-clean-evidence-first-design | effective | jeff | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-jeff-compensation-before-owner | baseline | general | finding | finding | 35 | True | False | True | False | 權威來源仍未定，卻先疊同步與修復機制，多租戶權限的責任邊界反而更模糊。 |
| workflow-jeff-compensation-before-owner | baseline | general | finding | finding | 46 | True | True | True | True | canonical owner 尚未決定，卻先增加兩份快取與三個寫入方，責任邊界反而更模糊。 |
| workflow-jeff-compensation-before-owner | effective | jeff | finding | finding | 45 | True | False | True | False | canonical owner 未定卻讓三方都能改角色；同步與修復是在替責任邊界未定還債。 |
| workflow-jeff-compensation-before-owner | effective | jeff | finding | finding | 41 | True | True | True | True | owner 尚未決定就複製角色並開放多方改寫，同步與修復是在替責任邊界未定付成本。 |
| workflow-jeff-solution-before-problem | baseline | general | finding | finding | 29 | True | True | True | True | 主要流失點與成功指標尚未定義，技術路徑卻已先鎖定提醒服務。 |
| workflow-jeff-solution-before-problem | baseline | general | finding | finding | 29 | True | False | True | False | 主要流失點與成功指標尚未定義，卻已先把解法鎖定在提醒服務。 |
| workflow-jeff-solution-before-problem | effective | jeff | finding | finding | 36 | True | False | True | False | 流失點與成功指標未定，就先鎖定提醒服務，後續系統成本是在解需求還是假設？ |
| workflow-jeff-solution-before-problem | effective | jeff | finding | finding | 40 | True | True | True | True | 主要流失點尚未定義，queue 與排程器可能只是在替過早選定的提醒方案增加成本。 |
| workflow-lamport-clean-invariant-first | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-lamport-clean-invariant-first | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-lamport-clean-invariant-first | effective | lamport | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-lamport-clean-invariant-first | effective | lamport | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-lamport-clean-invariant-first | primary | linus | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-lamport-clean-invariant-first | primary | linus | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-lamport-delay-patches-ordering | baseline | general | finding | finding | 37 | True | False | True | False | 每次都拉長 debounce，卻還沒有用 A、B 亂序測試排除真正的競態。 |
| workflow-lamport-delay-patches-ordering | baseline | general | finding | finding | 39 | True | True | True | True | 每次只拉長 debounce，仍沒有用交錯請求驗證「最後查詢勝出」的核心假設。 |
| workflow-lamport-delay-patches-ordering | effective | lamport | finding | finding | 43 | True | False | True | False | 調高 debounce 只改變機率，A 晚於 B 抵達時仍會破壞「最後查詢」不變條件。 |
| workflow-lamport-delay-patches-ordering | effective | lamport | finding | finding | 40 | True | False | True | False | 調高 debounce 只降低機率，A 晚於 B 抵達時「最後查詢」仍無法保證。 |
| workflow-lamport-delay-patches-ordering | primary | fowler | finding | finding | 49 | True | False | True | False | 每次調高 debounce 都只延後競態；單一 request 測試仍沒驗證最後查詢才可更新結果。 |
| workflow-lamport-delay-patches-ordering | primary | fowler | finding | finding | 43 | True | False | True | False | 第三次調高 debounce 仍繞開亂序根因，單一請求測試也無法驗證最後查詢必定勝出。 |
| workflow-lamport-happy-path-before-invariant | baseline | general | finding | finding | 48 | True | True | True | True | 成功案例不足以支撐部署；若扣款後、寫 marker 前中斷，retry 時「最多一次」還成立嗎？ |
| workflow-lamport-happy-path-before-invariant | baseline | general | finding | finding | 34 | True | False | True | False | 若中斷發生在扣款與寫入標記之間，retry 時「最多一次」還成立嗎？ |
| workflow-lamport-happy-path-before-invariant | effective | lamport | finding | finding | 37 | True | False | True | False | 若扣款後、marker 前中斷，retry 如何維持每張發票最多扣款一次？ |
| workflow-lamport-happy-path-before-invariant | effective | lamport | finding | finding | 36 | True | False | True | False | 若扣款後、寫 marker 前中斷，retry 時「最多一次」還成立嗎？ |
| workflow-lamport-happy-path-before-invariant | primary | beck | finding | finding | 28 | True | True | True | True | 成功案例不足以支撐部署；兩步間中斷仍未驗證「最多一次」。 |
| workflow-lamport-happy-path-before-invariant | primary | beck | finding | finding | 43 | True | False | True | False | 成功案例還沒驗證「扣款後、寫標記前」的中斷，部署無法回答 retry 是否仍只扣一次。 |
| workflow-linus-checklist-before-real-install | baseline | general | finding | finding | 37 | True | False | True | False | 交付宣告跑在必要驗證前面，Windows 與 Linux 安裝都還沒執行。 |
| workflow-linus-checklist-before-real-install | baseline | general | finding | finding | 36 | True | True | True | True | 完成宣告跑在必要驗證前面，Windows、Linux 乾淨安裝都未執行。 |
| workflow-linus-checklist-before-real-install | effective | linus | finding | finding | 27 | True | False | True | False | 完成宣告跳過了明定的雙平台安裝驗證，交付條件仍未成立。 |
| workflow-linus-checklist-before-real-install | effective | linus | finding | finding | 38 | True | True | True | True | 完成宣告已越過必要驗證：Windows 與 Linux 的乾淨安裝都未執行。 |
| workflow-linus-clean-single-path-proof | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-linus-clean-single-path-proof | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-linus-clean-single-path-proof | effective | linus | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-linus-clean-single-path-proof | effective | linus | no_finding | no_finding | 0 | True | True | None | True |  |
| workflow-linus-layers-hide-undecided-owner | baseline | general | finding | finding | 43 | True | False | True | False | 要求只留一條讀寫路徑，但 owner 未定、交付仍有四條路徑，測試通過不足以支撐完成。 |
| workflow-linus-layers-hide-undecided-owner | baseline | general | finding | finding | 41 | True | False | True | False | 交付要求單一路徑，但 owner 未定、圖上仍有四條路徑，完成宣告已偏離停止條件。 |
| workflow-linus-layers-hide-undecided-owner | effective | linus | finding | finding | 32 | True | False | True | False | owner 仍未定、讀寫有四條路徑，完成宣告與單一路徑要求矛盾。 |
| workflow-linus-layers-hide-undecided-owner | effective | linus | finding | finding | 42 | True | True | True | True | owner 仍是 TBD 且保留四條路徑，與「只有一條讀寫路徑」的完成條件直接矛盾。 |

## Scoring boundary

`issue_match` is a deterministic concept-group check. A miss can therefore be either a true miss or a defensible wording that needs blind human adjudication. `Sentence ended` only checks final punctuation and is a review queue, not proof that wording is complete or incomplete. Raw JSONL is retained for both reviews. Correct silence is objective for these seeded clean cases.
