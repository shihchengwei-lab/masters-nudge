# Decision-delta v6：7-packet Reviewer-only replay

## 目的

檢查最小 prompt 修正後，Nudge 是否真的改變主模型下一個決定，而不是認同、稱讚或重述當前 patch。路由時序、persona context、provider 與機械輸出層均未修改。

Provider 固定為 Anthropic `claude-opus-5`，逾時 90 秒。輸入沿用先前 7 個實際 first-change packet；沒有執行主模型、題目 patch 或 SWE-bench 測試。

## 執行結果

- 7/7 `finding`，0/7 `no_finding`，0 error。
- 3/7 完全符合輸出契約；4/7 超過 52 字。
- 中位延遲 23,144 ms；最長 42,901 ms。
- finding 中位長度 53 字；最長 72 字。

## 非盲語義判讀

「改變下一個決定」的判準：finding 會要求換方向、刪除非必要部分，或重新放置責任。只同意或換句話說算重述。

| Packet | 判讀 | 根據 |
|---|---|---|
| t01 | 有實質差異、根據強 | 要求移除 `PermutationGroup` 型別分支，改成同一映射責任。 |
| t02 | 有實質差異、但與題意衝突 | 要求不要合併 `partial` 參數；題目明確要求參數可由 `ResolverMatch.__repr__()` 看見並建議在 `__init__()` 解包。 |
| t03 | 有實質差異、根據強 | 要求測試只驗證 `eval` 往返，不固定 set 的任一字串順序。 |
| t04 | 有實質差異、根據強 | 要求執行延後 `tearDown` 的位置同時清狀態並還原，補上目前 patch 未處理的生命週期責任。 |
| t05 | 有實質差異、根據弱 | 要求 `Mul/Pow` 也處理 `None`，但 packet 沒提供那些分支的實作證據。 |
| t07 | 有實質差異、根據強 | 挑戰目前保留 `-0.00` 的選擇，主張小於顯示門檻時統一成可見的零。 |
| t10 | 有實質差異、根據弱 | 要求責任回到 `import_object`；但「會改動所有成員取值語意」把 `PropertyDocumenter.get_attr()` 的實際作用域說得過廣。 |

合計：7/7 會改變下一個決定、0/7 純重述；其中 4 題根據強、2 題根據弱、1 題與題目證據衝突。

## 結論與限制

這次修正有擋住「只是認同或重述」的出口，但沒有讓 provider 更願意沉默；7 題全部仍輸出 finding。問題從「沒有第二方向」轉成「第二方向是否有足夠證據」：t02 明顯為了另一方向犧牲題意，t05 與 t10 的理由則超出 packet 能支持的範圍。

這 7 題原本就是從會產生 finding 的 packet 挑出，不能用來估計 `no_finding` 準確率。若要驗證沉默規則，下一組必須加入已經採取明顯正確、無需改變決定的負例 packet。
