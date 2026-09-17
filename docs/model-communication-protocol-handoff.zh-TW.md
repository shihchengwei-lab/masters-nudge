# Masters’ Nudge 雙模型通訊協定交接單

日期：2026-09-15  
狀態：歷史草案，已由 [SPEC.zh-TW.md](../SPEC.zh-TW.md) 取代，不再作為目前實作或驗收依據。以下保留當時的討論內容。

## 一句結論

目前的 C 臂是「Actor 完成一批工具操作後，由 Provider 做一次事後評論」，不是雙模型協作。`PostToolBatch` 只能當事件通知；要做到自動、原生、可往返的模型通訊，終態需要修改 fork 的 Codex。通訊語意仍應先用不改 fork 的小型原型驗證，避免先動 Rust，最後才發現協定本身沒有價值。

## 目標

讓 `gpt-5.6-sol` Actor 在實作前，針對一個尚未決定的結構選擇，和 `gpt-6-astra` Provider 完成一次有狀態的短對話。Astra 提供 Actor 尚未想到的既有結構或否決前提；Sol 保留 repository 查證與實作責任。

成功時應看到：

- Sol 因 Astra 提供的新關係而刪掉或合併機制，而非新增旗標、分支、wrapper 或 transport identity 特例。
- Astra 不需要完整探索 repository，也不輸出 patch。
- Sol 能回傳查證結果，Astra 能確認或撤回先前判斷。
- 任務契約不下降；Astra 的時間與 token 明顯低於直接讓 Astra 完成整題。

## 已確認的問題

### `PostToolBatch` 的限制

`PostToolBatch` 只告訴 Host「這一批工具已經結束」，並把 Hook 的 `additionalContext` 放進下一次模型推論。它沒有表達：

- Sol 正在考慮哪個決策。
- 哪個約束必須保留。
- Astra 還缺哪項事實。
- Sol 如何回答 Astra。
- Astra 是否根據新證據撤回意見。
- Sol 最後接受或拒絕了什麼。

因此，無論如何修改 Nudge 文句，Astra 都只能從已發生的改動猜測意圖，角色自然退化成 reviewer。

### 已排除的方向

- 在 Nudge 外加一句「先驗證、成立就刪減」：Actor 仍改用另一個特例，成本更高。
- 在普通否決前加上「Linus 警報」：兩個候選的 Git tree 完全相同，只增加 token。
- 要 Astra 自己完整查看 repository：理解成本接近直接讓 Astra 實作，失去稀疏專家協作的價值。
- 繼續增加 source-context regex、caller 特例或手工 facts：這是在替不完整的單向 packet 補洞。
- 繼續調整 reviewer prompt：前幾輪沒有形成可重複的進步訊號。

相關報告：

- `E:\mnw2-20260913\nudge-delivery-wrapper-v1\results\DELIVERY_WRAPPER_REPORT.zh-TW.md`
- `E:\mnw2-20260913\linus-veto-prefix-v1\results\LINUS_VETO_PREFIX_REPORT.zh-TW.md`
- `experiments/fact-selector-20260913/REPORT.md`

## 最小通訊協定草案

協定發生在結構選擇仍可改變、尚未開始實作時：

```text
Sol: CONSULT
       ↓
Astra: QUESTION（可選，一個缺少的關鍵事實）
       ↓
Sol: EVIDENCE（查 repository 後回答）
       ↓
Astra: ADVICE（AFFORDANCE / VETO / PASS）
       ↓
Sol: RESOLVE（接受或拒絕及理由）
       ↓
Sol 才執行修改
```

最小語意：

- `CONSULT`：Sol 說明「準備做的選擇、必須保留的行為、目前不確定之處」。
- `QUESTION`：Astra 最多要求一項能改變選擇的可觀察事實；不得要求全面 review。
- `EVIDENCE`：Sol 使用既有工具查證並回覆結果；Astra 不直接接管 repository。
- `AFFORDANCE`：指出一個已存在、可讓新增機制消失的結構關係。
- `VETO`：指出目前選擇依賴的哪個前提已被證據推翻。
- `PASS`：沒有新增資訊。
- `RESOLVE`：Sol 明確接受或拒絕，避免同一意見反覆注入。

先不要設計大型 JSON schema、decision graph、call graph 或多輪 debate。第一版最多一次 `QUESTION → EVIDENCE` 往返。

## 是否需要修改 fork Codex

分成兩個階段：

### 協定原型：不用修改 fork

先用一個 Actor 可主動呼叫的 `consult` 工具，或用測試腳本依序呼叫 Sol 與 Astra。這一步只回答：「上述對話語意能否讓 Sol 找到減法解，而不再補特例？」

若做成產品內原型，可優先考慮 plugin 內的 MCP tool：

1. Sol 呼叫 `consult`，送出 `CONSULT`。
2. 工具呼叫 Astra 並回傳 `QUESTION` 或 `ADVICE`。
3. Sol 查證後可用同一 consultation id 再呼叫一次。
4. 工具保存這一次短對話，完成後關閉。

這條路能驗證協定，不必先維護 Codex Rust fork。風險是 Sol 可能不主動呼叫；該問題應獨立量測，不能先用自動 hook 掩蓋。

### 自動、原生整合：需要修改 fork

若產品要求「不用 Actor 主動呼叫，Host 能在正確決策點啟動對話」，現有 Hook／plugin surface 不足。fork 需要在模型取樣迴圈持有 consultation 狀態，並支援：

- 在實作前建立 `CONSULT`，而非從工具結果反推決策。
- 把 Provider 的問題送回同一個 Actor turn。
- 接收 Actor 的 `EVIDENCE`，再讓 Provider 確認或撤回。
- 將 `RESOLVE` 與 decision id 綁定，避免重複插話。
- timeout、取消與 Provider 失敗時讓 Actor 正常繼續。

`PostToolBatch` 最多保留為稽核／證據來源，不再負責啟動 Provider 或代表一個工程決策。

## 下一個 session 的最小工作

只做一題、先證明語意，不做完整三臂或論文級環境：

1. 使用之前會誘發 `payloadAlreadySent`／`sendPostFunc !== _beaconSender` 的 AppInsights 題。
2. 固定 Sol=`gpt-5.6-sol`、Astra=`gpt-6-astra`。
3. 在 Sol 修改前，人工或腳本執行一次上述協定；最多一輪追問。
4. 保留完整模型輸入、輸出、Git diff、時間與 token。
5. 和同題 direct Sol 候選比較：任務契約、是否新增特例、是否使用既有 owner、時間與 token。

停止條件：

- Astra 要求全面讀 repository 或直接產生 patch：協定已退化成 Astra 實作，停止。
- Sol 仍以新旗標、分支、wrapper 或 identity check 回應：本協定沒有解除發散，停止。
- Astra consultation 成本接近直接 Astra 實作：雙模型架構沒有成本優勢，停止。

通過這個單題門檻後，才決定是否做 MCP 原型；MCP 原型通過後，才考慮修改 fork。

## Repository 現況與限制

### Masters’ Nudge

- 路徑：`C:\Users\kk789\Desktop\GH_repos\masters-nudge`
- 分支：`codex/structural-event-contract-v0.5.0`
- 本交接前 HEAD：`68cd5f22e84ddc0cab020ec37b338f480731f7b9`
- 工作樹已有多個未提交修改與 `experiments/`；全部視為既有工作，不要回滾或覆寫。
- 目前沒有授權 commit、push、安裝或發布。

### Codex fork

- 路徑：`C:\Users\kk789\Desktop\GCA\codex`
- 分支：`local/post-tool-batch`
- 目前 HEAD：`2436f469b550bfb8cd1b3c9c334930c186046aae`
- 2026-09-15 查看到 `codex-rs/core/tests/suite/hooks.rs` 有未提交修改；先釐清來源，不要覆寫。
- 舊實作報告：`C:\Users\kk789\Desktop\GCA\POST_TOOL_BATCH_IMPLEMENTATION_REPORT.md`

## 執行注意事項

- 不要把新的協定塞回 `PostToolBatch` payload；那會重建同一個 reviewer 架構。
- 不要先替所有訊息設計通用框架；只實作單題需要的最小往返。
- 所有實測結束後，關閉該次測試啟動的 Codex CLI，取回記憶體；不要誤關 Windows 桌面版 Codex。
- 報告要分開「協定語意有效」與「fork 整合可行」，兩者不能互相代替。
