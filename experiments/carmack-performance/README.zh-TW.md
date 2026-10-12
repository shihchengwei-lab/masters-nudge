# Carmack performance：離線 smoke、CLI 啟動限制與 A/B 模板

本目錄的 Windows 數字全部是固定合成資料。smoke 的 Provider 回覆與 Actor 後續步驟也全部由測試作者事先編寫，不是模型輸出、Windows 裝置量測或 A/B 結果。離線 smoke 不呼叫模型；另一次真實 CLI 啟動嘗試的結果與限制見下節。沒有 Windows 裝置存取或系統設定變更。

## 真實 CLI 嘗試：只驗證到 task-start

2026-10-12 使用 Codex CLI 0.159.2 做隔離的單次啟動，未永久安裝 plugin。Actor 確實啟動，原生 `UserPromptSubmit` 在專用 journal 建立一筆 performance round；shell 與 `apply_patch` 都在命令執行前遇到以下錯誤：

```text
error building bubblewrap command: app-server socket directory must be a user-owned directory with mode 0700
```

無模型的 `/bin/true` 沙箱預檢也重現相同錯誤。相同版本的 [daemon directory 程式](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/uds/src/daemon_directory.rs#L1-L39)要求固定共用 socket 目錄為 0700；外層沙箱的 [socket 目錄遮罩](https://github.com/openai/codex/blob/rust-v0.159.2/codex-rs/linux-sandbox/src/bwrap.rs#L853-L886)則將該目錄呈現為唯讀 0000，阻擋巢狀沙箱建立。這是所測執行環境的相容性限制，不是效能瓶頸量測或 performance profile 效果。沒有修改或繞過該隔離。

本次量測、checkpoint、真實 Provider 呼叫及 Nudge 採納均為 0；沒有 CPU／RAM／I/O 基準或前後改善數字。必須先在受支援、保留安全隔離的執行環境通過同一沙箱預檢，才可重試 live 診斷。公開版本只保留去識別化摘要，不包含登入資料、原始對話、session ID、journal 或執行期目錄。

## 必須明確 opt-in；沒有自動診斷觸發

預設 profile 仍是 `software-engineering`。performance 模式必須在啟動 Host 前設定 `MASTERS_NUDGE_PROFILE=performance`，讓 Host hook 與 Actor 呼叫的 checkpoint 繼承同一組環境。Actor 還需要在一批診斷結果完成、準備決定下一步時，主動呼叫 `diagnostic_checkpoint.py`；這不是監看所有 shell 指令的自動 hook，Actor 沒呼叫就沒有診斷 Nudge。

CLI 不要求 Actor 知道 Host session ID；它用正規化的 Git `cwd` 與完全相同的 `task_request`，尋找 journal 中唯一保留的 round。歷史 session 沒有自動過期，舊 round 也可能造成歧義；不能把「保留」解讀成確定目前仍活躍。應使用新的專用 data directory，先讓真正的 Host `UserPromptSubmit` 建立 round，再由同一任務呼叫 checkpoint。缺少 round、要求不符或多筆匹配均應報錯，不能猜測 session。合成 smoke 以 Adapter 模擬 task-start。上述獨立 live 嘗試只驗證原生 task-start；完整 checkpoint／Provider／Actor 交付鏈仍未驗證。

## 重現

在倉庫根目錄，使用 Python 3.10+ 與 Git：

```sh
python tools/smoke_performance.py
python tools/smoke_performance.py --output experiments/carmack-performance/smoke-local.json
```

第一個指令把完整 JSON audit 印到 stdout，第二個另存檔案。指定的結果檔若已存在會拒絕覆蓋，請換新檔名。不需要 Codex CLI、登入、API key、網路、Windows 或 plugin 安裝。腳本建立臨時 Git evidence 工作區及隔離 journal，結束時刪除臨時目錄；只有指定的 audit 檔會保留。它不讀取使用者模型設定、不執行 fixture 內的工具敘述，也不測量本機記憶體。

預期：`PASS_OFFLINE_SYNTHETIC_SMOKE_ONLY`、2 次 stub dispatch、1 筆 feedback、1 筆 silence。`smoke-result.json` 如存在，是一次實際離線執行留下的完整 audit。JSON 中 `offline_*elapsed_seconds` 和 journal 的 elapsed 是 Python／stub 接線時間，絕不是模型或 Windows 效能數字；真實 tokens、費用與模型延遲為 null / NOT_RUN。

## 固定流程與可以證明的範圍

1. Adapter 接收 UserPromptSubmit，建立 performance round；一般 shell PostToolUse 不呼叫 Provider
2. `windows-ram-only.synthetic.json` 只有「待機 75%」；固定 stub 回四欄 Nudge，要求同一時間窗的可用量、提交量／上限、paging、延遲與程序私用量，先不要動系統
3. 同一材料只改 batch ID、tool call ID、reason、progress：去重，不再次 dispatch
4. `windows-pressure-window.synthetic.json` 是事先備妥的新合成時間窗；第二個固定 stub 回 `{"feedback": null}`。此 silence 只測試「沒有可支持的動作時可以停止」的傳輸路徑，不代表模型判斷正確
5. 同一新材料反轉順序並重新命名 ID：仍去重。最後核對 prompt、四欄字數、原始 diagnostic output、journal、沒有未完成 judgment

checkpoint 直接經由 in-process `NudgeCore.process_diagnostic(payload)`。它測到 Adapter 的 task-start／忽略無關事件，以及 core、schema、材料、去重與 journal；沒有假稱測到真實 Host 的 CLI 調用、hook 注入或 Actor 下一次 inference。完整 payload 保留 `cwd, task_request, batch_id, reason, progress, evidence`，每個 evidence 僅含 `tool_use_id, tool_name, tool_input, tool_response`。fixture 外層 provenance 不送進 checkpoint。

查看 audit 時，`checkpoints` 記錄每次觸發理由、材料、Nudge、結果及離線耗時；`provider_stub_dispatches` 保留實際交給 stub 的 packet；`journal` 保留實際 journal 終態。臨時路徑替換為 `$SMOKE_TMP`、倉庫路徑替換為 `$REPO`，避免把執行者路徑帶進版本庫。

## 手動 Host 啟動範例（完整診斷流程尚未驗證）

以下是手動啟動範例，不是本 smoke 的重現要求，也不是上述受阻 live 嘗試的完整重現腳本；實際啟動 Actor／Provider 可能付費，須先取得指定型號、budget 與資料傳輸授權。前提是已建置並正確載入本分支的 plugin，Host 支援並已信任對應 hook，而且目前目錄為專用 Git evidence 工作區。新 data directory 也會隔離 Provider 設定，未明確設定型號時將使用程式預設值；請在獲准預算與型號確定後才試跑。

POSIX shell，在啟動 Host 前設定；變數只傳給這次啟動的行程：

```sh
MASTERS_NUDGE_PROFILE=performance \
MASTERS_NUDGE_DATA_DIR="$(mktemp -d -t masters-nudge-performance.XXXXXX)" \
codex
```

PowerShell，在同一個新 shell 內先設定，再啟動 Host；變數不寫入使用者或系統全域設定：

```powershell
$env:MASTERS_NUDGE_PROFILE = "performance"
$env:MASTERS_NUDGE_DATA_DIR = Join-Path ([System.IO.Path]::GetTempPath()) ("masters-nudge-performance-" + [guid]::NewGuid().ToString("N"))
codex
```

在這個 Host 的真實 `UserPromptSubmit` 已登記任務後，Actor 才能把已審核的 UTF-8 payload 送到安裝版本的 `diagnostic_checkpoint.py`。請使用驗證過的實際入口路徑；下列 `<verified-runtime>` 是要替換的佔位字，不能原樣執行：

```sh
python <verified-runtime>/diagnostic_checkpoint.py < redacted-diagnostic-payload.json
```

PowerShell 使用 Python 讀取原始 bytes，可避開不同 PowerShell 版本的管線編碼差異：

```powershell
python -c "from pathlib import Path; import subprocess,sys; subprocess.run([sys.executable, r'<verified-runtime>\diagnostic_checkpoint.py'], input=Path('redacted-diagnostic-payload.json').read_bytes(), check=True)"
```

請勿把含 `__SMOKE_GIT_WORKSPACE__` 的 fixture 原封不動送入真實 Provider。CLI 的 `additionalContext` 是一般工具 stdout，並不證明 Host hook 已注入 Actor 上下文。`no_feedback` 也可能表示重複材料、額度用完或 round 被取代，必須查看 journal 才能說是 Provider silence。

## Windows 資料的意義與限制

這個案例故意從證據不足開始。RAM 占用百分比與快取分布不應被當成單一問題判準；後續應將症狀和相同時間窗的壓力指標一起看。此處只是測試資料的設計理由，不是對任何真實電腦的結論。

合成案例的 standby 已包含在 available，不能再相加。paging 計數也不應被自動說成只有 pagefile I/O。短時間窗、低 paging 與穩定的兩個假程序不能排除其他時間的問題，也不能解釋整台電腦的全部記憶體歸屬。

指標背景可參考 Microsoft 的 [Cache and Memory Manager 排查](https://learn.microsoft.com/en-us/windows-server/administration/performance-tuning/subsystem/cache-memory-management/troubleshoot)、[Memory Performance Information](https://learn.microsoft.com/en-us/windows/win32/memory/memory-performance-information) 與 [RAMMap](https://learn.microsoft.com/en-us/sysinternals/downloads/rammap)。本 smoke 沒有下載或執行 RAMMap。

## 真實 A/B 尚未執行

`matched-ab.NOT-RUN.json` 是未填寫的實驗模板。control 與 Carmack arm、tokens、費用、時間、品質差異與勝者全部保持 NOT_RUN／null。

若日後明確授權實測，先填妥相同 Actor 型號／推理強度、任務、初始 evidence、工具權限、budget、可取得的後續資料與重複次數；唯一預定差異是有無 performance Nudge。保留真實 Actor 選擇及後續量測，不能把這裡預寫的 follow-up 當成模型因 Nudge 改善的證據。分開報告重播固定資料、現場量測與真實系統介入；工具錯誤不能變成 silence 或成功案例。

## 隱私與安全界線

- 優先只提供與症狀相關、去識別化且有時間窗的唯讀結果；不要提交 token、環境變數、帳號、使用者路徑、視窗標題或無關整機清單
- 實際 diagnostic payload 會進入本機 journal，也可能送往真實 Provider；使用真資料前確認資料目的地及授權
- 不清 standby、不改 pagefile、不停服務、不停安全軟體、不關背景／啟動項、不修改 BIOS／登錄；本 smoke 沒有任何這些動作
- 本目錄不提供把 70–80% 占用直接轉為修復動作的腳本
- 無實際 Windows 資料就不下真實診斷；無 live Actor／Provider 試驗就不宣稱模型效果
