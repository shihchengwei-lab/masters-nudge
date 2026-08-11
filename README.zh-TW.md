# Masters’ Nudge

繁體中文 | [English](README.md)

**套上一位大師的濾鏡做場邊審查，每一位各關注不同的面向。**

<img src="spritesheet.webp" alt="Masters’ Nudge 工程 checkpoint 提醒鈴動畫" width="720">

## 簡介

Masters’ Nudge 掛在 [Claude Code](https://docs.anthropic.com/en/docs/claude-code) 上：在少數時機把當下狀況整理後，送到**另一個**模型做審查，必要時回傳最多 52 字的短評。主 Claude 仍寫碼與決策；本工具只提供第二意見。

| | 誰 | 做什麼 |
|---|---|---|
| 主 agent | Claude Code（Anthropic） | 寫程式、跑工具 |
| 審查 | Masters’ Nudge（預設經 Codex CLI 呼叫 OpenAI） | 在特定事件與回合結束時產出短評 |

**你看不看得到**，和 Claude 看不看得到，不一樣：

| 時機 | Claude | 你（終端機） | 你（浮動視窗，可選） |
|---|---|---|---|
| 工具失敗、測試失敗、或變更首次超過約 80 行 | 當下收到短評 | 看不到 | 看不到 |
| 一輪結束 | 你**下一次**送出訊息時才注入 | 看不到 | 看得到該則短評 |

Claude Code 的 system-reminder 不會畫在終端畫面上，所以沒開浮動視窗時，你多半只會從 Claude 後續行為間接感受到審查結果。

沒有值得講的問題時保持靜默。可選的六種「大師」濾鏡只改優先檢查什麼，見 [濾鏡](#濾鏡)。

```
Claude Code
    │ 工具失敗 / 測試失敗 / 首次大變更
    ├─► 途中審查（同步）→ 只進 Claude
    │
    │ 這一輪結束
    └─► 背景審查 → 寫入本機 log
              ├─ 你下次送出訊息 → 注入 Claude（標成第二意見，非指令）
              └─ 可選：浮動視窗顯示回合末短評
```

## 適用對象

**適用**：使用 Claude Code，且可接受審查時帶出的內容（你的 prompt、工具輸出、檔案片段、錯誤訊息等）離開本機、送到外部模型 API（**預設 OpenAI**；可改 Anthropic）。

**不適用**：對話或程式碼不得外送的環境。細節見 [隱私](#隱私)。不符合就不要裝。

成本上：預設**每個回合結束都會**呼叫一次審查模型；途中僅在命中錯誤／測不過／首次大變更時再呼叫。繁忙時 token 會累積。

## 行為

| 種類 | 何時觸發 | 誰收到 | 時序 |
|---|---|---|---|
| 途中（checkpoint） | 工具錯誤、測試失敗、working tree 首次超過約 80 行變更 | 僅 Claude（貼在該次工具結果旁） | 同步；**僅命中時**可能暫停最多約 15 秒，其餘工具事件只做本機判斷 |
| 回合末（Stop） | Claude 一輪結束 | Claude（下次你送出訊息時）；浮動視窗 | 背景，不擋當前回合 |

注入給 Claude 的回合末短評帶固定框定：第三方第二意見，不是指令。途中短評只送一次，不進浮動視窗，也不在下次 prompt 重送。

輸出要嘛一則 finding，要嘛靜默；finding 去 markdown／套話後硬上限 52 字。

## 安裝

### 前置

- 可用的 Claude Code
- 預設路徑：本機 [Codex CLI](https://github.com/openai/codex) 已安裝且可完成登入／呼叫  
  （或改 `BUDDY_PROVIDER=anthropic`，走 `claude -p`）
- `bash`（macOS／Linux 原生；Windows 可用 Git Bash 或 WSL 跑下方腳本）

### 步驟

1. 複製腳本（不改 settings）：

```bash
bash install.sh
```

目標目錄：`~/.claude/scripts/buddy/`。

2. 打開 `~/.claude/settings.json`，把 [`settings-snippet.json`](settings-snippet.json) 裡的 `hooks` **合併**進去：保留你既有的 hooks，把 snippet 中的 `PostToolUse`、`PostToolUseFailure`、`Stop`、`UserPromptSubmit` 條目加在旁邊。不要整檔覆蓋。snippet 內 `_comment` 亦有提醒。

3. （可選）開浮動視窗，否則你在 UI 上幾乎看不到回合末短評：

```bash
pip install Pillow
```

- **Windows：** 雙擊 `~/.claude/scripts/buddy/start_buddy_window.bat`
- **macOS / Linux：** `python3 ~/.claude/scripts/buddy/buddy_window.py &`

關閉視窗不會停用 hooks。

### 如何確認有在跑

- 在 Claude Code 裡觸發一次測試失敗，或累積超過約 80 行變更後再跑一輪：命中途中審查時 Claude 可能多等數秒；回合結束後應出現 `~/.claude/buddy/<session_id>.log`。
- 腳本錯誤：`~/.claude/buddy-error.log`。
- 若完全沒有 log：多半是 hooks 未合併成功，或 Codex／`BUDDY_PROVIDER` 端呼叫失敗。

## 濾鏡

預設為通用、證據優先的審查。浮動視窗下拉可切換（寫入 `~/.claude/buddy/config.json`，下次審查生效）。啟動 Claude Code 前設 `BUDDY_PERSONA` 可覆寫視窗選擇。

| 值 | 靈感來源 | 優先面向 |
|---|---|---|
| `jeff` | Jeff Dean | 因果、資料流、狀態、規模、維運成本 |
| `linus` | Linus Torvalds | 多餘抽象、繞路、責任歸屬不清 |
| `fowler` | Martin Fowler | 設計氣味、耦合、變更成本、不改行為的重構 |
| `beck` | Kent Beck | 小步驟、測試、當前範圍、做完即停 |
| `lamport` | Leslie Lamport | 不變量、事件順序、重試、部分失敗 |
| `carmack` | John Carmack | 實際執行路徑、量測、多餘工作 |

濾鏡只改檢查優先序，不改證據門檻、單則 finding、字數上限。對應檔案在 `personas/`，附加於 `buddy-prompt.txt` 之後。非模仿本人，亦非六個 agent 同時發言。

<details>
<summary>各濾鏡補充</summary>

##### Jeff Dean — 系統因果與成本

> “As systems scale up, simply stamping out all sources of variability does not work.” — [Jeff Dean](https://research.google/pubs/achieving-rapid-response-times-in-large-online-services/)

機制對應哪個真實限制；沿資料流、延遲、狀態、失敗處理與維運成本追影響。不預設需要 Google 規模。

##### Linus Torvalds — 直接程式碼與責任歸屬

> “Talk is cheap. Show me the code.” — [Linus Torvalds](https://groups.google.com/g/mlist.linux.kernel/c/pdl_7y9bPgk)

遮住實際行為或責任的包裝與間接層。取檢查面向，不是語氣。

##### Martin Fowler — 既有設計的安全演進

> “…to make it easier to understand and cheaper to modify without changing its observable behavior.” — [Martin Fowler](https://martinfowler.com/bliki/DefinitionOfRefactoring.html)

後續變更成本過高的結構；偏好小幅、不改可觀察行為的調整。

##### Kent Beck — 可測的小步

> “You don’t always have to take tiny steps, but they are always an option.” — [Kent Beck](https://newsletter.kentbeck.com/p/first-one-then-many)

當前需求與有效回饋；需求已滿足後是否仍在膨脹實作。

##### Leslie Lamport — 狀態、順序、失敗

> “A distributed system is one in which the failure of a computer you didn’t even know existed can render your own computer unusable.” — [Leslie Lamport](https://www.microsoft.com/en-us/research/publication/distribution/)

隱藏狀態與事件順序；重試、重複、延遲、部分失敗對結果的影響。

##### John Carmack — 實際執行路徑

> “Sometimes, the elegant implementation is just a function. Not a method. Not a class. Not a framework. Just a function.” — [John Carmack](https://twitter.com/ID_AA_Carmack/status/53512300451201024)

控制流與資料搬運；效能宣稱需有量測；不改結果卻增加工作的機制。

</details>

預設走 OpenAI，是為了與主 agent 的 Anthropic 家族錯開；屬設計取捨，非正確率保證。

## 設定

| 環境變數 | 預設 | 作用 |
|---|---|---|
| `BUDDY_PROVIDER` | `openai` | `openai`（`codex exec`）或 `anthropic`（`claude -p`） |
| `BUDDY_MODEL` | `gpt-5.6-sol` / `sonnet` | 傳給選定 CLI 的模型名 |
| `BUDDY_TIMEOUT` | `60` | 回合末模型呼叫逾時（秒） |
| `BUDDY_CHECKPOINT_TIMEOUT` | `15` | 途中審查同步等待上限（秒） |
| `BUDDY_CLAUDE_DIR` | `~/.claude` | log 與狀態目錄 |
| `BUDDY_PERSONA` | 未設定 | 強制濾鏡；優先於浮動視窗 |
| `BUDDY_SPRITE_PATH` | 內建 spritesheet | 自訂透明背景 spritesheet |
| `BUDDY_SHADOW_EVALUATION_DAYS` | `7` | 成本策略 shadow 評估天數 |
| `BUDDY_SHADOW_TARGET_CALLS` | `300` | 評估用目標審查次數 |

審查文案與規則：`~/.claude/scripts/buddy/buddy-prompt.txt`。

### 成本遙測與 shadow 評估

安裝後首次審查起算固定 7 天：可能省成本的略過只標註與量測，實際仍每次呼叫模型。第 7 天後的下一次審查寫入 `~/.claude/buddy/shadow-evaluation.md` 並顯示一次通知；不足 300 次標 `insufficient_samples`，不自動延長，也不自動啟用略過。

每次審查會把不含對話內容的 metadata 追加到 `~/.claude/buddy/review-telemetry.jsonl`。若要重開評估，刪除 `shadow-evaluation.json`、`shadow-evaluation.md`、`review-telemetry.jsonl`。

## 隱私

**會把對話與工具事件送至外部模型廠商。** 每次回合末審查，以及每次命中的途中審查，各為一次外送。內容可能包含：

1. 最新使用者 prompt（上限 2000 字；長文保留頭尾，中段標截斷）
2. 途中：觸發的工具事件（≤3000）與最近 agent 上下文（≤1200）
3. 回合末：最後宣告（≤2500）與當輪工具結果（≤2000；可能含讀檔內容、指令輸出、錯誤、diff）。缺證據時退回較長的 transcript 切片
4. 可選的 agentcam 摘錄（合計 ≤2000）
5. 本 session 最近最多 3 則短評（避免重複）
6. 審查用 system prompt 與選定濾鏡檔（規則，非你的專案原文）

預設 `BUDDY_PROVIDER=openai` 會把與 Anthropic 主 agent 相關的內容轉送 OpenAI。中途切換 provider 時，先前短評可能作為「最近幾則」送進新廠商。反應與任務錨點亦以明文存在 `~/.claude/buddy/`。

連同廠商外送都不能接受時，請勿啟用。廠商保留／訓練政策請查現行 API 條款。

## 選用整合

### agentcam

若使用 [agentcam](https://github.com/shihchengwei-lab/agentcam)，會在有報告時附上風險、變更檔、exit code、測試與驗證等段落。未安裝則跳過。

### 自訂 sprite

```bash
export BUDDY_SPRITE_PATH=/path/to/spritesheet.png
```

檔案不存在時仍開視窗，僅無動畫。

### 語系

預設提示為繁體中文。換語系需同步：`buddy-prompt.txt`、`inject.py` 內包裝字串（搜尋 `第三方第二意見`），可選更新 `test_buddy.py` 的中文 fixture。管線本身與語言無關。

## 實作摘要

審查用小型、有標籤的證據封包，而非固定重送整段對話。你送出訊息時記錄任務錨點與 transcript 位置；途中帶錨點與觸發事件；回合末帶錨點、最終宣告與當輪工具結果。結構化契約見 `reaction-schema.json`。

倉庫內腳本與路徑仍使用 `buddy.py`、`BUDDY_*`、`~/.claude/buddy/`，以免破壞既有安裝。產品名稱為 Masters’ Nudge。

| 元件 | 路徑 |
|---|---|
| 安裝 | `install.sh` → `~/.claude/scripts/buddy/` |
| Hooks 片段 | `settings-snippet.json` |
| 途中審查 | `checkpoint.sh` / `checkpoint.py` |
| 回合末審查 | `buddy.sh` / `buddy.py` |
| 注入 | `inject.sh` / `inject.py` |
| 證據封包 | `source_context.py` |
| 提示與濾鏡 | `buddy-prompt.txt`、`personas/*.txt` |
| 輸出契約 | `reaction-schema.json` |
| 浮動 UI | `buddy_window.py`、`start_buddy_window.bat` |
| 測試 | `python -m unittest test_buddy -v` |
| 路線圖 | `ROADMAP.md` |
| 歷史筆記 | `BUDDY_FORENSICS_REPORT.md` |

Runtime：

| 路徑 | 用途 |
|---|---|
| `~/.claude/buddy/<session_id>.log` | 反應 JSONL |
| `~/.claude/buddy/<session_id>.state.json` | 注入讀取指標 |
| `~/.claude/buddy/<session_id>.source.json` | 任務錨點與 transcript 位置 |
| `~/.claude/buddy/config.json` | 視窗保存的濾鏡 |
| `~/.claude/buddy/<session_id>.checkpoints/` | 途中審查去重 |
| `~/.claude/buddy-error.log` | 錯誤 log |

## 已知限制

- 命中途中審查可能讓 agent 暫停最多 `BUDDY_CHECKPOINT_TIMEOUT`（預設 15 秒）。
- 測試失敗啟發式可能漏判少見 runner；大變更依 Git 與未追蹤文字檔，binary 不計，session 內約超過 80 行後觸發一次。
- 簡短 follow-up（如「繼續」）會取代先前詳細 prompt 作為任務錨點。
- 當輪工具證據依賴 transcript 寫入時機；延遲寫入可能不完整。
- 若你在回合末審查完成前就送下一則訊息，該則短評會晚一輪才注入。
- 無時間 cooldown；回合末每次都呼叫模型。成本略過目前僅 shadow。
- 其他 hook 若無 `BUDDY_ACTIVE` 類防護，仍可能與 `claude`／`codex` 形成迴圈。

## 起源

參考 [`cold-eyes-reviewer`](https://github.com/shihchengwei-lab/cold-eyes-reviewer) 的 hook 與 CLI 模式，並從 Claude Code 舊 Buddy／Cinder companion 用法重寫。`buddy_screenshot.png`、`cinder_screenshot.png` 為歷史素材；現行圖示為工程 checkpoint 提醒鈴。

## 授權

MIT
