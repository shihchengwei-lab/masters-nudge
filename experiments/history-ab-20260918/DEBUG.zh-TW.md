# 第六題除錯紀錄

- 題目：`read-only-repo-tools`
- 發生位置：第二次 B 臂
- 工具訊息：`input_size: 材料超過上限，無法保留必要原文`
- 結果：該次執行無效；整道題目不納入五題工具效果比較。
- 證據：`E:\mn-history-ab-20260918\runs\read-only-repo-tools\repeat-2\B\result.json`
- 待查：哪一份必要原文使材料包超過上限，以及現有材料取捨為何無法產生合法封包。

## 根源與修復

根源是資料包為每行重複保存 `line` 與 `text` 欄位，使 11,712 字、295 行的合法修改膨脹成 21,696 字。工具是否故障因而取決於 Actor 如何分批修改。

修正後每段只保存路徑、起始行號及連續文字陣列；後續行號由陣列位置推導。容量上限仍為 20,000 字，修改原文沒有截斷。

Smoke：`read-only-repo-tools` 第三次 B 臂完成，契約通過，4 次 Provider 判斷為 2 次反饋、2 次沉默，最大資料包 13,812 字，沒有工具故障。證據：`E:\mn-history-ab-20260918\runs\read-only-repo-tools\repeat-3\B\result.json`。
