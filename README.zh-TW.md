# Masters’ Nudge

繁體中文 | [English](README.md)

**在長任務裡，替 Claude Code 加一個不同的聲音。**

## 簡介

Claude Code 做得越久，前面的選擇越容易一路影響後面的工作。

方向對了，工作會越來越順；方向偏了，它也可能沿著同一條路繼續補、繼續繞，直到看起來完成，卻留下原本沒看見的問題。

Masters’ Nudge 會在幾個關鍵時刻，請另一個模型看一小段剛發生的工作，再留下一句最值得提醒的事。沒有明確問題，就保持安靜。

Claude Code 照常工作與決定；Masters’ Nudge 只在旁邊加一個不同的聲音。

## 為什麼只說一句？

每次提醒最多 52 個字，只指出一個具體問題。

可能是方向偏了、範圍越做越大、結構變得太複雜，或完成的結論還缺少證據。

這 52 個字的重點，不是多給一份答案，而是讓同一份工作被換個角度看一次。Claude Code 可以在繼續之前，重新看一眼眼前的選擇。

## 為什麼換一個模型？

同一個模型回頭檢查自己的工作，容易繼續沿用原來的想法。

因此，Masters’ Nudge 預設讓 Anthropic 的 Claude Code 負責工作，再由 OpenAI 模型從旁檢查。換一個模型，是為了增加看見不同問題的機會。

審查模型只會收到一小段當下資料，也只能根據這些內容提出提醒。看不出明確問題，就不出聲。

## 它什麼時候加入？

```
Claude Code 正常工作
    │ 工具失敗 / 測試失敗 / 首次大變更
    ├─► 立即檢查一次 → 只交給 Claude
    │
    │ 這一輪結束
    └─► 背景檢查一次
              ├─ 下次對話時交給 Claude
              └─ 顯示在浮動視窗
```

| 時機 | 再看一眼的原因 | 誰會看到 |
|---|---|---|
| 工具失敗 | 可能只處理了表面症狀 | Claude Code |
| 測試失敗 | 修法可能開始繞遠路 | Claude Code |
| 變更首次超過約 80 行 | 工作範圍可能正在變大 | Claude Code |
| 一輪工作結束 | 確認結果是否真的完成 | Claude Code、浮動視窗 |

途中檢查只在命中前三種情況時呼叫模型，可能讓 Claude Code 多等最多約 15 秒。回合末檢查在背景執行，不會擋住剛完成的工作。

回合末短評會在你下次送出訊息時交給 Claude。Claude Code 不會把這類 system-reminder 顯示在終端機裡；浮動視窗是你直接看到短評的地方。

輸出要嘛一則 finding，要嘛靜默；finding 去除 markdown 與套話後，硬上限為 52 字。

## 適用對象

**適用**：使用 Claude Code，且可接受審查時帶出的內容（你的 prompt、工具輸出、檔案片段、錯誤訊息等）離開本機、送到外部模型 API（**預設 OpenAI**；可改 Anthropic）。

**不適用**：對話或程式碼不得外送的環境。細節見 [隱私](#隱私)。不符合就不要裝。

成本上：預設**每個回合結束都會**呼叫一次審查模型；途中僅在命中錯誤／測不過／首次大變更時再呼叫。繁忙時 token 會累積。

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

## 濾鏡：不同階段，看不同地方

專案在不同階段，容易忽略的事情也不同。

設計時，要留意資料、狀態與責任放在哪裡；實作時，要留意是否越做越多；程式開始成長後，要留意下一次修改會不會變難；準備交付時，則重新看看哪些複雜度其實不需要存在。

| 階段 | 視角 | 它會先問 |
|---|---|---|
| General only | 一般檢查 | 現在最明確的問題是什麼？ |
| Design | Jeff Dean（`jeff`） | 資料、狀態與責任是不是放錯地方？ |
| Build | Kent Beck（`beck`） | 是否已經做超過現在需要的範圍？ |
| Evolve | Martin Fowler（`fowler`） | 這個結構會不會讓下次修改更困難？ |
| Review | Linus Torvalds（`linus`） | 哪些多餘層次其實不需要存在？ |

另外兩個視角會在出現明確訊號時，暫時加入一次：

- 遇到重試、冪等、競態、重複處理、先後順序或部分失敗時，改從 Leslie Lamport（`lamport`）的角度檢查。
- 遇到 profiler、benchmark，或連到延遲、吞吐、配置、複製、I/O、hot path 的實測數字時，改從 John Carmack（`carmack`）的角度檢查。

兩者同時符合時，先看正確性風險較高的 Lamport 視角。只出現 `async`、`cache`、`performance` 或 `latency` 其中一個詞，不足以切換。

每個名字代表一組關注重點。短評不會模仿本人，語氣始終維持直接、具體。

不論目前是哪個階段，只要眼前有明顯錯誤、證據不足、做偏需求或交付缺口，Masters’ Nudge 都會先指出它。

浮動視窗下拉會把階段寫入 `~/.claude/buddy/config.json`，下次審查生效；預設為 Build。下拉顯示選定的階段，彩色 badge 顯示上一則短評實際使用的視角。Lamport 或 Carmack 暫時加入時，badge 會改變，但下拉選擇不變。

新設定檔格式為 `{"stage":"build"}`；合法階段是 `general`、`design`、`build`、`evolve`、`review`。

啟動 Claude Code 前設定 `BUDDY_PERSONA` 仍可強制指定 lens，且會停用專科切換。舊 persona 格式的設定仍可讀取：四個生命週期 lens 映射到對應階段；舊 Lamport／Carmack 選擇會維持鎖定，直到使用者在視窗改選階段。

Lens 只改先看哪類問題，不改證據門檻、模型呼叫次數、單則 finding 或字數上限。對應檔案在 `personas/`，附加於 `buddy-prompt.txt` 之後。六個視角共用同一次審查，不是六個 agent 同時發言。

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
| `BUDDY_PERSONA` | 未設定 | 強制 `general`、`jeff`、`beck`、`fowler`、`linus`、`lamport` 或 `carmack`；優先於浮動視窗與專科路由 |
| `BUDDY_SPRITE_PATH` | 內建 spritesheet | 自訂透明背景 spritesheet |
| `BUDDY_SHADOW_EVALUATION_DAYS` | `7` | 成本策略 shadow 評估天數 |
| `BUDDY_SHADOW_TARGET_CALLS` | `300` | 評估用目標審查次數 |

審查文案與規則：`~/.claude/scripts/buddy/buddy-prompt.txt`。

### 成本遙測與 shadow 評估

安裝後首次審查起算固定 7 天：可能省成本的略過只標註與量測，實際仍每次呼叫模型。第 7 天後的下一次審查寫入 `~/.claude/buddy/shadow-evaluation.md` 並顯示一次通知；不足 300 次標 `insufficient_samples`，不自動延長，也不自動啟用略過。

每次審查會把不含對話內容的 metadata 追加到 `~/.claude/buddy/review-telemetry.jsonl`，包括階段、primary lens、effective lens、專科 trigger 與路由來源。反應 log 的 `persona` 代表 effective lens，並帶有同一套路由 metadata。若要重開評估，刪除 `shadow-evaluation.json`、`shadow-evaluation.md`、`review-telemetry.jsonl`。

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

內建 Rook spritesheet 為兩列、每列六格：第一列安靜待機，第二列收到審查結果時短暫反應。浮窗外圍的低彩度底色跟隨 badge 顯示的 effective lens；專科單次接手會換底色，但不改寫持久設定的生命週期階段。Rook 本身維持石墨黑。

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
| 提示與路由 | `buddy-prompt.txt`、`personas/*.txt`、`lens_router.py` |
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
| `~/.claude/buddy/config.json` | 視窗保存的生命週期階段 |
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

參考 [`cold-eyes-reviewer`](https://github.com/shihchengwei-lab/cold-eyes-reviewer) 的 hook 與 CLI 模式，並從 Claude Code 舊 Buddy／Cinder companion 用法重寫。`buddy_screenshot.png`、`cinder_screenshot.png` 為歷史素材；現行夥伴為渡鴉 Rook，浮窗底色會跟隨實際使用的 review lens。

## 授權

MIT
