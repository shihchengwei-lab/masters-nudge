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

## 一次判斷

只有原生工具輸入最上層帶有明確修改結構的工具結果批次會交給 Provider：`patch`、
`diff`、路徑加上 `old_string` 與 `new_string`，或路徑加上 `content`。純讀取、狀態
檢查，以及單獨出現的驗證、失敗或量測結果都不會呼叫 Provider。每個修改批次各自
接受判斷；Masters' Nudge 不從結果文字猜測成功與否，也不把稍後的結果配對到先前的
修改。是否採納 Nudge、如何修改及如何驗證，仍由主 Agent 決定。

Provider 在乾淨脈絡中看任務開頭與受長度限制的決策證據。每筆修改證據保留 Host
提供的具體修改輸入與可觀察結果，不會依識別名稱的字串相同來推論來源關係。
Provider 自行形成因果判斷，再挑出最可能改變下一個工程決策、且非顯而易見的觀察。
同一個工作階段中，最多三則已回傳的 Nudge 會另外作為去重排除資訊送入；這些 Nudge
不是證據，也不代表主 Agent 的決策軌跡。

Provider 一次檢查三個結構原則，不先把問題路由成某一類：

- 讓非法狀態無法由資料結構建構；
- 讓事件與狀態沿單向因果流動；
- 讓副作用與依賴保持明確，使行為可以局部推理。

三個原則共同構成一次判斷，不是三個 Lens、三次模型呼叫或三則 Nudge。

三個原則各用一個詞表示：`validity` 是非法狀態、`causality` 是單向因果流、
`predictability` 是可預測性。Provider 分開回傳直接支撐判斷的可見 `evidence_seq`、
原則、精準定位程式概念的 `anchor`，
以及用一個短句描述單一工程關係的 `relationship`。`anchor` 只保留一個最小定位；
Host 顯示時才加上固定的 `warning`，例如 `causality warning:`。`warning` 不承擔分類或
程度語意。

Nudge 可以指出實作真正選擇的抽象或責任、預測眼前案例以外的行為，或提出更自然的
資料與控制流程形狀。例行驗證狀態與重述任務不屬於 Nudge 的角色。

## 如何運作

```text
任務與可觀察的工具結果
            ↓
     Provider 一次判斷
            ↓
   一則短 Nudge，或保持沉默
            ↓
      Agent 的下一段脈絡
```

每則 Nudge 都依目前情況生成，不是隨機抽一句罐頭訊息。Nudge 是獨立第二意見，
不是 review、評分、問題、完整解法，也不是一律要求多跑測試。

Claude Code 提供理想的 `PostToolBatch` 控制點：同一個模型步驟的工具結果都完成後，
下一步開始前才判斷。Codex 整合需要支援 `PostToolBatch` 的 Codex build；只有
`PostToolUse` 的原版 Codex 不會執行這個 Hook。本機 Codex 實作與上游需求整理在
[`PostToolBatch` Issue 草稿](docs/codex-post-tool-batch-issue-draft.md)。

Provider 發生錯誤或超過固定 90 秒時，這次 Nudge 直接結束，主要 Agent 照常繼續。

## 隱私

### 哪些資料會離開電腦

選定的 Provider 會收到一份受長度限制的資料，可能包含：

- 目前任務，或從長任務找回的 Goal；
- 當前批次內依原始順序排列的每個工具呼叫與結果；每筆內容都有長度上限；
- 同一個工作階段中，最多三則已回傳的 Nudge，只作為去重排除資訊。

Provider 不會收到完整對話、模型未公開的內部思考、先前批次的工具結果，或自動讀取
的本機檔案內容。

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
