# Carmack Performance prototype：實作前決策

記錄時間：2026-10-12；起點：main `fa092ba`。本節保留程式修改前的決策與當時驗證範圍；後續 CLI 啟動嘗試及沙箱阻擋請見 [README](README.zh-TW.md) 與 [交付報告](REPORT.zh-TW.md)。

## 五個觸發問題

1. **現有 hook 能可靠取得什麼？** 倉庫目前 `hooks/hooks.json` 僅將成功與否由核心判讀的原生 `apply_patch` PostToolUse 事件送至 `review_patch`，內容有 tool_use_id、tool_input、tool_response、session/turn/cwd。`UserPromptSubmit` 提供目標與最新要求。既有程式、測試及封存的 lifecycle 說明支持此接線；本次沒有啟動真實 Codex Host，因此不宣稱已驗證一般 shell/profiler 回傳或任意工具自動 hook。
2. **避免每條無關命令觸發？** 不擴大 PostToolUse matcher，不分析 command 關鍵字。預設 software-engineering profile 維持原樣。僅 performance profile 使用明確 `diagnostic_checkpoint.py` 命令列 checkpoint，由 Actor 在一批資料收齊、準備選擇診斷／修改方向時主動呼叫。原 MCP 工具對 Actor 隱藏且只 allowlist review_patch，因此不假定新增 MCP 工具就能被呼叫。checkpoint 用 cwd 與最新要求原文精確匹配唯一已登記輪次，不猜測 session/turn ID；找不到或多義就 fault。
3. **如何界定 meaningful evidence / batch？** Actor 明示 batch_id、reason（這批結果為何影響下一步）、progress（前次建議後的進展），一次提交 1–8 個有工具名稱、穩定結果 ID、原始輸入與非空輸出的紀錄。有限尺寸、防止空批次屬機械檢查；是否有充分量測證據由 Provider 判斷，不用效能字詞或數值門檻冒充語意判斷。材料標示 actor_supplied，不能視為 Host 驗證過的原始事件。不要提交 token、環境變數、帳號或無關整機清單。
4. **無法判斷即將收斂時的替代？** 明確 checkpoint 就是可審計的替代；不聲稱自動辨識 Actor 思考階段。Actor 若忘記呼叫，就沒有診斷 Nudge。仍可在產品 patch 後循原生路徑得到 performance Nudge。
5. **journal 能記錄理由？** 保留 profile、trigger kind、batch_id、reason、progress、來源及內容 fingerprint，以及完整供應材料、Provider 輸出／usage／elapsed 與 fault/silence。相同任務/session 的內容 fingerprint 去重須在 queue reservation 同一交易內完成；忽略外層 batch ID、tool call ID、reason、progress 與紀錄排序，避免重新包裝相同量測造成重複呼叫。穩定 batch_id 改用不同材料是 input fault。新量測要保留實際 timestamp/window，不能只改 ID 假裝新證據。

## 最小界線

- `MASTERS_NUDGE_PROFILE=performance` 明確 opt-in；原預設與 Linus prompt 不改。performance 的 journal 放在資料目錄的 `performance` 子目錄，避免與預設 profile 的額度及歷史混用；Provider model 設定仍沿用原 settings 目錄。
- 仍限制 Git workspace；Windows system diagnosis 可使用專用 Git evidence 工作區，唯讀 Host 資料須由 Actor 明確提供，不擴大 Provider 檔案權限。
- 沿用四欄 schema、parser 及 40/25/61/35（含標籤 200 字）限制。STRUCTURE 是待驗證的量測區分／資料成本關係，可以自然承載純診斷方向；performance 專用尾端引導不要求 Actor 一定修改。
- Provider process、唯讀 MCP、期限、每輪 3 feedback 或 2 silence、fault 封鎖沿用；profile 只選提示與 checkpoint 能力，沒有第二 Actor。
- diagnostic 結果不可因 exit_code=0 就壓成「成功」；超過輸入硬上限則明確 fault；diagnostic 完整包（含要求、metadata、前次 Nudge 與 JSON overhead）超過 20,000 字就 fault，不呼叫 Provider。
- 無 Windows 裝置與模型付費執行授權。本輪提供固定合成 evidence、離線 stub integration 及未執行的真實對照紀錄模板；不得將 fixtures 當作量測、Provider 效果或 A/B 結論。

## 接入與隱私限制（實作前補充）

- 命令列輸出是 Actor 呼叫 command 後讀取的工具結果；並非已驗證的 Codex Host additionalContext hook 送達，也不保證 Actor 會主動提交 checkpoint 或採納。
- cwd/request 比對只讀既有 journal 的 UserPromptSubmit 原文；checkpoint 不另存一份要求或 task_request 到 batch/alias 表，也不讀 transcript、環境變數或整機資料。既有材料包仍須攜帶 task contract。
- rounds 保留歷史 session，不能當作 live session 名冊。若兩個保留 session 的 cwd/request 完全相同，本版拒絕猜測；使用隔離 data directory 並讓 Host 正常記錄新的使用者事件。
- 唯讀 Provider 只沿用 Git workspace 的 search/read，不直接執行診斷命令。使用者／Actor 必須在提交前排除敏感或無關資料；本 prototype 不是秘密辨識／遮罩系統。
