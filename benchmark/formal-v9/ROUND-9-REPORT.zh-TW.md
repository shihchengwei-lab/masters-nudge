# 第九輪 Benchmark 正式報告

日期：2026-09-24；封存版本：`06fd30f`；Actor 與 Provider 均為 GPT-6 Sol medium

## 結論

**B 臂產生可驗證的行為收益；目前沒有達成「結構品味勝率提高，且額外成本值得」的產品標準。**

29 題各做兩次 A/B，共 58 組。事前預留契約測試 A 通過 54/58、B 通過 55/58。原始盲評在雙方通過預留測試的 54 組中，A 勝 15、B 勝 11、平手 28。但原評審把「預留測試通過」當作「兩邊行為都正確」；對 10 題追加相同輸入後，其中 20 組出現行為差異：B 單獨通過 11、A 單獨通過 6、雙方未過 3。其餘 17 題、34 組也追加了同題同輸入檢查，四臂全部通過。

逐組核查後，全部 58 組為 **B 較好 14、A 較好 11、平手 27、雙方未過 6**。B 的 14 組分別是預留契約勝 1、追加行為勝 11、結構勝 2；A 的 11 組是追加行為勝 6、結構勝 5。B 的主要收益是具體行為正確性。在追加輸入兩臂都通過的 34 組，結構盲評是 **A 勝 5、B 勝 2、平手 27**，沒有觀測到 B 的結構品味優勢。

B 的 58 次執行比 A 多 **5,976.329 秒（61.5%）**及 **2,361,584 非快取輸入 token（112.7%）**。本輪支持保留並改善 Provider 的高價值回饋路線；以目前的品質差距與成本，尚不支持宣告本版工具已通過產品效果驗收。

| 原定成功條件 | 觀測 | 判定 |
|---|---|---|
| 契約完成率不下降 | A 54/58、B 55/58 | 達成 |
| 品味勝率提高 | 34 組追加行為均過後的結構比較：A 5、B 2、平 27；其餘 20 組先由行為檢查分勝負或記雙方失敗 | 未達成 |
| 增加的時間與 token 值得 | B 多 61.5% 耗時、112.7% 非快取輸入；58 組實作結果僅多 3 組較好 | 未達成 |

## 測試條件與評分

原選 30 題，`sphinx-doc__sphinx-7748` 因預留測試要求題目未告知的反斜線續行行為而排除，計分 29 題，涵蓋八個開源專案：Rust 9、JavaScript 6、TypeScript 8、Python 6。入選前先確認固定起點的預留測試失敗、來源參考修補通過，且測試實際執行；另有 Tokio-4789 因 Windows 上參考修補無法編譯，在 30 題執行前換成 Vue-11694。每題從同一 Git 起點各跑 A1、A2、B1、B2，共 116 次 Actor 執行。Actor 自行實作；交卷後才套用預留測試。既有測試不可修改；Actor 新增的測試先保存再移開，以免影響預留驗收。全部執行、補丁、事件、token 與驗收輸出均有封存紀錄；沒有執行故障或 Provider fault。

| 條件 | A | B |
|---|---|---|
| Actor | GPT-6 Sol medium | GPT-6 Sol medium |
| 題尾文字 | 「請高品味的完成任務。」 | 移除這句 |
| Masters’ Nudge | 關閉 | 開啟；`apply_patch` 後由 GPT-6 Sol medium Provider 回傳結構回饋或沉默 |
| 起點、任務、預留測試 | 同題同次一致 | 同題同次一致 |

比較的是完整 B 流程：B 同時啟用 Provider 並移除 A 的通用品味句。各臂獨立生成，沒有從同一份中途程式分岔。因此逐組結果可以比較流程，單筆勝負不直接證明某則 nudge 的因果效果。

預留測試先決定契約通過：54 組兩臂都過、1 組只有 B 過、3 組都未過。原始品味盲評僅對兩臂都過的 54 組進行。評審是 GPT-6 Astra medium，只讀題目與匿名 X/Y 補丁。兩位評審以相反 X/Y 順序獨立評分，勝者不同時加第三位，共 110 次判斷；各給 1–5 分並說明具體差異，至少兩票一致才採計。品味六項標準為：非法狀態難以建立、因果單向、局部行為可預測、事實只有一個來源、複雜度留在真正邊界、抽象確實消除概念或分支。長短、格式、註解或與參考修補相似本身不加分。

## 盲評失真與核查方法

原盲評票數仍封存為 **A 15／B 11／平 28**。先從評審提出的具體行為疑點選 10 題、20 組；再對其餘 17 題、34 組各設計一份任務相關的追加輸入。將每臂原補丁套回固定起點，同題四臂使用同一份輸入；Rust 使用每臂獨立 Cargo 編譯目錄。54 組可評品味的 A/B 現在都有追加行為檢查：20 組出現差異或雙方失敗，34 組兩臂都通過。單邊通過時，以行為正確的一臂優先於原結構票；雙方都失敗則不選品味勝者。34 組兩臂均過者保留原始盲評：7 組有勝負的理由已核對為結構比較，27 組由兩位反向順序的評審判平手。全部 58 組都有逐筆判定及來源。

這些追加輸入是事後診斷，故下文的「核查後結果」**不偽稱為事前封存的盲評分數**；事前契約分數也不改寫。報告同時提供兩種數字，供產品判斷及下一輪題庫修正。

| 追加輸入 | 第一次 A/B | 第二次 A/B | 原始盲評 |
|---|---|---|---|
| ripgrep-2488：兩個有效 regex，第一個有 `(?x)` 尾端註解 | 失敗／失敗 | 失敗／通過 | 平／A |
| Django-11885：合併 distinct 與一般 QuerySet | 通過／失敗 | 失敗／通過 | A／A |
| Django-12774：`parent` 約束以 `parent_id` 查詢 | 失敗／通過 | 失敗／失敗 | B／A |
| Dayjs-973：夏令時間缺口保留固定時區 02:30 | 失敗／通過 | 失敗／通過 | B／B |
| Sphinx-10673：關閉索引後不連到不存在的頁面 | 通過／失敗 | 通過／失敗 | A／A |
| Tracing-2008：內層拒絕事件後不誤呼叫外層 | 通過／失敗 | 通過／失敗 | A／A |
| Vue-10250：保留無關 CSS 自訂屬性的差異警告 | 失敗／通過 | 失敗／通過 | B／B |
| Vue-11694：一次賦值只重跑 effect 一次 | 失敗／通過 | 通過／失敗 | B／A |
| Vue-11761：子類 getter 接收代理物件且只執行一次 | 失敗／通過 | 失敗／通過 | B／B |
| Vue-8381：`for-of` 暫時性死區與 `var` 作用域 | 失敗／失敗 | 失敗／通過 | A／B |

ripgrep-2488 與 Django-11885 的第二次，原盲評選 A，追加行為只有 B 通過。Django-12774 第二次與 Vue-8381 第一次，原盲評選 A，但雙方都未通過。這四張 A 票不能再當成乾淨的品味勝。檢查的輸入、四臂輸出與原始票數皆可從後述證據重算。

其餘 17 題的追加輸入如下；**每題 A1、B1、A2、B2 均通過（68/68 次實測）**。因此這 34 組沒有因新增輸入改變勝負，仍用原盲評的結構判定。

| 題目 | 追加檢查的行為 |
|---|---|
| ripgrep-1367 | 固定重複三個字元後接尾字的比對 |
| ripgrep-1642 | `max-count=2`、後文一行及更後面的命中 |
| ripgrep-2209 | 多個有界多行比對的替換 |
| clap-4909 | 可選值第一次省略、第二次給值時的參數位置 |
| Django-11815 | 包含翻譯成員的 Enum 名稱序列化 |
| Django-12262 | simple/inclusion tag 的 keyword-only 預設值及重複參數 |
| Express-3495 | 含空白與埠號的第一個 forwarded host |
| Dayjs-556 | 方括號內的跳脫格式與外部有效格式相鄰 |
| Dayjs-569 | 不同每週起始日與負數 weekday 偏移 |
| Dayjs-668 | 固定 UTC offset 下的時間點、複製與 locale |
| Dayjs-873 | 非零時區下的年、年月解析 |
| Bytes-643 | 複製與釋放後的底層資料獨占狀態 |
| Bytes-732 | 1 至 7 位元組、兩種位元序的有號整數 |
| Tracing-2883 | 事件巨集第一個欄位使用字串或常數欄名 |
| Vue-10027 | 巢狀 post-flush callback 的 id 排序 |
| Vue-10218 | 動態 slot 名稱的 `v-bind` 簡寫及 fallback |
| Vue-11813 | computed getter 跨連續更新接收 oldValue |

Clap 的追加檢查首次命令選到 0 個測試；修正選擇器後四臂各執行 1 個測試並通過。Tracing 首次受離線依賴解析阻擋；四臂使用原題鎖定依賴重跑後各執行 1 個測試並通過。這兩項環境／選擇器問題沒有算作 Actor 失敗。

## 29 題逐題結果

「行為」是追加輸入的勝負；「結構」是原雙盲評的勝負；「驗收」是預留契約測試。「雙方行為未過」及「雙方驗收未過」各有三組。預留測試欄是實際執行的主要選擇器。每題兩次各一組 A/B。

| 題目 | 任務要求 | 預留測試 | 第一次 | 第二次 |
|---|---|---|---|---|
| ripgrep-1367 | 固定次數重複的 literal 擷取不漏比對 | regression::r1319 | B 結構 | 平手 |
| ripgrep-1642 | --max-count 已達上限時，後續命中不延長 context | regression::r1380 | A 結構 | A 結構 |
| ripgrep-2209 | 多行搜尋與替換不重複或擴張比對內容 | regression::r2095／r2208 | A 結構 | 平手 |
| ripgrep-2488 | 多個搜尋模式的內嵌旗標彼此隔離 | regression::r2480 | 雙方行為未過 | B 行為 |
| clap-4909 | 可選值參數即使未提供值，index_of／indices_of 仍能回報參數位置 | indices_mult_optional_value | 平手 | 平手 |
| django-11815 | Enum 預設值按名稱序列化，翻譯後仍可讀取 migration | WriterTests.test_serialize_enums 等 | 平手 | 平手 |
| django-11885 | 同表的 fast delete 條件合併以減少查詢 | FastDeleteTests.test_fast_delete_combined_relationships | A 行為 | B 行為 |
| django-12262 | simple/inclusion tag 支援有預設值的 keyword-only 參數及重複參數錯誤 | template_tests.test_custom | 平手 | 平手 |
| django-12273 | 子模型主鍵重設後建立新資料列 | ModelInheritanceTest 主鍵重設測試 | B 驗收 | 雙方驗收未過 |
| django-12774 | in_bulk 接受單欄完整 UniqueConstraint，拒絕部分或複合唯一 | LookupTests.test_in_bulk_meta_constraint | B 行為 | 雙方行為未過 |
| express-3495 | req.hostname 取多段 X-Forwarded-Host 第一段並去空白／埠號 | req.hostname.js：multiple X-Forwarded-Host | 平手 | 平手 |
| dayjs-556 | 格式外掛不得插值方括號內的跳脫文字 | advancedFormat／buddhistEra.test.js | 平手 | 平手 |
| dayjs-569 | weekday 依 locale 的每週起始日讀寫 | weekday.test.js | 平手 | 平手 |
| dayjs-668 | 設定 UTC offset 後保留正確時間 | utc-utcOffset.test.js | A 結構 | B 結構 |
| dayjs-873 | YYYY／YYYY-MM 與時區格式正確解析 | customParseFormat.test.js | 平手 | 平手 |
| dayjs-973 | utcOffset 的 keepLocalTime 保持當地鐘面時間 | utc-utcOffset.test.js | B 行為 | B 行為 |
| sphinx-10673 | toctree 接受 genindex／modindex／search 產生頁面 | test_toctree_index | A 行為 | A 行為 |
| bytes-643 | Bytes 正確回報底層資料是否由自己獨有 | test_bytes：is_unique | 平手 | 平手 |
| bytes-732 | 短於八位元組的有號整數讀取要正確符號延伸 | test_buf：test_get_int | 平手 | A 結構 |
| tracing-2008 | 按事件欄位決定下層是否收到事件 | event_enabling | A 行為 | A 行為 |
| tracing-2883 | level 事件巨集接受首欄的字串或常數欄名 | tracing event／macros | 平手 | 平手 |
| Vue-10027 | 巢狀 flushPostFlushCbs 保持 job 排序 | scheduler：nested flushPostFlushCbs | 平手 | 平手 |
| Vue-10218 | slot name 支援 v-bind 簡寫 | transformSlotOutlet：v-bind shorthand | 平手 | 平手 |
| Vue-10250 | CSS v-bind 與 inline style 不產生錯誤 hydration 警告 | hydration：css v-bind | B 行為 | B 行為 |
| Vue-10874 | keyof 型別推導出正確的 runtime prop 類型 | resolveType：keyof | 雙方驗收未過 | 雙方驗收未過 |
| Vue-11694 | 直接包住 ref 的 reactive 不遞迴溢位 | reactive：ref nested in reactive | B 行為 | A 行為 |
| Vue-11761 | Array 子類的方法能追蹤項目變動並重算 computed | reactiveArray.spec.ts | B 行為 | B 行為 |
| Vue-11813 | computed getter 取得前一次結果 oldValue | computed：pass oldValue | 平手 | 平手 |
| Vue-8381 | 行內函式能取用 v-for 的迴圈變數 | compileTemplate：compiler for of | 雙方行為未過 | B 行為 |

### 三組未通過預留契約的原因

| 組別 | 已執行測試與觀察 | 與任務的關係 |
|---|---|---|
| Vue-10874 第一次與第二次 | `keyof` 測試各執行 1 項並失敗。前三臂把不同來源的型別都擴成 `String／Number／Symbol`；B2 修正部分型別，但陣列、物件與集合仍回報 `Unknown`。 | 題目要求 `keyof` 能推導 runtime prop 類型；來源 issue 的最小重現是 `string／number`，預留測試另涵蓋不同型別來源。失敗是推導結果不符，沒有新增介面要求。 |
| Django-12273 第二次 | A2 與 B2 都通過單一繼承測試；多重繼承測試在 `save()` 時撞到既有父子連結主鍵，發生 `UNIQUE constraint failed`。 | 原題範例只有單一繼承；多重繼承是同一個「子模型主鍵重設後建立新資料列」問題的延伸。這個變體已在事前預留測試，按原驗收規則列為未過。 |

Sphinx-7748 的反斜線續行格式不在交給 Actor 的題目中，已於計分前排除。上表的三組則有實際執行的任務相關測試與可定位的行為差異；報告保留題目範例與驗收變體的差別，方便讀者自行檢查契約邊界。

## 時間、token 與測試花費

以下是 **29 題計分用的 58 次 A 與 58 次 B** 產品執行。非快取輸入＝輸入減快取輸入；推理輸出已包含在輸出 token 中。

| 合計 | A | B | B 增量 |
|---|---:|---:|---:|
| 案例耗時 | 9,719.565 秒 | 15,695.894 秒 | +5,976.329 秒，+61.5% |
| 非快取輸入 token | 2,095,325 | 4,456,909 | +2,361,584，+112.7% |
| 快取輸入 token | 26,249,216 | 51,542,016 | +25,292,800 |
| 輸出 token | 303,248 | 490,709 | +187,461 |
| 預留契約通過 | 54/58 | 55/58 | +1 |

B 增加的非快取輸入中，Provider 用 **2,037,906**，Actor 在 B 條件下多用 **323,678**。Provider 共判斷 129 次、記錄 5,203.589 秒：50 次有回饋，用 2,559.659 秒及 810,104 非快取輸入 token；79 次沉默，用 2,643.930 秒及 1,227,802 非快取輸入 token。沉默仍需付費，但沉默次數本身不是品質目標。

原盲評另花 110 次 Judge 呼叫、1,691.199 秒、1,042,198 非快取輸入 token、37,916 輸出 token；這是測試成本，不是產品使用成本。被排除的 Sphinx-7748 也跑過四臂；**30 題全部原始 Actor／Provider 執行**為 6,842,105 非快取輸入 token、26,549.975 秒。時間是各案例紀錄的串行加總，不是平行工作的實際等待時間；沒有可對應的帳單金額。

17 題新增行為檢查的最終四臂執行紀錄共 68 次、458.974 秒；這是本機測試時間，沒有呼叫模型，不列入上述產品或 Judge token。環境排錯與報告撰寫的時間沒有完整帳單紀錄，故不併入這個數字。

## 可用於迭代的 nudge 證據

| 核查後結果 | 組數 | B 執行曾收到回饋 | 回饋則數 |
|---|---:|---:|---:|
| B 行為勝 | 11 | 8 | 20 |
| A 行為勝 | 6 | 2 | 2 |
| B 結構勝 | 2 | 1 | 2 |
| A 結構勝 | 5 | 3 | 5 |
| 平手 | 27 | 8 | 10 |
| B 契約勝 | 1 | 1 | 3 |
| 雙方行為或契約未過 | 6 | 4 | 8 |

這是 58 次 B 執行的回饋分布；一次執行可收到多則回饋。每組的原始 nudge 內容、先後次序、耗時及 token 已放在逐筆資料中，不能由「收到回饋」直接推定勝負原因。

**有效方向。**11 組 B 單獨通過追加行為檢查中，8 組收到 Provider 回饋；其中 7 組的內容對準被測出的邊界：ripgrep-2488 的註解吞掉群組結尾、Django-12774 的欄位別名、Dayjs-973 的夏令時間、Vue-10250 的 CSS 排除範圍、Vue-8381 的 `var` 作用域。Django-12273 第一次另有三則主鍵與父連結的回饋，B 通過預留測試而 A 未過。這些案例顯示 Provider 確實能提出承重反饋。

**失準方向。**Django-11885 第一次，回饋提議讓 QuerySet 用 `OR` 合併，漏掉 distinct 與一般查詢不相容的前提，B 在追加輸入失敗。Tracing-2008 第一次，回饋指出被 filter 拒絕時只跳過該分支，卻沒有處理巢狀事件的篩選狀態生命週期，B 仍誤呼叫外層。這是兩個具體迭代材料：固定同一 Actor 中途狀態、模型與觸發次數，分開測試 nudge 能否說清合併前提與狀態生命週期，不一次改兩個規則。

**無法歸功於回饋的勝利。**B 的 11 組追加行為勝中有 3 組 Provider 沉默，包含 Vue-11761 兩次；Vue-11694 第一次雖有回饋，內容指向 readonly ref，與這次測出的重複 effect 不同。核查後 27 組平手中，8 組 B 曾收到回饋。要改善的是回饋是否抓到承重關係，以及 Actor 後續實作，而非追求多出聲或多沉默。

A 的預留驗收 54/58，題型已有天花板；27 組結構平手壓縮區分能力。下一輪應在執行前讓任務文字、預留測試與行為邊界一致，對 A/B 使用同樣驗收，再做品味盲評。這是題庫修正，不改寫第九輪封存結果。

## 證據與驗證

- 逐筆資料：`D:\masters-nudge-benchmark\round-9-calibration\final-report\ADJUDICATION.json`，含 58 組契約、盲評、核查後結果、Provider 次數、成本與證據路徑。
- 原始 Actor／驗收：`A1-data.json`、`remaining\runs\...\result.json`、`remaining\audit.json`、`remaining\case-matrix.json`。
- 原盲評：`blind\plan.json`、`blind\judge-summary.json`、`blind\judges\...\pair.json`。
- 行為重播：原 10 題在 `semantic-audit\`，新增 17 題在 `full-audit\plan.json`、`fixture-manifest.json`、`results\` 與 `logs\`。逐組資料含追加檢查輸出及檔案雜湊。
- `final-report\adjudicate.py` 核對 29 題、58 組、54 組追加行為檢查、測試檔一致性、日誌、補丁與成本；`semantic-audit\verify_results.py` 核對原十題重播。兩項已執行並通過。

**判定範圍：**契約通過率是事前封存分數；核查後實作勝負含事後、同輸入的行為檢查，用於診斷工具效果。每題追加的是一組任務相關輸入，不能代表所有可能輸入；本輪全部 29 題與 58 組的原始分數、核查後結果和實測成本均已列出。
