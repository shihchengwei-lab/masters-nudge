# 第六輪 Benchmark

歷史結果：本輪使用 `gpt-5.6-sol`；目前分支的較新結果與限制見[第八輪正式報告](../formal-v8/ROUND-8-REPORT.zh-TW.md)。兩輪的模型、題目及測試條件不同，不能直接當成同條件趨勢。

## 六條品味定義

1. 讓非法狀態無法被建立，而不是事後增加防護判斷。
2. 讓原因單向產生結果；事件是已發生的事實，狀態由事件推導，避免多條更新順序互相競爭。
3. 可預測性高於靈活性；消除副作用與隱藏依賴，讓局部程式的行為可以局部判斷。
4. 每項事實只有一個權威來源；其他呈現由來源推導，不同步維護多份副本。
5. 必要複雜度留在真正的邊界，核心路徑保持直接。
6. 抽象必須消除概念或分支；只增加包裝、改名或預留未證實的彈性，不算改善。

## 測試設計

- 共同條件：六個 repository 任務；每題每臂各獨立執行兩次，共 24 次。Actor 均使用 `gpt-5.6-sol`、medium reasoning、相同起始 commit、相同不可修改測試與相同執行限制。
- A 臂：不啟用 Masters’ Nudge；任務提示額外加入「請高品味的完成任務。」。
- B 臂：啟用 Masters’ Nudge，不加入上述抽象要求；每次 `apply_patch` 後由 Provider 判斷要回饋一則 Nudge 或沉默，結果回到 Actor 的工作脈絡。
- 盲評：兩位 `gpt-6-astra` 評審先取得同一組六條品味定義，再以互換的 X／Y 順序比較同題同次的 A／B；兩位結論不同時才啟用第三位。報告已將 X／Y 解盲為 A／B。
- A 臂第一輪沿用校準時保存的六筆實作：高品味要求置於任務正文前；第二輪置於共同提示末尾。文字內容與其他執行條件相同，但位置差異仍是本輪限制。

## 結果

| 指標 | A | B |
|---|---:|---:|
| 契約完成 | 12/12 | 12/12 |
| 品味勝出 | 2 | 7 |
| 平手 | 3 | 3 |
| 總耗時 | 3,900.2 秒 | 5,648.7 秒 |
| 非快取輸入 Token | 711,704 | 1,384,710 |
| 快取輸入 Token | 9,550,080 | 13,304,320 |
| 輸出 Token | 93,128 | 132,960 |

## 各組盲評

| 題目 | 次數 | 勝者 | 評語與改進 |
|---|---:|:---:|---|
| tokio-rs__tokio-6742 | 1 | B | 評審1（選 B）：B 將 spawn callback 放在 owned.bind 之前：使用者 callback 若 panic，尚未建立 runtime 持有的任務。A 先 bind 再呼叫 callback，中斷時可能留下已登錄卻未排程的任務，讓核心生命週期依賴外部 callback 正常返回。B 因而更符合非法中間狀態最小化、局部可預測性及邊界隔離。終止 hook 方面，兩者都隔離清理與 callback 的 panic；B 直接讀取 core.task_id，也避免 A 新增的 unsafe Header 存取。其餘配置傳遞與 hook 抽象結構大致相同。 改進：將 A 的 spawn callback 移至 owned.bind 前，讓 callback 成功返回後才建立並登錄任務，避免 panic 打斷 bind 到排程之間的生命週期。 / 評審2（選 B）：主要差異是使用者回呼與任務註冊的順序。B 在 owned.bind 前執行 spawn 回呼；A 在 bind 後、排程前執行，且未隔離回呼 panic，因此回呼失敗時會留下已註冊卻未完成排程的任務。B 將可能失敗的外部行為放在狀態變更前，較能避免半完成狀態，也降低更新順序的耦合。終止路徑上，兩者都將回呼與清理的 panic 分開隔離，但 B 直接透過安全存取取得 task_id，A 額外引入 unsafe Header::get_id，增加局部推理負擔。兩者的設定來源、opaque metadata 與 hooks 包裝基本等價，沒有額外拉開差距。 改進：A 應先在 owned.bind 前執行 spawn 回呼，避免回呼 panic 中斷已註冊任務的排程流程；若必須維持建立後通知，則需在同一邊界明確處理 panic 並完成任務清理。 |
| tokio-rs__tokio-6742 | 2 | B | 評審1（選 B）：B 將 spawn hook 集中在共同的任務建立入口，避免 A 在三種 scheduler 分別維護觸發時序；並直接借用配置中的 hooks，省去 A 每次終止時建立包裝、複製 Arc 的中介流程，較符合單一來源與直接核心路徑。B 也將終止 hook 放在獨立的 panic 邊界，避免前面的完成處理發生 panic 時連帶跳過通知，降低副作用耦合。不過 B 的 Handle::task_hooks 使用 unwrap，仍把「runtime scheduler 必定提供 hooks」留作隱含約定，因此未給滿分。 改進：A 可將 spawn hook 移至共同的任務建立入口，透過 Schedule 借用配置中的 hooks，讓各 scheduler 僅提供資料來源，消除三處重複的觸發邏輯。 / 評審2（選 B）：B 將 spawn hook 集中在共用的 task 建立路徑，三種排程器只提供設定；A 分別維護觸發位置與判斷，增加日後修改時行為分歧的機會。B 直接借用 callback；A 的 TaskHarnessScheduleHooks 每次包裝並複製 Arc，未消除分支。B 的 termination hook 使用獨立 panic 邊界，也避免前段完成處理的 panic 跳過通知。這些符合單向事件、局部可預測性與有效抽象原則。不過 B 將可選的 task_hooks 再 unwrap，且為 blocking task 保留整個 Handle，仍有額外耦合，因此未給滿分。兩者沒有明顯的多份可變狀態同步問題。 改進：A 可讓 Schedule 提供預設為 None 的 spawn callback 存取方法，統一在共用 task 建立路徑觸發；blocking 與 local 排程器維持 None。如此可保留其適用範圍，同時消除三種排程器各自維護的觸發邏輯。 |
| clap-rs__clap-5298 | 1 | A | 評審1（選 A）：A 的結構優勢是把互斥規則集中在 Validator::validate_conflicts，直接從 matcher 的明確輸入與子命令推導結果，與既有 exclusive 驗證共用同一層。B 在 parser 中先 resolve_pending 再檢查衝突，雖能提早拒絕進入子命令，但也讓語義驗證依賴解析階段的更新順序，增加 parser 與 validator 的責任分散。錯誤資料方面，A 的單一 String 在型別上保證必須提供一個衝突項；B 的 Vec 可表達空集合，再由呼叫端判空、建構端區分單複數、格式端重新分支。B 將 possible_subcommand 簡化為名稱辨識是優點，列出全部衝突也有實際用途，但整體仍以 A 的驗證集中度與資料協定直接性較佳。 改進：將 B 從 matcher 蒐集並判定衝突的邏輯移至 Validator::validate_conflicts，保留列出全部衝突的功能；讓解析器專注於子命令辨識與位置參數優先序，避免為這項語義驗證額外協調 resolve_pending 的時機。 / 評審2（選 A）：A 將衝突規則集中在既有 Validator::validate_conflicts，直接由 matcher 中的子命令與明確輸入參數推導結果，並沿用 required 資訊產生 usage，讓解析與驗證各有單一責任。B 雖讓 possible_subcommand 專注名稱辨識，卻把衝突驗證加入解析流程，額外要求先 resolve_pending，增加執行順序依賴。錯誤資料方面，A 的單一參數直接表達一組衝突；B 的 Vec 允許空集合，並增加單數／複數轉換與格式分支。A 仍有不足：possible_subcommand 的布林參數在不同呼叫點代表不同條件，局部可讀性較差。 改進：B 可將衝突檢查移至 Validator::validate_conflicts，由 matcher 統一提供已解析事實，移除為此加入的 resolve_pending 順序依賴，並使用驗證器既有的 required 資訊建立 usage。 |
| clap-rs__clap-5298 | 2 | B | 評審1（選 B）：B 將 possible_subcommand 收斂為名稱辨識，把位置參數的優先規則留在呼叫處，並在進入子命令前統一拒絕衝突，讓辨識、選擇與錯誤的因果更直接。A 保留辨識函式內的衝突政策，且同一布林參數在不同呼叫處代表不同條件；衝突又延至 validator 處理，使父層衝突診斷受子命令解析結果影響。B 的格式器也實際共用了衝突對象的呈現流程。不過 B 仍依賴 valid_arg_found，且建構函式接受空衝突清單，尚未完全由型別保證有效狀態。 改進：A 可將衝突檢查移到進入子命令的共同入口：先解析待處理參數，再從 matcher 推導衝突；同時移除 possible_subcommand 的布林參數，讓它只負責名稱辨識。 / 評審2（選 A）：A 將互斥規則集中於既有的 validate_conflicts，直接從 matcher 的子命令與明確提供的參數推導衝突，權威來源與驗證邊界較一致。B 雖讓 possible_subcommand 成為單純辨識函式，但新增的衝突路徑依賴 valid_arg_found，再呼叫 resolve_pending 並重新收集 matcher，讓判定跨越歷史旗標與實際匹配狀態，也使解析流程承擔額外驗證責任。兩者都未以型別排除非法組合；A 的主要優勢是狀態來源與責任集中，而非防護判斷較多。 改進：B 可將子命令衝突檢查移至 validate_conflicts，直接以 matcher 中的子命令及明確參數判定，移除新增路徑對 valid_arg_found 與 resolve_pending 的依賴；保留純粹的子命令辨識函式。 / 評審3（選 B）：B 有實質結構優勢：possible_subcommand 只負責名稱辨識，位置參數的優先規則留在呼叫端，消除了查詢函式對解析歷史的隱藏依賴；並在進入子命令前集中處理衝突，使非法組合不必先經過子命令解析才被拒絕。錯誤呈現也共用既有衝突格式流程。A 從 matcher 推導衝突值得肯定，但仍將辨識與衝突政策混在 possible_subcommand，且新增獨立的子命令格式分支。B 仍以 valid_arg_found 決定是否報錯、另從 matcher 收集內容，存在兩份事實可能不一致的結構弱點。 改進：A 可將 possible_subcommand 改為純名稱辨識，把位置參數優先判斷留在呼叫端，並在共用的子命令入口解析完待處理參數後，直接依 matcher 的明確參數判定衝突，避免先解析子命令再驗證。 |
| vuejs__core-8511 | 1 | B | 評審1（選 B）：B 將泛型引數複製後附加 _ownerScope；A 直接改寫原始 AST 引數節點，使共用節點的作用域受解析過程影響，增加隱藏副作用與更新順序依賴。B 也在呼叫邊界確認型別參數與引數存在，讓建立作用域的函式只接受完整輸入。兩者的快取策略與作用域繼承基本相同，主要優勢是 B 將本次綁定限制在新作用域內，較符合原則 1、2、3、5。 改進：A 應在 resolveGenericScope 中以 { ...type, _ownerScope: scope } 建立本次綁定的節點，再放入 genericScope.types，避免修改原始引數節點。 / 評審2（選 B）：B 在綁定泛型參數時建立節點的淺拷貝，再附上 _ownerScope；A 直接改寫傳入的型別引數節點，使共享 AST 帶入此次解析的作用域，增加後續解析對呼叫順序的隱藏依賴。B 的 createTypeScope 也要求已確認存在的參數與引數，讓建立作用域的核心路徑不必再處理缺值。兩者的快取策略基本相同，主要結構優勢是 B 將此次綁定的修改限制在新節點上，較符合局部可預測性與單向資料流。 改進：A 應將 genericScope.types[param.name] 設為 { ...type, _ownerScope: scope }，避免直接修改原始型別引數節點。 |
| vuejs__core-8511 | 2 | B | 評審1（選 B）：B 有實質結構優勢：泛型具現化時複製成員再附加作用域，避免 A 對共用成員節點覆寫 _ownerScope，使先前解析結果受後續解析順序影響，符合原則 2、3。B 保留泛型別名宣告，直接讀取 typeParameters；A 另將資訊掛到 annotation._typeParameters，增加需維護的衍生表示，B 更符合原則 4。B 也明確區分實參的呼叫端作用域與預設型別的宣告端作用域；A 統一使用呼叫端作用域，並將 constraint 當作缺省實參，混合不同語意。這些差異涉及狀態隔離與作用域建模，並非程式大小或風格。 改進：A 應先在 typeElementsToMap 的泛型路徑複製成員節點，再設定該次具現化的 _ownerScope，讓不同型別實參的解析結果各自持有成員，消除共用節點覆寫造成的順序依賴。 / 評審2（選 B）：B 在泛型解析時複製屬性節點，再綁定實例作用域；A 仍透過 typeElementsToMap 改寫共享節點的 _ownerScope，讓不同泛型實例互相影響，增加解析順序的隱藏依賴。B 也區分實參的呼叫端作用域與預設型別的宣告端作用域，並保留原始泛型宣告作為參數資訊來源；A 統一使用呼叫端作用域，且另掛 _typeParameters 維護宣告資訊。這些結構差異使 B 在可預測性、來源一致性與邊界責任上較佳。不過 B 的快取判斷依賴傳入 scope，未統一依據最終解析作用域，仍有改善空間。 改進：A 應在 typeElementsToMap 的泛型路徑建立實例專屬的屬性／方法節點，再設定 _ownerScope，避免後續實例改寫先前解析結果所持有的共享節點。 |
| anuraghazra__github-readme-stats-105 | 1 | A | 評審1（選 A）：兩者都將配色規則集中於 getCardColors，讓渲染結果單向由選項推導，沒有額外狀態同步。A 的實質優勢在主題查找邊界：只接受 themes 自有的鍵；B 使用 themes[theme] \|\| fallbackColors，會將 toString 等繼承屬性當成主題，進而產生 #undefined，讓物件原型成為隱藏依賴。B 以 themes.default 衍生儲存庫卡片預設值，比 A 重複列出共同色碼更符合單一來源原則，但 A 對有效主題集合的限制更具結構價值。 改進：B 應在 getCardColors 的主題查找處使用 Object.prototype.hasOwnProperty.call(themes, theme)，僅接受登錄的主題，其餘統一採用 fallbackColors。 / 評審2（選 A）：兩者都將配色規則集中於 getCardColors，資料流單向且無額外狀態同步。A 的實質優勢是將主題查詢限制於 themes 自有鍵；B 的 themes[theme] 會把 constructor、toString 等繼承屬性當成主題，進而產生 #undefined。A 將此複雜度留在查詢邊界，行為較可預測。不過 B 從 themes.default 衍生儲存庫卡片預設值，比 A 重複寫入三個共用色碼更符合單一權威來源。 改進：B 可將主題表改為無原型的字典，使 themes[theme] 只能取得明確登錄的主題，保留目前共用預設值的衍生方式。 |
| anuraghazra__github-readme-stats-105 | 2 | B | 評審1（選 B）：B 將卡片預設色明確傳入共用解析器，儲存庫卡片只覆寫 icon_color，其餘由 themes.default 推導，符合單一來源。A 的 default-repocard 重複保存三項相同色值，並將卡片種類混入主題名稱；未提供主題時使用儲存庫預設，未知主題或無效覆寫卻回退至統計卡片預設，使回退規則較難局部判斷。B 的 getColor 統一四種顏色的解析規則，且主題查找限定自身屬性。兩者皆無新增狀態同步或更新順序問題，主要差異在預設值建模與解析邊界。 改進：A 可移除 default-repocard 主題，讓 getCardColors 接受卡片預設色；儲存庫預設由 themes.default 加上 icon_color 覆寫推導，並統一用於缺省、未知主題及無效顏色的回退。 / 評審2（選 B）：B 將卡片預設色明確傳入解析器，並由 themes.default 推導儲存庫卡片配色，只覆寫 icon_color，符合單一來源與局部可推理性。A 複製整份預設配色到 default-repocard，並把卡片種類編碼成主題名稱；未指定主題與未知主題因此走向不同的預設來源。B 的主題查找也限定自身屬性，A 則可能把原型屬性當成主題，再靠逐色驗證回退。兩者皆為單向、無狀態更新的解析流程，這方面無實質差異。 改進：A 可移除 default-repocard 特殊主題，改由 themes.default 加上儲存庫圖示色推導卡片預設值，作為獨立參數傳入 getCardColors，統一處理缺省與未知主題的回退。 |
| sharkdp__bat-1276 | 1 | B | 評審1（選 B）：B 將「橫線或空白行」放在同一個互斥分支中，並沿用既有 grid 分支決定優先順序，輸出行為可局部判斷。A 先在函式入口輸出橫線，再於後面的 padding 分支排除 rule；同一個分隔決策分散成兩處，維護時必須同步理解與修改。依準則 3、4、5，B 有實質的局部推理優勢。兩者的狀態表示、設定階段警告與 API 結構相同；B 額外的文件與補全不構成結構加分。 改進：A 可把有 header 時的橫線輸出移到原本 padding 的位置，以單一 if/else 選擇橫線或空白行；無 header 時則納入既有 grid 分支鏈，移除入口預先輸出與後續抑制之間的耦合。 / 評審2（選 B）：B 將「畫橫線或輸出空白行」放在原本的 padding 分支內，互斥關係可由局部結構直接判斷，grid 優先序也沿用既有分支。A 在函式開頭先畫線，再於後方以 !rule 抑制空白行，將同一個分隔決策拆成兩處，維護時必須同時推理前後條件與輸出順序。B 雖在兩個 header 路徑各有畫線呼叫，仍比 A 的跨區段耦合更符合局部可預測性與核心路徑直接的原則。兩者的狀態表示與設定階段警告相同，沒有評分差異。 改進：A 可將畫線移回實際處理 padding 的位置，以同一個 if/else 決定橫線或空白行；無 header 的路徑則在既有 grid 分支後處理 rule，消除開頭輸出與後方抑制之間的依賴。 |
| sharkdp__bat-1276 | 2 | tie | 評審1（選 tie）：兩者的核心結構相同：由 StyleComponents 判定樣式，沿用 add_header_padding 決定分隔時機，並重用 print_horizontal_line；沒有新增競爭更新順序、同步維護的衍生狀態或多餘抽象。兩者也都允許 grid 與 rule 並存，以既有分支決定優先序。B 將警告留在 config 組裝處，比 A 在 style_components 計算中直接輸出 stderr 更能隔離副作用，但差異有限。A 在提前返回的路徑增加 rule 處理，屬於輸出路徑覆蓋差異，不能僅憑多一個分支判定工程品質較差。在共同契約已通過的前提下，沒有實質結構優勢。 改進：A 可將 grid 與 rule 並存的警告移至 config 取得樣式之後，讓 style_components 專注於解析與推導，避免呼叫樣式計算時隱含產生 stderr 輸出。 / 評審2（選 tie）：兩者的核心結構相同：以 StyleComponent::Rule 表達設定，沿用既有樣式轉換與水平線繪製，未新增獨立狀態或同步機制。B 在 config() 輸出警告，A 在 style_components() 內輸出，B 的計算與副作用分界較清楚；A 另在提前返回的路徑處理 rule，但這屬路徑覆蓋差異，本身不代表結構較佳。整體沒有足以拉開評分的實質結構優勢。 改進：無明確較弱者；A 可將警告輸出移至 config() 的呼叫端，使 style_components() 專注回傳樣式設定，避免查詢設定時隱含寫入 stderr。 |
| darkreader__darkreader-6747 | 1 | tie | 評審1（選 tie）：兩者唯一差異是區域變數名稱，沒有實質結構差異。兩者都在共同查詢邊界將紀錄 ID 去重並排序，使輸出順序不再依賴收集順序；消費端一致以首項取得通用規則、以 slice(1) 取得其餘規則。依六項標準，兩者的狀態表示、資料流、權威來源與抽象程度完全相同。 改進：沒有較弱者。兩者若要進一步改善，可在查詢邊界明確表示 genericFix 與 siteFixes，集中處理通用規則的辨識，減少消費端對陣列位置及 '*' 檢查的依賴。 / 評審2（選 tie）：兩者唯一差異是區域變數名稱，沒有實質結構優劣。兩者皆在 getSitesFixesFor() 將 ID 去重並按數值排序，消除結果對收集順序的依賴；消費端一致以首項取得通用修正、以 slice(1) 取得其餘修正。排序、快取存取、狀態來源與抽象程度完全相同。 改進：沒有較弱者。共同可改善之處是將「通用修正位於首項」明確表達於回傳結構，例如分別回傳 genericFix 與 siteFixes，讓消費端不必依賴陣列位置辨識角色。 |
| darkreader__darkreader-6747 | 2 | tie | 評審1（選 tie）：兩份 diff 完全相同，沒有實質結構差異。兩者都在 getSitesFixesFor() 統一去重並依 record ID 排序，讓輸出順序不再依賴記錄收集順序；消費端一致以 fixes[0] 取得通用修正、以 slice(1) 處理其餘修正。這符合可預測性、單一權威來源與邊界集中處理的原則，且未增加多餘抽象。 改進：沒有較弱的一方。共同可改善處是：目前通用修正排首仍依賴 record ID 的配置；可在索引建立邊界驗證通用修正對應首筆記錄，讓此排序前提成為明確的不變條件。 / 評審2（選 tie）：兩份 diff 完全相同，沒有實質結構差異。兩者都在 getSitesFixesFor 邊界將 ID 去重並按數值排序，消除收集順序對輸出順序的影響；消費端一致使用 fixes[0] 與 slice(1)，沒有新增同步狀態或多餘抽象。不過，通用修正排第一仍依賴 ID 順序與設定排列的約定，並非由型別保證。 改進：沒有較弱者。共同可改善處：在建立索引的邊界驗證首筆為通用修正，讓排序所依賴的資料約定在來源處成立。 |

## 證據範圍

- 未評品味：0 組。
- Provider 共呼叫 32 次：22 次回饋、10 次沉默。
- A 第一輪沿用校準時相同條件下保存的六筆實作。
- 個別 Actor、Provider 與評審證據保存在 `formal-artifacts`。
