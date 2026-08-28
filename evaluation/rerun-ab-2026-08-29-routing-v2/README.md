# Masters' Nudge routing-v2：10 題配對 A/B 重跑

日期：2026-08-29  
資料集：SWE-bench Verified  
比較：A 無 Nudge；B 使用 first-principles Automatic Lens routing。

## 結論

- A 通過 9/10，B 通過 9/10；A-only 0、B-only 0。沒有勝負分歧題，不能宣稱成功率提升或兩組等效。
- B 有 9 次 reviewer 呼叫：8 次 finding、1 次 `no_finding`。8 次 finding 全部注入，且全部有後續 response observation。
- Lens 分布為 Beck 6、Linus 2；不再像上一輪 10/10 finding 全是 Beck，但仍沒有 Jeff、Fowler、Lamport 或 Carmack。
- 2 則 Linus finding 直接改變資料／介面決策；其餘 6 則仍以測試、驗證或停止點為中心。路由已有方向性改善，但「review 味」仍佔多數。
- `t10` 有產品與測試檔案變更，卻沒有 reviewer telemetry，表示 first-change trigger 尚未涵蓋所有 Codex 檔案變更事件。

## 鎖定設計

- 沿用上一輪完全相同的 10 題、base commit、A/B 順序與官方 test patch。
- 主模型兩組均為 `gpt-5.6-sol`、`medium`；B reviewer 為 `gpt-5.6-sol`。
- 重用鎖定的 base checkout、Python 環境與 eligible preflight；20 個模型 arm、20 個最終 score 都重新執行。
- A、B 使用獨立 checkout 與隔離 `CODEX_HOME`；B 凍結 routing-v2 plugin。
- 評分只抽取產品程式碼 patch，套到乾淨 base 後加入官方 test patch。

完整條件見 [contract.json](./contract.json)，機器結果見 [results.json](./results.json)，逐次 Nudge 與第一個後續語意事件見 [nudge-observations.json](./nudge-observations.json)。

## 逐題結果

| 題目 | A | B | A 秒 | B 秒 | 產品 patch 相同 | B Lens |
|---|---:|---:|---:|---:|---:|---|
| `pytest-dev__pytest-7432` | pass | pass | 80 | 140 | 否 | Beck |
| `sympy__sympy-21379` | pass | pass | 135 | 185 | 否 | Linus |
| `django__django-14434` | pass | pass | 85 | 115 | 是 | Beck |
| `django__django-12209` | pass | pass | 100 | 190 | 否 | Linus |
| `sphinx-doc__sphinx-8265` | pass | pass | 105 | 190 | 否 | Beck |
| `django__django-13821` | pass | pass | 105 | 120 | 是 | Beck |
| `sympy__sympy-24539` | pass | pass | 65 | 75 | 是 | Beck |
| `pytest-dev__pytest-10051` | pass | pass | 50 | 90 | 是 | Beck |
| `django__django-13513` | fail | fail | 90 | 115 | 否 | none (`no_finding`) |
| `sphinx-doc__sphinx-8056` | pass | pass | 195 | 140 | 否 | none（未觸發） |

唯一實質失敗題 `t09` 的 A、B 都在官方 `test_innermost_exception_without_traceback` 得到 0 個 frame，而預期為 1。

## Nudge 與主模型後續事件

| 題目 | Lens | Nudge | 注入後第一個可觀察語意事件 |
|---|---|---|---|
| t01 | Beck | 先實際執行新增案例，確認兩種標記在 --runxfail 下的位置。 | 目標驗證失敗 |
| t02 | Linus | 別把所有 PolynomialError 都當互質；僅在 Piecewise 非多項式路徑略過 gcd。 | 程式變更 |
| t03 | Beck | 回歸測試應傳入 opclasses，確實覆蓋此次修正的分支。 | 程式變更 |
| t04 | Linus | 讓初始化直接記錄 PK 是否顯式提供，別靠預設值相等推斷來源。 | 程式變更 |
| t05 | Beck | 優先補上 autodoc 簽名輸出的回歸測試，確認修正觸及使用者行為。 | 程式變更 |
| t06 | Beck | 先以後端測試驗證 3.8 拒絕與 3.9 接受，再停止擴張。 | 程式變更 |
| t07 | Beck | 先以替代符號的實際輸出測試鎖定行為，再宣告完成。 | 成功驗證 |
| t08 | Beck | 先執行新增的回歸測試再收尾；目前只有補丁套用成功，沒有測試結果。 | 成功驗證 |
| t09 | none | reviewer 回傳 `no_finding` | 無注入 |
| t10 | none | reviewer 未被觸發 | 無注入 |

上述資料只證明注入後發生的第一個語意事件；不能證明 Nudge 造成該事件或被完整採納。

## 成本

| 指標 | A | B | 差異 |
|---|---:|---:|---:|
| 總執行時間 | 1,010 秒 | 1,360 秒 | B +350 秒 |
| 每題中位時間 | 95 秒 | 130 秒 | B +35 秒 |
| 主模型 input tokens | 3,129,899 | 3,372,027 | B +7.7% |
| 主模型 output tokens | 31,117 | 39,033 | B +25.4% |

B 另有 9 次 reviewer 呼叫：171,604 input tokens、2,336 output tokens、1,895 reasoning tokens，合計 API latency 約 92 秒。4/10 題的 A/B 產品 patch 完全相同。

## 評分器修正

`t10` 第一次重評時，兩組皆因 Sphinx 3.2.0 搭配 `docutils 0.23` 產生額外 node-registration warning，污染 warning assertion。依契約只將 evaluator 的 `docutils` 固定為 0.16，使用原模型 patch 重評；A、B 均為 42 passed。原始 score 與 evaluator 分別保留為 `score-infra-docutils-0.23.json` 與 `evaluator-infra-docutils-0.23`。

## 驗證狀態與限制

已執行並通過：20 個模型 arm 正常完成；20 個最終 score 完成；A、B 各 9 pass、1 fail；8 次注入皆有 response observation；plugin runtime 在凍結前同步。

未驗證：未使用 SWE-bench 官方 Docker/Linux harness；未測其他模型、reasoning effort 或非 SWE-bench 任務；10 題不足以估計小幅效果；沒有人工盲評 Nudge 品味；response observation 不能提供因果或完整採納證據。
