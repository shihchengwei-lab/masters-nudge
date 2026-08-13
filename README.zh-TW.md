# Masters’ Nudge

繁體中文 | [English](README.md)

**在長任務裡，替 Claude Code 或 Codex CLI 加一個不同的聲音。**

![同一個 checkpoint 經六種 Masters’ Nudge 工作流視角呈現的實際浮窗](docs/images/masters-nudge-six-lenses-hero.png)

*同一份證據、同一個模型，只更換 lens。圖中是未改字的 reviewer 輸出，
由六個真實 Tk 浮窗呈現；代表句依完整性與 lens 對齊挑選。控制測試中，
六個 lens 有五個能穩定分流。[查看評估與選圖細節。](evaluation/results/lens-differentiation-v2-20260813/LENS_DIFFERENTIATION_RESULT.md)*

## 簡介

coding agent 做得越久，前面的選擇越容易一路影響後面的工作。

方向對了，工作會越來越順；方向偏了，它也可能沿著同一條路繼續補、繼續繞，直到看起來完成，卻留下原本沒看見的問題。

Masters’ Nudge 會在幾個關鍵時刻，請另一個模型看一小段工作如何推進，再留下一個值得重看下一步的理由。證據裡沒有可靠的新角度，就保持安靜。

主 agent 照常工作與決定；Masters’ Nudge 只在旁邊加一個不同的聲音。目前支援 Claude Code 與 Codex CLI 0.147+。

## 為什麼只說一句？

每次提醒最多 52 個字，只指出一個具體的工作流張力或問題。

可能是某個假設從未被重看、回饋停得太早、範圍越做越大、事件順序不穩，或完成宣告已經跑在證據前面。

這 52 個字的重點，不是多給一份答案或 code review，而是讓同一段工作流被換個角度看一次。主 agent 可以在繼續之前，重新看一眼眼前的選擇。

## 為什麼換一個模型？

同一個模型繼續自己的工作時，容易把原來的假設一起帶進下一個決定。

Reviewer 預設使用 OpenAI `gpt-5.6-sol`，也可改用 Anthropic `claude -p`。主 agent 是 Anthropic 時，這同時跨了模型廠商；主 agent 是 Codex 時，請自行決定 reviewer provider，此時分離的是上下文與角色，不保證跨模型家族。

第二個模型只會收到一小段當下資料，也只能根據這些內容提出提醒。程式、測試與工具結果可以當證據錨點，但真正檢視的是工作如何被框定、排序、控制範圍、取得回饋、驗證與宣告完成。看不出有用提醒，就不出聲。

## 它什麼時候加入？

```
Coding agent 正常工作
    │ 工具失敗 / 測試失敗 / 首次大變更
    ├─► 立即檢查一次 → 只交給主 agent
    │
    │ 這一輪結束
    └─► 背景檢查一次
              ├─ 下次對話時交給主 agent
              └─ 顯示在浮動視窗
```

| 時機 | 再看一眼的原因 | 誰會看到 |
|---|---|---|
| 工具失敗 | 可能只處理了表面症狀 | 主 agent |
| 測試失敗 | 修法可能開始繞遠路 | 主 agent |
| 變更首次超過約 80 行 | 工作範圍可能正在變大 | 主 agent |
| 一輪工作結束 | 確認結果是否真的完成 | 主 agent、浮動視窗 |

途中檢查只在命中前三種情況時呼叫模型，可能讓主 agent 多等最多約 15 秒。回合末檢查在背景執行，不會擋住剛完成的工作。Claude Code 以 `PostToolUseFailure` 回報失敗；Codex adapter 會在收到 `PostToolUse` 時辨識結構化的非零 exit code 與 failure status。但實測 Windows 0.147.0 不會為非零 Bash 結果發出該事件，因此該版的即時失敗檢查是 best-effort，並以 Stop review 兜底。

回合末短評會在你下次送出訊息時交給主 agent。浮動視窗會讀取兩種 host 的 namespaced log，是使用者直接看短評的管道。

輸出要嘛一則 finding，要嘛靜默；finding 去除 markdown 與套話後，硬上限為 52 字。

## 適用對象

**適用**：使用 Claude Code 或 Codex CLI，且可接受審查時帶出的內容（你的 prompt、工具輸出、檔案片段、錯誤訊息等）離開本機、送到外部模型 API（**預設 OpenAI**；可改 Anthropic）。

**不適用**：對話或程式碼不得外送的環境。細節見 [隱私](#隱私)。不符合就不要裝。

成本上：預設**每個回合結束都會**呼叫一次審查模型；途中僅在命中錯誤／測不過／首次大變更時再呼叫。繁忙時 token 會累積。

## 安裝

### 前置

- Claude Code、Codex CLI 0.147+，或兩者
- 可呼叫的 reviewer CLI：預設為 [Codex CLI](https://github.com/openai/codex)，或設 `MASTERS_NUDGE_PROVIDER=anthropic` 使用 `claude -p`
- Python 3.10+

### 步驟

1. 安裝共用 runtime 與 adapter；兩種 installer 都不會修改 host 設定：

```bash
bash install.sh --all
```

Windows PowerShell：

```powershell
.\install.ps1 -HostName all
```

只裝單一 host 可用 `--claude` / `--codex`，或 `-HostName claude` / `codex`。共用 runtime 在 `~/.masters-nudge/runtime/`；為了既有安裝相容，Claude 仍保留 `~/.claude/scripts/buddy/` target。

2. 依使用的 host 啟用 hooks：

   - **Claude Code：**把 [`settings-snippet.json`](settings-snippet.json) 的 `hooks` 合併進 `~/.claude/settings.json`。
   - **Codex CLI 0.147+：**把 [`codex-hooks-snippet.json`](codex-hooks-snippet.json) 的 `hooks` 合併進 `~/.codex/hooks.json`，保留既有 hooks，再以 `/hooks` 檢查並信任。自動化環境也有 `--dangerously-bypass-hook-trust`，只能在先看過命令後使用。詳見 [官方 hooks 文件](https://learn.chatgpt.com/docs/hooks)。

兩者都不要整檔覆蓋。

3. （可選）開浮動視窗，否則你在 UI 上幾乎看不到回合末短評：

```bash
pip install Pillow
```

- **Windows：** 雙擊 `~/.claude/scripts/buddy/start_buddy_window.bat`
- **macOS / Linux：** `python3 ~/.claude/scripts/buddy/buddy_window.py &`

關閉視窗不會停用 hooks。

### 如何確認有在跑

- 觸發一次測試失敗，或完成一輪工作：命中途中審查時 agent 可能多等數秒；回合末 finding 應在下次 prompt 注入。
- 新 log：`~/.masters-nudge/data/<host>--<session_id>.log`；錯誤：`~/.masters-nudge/data/error.log`。
- 若完全沒有 log：多半是 hooks 未合併／未信任，或 reviewer CLI／provider 呼叫失敗。

## 濾鏡：不同階段，看工作流的不同地方

專案在不同階段，容易忽略的事情也不同。

設計時，要留意資料、狀態與責任放在哪裡；實作時，要留意是否越做越多；程式開始成長後，要留意下一次修改會不會變難；準備交付時，則重新看看哪些複雜度其實不需要存在。

| 階段 | 視角 | 它會先問 |
|---|---|---|
| Design | Jeff Dean（`jeff`） | 資料、狀態與責任是不是放錯地方？ |
| Build | Kent Beck（`beck`） | 是否已經做超過現在需要的範圍？ |
| Evolve | Martin Fowler（`fowler`） | 這個結構會不會讓下次修改更困難？ |
| Review | Linus Torvalds（`linus`） | 哪些多餘層次其實不需要存在？ |

另外兩個視角會在出現明確訊號時，暫時加入一次：

- 遇到重試、冪等、競態、重複處理、先後順序或部分失敗時，改從 Leslie Lamport（`lamport`）的角度檢查。
- 遇到 profiler、benchmark，或連到延遲、吞吐、配置、複製、I/O、hot path 的實測數字時，改從 John Carmack（`carmack`）的角度檢查。

兩者同時符合時，先看正確性風險較高的 Lamport 視角。只出現 `async`、`cache`、`performance` 或 `latency` 其中一個詞，不足以切換。

每個名字代表一組核心概念與關注面向。短評不會模仿本人，也不是增加一份 code review；技術細節只用來錨定值得重看的工作方式。

不論目前是哪個階段，只要眼前有破壞性操作、安全或授權風險、做偏需求，或完成宣告與可見證據明確矛盾，Masters’ Nudge 都會先踩煞車。

浮動視窗下拉會把階段寫入 `~/.masters-nudge/data/config.json`，下次審查生效；預設為 Build。下拉顯示選定的階段，彩色 badge 顯示上一則短評實際使用的視角。Lamport 或 Carmack 暫時加入時，badge 會改變，但下拉選擇不變。既有 `~/.claude/buddy/config.json` 會繼續讀取，直到新設定寫進 neutral data 目錄。

新設定檔格式為 `{"stage":"build"}`；合法階段是 `design`、`build`、`evolve`、`review`。General 是所有階段共用的工作流證據與踩煞車底座，不是可選濾鏡。

啟動 host 前設定 `MASTERS_NUDGE_PERSONA`（或舊 `BUDDY_PERSONA`）仍可強制指定 lens，且會停用專科切換。舊 persona 格式的設定仍可讀取：四個生命週期 lens 映射到對應階段；舊 General 設定回到預設 Build；舊 Lamport／Carmack 選擇會維持鎖定，直到使用者在視窗改選階段。

Lens 只改先重看工作流的哪個面向，不改證據門檻、模型呼叫次數、單則 Nudge 或字數上限。對應檔案在 `personas/`，附加於 `buddy-prompt.txt` 之後。六個視角共用同一次模型呼叫，不是六個 agent 同時發言。

<details>
<summary>各濾鏡補充</summary>

##### Jeff Dean — 系統因果與成本

> “As systems scale up, simply stamping out all sources of variability does not work.” — [Jeff Dean](https://research.google/pubs/achieving-rapid-response-times-in-large-online-services/)

機制對應哪個真實限制；沿資料流、延遲、狀態、失敗處理與維運成本追影響。不預設需要 Google 規模。

##### Linus Torvalds — 直接性與責任歸屬

> “Talk is cheap. Show me the code.” — [Linus Torvalds](https://groups.google.com/g/mlist.linux.kernel/c/pdl_7y9bPgk)

工作是否用包裝與間接層延後決定；目前還有沒有一條清楚的主路徑與負責者。取概念，不取語氣。

##### Martin Fowler — 知識邊界與安全變更

> “…to make it easier to understand and cheaper to modify without changing its observable behavior.” — [Martin Fowler](https://martinfowler.com/bliki/DefinitionOfRefactoring.html)

這次變更透露哪份知識應該放在哪裡，以及下次變更會有多貴；偏好小幅、保留行為的步驟。

##### Kent Beck — 回饋迴路與小步

> “You don’t always have to take tiny steps, but they are always an option.” — [Kent Beck](https://newsletter.kentbeck.com/p/first-one-then-many)

從目前假設走到有效回饋的最短路徑；停止條件已滿足後，工作是否仍在膨脹。

##### Leslie Lamport — 狀態、順序、失敗

> “A distributed system is one in which the failure of a computer you didn’t even know existed can render your own computer unusable.” — [Leslie Lamport](https://www.microsoft.com/en-us/research/publication/distribution/)

工作對狀態與事件順序做了哪些假設；重試、重複、延遲或部分失敗是否破壞承諾的不變條件。

##### John Carmack — 實際執行路徑

> “Sometimes, the elegant implementation is just a function. Not a method. Not a class. Not a framework. Just a function.” — [John Carmack](https://twitter.com/ID_AA_Carmack/status/53512300451201024)

實際執行了什麼、真正量到了什麼；目前路徑是在移除工作，還是只把工作換個地方做。

</details>

預設走 OpenAI，可讓 Anthropic 主 agent 與 reviewer 錯開模型家族；若主 agent 本身是 Codex，則仍是獨立 reviewer 呼叫，但不是跨廠商檢查。這是設計取捨，非正確率保證。

## 設定

`MASTERS_NUDGE_*` 是新命名空間；下列 `BUDDY_*` 都保留為既有安裝相容 alias。

| 環境變數 | 預設 | 作用 |
|---|---|---|
| `MASTERS_NUDGE_PROVIDER` / `BUDDY_PROVIDER` | `openai` | `openai`（`codex exec`）或 `anthropic`（`claude -p`） |
| `MASTERS_NUDGE_MODEL` / `BUDDY_MODEL` | `gpt-5.6-sol` / `sonnet` | 傳給選定 CLI 的模型名 |
| `MASTERS_NUDGE_TIMEOUT` / `BUDDY_TIMEOUT` | `60` | 回合末模型呼叫逾時（秒） |
| `MASTERS_NUDGE_CHECKPOINT_TIMEOUT` / `BUDDY_CHECKPOINT_TIMEOUT` | `15` | 途中審查同步等待上限（秒） |
| `MASTERS_NUDGE_DATA_DIR` | `~/.masters-nudge/data` | 新 log、state、config 與無內容 telemetry |
| `MASTERS_NUDGE_RUNTIME_DIR` | `~/.masters-nudge/runtime` | 共用安裝 runtime |
| `MASTERS_NUDGE_PERSONA` / `BUDDY_PERSONA` | 未設定 | 強制 `jeff`、`beck`、`fowler`、`linus`、`lamport` 或 `carmack`；優先於浮動視窗與專科路由 |
| `MASTERS_NUDGE_SPRITE_PATH` / `BUDDY_SPRITE_PATH` | 內建 spritesheet | 自訂透明背景 spritesheet |
| `MASTERS_NUDGE_SHADOW_EVALUATION_DAYS` / `BUDDY_SHADOW_EVALUATION_DAYS` | `7` | 成本策略 shadow 評估天數 |
| `MASTERS_NUDGE_SHADOW_TARGET_CALLS` / `BUDDY_SHADOW_TARGET_CALLS` | `300` | 評估用目標審查次數 |
| `BUDDY_CLAUDE_DIR` | 未設定 | 舊路徑相容 override；明確設定時保留原 Claude data 路徑 |

審查文案與規則：`~/.masters-nudge/runtime/buddy-prompt.txt`；Claude 相容副本仍在 `~/.claude/scripts/buddy/`。

### 成本遙測與 shadow 評估

安裝後首次審查起算固定 7 天：可能省成本的略過只標註與量測，實際仍每次呼叫模型。第 7 天後的下一次審查寫入 `~/.masters-nudge/data/shadow-evaluation.md` 並顯示一次通知；不足 300 次標 `insufficient_samples`，不自動延長，也不自動啟用略過。

每次審查會把不含對話內容的 metadata 追加到 `~/.masters-nudge/data/review-telemetry.jsonl`，包括 host、turn、階段、primary lens、effective lens、專科 trigger 與路由來源。反應 log 的 `persona` 代表 effective lens，並帶有同一套路由 metadata。若要重開評估，刪除 `shadow-evaluation.json`、`shadow-evaluation.md`、`review-telemetry.jsonl`。

## 隱私

**會把對話與工具事件送至外部模型廠商。** 每次回合末審查，以及每次命中的途中審查，各為一次外送。內容可能包含：

1. 最新使用者 prompt（上限 2000 字；長文保留頭尾，中段標截斷）
2. 途中：觸發的工具事件（≤3000）與最近 agent 上下文（≤1200）
3. 回合末：最後宣告（≤2500）與當輪工具結果（≤2000；可能含讀檔內容、指令輸出、錯誤、diff）。Claude 缺證據時可退回 bounded transcript；Codex 不解析 transcript，而使用 PostToolUse 時累積的 bounded journal
4. 可選的 agentcam 摘錄（合計 ≤2000）
5. 本 session 最近最多 3 則短評（避免重複）
6. 審查用 system prompt 與選定濾鏡檔（規則，非你的專案原文）

預設 `MASTERS_NUDGE_PROVIDER=openai` 不論 host 都會把證據封包送往 OpenAI。中途切換 provider 時，先前短評可能作為「最近幾則」送進新廠商。反應、任務錨點與 bounded tool journal 會以明文存在 `~/.masters-nudge/data/`。舊 `~/.claude/buddy/` log 與 config 仍可讀，但不會自動移動或刪除。

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

Codex 會把 hook payload 正規化成 prompt-submitted、tool-completed、
turn-stopped 事件。Claude 相容 hooks 會轉換 checkpoint 工具事件；其餘路徑
則直接更新 turn state，或建立同一份 `ReviewRequest` 契約。兩種 host 的實際
審查都直接進入 `ReviewCore`，不再經過 host 專用的轉交 callback。

共用 core 負責 lens 路由、prompt 組合、provider 呼叫、42 字回答閉環目標／
52 字硬上限、結構化輸出處理、最近短評上下文、反應保存與 telemetry。Host
adapter 負責原生事件解析、證據擷取、turn journal、checkpoint 去重與 delivery
state；共用 evidence helper 建立小型、有標籤的證據封包，而不是固定重送整段
對話。輸出契約見 `reaction-schema.json`。

新 runtime 與 data 路徑已與 host 解耦。`buddy.py`、`BUDDY_*`、`~/.claude/buddy/` 仍作為既有安裝 compatibility layer；舊資料原地讀取，不會自動搬移或刪除。產品名稱為 Masters’ Nudge。

| 元件 | 路徑 |
|---|---|
| 安裝 | `install.sh` 或 `install.ps1` → `~/.masters-nudge/runtime/` |
| Hooks 片段 | Claude `settings-snippet.json`；Codex `codex-hooks-snippet.json` |
| 共用 core | `masters_nudge/core.py`、`contracts.py`、`providers.py` |
| 架構說明 | `docs/phase-c-architecture.md` |
| Codex adapter | `hook_entry.py`、`masters_nudge/codex_adapter.py` |
| Claude 相容 adapter | `checkpoint.py`、`buddy.py`、`inject.py` 與 shell wrappers |
| 證據封包 | `source_context.py` |
| 提示與路由 | `buddy-prompt.txt`、`personas/*.txt`、`lens_router.py` |
| 輸出契約 | `reaction-schema.json` |
| 浮動 UI | `buddy_window.py`、`start_buddy_window.bat` |
| 測試 | `python -m unittest discover -v` |
| 路線圖 | `ROADMAP.md` |
| 歷史筆記 | `BUDDY_FORENSICS_REPORT.md` |

Runtime：

| 路徑 | 用途 |
|---|---|
| `~/.masters-nudge/data/<host>--<session_id>.log` | 反應 JSONL |
| `~/.masters-nudge/data/<host>--<session_id>.turn.json` | 任務錨點與 bounded tool journal |
| `~/.masters-nudge/data/<host>--<session_id>.delivery.json` | 注入讀取指標 |
| `~/.masters-nudge/data/config.json` | 視窗保存的生命週期階段 |
| `~/.masters-nudge/data/<host>--<session_id>.checkpoints/` | 途中審查去重 |
| `~/.masters-nudge/data/error.log` | 錯誤 log |
| `~/.claude/buddy/*` | 唯讀 legacy compatibility；明確設定 `BUDDY_CLAUDE_DIR` 時除外 |

## 已知限制

- 命中途中審查可能讓 agent 暫停最多 `MASTERS_NUDGE_CHECKPOINT_TIMEOUT` / `BUDDY_CHECKPOINT_TIMEOUT`（預設 15 秒）。
- 測試失敗啟發式可能漏判少見 runner；大變更依 Git 與未追蹤文字檔，binary 不計，session 內約超過 80 行後觸發一次。
- 簡短 follow-up（如「繼續」）會取代先前詳細 prompt 作為任務錨點。
- Claude 當輪工具證據仍可能受 transcript 寫入時機影響；Codex 改在每次 PostToolUse 累積 journal，每輪上限 8,000 字，不依賴 transcript 格式。
- 實測 Windows Codex CLI 0.147.0 對非零 Bash 結果沒有發出 `PostToolUse`，與現行文件不一致；該失敗不會進 journal，只能由 Stop review 接手。詳見 [live smoke 結果](evaluation/results/phase-c-codex-smoke-20260813/SMOKE_RESULT.md)。
- 同一版也會略過原生 `async: true` hook，因此 Codex Stop 使用快速 detached-worker shim；待最低支援版本實證支援 native async 後可移除。
- 若你在回合末審查完成前就送下一則訊息，該則短評會晚一輪才注入。
- 無時間 cooldown；回合末每次都呼叫模型。成本略過目前僅 shadow。
- 其他 hook 若無 `MASTERS_NUDGE_ACTIVE` / `BUDDY_ACTIVE` 類防護，仍可能與 `claude`／`codex` 形成迴圈。

## 起源

參考 [`cold-eyes-reviewer`](https://github.com/shihchengwei-lab/cold-eyes-reviewer) 的 hook 與 CLI 模式，並從 Claude Code 舊 Buddy／Cinder companion 用法重寫。`buddy_screenshot.png`、`cinder_screenshot.png` 為歷史素材；現行夥伴為渡鴉 Rook，浮窗底色會跟隨實際使用的 review lens。

## 授權

MIT
