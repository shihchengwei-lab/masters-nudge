# Masters’ Nudge

繁體中文 | [English](README.md)

> **在補丁式結構還容易改變時，就指出方向問題。**

Masters’ Nudge 會在 Claude Code 或 Codex Agent 做下一個決定前，提供一次獨立、唯讀的
結構介入。Provider 可以指出更好的責任邊界或既有 seam；如何實作與驗證仍由主模型決定。

## 看一次真實執行

![從測試通過到主模型下一個決策的一次實際執行](docs/assets/actual-nudge-run.png)

這不是介面示意圖，而是一次真實 CLI 執行的紀錄。程式原本就能運作，兩個測試也都
通過；但 `web_total` 和 `invoice_total` 各自保存同一份折扣公式。

Hook 把程式與測試結果交給 Provider。Provider 回傳一則 Nudge，建議讓折扣公式只有
一個擁有者。主模型判斷建議合理，實際抽出 `discounted_total`，再跑一次相同測試。

截圖只省略啟動警告、時間戳與重複輸出；Nudge、主模型判斷、程式差異與測試結果都
來自同一次執行。這只證明曾觀察到這次反應，不保證主模型每次都會採納 Nudge。

## 一次早期判斷

只有原生工具輸入最上層帶有明確修改結構的工具結果批次會交給 Provider：`patch`、
`diff`、路徑加上 `old_string` 與 `new_string`，或路徑加上 `content`。純讀取、狀態
檢查，以及單獨出現的驗證、失敗或量測結果都不會呼叫 Provider。在任務收到第一則
介入前，修改批次可以觸發新的工作區判斷；是否採納、如何修改及如何驗證仍由主 Agent 決定。

Codex 原生 `apply_patch` 會把修改內容放在最上層 `command`。只有工具名稱完全等於
`apply_patch`，而且 `command` 含有完整 patch 外框及新增、修改或刪除操作時，
Masters' Nudge 才接受這個 Codex 專用格式；其他工具或一般命令文字仍不符合資格。

任務開始時，Masters' Nudge 會記錄受長度限制的 Git 工作區狀態。明確修改發生後，
Provider 收到任務契約、任務起點工作區、目前累積工作區，以及明確變更檔案的目前內容。
Actor 對自己方案的描述不會被當成判斷證據。

OpenAI Provider 會以唯讀權限在 Actor 的工作區執行，因此能自行確認既有抽象、owner、
caller、資料路徑或控制流程，不必依賴 Host 預選的原始碼視窗。其他 Provider 會收到
相同的受限快照。Host 只辨識變更路徑，不替變更指定 ownership、生命週期或資料流意義。

Provider 只回傳 `pass` 或 `intervene`。介入會說明目前選擇、結構成本、Actor 可評估的
方向，以及具體 repository 證據。方向可以有明確意見，但不能包含 patch、替代程式碼或
逐步修改指令。任務收到一則介入後，後續修改批次保持安靜；新任務會重設這個界線。

## 如何運作

```text
任務契約 + 任務起點工作區
              ↓
          Actor 修改
              ↓
目前累積工作區 + 變更檔案
              ↓
唯讀 Provider ── pass（安靜）
              └─ intervene（方向建議）
                         ↓
                 Actor 負責實作
```

`pass` 只表示目前快照沒有產生重要且有依據的介入，不代表任務完成或設計已經最佳。

Claude Code 提供理想的 `PostToolBatch` 控制點：同一個模型步驟的工具結果都完成後，
下一步開始前才判斷。Codex 整合需要支援 `PostToolBatch` 的 Codex build；只有
`PostToolUse` 的原版 Codex 不會執行這個 Hook。本機 Codex 實作與上游需求整理在
[`PostToolBatch` Issue 草稿](docs/codex-post-tool-batch-issue-draft.md)。

Provider 發生錯誤或超過固定 90 秒時，這次 Nudge 直接結束，主要 Agent 照常繼續。

## 隱私

### 哪些資料會離開電腦

選定的 Provider 會收到一份受長度限制的資料，可能包含：

- 目前任務，或從長任務找回的 Goal；
- 任務起點時受長度限制的 Git status 與 diff；
- 目前受長度限制的 Git status 與累積 diff；
- 修改明確指定之檔案目前內容的限量版本。

Provider 不會收到完整對話、模型未公開的內部思考，也不會把 Actor 對方案的描述當成
證據。OpenAI Provider 可用唯讀工具檢查工作區內檔案，但無法修改工作區。

Anthropic 與 OpenAI 是雲端 Provider，這份資料會離開你的電腦，並受該 Provider
的資料政策約束。如果資料不能離開電腦，請選本機 Ollama。Ollama 只允許連到本機
位址，使用已安裝的模型，也不會失敗後偷偷改送雲端。

## 本機紀錄

Masters’ Nudge 會把目前任務狀態與少量稽核紀錄存在
`~/.masters-nudge/data/`。稽核紀錄包含 Nudge 回傳給 Host 的時間與 Nudge 內容。

這只能證明 Hook 已把 Nudge 回傳給 Claude Code 或 Codex，不能證明主模型真的讀到、
採納，或因為 Nudge 才採取後續行動。

每次開始新任務時，系統會刪除超過 30 天沒有更新的工作階段資料。Provider 偏好
另外存在 `~/.masters-nudge/config.json`，會保留到你再次修改。舊設定中的 `lens`
欄位會被忽略，下一次儲存 Provider 設定時移除。

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
