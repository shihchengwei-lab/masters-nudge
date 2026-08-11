# Masters’ Nudge

繁體中文 | [English](README.md)

**六位大師，一句及時提醒。**

<img src="spritesheet.webp" alt="Masters’ Nudge 工程 checkpoint 提醒鈴動畫" width="720">

Masters’ Nudge 是長時間 coding agent 的第三方 side-review companion。
它可以選用 Jeff Dean、Linus Torvalds、Martin Fowler、Kent Beck、
Leslie Lamport 或 John Carmack 所代表的工程鏡頭，在值得介入的 checkpoint
只回傳一句有證據的 nudge。人名只用來引導注意力，不會模仿本人。

專案源自重建 Claude Code 舊 Buddy/Cinder companion 精神的實驗。為了不破壞
既有安裝，`buddy.py`、`BUDDY_*` 與 `~/.claude/buddy/` 等名稱保留作為相容層。

- 在長時間 agentic 工作途中執行同步、事件式的 checkpoint hook。工具失敗、
  測試失敗，或 working tree 首次超過 80 行變動時才呼叫 Masters’ Nudge。
  產生的一句 nudge 透過 `additionalContext` 直接送回主 Claude；不阻擋
  工具，也不等待使用者批准。
- 保留每輪結束後的 Stop hook（背景模式，使用者感受不到延遲），作為回合末
  補充審查。
- 改用小型、有標籤的證據封包，不再固定重送一段滾動 transcript。
  `UserPromptSubmit` 會把最新使用者 prompt 記成有上限的任務錨點，並記住
  當時的 transcript 位元組位置。Checkpoint 收到任務錨點、觸發事件與少量
  最近 Agent context；Stop 審查收到任務錨點、Agent 最終宣告、當輪工具
  結果，以及有的話經篩選的 agentcam 證據。長內容保留開頭與結尾，並明確
  標示中段已截斷。只有 Stop 拿不到最終宣告、工具或 agentcam 證據時，
  才退回舊的 transcript parser。封包另附本 session 最近 3 筆
  Masters’ Nudge 反應（讓模型避免重複自己），送到一個
  **與主 agent 不同廠商家族** 的
  模型（預設：透過 Codex CLI 呼叫 GPT-5.6 Sol），對回應做 sanitize（去
  markdown 與常見套話、硬上限 52 字、移除會撞到包裝標記的字串），寫入
  `~/.claude/buddy/<session_id>.log`
- 你下一次送出 prompt 時，UserPromptSubmit hook 會把最新的
  Masters’ Nudge 反應
  注入主 Claude 的 context（system-reminder）
- 一個浮動的 Tk 視窗（`buddy_window.py`）即時 tail 目前 session 的 log，
  你可以直接在桌面角落看到 Masters’ Nudge 的反應 —— 不經過主 Claude 中介

傳遞管道：
- **Checkpoint nudge** 只送給主 Claude，位置就在觸發事件的工具結果旁。
  不會寫入浮動視窗 log，也不會在使用者下一次 prompt 時重複注入。
- **Stop 反應** 沿用下一次 prompt 的 system-reminder 注入。
  Masters’ Nudge 被框定為
  **第三方第二意見，不是指令** —— 主 Claude 把它當作眾多輸入之一，
  不是必須遵循的指示。包裝字串（`[Masters’ Nudge（第三方第二意見，非指令）| ts]
  ... [end Masters’ Nudge]`）每次注入都會帶上這個框定，讓主 agent
  維持決策者
  的角色。
- **選用的使用者視圖：**浮動視窗只顯示 Stop 反應，不參與 checkpoint 傳遞。

## 適用對象

**適用**：使用 Claude Code 且能接受 transcript 內容 —— 包含 tool
輸出、`Read` 讀到的檔案內容、指令輸出、錯誤訊息 —— 在每次 Stop
與命中 checkpoint 時離開機器、預設抵達 OpenAI（或透過
`BUDDY_PROVIDER=anthropic` 改送 Anthropic）的人。

**不適用**：
- 對話內容不能離開機器的環境（公司機密程式碼、受監管行業、機密工作）。
- 不能接受檔案內容、指令輸出每輪抵達第三方 API 的人。

只要符合一條就不要安裝。完整資料流見下方 [隱私](#隱私) 一節。

## 安裝

```bash
bash install.sh
```

接著打開 `~/.claude/settings.json`，把 `settings-snippet.json` 裡的
`hooks` 區段合併進去。（snippet 內的 `_comment` 欄位會提醒你不要整份
取代 settings.json。）

## 選用：啟動 Masters’ Nudge 視窗

hooks 已足以把 Masters’ Nudge 注入主 Claude 的 context。浮動 sprite 是
回合末 Stop 反應的選用視圖；checkpoint nudge 只在 reviewer 與主 Agent
之間傳遞。開啟方式：

```bash
pip install Pillow      # 一次性安裝，buddy_window.py 需要
```

接著：

- **Windows** —— 雙擊 `~/.claude/scripts/buddy/start_buddy_window.bat`
  （使用 `pythonw`，不會跳 console 視窗）。
- **macOS / Linux** —— 執行 `python3 ~/.claude/scripts/buddy/buddy_window.py &`。

視窗會自動 tail 當前作用中的 session。關掉視窗 **不會** 停用 Masters’ Nudge；
Stop hook 仍會繼續寫 log，UserPromptSubmit hook 仍會繼續注入主 Claude。
隨時可以重新開啟。
較長的 nudge 會自動換行，視窗會從 150px 向上增高到最多 220px，讓 52 字
上限完整顯示，同時維持視窗底部位置。

### 自訂 sprite

`install.sh` 會內建 Masters’ Nudge 的工程 checkpoint 提醒鈴 spritesheet
（`spritesheet.webp`）。視窗會從 `buddy_window.py` 同目錄載入。要用自己的圖，把
`BUDDY_SPRITE_PATH` 指到任何透明背景的 spritesheet —— 自動分格偵測
能處理任意 frame 數與 row 排列：

```bash
export BUDDY_SPRITE_PATH=/path/to/your/spritesheet.png
```

Windows PowerShell 請使用：

```powershell
$env:BUDDY_SPRITE_PATH = "C:\path\to\your\spritesheet.png"
```

如果檔案不存在，視窗仍會開啟並顯示對話泡泡，只是看不到 sprite。

## 設定

| 環境變數 | 預設值 | 效果 |
|---|---|---|
| `BUDDY_PROVIDER` | `openai` | 由哪一家廠商發聲。`openai`（用 `codex exec`）或 `anthropic`（用 `claude -p`） |
| `BUDDY_MODEL` | `gpt-5.6-sol`（openai）/ `sonnet`（anthropic） | 傳給選定 CLI 的具體模型名；也可設定此變數固定使用其他支援的模型 |
| `BUDDY_TIMEOUT` | `60` | 模型呼叫的逾時秒數 |
| `BUDDY_CHECKPOINT_TIMEOUT` | `15` | 同步 checkpoint nudge 等待模型的最長秒數 |
| `BUDDY_CLAUDE_DIR` | `~/.claude` | log 與狀態檔放在哪 |
| `BUDDY_PERSONA` | 未設定 | 選用的工程審查鏡頭：`jeff`、`linus`、`fowler`、`beck`、`lamport` 或 `carmack` |

編輯 `~/.claude/scripts/buddy/buddy-prompt.txt` 可調整審查行為。

### 六種 master lenses

六位人物是工程注意力線索，不是人格模仿，也不是六個 Agent 同時開會。
`BUDDY_PERSONA` 每個 session 選一種 lens；不設定時使用通用、證據優先的審查。

啟動 Claude Code 前選一種 lens：

```bash
export BUDDY_PERSONA=linus
```

Windows PowerShell 請使用：

```powershell
$env:BUDDY_PERSONA = "linus"
```

| 值 | 靈感來源 | 優先注意 |
|---|---|---|
| `jeff` | Jeff Dean | 系統因果、資料流、state、scale 與維運成本 |
| `linus` | Linus Torvalds | 不必要 abstraction、indirection、wrapper 與不清楚的 ownership |
| `fowler` | Martin Fowler | design smell、變更成本、coupling 與不改行為的重構 |
| `beck` | Kent Beck | 小步驟、測試、當前範圍與滿足需求後停止 |
| `lamport` | Leslie Lamport | invariant、狀態轉換、事件順序、retry 與部分失敗 |
| `carmack` | John Carmack | 實際執行、資料搬運、量測與不必要工作 |

Masters’ Nudge 會把 `personas/` 中選定的檔案附加到共用 `buddy-prompt.txt`。
選定的 lens 只改變優先檢查的問題，不會取代原本的證據、旁觀者、單一
finding 與 52 字限制。每個 lens 含兩個極短選題例，把可見證據對應到優先
檢查的問題類型；選題例不是輸出範本。這些提示尚未證明能提升正確率或能力。

**為什麼預設用 OpenAI**：主 agent 是 Anthropic Claude。把 Masters’ Nudge 放在
不同廠商（OpenAI 的 GPT-5.6 Sol）能得到更獨立的批評 —— 不同訓練、不同盲點、
較少回音主 agent 的推理。

## 選用：agentcam 整合

Masters’ Nudge 可以選擇性接收
[agentcam](https://github.com/shihchengwei-lab/agentcam) 產生的報告 ——
agentcam 是另一個獨立工具，會記錄 AI agent 一次 run 實際做了什麼（git
變更、動到的檔案、exit code、風險旗標）。如果你裝了 agentcam 並用它
記錄 agent run，Masters’ Nudge 會自動把最新的 `AGENT_RUN_REPORT.md` 一起送進
payload，讓第二意見模型可以引用作為證據。

**你不需要裝 agentcam 才能用 Masters’ Nudge。** 這個整合是純加值：

- **沒裝 agentcam**：Masters’ Nudge 使用任務錨點、Agent 宣告與可用的工具證據。
  不會錯誤、不會警告、無需任何設定。
- **裝了 agentcam**：每次在 `<repo>/.git/agentcam/runs/*/` 下產生新的
  `AGENT_RUN_REPORT.md`，hook 會挑出 `Risk Flags`、`Changed Files`、
  exit code、測試與驗證段落；合計最多保留 2000 字的開頭與結尾。

偵測完全自動：hook 從 cwd 往上找 `.git`，再找
`.git/agentcam/runs/*/AGENT_RUN_REPORT.md`，目錄或檔案不存在就靜默跳過。
Per-session 去重確保同一份 report 不會被送兩次。

安裝與用法請看 [agentcam repo](https://github.com/shihchengwei-lab/agentcam)。

## 其他語系（在地化）

Masters’ Nudge 預設使用繁體中文。要切換到其他語言，需要改三處：

1. **`buddy-prompt.txt`**（主要）—— 定義 Masters’ Nudge 講什麼語言、
   審查行為與字數規則。整份重寫成目標語言。
2. **`inject.py`**（grep `第三方第二意見`）—— wrapper 字串
   `[Masters’ Nudge（第三方第二意見，非指令）| {ts}] ... [end Masters’ Nudge]` 是寫死的
   中文。如果只改 prompt 不改這裡，主 Claude 看到的會是「中文框定 +
   外語評論」的混搭，框定會破。同步翻譯 wrapper。
3. **`test_buddy.py`**（可選）—— 測試 fixture 用中文字串。不影響
   runtime，但如果想讓測試套件驗證 sanitizer 對新語系字元也正確，
   順手換掉。

`buddy.py` 的 sanitizer、log/state、hook 機制都是 language-neutral，
不用動。

## 檔案

| 檔案 | 用途 |
|---|---|
| `buddy.sh` | Stop hook 入口 —— 把 `buddy.py` 丟到背景執行後立即返回 |
| `buddy.py` | 組合 Stop 證據封包，呼叫設定的模型（OpenAI codex 或 Anthropic claude），寫入反應 |
| `checkpoint.sh` | 同步的 PostToolUse／PostToolUseFailure hook 入口 |
| `checkpoint.py` | 分類與去重 checkpoint，回傳不阻擋的 `additionalContext` nudge |
| `source_context.py` | 保存任務錨點，替 Stop 與 checkpoint 組合共用的有上限標籤證據封包 |
| `inject.sh` | UserPromptSubmit hook 入口 —— 把 hook 輸入 pipe 給 `inject.py` |
| `inject.py` | 記錄最新任務錨點，再把最新未讀的反應注入為追加 context |
| `buddy-prompt.txt` | Masters’ Nudge 的 system prompt（審查行為 + 長度 / 結構規則） |
| `personas/*.txt` | 由 `BUDDY_PERSONA` 選用的六種 master-lens overlay |
| `buddy_window.py` | 顯示工程 checkpoint 提醒鈴動畫的 Tk 浮動視窗 |
| `start_buddy_window.bat` | Windows 啟動器（使用 `pythonw`，不跳 console 視窗） |
| `install.sh` | 把所有腳本複製到 `~/.claude/scripts/buddy/` |
| `settings-snippet.json` | 要合併進 `~/.claude/settings.json` 的 hook 條目 |
| `test_buddy.py` | 單元與煙霧測試 —— `python -m unittest test_buddy -v`（來源封包、checkpoint 傳遞、transcript fallback、sanitizer、mock CLI、state pointer） |
| `BUDDY_FORENSICS_REPORT.md` | 原版 Cinder 鑑識報告 —— binary 逆向、API 探測、366 筆盲截取產出分析，以及歷史 GPT-5.5 vs Cinder 跨廠商對照實驗 |
| `ROADMAP.md` | 後續擴充項目，附狀態 / 「為什麼留著」/「什麼觸發才動工」 |

## Runtime 檔案（首次使用時建立）

| 檔案 | 用途 |
|---|---|
| `~/.claude/buddy/<session_id>.log` | 單一 session 的 Masters’ Nudge 反應 JSONL |
| `~/.claude/buddy/<session_id>.state.json` | inject.py 的讀取指標（最後消耗的 timestamp），單一 session |
| `~/.claude/buddy/<session_id>.source.json` | 最新的有上限任務錨點，以及送出 prompt 時的 transcript 位元組位置 |
| `~/.claude/buddy/<session_id>.checkpoints/` | 單一 session 的 checkpoint 去重指紋 |
| `~/.claude/buddy-error.log` | 任一腳本的錯誤（跨 session 共用） |

## 隱私

**Masters’ Nudge 會把對話與工具事件資料送給外部模型廠商。** 每次 Stop hook 會送出
一份 payload；命中的 checkpoint 會在同一輪工作途中再送一份（預設：透過
Codex CLI 送 OpenAI；備選：透過 Claude CLI 送 Anthropic）。內容包含：

1. **最新使用者 prompt 形成的任務錨點**：由 `UserPromptSubmit` 擷取，
   上限 2000 字。長 prompt 保留開頭與結尾，中間以
   `[…中段已截斷…]` 明確標示。
2. **Checkpoint 呼叫：**任務錨點、觸發工具事件（最多 3000 字），以及
   最近 Agent context（最多 1200 字）。事件可能包含工具輸入、失敗／結果
   文字或偵測到的 working-tree 變動行數。
3. **Stop 呼叫：**任務錨點、hook 直接提供的 `last_assistant_message`
   （最多 2500 字），以及保存在 prompt-time transcript 位元組位置之後的
   當輪 `tool_result` 證據（最多 2000 字）。工具證據可能包含 Read 讀到的
   檔案內容、指令輸出、stderr、錯誤訊息與 diff。若 Stop 拿不到最終宣告、
   工具或 agentcam 證據，hook 才退回舊的 6000 字 transcript 封包，以及
   最多 2000 字的 tool output。
4. **選用的 agentcam 證據：**風險、異動檔案、exit code、測試與驗證等
   指定段落，合計上限 2000 字。
5. **本 session 最近 3 句 Masters’ Nudge 回應**（每句 ≤ 200 字元），預先
   黏在訊息前面，讓模型避免重複自己。這些回應原本就是某次廠商呼叫
   產生的，但會在同 session 後續每次呼叫被**重新送出**。
6. **Masters’ Nudge prompt**（`buddy-prompt.txt` 加上選定的 `personas/*.txt`
   overlay，若有設定），每次呼叫作為 system prompt 送出。內含審查規則，
   不含使用者資料。

這代表：

- 最新使用者 prompt、程式碼片段、檔案路徑、錯誤訊息、指令輸出與經挑選的
  Agent 證據，都可能離開你的機器、抵達廠商的 API。
- 長 session 每完成一輪至少有一次外送，另外加上命中的 `error`、
  `test-fail`，以及首次 `large-diff` checkpoint。
- 長證據欄位會同時保留開頭與結尾，不再只留尾端；中段會被省略並明確
  標記，因此中段細節仍可能影響判斷。
- 有可靠 finding 時，每句反應以 48–52 個有效字為目標，並會在 log 寫入前
  與注入前硬截斷到 52 字，所以主 agent
  每輪看到的內容刻意短。
- 預設 `BUDDY_PROVIDER=openai` 代表你跟 Anthropic Claude 的對話
  transcript 會被轉送到 OpenAI。如果這對你是合規紅線，設
  `BUDDY_PROVIDER=anthropic` 讓資料留在跟主 agent 同一家廠商。
- 如果你在 session 中途切換 `BUDDY_PROVIDER`，廠商 A 之前產生的反應
  回應，會在下次呼叫時跟著當作「最近 3 句」context 送給廠商 B。
- 廠商的資料保留與訓練政策各家不同、會隨時間變動。請查閱所選廠商目前的
  API 使用條款。

**本機保存：** Masters’ Nudge 反應以純文字 JSONL 形式存在
`~/.claude/buddy/<session_id>.log`；最新任務錨點與 transcript 位置存在
`<session_id>.source.json`。錯誤寫到 `~/.claude/buddy-error.log`。任何能
讀取你 home 目錄的人都看得到。

如果連同一家廠商外送都不能接受，不要啟用 Masters’ Nudge。

## 已知限制

- Checkpoint hook 必須同步執行，主 Claude 才能在下一次模型請求前讀到 nudge。
  命中事件可能讓 Agent 暫停最多 `BUDDY_CHECKPOINT_TIMEOUT` 秒（預設 15 秒）；
  未命中的工具事件只做本機分類，不呼叫模型。
- 測試失敗偵測結合失敗的 shell 指令與輸出樣式；不常見的 test runner 可能
  漏判或分錯類。大型變更使用 Git numstat 加上未追蹤文字檔計數，在單一
  session 首次超過 80 行時觸發；binary 不列入。
- 任務錨點就是最新送出的 prompt。像「繼續」這種簡短追問會取代前一個較完整
  的 prompt，可能讓審查 context 變少。
- 當輪工具證據依賴 transcript 在 prompt-time 位元組位置之後完成寫入；延遲或
  非典型寫入可能讓工具證據不完整。Checkpoint 仍直接包含觸發事件，Stop
  通常仍有 hook 直接提供的 `last_assistant_message`。
- 長證據採開頭＋結尾截取，會刻意省略中段。舊 transcript 路徑只作 Stop
  fallback，不是一般的來源選擇方式。
- 背景模式代表打字快的人可能在 Masters’ Nudge 還沒生成完就送出下一個 prompt ——
  那一輪的反應會出現在 *再下一輪*，不是緊接著的那輪。實務上打字思考
  時間就足以蓋掉。
- 不使用時間 cooldown。每次 Stop 都會呼叫模型；checkpoint 採事件式觸發，
  完全相同的事件會去重。繁忙時 token 用量仍會累積。
- 遞迴用 `BUDDY_ACTIVE` 環境變數防護，但如果你還有其他 hook 會遞迴
  呼叫 `claude`/`codex` 又沒做類似防護，要小心無窮迴圈。
- Masters’ Nudge 反應以 `UserPromptSubmit hook success:` 的 system-reminder
  訊息注入 Claude Code。**只有主 Agent 看得到** —— system-reminder
  不會 render 在使用者的終端機畫面上。這個不對稱正是
  `buddy_window.py` 存在的理由：浮動視窗是你唯一能直接看到 Masters’ Nudge
  的管道。

完整的後續項目清單與已完成項目見 `ROADMAP.md`。

## 起源

專案起源是閱讀
[`cold-eyes-reviewer`](https://github.com/shihchengwei-lab/cold-eyes-reviewer)
的 hook + Claude CLI 呼叫模式，再從使用者於 2026 年 4 月使用的舊 Cinder
個性字串重新寫起。`buddy_screenshot.png` 與 `cinder_screenshot.png` 保留為
歷史對照；目前使用中的吉祥物已改為工程 checkpoint 提醒鈴。

## 授權

MIT
