# Phase A reaction-quality calibration

- Generated: 2026-08-13T00:00:30.049908+00:00
- Provider/model: `openai` / `gpt-5.6-sol`
- Fixtures: `C:\Users\Boreas\Desktop\masters-nudge\evaluation\fixtures.json`
- Repeats: 1
- Randomization seed: 20260813
- Git commit: `06a110e2e668a3dcf8045646e7fb5a33b4355533`
- Fixtures SHA-256: `602561725774bbf63afbf6acbb66e78cf857c0103e688ac5b78e6a9ae3c4c586`
- Runner SHA-256: `5e45005678237e398b29e85b94aa073f3c393a382eaa58774e508af7cbb80338`
- Interpretation: calibration only; not a formal product-impact claim.

## Condition summary

| Condition | Calls | Provider success | Raw schema | Status | Issue match | Correct silence | Sentence ended | Oracle match | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 12 | 12/12 (100.0%) | 12/12 (100.0%) | 12/12 (100.0%) | 8/8 (100.0%) | 4/4 (100.0%) | 4/8 (50.0%) | 12/12 (100.0%) | 8617 ms |
| effective | 12 | 12/12 (100.0%) | 12/12 (100.0%) | 12/12 (100.0%) | 8/8 (100.0%) | 4/4 (100.0%) | 7/8 (87.5%) | 12/12 (100.0%) | 12754 ms |
| primary | 4 | 4/4 (100.0%) | 4/4 (100.0%) | 4/4 (100.0%) | 2/2 (100.0%) | 2/2 (100.0%) | 0/2 (0.0%) | 4/4 (100.0%) | 7699 ms |

## Paired outcomes

- `effective_vs_baseline`: 0 wins, 12 ties, 0 losses
- `effective_vs_primary`: 0 wins, 4 ties, 0 losses

## Per-call results

| Fixture | Condition | Lens | Expected | Actual | Schema | Match | Ended | Correct | Finding |
|---|---|---|---|---|---:|---:|---:|---:|---|
| build-clean-minimal-date-fix | baseline | general | no_finding | no_finding | True | True | None | True |  |
| build-clean-minimal-date-fix | effective | beck | no_finding | no_finding | True | True | None | True |  |
| build-future-locale-registry | baseline | general | finding | finding | True | True | True | True | 新增兩個外掛架構檔與六種語系 stub，超出日期修正需求，擴大交付範圍與返工風險。 |
| build-future-locale-registry | effective | beck | finding | finding | True | True | True | True | 測試轉綠後新增兩個 plugin 架構檔與六種 locale stub，超出日期修正範圍，增加返工風險。 |
| carmack-clean-measured-path | baseline | general | no_finding | no_finding | True | True | None | True |  |
| carmack-clean-measured-path | effective | carmack | no_finding | no_finding | True | True | None | True |  |
| carmack-clean-measured-path | primary | jeff | no_finding | no_finding | True | True | None | True |  |
| carmack-redundant-json-roundtrips | baseline | general | finding | finding | True | True | False | True | 匯入 hot path 仍保留三次完整 payload copy，已佔 68% CPU，p95 仍為 |
| carmack-redundant-json-roundtrips | effective | carmack | finding | finding | True | True | True | True | 匯入路徑三次完整複製同一 payload，耗68% CPU；下游只需 dict，p95 仍 12 ms。 |
| carmack-redundant-json-roundtrips | primary | fowler | finding | finding | True | True | False | True | 匯入 hot path 仍讓同一 payload 完整複製三次，佔 68% CPU，p95 仍為 12 |
| design-clean-single-source | baseline | general | no_finding | no_finding | True | True | None | True |  |
| design-clean-single-source | effective | jeff | no_finding | no_finding | True | True | None | True |  |
| design-dual-status-writers | baseline | general | finding | finding | True | True | False | True | accounts.status 與 status_copy 都可寫且每分鐘才同步，衝突時沒有唯一真相來源 |
| design-dual-status-writers | effective | jeff | finding | finding | True | True | True | True | 正式欄位與status_copy皆可寫且隔分鐘同步，期間畫面會顯示不同狀態，違反最新一致需求。 |
| evolve-duplicated-discount-rule | baseline | general | finding | finding | True | True | True | True | checkout.py 等三模組仍各存折扣門檻，未來調整容易漏改，造成結帳、發票與退款判斷不一致。 |
| evolve-duplicated-discount-rule | effective | fowler | finding | finding | True | True | True | True | 會員折扣門檻仍分散在三個模組，日後調整須同步修改，容易因漏改造成結帳、發票與退款結果不一致。 |
| general-no-network-violation | baseline | general | finding | finding | True | True | False | True | telemetry.py 結束時會將事件 POST 到外部分析站，直接違反資料只能留在本機、不得連網或傳 |
| general-no-network-violation | effective | jeff | finding | finding | True | True | False | True | telemetry.py 結束時將本機事件 POST 到外部分析站，直接違反不得連網或傳出裝置的離線統計 |
| general-test-claim-conflict | baseline | general | finding | finding | True | True | False | True | pytest 仍有 CSV 換行引號與 UTF-8 BOM 兩項失敗，卻宣告完整測試全過，交付結論與工具 |
| general-test-claim-conflict | effective | linus | finding | finding | True | True | True | True | pytest 仍有 CSV 換行引號及 UTF-8 BOM 兩項失敗，完整測試全過的交付宣告與結果矛盾。 |
| lamport-clean-idempotent-retry | baseline | general | no_finding | no_finding | True | True | None | True |  |
| lamport-clean-idempotent-retry | effective | lamport | no_finding | no_finding | True | True | None | True |  |
| lamport-clean-idempotent-retry | primary | linus | no_finding | no_finding | True | True | None | True |  |
| lamport-stale-search-overwrite | baseline | general | finding | finding | True | True | True | True | 搜尋結果更新未比對 request_id，較早送出的 A 晚完成時會覆蓋 B，畫面因此顯示舊查詢結果。 |
| lamport-stale-search-overwrite | effective | lamport | finding | finding | True | True | True | True | 搜尋結果未檢查請求編號；B 先完成後，A 的舊回應仍會覆寫結果，最終顯示的不是最後一次查詢。 |
| lamport-stale-search-overwrite | primary | beck | finding | finding | True | True | False | True | 搜尋結果更新未比對 request_id，較早送出的 A 晚完成後會覆蓋 B，畫面不再對應使用者最後一次 |
| review-forward-only-layers | baseline | general | finding | finding | True | True | True | True | 固定一個 X-App-Version 卻新增三個純轉交類別，沒有額外行為，徒增維護與追蹤請求流程的成本。 |
| review-forward-only-layers | effective | linus | finding | finding | True | True | True | True | 新增的三個類別都只有一個原樣轉交方法，單一 header 被拆成三層，增加追查成本卻沒有額外行為。 |

## Scoring boundary

`issue_match` is a deterministic concept-group check. A miss can therefore be either a true miss or a defensible wording that needs blind human adjudication. `Sentence ended` only checks final punctuation and is a review queue, not proof that wording is complete or incomplete. Raw JSONL is retained for both reviews. Correct silence is objective for these seeded clean cases.
