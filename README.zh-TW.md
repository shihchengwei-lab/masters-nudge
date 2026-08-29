# Masters’ Nudge

繁體中文 | [English](README.md)

> **測試通過，只能確定行為；不能替 Agent 選擇設計。**

Masters’ Nudge 在 Claude Code 或 Codex Agent 的下一個決策前，加入一項有證據的
工程取捨。

---

## 實際執行

![從測試通過到主模型下一個決策的一次實際執行](docs/assets/actual-nudge-run.png)

我們先準備一段今天能正常運作的程式：2 個測試通過。但同一套折扣算法出現在兩個
地方。因為眼前沒有錯誤，Agent 很可能就停下；問題是未來如果只改到其中一份，
兩邊算出的金額可能不同。

Nudge 提醒主模型：折扣只算一次就好。主模型真的刪掉重複的那份，讓結帳功能直接
使用原本的折扣計算。修改後，同樣的 2 個測試再次通過。

圖片把這次執行中未改寫的 Nudge、主模型回應、實際檔案修改與測試結果排在一起。
這次由 Automatic 選到 Simplicity，Anthropic `claude-opus-5` 產生 Nudge，OpenAI
`gpt-5.6-sol` 擔任主模型。這是一次真實反應，不保證每則 Nudge 都會被採納。

---

## 三個工程 Lens

| Lens | 聚焦的決策 |
|---|---|
| Simplicity | 哪些複雜度有必要，以及責任應由哪個元件擁有 |
| Reliability | 事件換序、重試或中途失敗時，什麼仍必須成立 |
| Performance | 真實 execution path 上，哪些已量到的工作應該消失 |

本專案把這些關於責任、不變量與實際成本的持續性偏好稱為工程品味。

---

## Nudge 輸出契約

對主要 agent 而言，Nudge 是一則簡短、以證據為錨點的獨立第二意見。
Provider 每次只回傳一個 JSON 結果：

- `finding`：用一則繁體中文直接陳述一項具體工程取捨，最長 52 個字元；
- `no_finding`：現有證據不足以支持有用取捨時保持沉默。

Finding 直接說明此刻應優先、保留、簡化或移除什麼。Finding 不是問題、review
敘事、完整解法，也不是泛泛要求新增、執行或通過測試。

例如：

```text
直接記錄輸入來源；別用值猜測，因為相同值不代表相同來源。
```

主要 agent 會收到：

```text
獨立第二意見：
<一則短方向>
```

Runtime 驗證刻意只處理結構：JSON schema、狀態與欄位一致性、合法 Lens、空值、
單一輸出物件與 52 字元上限。程式不使用關鍵字或 regex 判斷工程品味，也不改寫
結構合法的結果。

Provider 不會看到過去的 Nudge。系統只在生成完成後，攔下與先前注入內容完全相同
的 finding。

---

## 運作方式

```text
可觀察的工具結果
        ↓
受限的任務與證據封包
        ↓
一個合格 Lens，或不選
        ↓
一則短 Nudge，或 no_finding
        ↓
進入 Agent 後續 context
```

每則 Nudge 都依控制點當下的證據生成，不是從預先寫好的句子清單中挑選。Nudge
作為新的 context，可以在不改變模型權重的情況下影響後續生成；主要 Agent 可以
採納、重新解讀或忽略 Nudge。

Automatic 模式由精簡 Router 選出一個合格 Lens 或 `none`。Generator 只收到原始
封包與選中的 Filter，不會收到 Router 的理由。手動模式固定一個 Lens，但不會取消
證據要求，也不會強迫 Provider 產生 finding。

Filter 背後的人名只是 provider prompt 內部的注意力提示，不表示 Provider 會模仿
某個人物，也不表示 Provider 因此取得某個人物的能力。

Masters’ Nudge 不是 reviewer、裁判、完整解題者或 Stop gate，也不宣稱提升通用
解題正確率。

---

## Host 控制點

理想的介入時點是：目前模型步驟的工具結果已全部完成，下一次模型 request 尚未開始。

| Host | 控制點 | 精確度 | 已知限制 |
|---|---|---|---|
| Claude Code | 原生 `PostToolBatch` | 對原生 batch 精確 | 只有序列化結果含明確失敗訊號時，才把 batch 標記為失敗 |
| Codex | 同步 `PostToolUse` | 近似 | Codex 沒有原生 batch 邊界，因此平行工具可能被分開觀測與判斷 |

Claude Code 對一個完成的工具 batch 最多建立一次 Nudge attempt。Codex 把每個
`PostToolUse` 視為單項 batch。Masters’ Nudge 不使用 timer、transcript 猜測或
延遲補送來假裝不存在的 Codex batch 邊界。

符合條件的 attempt 會同步執行，讓有效 Nudge 能在同一回合進入後續 context。
Provider 工作時間最多 90 秒，外層 Host Hook 預留 120 秒。Automatic 模式由
Router 與 Generator 共用 Provider 時限；手動模式只呼叫一次 Generator。錯誤或
逾時採 fail-open：結束這次 attempt，主要 agent 繼續工作。

在 `Stop` 時，Hook 只記錄主要 agent 是否回應先前的 Nudge；不會呼叫 Provider、
產生另一則 Nudge、阻擋完成或延長回合。

---

## Provider 看得到什麼

Provider 只收到目前控制點建立的受限封包。依事件不同，封包可能包含：

- 目前的使用者任務錨點；
- 任務明確指定的本機來源內容；
- 最近且受長度限制的實質變更；
- 客觀的失敗、驗證、工具結果與量測。

Provider 不會收到：

- 完整 transcript；
- 主要模型未公開的內部思考；
- 主要 agent 進行中的說明或對 Nudge 的反應；
- 過去的 Nudge；
- 一般導覽、搜尋或瀏覽輸出；
- 未被任務明確指定的原始碼探索；
- 工具名稱或完整命令。

Base prompt 只定義 Provider 是什麼、看得到什麼，以及輸出契約。選中的 Filter
承擔完整工程聚焦。Router 與 Generator 都使用原始封包；Generator 不會收到
routing hypothesis。

---

## 支援的 Provider

- Anthropic
- OpenAI
- xAI，透過已登入的 Grok CLI
- 本機 Ollama

每次 Nudge attempt 都是獨立的模型呼叫，即使 Provider 與主要 agent 使用同一個
模型家族。Provider 失敗時，不會在未告知的情況下切換到另一個 Provider。

未覆寫設定時，Claude Code 使用 Anthropic `sonnet`；Codex 使用 OpenAI
`gpt-5.6-sol`。

---

## 安裝

需求：

- 支援 plugin 的 Claude Code 或 Codex CLI；
- Python 3.10+；
- 已登入所選雲端 Provider 對應的 CLI，或已安裝本機 Ollama 模型。

### Claude Code

```bash
claude plugin marketplace add shihchengwei-lab/masters-nudge
claude plugin install masters-nudge@masters-nudge --config python_command=python
```

若 `python` 不是 Python 3.10+，請把 `python_command` 改成 `python3` 或 Python
執行檔的絕對路徑。設定值只能包含一個執行檔，不能附加其他參數。

### Codex

```bash
codex plugin marketplace add shihchengwei-lab/masters-nudge
codex plugin add masters-nudge@masters-nudge
```

安裝後請開啟新的 task。在 Codex 中開啟 `/hooks`，檢查並批准 plugin 命令。

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

更新後請重新啟動 Host。解除安裝會保留 `~/.masters-nudge/data/` 中的既有資料。

---

## 使用與檢查

Hooks 會自動執行，不需要在每個 Prompt 中指名 Masters’ Nudge。Plugin 也提供處理
下列明確任務的 Skills：

- **「檢查 Masters’ Nudge 是否準備完成。」** 檢查 Python、Provider 存取、資料
  目錄寫入、Host Hooks、控制點精確度與選用 UI 依賴，不會呼叫 Nudge provider。
- **「開啟 Masters’ Nudge 浮動視窗。」** 開啟本機歷史與設定視窗；需要 Pillow，
  以及包含 Tkinter 的 Python。
- **「將 Masters’ Nudge 設定成使用我的本機 Ollama 模型
  `<完整模型名>`。」** 驗證 loopback Ollama 上已安裝的模型，並保存 Provider 設定。
- **「遷移舊版 Masters’ Nudge hooks。」** 先顯示 dry run；取得明確同意後，才修改
  可以清楚辨識的舊版 Hooks。

已退休的 Lens 設定會回到 Automatic 模式，不會映射成仍保留的 Lens。

---

## 設定

| 變數 | 預設值 | 用途 |
|---|---|---|
| `MASTERS_NUDGE_PROVIDER` | 依 Host 決定 | `anthropic`、`openai`、`grok` 或 `ollama-local` |
| `MASTERS_NUDGE_MODEL` | 依 Host 決定 | Provider 的完整模型名稱 |
| `MASTERS_NUDGE_OLLAMA_URL` | `http://127.0.0.1:11434` | Loopback Ollama endpoint |
| `MASTERS_NUDGE_TIMEOUT` | `90` | Provider 逾時秒數 |
| `MASTERS_NUDGE_CHECKPOINT_TIMEOUT` | `90` | 工具控制點的 Provider 逾時秒數 |
| `MASTERS_NUDGE_DATA_DIR` | `~/.masters-nudge/data` | 狀態、findings、receipts、telemetry 與 Provider 設定 |
| `MASTERS_NUDGE_STAGE` | 未設定 | `automatic`、`review`、`reliability` 或 `performance` |
| `MASTERS_NUDGE_SPRITE_PATH` | 內建 sprite | 選用浮動視窗的 spritesheet |

`MASTERS_NUDGE_STAGE` 優先於 `config.json` 保存的階段。`review` 選擇
Simplicity，`reliability` 選擇 Reliability，`performance` 選擇 Performance；
未設定時由 Automatic 模式使用 Router。

Provider 環境變數優先於 `reviewer.json` 中保存的設定。損壞的 Provider 設定會留下
診斷並結束該次 attempt。

本機 Ollama 模式只連接 loopback endpoint，停用 client proxy 與 redirect，使用
已安裝的模型，不會自行下載。本機 Provider 失敗時，attempt 直接結束，不會改送雲端。

---

## 資料、隱私與證據界線

任務、受限證據、findings、投遞 receipts、Provider 設定與診斷 telemetry，會以
純文字保存在：

```text
~/.masters-nudge/data/
```

Telemetry 記錄不含內容的 Host、Hook event、route、status、latency，以及 Provider
回報的用量 metadata。

Injected receipts 與後續 response observations 只能證明投遞順序。
這些記錄不能證明 Nudge 導致後續行動。Masters’ Nudge 也不宣稱能提升通用解題
正確率或測試通過率。Filter 能否產生可辨識的工程品味，需要另以固定證據封包進行
盲測評估。

雲端 Provider 的資料保留與訓練政策由各 Provider 決定。

---

## 開發

Repository 原始碼是唯一實作來源；版控中的 plugin package 由原始碼產生。

```bash
python -m unittest discover -v
python tools/build_plugin.py --check
```

- 架構：[docs/architecture.md](docs/architecture.md)
- 目前決策：[ROADMAP.md](ROADMAP.md)
- 授權：[MIT](LICENSE)
