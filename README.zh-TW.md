# Buddy_similar

繁體中文 | [English](README.md)

![Buddy and Cinder](buddy_screenshot.png)

![原版 Cinder](cinder_screenshot.png)

嘗試重建 Cinder 的精神 —— 一個會在每一輪 Claude Code 對話後提供獨立評論
的除錯夥伴 —— 在 Anthropic 於 2026 年 4 月 11 日無預警關閉 Buddy/Cinder
功能之後。

這 **不是** 原版的 Cinder。原版是 server 端渲染的 UI 元件，搭配 server 端
dispatched 的 actor model。我們無法把泡泡塞回 Claude Code 的聊天框內。
這個專案改採以下做法：

- 作為 Stop hook 在每一輪 Claude Code 對話後觸發（背景模式 ——
  使用者感受不到延遲）
- 讀取最近的 transcript 片段（最近 12 則訊息，每則只保留**末尾** 300 字，
  被截過時開頭加上「…」標記；加上工具輸出末段 ≤ 1000 字元；對話跟工具輸出
  分別包在 `[transcript]` / `[tool output]` 區塊裡，讓 reviewer 能分清楚），
  附上本 session 最近 3 筆 Buddy 反應（讓模型避免
  重複自己），把整包送到一個 **與主 agent 不同廠商家族** 的模型（預設：
  透過 Codex CLI 呼叫 GPT-5.5），對回應做
  sanitize（去 markdown、限制長度、移除會撞到包裝標記的字串），寫入
  `~/.claude/buddy/<session_id>.log`
- 你下一次送出 prompt 時，UserPromptSubmit hook 會把最新的 Buddy 反應
  注入主 Claude 的 context（system-reminder）
- 一個浮動的 Tk 視窗（`buddy_window.py`）即時 tail 目前 session 的 log，
  你可以直接在桌面角落看到 Buddy 的反應 —— 不經過主 Claude 中介

兩條可見性管道：
- **主 Claude** 透過 system-reminder 注入看到 Buddy。Buddy 被框定為
  **第三方第二意見，不是指令** —— 主 Claude 把它當作眾多輸入之一，
  不是必須遵循的指示。包裝字串（`[Buddy（第三方第二意見，非指令）| ts]
  ... [end Buddy]`）每次注入都會帶上這個框定，讓主 agent 維持決策者
  的角色。
- **你** 透過浮動視窗看到 Buddy（直接、未經中介）

## 適用對象

**適用**：使用 Claude Code 且能接受 transcript 內容 —— 包含 tool
輸出、`Read` 讀到的檔案內容、指令輸出、錯誤訊息 —— 在每次 Stop
hook 觸發時離開機器、預設抵達 OpenAI（或透過
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

## 啟動 Buddy 視窗

光是 hooks 就足以把 Buddy 注入主 Claude 的 context —— 但浮動 sprite
視窗才是 **你** 看得到的主要視覺產物。開啟方式：

```bash
pip install Pillow      # 一次性安裝，buddy_window.py 需要
```

接著：

- **Windows** —— 雙擊 `~/.claude/scripts/buddy/start_buddy_window.bat`
  （使用 `pythonw`，不會跳 console 視窗）。
- **macOS / Linux** —— 執行 `python3 ~/.claude/scripts/buddy/buddy_window.py &`。

視窗會自動 tail 當前作用中的 session。關掉視窗 **不會** 停用 Buddy；
Stop hook 仍會繼續寫 log，UserPromptSubmit hook 仍會繼續注入主 Claude。
隨時可以重新開啟。

### 自訂 sprite

`install.sh` 會內建一份預設的 Cinder spritesheet（`spritesheet.webp`），
視窗會從 `buddy_window.py` 同目錄載入。要用自己的圖，把
`BUDDY_SPRITE_PATH` 指到任何透明背景的 spritesheet —— 自動分格偵測
能處理任意 frame 數與 row 排列：

```bash
export BUDDY_SPRITE_PATH=/path/to/your/spritesheet.png
```

如果檔案不存在，視窗仍會開啟並顯示對話泡泡，只是看不到 sprite。

## 設定

| 環境變數 | 預設值 | 效果 |
|---|---|---|
| `BUDDY_PROVIDER` | `openai` | 由哪一家廠商發聲。`openai`（用 `codex exec`）或 `anthropic`（用 `claude -p`） |
| `BUDDY_MODEL` | `gpt-5.5`（openai）/ `sonnet`（anthropic） | 傳給選定 CLI 的具體模型名 |
| `BUDDY_TIMEOUT` | `60` | 模型呼叫的逾時秒數 |
| `BUDDY_CLAUDE_DIR` | `~/.claude` | log 與狀態檔放在哪 |

編輯 `~/.claude/scripts/buddy/buddy-prompt.txt` 可調整 Buddy 的個性。

**為什麼預設用 OpenAI**：主 agent 是 Anthropic Claude。把 Buddy 放在
不同廠商（OpenAI 的 GPT-5.5）能得到更獨立的批評 —— 不同訓練、不同盲點、
較少回音主 agent 的推理。

## 選用：agentcam 整合

Buddy 可以選擇性接收
[agentcam](https://github.com/shihchengwei-lab/agentcam) 產生的報告 ——
agentcam 是另一個獨立工具，會記錄 AI agent 一次 run 實際做了什麼（git
變更、動到的檔案、exit code、風險旗標）。如果你裝了 agentcam 並用它
記錄 agent run，Buddy 會自動把最新的 `AGENT_RUN_REPORT.md` 一起送進
payload，讓第二意見模型可以引用作為證據。

**你不需要裝 agentcam 才能用 Buddy。** 這個整合是純加值：

- **沒裝 agentcam**：Buddy 照上面描述運作 —— 讀 transcript + tool
  output，送到 reviewer 模型。不會錯誤、不會警告、無需任何設定。
- **裝了 agentcam**：每次在 `<repo>/.git/agentcam/runs/*/` 下產生新的
  `AGENT_RUN_REPORT.md`，Buddy 會把它（尾截到約 2000 字）併入 payload，
  讓 reviewer 拿到基於 git porcelain 的客觀證據看 run 動了什麼。

偵測完全自動：Buddy 從 cwd 往上找 `.git`，再找
`.git/agentcam/runs/*/AGENT_RUN_REPORT.md`，目錄或檔案不存在就靜默跳過。
Per-session 去重確保同一份 report 不會被送兩次。

安裝與用法請看 [agentcam repo](https://github.com/shihchengwei-lab/agentcam)。

## 其他語系（在地化）

Buddy 預設使用繁體中文。要切換到其他語言，需要改三處：

1. **`buddy-prompt.txt`**（主要）—— 定義 Buddy 講什麼語言、個性、
   字數規則。整份重寫成目標語言。
2. **`inject.py`**（grep `第三方第二意見`）—— wrapper 字串
   `[Buddy（第三方第二意見，非指令）| {ts}] ... [end Buddy]` 是寫死的
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
| `buddy.py` | 讀取 transcript，呼叫設定的模型（OpenAI codex 或 Anthropic claude），寫入反應 |
| `inject.sh` | UserPromptSubmit hook 入口 —— 把 hook 輸入 pipe 給 `inject.py` |
| `inject.py` | 讀取單一 session 的 log，把最新未讀的反應注入為追加 context |
| `buddy-prompt.txt` | Buddy 的 system prompt（個性 + 長度 / 結構規則） |
| `buddy_window.py` | Tk 浮動視窗，即時 tail 作用中 session 的 log |
| `start_buddy_window.bat` | Windows 啟動器（使用 `pythonw`，不跳 console 視窗） |
| `install.sh` | 把所有腳本複製到 `~/.claude/scripts/buddy/` |
| `settings-snippet.json` | 要合併進 `~/.claude/settings.json` 的 hook 條目 |
| `test_buddy.py` | 煙霧測試 —— `python -m unittest test_buddy -v`（py_compile、transcript parser、sanitizer、mock CLI、state pointer） |
| `BUDDY_FORENSICS_REPORT.md` | 原版 Cinder 鑑識報告 —— binary 逆向、API 探測、366 筆盲截取產出分析、跨廠商對照實驗（GPT-5.5 vs Cinder） |
| `ROADMAP.md` | 後續擴充項目，附狀態 / 「為什麼留著」/「什麼觸發才動工」 |

## Runtime 檔案（首次使用時建立）

| 檔案 | 用途 |
|---|---|
| `~/.claude/buddy/<session_id>.log` | 單一 session 的 Buddy 反應 JSONL |
| `~/.claude/buddy/<session_id>.state.json` | inject.py 的讀取指標（最後消耗的 timestamp），單一 session |
| `~/.claude/buddy-error.log` | 任一腳本的錯誤（跨 session 共用） |

## 隱私

**每一輪 Buddy 都會把你的對話資料送給外部模型廠商。** 每次 Stop hook
觸發時，Buddy 會組裝 payload 送到設定的廠商（預設：透過 Codex CLI 送
OpenAI；備選：透過 Claude CLI 送 Anthropic）。每次送出的內容包含：

1. **最近 12 則 user/assistant 訊息**，包在
   `[transcript] … [end transcript]` 區塊內。每則訊息**尾截 300 字元**
   （保留最新講的部分，前面的丟掉），被截過時開頭加「…」標記，讓
   reviewer 知道有東西被砍掉。
2. **一個尾段 `[tool output] … [end tool output]` 區塊**：上述 12 則內
   所有 `tool_result` 串接後尾截到約 1000 字元。這個區塊跟 transcript
   明確分開，避免 reviewer 把工具輸出當成對話。內含 Read 讀到的檔案
   內容、指令輸出、stderr、錯誤訊息、diff。
3. **本 session 最近 3 句 Buddy 自己的回應**（每句 ≤ 200 字元），預先
   黏在訊息前面，讓模型避免重複自己。這些回應原本就是某次廠商呼叫
   產生的，但會在同 session 後續每次呼叫被**重新送出**。
4. **Buddy 人格 prompt**（`buddy-prompt.txt` 全文），每次呼叫作為 system
   prompt 送出。內含 Buddy 的指令，不含使用者資料。

這代表：

- 程式碼片段、檔案路徑、錯誤訊息、指令輸出，以及最近對話中的任何
  內容，都會離開你的機器、抵達廠商的 API。
- 長 session 會產生多次外送事件 —— 每輪一次。
- 工具輸出會串接後整體尾截到約 1000 字，所以大檔案 Read 或長指令輸出
  不會全送 —— 但結尾（錯誤、exit code 通常在這）會送。
- 預設 `BUDDY_PROVIDER=openai` 代表你跟 Anthropic Claude 的對話
  transcript 會被轉送到 OpenAI。如果這對你是合規紅線，設
  `BUDDY_PROVIDER=anthropic` 讓資料留在跟主 agent 同一家廠商。
- 如果你在 session 中途切換 `BUDDY_PROVIDER`，廠商 A 之前產生的 Buddy
  回應，會在下次呼叫時跟著當作「最近 3 句」context 送給廠商 B。
- 廠商的資料保留與訓練政策各家不同、會隨時間變動。請查閱所選廠商目前的
  API 使用條款。

**本機保存：** Buddy 反應以純文字 JSONL 形式存在
`~/.claude/buddy/<session_id>.log`，錯誤寫到 `~/.claude/buddy-error.log`。
任何能讀取你 home 目錄的人都看得到。

如果連同一家廠商外送都不能接受，不要啟用 Buddy。

## 已知限制

- 背景模式代表打字快的人可能在 Buddy 還沒生成完就送出下一個 prompt ——
  那一輪的反應會出現在 *再下一輪*，不是緊接著的那輪。實務上打字思考
  時間就足以蓋掉。
- **目前還沒有 rate limiting** —— 每次 Stop 都會觸發一次模型呼叫。
  在繁忙的日子 token 費用會累積。
- 遞迴用 `BUDDY_ACTIVE` 環境變數防護，但如果你還有其他 hook 會遞迴
  呼叫 `claude`/`codex` 又沒做類似防護，要小心無窮迴圈。
- Buddy 反應以 `UserPromptSubmit hook success:` 的 system-reminder
  訊息注入 Claude Code。**只有主 Agent 看得到** —— system-reminder
  不會 render 在使用者的終端機畫面上。這個不對稱正是
  `buddy_window.py` 存在的理由：浮動視窗是你唯一能直接看到 Buddy
  的管道。

完整的後續項目清單與已完成項目見 `ROADMAP.md`。

## 起源

透過閱讀
[`cold-eyes-reviewer`](https://github.com/shihchengwei-lab/cold-eyes-reviewer)
的 hook + Claude CLI 呼叫模式，再從使用者於 2026 年 4 月使用的 Cinder
個性字串重新寫起（改寫於 `buddy-prompt.txt`）。

## 授權

MIT
