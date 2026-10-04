# Masters’ Nudge 模型配置對比報告

> **十二題原始研究紀錄。** 本報告保留每臂24次、全部168次的原始統計與匿名初評；現行主要完成率與成本採九題、每臂18次，見[九題主要報告](PRIMARY.zh-TW.md)。三題另列為[未解挑戰](../unresolved-challenges-20261004/README.zh-TW.md)。這是事後分類；答案、判分與原始數據未改。品味最終結果見覆核複評。

本報告比較直接實作與加入結構提醒，以及不同模型與思考深度，對完整交付、程式結構與成本的影響。測試日期：2026-09-30 至 2026-10-04。範圍：12 題、七種配置，每題每配置各跑兩次，共 **168 份交付**。

**品味評分階段：本報告保存匿名盲評的初評數字。最終採用[程式碼覆核複評](taste-review/README.zh-TW.md)：I 對 C 為七勝零敗、四持平；I 對 F 為五勝零敗、四持平。** 複評已知組別與初評結果，沒有重跑 Actor 或新增匿名評審票；完整交付、時間、Token 與原始紀錄不變。

**完整交付與時間效率優先，這批結果首選 C：Sol xhigh 直接做；願意增加用量換取結構品味，I：Sol xhigh＋Sol xhigh 有收益。** I 與 C 同為 13/24，匿名品味九勝零敗、兩持平，時間增加 26.9%；I 相對 F 多完成兩份，品味五勝兩敗、兩持平，時間減少 0.6%、未快取輸入增加 14.5%。保留 medium Actor 時，B 相對 A 仍有交付與結構收益。

## 1. 工具、研究問題與七臂條件

Masters’ Nudge 是實作途中的結構建議工具。**Actor** 是負責修改與驗證程式的 AI；**Provider** 是唯讀程式的另一個 AI，根據任務、當次修改與必要程式關係，提出簡短建議。Actor 決定如何採納並完成交付，Provider 不直接修程式。

研究比較增加提醒、提高 Actor 深度、換 Provider 模型，以及提高 Provider 深度，對契約完成、結構品味與成本的影響。Sol 指 **GPT-6.1 Sol**，Astra 指 **GPT-6 Astra**；medium 與 xhigh 是思考深度設定。

| 臂 | Actor 模型 | Actor 深度 | Provider 模型 | Provider 深度 | Nudge | 執行檔版本 |
|---|---|---|---|---|---|---|
| A | GPT-6.1 Sol | medium | 無 | 無 | 關閉 | 0.159.0 |
| B | GPT-6.1 Sol | medium | GPT-6.1 Sol | medium | 啟用 | 0.159.0 |
| C | GPT-6.1 Sol | xhigh | 無 | 無 | 關閉 | 0.159.0 |
| D | GPT-6.1 Sol | medium | GPT-6 Astra | medium | 啟用 | 0.159.2 |
| E | GPT-6.1 Sol | xhigh | GPT-6 Astra | medium | 啟用 | 0.159.2 |
| F | GPT-6.1 Sol | xhigh | GPT-6.1 Sol | medium | 啟用 | 0.159.2 |
| I | GPT-6.1 Sol | xhigh | GPT-6.1 Sol | xhigh | 啟用 | 0.159.2 |

共同條件：每臂 24 次嘗試、兩個工作槽並行、每次 Actor 上限 1,800 秒，包含等待 Provider；Provider 呼叫上限 1,200 秒、Hook 上限 1,320 秒。提醒臂最多送達三則建議，兩次沉默後停止提醒；A/C 實際沒有 Provider。每次從該題相同基底獨立開始，使用相同中性任務提示、預裝依賴、固定驗收與品味準則；個人規則與其他外掛不加入 Actor 條件。彙整程式核對了 168 份實際啟動與結果紀錄，以及各題七臂任務提示一致。

B/D/E/F/I 使用同一定稿語意提示、欄位與工具邏輯。Provider 先從完整交付結果回推容易遺漏的要求，填入 `required`；再追查目前資料結構在哪裡混同或丟失必要資訊、因而需要補救，提出可檢查的替代關係，填入 `structure`。另兩欄為 `observed`（可見程式關係）與 `why`（對任務的影響）。四欄各有 40／25／61／35 字元限制，含標籤的總呈現上限 200 字元。檔案是否原本存在以 `file_origin` 事實提供，讓新增測試與修改既有測試可被區分。實際英文提示、schema 與工具程式保存在 [定稿工具](protocol/nudge-plugin/buddy-prompt.txt)。I 的[實驗工具快照](protocol/nudge-plugin-I/masters_nudge/runtime.py)只把 Provider 深度常數由 medium 改為 xhigh；正式產品仍固定 medium，沒有新增深度設定介面。

七臂分輪執行，A 是封存的直接實作基準，B 至 F 與 I 是後續交付。A/B/C 使用 0.159.0，D/E/F/I 使用 0.159.2。I-F 的模型、Actor 深度、CLI、提示與驗收相同，配置變因是 Provider medium→xhigh；I 的執行器另有逾時終止與驗收錯配修復，見 4.3。I-C 含 CLI 版本差異。模型呼叫發生於不同時間，本報告評的是這批配置的實際收益。

## 2. 排名速覽

`>` 表示此項表現較好；`=` 表示本批數值相同，或品味勝負總數打平。時間與 Token 排名以**較少為較好**；這些符號沒有統計等價檢定的意思。

| 評比 | 本批關係 | 讀法 |
|---|---|---|
| 完整交付份數 | **C = I > F > E > B = D > A** | 功能、執行規則、時限及相容性補查都通過 |
| 功能通過，不計交付時間 | I > C = F > E > B = D > A | 用來區分程式錯誤與收尾超時 |
| 至少一次完成的題數 | F = I > C = E > B = D > A | 解到的題型範圍 |
| 兩次都完成的題數 | C > I > A = B = D = E = F | 同題兩次均完成的觀察結果 |
| 累計時間較少 | A > D > B > E > C > I > F | 全部 24 次 Actor 耗時相加，含失敗與等待 Provider |
| 每完成一份的時間較少 | **C > D > B > E > I > A > F** | 總時間除以完整交付份數，含失敗成本 |
| 未快取輸入 Token 較少 | A > C > D > B > E > F > I | 七臂共同 19 個有完整用量的題目／次序位置 |
| 快取輸入 Token 較少 | A > D > C > B > E > F > I | 同一批 19 個位置 |
| 輸出 Token 較少 | A > D > B > C > E > F > I | 同一批 19 個位置 |

程式碼品味只列直接比較：**B > A、C > A、D > A、B = C、B > D、D > E、C = F、F > E、I > C、I > F**。每組共同完成的樣本不同，不能把這些關係串成七臂總排名。例如 I-B 未比較，不能由 I > C 且 B = C 推出 I > B。

## 3. 題目與驗收契約

12 題來自實際開源專案，涉及資料表示、非同步狀態、相容性、介面整合與跨層責任。題目與驗收曾在準備階段澄清、校準；本研究以已固定的 `task.md` 為契約，並以 `contract.json` 將每項要求連到檢查。來源連結提供題目出處，判分依據是包內契約。

| 題目／完整契約 | 來源專案 | 語言 | 主要交付要求 |
|---|---|---|---|
| [nodebb-images](protocol/evaluation/cases/nodebb-images/task.md) | [NodeBB/NodeBB](https://github.com/NodeBB/NodeBB/commit/8168c6c4) | JavaScript | 依擁有者與圖片類別刪除全部相關檔案，保留其他人的檔案與原介面行為。 |
| [ansible-type-tags](protocol/evaluation/cases/ansible-type-tags/task.md) | [ansible/ansible](https://github.com/ansible/ansible/commit/d33bedc4) | Python | 型別轉換保留信任與來源標記，正確處理布林、位元組、序列、映射及空值。 |
| [element-sessions](protocol/evaluation/cases/element-sessions/task.md) | [element-hq/element-web](https://github.com/element-hq/element-web/commit/772df302) | TypeScript／React | 多裝置勾選、計數、取消與單次批次登出；篩選切換、刷新及驗證取消保持一致。 |
| [flipt-segments](protocol/evaluation/cases/flipt-segments/task.md) | [flipt-io/flipt](https://github.com/flipt-io/flipt/commit/524f2773) | Go | 支援單一／多分群的匯入、匯出與儲存，保留 rollout 原有格式與既有行為。 |
| [openlibrary-index-state](protocol/evaluation/cases/openlibrary-index-state/task.md) | [internetarchive/openlibrary](https://github.com/internetarchive/openlibrary/commit/322d7a46cdc965bfabbf9500e98fde098c9d95b2) | Python | 按作品、作者、版本分別更新索引，處理孤立版本，並回傳可檢查的新增與刪除結果。 |
| [proton-mailbox-retry](protocol/evaluation/cases/proton-mailbox-retry/task.md) | [protonmail/webclients](https://github.com/protonmail/webclients/commit/e65cc5f33719e02e1c378146fb981d27bc24bdf4) | TypeScript／React | 修改操作期間暫緩抓取；失敗與陳舊回應需重試，保留未完成刷新與載入狀態。 |
| [flipt-storage-cache](protocol/evaluation/cases/flipt-storage-cache/task.md) | [flipt-io/flipt](https://github.com/flipt-io/flipt/commit/e2bd19dafa7166c96b082fb2a59eb54b4be0d778) | Go | 讓儲存層查詢也使用快取，識別 no-store 請求並禁止寫入快取。 |
| [fb-metaflow-stubs](protocol/evaluation/cases/fb-metaflow-stubs/task.md) | [Netflix/metaflow](https://huggingface.co/datasets/LiberCoders/FeatureBench) | Python | 由執行時物件產生型別描述檔，保留類別、函式簽名、註記、overload 與模組狀態。 |
| [tracing-1523](protocol/evaluation/cases/tracing-1523/task.md) | [tokio-rs/tracing](https://github.com/tokio-rs/tracing/pull/1523) | Rust | 各記錄層有獨立過濾視圖，包含巢狀關係、事件、span、上下文與快取判斷。 |
| [proton-untrusted-keys](protocol/evaluation/cases/proton-untrusted-keys/task.md) | [protonmail/webclients](https://github.com/protonmail/webclients/commit/715dbd4e6999499cd2a576a532d8214f75189116) | TypeScript／React | 區分固定與不可信金鑰的加密偏好，保留使用者關閉選擇、預設行為、儲存與上傳。 |
| [regexp-404](protocol/evaluation/cases/regexp-404/task.md) | [ota-meshi/eslint-plugin-regexp](https://github.com/ota-meshi/eslint-plugin-regexp/pull/404) | TypeScript／JavaScript | 把字元集合納入重複分支分析，保持比對方向、順序與安全修正行為。 |
| [clap-2297](protocol/evaluation/cases/clap-2297/task.md) | [clap-rs/clap](https://github.com/clap-rs/clap/pull/2297) | Rust | 按每次參數出現分組取得值，正確處理自我覆寫，保留既有出現次數語意。 |

完整 [題目清單](protocol/evaluation/cases.json) 包含原專案、來源、基底提交版本及環境映像指紋；各題目連結旁的資料夾包含要求對照、原測試清單與補充驗收。各題等權，不加入難度或商業價值權重；兩次嘗試不是兩道不同題目。

## 4. 測試 harness：如何執行、判分與保留證據

Harness 是負責安排實驗、執行固定檢查及收集紀錄的程式。它與 Nudge 工具的責任分開：不替 Actor 修答案，也不靠建議文字的句型或數量判定程式品味。

| 階段 | 實際工作 | 可核對材料 |
|---|---|---|
| 固定條件 | 封存題目、基底、提示、工具、模型深度、執行檔與依賴指紋 | `data/plans/A.json` 至 `F.json`、各臂來源 manifest |
| I 臂追加 | 封存 xhigh Provider 實驗覆寫、24 份原答案、C-I/F-I 原票及修復紀錄 | `data/plans/I.json`、`harness/I/`、`data/provenance/I/` |
| 預檢 | 檢查 12 題來源、依賴與映像可用，隔離全域設定 | 各臂 `preflight.py` 與原始檢查紀錄 |
| Actor 實作 | 還原該題基底，啟動指定模型；保存命令、改檔、最終 patch、用量及耗時 | 每次 `launch.json`、`prompt.txt`、`actor-events.jsonl`、`result.json` |
| Provider 提醒 | 修改批次觸發，提供最新任務、當次程式關係、檔案來源與前次建議；必要時唯讀查庫 | `provider-attempts.json` 與工具追蹤；有建議、沉默、故障分開記錄 |
| 功能檢查 | 將原交付放進固定驗收環境，執行原測試與已封存補充檢查 | `evaluation/<臂>/<題目>/<次序>/` 日誌、`score-v3.json` |
| 執行規則審核 | Astra medium 讀 Actor 原指令、命令與修改紀錄，核對範圍、時限及禁止動作 | `execution-evidence.json`、`execution-review.json`、評審原始輸出 |
| 相容性補查 | 對所有臂以同一輸入檢查兩項已確認原條款，保留原分數另算修正版 | `data/diagnostics/`、原生日誌與 fixture |
| 品味盲評 | 將雙方完整交付匿名為 X/Y，讀實際程式關係，交換順序評兩次，分歧才第三次 | 匿名 mapping、每張原始票、唯讀紀錄與 `pair.json` |
| 收尾 | 核對原始交付未變、測試環境還原，重建數據與報告 | `source-index.json`、`collection.json`、`integrity.json` |

Actor 可以新增自己的測試，不能修改、刪除或替換既有測試；任務也禁止提交、安裝套件、查 Git 歷史、用外部網路、讀其他題目或參考解、委派其他 Agent。公開檢查 helper 與預裝工具依任務規則可用。執行審核沿實際動作判斷，不把命令中出現 `git` 或 `install` 等字串直接當成違規。

功能檢查按題目使用固定容器或原生工具。環境資料包括映像 SHA、Windows 原生 Node／Cargo／Rust 版本及 Regexp 的預裝依賴，見 [環境資料](protocol/evaluation/environment.json) 與題目清單。Actor 看不到補充判分材料、其他臂交付與評審票。

### 4.1 完整交付的判定

**完整交付 = 全部固定功能檢查通過 + 執行規則通過 + 相同原條款補查通過。** 每次 30 分鐘限制包含在執行條件內。所有 24 次嘗試都進入完成率與時間分母；失敗、超時及工具故障保留，不因結果不好再抽一次答案。

原驗收遺漏的兩項相容性條款，後來在盲評中被發現，分別是：

1. **Flipt rollout 舊格式**：仍須匯出 `segment: {key: <值>, value: <布林>}`，不能把單元素清單改成新的 `keys` 格式。
2. **Clap 既有出現次數**：自我覆寫後的值可被替換，但不能將原本應保留的 `occurrences` 計數從 2 改成 1。

補查對七臂各兩份交付使用相同 fixture；Clap 另保留原基底正向對照。這是原條款的驗收補足，原始 `score-v3.json` 不覆寫。只在有一致補查證據時調整報告口徑。尚未執行確認的 NodeBB／郵箱重試靜態疑點另存評審紀錄，不自動加入完成率扣分。

| 補查 | fixture SHA-256 |
|---|---|
| Flipt | `6800a89c0be79a8fa85ab53336db49db3733ddf1be280c0256338beccf663db3` |
| Clap | `896290bc8d936448f0f4107c299c10e1b8eba447b72bf5c651e4a8c3e60bfe44` |

確認缺口：Clap B1；Flipt D1；Flipt E2 與 Clap E2；Flipt F2。其餘同項補查通過。

### 4.2 品味如何判斷

兩個隔離的 **GPT-6 Astra medium** 呼叫只看契約、共同基底與匿名 X/Y 實際程式，依需要唯讀查找；不看臂名、Provider 建議、Actor 推理、其他評審意見或參考解。第二次交換 X/Y；兩次不同時加入第三次，多數決，三種結果各一票則持平。

評審使用六項準則：非法狀態難以建立、資料流單向、局部行為可預測、單一事實來源、複雜度留在必要邊界、抽象能消除概念或分支。Provider 把最後兩項合為第五條；評審分列六項。評審結合任務判斷取捨，必須指出實際位置與影響；不把行數、helper 數、測試量或接近參考解程度換成機械分數。完整 [盲評規則](protocol/evaluation/blind-rubric.txt) 隨包保存。

### 4.3 故障與材料版本

真實解題失敗不重抽。基礎設施故障則保留原紀錄，處理故障後接續尚未完成部分：D 的同版本舊執行檔無法啟動 Sol，使用者同意換成已驗證的桌面版；D 有一次服務容量中斷，在零修改、零 Provider 的狀態下接續；C 一次執行審核讀檔工具失效，只恢復審核，沒有重跑 Actor。Clap 初版診斷 fixture 先被原基底拒絕，保留為無效對照；修正測量工具並通過基底對照後，才採用有效補查。較早驗收中的 Defender 隔離事件也保留獨立環境證據，未當作 Actor 修改測試。

I 有三項修復，全部保存原始紀錄、來源前後快照與判定依據：

1. **NodeBB I1 初次容量故障**：零改碼、零 Provider 呼叫、空 patch，另存原嘗試後等待五分鐘接續。額外 Actor 17.172 秒與驗收 32.853 秒另列，不當作第二次解題成果。
2. **Tracing I1 逾時清理故障**：無效的 `taskkill /T /I` 未終止子程序，改為 `/T /F`。原 17 份結果保留，只執行剩餘六份。無法可靠還原截止當下 patch，I1 記為逾時失敗、`final.patch` 為空；原事件與 `after-deadline.patch` 保留供審計，逾時後內容不算交付。時間按上限 1,800 秒記帳，額外 291.651 秒另列；終止碼與完整 Actor Token 缺失，Token 配對排除。
3. **NodeBB I1 驗收錯配**：固定驗收曾沿用初次容量故障的空 patch。指紋核對發現後，保存錯配驗收，對同一現有答案重做固定檢查、接續判分；沒有重跑 Actor。修正驗收耗時 39.219 秒另列。

修復資料位於證據包 `infrastructure/I/`、[I 來源紀錄](data/provenance/I/)與 `harness/I/`。原 17 份及全部 24 份 Actor 結果的保留指紋均已核對。I 的原 `final-integrity.json` 中 `same_frozen_cli_as_E` 是沿用的欄位名；本包另以計畫與 CLI 指紋核對 I、F 相同，不把欄位名稱當成配置依據。

當前七臂條件以封存 `plan.json`、實際 `launch.json` 與任務提示為準。共用評測來源中的舊 `PROTOCOL.zh-TW.md` 尚保留較早 GPT-6／題尾措辭的研究說明；本輪 Actor 全部為 GPT-6.1 Sol、相同中性任務，已逐份核對。A 計畫中的舊 Provider 提示指紋沒有用於 A 執行，因為 A 沒有 Provider。

## 5. 契約完成與逐題結果

| 臂 | 完整交付 | 至少一次完成的題數 | 兩次都完成的題數 | 累計分鐘 | 每完成一份的分鐘 |
|---|---|---|---|---|---|
| A | 6/24（25.0%） | 3/12 | 3/12 | 259.3 | 43.2 |
| B | 8/24（33.3%） | 5/12 | 3/12 | 296.0 | 37.0 |
| C | 13/24（54.2%） | 7/12 | 6/12 | 393.9 | 30.3 |
| D | 8/24（33.3%） | 5/12 | 3/12 | 273.1 | 34.1 |
| E | 10/24（41.7%） | 7/12 | 3/12 | 383.8 | 38.4 |
| F | 11/24（45.8%） | 8/12 | 3/12 | 502.9 | 45.7 |
| I | 13/24（54.2%） | 8/12 | 5/12 | 499.9 | 38.5 |

累計分鐘是每次 Actor 的實際經過時間相加，含等待 Provider 與失敗嘗試；不是七臂研究的總等候時間，也不包含測試判分、品味評審與補查。每完成一份的分鐘，使用全部 24 次嘗試耗時除以完整交付份數。

原凍結完成、補查修正與純功能結果分開如下：

| 臂 | 原凍結完成 | 相容性補查後完整交付 | 功能通過、不計交付時間 |
|---|---|---|---|
| A | 6 | 6 | 6 |
| B | 9 | 8 | 8 |
| C | 13 | 13 | 13 |
| D | 9 | 8 | 8 |
| E | 12 | 10 | 10 |
| F | 12 | 11 | 13 |
| I | 13 | 13 | 14 |

F 的 NodeBB1、Clap1 與 I 的 Clap1 功能及相容性檢查通過，卻未在時限內完成交付。因此 I 功能通過 14 份、完整交付 13 份；C/F 功能各 13 份，完整交付分別 13／11。F 五份超時、I 三份，A/C/E 各兩份、B 一份、D 零份；實際名單在完整數據中。Tracing I1 的截止 patch 不可還原，沒有計入功能通過。

| 題目 | A | B | C | D | E | F | I |
|---|---|---|---|---|---|---|---|
| nodebb-images | 0/2 | 1/2 | 2/2 | 0/2 | 0/2 | 1/2 | 0/2 |
| ansible-type-tags | 0/2 | 1/2 | 1/2 | 0/2 | 1/2 | 1/2 | 1/2 |
| element-sessions | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| flipt-segments | 2/2 | 2/2 | 2/2 | 1/2 | 1/2 | 1/2 | 2/2 |
| openlibrary-index-state | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 1/2 | 1/2 |
| proton-mailbox-retry | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 | 2/2 |
| flipt-storage-cache | 0/2 | 0/2 | 2/2 | 0/2 | 1/2 | 2/2 | 2/2 |
| fb-metaflow-stubs | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| tracing-1523 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| proton-untrusted-keys | 0/2 | 0/2 | 2/2 | 1/2 | 2/2 | 0/2 | 2/2 |
| regexp-404 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 | 0/2 |
| clap-2297 | 0/2 | 0/2 | 0/2 | 2/2 | 1/2 | 1/2 | 1/2 |

C 解到七題，其中六題兩次完成；F 與 I 各解到八題，分別三題／五題兩次完成。I 相對 F 在 Flipt 分群、不可信金鑰增加完成，但 NodeBB 仍為零。Clap 是 D 兩次完成、I 一次完成、C 兩次未完成，顯示總體排名仍有題型差異。Metaflow、Tracing、Regexp 在七臂都未完整交付。

## 6. 程式碼品味初評：匿名盲評

只比較雙方完整交付的同題／同次序配對，保留原始票；確認契約缺口後，移除不再符合完整交付條件的品味配對，沒有重評或換票。本報告沿用已做的十組直接比較，共 71 個可評配對；I 新增的 C-I、F-I 分別有 11／9 個配對。

| 直接比較 | 共同完整配對 | 前者勝 | 後者勝 | 持平 | 本批關係 |
|---|---|---|---|---|---|
| A-B | 6 | 1 | 5 | 0 | B > A |
| A-C | 6 | 2 | 4 | 0 | C > A |
| B-C | 8 | 4 | 4 | 0 | B = C |
| A-D | 5 | 0 | 5 | 0 | D > A |
| B-D | 5 | 2 | 1 | 2 | B > D |
| D-E | 6 | 5 | 1 | 0 | D > E |
| C-F | 8 | 3 | 3 | 2 | C = F |
| E-F | 7 | 0 | 7 | 0 | F > E |
| C-I | 11 | 0 | 9 | 2 | I > C |
| F-I | 9 | 2 | 5 | 2 | I > F |

未直接評的組合為 **A-E、A-F、A-I、B-E、B-F、B-I、C-D、C-E、D-F、D-I、E-I**。各組樣本不同，單組 `>` 不具有跨組傳遞性。

結構差異的具體例子：

- **F 勝 C，Element 兩份**：將「選取值」與「更新選取的方法」成對提供、共同決定來源，避免畫面讀外部狀態卻修改內部狀態。F1 的提醒指出這個關係，最後程式也採納。
- **C 勝 F，Flipt 第一份**：把格式差異集中在 segment 型別；F 在整份規則讀寫中重述資料對應，新增欄位要同步多處。
- **C 勝 F，郵箱重試第一份**：回應與延遲重試綁定發起請求，非同步工作的歸屬較清楚。
- **F 勝 C，郵箱重試第二份**：區分已發出的請求與後來新增的刷新義務，較早的回應不會抹掉較晚的要求。
- **C = F，快取兩份**：兩位評審均未看見足以決定勝負的結構差異。
- **I 勝 C，Flipt 第一份**：兩種輸入格式在解碼邊界收斂為單一 `Keys` 表示，下游不用維持 `Key/Keys` 優先關係；SQL 用局部值推導 operator，避免改寫呼叫者請求。
- **I 勝 C，不可信金鑰第一份**：保留 pinned／untrusted 各自偏好，初始化與來源切換共用同一選擇規則；C 只留下合併值，切換來源時沿用前一來源選擇。評審也指出 I 仍有衍生狀態同步代價，勝出不代表沒有弱點。

為了檢查不同共同完成樣本對結論的影響，可再將既有票投影到七臂都完成的四份：Element 兩份與郵箱重試兩份。這只是同一批原票的子集，沒有新增評審。

| 直接比較 | 前者勝 | 後者勝 | 持平 |
|---|---|---|---|
| A-B | 0 | 4 | 0 |
| A-C | 2 | 2 | 0 |
| B-C | 3 | 1 | 0 |
| A-D | 0 | 4 | 0 |
| B-D | 2 | 0 | 2 |
| D-E | 4 | 0 | 0 |
| C-F | 1 | 3 | 0 |
| E-F | 0 | 4 | 0 |
| C-I | 0 | 4 | 0 |
| F-I | 1 | 2 | 1 |

這個子集顯示部分提醒臂的結構優勢，但主要品味表仍保留各組所有符合條件的配對，不能只挑有利的子集代替總表。

## 7. 花費、提醒與品質斷點

### 7.1 時間與 Token

時間效率關係：**C > D > B > E > I > A > F**。C 每份完整交付的時間最低。I 累計 499.9 分鐘、每完成一份 38.5 分鐘；F 累計耗時最高、完整交付較 C/I 少兩份，單位交付時間最高。

七臂 Token 使用共同 **19/24 個題目／次序位置**，提醒臂計 Actor＋Provider，直接做的臂只計 Actor。共同排除 NodeBB 第一次、Tracing 兩次、Regexp 第二次、Clap 第一次；至少一臂缺少完整 Actor 用量，不能把缺值當零。完成率與時間仍使用全部 24 次。此分母與原 A–F 總覽相同；I-C 另有 21 份配對的用量表。

| 臂 | 未快取輸入 Token | 快取輸入 Token | 輸出 Token |
|---|---|---|---|
| A | 1,158,877 | 12,801,408 | 168,348 |
| B | 2,189,474 | 27,920,000 | 260,063 |
| C | 1,959,887 | 27,412,608 | 386,774 |
| D | 2,096,173 | 21,635,072 | 222,997 |
| E | 2,587,243 | 34,152,576 | 422,577 |
| F | 2,961,902 | 43,205,760 | 473,977 |
| I | 3,392,221 | 51,838,720 | 557,983 |

未快取輸入、快取輸入與輸出分開呈現。沒有逐次金額帳單，也沒有合併成貨幣成本；Astra 與 Sol 的 Token 不視為同單價。以已有紀錄比較，F 對 C 的未快取輸入增加 51.1%、輸出增加 22.5%；對 E 分別增加 14.5%、12.2%。F 的累計時間對 C 增加 27.7%、對 E 增加 31.0%。

七臂共同 19 份口徑下，I 對 C 未快取輸入增加 **73.1%**、快取輸入增加 **89.1%**、輸出增加 **44.3%**。另用 I 與每個對照各自完整的用量位置，重算如下；I-C 的 21 份與共同 19 份不能混用：

| I 相對 | 完整交付變化 | I 勝／對方勝／持平 | 24 份時間變化 | Token 配對數 | 未快取輸入變化 | 快取輸入變化 | 輸出變化 |
|---|---|---|---|---|---|---|---|
| C | 0 | 9/0/2 | +26.9% | 21 | +71.4% | +90.6% | +42.8% |
| F | 2 | 5/2/2 | -0.6% | 19 | +14.5% | +20.0% | +17.7% |

I 對 F：契約與品味**進步**，時間**持平（減少 0.6%）**，Token 成本**退步**。I 對 C：契約**持平**、品味**進步**，時間與 Token 成本**退步**。「時間持平」指本批差距很小，沒有等價檢定。I-C 21 份只排除 Tracing 兩次與 Clap 第一次；I-F 19 份與七臂共同分母相同。

新增 B 至 F 與 I 研究所記錄的評審開銷另列，包含原始評審與已記錄的審核恢復；A 基準先前建立的成本不混入這張表。固定驗收、原生補查的執行日誌與耗時留在證據包，均不混入 Actor 時間。

| 新增研究 | 評審呼叫 | 累計分鐘 | 輸入 Token | 快取輸入 Token | 輸出 Token |
|---|---|---|---|---|---|
| B | 37 | 26.3 | 2,838,017 | 1,842,560 | 36,758 |
| C | 54 | 38.5 | 4,599,267 | 3,004,160 | 52,968 |
| D | 52 | 42.0 | 4,896,878 | 3,346,560 | 56,701 |
| E | 36 | 23.8 | 2,747,086 | 1,745,280 | 34,420 |
| F | 56 | 49.8 | 4,882,285 | 3,270,912 | 56,286 |
| I | 67 | 55.8 | 6,003,115 | 4,031,488 | 68,295 |

### 7.2 提醒不是採納率

| 臂 | 收到提醒的交付 | 送達提醒 | Provider 故障 | 執行規則通過 | 超時 |
|---|---|---|---|---|---|
| A | 0/24 | 0 | 0 | 22/24 | 2 |
| B | 21/24 | 46 | 0 | 23/24 | 1 |
| C | 0/24 | 0 | 0 | 22/24 | 2 |
| D | 17/24 | 33 | 0 | 24/24 | 0 |
| E | 18/24 | 27 | 0 | 22/24 | 2 |
| F | 21/24 | 41 | 0 | 19/24 | 5 |
| I | 21/24 | 40 | 0 | 21/24 | 3 |

B/D/E/F/I 合計送達 **187 則**提醒，Provider 故障均為零。I 收到 40 則，21/24 份交付至少收到一則。這表示傳遞正常，不表示每則建議都正確、被採納或使交付改善。

這批七臂沒有對 187 則提醒作一致的真／誤報、內容品質與採納標註，因此不提供這三項的百分比排名，也不沿用較早提示版本的標籤。提醒內容、當時程式與後續 patch 都已保存，可供逐則審計；本報告以共同完整交付的匿名品味結果評估結構收益。Element F1 與首頁的 A1/B1 對照是可追溯案例，不能用單一案例代表整體採納率。

E 相對 D 新增的四份完整交付都沒有收到提醒；因此那四份不能被算成 Provider 建議的採納成果。Provider 零故障也不能消除選題、內容品質、Actor 實作與收尾時間的差異。

## 8. 本批效益判斷

| 使用目標 | 本批選擇 | 依據 |
|---|---|---|
| 優先完整交付與時間效率 | **C：Sol xhigh 直接做** | 完成 13/24、六題兩次完成；每完成份耗時最低 |
| 保留 medium Actor，重視結構改善 | **B：Sol medium＋Sol medium** | 對 A 完成多兩份、共同完成品味五勝一敗；對 D 完成持平、品味較佳 |
| xhigh Actor 願意增加 Token 換結構品質 | **I：Sol xhigh Provider** | 對 C 完成持平、品味九勝零敗；對 F 完成多兩份、品味五勝兩敗，時間相近但用量更高 |
| 希望解到更多題型 | **F = I** | 各八題至少一次完成；I 五題兩次完成，F 三題；Metaflow／Tracing／Regexp 均未突破 |

提高 Actor 深度有交付收益：A→C 多七份，D→E 多兩份；品味沒有普遍隨深度提升，C 對 B 打平、E 對 D 一勝五敗。提高 Sol Provider 深度的 F→I，則在這批觀察到交付與品味改善；I 與 C 完成總數相同，但不是相同 13 份：共同完成 11 份，I-only 與 C-only 各兩份。I-F 共同完成九份、I-only 四份、F-only 兩份。

若目標是「契約完成不下降、品味提高」，B 相對 A、I 相對 C/F 顯示收益，F 相對 C 沒有達成。是否值得額外成本需依使用目標選擇，沒有預設金額門檻。I 的 xhigh Provider 是實驗覆寫，正式產品仍固定 medium。12 題各兩次是固定題組的觀察，沒有把 168 份交付當成 168 道獨立題目宣稱統計顯著性。

## 9. 陌生讀者如何審計或重建

本資料夾可整體移到另一台電腦。統計重建只需 Python 3.11 以上與標準函式庫，無需模型金鑰、原 D/E 槽或網路。從資料夾開啟 PowerShell：

```powershell
python -X utf8 .\aggregate.py --verify
```

這會逐份核對證據指紋、實際模型／深度／基底／提示／時限，從原固定分數與相同補查重算 168 份交付，重建配對品味及七臂共同 Token 分母，並與現有 JSON、CSV、報告比對。要重新產生統計與報告則執行：

```powershell
python -X utf8 .\aggregate.py
```

這兩個命令都不重跑 AI 或修改交付。`collect.py` 是本次從本機原始封存材料建立證據包的收集程式；`aggregate.py` 是離線彙整程式。重跑 Actor 實驗則需復原各臂相應 harness、原專案基底、預裝依賴與指定 CLI；相關程式快照與步驟見 [harness 說明](HARNESS.zh-TW.md)。原始專案檢出、依賴映像與 CLI 二進位未收入本包。

| 材料 | 用途 |
|---|---|
| [完整數據](results-summary.json) | 168 份判定、失敗檢查、補查缺口、用量、配對票與排名 |
| [交付明細 CSV](deliveries.csv) | 可用試算表核對每題／臂／次序與 patch 指紋 |
| [原始證據包](evidence.zip) | 所有七臂 run、固定驗收日誌、執行審核、已有盲評票與原生補查；解壓可直接閱讀 |
| [來源索引](source-index.json) | 每個檔案的原始位置、包內位置與 SHA-256 |
| [收集紀錄](collection.json) | 原始來源未變、證據包大小與指紋；沒有新增解題或評審 |
| [完整性結果](integrity.json) | 程式、模板、報告、摘要、CSV 與證據包指紋 |
| `data/plans/`、`harness/` | 七臂封存計畫與實際程式來源快照 |
| `protocol/evaluation/` | 完整契約、驗收程式、測試、評審規則與上游授權說明 |
| `protocol/nudge-plugin/`、`protocol/nudge-plugin-I/` | 定稿提示、欄位限制與 medium／xhigh 實驗工具快照 |

建議審計順序：先選一題與一臂，讀 `task.md`／`contract.json`；再用 CSV 找到交付，讀證據包的原 patch、功能日誌與執行審核；若涉及 Flipt／Clap，補讀相同條款診斷；最後才核對該配對原始盲評票。這樣可沿「要求 → 實作 → 判定 → 統計」重現結論。

A 沒有每臂的預封存來源快照目錄；本包另收集其可用 harness，並以當時啟動、事件及結果紀錄核對實際條件。B 至 F 與 I 的程式快照均已與原研究來源 manifest 核對。完整原始紀錄與歷史分數保留，這份報告不覆寫先前研究。
