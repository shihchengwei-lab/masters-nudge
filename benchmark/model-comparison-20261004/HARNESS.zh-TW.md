# 七臂 benchmark harness 與審計說明

## 本包能做什麼

`aggregate.py` 可從本包原始紀錄重建全部統計，不呼叫模型、不連網、不需要原 D/E 槽。`harness/` 保存執行研究時的程式來源，供檢查如何啟動模型、觸發工具、固定驗收及盲評；重新執行解題研究另需原專案、預裝依賴與指定版本 CLI。

七臂共 168 份 Actor 交付；同題同次序是比較位置，各臂從同一基底重新開始，不是接續另一臂的答案。品味沿用十組直接比較，按目前完整交付口徑保留 71 個配對決定；每個決定含二至三張獨立模型評審票。

## 一、離線重建統計

在本資料夾開啟 PowerShell，先確認 Python 已安裝且為 3.11 以上：

```powershell
python --version
python -X utf8 .\aggregate.py --verify
```

驗證程序會：

1. 核對 `source-index.json` 每個包內原始檔的 SHA-256，及 `evidence.zip` 整體指紋。
2. 讀取 168 份 `result.json`、`score-v3.json`、`launch.json` 與原 patch。驗證 Actor 模型／深度、Provider 條件、hook 開關、基底、30 分鐘時限與提醒額度，核對原 patch 指紋。
3. 核對每題七臂任務提示一致。提示文字指紋按原 harness 的文字讀取方式統一換行；檔案原始位元組另有來源指紋。
4. 從原 `task_completed` 開始，套用所有七臂同 fixture 的 Flipt／Clap原條款補查；原分數不覆寫。
5. 重新建立契約完成、功能通過、逐題次數、時間與提醒統計。Token 只使用七臂共同 19 個完整用量位置，缺失不當零。
6. 讀取每位評審原始輸出、匿名對應、交換次序與多數決，與原 `pair.json` 及研究摘要交叉核對；保留雙方完整交付的配對。核對每組共同完成數等於可評配對數，列出因已確認缺口排除的原票，不改原票。
7. 核對 I 原 17 份及全 24 份 `result.json` 保留指紋、C/F 對照來源指紋，以及原 6,338 個 A–F 來源記錄與全部檔案位元組保留。
8. 與既有 JSON、CSV、報告、程式及模板指紋比對。任一不一致會終止並回報位置。

重新產生統計：

```powershell
python -X utf8 .\aggregate.py
```

在原研究電腦上，若也想核對來源仍未改變，可加上：

```powershell
python -X utf8 .\aggregate.py --verify --originals
```

`--originals` 會讀來源索引中的原始本機路徑，移到另一台電腦時不需要這個選項。上述命令都不會啟動 Actor、Provider 或評審。

## 二、如何讀取單份交付與原票

可用檔案總管開啟 `evidence.zip`，或先解壓：

```powershell
Expand-Archive -LiteralPath '.\evidence.zip' -DestinationPath '.\evidence'
```

以 Element F1 為例：

| 步驟 | 位置 | 可核對內容 |
|---|---|---|
| 任務 | `protocol/evaluation/cases/element-sessions/task.md`、`contract.json` | 要求、驗收介面與檢查對照 |
| 啟動 | `evidence/runs/F/element-sessions/F1/launch.json`、`prompt.txt` | 實際模型、深度、hook、基底與任務提示 |
| 實作 | 同資料夾的 `actor-events.jsonl`、`final.patch`、`actor-final.txt` | Actor 行動、原程式改動、最終說明 |
| 提醒 | 同資料夾的 `provider-attempts.json` | 當時傳給 Provider 的材料、原始建議、唯讀工具追蹤、送達與用量 |
| 功能 | `evidence/evaluation/F/element-sessions/F1/`、原 `score-v3.json` | 原測試、補充檢查與判分日誌 |
| 執行規則 | run 中的 `execution-evidence.json`、`execution-review.json`；`evidence/execution-judges/F/` | 是否符合指令、原評審依據與事件行號 |
| 品味 | `evidence/judges/F/element-sessions/trial-1/C-F/` | 每位評審、匿名 mapping、原輸出與多數決結果 |
| 彙整 | `deliveries.csv`、`results-summary.json` | 可追到該份 patch 指紋的最終報告判定 |

盲評中 X/Y 的對應會隨次序交換，先讀該次 `mapping`，再讀 `winner_arm`。同一配對判定是一票結果，不能把二至三位評審呼叫當成二至三個獨立程式作品。

## 三、原執行 harness 的程式責任

各臂程式位於 `harness/B/` 至 `harness/F/` 及 `harness/I/`；來源 manifest 保留原檔位置、快照位置與指紋。I 的 `study/` 是最近一次完整研究流程，其共用依賴在 `dependencies/`、原條款測量在 `diagnostics/`。

| 程式／材料 | 責任 |
|---|---|
| `data/plans/<臂>.json` | 模型、深度、題目、基底、CLI、提示、工具、評測指紋與配對預案 |
| `study/preflight.py` | 驗證固定來源與依賴 |
| `study/pipeline.py` | Actor → 原條款補查 → 執行審核與匿名品味 → 報告 → 完整性 |
| `study/run.py` | 管理研究根目錄、封存對照來源、題目還原、結果路徑與兩個工作槽 |
| `study/actor_runner.py`、共用 runner | 依條件啟動 CLI、計時、保存事件與 Provider 結果、取得最終 patch |
| `protocol/nudge-plugin/`、`protocol/nudge-plugin-I/` | medium／xhigh 實驗工具：提醒 hook、Provider 呼叫、唯讀查庫、四欄 schema、來源事實與狀態紀錄 |
| `protocol/evaluation/evaluate.py` | 將原固定檢查與執行審核結果組成 `score-v3.json`；不以臂名判分 |
| `container_checks.py`、`native_checks.py`、各題 `checks/` | 原容器／原生功能驗收 |
| `study/review.py`、`study/finish.py` | 輸出執行證據，交 Astra medium 依任務作語意審核 |
| `study/transcript_reader.py` | 執行審核唯讀閱覽 Actor 材料 |
| `study/blind.py`、`blind-rubric.txt` | 匿名程式來源、交換順序、多數決、原票保存與契約疑點另列 |
| `study/verify_final.py` | 核對舊對照未變、實際設定、固定來源、題目內容與 Git 暫存條目還原 |
| 本包 `collect.py` | 從封存研究收集原始紀錄、來源快照與指紋；不改答案、不重跑模型 |
| 本包 `aggregate.py` | 從包內原始紀錄重算七臂結果與排名，產生 CSV、JSON、報告與完整性紀錄 |

不同臂的源碼保留各自實際版本，不以最新腳本冒充所有臂的執行程式。I 保存 32 個來源快照；修復前後版本另存證據包 `infrastructure/I/harness-amendments/`。A 沒有預先保存的逐檔來源快照目錄，另放入 `harness/A/collected-at-close/`，並靠當時 `launch`／事件／結果核對其執行條件。

A 封存研究中較早 B 版本的執行審核材料，另放在證據包 `history/A-study-earlier-B-execution-judges/`。它們只保留歷史來源，不參與本七臂 B 的判分與統計；本次 B 一律讀 `runs/B/` 與新 B 研究來源。

Provider 五條準則與品味評審六項準則的拆分、較早通用 protocol 與本次實際計畫的差異，已在主報告說明。實際啟動設定與封存任務優先於通用文件中的舊研究名稱或模型措辭。

## 四、要重新執行模型實驗時，需要的條件

這是建立新研究，不是離線重建本批統計。原交付與原票保留；新結果需要新輸出目錄與計畫，不覆寫本批材料。

1. 依 `protocol/evaluation/cases.json` 取得原專案，檢出各題 `base_commit`，復原公開任務與指定 helper。基底、任務與依賴來源均須與計畫相符。
2. 還原預裝容器映像或原生依賴；原映像指紋、Node、Cargo、Rust 與其他工具版本見環境資料。這些大型依賴未收入本包。
3. 取得計畫指定 CLI。A/B/C 為 0.159.0、D/E/F/I 為 0.159.2；二進位 SHA 分別為 `86e8ef1013f98df51fdeea446597f7e3ca32e454d1d4d8c0402a68b03c311d70` 與 `34549ded6e2aee87c911c62d025e52e26c488683d0f489cd68f756baef1a6df6`。實驗程式需要可用的模型帳戶；帳戶與憑證不在材料包中。
4. 依來源 manifest 還原該臂 runner 與相依程式路徑。原腳本有研究電腦的絕對路徑，不能只把腳本搬走就宣稱相同環境已就緒。必要的路徑變更與新的執行檔差異應記入新研究計畫。
5. 在新計畫固定模型、深度、兩工作槽、30 分鐘限制、每題兩次、提醒額度、題目／工具／評測指紋與比較組合。預檢通過後才執行 Actor。
6. 依原流程保存全部正負結果、固定驗收、執行審核與相同補查，再只對共同完整交付做匿名品味。真正解題失敗不重抽；基礎設施中斷保存原紀錄後接續未完成部分。
7. 完成來源與環境還原核對，產生新報告。模型輸出會有變動；相同流程不要求逐字重現原答案。

## 五、判分公式與資料邊界

```text
原凍結完成 = score-v3.task_completed
目前完整交付 = 原凍結完成 且 已確認原條款補查通過
不計交付時間的功能通過 = 固定功能通過 且 原條款補查通過
完成率 = 目前完整交付數 / 24
單位交付時間 = 全部 24 次 Actor 時間總和 / 目前完整交付數
未快取輸入 = Actor輸入 + Provider輸入 - 兩者快取輸入
品味可評配對 = 同題同次序、雙方目前完整交付
```

時間、Token、完整交付與品味分開呈現。已確認缺口會改變可評品味配對，但不改原票。尚未確認的靜態疑點不自動改完成率。每組共同完成的樣本不同，沒有直接比較的組合不透過其他票推定勝負。

## 六、I 臂的新增條件與修復

I Actor 與 Provider 都是 GPT-6.1 Sol xhigh；工具提示、schema、欄位限制與 F 相同。`protocol/nudge-plugin-I/masters_nudge/runtime.py` 只覆寫 Provider 深度常數，離線彙整逐位元組核對此差異；正式產品仍固定 medium。I-C／I-F 使用原 C/F 交付，不重跑對照，評審仍是 Astra medium。

I 的零改碼容量故障另存後退避接續；Tracing I1 終止命令修復後保留逾時失敗，不採用晚到 patch；NodeBB I1 錯配驗收改為核對同一現有 patch 再驗收。原 17 份與全部 24 份 Actor 結果保留指紋均已核對，沒有因功能失敗重抽。詳細秒數、截止 patch 缺失、Actor Token 缺失及補查限制見[主報告 4.3](REPORT.zh-TW.md#43-故障與材料版本)。修復日誌、容量原嘗試及錯配驗收在 `infrastructure/I/`；收集證明在 `data/provenance/I/collection-extension.json`。

七臂排名與首頁使用共同 19 份 Token 位置。`results-summary.json` 的 `I_comparisons` 另列 I-C 的 21 份與 I-F 的 19 份，均由逐份用量重算、交叉核對 I 原摘要。時間使用全部 24 次；Tracing I1 計上限 1,800 秒、額外 291.651 秒獨立列出。

`collect.py --add-i <完成研究根目錄>` 是此次追加原始材料的收集方式：驗證完成狀態、來源快照及原檔指紋，保留既有壓縮包全部成員後加入 I，再重新核對全部來源。已收集過 I 時拒絕重複追加。一般讀者只需 `aggregate.py --verify`，不需原研究路徑。

本包不新增逐則提醒內容標註。`provider-attempts.json` 保留分析誤報、內容與採納所需的原材料；送達數只是工具輸送結果，與正確率或採納率不同。
