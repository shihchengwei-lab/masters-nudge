# 開發與維護

本文件描述 2026-10-03 工作樹。工具規則以 [SPEC](../SPEC.zh-TW.md) 為準，效果以對應的[測試報告](../benchmark/README.zh-TW.md)為準。

## 原始碼與外掛的關係

| 位置 | 責任 |
|---|---|
| `buddy-prompt.txt` | 現行兩步選題、五條品味準則與欄位語意 |
| `nudge-schema.json`、`masters_nudge/provider_contract.py` | 四欄 JSON 與字元限制 |
| `masters_nudge/contracts.py` | 共用材料、結果形狀與額度常數 |
| `masters_nudge/prompting.py` | 唯一 Actor 回饋格式與固定尾端引導 |
| `masters_nudge/codex_adapter.py`、`hook_entry.py`、`mcp_entry.py` | 原生事件、命令／MCP 接入與回覆 |
| `masters_nudge/core.py`、`evidence.py`、`storage.py` | 組包、來源事實、呼叫順序、結果與計次 |
| `masters_nudge/providers.py`、`read_only_repo_mcp.py` | 外部 Provider、期限與唯讀搜尋／讀取 |
| `masters_nudge/runtime.py`、`settings.py`、`management.py`、`masters_nudge_cli.py` | 預設、設定、診斷與歷史查詢 |
| `masters_nudge/plugin_inventory.py` | 外掛生成檔與靜態檔的唯一清單 |
| `plugins/masters-nudge/` | 可分發外掛；生成程式不得另行手改成第二套實作 |
| `tests/spec/` | 現行工程契約檢查 |
| `tools/`、`benchmark/`、`experiments/` | 開發驗證、固定研究與歷史材料；不在日常外掛執行路徑 |

外掛清單在 `plugins/masters-nudge/.codex-plugin/plugin.json`；Hook 在 `hooks/hooks.json`，只接 `UserPromptSubmit` 與 `PostToolUse`。`.mcp.json` 宣告常駐 Nudge MCP。三個管理技能是靜態外掛文件，由技能自身說明使用時機。

現行 Provider 提示採 2026-10-01 定稿；載入後去除首尾空白的 SHA-256 為 `e67172b2e0daa982139a2c99b1656b6e01982ec7ee54d96193395e3763eb0214`。之後為三道難題嘗試的選題改寫已回退。四欄上限依顯示順序為 **40／25／61／35**，含標籤總上限 **200**；Provider 五條準則與盲評拆開的六項準則各有用途。

## 設定與本機資料

預設設定是使用者目錄下 `.masters-nudge/config.json`，紀錄是 `.masters-nudge/data/feedback.sqlite3`，故障紀錄是同資料目錄的 `error.log`。

| 環境變數 | 現行用途 |
|---|---|
| `MASTERS_NUDGE_DATA_DIR` | 覆蓋設定與資料目錄；指定後兩者都直接位於該目錄 |
| `MASTERS_NUDGE_RUNTIME_DIR` | 覆蓋提示、schema 等執行檔案所在目錄 |
| `MASTERS_NUDGE_TEST_MODE=1` | 將故障向測試執行器拋出；一般使用只回故障狀態並讓 Actor 繼續 |
| `MASTERS_NUDGE_ACTIVE=1` | Provider 子程序的重入防護，避免自己的工具動作再次觸發 Nudge |

模型設定只改 Provider。未設定時是 `gpt-5.6-sol`，Provider 深度固定 medium；六臂研究顯式指定自己的配置。`provider reset` 移除儲存選擇並恢復程式預設，沒有更換 Actor。

`recent-nudges` 讀取送達、原材料、讀取紀錄與可用用量；送達紀錄不是採納追蹤。不要從不存在的欄位推論完成率、誤報率或 Actor 採納率。

## 修改後如何核對

先確認 Python 與 Git 已可用。從 repo 根目錄執行 PowerShell：

```powershell
python --version
git --version
python tools/build_plugin.py --write
python tools/build_plugin.py --check
python -m unittest discover -s tests -v
git diff --check
```

只有修改生成來源後才需要 `--write`；文件整理可直接 `--check`。檢查成功分別表示副本同步、既有工程契約通過、差異沒有空白錯誤；不證明模型選題、採納或程式品味改善。CI 定義在 `.github/workflows/ci.yml`，設定涵蓋 Windows／Ubuntu／macOS 與 Python 3.10／3.14；本機執行不能代表那些遠端工作均已通過。

離線核對最新六臂結果：

```powershell
python -X utf8 .\benchmark\sol61-six-arm-20261002\aggregate.py --verify
```

這只讀包內凍結材料並重建統計，不呼叫 Actor、Provider 或評審。用 `--originals` 才額外核對原研究電腦的 D/E 槽來源；一般 clone 不需要它。完整方法見[harness 說明](../benchmark/sol61-six-arm-20261002/HARNESS.zh-TW.md)。

另有四個需明確指定輸出／執行條件的診斷工具：`verify_spec_provider.py` 測真實 Provider／MCP 能力；`verify_spec_recorded_reads.py` 重播已記錄的唯讀操作；`verify_spec_actor.py` 測原生 Actor 至外掛的交付路徑；`verify_spec_app_server.py` 測事件、故障與中斷。它們不屬一般單元測試，其中模型診斷會消耗模型用量；單次路徑通過不代表多題品味改善。執行前讀各程式的參數與用途，不把歷史輸出當目前驗證。

## 文件維護規則

現行改動須核對中英文 README、SPEC、固定提示、schema、實作與生成副本。只改字數或 JSON 不足以宣告內容品質改善；模型效果需用對應材料實測。

歷史任務、驗收、提示、原票與數值保留當時條件；只在外層索引或歷史報告的狀態說明中標清版本。六臂凍結包內檔案以指紋核對，不為了對齊現行措辭而改寫。新增研究使用新目錄與計畫。

工作樹整理、生成副本、安裝、提交、推送與發布是不同動作。文件不得把尚未做的動作寫成完成；本機 `HANDOFF.md` 保持忽略，不加入公開包。
