# Masters' Nudge 10 題配對 A/B pilot

日期：2026-08-29  
資料集：SWE-bench Verified  
目的：先驗證 A/B 流程與觀察方向，不把 10 題結果宣稱為穩定效應。

## 結論

- A（無 Nudge）通過 8/10；B（有 Nudge）通過 8/10。
- 配對差異為 A-only 0、B-only 0。沒有可提供方向資訊的勝負分歧題；exact McNemar/sign test 的慣例值為 `p = 1.0`，不能據此宣稱兩組等效。
- B 在 9/10 題實際注入 Nudge，共 10 次；10 次都有後續可觀察事件。`t06` 沒有 finding，也沒有注入。
- 10 次 finding 全部使用 `beck` lens，而且 10/10 都把建議落在測試、斷言、驗證或停止點。句型已是直接指令、沒有提問，但內容仍明顯偏 review／驗證，而不是多種大師品味。
- 本 pilot 沒有觀察到成功率提升；也不能以 10 題排除較小的正向或負向效果。

## 鎖定設計

- 主模型：兩組皆為 `gpt-5.6-sol`、`medium`。
- A：隔離的 `CODEX_HOME`，無 hooks。
- B：隔離的 `CODEX_HOME`，載入凍結的 Masters' Nudge hooks；reviewer 為 `gpt-5.6-sol`。
- 固定 seed 選題與決定 A/B 執行順序；兩組使用獨立 checkout。
- 主模型看不到 gold patch 與官方 test patch，且提示禁止查外部解答。
- 評分時只抽取產品程式碼差異，套到乾淨 base commit，再加入官方 test patch，執行官方 patch 修改到的所有測試檔或 Django test label。
- 已完成的模型答案不重跑。只允許修正評分器相依套件，再對同一份程式差異重評。

完整預註冊條件見 [contract.json](./contract.json)，機器可讀結果見 [results.json](./results.json)。

## 逐題結果

| 題目 | 順序 | A | B | A 秒 | B 秒 | 產品 patch 相同 | B 的 Nudge |
|---|---|---:|---:|---:|---:|---:|---|
| `pytest-dev__pytest-7432` | B→A | pass | pass | 70 | 95 | 是 | 先為布林 skipif 補上 reason，再重跑定位回歸測試。 |
| `sympy__sympy-21379` | A→B | pass | pass | 105 | 135 | 否 | 優先把回歸測試改為清快取後直接斷言原始 subs 首次呼叫成功。 |
| `django__django-14434` | A→B | pass | pass | 95 | 110 | 是 | 先用正確測試標籤跑通新增回歸案例，再視為完成驗證。 |
| `django__django-12209` | A→B | pass | pass | 105 | 255 | 否 | ① 先用正確測試標籤驗證顯式主鍵的普通 save 只更新既有資料。 ② 停止前優先驗證重複載入顯式主鍵 fixture 的可觀察行為。 |
| `sphinx-doc__sphinx-8265` | B→A | pass | pass | 125 | 190 | 否 | 先消除既有簽名註解測試回歸，再以目標方法簽名測試通過為停止點。 |
| `django__django-13821` | B→A | pass | pass | 95 | 100 | 是 | 無 finding／無注入。 |
| `sympy__sympy-24539` | A→B | pass | pass | 50 | 65 | 是 | 停止前執行完整的 test_rings.py，確認既有無參數行為未回歸。 |
| `pytest-dev__pytest-10051` | A→B | pass | pass | 60 | 65 | 是 | 聚焦測試已覆蓋清除前後的可觀察一致性，現在應停止擴張。 |
| `django__django-13513` | A→B | fail | fail | 590 | 150 | 否 | 優先斷言除錯輸出不含被抑制的 RuntimeError，而非只檢查串接提示。 |
| `sphinx-doc__sphinx-8056` | A→B | fail | fail | 235 | 345 | 否 | 先以最小 Napoleon 重現案例驗證合併參數輸出，通過即停止擴張。 |

失敗型態：

- `django__django-13513`：A 只留下測試變更，因此抽取後的產品 patch 為空；B 有修改 `django/views/debug.py`，但官方回歸測試仍得到 0 個 frame，兩組都失敗。
- `sphinx-doc__sphinx-8056`：A、B 都修改 `sphinx/util/docfields.py`，但官方兩個目標案例仍失敗（`2 failed, 40 passed`）。

## Nudge 與主模型後續事件

10 次注入後的第一個可觀察語意事件為：

- 4 次程式變更事件。
- 4 次成功驗證事件。
- 2 次失敗驗證事件，分別是 `t09`、`t10`。

這只證明 Nudge 已注入，且之後觀察到上述事件；不能證明事件是 Nudge 造成，也不能證明主模型完全採納建議。

## 成本與行為差異

| 指標 | A | B | 差異 |
|---|---:|---:|---:|
| 總執行時間 | 1,530 秒 | 1,510 秒 | B -20 秒（受 `t09-A` 590 秒離群值影響） |
| 每題中位時間 | 約 100 秒 | 約 123 秒 | B 約 +23 秒 |
| 主模型 input tokens | 3,502,059 | 4,124,810 | B +17.8% |
| 主模型 output tokens | 31,253 | 43,323 | B +38.6% |

B 另有 10 次 reviewer 呼叫：167,019 input tokens、1,597 output tokens、1,140 reasoning tokens，合計 API latency 約 89 秒。reviewer latency 已包含在 B 的執行時間內。

5/10 題的 A/B 產品 patch 完全相同；其餘 5 題 patch 不同，但沒有改變本次 pass/fail 配對結果。

## 評分環境修正

第一次評 `t10` 時，舊版 Sphinx 被目前最新版 `sphinxcontrib-*` 與 `alabaster` 破壞，出現與題目無關的 setup error。依預註冊規則，只固定歷史相容相依版本，並以原本 A/B patch 重評；模型沒有重跑。乾淨重評後兩組仍各有 2 個目標測試失敗。先前兩次評分器輸出已保留在工作目錄的 `evaluator-infra-unpinned*` 與 `score-infra-unpinned*.json`。

## 驗證狀態與限制

已執行並通過：

- Masters' Nudge source preflight：309 tests passed、2 skipped。
- plugin runtime 同步檢查。
- 10 題都在 base + 官方 test patch 上重現失敗後才納入。
- 20 個模型 arm 都正常結束，沒有超時或重跑答案。
- 20 個最終評分都完成；A、B 各 8 pass、2 fail。
- 凍結 plugin 與目前測試來源逐檔 SHA-256 比對：61 個檔案，0 個差異。

未驗證：

- 未在 SWE-bench 官方 Docker/Linux harness 重跑；本次是 Windows-native convenience sample。
- 未驗證其他模型、reasoning effort、reviewer 或非 SWE-bench 任務。
- 未驗證長期使用者品質、主觀「品味」評分或不同 persona 的分布。
- 10 題不足以估計小幅效果、置信區間或一般化效力；本結果只支持「這 10 題未出現 pass/fail 差異」。
