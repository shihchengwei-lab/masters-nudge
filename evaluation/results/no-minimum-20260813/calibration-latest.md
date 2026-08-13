# Phase A reaction-quality evaluation

- Generated: 2026-08-13T00:37:55.762006+00:00
- Provider/model: `openai` / `gpt-5.6-sol`
- Fixtures: `C:\Users\Boreas\Desktop\masters-nudge\evaluation\fixtures.json`
- Repeats: 2
- Randomization seed: 20260814
- Git commit: `06a110e2e668a3dcf8045646e7fb5a33b4355533`
- Fixtures SHA-256: `602561725774bbf63afbf6acbb66e78cf857c0103e688ac5b78e6a9ae3c4c586`
- Runner SHA-256: `dfa78671791658ac1d0d794b4bb63697e95986c297ce5c56f20b2c41d092eba8`
- Base prompt SHA-256: `f76a64c860bd9a1c8c52542cc7957fcfddcada3a8787535bca4ffafe767897ba`
- Reviewer CLI: `codex-cli 0.147.0`
- Interpretation: calibration only; not a formal product-impact claim.

## Condition summary

| Condition | Calls | Provider success | Raw schema | Status | Issue match | Correct silence | Avg chars | At 52 | Sentence ended | Oracle match | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 24 | 24/24 (100.0%) | 24/24 (100.0%) | 24/24 (100.0%) | 11/16 (68.8%) | 8/8 (100.0%) | 45.4 | 3/16 (18.8%) | 13/16 (81.2%) | 19/24 (79.2%) | 8029 ms |
| effective | 24 | 24/24 (100.0%) | 24/24 (100.0%) | 24/24 (100.0%) | 13/16 (81.2%) | 8/8 (100.0%) | 46.2 | 8/16 (50.0%) | 10/16 (62.5%) | 21/24 (87.5%) | 8191 ms |
| primary | 8 | 8/8 (100.0%) | 8/8 (100.0%) | 8/8 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 49.5 | 1/4 (25.0%) | 2/4 (50.0%) | 8/8 (100.0%) | 7291 ms |

## Paired outcomes

- `effective_vs_baseline`: 2 wins, 22 ties, 0 losses
- `effective_vs_primary`: 0 wins, 8 ties, 0 losses

## Per-call results

| Fixture | Condition | Lens | Expected | Actual | Chars | Schema | Match | Ended | Correct | Finding |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| build-clean-minimal-date-fix | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| build-clean-minimal-date-fix | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| build-clean-minimal-date-fix | effective | beck | no_finding | no_finding | 0 | True | True | None | True |  |
| build-clean-minimal-date-fix | effective | beck | no_finding | no_finding | 0 | True | True | None | True |  |
| build-future-locale-registry | baseline | general | finding | finding | 50 | True | True | True | True | 新增 locale plugin 架構與六種 stub 超出日期修正範圍，擴大交付面並增加返工風險。 |
| build-future-locale-registry | baseline | general | finding | finding | 50 | True | True | True | True | 新增 locale plugin 架構與六種 stub 超出日期修正範圍，擴大交付面並增加返工風險。 |
| build-future-locale-registry | effective | beck | finding | finding | 52 | True | True | True | True | 目標測試轉綠後仍新增 plugin 架構與六種 locale stub，超出日期修正範圍，增加返工風險。 |
| build-future-locale-registry | effective | beck | finding | finding | 52 | True | True | False | True | 目標測試已通過後仍新增 plugin 架構與六種 locale stub，超出日期修正範圍，增加返工風險 |
| carmack-clean-measured-path | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| carmack-clean-measured-path | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| carmack-clean-measured-path | effective | carmack | no_finding | no_finding | 0 | True | True | None | True |  |
| carmack-clean-measured-path | effective | carmack | no_finding | no_finding | 0 | True | True | None | True |  |
| carmack-clean-measured-path | primary | jeff | no_finding | no_finding | 0 | True | True | None | True |  |
| carmack-clean-measured-path | primary | jeff | no_finding | no_finding | 0 | True | True | None | True |  |
| carmack-redundant-json-roundtrips | baseline | general | finding | finding | 52 | True | True | False | True | 匯入 hot path 仍保留三次完整 copy，已知佔 68% CPU，未處理 p95 12 ms 超 |
| carmack-redundant-json-roundtrips | baseline | general | finding | finding | 45 | True | False | True | False | 匯入 hot path 仍保留三次完整轉換，p95 為 12 ms，未達 8 ms 目標。 |
| carmack-redundant-json-roundtrips | effective | carmack | finding | finding | 52 | True | True | False | True | 匯入 hot path 對同一 payload 完整複製三次，佔 68% CPU；下游只需 dict，保 |
| carmack-redundant-json-roundtrips | effective | carmack | finding | finding | 52 | True | True | False | True | 匯入 hot path 對同一 payload 完整複製三次，耗掉 68% CPU；下游只需 dict， |
| carmack-redundant-json-roundtrips | primary | fowler | finding | finding | 52 | True | True | False | True | 匯入 hot path 仍對同一 payload 完整複製三次，p95 仍為 12 ms，未達 8 ms |
| carmack-redundant-json-roundtrips | primary | fowler | finding | finding | 51 | True | True | False | True | 匯入 hot path 仍對同一 payload 完整複製三次，p95 為 12 ms，未達 8 ms |
| design-clean-single-source | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| design-clean-single-source | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| design-clean-single-source | effective | jeff | no_finding | no_finding | 0 | True | True | None | True |  |
| design-clean-single-source | effective | jeff | no_finding | no_finding | 0 | True | True | None | True |  |
| design-dual-status-writers | baseline | general | finding | finding | 44 | True | False | True | False | 雙欄位都可寫且每分鐘才同步，期間會顯示不同狀態，也可能互相覆寫，違反所有畫面一致的要求。 |
| design-dual-status-writers | baseline | general | finding | finding | 52 | True | False | False | False | accounts.status 與 status_copy 可各自寫入且每分鐘才同步，衝突時無唯一真相， |
| design-dual-status-writers | effective | jeff | finding | finding | 52 | True | False | False | False | accounts.status 與 status_copy 都可寫且每分鐘雙向同步，沒有單一真實來源，衝 |
| design-dual-status-writers | effective | jeff | finding | finding | 52 | True | False | False | False | accounts.status 與 status_copy 都可寫且每分鐘雙向同步，沒有單一狀態來源，衝 |
| evolve-duplicated-discount-rule | baseline | general | finding | finding | 38 | True | True | True | True | 折扣門檻仍分散在三個模組，日後調整容易漏改，造成結帳、發票與退款結果不一致。 |
| evolve-duplicated-discount-rule | baseline | general | finding | finding | 37 | True | True | True | True | 折扣門檻仍散落三個模組，之後調整容易漏改，造成結帳、發票與退款判斷不一致。 |
| evolve-duplicated-discount-rule | effective | fowler | finding | finding | 42 | True | True | True | True | 會員折扣門檻仍散落三個模組，下次調整須同步修改，容易產生結帳、發票與退款規則不一致。 |
| evolve-duplicated-discount-rule | effective | fowler | finding | finding | 36 | True | True | True | True | 會員折扣門檻仍散落三個模組，下次調整須同步修改，容易產生折扣判斷不一致。 |
| general-no-network-violation | baseline | general | finding | finding | 51 | True | True | True | True | telemetry.py 結束時把事件 POST 到外部分析站，直接違反資料不得連網或傳出裝置的要求。 |
| general-no-network-violation | baseline | general | finding | finding | 50 | True | True | True | True | telemetry.py 結束時會把事件 POST 到外部分析站，違反資料不得連網或傳出裝置的要求。 |
| general-no-network-violation | effective | jeff | finding | finding | 45 | True | True | True | True | telemetry.py 結束時會 POST 統計資料，直接違反不得連網或傳出裝置的需求。 |
| general-no-network-violation | effective | jeff | finding | finding | 52 | True | True | True | True | telemetry.py 結束時會把事件 POST 到外部分析站，直接違反資料不得連網或傳出裝置的要求。 |
| general-test-claim-conflict | baseline | general | finding | finding | 47 | True | True | True | True | 完整測試仍有 2 項 CSV 測試失敗，卻宣告全部通過可交付，結論與 pytest 證據矛盾。 |
| general-test-claim-conflict | baseline | general | finding | finding | 52 | True | True | False | True | pytest 仍有 CSV 換行引號與 UTF-8 BOM 兩項失敗，與「完整測試全過、可交付」的宣告矛 |
| general-test-claim-conflict | effective | linus | finding | finding | 39 | True | True | True | True | 完整測試仍有 2 項 CSV 測試失敗，卻宣告全部通過可交付，結論與證據矛盾。 |
| general-test-claim-conflict | effective | linus | finding | finding | 37 | True | True | True | True | pytest 仍有 2 項 CSV 測試失敗，卻宣告完整套件通過並可交付。 |
| lamport-clean-idempotent-retry | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| lamport-clean-idempotent-retry | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| lamport-clean-idempotent-retry | effective | lamport | no_finding | no_finding | 0 | True | True | None | True |  |
| lamport-clean-idempotent-retry | effective | lamport | no_finding | no_finding | 0 | True | True | None | True |  |
| lamport-clean-idempotent-retry | primary | linus | no_finding | no_finding | 0 | True | True | None | True |  |
| lamport-clean-idempotent-retry | primary | linus | no_finding | no_finding | 0 | True | True | None | True |  |
| lamport-stale-search-overwrite | baseline | general | finding | finding | 43 | True | False | True | False | 搜尋結果缺少 request_id 檢查，較晚完成的舊查詢 A 會覆蓋最後輸入的 B。 |
| lamport-stale-search-overwrite | baseline | general | finding | finding | 43 | True | True | True | True | Search A 晚完成會覆蓋 Search B 結果，搜尋框顯示的不是最後一次查詢。 |
| lamport-stale-search-overwrite | effective | lamport | finding | finding | 46 | True | True | True | True | 搜尋結果更新未檢查 request_id；A 晚於 B 完成會覆寫 B，畫面顯示舊查詢結果。 |
| lamport-stale-search-overwrite | effective | lamport | finding | finding | 42 | True | True | True | True | 搜尋結果更新未檢查 request_id；A 晚完成會覆寫 B，畫面顯示舊查詢結果。 |
| lamport-stale-search-overwrite | primary | beck | finding | finding | 46 | True | True | True | True | 搜尋回應未比對 request_id，較早的 A 晚完成會覆蓋 B，畫面不再是最後查詢結果。 |
| lamport-stale-search-overwrite | primary | beck | finding | finding | 49 | True | True | True | True | 搜尋結果更新未核對 request_id，較早的 A 後完成會覆蓋 B，畫面不再對應最後一次查詢。 |
| review-forward-only-layers | baseline | general | finding | finding | 36 | True | False | True | False | 測試只驗證 header 存在，未驗證版本值；空字串或錯誤版本也會通過。 |
| review-forward-only-layers | baseline | general | finding | finding | 36 | True | True | True | True | 為固定 header 新增三層純轉交類別，擴大維護面且沒有可見需求依據。 |
| review-forward-only-layers | effective | linus | finding | finding | 52 | True | False | False | False | VersionHeaderProvider、Adapter、Bridge 都只轉交同一字串，固定加標頭被 |
| review-forward-only-layers | effective | linus | finding | finding | 36 | True | True | True | True | 固定 header 被拆成三層純轉交，沒有獨立行為，增加維護與追蹤成本。 |

## Scoring boundary

`issue_match` is a deterministic concept-group check. A miss can therefore be either a true miss or a defensible wording that needs blind human adjudication. `Sentence ended` only checks final punctuation and is a review queue, not proof that wording is complete or incomplete. Raw JSONL is retained for both reviews. Correct silence is objective for these seeded clean cases.
