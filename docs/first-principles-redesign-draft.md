# Masters’ Nudge 第一性原理修改草案

狀態：討論定案後的實作草案，尚未實作  
日期：2026-08-29

## 1. 目標

Masters’ Nudge 不負責讓主模型更會解題，也不扮演 reviewer、裁判或煞車者。Nudge 是另一套工程品味根據當下證據形成的獨立第二意見；可能改變或強化下一步，也可以沉默，但不以找出主模型盲點為任務。

```text
主模型採取行動
→ 環境產生可觀察結果
→ 收集與去重證據
→ Router 選擇一個合格濾鏡或 none
→ Generator 只用該濾鏡獨立形成一項取捨
→ 在下一次模型決策前注入 Nudge
```

理想控制點是：**證據已完整，下一次模型決策尚未開始。** Hook 只是各 Host 接近這個控制點的 adapter。

## 2. 濾鏡範圍

只保留三個能反制通用 coding agent 穩定預設偏差的濾鏡：

| 濾鏡 | 聚焦 | 最低證據門檻 |
|---|---|---|
| Linus | 必要複雜度與單一責任 | 當前任務觸及的 wrapper、adapter、fallback、相容路徑、workaround、重複 owner 或修補累積 |
| Lamport | invariant、事件順序與部分失敗 | 明確 invariant、至少兩個可換序事件，以及 packet 支持的重試、中斷、重送或部分成功路徑 |
| Carmack | 實際執行成本與少做工作 | profiler、benchmark、trace 或可把成本定位到 execution path 的數字 |

移除 Jeff、Beck、Fowler；其承重部分已被通用模型或保留濾鏡涵蓋。自動與手動模式都只提供 Linus、Lamport、Carmack。既有設定若選到退休濾鏡，明確回到 `automatic`，不映射成另一位大師。

手動模式只固定聚焦濾鏡，不強迫輸出；最低證據門檻仍然適用。

## 3. Provider 輸入與 prompt

### Base prompt

Base prompt 只定義：

1. **身分**：針對仍可改變決策的獨立第二意見，不是 reviewer、裁判、完整解題者或主模型的對手。
2. **可知範圍**：只使用 bounded packet；未提供的 repository、需求、隱藏工作與主模型推理一律未知。
3. **輸出契約**：回傳一則短促、單一取捨的 Nudge，或 `no_finding`；使用既定 JSON schema、繁體中文與 52 字上限。

Base prompt 不包含工程焦點、路由規則或通用品味指導。

### Filter prompt

Filter prompt 承擔全部聚焦：

- 哪些證據足以讓該濾鏡發言，哪些近似訊號不足。
- 如何從證據形成該濾鏡特有的工程取捨。
- 如何直接表達偏好，不變成問題、檢查流程或 review 敘事。
- 兩個短正面範例。

大師姓名只作為注意力提示，不模仿人物語氣。

### Runtime packet

Provider 只收到：

```text
task_anchor  使用者正在解決的問題
evidence     實際變更、事件結果、狀態或量測
```

Packet 不含 `current_direction`、主模型推理摘要、running explanation 或過去的 Nudge。實際 diff 與工具結果可以作為客觀證據，但不得包裝成主模型的動機。

過去 Nudge 不提供給 Provider。若要避免完全相同的內容重複注入，只在輸出後使用 exact hash 去重，不做語義攔截。

### 輸出驗證

程式層只驗證 JSON schema、狀態與欄位一致性、合法濾鏡名稱、字數、空值和單一輸出物件。程式層不以 regex 或關鍵字判斷品味、review 語氣或取捨品質，也不改寫結構合法的 Provider 輸出。

## 4. 路由與 ownership

每項責任只有一個 owner：

| 元件 | 負責 | 不負責 |
|---|---|---|
| Host adapter | 將 native event 正規化成完整可用的事件或 batch | 選擇濾鏡、解讀工程語義 |
| checkpoints／evidence | 記錄、限縮、排序、fingerprint 與去重；排除純導覽或空結果 | 判斷 Linus、Lamport、Carmack 哪個成立 |
| Router | 根據同一份 `task_anchor`、`evidence` 與三個最低門檻，回傳一個濾鏡或 `none` | 提供建議、產生 Nudge、替 Generator 解釋證據 |
| Generator | 使用 Base prompt、單一 Filter prompt 與原始 packet 形成 Nudge 或沉默 | 看其他濾鏡、主模型推理或 Router 理由 |
| Provider contract | 驗證機械輸出契約 | 判定語義品質 |
| Delivery | 注入合法且未完全重複的 Nudge，記錄結果 | 修改 Nudge、補做語義判斷 |

Router 只輸出濾鏡名稱或 `none`；Router 的 routing hypothesis 不傳給 Generator。Generator 必須直接根據原始 packet 形成獨立意見。

路由不依開發階段、任務主題、工具名稱、是否跑測試或是否發生一般錯誤。以下近似訊號本身不足：

- Linus：只看到 abstraction、舊程式碼或疑似 dead code。
- Lamport：只看到 `async`、queue、network 或一般錯誤處理。
- Carmack：只看到 performance 任務、loop、cache 或沒有數字的效能猜測。

多個濾鏡同時合格時，Router 只選證據最具體、最接近下一次決策的一個；不得為了輪替人物或輸出新鮮感選擇濾鏡。

## 5. Host 控制點

### Claude Code

- `UserPromptSubmit`：只記錄 `task_anchor`。
- `PostToolBatch`：同一模型步驟的工具全部完成後，收集完整 batch、呼叫 Router，必要時呼叫 Generator 並注入一則 Nudge。
- `Stop`：只記錄反應與診斷；不呼叫 Provider、不產生 Nudge、不延續回合。
- 移除以每個 `PostToolUse`／`PostToolUseFailure` 產生 Nudge 的路徑。

實作前重新核對 Claude Code 當前 `PostToolBatch` payload schema 與失敗結果表示法。

### Codex

- `UserPromptSubmit`：只記錄 `task_anchor`。
- 同步 `PostToolUse`：作為近似控制點；單一工具時接近理想窗口，平行工具時可能只看到部分結果且各自觸發。
- `Stop`：只記錄反應與診斷；不呼叫 Provider、不產生 Nudge、不延續回合。
- 不使用 timer、非穩定 transcript 或延遲補送來猜測 batch 結束。

Codex 的近似限制直接寫入 architecture、README 與 doctor；Host 與 hook event 已能表示現況，不新增 capability enum。Hosted tools 是否涵蓋依當前 Host 契約明示。

另準備一份 Codex 上游 issue 草稿，請求「同一模型步驟的所有工具完成後只觸發一次，並能在下一次模型 request 前注入 context」的 `PostToolBatch`。實際送出另行授權。

## 6. 最小修改面

| 區域 | 修改方向 |
|---|---|
| `buddy-prompt.txt` | 只保留身分、可知範圍與輸出契約 |
| `personas/` | 只保留並聚焦 Linus、Lamport、Carmack；刪除 Jeff、Beck、Fowler |
| `persona_config.py`、UI | registry 與選項只接受三個濾鏡；退休值回到 Automatic |
| `lens_router.py`、Router prompt | 只負責證據資格與單一濾鏡選擇；不產生或傳遞 routing hypothesis |
| `masters_nudge/checkpoints.py`、`evidence.py` | 只收集、限縮、排序與去重證據；移除 `first-change`、`repeated-failure-family` 和濾鏡語義判斷 |
| Packet builder | 只傳 `task_anchor` 與客觀 `evidence`；移除過去 Nudge 與主模型推理資訊 |
| `masters_nudge/prompting.py` | 固定 Base／單一 Filter／Runtime packet 分層 |
| `masters_nudge/provider_contract.py` | 只保留結構驗證 |
| Claude manifest／adapter | 改用 `PostToolBatch`；Stop observation-only |
| Codex manifest／adapter | 保留同步 `PostToolUse` 並公開近似限制；不自行聚合 batch |
| doctor、telemetry、文件 | 依 Host 與實際 hook event 顯示控制點與已知缺口 |
| plugin inventory、README、CHANGELOG | 移除退休濾鏡並更新安裝包內容與產品敘述 |

Repository source 是唯一實作來源；`plugins/masters-nudge/` 由既有 package builder 產生，不手動維護第二份分歧程式。

## 7. 實作順序與驗收

1. **Prompt 與設定契約**
   - Base prompt 不含濾鏡焦點、找盲點或要求唱反調的指令。
   - Packet 只含 `task_anchor` 與 `evidence`。
   - 只接受 Linus、Lamport、Carmack 與 `automatic`；退休值回到 Automatic。
   - Provider contract 只拒絕結構不合法的輸出。

2. **路由與 Generator ownership**
   - checkpoints 不選濾鏡；Router 是唯一選擇者。
   - Router 回傳一個濾鏡或 `none`，其理由不進入 Generator prompt。
   - Generator 只看到一個 Filter 與原始 packet。
   - 三個濾鏡各有足以發言與必須沉默的 fixtures；手動模式不繞過門檻。

3. **Host adapter**
   - Claude synthetic `PostToolBatch` 一個 batch 最多產生一次 attempt，成功與失敗結果都能成為 evidence。
   - Codex `PostToolUse` 保持 per-tool 行為，不以 timer 假裝 batch barrier。
   - 兩個 Host 的 Stop 都不呼叫 Provider、不輸出 Nudge、不延續回合。
   - doctor 與文件正確標示 Claude 精確控制點和 Codex 近似控制點。

4. **打包與回歸**
   - 更新文件、UI、plugin inventory 並重新產生安裝包。
   - 執行完整程式測試、generated-package 一致性檢查與 `git diff --check`。
   - 新鮮安裝後驗證兩個 Host 的 hook 註冊狀態。

程式測試只證明契約與 adapter 行為。品味是否可辨識，另以固定 packet 的盲測評估，不以 SWE-bench 通過率作為主要尺度。

## 8. 範圍邊界

- 不宣稱 Nudge 提升解題正確率或測試通過率。
- 不讓 Provider 審查完整 transcript、完整 repository 或主模型推理，也不要求找錯或反駁主模型。
- 不用 Stop 產生 review，不為 Codex 自製 batch barrier，也不把產品擴張成完整 App Server client。

完成標準：**每位大師只在自己的證據成立時，獨立形成一個具體工程取捨，並在 Host 能提供的最接近決策間隙中投下一票。**
