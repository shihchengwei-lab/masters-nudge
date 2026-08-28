# Masters’ Nudge

繁體中文 | [English](README.md)

> 在 LLM agent 工作途中，動態加入一個新的語義錨點。

Masters’ Nudge 是給 Claude Code 與 Codex 使用的動態 context steering plugin。

它在選定的 checkpoint 收集主要 agent 當下留下的有限證據，交給獨立的 Nudge provider。Provider 透過指定的 Lens 聚焦問題，產生一則短 Nudge，再由 Harness 寫入主要 agent 的 context。

短問題是 Nudge 的外在形式。底層動作是把一個新的語義錨點放進 context，讓主要 agent 在新的條件下繼續生成。

---

## 運作迴圈

```text
使用者提出任務
        ↓
主要 agent 工作，留下可觀察結果
        ↓
Hook 收集當下任務與有限證據
        ↓
Checkpoint policy 判斷是否進行 review
        ↓
Nudge provider 透過指定 Lens 聚焦
        ↓
產生一則短問題，或回傳 no_finding
        ↓
Harness 將 Nudge 作為新錨點寫入 context
        ↓
主要 agent 在新的 context 下繼續工作
        ↺
```

每則 Nudge 都根據當下證據動態生成。

同一個 Lens 在不同任務、不同階段或不同結果下，可以產生完全不同的錨點。

---

## 底層機制

LLM 依目前的 context，計算下一個 token 的條件機率。

Nudge 進入 context 後，它的 token 也會參與後續生成，使下一個 token 的機率分布與後續生成路徑產生偏移。

這裡的「錨點」就是加入 context 的一小段 token。它把一個新的檢查方向放進模型後續生成可以回指的條件中。

```text
原本的 context
        +
一個新的語義錨點
        ↓
新的 token 分布
        ↓
可能不同的生成路徑
```

Masters’ Nudge 目前把這個錨點壓縮成一則短問題。

問題提供方向，但不展開完整解法。主要 agent 會自行把這個方向與原本的任務、證據和生成路徑混合，再決定下一步輸出。

這個控制點位於推論階段的 context，模型權重保持不變。

錨點的內容、注入時點、主要 agent 當下的工作狀態，以及既有 context，都會影響最後形成的偏移。

---

## 為什麼叫 Masters’ Nudge

`Masters` 指的是放在 Nudge provider 前方的聚焦濾鏡。

廣為人知的人名是這層濾鏡的外在形式。底層利用的是人物名稱與相關概念在模型訓練材料中的密集關聯。

這個設計建立在一個實務假設上：

知名人物在模型訓練材料中通常有大量相關文本。人物名稱會與他們反覆關心的問題、判斷方式、取捨原則、案例和表達語彙共同出現。

可以把這種關係簡化理解成：人物名稱與特定問題意識，在模型內部形成相近的語義向量區域。

當人物名稱出現在 provider prompt 中，相關的判斷方式更容易被喚起，provider 的生成也更容易聚焦到那些關注點。

```text
當下證據
    +
Master filter
    ↓
Nudge provider
    ↓
聚焦到相近的語義區域
    ↓
產生一則短 Nudge
    ↓
成為主要 agent context 中的新錨點
```

Master filter 只提供給 Nudge provider。

Provider 透過這層濾鏡閱讀當下證據，選出最值得帶入主要 agent context 的方向，再把它壓縮成一則 Nudge。

主要 agent 只會收到最後產生的問題，不會看到人物名稱、角色設定或完整的 reviewer prompt。

專案名稱描述的就是這條路徑：

> **Masters 聚焦 provider，provider 產生 Nudge，Nudge 成為主要 agent context 中的新錨點。**

這個專案的承重點，是 Lens 能否讓 provider 從證據中選出有價值的方向，以及最後的 Nudge 能否影響主要 agent 當下的生成路徑。

人名是 Lens 的一種壓縮表示法。同一個位置也可以放入明確的工程準則、道德哲學、合規要求、科學方法或其他評估框架。

---

## Lens 決定聚焦方向

Lens 定義 Nudge provider 應該注意什麼。

它可以聚焦於：

- 軟體工程品味；
- 系統邊界與責任歸屬；
- 狀態、事件順序與不變量；
- 執行成本與效能；
- 道德取捨；
- 合規證據；
- 科學上的反例與可證偽條件。

不同 Lens 會從同一份證據中選出不同的語義錨點。

目前的實作把錨點表達成問題：

```text
工程 Lens：
哪個元件真正擁有這個狀態？

道德 Lens：
這個決定把誰的代價移到系統外？

合規 Lens：
哪份證據支持這項合規宣告？

科學 Lens：
什麼結果能區分這兩個解釋？
```

目前這個 repository 實作的是軟體工程版本。其他 Lens 可以沿用相同的 Hook、checkpoint 與注入迴圈。

---

## 一則 Nudge 的形狀

目前的輸出契約把語義錨點壓縮成一則短問題。

對主要 agent 而言，Nudge 是一則簡短、以證據為錨點的獨立第二意見。

Reviewer 每次回傳兩種結果之一。

### `finding`

一則有效的 Nudge：

- 根據目前提供的證據；
- 聚焦一個假設、限制、反例或替代方向；
- 提出一個現在可以檢查的問題；
- 一次只包含一個想法；
- 最長 52 個字元。

主要 agent 會收到：

```text
獨立第二意見：
<一則短問題>
```

### `no_finding`

當目前證據沒有支持值得加入的新方向時，Reviewer 可以回傳 `no_finding`，主要 agent 照原本的路徑繼續工作。

`no_finding` 的實際機率通常偏低。

LLM 在收到 review 任務後，傾向產生一個可以交付的意見，不傾向回答「沒有意見」。即使證據不足，它仍可能勉強選出一個問題。

因此，`no_finding` 提供的是一個明確的沉默出口，不應預期它和 `finding` 一樣常見。

結構驗證器負責檢查輸出格式、內容數量與長度。符合契約的 Nudge 才會進入主要 agent 的 context。

---

## 與其他控制方式的差別

| 控制方式 | 介入方式 |
|---|---|
| 固定 System Prompt | 在任務開始前持續施加固定的行為偏向 |
| Temperature | 全域改變 token 取樣的分散程度 |
| 完整 Reviewer | 產生另一套分析、建議或解法 |
| Masters’ Nudge | 根據當下狀態，加入一個短而局部的語義錨點 |

固定 System Prompt 適合放置長期規則。

Temperature 適合調整整體取樣方式。

完整 Reviewer 適合交付另一份分析結果。

Masters’ Nudge 則把介入放在工作途中：先讀取主要 agent 已經做到哪裡，再決定此刻要把哪個方向放進 context。

目前的實作使用短問題承載這個方向。

---

## Harness 把一次 Prompt 變成迴圈

單次 Prompt 可以請另一個模型產生一個新的思考方向。

Harness 負責讓這個方向在固定流程中反覆運作：

1. 保存使用者任務；
2. 收集可觀察證據；
3. 判斷 checkpoint；
4. 選擇 Lens；
5. 呼叫 Nudge provider；
6. 驗證 Nudge 格式；
7. 將 Nudge 作為新錨點寫入主要 agent 的 context；
8. 記錄 review、投遞與後續反應。

這層工程結構把一次性的 Prompt 技巧，變成可重複、可替換、可觀察的動態介入機制。

---

## 可插拔的超我

可以用一個簡化的比喻理解這個架構：

- **主要 LLM 是本我**：提供持續生成、解題與行動的動力；
- **Harness 是自我**：管理工具、證據、時機與工作流程；
- **Nudge 是超我**：在特定時點帶入額外的語義錨點。

更換 Lens，就等於更換這個超我關注的事情。

它可以加入工程品味的錨點，也可以加入道德、合規、安全或科學證據的錨點。主要模型與 Harness 保持不變，介入方向可以動態替換。

這裡借用的是架構中的角色分工，不是對模型心理狀態的主張。

---

## 張力與收斂

主要 agent 工作一段時間後，會形成一條逐漸收斂的生成路徑。

Nudge 把另一個語義錨點加入同一個 context，使主要 agent 同時面對原本的路徑與新的方向。

當 Nudge 命中盲點時，這股張力可以：

- 揭露尚未驗證的假設；
- 阻止過早宣告完成；
- 拉回已被忽略的方向；
- 促使 agent 補上一個辨別性檢查；
- 推動原本低機率但有價值的生成路徑。

當 Nudge 與充分證據衝突，或在錯誤時點重新打開問題時，張力也可能表現為：

- 已經解決的問題被重新展開；
- 主要目標失焦；
- 工作方向來回擺盪；
- 生成路徑持續發散而無法收斂。

這個機制的效果來自張力，也受張力限制。

Harness 透過少數 checkpoint、有限證據、單一問題、52 字元上限與 `no_finding`，控制每次介入的範圍。

---

## 目前的軟體工程版本

Repository 目前提供六種工程 Lens：

| Lens | 聚焦方向 |
|---|---|
| Design | 上游限制、責任歸屬與下游成本 |
| Build | 最短回饋路徑、可觀察行為與停止條件 |
| Evolve | 重複知識、變更擴散與正確歸屬 |
| Review | 控制流程、必要複雜度與所有權 |
| Reliability | 狀態、事件順序、不變量與局部失敗 |
| Performance | 實際執行成本與不必要工作 |

Automatic 模式會根據主要 agent 回報的當下工作焦點選擇 Lens。這份焦點回報只負責選擇 reviewer prompt；是否進行 review 仍由 Hook 與 checkpoint policy 決定。

手動設定可以固定使用六種 Lens 中的任一種：Design、Build、Evolve、Review、Reliability 或 Performance。

---

## 支援環境

### Host

- Claude Code
- Codex CLI

兩個 Host 使用不同的事件 adapter，再建立相同格式的受限 `ReviewRequest`，交給共同的 review core。

### Nudge provider

- Anthropic
- OpenAI
- xAI，透過已登入的 Grok CLI
- 本機 Ollama

Reviewer 每次都是獨立的模型呼叫，即使它使用與主要 agent 相同的 provider。

---

## Review checkpoint

目前的 Hook 會在下列時點考慮產生 Nudge：

- 相同可觀察範圍發生第二次失敗；
- 長期目標明確轉為 `complete` 或 `blocked`；
- 一個工作回合結束。

一般程式變更、大型 diff、成功驗證與第一次失敗會先累積為證據。Checkpoint 成立後，Nudge provider 才會讀取受限的證據封包。

符合條件的 review 會同步執行，讓 Nudge 在同一回合進入主要 agent 的後續 context。

Provider 工作時間最多 90 秒，外層 Host Hook 預留 120 秒。Review 發生錯誤或逾時時，這次介入結束，主要 agent 繼續工作。

---

## 安裝

需求：

- 支援 plugin 的 Claude Code 或 Codex CLI；
- Python 3.10+；
- 已登入所選雲端 Nudge provider 對應的 CLI；使用本機 Ollama 時不需要雲端登入。

### Claude Code

```bash
claude plugin marketplace add shihchengwei-lab/masters-nudge
claude plugin install masters-nudge@masters-nudge --config python_command=python
```

若 `python` 不是 Python 3.10+，請將 `python_command` 改成 `python3` 或 Python 執行檔的絕對路徑。

設定值只能包含一個執行檔，不能附加參數。

### Codex

```bash
codex plugin marketplace add shihchengwei-lab/masters-nudge
codex plugin add masters-nudge@masters-nudge
```

安裝後請開啟新的 task。

Codex 使用者需進入 `/hooks`，檢查命令並批准 plugin hooks。

Plugin 封裝與 Hook 核准方式以目前的 [OpenAI plugin 文件](https://developers.openai.com/plugins/build/plugins)與 [Codex Hooks 文件](https://learn.chatgpt.com/docs/hooks)為準。

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

更新後請重新啟動 Host。

解除安裝會保留 `~/.masters-nudge/data/` 中的既有資料。

---

## 使用與檢查

Hooks 會自動執行，不需要在每個 Prompt 中手動呼叫 Masters’ Nudge。

以下說法會啟用 plugin 內建的 Skills：

- **「檢查 Masters’ Nudge 是否準備完成。」**  
  檢查 runtime、provider、資料目錄寫入權限、Hooks 與選用的 UI 依賴，不會呼叫 Reviewer。

- **「開啟 Masters’ Nudge 浮動視窗。」**  
  開啟本機歷史視窗；需要 Pillow，以及包含 Tkinter 的 Python。

- **「將 Masters’ Nudge 設定成使用我的本機 Ollama 模型 `<完整模型名>`。」**  
  驗證 loopback Ollama 上已安裝的模型，並保存設定。

- **「遷移舊版 Masters’ Nudge hooks。」**  
  先顯示 dry run，取得明確同意後，再處理可以明確辨識的舊版 Hook。

遷移前會在 Host 設定旁建立帶有時間戳的備份。需要人工判斷的舊設定會留在診斷結果中，既有 review 資料會保留。

---

## 設定

未覆寫時：

- Claude Code 使用 Anthropic `sonnet`；
- Codex 使用 OpenAI `gpt-5.6-sol`。

常用環境變數：

| 變數 | 預設值 | 用途 |
|---|---|---|
| `MASTERS_NUDGE_PROVIDER` | 依 Host 決定 | `anthropic`、`openai`、`grok` 或 `ollama-local` |
| `MASTERS_NUDGE_MODEL` | 依 Host 決定 | Reviewer 的完整模型名稱 |
| `MASTERS_NUDGE_OLLAMA_URL` | `http://127.0.0.1:11434` | Loopback Ollama endpoint |
| `MASTERS_NUDGE_TIMEOUT` | `90` | 回合結束時的 Reviewer 逾時秒數 |
| `MASTERS_NUDGE_CHECKPOINT_TIMEOUT` | `90` | 工作途中的 Reviewer 逾時秒數 |
| `MASTERS_NUDGE_DATA_DIR` | `~/.masters-nudge/data` | Logs、state、receipts、telemetry 與 reviewer 設定 |
| `MASTERS_NUDGE_STAGE` | 未設定 | 選擇 `automatic`、`design`、`build`、`evolve`、`review`、`reliability` 或 `performance` |
| `MASTERS_NUDGE_SPRITE_PATH` | 內建 sprite | 選用浮動視窗的 spritesheet |

Provider 環境變數優先於 `reviewer.json` 中保存的設定。

`MASTERS_NUDGE_STAGE` 優先於 `config.json` 中的工程階段。未指定時使用 Automatic 模式；指定工程階段時，Reviewer 固定使用對應 Lens。

損壞或無法解析的 Reviewer 設定會留下診斷，並結束該次 review。

### 本機 Ollama

本機模式只連接 loopback HTTP endpoint，並停用 client proxy 與 redirect。

設定流程會確認 Ollama 已關閉 cloud 功能，並檢查模型 metadata。Masters’ Nudge 使用已經安裝的模型，不會自行下載模型。

本機 Provider 發生錯誤時，這次 review 直接結束，不會轉送到雲端 Provider。

---

## 資料與隱私

Reviewer 只會收到 Hook 建立的受限證據封包。

依觸發事件不同，封包可能包含：

- 最新的使用者任務要求；
- 從任務明確指定的本機來源讀到的內容；
- 最新且受長度限制的實質變更；
- 驗證與失敗的語意結果；
- Stop 邊界的當下最終宣告。

最多三則先前已注入的 Nudge，會作為避免重複的排除集合送給 Reviewer。

Reviewer prompt 與所選 Lens 屬於生成指令，不屬於證據。

下列內容不會進入 Reviewer 封包：

- 完整 transcript；
- 主要模型未公開的內部思考；
- 一般搜尋與瀏覽輸出；
- 未被任務明確指定的一般原始碼探索；
- 外部報告；
- 工具名稱與完整命令；
- 主要 agent 進行中的說明或對 Nudge 的反應。

任務、證據、Nudge、投遞 receipts、Provider 設定與診斷 telemetry，會以純文字保存在：

```text
~/.masters-nudge/data/
```

Telemetry 記錄路由、狀態、延遲，以及 Provider 回報的用量 metadata。

Review 排程與 receipt 狀態記錄在[架構文件](docs/architecture.md)。

雲端 Provider 的資料保留與訓練政策由各 Provider 決定。

---

## 歷史測試材料

Repository 保留了一次 prerelease A/B snapshot：

- 四個先前未使用的 SWE-bench Verified tasks；
- Arm A 關閉 plugin hooks，通過 2/4；
- Arm B 啟用當時的 plugin snapshot，通過 3/4；
- Arm B 共產生並注入六則 Reviewer findings；
- 其中一個 task 在兩組之間出現不同結果。

這份 snapshot 來自 commit `ac090a9f34ff76b826ceedb10361f7d7a3bd4ed3`，記錄的是當時版本，不代表目前 source tree 的驗證結果。

四個固定順序 task 只能提供描述性的行為材料。目前材料不足以建立穩定效果、證明泛化，或把其中一個 task 的結果歸因於 Nudge。

Injected receipts 與後續 response observations 只能證明投遞順序。它們不能單獨證明 Nudge 造成後續行動。

完整 protocol、結果、排除項目與宣告範圍：

- [Historical prerelease benchmark](evaluation/README.md)

---

## 開發

Repository 中的 plugin package 由原始碼產生。

送出變更前執行：

```bash
python -m unittest discover -v
python tools/build_plugin.py --check
```

- 架構：[docs/architecture.md](docs/architecture.md)
- 目前決策：[ROADMAP.md](ROADMAP.md)
- 授權：[MIT](LICENSE)
