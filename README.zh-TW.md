# Masters’ Nudge

繁體中文 | [English](README.md)

Masters’ Nudge 會在少數工作檢查點與回合結束時，替 Claude Code 或 Codex 加入一個有證據依據的簡短第二意見。輸出要嘛是一句開放問句，要嘛保持安靜；所有決策與修改仍由主要 coding agent 負責。

目前套件版本：`0.2.0-dev.1`（預發行版）。

## 功能

Masters’ Nudge 把 hooks、skills、reviewer prompts、六種軟體工程濾鏡，以及選用的浮動視窗包成一個 plugin。它關注未驗證假設、範圍膨脹、回饋不足、脆弱的事件順序，以及證據尚未支持的完成宣告。

Nudge 不是 code review、命令，也不能證明另一個模型比較正確。Finding 會清除多餘格式，最長 52 個字。工具失敗、測試失敗、大型變更、長期目標狀態轉換與回合結束，都可能觸發一次 reviewer。

## 安裝

需求：

- 支援 plugin 的 Claude Code 或 Codex CLI
- Python 3.10+
- 已登入所選雲端 host CLI；若使用本機 Ollama 則不需要雲端登入

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

Shader 研究採用以下目標契約：交付在固定視覺與量測契約下，經實證建立且可重現的最佳 Shader Pareto 前沿，並保留足以重現候選判定的研究紀錄。

常用環境變數：

| 變數 | 預設 | 用途 |
|---|---|---|
| `MASTERS_NUDGE_PROVIDER` | 依 host 決定 | `anthropic`、`openai`、`grok` 或 `ollama-local` |
| `MASTERS_NUDGE_MODEL` | 依 host 決定 | Reviewer 的完整模型名 |
| `MASTERS_NUDGE_OLLAMA_URL` | `http://127.0.0.1:11434` | Loopback Ollama endpoint |
| `MASTERS_NUDGE_TIMEOUT` | `120` | 回合結束 reviewer 逾時秒數 |
| `MASTERS_NUDGE_CHECKPOINT_TIMEOUT` | `90` | 途中 reviewer 逾時秒數 |
| `MASTERS_NUDGE_DATA_DIR` | `~/.masters-nudge/data` | Logs、state、receipts、telemetry 與 reviewer 設定 |
| `MASTERS_NUDGE_PERSONA` | 未設定 | 強制 `jeff`、`beck`、`fowler`、`linus`、`lamport` 或 `carmack` |
| `MASTERS_NUDGE_SPRITE_PATH` | 內建 sprite | 選用浮動視窗 spritesheet |

環境變數優先於持久化的 `reviewer.json`。若持久設定損壞，審查會停止並留下診斷，不會靜默切換 provider。

本機模式只接受 loopback HTTP、停用 client proxy 與 redirect、要求 Ollama 回報 cloud 功能已關閉，並拒絕 remote model metadata。Masters’ Nudge 不會安裝或下載模型，也不會失敗後改用雲端 provider。Grok 則會透過已登入的 Grok CLI 使用 xAI 雲端服務。

## 隱私

預設 reviewer 會把受限的當下證據封包送到外部 provider：Claude Code 送至 Anthropic，Codex 送至 OpenAI；明確設定 `grok` 時送至 xAI。本機模式只送到通過驗證的 loopback Ollama server。

依觸發事件不同，封包可能包含：

- 最新使用者任務摘要；
- 觸發事件的工具輸入／輸出、錯誤、測試結果或 diff 摘要；
- 受長度限制的當回合 journal 或 Claude transcript 片段；
- 當下最終宣告與驗證證據；
- 選用的 agentcam evidence；
- Reviewer prompt 與所選濾鏡。

Reactions、任務摘要、受限 journal、投遞 receipts、注入後第一個可觀察的 host 動作、本機模型設定與不含對話內容的 telemetry，會以純文字存在 `~/.masters-nudge/data/`。後續動作只證明時序，不代表 Nudge 造成該動作。外部 provider 的保留與訓練政策不屬於本 repository，而且可能改變。

## 證據與限制

保留的證據索引位於 [evaluation/README.md](evaluation/README.md)。歷史 raw runs、截圖與工作目錄封存於已驗證的 [evidence archive release](https://github.com/shihchengwei-lab/masters-nudge/releases/tag/evidence-archive-2026-08-22)；完整 Riemann 實驗仍可從固定的 [tagged source tree](https://github.com/shihchengwei-lab/masters-nudge/tree/evidence-archive-2026-08-22/experiment/riemann-domain) 取得。

現有證據只支持以下有限結論：

- 固定 synthetic packets 顯示濾鏡區分與 schema compliance；不能證明一般情境的可靠性。
- Phase B synthetic tasks 沒有產生正向 treatment effect，實驗已停止。
- 歷史 Riemann trace 早於問句限定契約，而且投遞 receipt 不完整；不能作為目前產品驗證，也不能證明因果或數學正確性。
- 不同 provider 回報的 token、latency 與估計成本不是同一口徑，也不是帳單保證。
- 若 host 沒有送出預期原生事件，hook 投遞只能 best-effort。

## 開發

Repository 內的 plugin package 由原始碼產生。送出變更前執行：

```bash
python -m unittest discover -v
python tools/build_plugin.py --check
```

- 架構：[docs/phase-c-architecture.md](docs/phase-c-architecture.md)
- 目前決策：[ROADMAP.md](ROADMAP.md)
- 授權：[MIT](LICENSE)
