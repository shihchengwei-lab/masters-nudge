# Astra max 雙模型：Regexp 兩次挑戰結果

日期：2026-10-04。Actor、Provider 都是 GPT-6 Astra max；兩次從同一基底獨立開始，Actor 不限時。

**完整交付：0/2。** 原七臂此題為0/14；本輪同時改模型、深度與解題時限，不將差異單獨歸因於工具或模型，亦不併入七臂排名。

| 次數 | 完整交付 | 功能／執行契約 | Actor 分鐘（含 Provider 等待） | 提醒／送達／故障 |
|---|---|---|---:|---|
| J1 | False | fail／pass | 30.57 | 1／1／0 |
| J2 | False | fail／pass | 17.74 | 2／2／0 |

## 固定驗收、提醒與程式結構

### J1

固定檢查：{"reserved": "pass", "regexp_contract.js": "pass", "regexp_direction.js": "fail", "regexp_judge_concerns.js": "fail"}。

執行契約：遵守執行限制：只修改實作、文件及新增獨立測試，既有測試未改。沒有提交、安裝、查閱 Git 歷史、網路、委派或子代理；已執行指定測試、相關檢查與最終 diff，並如實回報測試失敗與環境缺依賴。本輪不限時，時間不構成違約。功能正確性另由固定驗收判定。

程式品質：局部結構方向合理，整體交付仍不合格；不判為高品味成品。

保留原量詞上下限，再以「未經過／已經過目標元素」兩種狀態追蹤路徑。這個新增狀態確實消除原先虛構重複次數的補救，複雜度有對應責任，不只是把補丁換個抽象名稱。但新判斷仍需分別接入結果排序、去重、選項與回報，這些接縫沒有完整承接原有語意。

- 主要功能通過：固定 reserved 與 regexp_contract.js 都通過，能定位巢狀元素、字元類別與範圍端點。這不等於完整交付。
- 原有效能責任漏接：/(?:a+|[ab])+$/ 的 reportExponentialBacktracking=certain 不再輸出原有的回溯風險警告。新增 NestedSubset 排在 Overlap 前；去重只允許 PrefixSubset 類別保留第二個效能診斷，NestedSubset 因而壓掉它。
- 結果種類混同：/ab|(?:ab|a)/ 中被覆蓋的 ab 與前面的 ab 相等，findNestedDuplication 只查 isSubsetOf 就一律標成 strict subset；相等與嚴格子集沒有留在結果結構裡。
- Actor 原 focused suite 有 67 通過、1 失敗；兩次均保留並說明 /((?:ab|ba)|(?:ba|ac))/ 的舊 valid 案例與新增巢狀回報衝突。固定驗收使用預先封存的套件，77/77 通過，兩種數字不可混用。即使不把該舊案例算失敗，獨立的效能警告與語意檢查仍不通過。
- 向後查找只修 NFA，未修較早的 AST 路徑：/(?<=a|a[ab])/ 仍誤報整段 a[ab] 可刪，而不是其中的 a。兩個分析入口對匹配方向不同步。
- 引用安全由 Actor 自行補上：iterateNestedElements 跳過 references.length>0 的捕獲群組，因此固定反向引用探針沒有誤報；這是保守限制，沒有把捕獲與引用關係納入同一分析表示。

提醒採納：實際採納，非只檢查。提醒指出量詞上下限被改成虛構次數，建議 NFA × 是否經過元素。Actor 後續改成 marker 與雙狀態投影，保留原量詞，並新增相應案例；方向被實作，但沒有帶出其他契約缺口。

來源：[Actor 說明](runs/regexp-404/J1/actor-final.txt)、[原始修改](runs/regexp-404/J1/final.patch)、[提醒](runs/regexp-404/J1/provider-attempts.json)、[執行覆核](runs/regexp-404/J1/execution-review.json)。

### J2

固定檢查：{"reserved": "pass", "regexp_contract.js": "pass", "regexp_direction.js": "fail", "regexp_judge_concerns.js": "fail"}。

執行契約：遵守執行限制：只修改實作、文件及新增獨立測試，既有測試未改。沒有提交、安裝、查閱 Git 歷史、網路、委派或子代理；已執行指定測試、相關檢查與最終 diff，並如實回報測試失敗與環境缺依賴。本輪不限時，時間不構成違約。功能正確性另由固定驗收判定。

程式品質：局部結構有實際改善，整體仍有錯誤刪除建議；不判為高品味成品。

同樣改成保留量詞、追蹤是否經過元素的狀態，並修正 AST 的向後查找與互相依賴的刪除建議。這些都有具體用途。但新增分析把捕獲值與後續引用的依賴丟掉，再以可接受字串集合判定刪除安全；完整使用流程的必要資訊仍不在結構中。

- 主要功能通過：固定 reserved 與 regexp_contract.js 都通過，能定位巢狀元素、字元類別與範圍端點。這不等於完整交付。
- 原有效能責任漏接：/(?:a+|[ab])+$/ 的 reportExponentialBacktracking=certain 不再輸出原有的回溯風險警告。新增 NestedSubset 排在 Overlap 前；去重只允許 PrefixSubset 類別保留第二個效能診斷，NestedSubset 因而壓掉它。
- 結果種類混同：/ab|(?:ab|a)/ 中被覆蓋的 ab 與前面的 ab 相等，findNestedDuplication 只查 isSubsetOf 就一律標成 strict subset；相等與嚴格子集沒有留在結果結構裡。
- Actor 原 focused suite 有 67 通過、1 失敗；兩次均保留並說明 /((?:ab|ba)|(?:ba|ac))/ 的舊 valid 案例與新增巢狀回報衝突。固定驗收使用預先封存的套件，77/77 通過，兩種數字不可混用。即使不把該舊案例算失敗，獨立的效能警告與語意檢查仍不通過。
- 反向引用造成實際錯誤刪除建議：/(?:a+|([ab]))(?!\1)/ 被建議刪除 a；固定探針顯示修改前可匹配、修改後不可匹配。保留字串集合及量詞不等於保留捕獲結果。
- 向後查找此次通過：AST 的 canOmitRight 只在 ltr 啟用，NFA 依方向延伸；/(?<=a|a[ab])/ 正確定位內部 a。這是局部進步，仍未完成其他責任。

提醒採納：第二次重複提醒後實際採納；第一次未完成結構修正。兩則提醒都指出同一量詞缺口與 hit 狀態方案。第一則後仍保留錯誤次數模型，第二則後 Actor 改成 marker、原量詞與 before/after 狀態。不能將兩則重複提醒算成兩個獨立改善。

來源：[Actor 說明](runs/regexp-404/J2/actor-final.txt)、[原始修改](runs/regexp-404/J2/final.patch)、[提醒](runs/regexp-404/J2/provider-attempts.json)、[執行覆核](runs/regexp-404/J2/execution-review.json)。

## 用量與方法

| 次數 | Actor＋Provider 輸入（含快取） | 快取輸入 | 未快取輸入 | 輸出 |
|---|---:|---:|---:|---:|
| J1 | 3,420,784 | 3,221,888 | 198,896 | 46,917 |
| J2 | 4,481,512 | 4,244,608 | 236,904 | 49,549 |

以下為各次原始 Token 用量；缺值保留 null，Provider 呼叫不存在時才是0。Actor 的輸入包含 Provider 送達後續上下文；Provider 模型本身另記，不能只看 Actor 費用。reasoning output 是 output 的子集，不重複加總。

```json
[
  {
    "arm": "J1",
    "actor_usage": {
      "input_tokens": 3146862,
      "cached_input_tokens": 3017728,
      "output_tokens": 38139
    },
    "provider_usage": {
      "input_tokens": 273922,
      "cached_input_tokens": 204160,
      "output_tokens": 8778
    }
  },
  {
    "arm": "J2",
    "actor_usage": {
      "input_tokens": 4136049,
      "cached_input_tokens": 3998336,
      "output_tokens": 37042
    },
    "provider_usage": {
      "input_tokens": 345463,
      "cached_input_tokens": 246272,
      "output_tokens": 12507
    }
  }
]
```

本輪執行契約與程式碼由 Codex 閱讀原始行動及程式作語意覆核，已知組別；沒有新增匿名品味評審票。原七臂沒有合格的 Regexp 答案，因此不作與失敗交付的品味勝負排名。

條件、harness、傳輸等待與來源見 [MATERIALS](evidence.zip)、[計畫](evidence.zip)；完整數據見 [results-summary.json](results-summary.json)，檔案指紋與原材料保全見 [final-integrity.json](evidence.zip)。

公開副本：本機路徑已匿名化；原始指紋與公開指紋見 [來源索引](source-index.json)。完整事件、執行證據、固定驗收與工具快照位於 [證據包](evidence.zip)。原始 final.patch 未修改。
