# Metaflow K1 授權續作報告

日期：2026-10-17。這是已套用 K1 的知情續作，不是從相同基底獨立重跑。未委派、安裝套件、連網、讀取 Git 歷史、提交、推送或建立 PR。

## 結果與交付

完整固定驗收 **9/9 通過**；目前 checkout 的六個保留測試檔、K1 回歸測試及本次新增回歸測試合計 **92 passed**。逐層檢查評估 JSON 的 `passed` 欄位，沒有任何 false；不是僅依程序退出碼判定。

- 交付補丁：[candidate-1.patch](candidate-1.patch)。SHA-256：`5b618d896439cd9325505b399681dd85933bf7308ffb28603cc42005457babf4`。
- 完整固定驗收：[actor-evaluation-1/evidence.json](actor-evaluation-1/evidence.json)，同目錄保留每項原始輸出；另有 [actor-evaluation-1-console.txt](actor-evaluation-1-console.txt)。
- 修補前失敗：[continuation-regressions-before-1.txt](continuation-regressions-before-1.txt)，10 failed、2 passed，未覆寫。
- 修補後測試：[continuation-tests-after-1.txt](continuation-tests-after-1.txt)，92 passed、2 個既有依賴警告。
- 完整性與實作差異：[continuation-integrity-1.json](continuation-integrity-1.json)。213 個既有測試檔、239 個封存材料檔的 SHA-256 均與起始紀錄一致。

補丁包含既有 K1 實作及 K1 的 `test/unit/test_stub_generator_runtime.py`，另加入本次回歸檔。匯出工具已排除固定測試安裝內容；`test/cmd/develop/test_stub_generator.py` 不在交付補丁中。

## 最小需求、假設與修補

先閱讀原始 `task.md`、`contract.json`、K1／K2 原始補丁、最終回覆、Provider 提醒與歷史評估，並核對 freshly reproduced baseline 的原始輸出。基準只有 `metaflow_members_input.py` 及 `metaflow_review_members_input.py` 失敗；其餘七項通過。

最小需求是保留明示 None 型別、輸出合法 metadata 表達式，並維持 K1 已通過的簽章、類別、匯入及重設責任。初始假設是兩個失敗位於不同輸出邊界，可不改類別走訪及 helper 契約而修復。新增測試先重現失敗後才修改實作。

相較 K1，`metaflow/cmd/develop/stub_generator.py` 只有兩個實作修改位置：

1. `_generate_function_stub` 在參數邊界，將明示 `parameter.annotation is None` 轉為 `type(None)`，再呼叫共用 helper。沒有註解的 `inspect.Parameter.empty` 仍維持空白；`_exploit_annotation(None)` 仍回傳空字串。修復同時適用於顯式簽章、runtime overload、property setter 及欄位註解補缺。
2. `typing.Annotated` 的 metadata 沿用既有 `_format_default`。可表示的 Python literals 保留；無效 repr、拋例外的 repr 及函式呼叫表達式改為 `...`。使用既有 `ast.literal_eval` 檢查，不新增 eval 路徑，不把 `record_effect()` 之類的呼叫輸出至 stub。原有 class metadata／預設值的匯入處理也沿用同一工具。

盤點結果：標準庫 `inspect`、`typing`、`ast` 及 repo 內 `_format_default` 已足夠，不需要新依賴或新的格式化子系統。K2 僅作為上述兩項修復方向的參考，未整份移植；未修改 K1 類別／NamedTuple／TypedDict 或部署器探索策略。

本次新增 `test/unit/test_stub_generator_continuation.py`，12 個案例涵蓋原生／延後註解、函式／顯式簽章、各參數種類、預設值、未註解參數、overload＋staticmethod、property accessor 與欄位補缺、opaque metadata，以及 `write_out` 整合輸出。檢查使用 `ast.parse`、AST 節點語意、`ast.literal_eval` 及產生註解的 runtime 值，未只比對任意字串。

## 命令與驗證

以下命令均從本次 checkout，以 PowerShell 執行；pytest 使用指定的離線容器 helper。原始標準輸出與錯誤輸出合併保存在上述新命名紀錄。

修補前先執行新回歸測試，退出碼 1：

```powershell
python "<STUDY_ROOT>\remaining-continuations-20261017\metaflow\calibration\public-tools\feature_python_check.py" test/unit/test_stub_generator_continuation.py --tb=short
```

修補後執行全部要求的既有及新增測試，退出碼 0：

```powershell
python "<STUDY_ROOT>\remaining-continuations-20261017\metaflow\calibration\public-tools\feature_python_check.py" test/unit/test_stub_generator_continuation.py test/unit/test_stub_generator_runtime.py test/cmd/develop/test_stub_generator.py test/unit/test_multicore_utils.py test/unit/test_argo_workflows_cli.py test/unit/test_pypi_parsers.py test/unit/test_local_metadata_provider.py test/unit/test_pypi_decorator.py --tb=short
```

上述為固定保留套件 45 項、K1 回歸 35 項、本次回歸 12 項。K1 測試包括整份 checkout stub 生成與逐檔 `ast.parse`、TypeVar／NewType 的執行語意、property／setter overload、Metaflow 注入方法及跨模組 reset。

依指定工具匯出並執行完整驗收，均退出碼 0：

```powershell
python "<STUDY_ROOT>\remaining-continuations-20261017\continuation.py" metaflow export --output "<STUDY_ROOT>\remaining-continuations-20261017\metaflow\candidate-1.patch"
python "<STUDY_ROOT>\remaining-continuations-20261017\continuation.py" metaflow evaluate --patch "<STUDY_ROOT>\remaining-continuations-20261017\metaflow\candidate-1.patch" --output "<STUDY_ROOT>\remaining-continuations-20261017\metaflow\actor-evaluation-1"
```

| 固定檢查 | 結果與證據 |
| --- | --- |
| reserved | pass；45 passed |
| annotation-api | pass |
| class-api | pass |
| function-api | pass |
| reset-api | pass |
| metaflow_docquotes_input.py | pass；函式及類別結尾引號文件均保留 |
| metaflow_members_input.py | 全部子項 pass；`def f(x: None) -> None`，helper None 契約仍成立 |
| metaflow_review_members_input.py | 全部子項 pass；self alias 未遞迴，`typing.Annotated[int, ...]` 可解析 |
| metaflow_typed_dict_keys_input.py | pass；保留含底線的 TypedDict keys |

已檢查最終交付路徑與完整差異，並從 K1 原始補丁重建實作文字，用 `difflib.unified_diff` 確認本輪僅有上述兩處修改。完整性紀錄另外逐層檢查 canonical `passed` 欄位，結果 `false_probe_flags: []`。

`git diff --check` 最初將 K1 沿用的 CRLF 視為行尾空白；以 `git -c core.whitespace=cr-at-eol diff --check` 驗證通過，未為此重寫既有檔案或測試。

## Nudge 內容與採納校準

實作修補的 Provider 審閱，attempt `61a83b17abca458183b91aad2b6f9832`，回傳 `{"feedback":null}`，`outcome=silence`、`delivered=0`；寫入本報告也觸發空回覆（attempt `29184069b5dd4b209d5f7bf088b7796c`）。因此沒有本輪收到而待判定採納的實質提醒，也沒有本輪 Provider 新發現可歸因的修復。最初兩項修復已由使用者續作指示提出，經原始輸出與新測試證實；repr 拋例外／呼叫表達式是測試補充的同一 metadata 問題，沒有重複計為新改善。完整性快照記錄的是實作驗證時點的審閱，不包含後續報告文字整理。

歷史提醒逐項核對如下。這些是知情續作的參考／繼承責任，不計為本輪新採納：

| 歷史來源 | 內容 | 本輪處理及具體證據 |
| --- | --- | --- |
| K1 `111413...` | 同名欄位註解仍保留 property／setter；annotation＋descriptor 同筆保存 | 保留既有採納實作，未另改類別流程；runtime 測試及 canonical annotated property／setter 子項通過 |
| K1 `0fa646...` | property／setter 保留完整 overload 集合 | 保留 `_function_signatures` 與 accessor 簽章集合；K1 overload 回歸通過，本次 None accessor 回歸亦通過 |
| K1 `b9ebf8...` | Metaflow 補充逐筆套用完整 overload 集合 | 保留 documented signatures 流程；K1 注入方法及 Metaflow overload 回歸通過 |
| K2 `166b7a...` | TypedDict 混合 total 繼承須保留每鍵 requiredness | 僅參考，未新增移植；K1 現有繼承 Required／NotRequired 與固定 key 檢查均通過 |
| K2 `49986f...` | Required／NotRequired／未標記三態，明示限定符優先 | 僅參考，沒有已證實的本輪缺口而擴充；未更動 K1 TypedDict 策略 |
| K2 `225978...` | 先探索 provider／flow／trigger 再輸出，避免走訪順序影響型別 | 僅參考，沒有已證實的本輪缺口而移植；K1 部署器回歸及完整 stub 解析通過 |

K2 另有一次歷史 silence，不計為送達或採納。沒有因提醒送達而自動認定採納，亦未從這次知情續作推論工具的因果成效。

## 範圍與限制

沒有尚未通過的固定驗收或要求執行的受影響測試，也沒有具體阻塞。既定 frozen evaluator 的四處 forward-reference 引號正規化原封不動；本報告的保留套件通過數是該固定版本，不宣稱另外執行了未正規化版本或整個 repo 的所有測試。歷史 K2 的 nested-class 命名、property／setter、NamedTuple 額外成員與 self-alias 失敗分開視為歷史參考，未移植其造成退步的改動。

Opaque metadata 以 `...` 保持合法語法，無法重建原 runtime-only 物件身分；這是此次要求接受的表示方式。依賴中的 YAML 與 requests 警告仍存在，沒有安裝／調整第三方套件。失敗紀錄、歷史資料、固定測試與評估定義均保留。
