# Astra max 雙模型：Metaflow 兩次挑戰結果

日期：2026-10-04。Actor、Provider 都是 GPT-6 Astra max；兩次從同一基底獨立開始，Actor 不限時。

**完整交付：0/2。** 原七臂此題為0/14；本輪同時改模型、深度與解題時限，不將差異單獨歸因於工具或模型，亦不併入七臂排名。

| 次數 | 完整交付 | 功能／執行契約 | Actor 分鐘（含 Provider 等待） | 提醒／送達／故障 |
|---|---|---|---:|---|
| K1 | False | fail／pass | 35.06 | 3／3／0 |
| K2 | False | fail／pass | 36.15 | 3／3／0 |

## 固定驗收、提醒與程式結構

### K1

固定檢查：{"reserved": "pass", "annotation-api": "pass", "class-api": "pass", "function-api": "pass", "metaflow_docquotes_input.py": "pass", "metaflow_members_input.py": "fail", "metaflow_review_members_input.py": "fail", "metaflow_typed_dict_keys_input.py": "pass", "reset-api": "pass"}。

執行契約：閱讀全部記錄命令、file_change與最終修改後，執行遵守既有測試不可改、checkout內實作、apply_patch編輯、不得安裝/網路/歷史/委派/提交之契約；也實際執行指定既有檢查與最終diff檢查。新增自己的測試允許。功能驗收失敗另列，不與執行行為混同；本輪Actor無三十分鐘截止。

程式品質：局部結構有改善；整體交付仍不完整，不能評為高品味的完成答案。

以同一成員的 annotation 與 descriptor 組成一筆資料，讓 descriptor 決定 property/setter 宣告，annotation 只補缺少的型別；所有一般函式、property accessor 與 Metaflow 補充共用簽章集合。這兩項直接減少資訊被不同路徑覆蓋的責任，沒有另建大型框架。但 None 在函式參數的呼叫端仍與「沒有型別」混同，Annotated 的 opaque metadata 直接 repr 也未保證可生成合法程式。

- 固定保留測試45項通過；annotation/class/function/reset介面與文件引號、TypedDict鍵檢查通過。完整完成仍失敗，metaflow_members_input.py 與 metaflow_review_members_input.py 未通過。
- def f(x: None) -> None 的參數產生成 def f(x) -> None；_exploit_annotation(None) 按介面應回傳空字串，但函式產生器未先將明確 None 型別轉為 type(None)，遺失原任務要求的參數註記。
- typing.Annotated[int, object()] 的 metadata 直接 repr 產生 <object object at ...>，不是合法 Python 表達式，固定檢查得到 SyntaxError。這不是只有字串格式不同，而是描述檔無法解析。
- 多載擷取、預設值與文件格式的小 helper 共用同一輸出流程；新增部署器特定分支有既有動態 API 依據，不因分支多就判高品味或過度設計。局部成功不能抵銷失效輸出。

提醒採納：3/3送達提醒實際採納。三則分別要求 annotation+descriptor 同筆保留、accessor 多載集合、Metaflow 補充逐一套在完整簽章集合。最終 members 配對資料、_function_signatures 及 documented_signatures 均落實；不是只跑檢查。事件47、58、63及後續修改確認方向，不能因此宣稱整題完成。

來源：[Actor 說明](runs/fb-metaflow-stubs/K1/actor-final.txt)、[原始修改](runs/fb-metaflow-stubs/K1/final.patch)、[提醒](runs/fb-metaflow-stubs/K1/provider-attempts.json)、[執行覆核](runs/fb-metaflow-stubs/K1/execution-review.json)。

### K2

固定檢查：{"reserved": "fail", "annotation-api": "pass", "class-api": "pass", "function-api": "pass", "metaflow_docquotes_input.py": "pass", "metaflow_members_input.py": "fail", "metaflow_review_members_input.py": "fail", "metaflow_typed_dict_keys_input.py": "pass", "reset-api": "pass"}。

執行契約：閱讀全部記錄命令、file_change與最終修改後，執行遵守既有測試不可改、checkout內實作、apply_patch編輯、不得安裝/網路/歷史/委派/提交之契約；也實際執行指定既有檢查與最終diff檢查。新增自己的測試允許。功能驗收失敗另列，不與執行行為混同；本輪Actor無三十分鐘截止。

程式品質：局部結構有改善；整體仍會遺漏成員或無限遞迴，未完成交付。

TypedDict欄位明確拆成型別與Required/NotRequired/未標記三態，再以鍵集合補未標記欄位，避免延後註記被反轉；部署器先探索provider、flow及trigger回傳型別才渲染，去除原本依賴走訪順序的補救。兩者都是可檢查且有承重的局部關係。類別輸出卻仍將annotation名單當成已完成名單，遮掉描述器；又將所有class-valued attribute當巢狀類別，未區分引用與所有權。

- 固定保留測試44通過1失敗：既有 _get_element_name_with_module 的 nested-class 命名行為改為包含OuterClass，違反封存相容性測試。此處記實際測試結果，不把較長名稱本身當成品味退步的證明。
- 同名 annotation+property 的成員因 member_name in annotations 被跳過，只留下 value: int，失去property與setter；NamedTuple annotations重建為_fields時也丟掉額外註記。固定members檢查均確認。
- Node.alias = Node 會被當成巢狀類別再次產生，固定review_members檢查觸發RecursionError。需要區分真正的巢狀定義與指向既有類別的值；這是結構關係混同。
- 明確None參數型別與Opaque Annotated metadata的合法語法已處理；TypedDict繼承及鍵檢查通過。但這些通過項不能消除另一條成員生成路徑的資訊遺失。

提醒採納：3/3送達提醒實際採納；另1次靜默。第一則落實逐鍵Required/NotRequired；第二則用_typed_dict_annotation保留明示三態，未解析型別也保留限定符；第三則在_get_deployer_signatures先探索完整provider資料再生成簽章。事件51、64、81及新增相應行為測試支持實際改碼採納。提醒都集中在這些局部關係，沒有覆蓋剩餘property/self-alias失敗。

來源：[Actor 說明](runs/fb-metaflow-stubs/K2/actor-final.txt)、[原始修改](runs/fb-metaflow-stubs/K2/final.patch)、[提醒](runs/fb-metaflow-stubs/K2/provider-attempts.json)、[執行覆核](runs/fb-metaflow-stubs/K2/execution-review.json)。

## 用量與方法

| 次數 | Actor＋Provider 輸入（含快取） | 快取輸入 | 未快取輸入 | 輸出 |
|---|---:|---:|---:|---:|
| K1 | 3,848,935 | 3,565,440 | 283,495 | 50,023 |
| K2 | 4,061,093 | 3,768,832 | 292,261 | 51,293 |

以下為各次原始 Token 用量；缺值保留 null，Provider 呼叫不存在時才是0。Actor 的輸入包含 Provider 送達後續上下文；Provider 模型本身另記，不能只看 Actor 費用。reasoning output 是 output 的子集，不重複加總。

```json
[
  {
    "arm": "K1",
    "actor_usage": {
      "input_tokens": 3623510,
      "cached_input_tokens": 3388416,
      "output_tokens": 43878
    },
    "provider_usage": {
      "input_tokens": 225425,
      "cached_input_tokens": 177024,
      "output_tokens": 6145
    }
  },
  {
    "arm": "K2",
    "actor_usage": {
      "input_tokens": 3658002,
      "cached_input_tokens": 3504384,
      "output_tokens": 43504
    },
    "provider_usage": {
      "input_tokens": 403091,
      "cached_input_tokens": 264448,
      "output_tokens": 7789
    }
  }
]
```

本輪執行契約與程式碼由 Codex 閱讀原始行動及程式作語意覆核，已知組別；沒有新增匿名品味評審票。原七臂沒有合格的 Metaflow 答案，因此不作與失敗交付的品味勝負排名。

條件、harness、傳輸等待與來源見 [MATERIALS](evidence.zip)、[計畫](evidence.zip)；完整數據見 [results-summary.json](results-summary.json)，檔案指紋與原材料保全見 [final-integrity.json](evidence.zip)。

公開副本：本機路徑已匿名化；原始指紋與公開指紋見 [來源索引](source-index.json)。完整事件、執行證據、固定驗收與工具快照位於 [證據包](evidence.zip)。原始 final.patch 未修改。
