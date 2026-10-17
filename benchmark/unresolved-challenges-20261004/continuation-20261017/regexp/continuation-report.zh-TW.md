本次從已套用的歷史 J2 繼續修補。最終固定評估四項全部通過，全部規則測試 1,730 項通過。既有 109 個測試檔案的 SHA-256 均未改變；新增獨立的 `tests/lib/rules/no-dupe-disjunctions-continuation.ts`，共 37 項測試。

候選交付檔為 [candidate-1.patch](candidate-1.patch)，SHA-256：`8de6e0a1a944cfe07389bf69929f2ba1e0195641c036367c2389a9657ae1e8c5`。固定評估的 [evidence.json](actor-evaluation-1/evidence.json) 與此雜湊一致。最終稽核見 [continuation-final-audit.json](continuation-final-audit.json)。

**目標、依據與起點**

依原始 `frozen-evaluation/cases/regexp-404/task.md` 與 `contract.json`：診斷非否定字元類別、範圍端點及巢狀分支的可刪元素；訊息區分嚴格子集與有序前綴涵蓋；保留範圍內部字元、擷取警告、既有選項、效能警告及正確位置。

已讀 J1、J2 的原始修補、最終回覆、Provider 回饋及兩份歷史評估，也核對重新產生的 baseline。歷史與基線一致顯示：

| 版本 | reserved | contract | direction | judge concerns |
| --- | --- | --- | --- | --- |
| 歷史 J1 | 通過，77 項 | 通過 | 失敗 | 失敗 |
| 歷史 J2 | 通過，77 項 | 通過 | 失敗 | 失敗 |
| 本次起點 baseline | 通過，77 項 | 通過 | 失敗 | 失敗 |
| candidate-1 | 通過，77 項 | 通過 | 通過 | 通過 |

原始輸出進一步證實：J1 的反向參照探針通過，但 lookbehind、效能警告、相等分類失敗；J2 修好了 lookbehind，卻新增反向參照誤報，另外兩個問題仍在。以上判斷來自各評估的原始 `PROBE_RESULT`，不是僅採信歷史總結。

本次重現紀錄：

- [continuation-before-direction.log](continuation-before-direction.log)：lookbehind 位置正確，但 `warningPreserved:false`。
- [continuation-before-concerns.log](continuation-before-concerns.log)：反向參照 `passed:false`、兩種效能選項的 warning 均為 false、相等分類 `passed:false`。
- [continuation-before-focused.log](continuation-before-focused.log)：既有固定 suite 與 J2 新增 suite 合計 114 通過。
- [continuation-before-regressions.log](continuation-before-regressions.log)：先寫的獨立回歸測試 9 通過、20 失敗，再開始改實作。

**實作與證據**

改動集中於 `lib/rules/no-dupe-disjunctions.ts`；沿用既有 refa、regexpp、regexp-ast-analysis 與報告流程，未新增相依套件。

| 修補 | 實作方式 | 最終證據 |
| --- | --- | --- |
| 巢狀診斷壓掉效能警告 | 去重保留完整結果；巢狀發現可與一項 Superset／Overlap 效能診斷並存，仍遵循效能選項 | `/(?:a+|[ab])+$/` 的 certain；`/(?:a+|[abc])+/` 的 default／certain；report 三選項與效能三選項交叉測試均通過 |
| 相等被說成嚴格子集 | 使用現有集合關係比較；內部區分 NestedDuplicate，輸出既有 already-covered 模板；精確相等不受前綴可用性過濾 | `/ab|(?:ab|a)/`、後接 `c`、`.source` 與擷取警告案例通過，位置仍指向巢狀 `ab` |
| 擷取／反向參照改變匹配 | 檢查候選實際路徑的相依擷取；涵蓋端只使用不設定相依擷取的路徑作證據 | 固定反向參照探針不再誤報；數字／命名參照、較早分支、順序兄弟擷取與量詞其他迭代的語意見證通過 |
| 無關兄弟擷取造成漏報 | 互斥兄弟分支不算候選依賴；涵蓋 NFA 保留不經相依擷取的分支及真實量詞界限 | Nudge 案例、對稱案例、optional／重複覆蓋分支、前綴與 lookbehind 案例通過 |
| 保留 J2 正確部分 | 不改既有 marker／hit NFA 與真實量詞 min/max；不改 J2 的 AST lookbehind 入口與方向修補 | contract 探針、既有 37 項 nested 測試、範圍端點／內部字元、擷取警告及位置測試通過 |

第一輪修補完成時 143 項相關測試通過，見 [continuation-after-repair-1.log](continuation-after-repair-1.log)。後續 Nudge 的範圍修正另有先失敗再通過的紀錄。

**Nudge 逐項處理**

本次實際收到一項有內容的 Nudge：

> OBSERVED: findNestedDuplication: capture→return
> WHY: 無關兄弟捕獲也封鎖安全的元素診斷
> STRUCTURE: 候選與覆蓋路徑各自保留捕獲依賴；驗證相容後比較，不因兄弟捕獲封鎖整支
> REQUIRED: (?:a+|(?:[ab]|(c)))\1 應報 [ab] 的 a

處置：採納。先核對原始合約，再重現此例確實漏報；這是 Provider 指出的新發現，不是起初已規劃的三項修補。第一輪以整個 alternative 含參照擷取就退出，確實過於保守。

相應改動：以 `hasReferencedCaptureOnPath` 檢查候選路徑；`toCaptureFreeNFA` 在涵蓋端排除會設定相依擷取的路徑，保留其他互斥分支，並保留 optional／重複的實際界限。前綴分析仍依匹配方向延伸 NFA。候選與覆蓋路徑均不設定相依擷取時，才據此證明涵蓋。

具體驗證：

- Nudge 原例最終只回報 `[ab]` 的 `a`，第 12 至 13 欄，使用 strict-subset 模板。
- 對稱例 `/(?:(?:a+|(c))|[ab])\1/` 回報第 17 至 18 欄的 `a`。
- 量詞跨迭代若可能設定相依擷取，仍不給新增的可刪元素診斷；`ac` 的原式可匹配、刪除後不可匹配，已由 JavaScript RegExp 實際驗證。
- 前綴、反向匹配、optional 與重複涵蓋分支各有新增測試。
- [continuation-before-nudge-regressions.log](continuation-before-nudge-regressions.log) 保存採納前漏報；[continuation-regressions-final.log](continuation-regressions-final.log) 保存最終通過結果。

歷史回饋另行區分：J1 的 `3fc99c2374a84446a901fe1b7bb730f1` 要求原量詞 NFA 加 visited 狀態；J2 的 `17c0d9e4ecdd407185278d4eef4b8909` 與 `e29c41525fb14bfda5ee543b93b5d400` 重複提醒同一量詞問題。這些修補已存在於 J2，本次沿用並驗證，不計為本次新採納或多項改善。歷史 silence 不算收到建議。

起初三項修補來自使用者已提供的失敗分析與原始探針。候選兄弟擷取漏報來自本次 Nudge；較早分支與順序兄弟擷取的其他語意見證由本次程式檢查與測試擴展找到。這是單次知情續跑，不能據此推論工具效果或建立獨立產品比較的因果結論。

**命令、結果與完整紀錄**

以下命令均於本 checkout 使用 PowerShell 執行。測試輸出透過 `Tee-Object -FilePath` 保存到本報告所在目錄；原始失敗紀錄未覆寫。所有實作／測試／報告編輯使用 apply_patch。

四項成功且無輸出的型別／lint 命令未由 Tee-Object 建立空檔，報告連結稽核因此失敗一次，見 `continuation-report-audit-1.log`；已依原工具回傳的 exit 0 補存明確標示的執行摘要，沒有重跑或捏造命令輸出。

```powershell
node node_modules/mocha/bin/mocha --require ts-node/register tests/lib/rules/no-dupe-disjunctions.ts --reporter spec --no-color --timeout 60000
node node_modules/mocha/bin/mocha --require ts-node/register tests/lib/rules/no-dupe-disjunctions-continuation.ts tests/lib/rules/no-dupe-disjunctions-nested.ts --reporter spec --no-color --timeout 60000
node node_modules/mocha/bin/mocha --require ts-node/register 'tests/lib/rules/*.ts' --reporter dot --no-color --timeout 60000
node node_modules/typescript/bin/tsc --noEmit --pretty false --project tsconfig.build.json
node node_modules/typescript/bin/tsc --noEmit --pretty false --project tsconfig.json
node node_modules/typescript/bin/tsc --noEmit --pretty false --project tsconfig.json --skipLibCheck
node node_modules/eslint/bin/eslint.js lib/rules/no-dupe-disjunctions.ts tests/lib/rules/no-dupe-disjunctions-continuation.ts
node node_modules/eslint/bin/eslint.js tests/lib/rules/no-dupe-disjunctions-continuation.ts
git diff --check
```

| 檢查 | 結果 | 紀錄 |
| --- | --- | --- |
| 使用者指定 focused 命令 | 77 通過 | continuation-focused-final.log |
| J2 inherited 37 項＋本次新增 37 項 | 74 通過 | continuation-regressions-final.log |
| 全部規則 | 1,730 通過 | continuation-all-rules-final.log |
| 正式程式型別 | 通過，exit 0 | continuation-build-types-2.log |
| 完整專案型別 | 失敗，exit 2；唯一錯誤是外部宣告找不到 jest-resolve | continuation-all-types-1.log |
| 完整專案型別，略過外部宣告檢查 | 通過，exit 0；不當作無條件完整型別檢查通過 | continuation-all-types-skip-lib.log |
| 修改實作與新增測試 ESLint | 通過，無錯誤／警告 | continuation-lint-2.log |
| 最後補充測試 ESLint | 通過，無錯誤／警告 | continuation-new-tests-lint-final.log |
| diff 空白檢查與人工閱讀 | 通過；已讀 candidate 實作、文件、新增測試，並比較 J2 原始修補 | candidate-1.patch、continuation-final-audit.json |

依賴狀態先以 `require.resolve` 查證：typescript、eslint、mocha、ts-node、refa 可用；`jest-resolve` 回傳 MODULE_NOT_FOUND。未安裝任何套件。Node 的既有 MODULE_TYPELESS_PACKAGE_JSON 提示不影響測試結果，未擴大修改套件設定。

固定評估命令：

```powershell
python "<STUDY_ROOT>\remaining-continuations-20261017\continuation.py" regexp export --output "<STUDY_ROOT>\remaining-continuations-20261017\regexp\candidate-1.patch"
python "<STUDY_ROOT>\remaining-continuations-20261017\continuation.py" regexp evaluate --patch "<STUDY_ROOT>\remaining-continuations-20261017\regexp\candidate-1.patch" --output "<STUDY_ROOT>\remaining-continuations-20261017\regexp\actor-evaluation-1"
```

已讀四項完整輸出，而非只看程序 exit 0：

- [reserved.txt](actor-evaluation-1/reserved.txt)：77 passing。
- [regexp_contract.js.txt](actor-evaluation-1/regexp_contract.js.txt)：量詞探針 passed=true。
- [regexp_direction.js.txt](actor-evaluation-1/regexp_direction.js.txt)：passed=true，warningPreserved=true。
- [regexp_judge_concerns.js.txt](actor-evaluation-1/regexp_judge_concerns.js.txt)：backreference passed=true、wronglyRemovable=false；default／certain 的 warning 均 true；equality passed=true，實際訊息為 already covered。

**中途失敗、歷史衝突與限制**

失敗紀錄均保留：第一輪新測試 20 失敗；Nudge 前 3 失敗，其中兩項是安全路徑漏報，另一項是我新加測試誤把既有整支 alternative 的擷取警告也要求禁報。後者已在本次新增檔內改成僅測試巢狀元素的案例，沒有修改任何既有測試。其後測試一度僅剩我新測試手算位置少一欄，並有 TypeScript parent 可空型別及 lint 格式問題；均修正後重新驗證。相關失敗保存於 `continuation-before-nudge-regressions.log`、`continuation-after-nudge-1.log`、`continuation-build-types-1.log`、`continuation-lint-1.log`。

歷史未凍結 suite 的唯一衝突另行記錄：J1、J2 final 都記載 67 通過、1 失敗，因原 valid 案例 `/((?:ab|ba)|(?:ba|ac))/` 要求零診斷，但新合約要求指出第二個 `ba`。精確見證是該分支接受的 `ba` 嚴格包含於較早 `(?:ab|ba)`，應定位第 16 欄。凍結的 `test.patch` 已在本次開始前將此例移至 invalid；本次沒有編輯該檔，實際跑出的固定案例通過。未宣稱原始未凍結 suite 全綠，也未為相容舊 valid 要求隱藏合約要求的診斷。

目前沒有未通過的固定接受檢查或相關規則測試。未跳過正式程式型別檢查；尚不能無條件宣稱全庫型別檢查成功，原因仍是預裝依賴缺少 jest-resolve。擷取安全證明保持保守：若候選路徑可能設定被參照的擷取，就不以單純語言包含關係給新增診斷；這不是完整 JavaScript 正規表示式等價求解器。

既有測試不變的證據是 [continuation-immutable-tests.json](continuation-immutable-tests.json) 與最終雜湊稽核。交付 patch 僅含文件、規則實作、本次新增檔及原封不動的 J2 新增檔；排除了固定測試安裝造成的原有測試 diff。歷史材料、評估器、固定定義均未修改。未 commit、push、建立 PR、安裝套件、存取網路、委派或啟用其他代理。
