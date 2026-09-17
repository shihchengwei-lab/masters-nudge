# Masters’ Nudge

繁體中文 | [English](README.md)

在執行者修改程式之後，提供一則小幅反饋，讓執行者重新判斷資料關係。
工具規格以 [SPEC.zh-TW.md](SPEC.zh-TW.md) 為準；目前重構驗收進度見 [驗收紀錄](docs/spec-refactor-progress.zh-TW.md)。

使用者要求先交給執行者。工具在原生 PostToolBatch 收到明確修改後，將任務、修改及工具結果交給
OpenAI Provider。Provider 以 Linus Torvalds 的六條思考準則查看材料，需要更多脈絡時自行搜尋或讀檔。
執行者決定是否採納建議，負責實作及驗證。

每輪最多三次反饋或兩次沉默；任一上限到達便停止。使用者新訊息重置額度，衝突要求以最新的為準。
正常但沒有具體疑點時沉默。工具錯誤另外顯示「本輪反饋未執行」，不冒充沉默，不計入額度。

## 支援範圍

- Python 3.10+、Git 工作區、已登入的 Codex Provider。
- Actor 需使用能提供 UserPromptSubmit、PostToolBatch 與 turn_id 的 Codex。
- Provider 僅 OpenAI／Codex，沒有其他供應商的替代路徑。
- MCP 只允許工作區文字搜尋、範圍讀檔；本批材料與後續讀取共用容量限制。
- 工具輸入必須有完整修改文字、差異或路徑與寫入內容。看不出修改內容的命令列寫檔不在支援範圍。

本機有自行維護的 PostToolBatch Codex 版本；一般 Codex 安裝是否支援，必須實際核對。
尚未完成驗收的版本不宣告已可正常交付；請以驗收紀錄為準。

## 設定與紀錄

```powershell
python masters_nudge_cli.py provider get
python masters_nudge_cli.py provider set openai --model gpt-5.6-sol
python masters_nudge_cli.py doctor --host codex
python masters_nudge_cli.py recent-nudges --limit 10
```

紀錄預設保存在使用者目錄下的 .masters-nudge/data/feedback.sqlite3，設定另存在 .masters-nudge/config.json。
紀錄包含材料、判斷、錯誤與有提供時的用量；送出反饋不代表執行者採納。

## 隱私

任務、修改、工具結果及 Provider 自行選讀的檔案內容會傳給 OpenAI。
MCP 禁止讀取工作區外、Git 內部及被忽略的檔案。工具不修改執行者的檔案。

## 開發

原始碼是唯一實作來源，插件副本由既有建置指令產生。

```powershell
python tools/build_plugin.py --write
python tools/build_plugin.py --check
python -m unittest discover -s tests -v
```

MASTERS_NUDGE_TEST_MODE=1 用於實測：故障回報為無效，測試執行程式必須停止該輪，不得繼續評分。
歷史實驗不屬於目前版本的驗收測試。
