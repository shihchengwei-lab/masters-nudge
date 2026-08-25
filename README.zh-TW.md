# Masters’ Nudge

繁體中文 | [English](README.md)

Masters’ Nudge 會在少數工作檢查點與回合結束時，替 Claude Code 或 Codex 加入一則簡短、以證據為錨點的獨立第二意見。Reviewer 可以指出被忽略的限制、反例、替代假設或方向，也可以保持安靜；實際送出的 Nudge 會標示為「獨立第二意見：」，所有決策與修改仍由主要 coding agent 負責。

## 功能

Masters’ Nudge 把 hooks、skills、reviewer prompts、六種軟體工程濾鏡，以及選用的浮動視窗包成一個 plugin。它關注未驗證假設、範圍膨脹、回饋不足、脆弱的事件順序，以及證據尚未支持的完成宣告。

Nudge 不是 code review、命令，也不能證明另一個模型比較正確。Finding 必須留在既有任務契約內、指出一個有限檢查、符合結構化輸出契約且最長 52 個字；不合格輸出會被拒絕，不會由程式改寫。相同可觀察範圍第二次失敗、長期目標明確轉成 `complete` 或 `blocked`，以及回合結束，都可能觸發 reviewer。一般變更、成功的專科證據、大型 diff 與單次失敗只會留下證據，不會打斷主要 agent。

符合條件的 checkpoint 與 Stop review 會同步執行：host 等 reviewer 回覆，並在同一回合送出 finding。Provider 工作最多 90 秒，外層 host hook 預留 120 秒；符合條件的事件可能因此增加等待時間。錯誤或逾時不會產生 Nudge，也不會自動重試 Provider 或切換 provider。

## 安裝

需求：

- 支援 plugin 的 Claude Code 或 Codex CLI
- Python 3.10+
- 已登入所選雲端 reviewer provider 對應的 CLI；若使用本機 Ollama 則不需要雲端登入

Claude Code：

```bash
claude plugin marketplace add shihchengwei-lab/masters-nudge
claude plugin install masters-nudge@masters-nudge --config python_command=python
```

若 `python` 不是 Python 3.10+，請將 `python_command` 改成 `python3` 或執行檔絕對路徑。設定值只能是一個執行檔，不能包含參數。

Codex：

```bash
codex plugin marketplace add shihchengwei-lab/masters-nudge
codex plugin add masters-nudge@masters-nudge
```

安裝後請開新 task。Codex 使用者需開啟 `/hooks`，檢查命令後批准 plugin hooks。Plugin 封裝與 hook 核准方式以目前的 [OpenAI plugin 文件](https://developers.openai.com/plugins/build/plugins)及 [Codex hooks 文件](https://learn.chatgpt.com/docs/hooks)為準。

更新或移除：

```bash
# Claude Code
claude plugin marketplace update masters-nudge
claude plugin update masters-nudge@masters-nudge
claude plugin uninstall masters-nudge@masters-nudge

# Codex
codex plugin marketplace upgrade masters-nudge
codex plugin add masters-nudge@masters-nudge
codex plugin remove masters-nudge@masters-nudge
```

更新後請重新啟動 host。解除安裝不會刪除 `~/.masters-nudge/data/`。

## 使用與檢查

Hooks 會自動執行。以下說法會啟用 plugin 內建 skills：

- 「檢查 Masters’ Nudge 是否準備完成。」— 檢查 runtime、provider、data 目錄寫入權限、hooks 與選用 UI 依賴，不會呼叫 reviewer。
- 「開啟 Masters’ Nudge 浮動視窗。」— 開啟本機歷史視窗；需要 Pillow，以及含 Tkinter 的 Python。
- 「將 Masters’ Nudge 設定成使用我的本機 Ollama 模型 `<完整模型名>`。」— 驗證 loopback Ollama 上已安裝的模型並儲存設定。
- 「遷移舊版 Masters’ Nudge hooks。」— 先顯示 dry run，取得明確同意後才處理完全符合的舊 hook。

遷移在修改 host 設定前會建立相鄰的時間戳備份。修改過或有歧義的 hooks、格式錯誤資料、目的檔衝突，以及無法安全轉成新階段的舊 specialist persona，都會留給人工處理。既有審查資料不會被刪除。

## 設定

未覆寫時，Claude Code 使用 Anthropic `sonnet`；Codex 使用 OpenAI `gpt-5.6-sol`。Reviewer 永遠是另一個模型呼叫，即使使用與 host 相同的 provider。

常用環境變數：

| 變數 | 預設 | 用途 |
|---|---|---|
| `MASTERS_NUDGE_PROVIDER` | 依 host 決定 | `anthropic`、`openai`、`grok` 或 `ollama-local` |
| `MASTERS_NUDGE_MODEL` | 依 host 決定 | Reviewer 的完整模型名 |
| `MASTERS_NUDGE_OLLAMA_URL` | `http://127.0.0.1:11434` | Loopback Ollama endpoint |
| `MASTERS_NUDGE_TIMEOUT` | `90` | 回合結束 reviewer 逾時；超過 90 會被限制為 90 |
| `MASTERS_NUDGE_CHECKPOINT_TIMEOUT` | `90` | 途中 reviewer 逾時；超過 90 會被限制為 90 |
| `MASTERS_NUDGE_DATA_DIR` | `~/.masters-nudge/data` | Logs、state、receipts、telemetry 與 reviewer 設定 |
| `MASTERS_NUDGE_STAGE` | 未設定 | 選擇 `design`、`build`、`evolve` 或 `review` |
| `MASTERS_NUDGE_SPRITE_PATH` | 內建 sprite | 選用浮動視窗 spritesheet |

Provider 環境變數優先於持久化的 `reviewer.json`；`MASTERS_NUDGE_STAGE` 優先於 `config.json` 的工程階段。若 reviewer 設定損壞，審查會停止並留下診斷，不會靜默切換 provider。

浮動視窗與公開設定只呈現工程階段和實際關注點，不顯示作為 reviewer 內部注意力提示的人物。Review 已到期後，直接的可靠性或效能證據可以選擇對應 specialist；專科證據本身不會觸發 review，兩者也不是手動階段設定。

本機模式只接受 loopback HTTP、停用 client proxy 與 redirect、要求 Ollama 回報 cloud 功能已關閉，並拒絕 remote model metadata。Masters’ Nudge 不會安裝或下載模型，也不會失敗後改用雲端 provider。Grok 則會透過已登入的 Grok CLI 使用 xAI 雲端服務。

## 隱私

預設 reviewer 會把受限的當下證據封包送到外部 provider：Claude Code 送至 Anthropic，Codex 送至 OpenAI；明確設定 `grok` 時送至 xAI。本機模式只送到通過驗證的 loopback Ollama server。

依觸發事件不同，封包可能包含：

- 最新使用者任務要求；
- 從任務中明示的本機來源讀到的內容；
- 分開且受長度限制的實質變更、驗證與失敗歷史；
- 觸發 checkpoint、當下最終宣告或完成證據；
- 選用的 agentcam evidence；
- Reviewer prompt 與所選濾鏡。

一般搜尋／瀏覽輸出、工具名稱與命令、主模型進行中的說明及完整 transcript 不會放進 reviewer 封包；有長度上限的語意 diff、驗證目標與失敗結果仍會保留。最近三則已注入 Nudge 文字只會用來避免重複，不包含主模型反應。注入後，下一次工具階段 review 會等待新的語意變更及其後續驗證或失敗。Reactions、任務要求、分層證據、投遞 receipts、本機模型設定與不含對話內容的診斷 telemetry，會以純文字存在 `~/.masters-nudge/data/`。Telemetry 只記錄路由、狀態、延遲與 provider 回報的用量 metadata；目前沒有正式成本實驗，也沒有自動成本 gate。Hook response 寫出並 flush 後只記為 `emitted`；必須等後續有語意證據的 Claude 或 Codex host event，才確認為 `injected`。後續動作只證明時序，不代表 Nudge 造成該動作。外部 provider 的保留與訓練政策不屬於本 repository，而且可能改變。

## 證據與限制

保留的證據索引位於 [evaluation/README.md](evaluation/README.md)。

現有證據只支持以下有限結論：

- 最新固定順序 benchmark 使用四題額外且先前未使用的 SWE-bench Verified 任務；Arm A 通過 2/4，Arm B 通過 3/4。T03 的結果不同，T04 則兩組都失敗。
- Arm B 產生六則 finding，六則都已注入並各有後續 response observation；這只證明投遞順序，不代表 Nudge 造成後續動作或結果。
- 不同 provider 回報的 token、latency 與估計成本不是同一口徑，也不是帳單保證。
- 若 host 沒有送出預期原生事件，hook 投遞只能 best-effort。

## 開發

Repository 內的 plugin package 由原始碼產生。送出變更前執行：

```bash
python -m unittest discover -v
python tools/build_plugin.py --check
```

- 架構：[docs/architecture.md](docs/architecture.md)
- 目前決策：[ROADMAP.md](ROADMAP.md)
- 授權：[MIT](LICENSE)
