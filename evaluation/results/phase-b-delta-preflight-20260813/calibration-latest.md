# Phase A reaction-quality evaluation

- Generated: 2026-08-13T02:10:50.130926+00:00
- Provider/model: `openai` / `gpt-5.6-sol`
- Fixtures: `evaluation\workflow-holdout-v2.json`
- Repeats: 1
- Randomization seed: 20260818
- Git commit: `06a110e2e668a3dcf8045646e7fb5a33b4355533`
- Fixtures SHA-256: `12cf1aefd98c83b813e63b45abc6d1d9a8c1a30bf3c9519d4e41d15e43fc5ef9`
- Runner SHA-256: `dfa78671791658ac1d0d794b4bb63697e95986c297ce5c56f20b2c41d092eba8`
- Base prompt SHA-256: `d79ac82a7608c73b38f4321abf21c756cbdf4b73b071e564d1c4bc5e8b251878`
- Reviewer CLI: `codex-cli 0.147.0`
- Interpretation: calibration only; not a formal product-impact claim.

## Condition summary

| Condition | Calls | Provider success | Raw schema | Status | Issue match | Correct silence | Avg chars | At 52 | Sentence ended | Oracle match | Avg latency |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| baseline | 7 | 7/7 (100.0%) | 7/7 (100.0%) | 7/7 (100.0%) | 1/7 (14.3%) | n/a | 38.0 | 0/7 (0.0%) | 7/7 (100.0%) | 1/7 (14.3%) | 8505 ms |
| effective | 7 | 7/7 (100.0%) | 7/7 (100.0%) | 7/7 (100.0%) | 2/7 (28.6%) | n/a | 36.9 | 0/7 (0.0%) | 7/7 (100.0%) | 2/7 (28.6%) | 7320 ms |
| primary | 3 | 3/3 (100.0%) | 3/3 (100.0%) | 3/3 (100.0%) | 1/3 (33.3%) | n/a | 39.0 | 1/3 (33.3%) | 2/3 (66.7%) | 1/3 (33.3%) | 8989 ms |

## Paired outcomes

- `effective_vs_baseline`: 2 wins, 4 ties, 1 losses
- `effective_vs_primary`: 1 wins, 1 ties, 1 losses

## Per-call results

| Fixture | Condition | Lens | Expected | Actual | Chars | Schema | Match | Ended | Correct | Finding |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|
| workflow-beck-fix-thrashing-without-experiment | baseline | general | finding | finding | 41 | True | False | True | False | 同一 assertion 連續換三層修法仍失敗，下一步是否該先用最小重現排除假設？ |
| workflow-beck-fix-thrashing-without-experiment | effective | beck | finding | finding | 27 | True | False | True | False | 同一斷言未變卻連換四層，還缺一個能排除假設的最小實驗。 |
| workflow-carmack-optimizes-before-measurement | baseline | general | finding | finding | 38 | True | False | True | False | 連瓶頸與輸出等價都還沒量，就續調 thread pool，如何知道方向對了？ |
| workflow-carmack-optimizes-before-measurement | effective | carmack | finding | finding | 44 | True | True | True | True | 尚未量 baseline 或驗證輸出，就調 thread pool，量到的會是哪個瓶頸？ |
| workflow-carmack-optimizes-before-measurement | primary | beck | finding | finding | 52 | True | False | False | False | 三種優化已疊上，卻還沒用 baseline 與等價檢查確認速度和輸出，再調 thread pool 會學 |
| workflow-carmack-warm-benchmark-for-cold-goal | baseline | general | finding | finding | 39 | True | False | True | False | 量到的是暖機後迴圈，卻據此宣告 cold start 與首次輸出都已完成驗證。 |
| workflow-carmack-warm-benchmark-for-cold-goal | effective | carmack | finding | finding | 39 | True | False | True | False | 量到的是載入後迴圈，卻用來宣告 cold start 完成；首次輸出也未驗證。 |
| workflow-carmack-warm-benchmark-for-cold-goal | primary | linus | finding | finding | 28 | True | False | True | False | 完成宣告量到的是暖機後迴圈，冷啟動與首次輸出仍未被驗證。 |
| workflow-fowler-policy-has-no-home | baseline | general | finding | finding | 30 | True | False | True | False | 五處同步改完卻仍各自保存規則，下一次調整仍得靠人工維持一致。 |
| workflow-fowler-policy-has-no-home | effective | fowler | finding | finding | 26 | True | True | True | True | 同一折扣知識要同步改五處，下次調整仍得重走五個邊界。 |
| workflow-jeff-solution-before-problem | baseline | general | finding | finding | 42 | True | False | True | False | 主要流失點與成功指標都未定義，技術方案卻已先鎖定 reminder service。 |
| workflow-jeff-solution-before-problem | effective | jeff | finding | finding | 39 | True | False | True | False | 主要流失點與成功指標未定，就先鎖定提醒服務，後續基礎設施可能只是在替假設還債。 |
| workflow-lamport-delay-patches-ordering | baseline | general | finding | finding | 37 | True | False | True | False | 連續調高 debounce 只壓低機率，仍未驗證或阻止 A、B 亂序覆寫。 |
| workflow-lamport-delay-patches-ordering | effective | lamport | finding | finding | 43 | True | False | True | False | 調高 debounce 只改機率，仍未驗證 A 晚於 B 抵達時「最後查詢」不變條件。 |
| workflow-lamport-delay-patches-ordering | primary | fowler | finding | finding | 37 | True | True | True | True | 每次只調高 debounce，卻沒用 A、B 交錯測試排除真正的亂序假設。 |
| workflow-linus-checklist-before-real-install | baseline | general | finding | finding | 39 | True | True | True | True | 交付宣告跑在必要驗證前面；Windows 與 Linux 的乾淨安裝都未執行。 |
| workflow-linus-checklist-before-real-install | effective | linus | finding | finding | 40 | True | False | True | False | 完成宣告跑在必要驗證前面，Windows 與 Linux 的乾淨安裝都還沒執行。 |

## Scoring boundary

`issue_match` is a deterministic concept-group check. A miss can therefore be either a true miss or a defensible wording that needs blind human adjudication. `Sentence ended` only checks final punctuation and is a review queue, not proof that wording is complete or incomplete. Raw JSONL is retained for both reviews. Correct silence is objective for these seeded clean cases.
