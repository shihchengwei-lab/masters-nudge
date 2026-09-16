# Masters’ Nudge

繁體中文 | [English](README.md)

> **Actor 完成修改後、再次思考前，加入一則獨立觀察。**

Masters’ Nudge 會針對 Claude Code 或 Codex Agent 剛完成的修改，提供至多一則
Nudge。Provider 只會看到任務與剛完成的修改；選擇解法、實作及驗證仍由 Actor
負責。

## 契約

只有明確完成修改的工具批次可以觸發 Provider：`patch`、`diff`、路徑加上
`old_string` 與 `new_string`，或路徑加上 `content`。Codex 原生
`apply_patch` 的 `command` 必須含完整 patch 外框才會被接受。

Provider 輸入只有：

```text
使用者任務 + 剛完成的修改
```

Provider 輸出只有兩種：

```json
{"nudge":null}
```

```json
{"nudge":{"message":"<一個具體關係>","evidence":["<任務或修改中確實存在的材料>"]}}
```

Provider 無法查看 Actor 工作區，也不會收到任務起點快照、累積 diff、檔案目前
內容、Actor 對方案的說明，或讀取 repository 的工具。完整任務與修改若超過輸入
上限，這次嘗試會直接結束，不會截斷後送出半份證據。

Nudge 會在修改批次完成後、Actor 下一次推理前加入 Host context。Nudge 不是
patch、命令、對話或最終 review；Actor 可以重新考慮整個解法，並保有全部實作權。
同一任務成功交付一則 Nudge 後，後續修改批次保持安靜。

## 時機

```text
任務 → Actor 修改 → 可選的一則 Provider Nudge → Actor 下一次推理
```

Claude Code 提供所需的 `PostToolBatch` 控制點。Codex 必須使用支援
`PostToolBatch` 的 build；只有 `PostToolUse` 的原版 Codex 不會執行此 Hook。
本機 Codex 實作與上游需求整理在
[`PostToolBatch` Issue 草稿](docs/codex-post-tool-batch-issue-draft.md)。

Provider 發生錯誤或超時時，主要 Agent 會在沒有 Nudge 的情況下繼續。

## 隱私

Anthropic 與 OpenAI 會收到任務及剛完成的修改，因此內容會離開電腦，並受
Provider 的資料政策約束。本機 Ollama 會把內容留在電腦上；Masters’ Nudge 只允許
Ollama 使用本機位址，也不會失敗後偷偷改送雲端。

本機任務狀態與已回傳的 Nudge 紀錄存放在 `~/.masters-nudge/data/`。紀錄只能
證明 Host 已回傳 Nudge，不能證明 Actor 已採納或照做。

## 支援的 Provider

- Anthropic
- OpenAI
- 本機 Ollama

每次嘗試只會使用一個已選定的 Provider。

## 安裝

需求：

- 支援 Plugin 的 Claude Code 或 Codex CLI；
- Python 3.10+；
- 已登入 Anthropic 或 OpenAI 對應 CLI，或已啟動 Ollama 並安裝指定模型。

### Claude Code

```powershell
claude plugin marketplace add shihchengwei-lab/masters-nudge
claude plugin install masters-nudge@masters-nudge --config python_command=python
```

### Codex

```powershell
codex plugin marketplace add shihchengwei-lab/masters-nudge
codex plugin add masters-nudge@masters-nudge
```

安裝後請開新任務。在 Codex 中開啟 `/hooks`，檢查並批准 Plugin 命令。

## 直接請 Agent 操作

Hooks 會自動執行。手動 Skills 可以檢查準備狀態、切換 Provider，或顯示近期
Nudge 紀錄。使用者不必修改環境變數或判讀原始 JSON。

## 開發

Repository 原始碼是唯一實作來源；版控中的 Plugin 套件由原始碼產生。

```powershell
python -m unittest discover -s tests -v
python tools\build_plugin.py --check
```

授權：[MIT](LICENSE)
