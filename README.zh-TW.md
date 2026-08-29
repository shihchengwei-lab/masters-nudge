# Masters’ Nudge

繁體中文 | [English](README.md)

> **測試通過，只能確定行為；不能替 Agent 選擇設計。**

Masters’ Nudge 會在 Claude Code 或 Codex Agent 做下一個決定前，提供一則簡短、
有證據的工程取捨。Masters’ Nudge 不會代替 Agent 解題或阻止 Agent 繼續，而是提醒
主模型可能忽略的取捨。

## 看一次真實執行

![從測試通過到主模型下一個決策的一次實際執行](docs/assets/actual-nudge-run.png)

這不是介面示意圖，而是一次真實 CLI 執行的紀錄。程式原本就能運作，兩個測試也都
通過；但 `web_total` 和 `invoice_total` 各自保存同一份折扣公式。

Hook 把程式與測試結果交給 Provider。Provider 回傳一則 Nudge，建議讓折扣公式只有
一個擁有者。主模型判斷建議合理，實際抽出 `discounted_total`，再跑一次相同測試。

截圖只省略啟動警告、時間戳與重複輸出；Nudge、主模型判斷、程式差異與測試結果都
來自同一次執行。這只證明曾觀察到這次反應，不保證主模型每次都會採納 Nudge。

## 三個 Lens

Lens 就是觀察問題的角度。

| Lens | 關注什麼 |
|---|---|
| Simplicity | 不必要的複雜度，以及責任放錯地方 |
| Reliability | 事件換序、重試或中途失敗時，什麼仍必須成立 |
| Performance | 真實執行路徑上，哪些已量到的工作可以移除 |

Automatic 模式會依現有證據選擇 Lens。你也可以請 Agent 顯示選項，再固定使用其中
一個 Lens。手動選擇不會強迫 Provider 硬擠出 Nudge；證據不足時仍會保持沉默。

Lens Prompt 裡的專家姓名只是注意力提示，不表示 Provider 取得該人物的能力，也不會
憑空讓 Nudge 更準確。

## 如何運作

```text
任務與可觀察的工具結果
            ↓
      一個合適的 Lens
            ↓
   一則短 Nudge，或保持沉默
            ↓
      Agent 的下一段脈絡
```

每則 Nudge 都依目前情況生成，不是隨機抽一句罐頭訊息。Nudge 是獨立第二意見，
不是 review、評分、問題、完整解法，也不是一律要求多跑測試。

Claude Code 提供理想的 `PostToolBatch` 控制點：同一個模型步驟的工具結果都完成後，
下一步開始前才判斷。Codex 目前只有 `PostToolUse`，只是近似控制點；平行工具的結果
可能被分開判斷。缺少的 Codex 控制點已整理成
[`PostToolBatch` Issue 草稿](docs/codex-post-tool-batch-issue-draft.md)。

Provider 發生錯誤或超過固定 90 秒時，這次 Nudge 直接結束，主要 Agent 照常繼續。

## 隱私

### 哪些資料會離開電腦

選定的 Provider 會收到一份受長度限制的資料，可能包含：

- 目前任務，或從長任務找回的 Goal；
- 任務明確指定的本機檔案內容，只在任務開始時讀取一次；
- 最近且相關的修改、失敗、驗證與量測；
- 實際執行過、經長度限制的命令及結果。

Provider 不會收到完整對話、模型未公開的內部思考，也不會收到探索專案時碰到的無關
檔案。

Anthropic 與 OpenAI 是雲端 Provider，這份資料會離開你的電腦，並受該 Provider
的資料政策約束。如果資料不能離開電腦，請選本機 Ollama。Ollama 只允許連到本機
位址，使用已安裝的模型，也不會失敗後偷偷改送雲端。

## 本機紀錄

Masters’ Nudge 會把目前任務狀態與少量稽核紀錄存在
`~/.masters-nudge/data/`。稽核紀錄包含 Nudge 回傳給 Host 的時間、使用的 Lens 與
Nudge 內容。

這只能證明 Hook 已把 Nudge 回傳給 Claude Code 或 Codex，不能證明主模型真的讀到、
採納，或因為 Nudge 才採取後續行動。

每次開始新任務時，系統會刪除超過 30 天沒有更新的工作階段資料。Provider 與 Lens
偏好另外存在 `~/.masters-nudge/config.json`，會保留到你再次修改。

## 支援的 Provider

- Anthropic
- OpenAI
- 本機 Ollama

每次 Nudge 只會使用一個已選定的 Provider，不會在失敗後偷偷換另一個。

## 安裝

需求：

- 支援 Plugin 的 Claude Code 或 Codex CLI；
- Python 3.10+；
- 已登入 Anthropic 或 OpenAI 對應的 CLI，或已啟動 Ollama 並先安裝要使用的模型。

### Claude Code

```bash
claude plugin marketplace add shihchengwei-lab/masters-nudge
claude plugin install masters-nudge@masters-nudge --config python_command=python
```

若 `python` 不是 Python 3.10+，請把 `python_command` 改成 `python3` 或合適 Python
執行檔的絕對路徑；不要附加其他命令參數。

### Codex

```bash
codex plugin marketplace add shihchengwei-lab/masters-nudge
codex plugin add masters-nudge@masters-nudge
```

安裝後請開啟新任務。在 Codex 中開啟 `/hooks`，檢查並批准 Plugin 命令。

### 更新或移除

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

更新後請重新啟動 Host。解除安裝不會刪除既有本機資料。

## 直接請 Agent 操作

Hooks 會自動執行。需要手動操作時，直接用白話告訴 Agent：

- **「檢查 Masters’ Nudge 是否準備完成。」** 檢查 Python、Provider 存取、資料
  儲存與 Host Hooks，不會產生 Nudge。
- **「切換 Masters’ Nudge Lens。」** 用白話列出 Automatic、Simplicity、
  Reliability、Performance，再確認保存後的選擇。
- **「切換 Masters’ Nudge Provider。」** 列出 Anthropic、OpenAI、本機 Ollama；
  設定 Ollama 時會確認已安裝的模型與本機服務。
- **「顯示最近的 Masters’ Nudge 紀錄。」** 用白話解釋近期稽核紀錄。

Skills 會在背後呼叫只輸出 JSON 的命令，再把結果翻成白話。使用者不用修改環境變數、
記住確切名稱，也不用看懂原始 JSON。

## 開發

Repository 原始碼是唯一實作來源；版控中的 Plugin 套件由原始碼產生。

```bash
python -m unittest discover -v
python tools/build_plugin.py --check
```

授權：[MIT](LICENSE)
