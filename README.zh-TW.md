# Masters’ Nudge

繁體中文 | [English](README.md)

> **測試通過，只證明行為；不能證明設計。**
>
> 綠燈代表現在能過。六個月後呢？

AI 可以把功能做出來、讓測試通過，程式結構卻仍靠同步、特殊分支與局部補丁維持正確。需求再變，這些補救也可能繼續增加。

Masters’ Nudge 想改善這個問題：在 AI 寫程式的過程中，加入一則高品味結構的提醒，讓另一種資料與責任安排進入後續思考，增加產生更好結構的機會。

## 看 Actor 真正收到提醒，再修改程式

Element 的多裝置勾選與批次登出任務中，**兩份都通過固定驗收。** 右邊的 AI 收到提醒後，下一次修改把「顯示勾選結果」和「處理點選」綁在一起，讓兩者使用同一份紀錄。

![14 秒左右聊天對照：左邊沒有提醒；右邊收到提醒後，把顯示和點選改為使用同一份紀錄。](docs/images/element-chat-replay.gif)

*聊天畫面依真實紀錄重建，訊息採節譯、提醒採白話轉述，修改以摘要呈現；中間操作與等待省略。[原始紀錄與驗收](docs/examples/element-live-recording.zh-TW.md)。*

## 效果與代價

核心基準使用 **九道程式修改任務、七種模型配置**，比較直接實作與加入結構提醒的完整交付、程式結構及成本。每題每配置各跑兩次，每配置18次，共126次；測試日期為 2026-09-30 至 10-04。Sol 指 GPT-6.1 Sol，Astra 指 GPT-6 Astra；medium 與 xhigh 是不同的思考深度。寫程式的模型稱為 Actor，提供提醒的模型稱為 Provider。

其餘三題 Regexp、Metaflow、Tracing 在七種配置中皆無實作通過完整驗收契約，另列為[未解挑戰](benchmark/unresolved-challenges-20261004/README.zh-TW.md)。

**Sol xhigh 搭配 Sol xhigh Provider，維持直接實作的 13/18 完整交付，並在共同完成的11組程式碼比較中取得7勝、0敗、4平。** 品味評估採**匿名初評＋完整流程覆核**。這項結構收益的代價是累計時間增加48.9%、未快取輸入 Token 增加74.3%。相對 Sol medium Provider，完整交付與結構覆核結果也改善，累計時間增加3.7%。各組結果如下：

| 比較條件 | 前者品味：勝／敗／持平 | 累計時間 | 未快取輸入 Token |
|---|---|---|---|
| B 對 A：Sol medium＋Sol medium 對直接做 | 5／1／0 | +24.3% | +84.2% |
| F 對 C：Sol xhigh＋Sol medium 對直接做 | 3／3／2 | +43.6% | +50.7% |
| I 對 C：Sol xhigh＋Sol xhigh 對直接做 | 7／0／4 | +48.9% | +74.3% |
| I 對 F：Provider medium→xhigh | 5／0／4 | +3.7% | +15.7% |

匿名初評比較 X/Y，並交換呈現順序；完整流程覆核則在已知配置下檢查同一批程式，將新增狀態、轉接、同步與相容處理納入完整流程的維護成本。I 對 C 的兩場初評勝利改為持平，得到最終7／0／4。表格採用全部71組共同完整交付的同題／同次序複評結果。時間涵蓋核心九題每配置全部18次嘗試，Token 使用七種配置共同16個有完整用量的位置，包含 Actor 與 Provider。

完整交付結果如下：

| 配置 | 寫程式的模型 | 提供提醒的模型 | 完整交付 |
|---|---|---|---|
| A | Sol medium | 無 | 6/18 |
| B | Sol medium | Sol medium | 8/18 |
| C | Sol xhigh | 無 | 13/18 |
| D | Sol medium | Astra medium | 8/18 |
| E | Sol xhigh | Astra medium | 10/18 |
| F | Sol xhigh | Sol medium | 11/18 |
| I | Sol xhigh | Sol xhigh | 13/18 |

完整交付包含功能、執行規則、30 分鐘時限及相同原條款的相容性補查。完成份數為 **C = I > F > E > B = D > A**。C 的每份完整交付耗時最低；I 在同樣13/18的完整交付下，取得更好的結構覆核結果。各組品味比較的共同完成樣本不同。

最終品味評比與程式依據見[程式碼覆核報告](benchmark/model-comparison-20261004/taste-review/README.zh-TW.md)；逐題完成、成本與詳細方法見[九題主要報告](benchmark/model-comparison-20261004/PRIMARY.zh-TW.md)。[測試方法與數據](benchmark/README.zh-TW.md)說明如何查驗題目、程式修改、驗收與評審紀錄，並離線重建統計。

[十二題完整報告](benchmark/model-comparison-20261004/REPORT.zh-TW.md)保留全部168次嘗試、逐題結果與實驗細節。

## 工具做了什麼

寫程式的模型稱為 Actor，提供提醒的模型稱為 Provider。Actor 完成一次修改後，Provider 唯讀檢查任務與相關程式，提出一則簡短的結構建議；建議自動進入 Actor 的上下文，Actor 決定是否採納並繼續實作與驗證。

```mermaid
flowchart LR
    A["Actor 完成 apply_patch"] --> B["Provider 唯讀任務、修改與相關程式"]
    B -->|有具體方向| C["一則四欄建議進入 Actor 脈絡"]
    B -->|沒有具體方向| D["沉默"]
    C --> E["Actor 判斷、實作並驗證"]
    D --> E
```

## 作用原理

Actor 的後續生成受任務、既有程式與前面的解題脈絡影響。遇到問題時，沿著原本方向加一個判斷或特例，是一條容易延續的局部修補路徑。

Nudge 把另一種具體的資料與責任安排注入上下文，讓「從結構上消除補救」也成為後續生成的候選方向。它希望影響 Actor 接下來選中的 token，提高採用更好結構的機率。

Provider 用五條品味準則尋找這種方向：讓非法狀態無法表達、保持單向因果與可預測行為、讓事實只有一個權威來源，以及把必要複雜度留在真正的邊界。提醒聚焦可檢查的替代關係，讓 Actor 能判斷並實作。兩步選題、四欄格式與字元額度見[行為規格](SPEC.zh-TW.md)。

## 限制

- Actor 負責判斷提醒、實作與驗證完整交付。
- 每輪最多三則建議或兩次沉默，先到任一上限就停止。可辨識的純測試修改直接略過，不呼叫 Provider、不耗額度。
- Provider 只支援 OpenAI／Codex。只觀察明確的 `apply_patch` 修改，無法觀察沒有提供修改內容的命令列寫檔。
- 已驗證的 Windows 平台上，中斷會停止 Provider 並保留中斷故障紀錄，詳見[驗證紀錄](docs/qualification/README.zh-TW.md)。Codex 仍可能缺少對應的 `PostToolUse` 完成事件；詳見[重現與追蹤](https://github.com/openai/codex/issues/46765)。

## 環境需求

已驗證並支援的安裝平台為 **Windows 11 x64**；Linux 與 macOS 的安裝流程尚未完成驗證。

需要 Codex 啟動環境的 `python` 命令指向 Python 3.10+、Git 工作區、可啟動且已登入的 Codex CLI，以及支援 `UserPromptSubmit`、同步 MCP `PostToolUse`、`Interrupt` 與 `turn_id` 的 Actor 執行環境。

Hook 與 MCP 共用 Python 入口。只有 `py` 或 `python3` 的環境，需要先讓 Codex 的 `python` 命令指向 Python 3.10+；修改 PATH 後重新開啟 Codex。

Windows 的寫程式聊天還需要已啟用、受支援的 [Windows 沙箱執行方式](https://learn.chatgpt.com/docs/windows/windows-sandbox)。

本 repo 外掛清單版本為 `0.6.3+codex.20261013`。Provider 深度固定 medium；測試中的 xhigh Provider 使用實驗設定。預設 Provider 模型為 `gpt-5.6-sol`，儲存的模型選擇覆蓋預設。

## 安裝、啟用與第一次使用

1. 確認 Python、Git 與 Codex CLI 已安裝；若 CLI 尚未登入，在 PowerShell 執行 `codex login`。
2. 在 Codex 桌面版的外掛頁，選 **Add → Add Marketplace → Add from a repository**，填入 `https://github.com/shihchengwei-lab/masters-nudge`，按 **Sync**。repo 的[外掛目錄](.agents/plugins/marketplace.json)提供 Masters’ Nudge；開啟它並安裝、啟用。來源與安裝介面可參照[官方步驟](https://developers.openai.com/learn/developers-codex-plugin)。
3. 依 Codex 的提示檢查並信任外掛 Hook。CLI 可輸入 `/hooks`，核對 Masters’ Nudge 的 `UserPromptSubmit`、`PostToolUse` 與 `Interrupt`，詳見[官方 Hook 說明](https://learn.chatgpt.com/docs/hooks)。
更新已安裝的版本後，重新開啟 Codex；若 hook 被標為「已修改」，檢查新命令後重新信任，再開始新對話。

4. 開啟新對話，請 Codex：「檢查 Masters’ Nudge 是否已就緒，並將 Provider 設為 gpt-6.1-sol。」外掛提供設定與診斷技能；就緒檢查會列出依賴、登入、啟用狀態，並使用 Codex 實際載入的 MCP 命令檢查初始化與工具探索；不呼叫 Provider。
5. 在自己的 Git 專案開啟新對話，交給 Actor 一項正常的程式修改。完成一次產品程式的 `apply_patch` 後，請 Codex：「顯示 Masters’ Nudge 最近的提醒紀錄。」`feedback` 表示已產生建議，`silence` 表示正常判斷後沒有建議；工具故障會另列原因。若有建議，可核對 Actor 上下文中的四欄提醒與後續程式改動。

如果已下載本 repo，也可在 repo 根目錄用 PowerShell 手動設定與查詢：

```powershell
python masters_nudge_cli.py provider set openai --model gpt-6.1-sol
python masters_nudge_cli.py doctor --host codex
python masters_nudge_cli.py recent-nudges --limit 10
```

## 隱私

任務原文、修改、工具結果、可完整放入共同材料額度的已修改檔案，以及檔案來源事實會傳給 OpenAI。Provider 可唯讀 Git 工作區中的未忽略檔案。完整任務起點檔案清單只保存在本機，送出時附本批路徑是否原本存在。

預設紀錄存於使用者目錄的 `.masters-nudge/data/feedback.sqlite3`，設定存於 `.masters-nudge/config.json`。`MASTERS_NUDGE_DATA_DIR` 可覆蓋位置。

## 開發

原始碼是唯一實作來源，外掛副本由建置指令產生：

```powershell
python tools/build_plugin.py --write
python tools/build_plugin.py --check
python -m unittest discover -s tests -v
```

使用、規格與開發文件見[文件索引](docs/README.zh-TW.md)。
