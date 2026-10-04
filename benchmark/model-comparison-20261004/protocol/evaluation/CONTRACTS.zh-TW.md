# 任務契約與固定驗收對照

每題原文是唯一需求來源；下表列出驗收要觀察的行為。完整條文引用與執行指令見各題 `contract.json`。`reserved` 包含該題固定的原始測試；其他名稱是本包內的補充檢查。

信箱題依[官方修法與原驗收](cases/proton-mailbox-retry/contract-resolution.json)釐清重試時序，原題目另存於該題 `source-task.md`。執行範圍、時限與禁止取得外部原實作等限制，依[評測規格](PROTOCOL.zh-TW.md)另核對原始執行紀錄。

## 刪除封面、頭像與帳號時清理檔案

[完整題目](cases/nodebb-images/task.md) · [逐條來源與檢查](cases/nodebb-images/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | 本機／遠端圖片判別；四種副檔名；明訂兩個 path helper 介面。 | `reserved`、`nodebb_images_files.js` |
| C02 | 群組清除三個欄位及對應原圖／縮圖。 | `reserved`、`nodebb_group_variants.js` |
| C03 | 使用者與 socket 移除入口、集中 helper、欄位清理及 uid 錯誤。 | `reserved`、`nodebb_images_files.js` |
| C04 | 帳號刪除清完該使用者所有 cover/avatar 格式；單類移除不越界。 | `reserved`、`nodebb_images.js`、`nodebb_images_files.js` |
| C05 | 檔案已不存在仍能完成移除。 | `reserved`、`nodebb_images_files.js` |

## 設定型別轉換保留來源標記

[完整題目](cases/ansible-type-tags/task.md) · [逐條來源與檢查](cases/ansible-type-tags/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | None 與未知型別保持原值；INI 字串仍解引號。 | `reserved` |
| C02 | bool 非嚴格轉換、不可雜湊值回 false；bool 轉 int。 | `reserved` |
| C03 | 型別接受範圍與精確 ValueError；none 只接受 None 或字面字串。 | `reserved`、`ansible-type-tags-v2-input.py`、`ansible-none-literal-input.py` |
| C04 | list／dict 具體容器、分割／去空白／去引號、路徑型別與 INI。 | `reserved` |
| C05 | 轉換保留 Origin；分割各元素帶 tag；不變值保持物件身分。 | `reserved`、`ansible-type-tags-v2-input.py` |
| C06 | 三個 tmp 別名產生不同空目錄，不傳播 tag。 | `reserved`、`ansible-type-tags-v2-input.py` |

## 多裝置選取與批次登出

[完整題目](cases/element-sessions/task.md) · [逐條來源與檢查](cases/element-sessions/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | 逐裝置選取／取消、checked 與計數一致。 | `reserved` |
| C02 | 單次請求包含目前選取 ID；成功後更新列表。 | `reserved` |
| C03 | 取消清空選取；三個明訂 testid。 | `reserved` |
| C04 | 點 checkbox／資訊切換選取；點動作按鈕不切換。 | `reserved` |
| C05 | 切換篩選清空選取。 | `reserved` |
| C06 | 互動驗證取消後清除 loading。 | `reserved` |
| C07 | 保持既有對外元件 props。 | `reserved` |

## 單一／多重分群的匯入、匯出與保存

[完整題目](cases/flipt-segments/task.md) · [逐條來源與檢查](cases/flipt-segments/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | rule segment 可序列化／反序列化字串與 keys/operator 物件。 | `reserved`、`snapshot` |
| C02 | 單 segment 的 rule／rollout 建立、更新、讀回採 OR。 | `reserved` |
| C03 | 單／多 segment 匯入匯出；rollout 格式相容。 | `reserved` |
| C04 | snapshot 保留兩種 rule 表示及 operator。 | `snapshot` |

## 依記錄類型產生與彙整搜尋索引更新

[完整題目](cases/openlibrary-index-state/task.md) · [逐條來源與檢查](cases/openlibrary-index-state/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | state 獨立預設、kwargs、相加不改來源、commit OR、has_changes、JSON 與 clear。 | `reserved`、`state-api` |
| C02 | Solr 單一請求 body；成功、非 JSON、錯誤 status 與傳輸失敗保留行為。 | `reserved`、`openlibrary-responses-input.py` |
| C03 | 所有 updater 的 awaitable 介面、prefix predicate、可迭代 preload。 | `reserved`、`openlibrary-preload-iterable-input.py` |
| C04 | work／edition 更新；孤立 edition 合成 work 並保留 title；work preload editions。 | `reserved`、`openlibrary-edition-keys-input.py`、`openlibrary-orphan-batch-input.py` |
| C05 | author 以自己 key 產生索引更新。 | `reserved` |
| C06 | 跨 type batch 彙整；commit 預設 true／false；記憶體文件更新不依賴外部 Solr。 | `reserved`、`openlibrary-orphan-batch-input.py` |
| C07 | 刪除各型別只留 delete；redirect 先刪自己再處理目標含 deleted target。 | `reserved`、`openlibrary-redirects-input.py` |

## 郵件清單操作重疊與延遲重試

[完整題目](cases/proton-mailbox-retry/task.md) · [逐條來源與檢查](cases/proton-mailbox-retry/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | 修改操作期間不請求；最後操作結束後由正常畫面更新流程恢復一次到期的刷新。 | `reserved`、`mailbox-contract` |
| C02 | 失敗／Stale 分別等 2／1 秒；到期仍有操作則保留刷新，不接受 Stale 回應。 | `reserved`、`mailbox-contract` |
| C03 | 等待有效回應時保持 loading／placeholders；有效回應後顯示內容。 | `reserved`、`mailbox-contract` |
| C04 | 明訂 actions、reducers 與 pendingActions selector 介面。 | `mailbox-contract` |

## 跨層旗標快取與請求儲存政策

[完整題目](cases/flipt-storage-cache/task.md) · [逐條來源與檢查](cases/flipt-storage-cache/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | 私有型別 context key 與 WithDoNotStore／IsDoNotStore。 | `reserved`、`cache-api` |
| C02 | 明訂 metadata constants；interceptor 的直接簽章、mark 與回傳不變。 | `reserved`、`server-wiring` |
| C03 | 兩種 evaluation request 仍快取；GetFlag 不在 request interceptor。 | `reserved`、`cache-api`、`server-wiring` |
| C04 | JSON／Proto helpers 與 marshal 函式參數；hit、miss、編解碼與 cache error。 | `reserved`、`cache-api` |
| C05 | storage GetFlag 的 key、hit、miss、source error。 | `reserved` |
| C06 | no-store 不寫入 storage cache。 | `reserved` |
| C07 | 不更改 gRPC wiring 以外的舊 helper／interceptor 呼叫者以遷就新介面。 | `scope` |

## 由執行期物件產生 Python 型別宣告

[完整題目](cases/fb-metaflow-stubs/task.md) · [逐條來源與檢查](cases/fb-metaflow-stubs/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | annotation 型別、泛型、Union／Callable、TypeVar／NewType、prefix／imports、自我／字串引用；None／empty 回空字串。 | `reserved`、`metaflow_members_input.py`、`annotation-api` |
| C02 | class 繼承／metaclass、方法／屬性／setter／init／runtime 欄位及 imports。 | `reserved`、`metaflow_members_input.py`、`metaflow_typed_dict_keys_input.py`、`class-api` |
| C03 | 函式簽章、各 parameter kind、defaults、decorators、overload、docstring、ignore 與指定錯誤行為。 | `reserved`、`function-api`、`metaflow_docquotes_input.py` |
| C04 | reset 清除每份模組的累積資料與追蹤；模組互不污染。 | `reserved`、`reset-api` |
| C05 | 有效型別宣告與模組邊界；保留資料成員／引用，不把外部 import 冒充本模組定義。 | `reserved`、`metaflow_review_members_input.py`、`class-api` |

## 多層追蹤過濾的獨立視圖與組合

[完整題目](cases/tracing-1523/task.md) · [逐條來源與檢查](cases/tracing-1523/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | registry feature 下指定 Filter／Filtered／FilterFn／DynFilterFn API、defaults 與 builder。 | `reserved` |
| C02 | 事件、span callback、Context lookup／scope／parent 的過濾視圖；子樹 AND，兄弟獨立。 | `reserved`、`tracing_contract_v2.rs`、`tracing_judge_concerns.rs` |
| C03 | global veto、local rejection、all-reject disabled。 | `reserved`、`tracing_contract_v2.rs`、`tracing_judge_concerns.rs` |
| C04 | 靜態 interest 可快取；動態每次求值；巢狀／重入保持狀態。 | `reserved`、`tracing_judge_concerns.rs` |
| C05 | max hint 合成涵蓋消費者，無界與外層限制。 | `reserved`、`tracing_hint_bounds.rs` |
| C06 | 既有 layering、downcast、boxed、reload 與 close cleanup。 | `reserved`、`tracing_contract_v2.rs` |

## 未釘選金鑰的加密偏好

[完整題目](cases/proton-untrusted-keys/task.md) · [逐條來源與檢查](cases/proton-untrusted-keys/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | vCard signed boolean 欄位與 CRLF 讀寫。 | `reserved`、`untrusted_preserve_false.test.ts` |
| C02 | pinned／untrusted 分離，缺省 true、無 key undefined、internal 規則。 | `reserved` |
| C03 | 外部 WKD encrypt/sign 依模型偏好，其餘輸出保留。 | `reserved` |
| C04 | UI toggle／sign、無 keys、有效／無效 keys、警告開關與儲存。 | `reserved`、`untrusted_upload.test.tsx`、`untrusted_preserve_false.test.ts` |
| C05 | 儲存正確偏好類別；無 key 不寫；email grouping、排序、加密時 signing true。 | `reserved`、`untrusted_preserve_false.test.ts` |

## 正規表示式中的巢狀冗餘分支

[完整題目](cases/regexp-404/task.md) · [逐條來源與檢查](cases/regexp-404/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | 題目列出的六組巢狀冗餘例及範圍端點；保留範圍內部字元。 | `reserved` |
| C02 | 巢狀 alternatives／class endpoint；JavaScript 匹配方向、capture、安全與選項相容。 | `reserved`、`regexp_contract.js`、`regexp_direction.js`、`regexp_judge_concerns.js` |
| C03 | 嚴格子集與 prefix 已覆蓋的訊息／位置正確，保留 capture 警告。 | `reserved`、`regexp_judge_concerns.js` |

## 重複選項的分組與覆寫

[完整題目](cases/clap-2297/task.md) · [逐條來源與檢查](cases/clap-2297/contract.json)

| 條款 | 驗收行為 | 檢查 |
|---|---|---|
| C01 | 公開 grouped_values iterator；absence、occurrence/value order；long／short／equals／delimiter。 | `reserved` |
| C02 | 多 positionals／--／flattened APIs 相容。 | `reserved` |
| C03 | 明訂 self override 清掉先前整組，包含 repeatable 與空組。 | `reserved`、`self-override` |
| C04 | AllArgsOverrideSelf 的短旗標組合。 | `reserved` |
| C05 | 既有 validation／required／conflict／occurrence／default 相容。 | `reserved` |
