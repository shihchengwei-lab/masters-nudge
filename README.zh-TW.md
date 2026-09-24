# Masters’ Nudge

繁體中文 | [English](README.md)

Masters’ Nudge 在寫程式的模型（Actor）修改程式後，呼叫另一個模型（Provider）讀取任務、修改與相關程式碼。Provider 回傳一則結構建議或不回饋；有建議時，工具會把它附在工具結果後，於 Actor 下一步前送進脈絡。Actor 決定怎麼實作。工具規則見 [SPEC.zh-TW.md](SPEC.zh-TW.md)。

## 案例：自訂快取鍵不應讀到繼承屬性

最近一次評估要求 Express 在渲染畫面時支援自訂 `cacheKey`。A 臂沒有 Provider，B 臂收到 Masters’ Nudge 回饋。B 臂初稿已讓快取讀寫使用新鍵，但快取仍是一般物件。Provider 回傳：

```text
OBSERVED: cache['toString'] -> Function
VIOLATES: inherited key -> false hit
PREFER: cache := Object.create(null)
```

B 臂 Actor 收到回饋後，把快取初始化改成 `Object.create(null)`；A 臂保留 `{}`。因此在 B 臂中，`toString` 之類的鍵只會對應實際存入的快取項目。兩臂都通過任務驗收，兩位盲評者都認為 B 的結構較好。

## 目前證據

最新正式評估中，兩臂任務驗收各通過 9/12，其中一題的文字與驗收標準有歧義。可盲評的八組中，B 勝四組、平手四組；B 的總執行時間多約 50%，非快取輸入 Token 多約 77%。[正式 Benchmark 報告](benchmark/formal-v8/ROUND-8-REPORT.zh-TW.md)記錄了方法、兩次 Vue CSS 建議的時序依賴問題及其他限制。這份結果測的是目前分支尚未發布的提示詞，不能當成已安裝版本的發行驗證。

每次 `apply_patch` 成功後，原生 PostToolUse 會同步呼叫常駐的 Codex 接入 MCP 工具
`review_patch`，由核心把任務、這次修改、成功結果及修改後工作區組成一次判斷。OpenAI／Codex Provider
依六條結構準則查看材料；提示詞要求沿程式路徑追查相關程式碼，以及新增分支或操作的輸入型別與 API，並可透過另一個唯讀 repository MCP 搜尋或讀檔。
有反饋時，工具保留原本的成功工具結果，再把 `OBSERVED`、`VIOLATES`、`PREFER` 三欄附在同一則結果後面，並要求執行者先判斷目前做法是否為任務必要。執行者仍決定是否採納建議，並負責實作及驗證。

每輪最多三次反饋或兩次沉默；任一上限到達便停止。使用者新訊息重置額度，衝突要求以最新的為準。
正常但沒有具體疑點時沉默。工具錯誤另外顯示「本輪反饋未執行」，不冒充沉默，不計入額度。

## 支援範圍

- Python 3.10+、Git 工作區、已登入的 Codex Provider。
- Actor 需使用能提供 UserPromptSubmit、PostToolUse 與 turn_id 的 Codex。
- Provider 僅 OpenAI／Codex，沒有其他供應商的替代路徑。
- Codex 接入 MCP 只公開 `review_patch`；Provider 唯讀 MCP 只允許工作區文字搜尋與範圍讀檔，本批材料與後續讀取共用容量限制。
- 工具輸入必須有完整修改文字、差異或路徑與寫入內容。看不出修改內容的命令列寫檔不在支援範圍。

## 已知限制

Windows 上的 Codex 若在同步 `PostToolUse` 執行期間中斷該輪，可能已送出 `hook/started`，卻沒有同一執行序號的
`hook/completed`。Masters’ Nudge 因而無法只靠事件判斷該次 Hook 已取消或仍在執行；這不是 Provider 沉默。
最小重現、事件順序與期望行為已提交至 [openai/codex#46765](https://github.com/openai/codex/issues/46765)，目前仍待 Codex 執行層修復。
本地重現紀錄見 [Codex PostToolUse 生命週期規格](experiments/champion-vs-preserved-result-20260920/CODEX-POSTTOOLUSE-LIFECYCLE-SPEC.md)。

目前原始碼與產生的插件副本一致。實際安裝狀態、不同 Codex 版本的事件行為，以及更新已安裝插件後的新任務完整流程，
仍須在目標環境另外確認，不能由單元測試代替。

## 設定與紀錄

```powershell
python masters_nudge_cli.py provider get
python masters_nudge_cli.py provider set openai --model gpt-6-sol
python masters_nudge_cli.py doctor --host codex
python masters_nudge_cli.py recent-nudges --limit 10
```

紀錄預設保存在使用者目錄下的 .masters-nudge/data/feedback.sqlite3，設定另存在 .masters-nudge/config.json。
紀錄包含材料、判斷、錯誤與有提供時的用量；送出反饋不代表執行者採納。
插件清單版本為 `0.6.0+codex.20260922164420`；目前分支的提示詞修改尚未發布。程式碼在未儲存模型選擇時仍以 `gpt-5.6-sol`、medium reasoning 為預設；儲存設定後會覆蓋這個值。上方評估使用 `gpt-6-sol`、medium reasoning，實際設定以 `provider get` 查詢結果為準。

## 隱私

任務、修改、工具結果及 Provider 自行選讀的檔案內容會傳給 OpenAI。
Provider 唯讀 MCP 禁止讀取工作區外、Git 內部及被忽略的檔案。工具不修改執行者的檔案。

## 開發

原始碼是唯一實作來源，插件副本由既有建置指令產生。

```powershell
python tools/build_plugin.py --write
python tools/build_plugin.py --check
python -m unittest discover -s tests -v
```
