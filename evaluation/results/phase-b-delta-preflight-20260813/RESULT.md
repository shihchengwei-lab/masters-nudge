# Phase B candidate delta preflight — result

The preflight is a **formal miss on the soft-target adherence diagnostic**, not a truncation or semantic-quality failure.

| Check | Required | Result |
|---|---:|---:|
| Schema-valid effective findings | 7/7 | 7/7 |
| Grounded, workflow-level, relevant, aligned, complete | 7/7 | 7/7 |
| Effective outputs at the 52-character hard cap | 0 | 0 |
| Effective outputs within the 42-character soft target | ≥6/7 | 5/7 |

The two soft-target misses were complete sentences of 43 and 44 characters. No output was truncated. Because 42 characters is intentionally a soft target, the prompt is frozen without tuning against these same cases and proceeds to the Phase B impact pilot with this miss disclosed.

Raw result SHA-256:

```text
0d4d40846c777af093e96cd8e941ad22a5a3ddd42e261f748295b61b529e4296
```

Effective outputs:

| Lens | Chars | Nudge |
|---|---:|---|
| Beck | 27 | 同一斷言未變卻連換四層，還缺一個能排除假設的最小實驗。 |
| Carmack | 44 | 尚未量 baseline 或驗證輸出，就調 thread pool，量到的會是哪個瓶頸？ |
| Carmack | 39 | 量到的是載入後迴圈，卻用來宣告 cold start 完成；首次輸出也未驗證。 |
| Fowler | 26 | 同一折扣知識要同步改五處，下次調整仍得重走五個邊界。 |
| Jeff | 39 | 主要流失點與成功指標未定，就先鎖定提醒服務，後續基礎設施可能只是在替假設還債。 |
| Lamport | 43 | 調高 debounce 只改機率，仍未驗證 A 晚於 B 抵達時「最後查詢」不變條件。 |
| Linus | 40 | 完成宣告跑在必要驗證前面，Windows 與 Linux 的乾淨安裝都還沒執行。 |
