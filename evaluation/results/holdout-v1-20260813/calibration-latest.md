# Phase A reaction-quality evaluation

- Generated: 2026-08-13T00:52:54.397719+00:00
- Provider/model: `openai` / `gpt-5.6-sol`
- Fixtures: `evaluation\holdout-fixtures-v1.json`
- Repeats: 2
- Randomization seed: 20260815
- Git commit: `06a110e2e668a3dcf8045646e7fb5a33b4355533`
- Fixtures SHA-256: `2d4e0b8a2afa34f829bd6df2138b9f3b60acc525b3405b2ea1eedddbd2d923c7`
- Runner SHA-256: `dfa78671791658ac1d0d794b4bb63697e95986c297ce5c56f20b2c41d092eba8`
- Base prompt SHA-256: `f76a64c860bd9a1c8c52542cc7957fcfddcada3a8787535bca4ffafe767897ba`
- Reviewer CLI: `codex-cli 0.147.0`
- Interpretation: calibration only; not a formal product-impact claim.

## Condition summary

| Condition | Calls | Provider success | Raw schema | Status | Issue match | Correct silence | Avg chars | At 52 | Sentence ended | Oracle match | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 32 | 32/32 (100.0%) | 32/32 (100.0%) | 31/32 (96.9%) | 13/20 (65.0%) | 12/12 (100.0%) | 48.4 | 7/19 (36.8%) | 13/19 (68.4%) | 25/32 (78.1%) | 7423 ms |
| effective | 32 | 32/32 (100.0%) | 32/32 (100.0%) | 31/32 (96.9%) | 13/20 (65.0%) | 11/12 (91.7%) | 50.4 | 15/21 (71.4%) | 10/21 (47.6%) | 24/32 (75.0%) | 7662 ms |
| primary | 8 | 8/8 (100.0%) | 8/8 (100.0%) | 8/8 (100.0%) | 2/4 (50.0%) | 4/4 (100.0%) | 46.5 | 0/4 (0.0%) | 2/4 (50.0%) | 6/8 (75.0%) | 7740 ms |

## Paired outcomes

- `effective_vs_baseline`: 2 wins, 27 ties, 3 losses
- `effective_vs_primary`: 0 wins, 8 ties, 0 losses

## Per-call results

| Fixture | Condition | Lens | Expected | Actual | Chars | Schema | Match | Ended | Correct | Finding |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| holdout-build-clean-csv-behavior | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-build-clean-csv-behavior | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-build-clean-csv-behavior | effective | beck | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-build-clean-csv-behavior | effective | beck | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-build-csv-private-test | baseline | general | finding | finding | 52 | True | False | False | False | 測試只驗證逗號判斷，未涵蓋換行、雙引號跳脫與 export_row，無法證明 Excel 開啟後仍是一列 |
| holdout-build-csv-private-test | baseline | general | finding | finding | 52 | True | True | False | True | 測試只驗證含逗號的私有判斷，未覆蓋換行、雙引號跳脫與 export_row，無法證明 Excel 開啟後 |
| holdout-build-csv-private-test | effective | beck | finding | finding | 52 | True | False | False | False | 新增測試只驗證 `_needs_quotes` 的逗號分支，未涵蓋需求中的換行、雙引號跳脫與 `出口列` |
| holdout-build-csv-private-test | effective | beck | finding | finding | 51 | True | False | True | False | 測試只驗證 `_needs_quotes` 的逗號判斷，未涵蓋需求中的換行、雙引號跳脫與匯出仍為一列。 |
| holdout-carmack-clean-single-decode | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-carmack-clean-single-decode | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-carmack-clean-single-decode | effective | carmack | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-carmack-clean-single-decode | effective | carmack | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-carmack-clean-single-decode | primary | jeff | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-carmack-clean-single-decode | primary | jeff | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-carmack-double-image-decode | baseline | general | finding | finding | 39 | True | False | True | False | benchmark p95 仍為 18.6 ms，未達 12 ms 交付目標。 |
| holdout-carmack-double-image-decode | baseline | general | finding | finding | 47 | True | True | True | True | 目前 p95 仍為 18.6 ms，未達 12 ms 交付門檻；重複 decode 尚未消除。 |
| holdout-carmack-double-image-decode | effective | carmack | finding | finding | 52 | True | False | False | False | make_thumbnail 與 compute_histogram 重複解碼同一 bytes，耗時 站 |
| holdout-carmack-double-image-decode | effective | carmack | finding | finding | 52 | True | False | False | False | make_thumbnail 與 compute_histogram 重複解碼同一份 bytes，合計耗 |
| holdout-carmack-double-image-decode | primary | fowler | finding | finding | 50 | True | False | False | False | make_thumbnail 與 compute_histogram 重複解碼同一 bytes，耗時 |
| holdout-carmack-double-image-decode | primary | fowler | finding | finding | 50 | True | False | False | False | make_thumbnail 與 compute_histogram 重複解碼同一 bytes，耗時 |
| holdout-design-clean-plan-revocation | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-design-clean-plan-revocation | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-design-clean-plan-revocation | effective | jeff | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-design-clean-plan-revocation | effective | jeff | no_finding | finding | 52 | True | False | False | False | 每次授權已讀目前方案，卻又讓舊 session 整體失效；降級可能連基礎功能也被登出，超出只撤高階權限的 |
| holdout-design-stale-plan-token | baseline | general | finding | finding | 49 | True | True | True | True | denylist 每 15 分鐘才更新，降級帳號最久仍可使用高階功能 15 分鐘，不符合立即失權。 |
| holdout-design-stale-plan-token | baseline | general | finding | finding | 50 | True | True | True | True | denylist 每 15 分鐘才匯入，降級後仍可使用高階功能最多 15 分鐘，不符合立即撤權需求。 |
| holdout-design-stale-plan-token | effective | jeff | finding | finding | 51 | True | True | True | True | denylist 每 15 分鐘才匯入降級帳號，降級後仍可能保有高階權限 15 分鐘，不符合立即失權。 |
| holdout-design-stale-plan-token | effective | jeff | finding | finding | 52 | True | True | True | True | denylist 每 15 分鐘才匯入降級帳號，使用者仍可保留高階權限最多 15 分鐘，不符合立即失權。 |
| holdout-evolve-clean-central-vat-rule | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-evolve-clean-central-vat-rule | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-evolve-clean-central-vat-rule | effective | fowler | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-evolve-clean-central-vat-rule | effective | fowler | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-evolve-vat-rule-duplication | baseline | general | finding | no_finding | 0 | True | None | None | False |  |
| holdout-evolve-vat-rule-duplication | baseline | general | finding | finding | 40 | True | True | True | True | 三個檔案各自保存免稅國別集合，後續調整容易漏改，造成報價、發票與匯出結果不一致。 |
| holdout-evolve-vat-rule-duplication | effective | fowler | finding | finding | 35 | True | True | True | True | 免稅國別規則仍散落三個檔案，下次異動須同步修改，容易漏改而產生不一致。 |
| holdout-evolve-vat-rule-duplication | effective | fowler | finding | finding | 39 | True | True | True | True | 免稅國別規則仍散落三個檔案；下次異動須同步修改，容易漏改造成計價與匯出不一致。 |
| holdout-general-authorization-log | baseline | general | finding | finding | 52 | True | False | False | False | debug_request.py 直接記錄所有 headers，已把 Authorization 的正式 |
| holdout-general-authorization-log | baseline | general | finding | finding | 51 | True | False | False | False | debug_request.py 直接記錄全部 headers，Authorization token |
| holdout-general-authorization-log | effective | jeff | finding | finding | 51 | True | True | False | True | debug_request.py 直接記錄完整 headers，測試已洩漏 Authorization |
| holdout-general-authorization-log | effective | jeff | finding | finding | 52 | True | False | False | False | debug_request.py 直接記錄所有 headers，已把 Authorization 的實際 |
| holdout-general-cleanup-scope | baseline | general | finding | finding | 48 | True | True | True | True | cleanup.py 從根目錄搜尋，會誤刪 generated/ 外的 .tmp，違反清理範圍。 |
| holdout-general-cleanup-scope | baseline | general | finding | finding | 48 | True | True | True | True | cleanup.py 從根目錄搜尋，會誤刪 generated/ 外的 .tmp，違反刪除範圍。 |
| holdout-general-cleanup-scope | effective | beck | finding | finding | 52 | True | True | False | True | cleanup.py 從專案根目錄搜尋，會誤刪 generated/ 外的 tests/fixtures |
| holdout-general-cleanup-scope | effective | beck | finding | finding | 52 | True | True | False | True | cleanup.py 從 repository root 掃描，會誤刪 generated/ 外的 .／ |
| holdout-general-migration-dry-run | baseline | general | finding | finding | 46 | True | False | True | False | down dry run 在 DROP 語法失敗，up 也未執行，尚未符合可回滾的交付條件。 |
| holdout-general-migration-dry-run | baseline | general | finding | finding | 46 | True | False | True | False | down dry run 在 DROP 語法失敗，up 也未執行，尚未符合可回滾的交付條件。 |
| holdout-general-migration-dry-run | effective | linus | finding | finding | 52 | True | False | False | False | down dry run 在 DROP 附近語法錯誤，且 up 未執行；「可安全回滾、準備交付」缺乏證據 |
| holdout-general-migration-dry-run | effective | linus | finding | finding | 52 | True | False | True | False | down dry run 在 DROP 語法錯誤並以 1 結束，up 也未執行，尚未符合可回滾交付條件。 |
| holdout-general-missing-platform-artifacts | baseline | general | finding | finding | 52 | True | True | True | True | dist 只有 Linux 壓縮檔，缺少 macOS 與 Windows 執行檔，三平台交付宣告不成立。 |
| holdout-general-missing-platform-artifacts | baseline | general | finding | finding | 52 | True | True | True | True | dist 只有 Linux 壓縮檔，缺少 macOS 與 Windows 執行檔，三平台交付宣告不成立。 |
| holdout-general-missing-platform-artifacts | effective | linus | finding | finding | 51 | True | True | True | True | dist 只有 Linux 壓縮檔，缺少 macOS 與 Windows 執行檔，無法完成三平台交付。 |
| holdout-general-missing-platform-artifacts | effective | linus | finding | finding | 52 | True | True | True | True | dist 只有 Linux 壓縮檔，缺少 macOS 與 Windows 執行檔，三平台交付宣告不成立。 |
| holdout-lamport-clean-email-outbox | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-lamport-clean-email-outbox | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-lamport-clean-email-outbox | effective | lamport | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-lamport-clean-email-outbox | effective | lamport | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-lamport-clean-email-outbox | primary | linus | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-lamport-clean-email-outbox | primary | linus | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-lamport-email-before-commit | baseline | general | finding | finding | 44 | True | True | True | True | send_email 成功後、marker 寫入前當機會重寄，同一訂單可能收到兩封收據。 |
| holdout-lamport-email-before-commit | baseline | general | finding | finding | 48 | True | True | True | True | send_email 成功後、marker 寫入前若當機，重試會再次寄信，違反同一訂單最多一封。 |
| holdout-lamport-email-before-commit | effective | lamport | finding | finding | 52 | True | True | True | True | worker 在寄信成功、寫 marker 前當機，retry 會重寄同一訂單，違反最多一封的不變條件。 |
| holdout-lamport-email-before-commit | effective | lamport | finding | finding | 52 | True | True | True | True | worker 在寄信成功、寫 marker 前當機，retry 會重寄同一訂單，違反最多一封的不變條件。 |
| holdout-lamport-email-before-commit | primary | beck | finding | finding | 43 | True | True | True | True | worker 在寄信成功、寫入 marker 前崩潰會重寄，同一訂單可能收到兩封收據。 |
| holdout-lamport-email-before-commit | primary | beck | finding | finding | 43 | True | True | True | True | worker 在寄信成功、寫入 marker 前當機會重寄，同一訂單可能收到兩封收據。 |
| holdout-review-clean-removed-flag | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-review-clean-removed-flag | baseline | general | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-review-clean-removed-flag | effective | linus | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-review-clean-removed-flag | effective | linus | no_finding | no_finding | 0 | True | True | None | True |  |
| holdout-review-deleted-flag-compatibility | baseline | general | finding | finding | 52 | True | True | False | True | `--legacy-cache` 仍被轉成相容模式並成功執行，違反應回報 unknown option， |
| holdout-review-deleted-flag-compatibility | baseline | general | finding | finding | 52 | True | True | False | True | `--legacy-cache` 仍被轉成相容模式且退出 0，違反移除後須回報 unknown 色選項的 |
| holdout-review-deleted-flag-compatibility | effective | linus | finding | finding | 52 | True | True | False | True | CLI 仍把 `--legacy-cache` 轉成 compat 並成功執行，違反必須回報未知選項的邊 |
| holdout-review-deleted-flag-compatibility | effective | linus | finding | finding | 52 | True | True | False | True | CLI 仍把 `--legacy-cache` 轉成相容模式並成功執行，違反必須回報 unknown、移 |

## Scoring boundary

`issue_match` is a deterministic concept-group check. A miss can therefore be either a true miss or a defensible wording that needs blind human adjudication. `Sentence ended` only checks final punctuation and is a review queue, not proof that wording is complete or incomplete. Raw JSONL is retained for both reviews. Correct silence is objective for these seeded clean cases.
