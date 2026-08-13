# Phase A reaction-quality calibration

- Generated: 2026-08-13T00:11:30.308618+00:00
- Provider/model: `openai` / `gpt-5.6-sol`
- Fixtures: `C:\Users\Boreas\Desktop\masters-nudge\evaluation\fixtures.json`
- Repeats: 2
- Randomization seed: 20260814
- Git commit: `06a110e2e668a3dcf8045646e7fb5a33b4355533`
- Fixtures SHA-256: `602561725774bbf63afbf6acbb66e78cf857c0103e688ac5b78e6a9ae3c4c586`
- Runner SHA-256: `51698113ffafc20a332041662dbd53c3c354d19af990e203083046bf52ee95cd`
- Reviewer CLI: `codex-cli 0.147.0`
- Interpretation: calibration only; not a formal product-impact claim.

## Condition summary

| Condition | Calls | Provider success | Raw schema | Status | Issue match | Correct silence | Sentence ended | Oracle match | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 24 | 24/24 (100.0%) | 24/24 (100.0%) | 22/24 (91.7%) | 7/16 (43.8%) | 8/8 (100.0%) | 4/16 (25.0%) | 15/24 (62.5%) | 8230 ms |
| effective | 24 | 24/24 (100.0%) | 24/24 (100.0%) | 24/24 (100.0%) | 14/16 (87.5%) | 8/8 (100.0%) | 4/16 (25.0%) | 22/24 (91.7%) | 9645 ms |
| primary | 8 | 8/8 (100.0%) | 8/8 (100.0%) | 8/8 (100.0%) | 2/4 (50.0%) | 4/4 (100.0%) | 2/4 (50.0%) | 6/8 (75.0%) | 9186 ms |

## Paired outcomes

- `effective_vs_baseline`: 7 wins, 17 ties, 0 losses
- `effective_vs_primary`: 2 wins, 6 ties, 0 losses

## Per-call results

| Fixture | Condition | Lens | Expected | Actual | Schema | Match | Ended | Correct | Finding |
|---|---|---|---|---|---:|---:|---:|---:|---|
| build-clean-minimal-date-fix | baseline | general | no_finding | no_finding | True | True | None | True |  |
| build-clean-minimal-date-fix | baseline | general | no_finding | no_finding | True | True | None | True |  |
| build-clean-minimal-date-fix | effective | beck | no_finding | no_finding | True | True | None | True |  |
| build-clean-minimal-date-fix | effective | beck | no_finding | no_finding | True | True | None | True |  |
| build-future-locale-registry | baseline | general | finding | finding | True | False | False | False | 目標修正與測試已完成，卻另增 locale_registry.py、plugin_loader.py 與 |
| build-future-locale-registry | baseline | general | finding | finding | True | True | False | True | locale_registry.py、plugin_loader.py 與六種 stub 超出前導零修正 |
| build-future-locale-registry | effective | beck | finding | finding | True | True | True | True | 目標測試轉綠後仍新增兩個外掛架構檔與六種未要求語系，範圍超出前導零修正，增加返工風險。 |
| build-future-locale-registry | effective | beck | finding | finding | True | True | False | True | 目標測試轉綠後仍新增兩個外掛架構檔與六種未要求的 locale stub，超出日期修正範圍並增加返工風險 |
| carmack-clean-measured-path | baseline | general | no_finding | no_finding | True | True | None | True |  |
| carmack-clean-measured-path | baseline | general | no_finding | no_finding | True | True | None | True |  |
| carmack-clean-measured-path | effective | carmack | no_finding | no_finding | True | True | None | True |  |
| carmack-clean-measured-path | effective | carmack | no_finding | no_finding | True | True | None | True |  |
| carmack-clean-measured-path | primary | jeff | no_finding | no_finding | True | True | None | True |  |
| carmack-clean-measured-path | primary | jeff | no_finding | no_finding | True | True | None | True |  |
| carmack-redundant-json-roundtrips | baseline | general | finding | finding | True | False | False | False | 匯入 hot path 仍保留三次完整 payload 轉換，已知占 68% CPU，p95 仍為 12 |
| carmack-redundant-json-roundtrips | baseline | general | finding | finding | True | False | False | False | 匯入 hot path 仍保留三段完整轉換，p95 為 12 ms，未達 8 ms 目標；重複 copy |
| carmack-redundant-json-roundtrips | effective | carmack | finding | finding | True | True | False | True | 匯入熱路徑同一 payload 完整複製三次，佔 68% CPU，p95 仍為 12 ms，未達 8 毫 |
| carmack-redundant-json-roundtrips | effective | carmack | finding | finding | True | True | False | True | 匯入路徑同一payload完整複製三次，占68%CPU；下游只需dict，p95 12ms，未達8ms目 |
| carmack-redundant-json-roundtrips | primary | fowler | finding | finding | True | False | False | False | 匯入 hot path 為配合 helper 介面連做三次完整轉換，已佔 68% CPU，p95 仍為 |
| carmack-redundant-json-roundtrips | primary | fowler | finding | finding | True | True | True | True | 匯入路徑對同一資料完整複製三次，但下游只需最終字典；p95 仍為 12 ms，未達 8 ms 目標。 |
| design-clean-single-source | baseline | general | no_finding | no_finding | True | True | None | True |  |
| design-clean-single-source | baseline | general | no_finding | no_finding | True | True | None | True |  |
| design-clean-single-source | effective | jeff | no_finding | no_finding | True | True | None | True |  |
| design-clean-single-source | effective | jeff | no_finding | no_finding | True | True | None | True |  |
| design-dual-status-writers | baseline | general | finding | finding | True | True | True | True | 兩個狀態欄位都可寫且每分鐘才雙向同步，衝突時無單一真相來源，畫面最長會有 60 秒狀態不一致。 |
| design-dual-status-writers | baseline | general | finding | finding | True | True | False | True | accounts.status 與 status_copy 可各自寫入且每分鐘才雙向同步，衝突時沒有唯一 |
| design-dual-status-writers | effective | jeff | finding | finding | True | True | False | True | accounts.status 與 status_copy 都可寫且每分鐘才同步，會短暫分歧，違反所有畫 |
| design-dual-status-writers | effective | jeff | finding | finding | True | True | False | True | accounts.status 與 status_copy 都可寫且每分鐘才同步，衝突時沒有單一真相來源 |
| evolve-duplicated-discount-rule | baseline | general | finding | no_finding | True | None | None | False |  |
| evolve-duplicated-discount-rule | baseline | general | finding | no_finding | True | None | None | False |  |
| evolve-duplicated-discount-rule | effective | fowler | finding | finding | True | True | True | True | checkout.py 等三模組仍各自保存折扣門檻；同一規則需三處同步，後續調整容易不一致。 |
| evolve-duplicated-discount-rule | effective | fowler | finding | finding | True | True | False | True | 會員折扣門檻仍散落於 checkout、invoice、refund，調整須三處同步，易漏改造成結果不一 |
| general-no-network-violation | baseline | general | finding | finding | True | True | False | True | telemetry.py 結束時把事件 POST 到外部分析站，直接違反統計資料只能留在本機且不得連網的 |
| general-no-network-violation | baseline | general | finding | finding | True | True | False | True | telemetry.py 結束時把本機事件 POST 到外部分析站，直接違反不得連網或傳出裝置的離線邊界 |
| general-no-network-violation | effective | jeff | finding | finding | True | True | False | True | telemetry.py 結束時會將本機事件 POST 到分析網站，直接違反統計資料不得連網或傳出裝置的 |
| general-no-network-violation | effective | jeff | finding | finding | True | True | True | True | telemetry.py 結束時仍將事件 POST 至外部分析站，直接違反資料僅存本機且不得連網的需求。 |
| general-test-claim-conflict | baseline | general | finding | finding | True | True | False | True | pytest 仍有 CSV 換行引號與 UTF-8 BOM 兩項失敗，卻宣告全部通過可交付，會掩蓋未修復 |
| general-test-claim-conflict | baseline | general | finding | finding | True | False | False | False | pytest 仍有 CSV 換行引號與 UTF-8 BOM 兩項失敗，exit code 1；「完整測試 |
| general-test-claim-conflict | effective | linus | finding | finding | True | True | False | True | 完整測試仍有兩項 CSV 測試失敗且 exit code 1，最終宣告「全部通過、可以交付」與工具證據矛 |
| general-test-claim-conflict | effective | linus | finding | finding | True | True | False | True | 完整測試仍有兩項 CSV 測試失敗且 exit code 為 1，與「全部通過、可以交付」的宣告直接矛盾 |
| lamport-clean-idempotent-retry | baseline | general | no_finding | no_finding | True | True | None | True |  |
| lamport-clean-idempotent-retry | baseline | general | no_finding | no_finding | True | True | None | True |  |
| lamport-clean-idempotent-retry | effective | lamport | no_finding | no_finding | True | True | None | True |  |
| lamport-clean-idempotent-retry | effective | lamport | no_finding | no_finding | True | True | None | True |  |
| lamport-clean-idempotent-retry | primary | linus | no_finding | no_finding | True | True | None | True |  |
| lamport-clean-idempotent-retry | primary | linus | no_finding | no_finding | True | True | None | True |  |
| lamport-stale-search-overwrite | baseline | general | finding | finding | True | False | True | False | 搜尋回應無條件更新 results，較早送出的 A 若較晚完成，會覆蓋 B，畫面顯示的不是最後一次查詢。 |
| lamport-stale-search-overwrite | baseline | general | finding | finding | True | True | True | True | 結果更新未檢查 request_id，較早的 A 晚完成會覆蓋 B，畫面將顯示舊查詢而非最後一次輸入。 |
| lamport-stale-search-overwrite | effective | lamport | finding | finding | True | True | True | True | 搜尋結果更新未檢查 request_id；B 先完成後，A 的舊回應會覆寫 B，畫面不再對應最後輸入。 |
| lamport-stale-search-overwrite | effective | lamport | finding | finding | True | True | False | True | 搜尋結果更新未檢查 request_id；B 先完成後，較舊的 A 仍會覆寫畫面，導致顯示的不是最後一次 |
| lamport-stale-search-overwrite | primary | beck | finding | finding | True | True | False | True | 搜尋結果更新未比對 request_id；較早送出的 A 若晚完成，會覆蓋 B，畫面不再對應使用者最後輸 |
| lamport-stale-search-overwrite | primary | beck | finding | finding | True | False | True | False | 搜尋結果更新未檢查請求識別碼，較早的 A 晚完成會覆蓋 B，畫面不再對應最後查詢。 |
| review-forward-only-layers | baseline | general | finding | finding | True | False | True | False | Provider、Adapter、Bridge 只轉傳同一字串，單一標頭卻增加三層抽象，徒增維護成本。 |
| review-forward-only-layers | baseline | general | finding | finding | True | False | False | False | 固定加一個標頭卻新增三個純轉交類別，VersionHeaderProvider、Adapter、橋接層擴 |
| review-forward-only-layers | effective | linus | finding | finding | True | False | False | False | 三個新類別都只轉交同一字串，卻為 X-App-Version 疊出三層無獨立行為的間接控制，徒增返工風險 |
| review-forward-only-layers | effective | linus | finding | finding | True | False | False | False | VersionHeaderAdapter 與 RequestHeaderBridge 都只轉交同一字串， |

## Scoring boundary

`issue_match` is a deterministic concept-group check. A miss can therefore be either a true miss or a defensible wording that needs blind human adjudication. `Sentence ended` only checks final punctuation and is a review queue, not proof that wording is complete or incomplete. Raw JSONL is retained for both reviews. Correct silence is objective for these seeded clean cases.
