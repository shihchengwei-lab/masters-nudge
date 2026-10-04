# GPT-6.1 Sol：xhigh 直接實作與封存 medium 對比

本輪提高思考深度有改善：相對A medium直接實作，C xhigh契約完成由6/24增至13/24，解出題數由3/12增至7/12；共同完成的6對品味C勝4、A勝2。相對B medium加工具，C多完成4份，品味4比4持平。C累計耗時393.9分鐘，比A多51.9%；同22對的未快取輸入多67.7%、輸出多128.6%。

A為medium直接做，B為medium加定稿工具，C為xhigh直接做。每題各兩次，12題、每臂24份；本次只新增C24份，A及B沿用封存交付與契約評分。

A-C是思考深度的主要比較：模型、任務文字、原始基底、CLI、環境、每Actor30分鐘及固定驗收一致，只將medium改成xhigh。C關閉hooks、plugins及Provider。B-C另比較「medium加工具」與「xhigh直接做」的交付；A-B品味票數保留原封存結果，不重評。

| 指標 | A medium直接 | B medium加工具 | C xhigh直接 |
|---|---:|---:|---:|
| 契約完成份數 | 6/24 | 9/24 | 13/24 |
| 至少一次完成的題數 | 3/12 | 6/12 | 7/12 |
| 兩次都完成的題數 | 3/12 | 3/12 | 6/12 |
| Actor累計耗時 | 259.3分鐘 | 296.0分鐘 | 393.9分鐘 |
| 沒有完整Actor用量紀錄 | 2 | 1 | 2 |

B耗時包含同步等待Provider；C及A沒有Provider。契約由固定功能驗收及沿原任務規則的語意執行審核共同決定。超時與失敗樣本保留，不因結果重抽或修交付。

## C 對 A

契約完成「進步」：C 13/24、A 6/24，差+7份。共同完成6對、只有C完成7對、只有A完成0對。

品味「進步」：共同完成的6對，C勝4、A勝2、持平0。評審只看匿名程式與原任務，依原固定準則；兩位GPT-6 Astra medium交換X/Y，意見不同才加入第三位裁決。

用量比較採雙方完整的22/24對；B包含Actor與Provider，A/C僅Actor。

| 用量 | A | C | C變化 |
|---|---:|---:|---:|
| 未快取輸入Token | 1,335,556 | 2,239,909 | +67.7% |
| 快取輸入Token | 14,849,280 | 31,135,744 | +109.7% |
| 輸出Token | 196,373 | 448,896 | +128.6% |

全部24份Actor累計耗時變化：+51.9%。用量缺失不當成0；對應雙方均排除於Token表，完成率與耗時保留全24對。排除清單：tracing-1523/1、tracing-1523/2。

## C 對 B

契約完成「進步」：C 13/24、B 9/24，差+4份。共同完成8對、只有C完成5對、只有B完成1對。

品味「持平」：共同完成的8對，C勝4、B勝4、持平0。評審只看匿名程式與原任務，依原固定準則；兩位GPT-6 Astra medium交換X/Y，意見不同才加入第三位裁決。

用量比較採雙方完整的22/24對；B包含Actor與Provider，A/C僅Actor。

| 用量 | B | C | C變化 |
|---|---:|---:|---:|
| 未快取輸入Token | 2,523,451 | 2,239,909 | -11.2% |
| 快取輸入Token | 32,407,168 | 31,135,744 | -3.9% |
| 輸出Token | 300,751 | 448,896 | +49.3% |

全部24份Actor累計耗時變化：+33.1%。用量缺失不當成0；對應雙方均排除於Token表，完成率與耗時保留全24對。排除清單：tracing-1523/1、tracing-1523/2。

## 逐題交付

| 題目／次數 | A契約 | B契約 | C契約 | A-C品味 | B-C品味 |
|---|---|---|---|---|---|
| nodebb-images／1 | 失敗 | 完成 | 完成 | — | B |
| nodebb-images／2 | 失敗 | 失敗 | 完成 | — | — |
| ansible-type-tags／1 | 失敗 | 完成 | 完成 | — | C |
| ansible-type-tags／2 | 失敗 | 失敗 | 失敗 | — | — |
| element-sessions／1 | 完成 | 完成 | 完成 | A | B |
| element-sessions／2 | 完成 | 完成 | 完成 | A | B |
| flipt-segments／1 | 完成 | 完成 | 完成 | C | C |
| flipt-segments／2 | 完成 | 完成 | 完成 | C | C |
| openlibrary-index-state／1 | 失敗 | 失敗 | 失敗 | — | — |
| openlibrary-index-state／2 | 失敗 | 失敗 | 失敗 | — | — |
| proton-mailbox-retry／1 | 完成 | 完成 | 完成 | C | C |
| proton-mailbox-retry／2 | 完成 | 完成 | 完成 | C | B |
| flipt-storage-cache／1 | 失敗 | 失敗 | 完成 | — | — |
| flipt-storage-cache／2 | 失敗 | 失敗 | 完成 | — | — |
| fb-metaflow-stubs／1 | 失敗 | 失敗 | 失敗 | — | — |
| fb-metaflow-stubs／2 | 失敗 | 失敗 | 失敗 | — | — |
| tracing-1523／1 | 失敗 | 失敗 | 失敗 | — | — |
| tracing-1523／2 | 失敗 | 失敗 | 失敗 | — | — |
| proton-untrusted-keys／1 | 失敗 | 失敗 | 完成 | — | — |
| proton-untrusted-keys／2 | 失敗 | 失敗 | 完成 | — | — |
| regexp-404／1 | 失敗 | 失敗 | 失敗 | — | — |
| regexp-404／2 | 失敗 | 失敗 | 失敗 | — | — |
| clap-2297／1 | 失敗 | 完成 | 失敗 | — | — |
| clap-2297／2 | 失敗 | 失敗 | 失敗 | — | — |

## 評審花費與審計

本次評審54次，累計38.5分鐘；輸入4,599,267、其中快取3,004,160、輸出52,968 Token。與Actor／工具用量分列；使用Codex帳號，沒有逐次金額帳單。

原封存A-B品味：6對，B勝5、A勝1、持平0；這是歷史票數，沒有重抽。

[完整數據](E:/masters-nudge-benchmark/sol61-c-xhigh-direct-12case-20261001/results-summary.json)、[材料與程序](E:/masters-nudge-benchmark/sol61-c-xhigh-direct-12case-20261001/MATERIALS.zh-TW.md)、[來源指紋](E:/masters-nudge-benchmark/sol61-c-xhigh-direct-12case-20261001/harness-source-manifest.json)、[完整性核對](E:/masters-nudge-benchmark/sol61-c-xhigh-direct-12case-20261001/final-integrity.json)。

## 改善落在哪裡

相對A，新增完成NodeBB兩次、Ansible第一次、Flipt快取兩次、Proton不可信金鑰兩次，共7份；原A完成的6份均保留。相對B，新增NodeBB第二次、Flipt快取兩次、Proton不可信金鑰兩次，失去Clap第一次，淨增加4份。OpenLibrary、Metaflow、Tracing、Regexp、Clap仍兩次皆未完成；Tracing兩次超過原30分鐘上限，其餘失敗保留於逐份score-v3.json。

品味改善集中在Flipt多條件與Proton重試，四個A-C配對均勝；Element兩對皆退步。評審認為Flipt將雙格式集中於同一份條件資料，少了多欄位同步與整個規則的轉換分支；Proton將延遲回應／重試綁定到產生它們的請求，減少舊請求改動新清單的可能。Element則讓登出流程同時管理介面選取，比A多承擔一項責任。這些是匿名評審的結構判讀，具體來源與反證位置見各judge result.json；不是由耗時或程式碼長短推定品味。

B-C八對，C勝Ansible第一次、Flipt多條件兩次、Proton重試第一次；B勝NodeBB第一次、Element兩次、Proton重試第二次。Flipt第一次B-C兩位評審意見不同，由第三位裁決；其餘新配對正反兩位一致。品味只比較雙方已完成的配對，新增單方成功不計品味勝。各票的contract_concerns是額外觀察，保留原文；本輪完成數沿固定驗收與原執行規則計算。

## 評分基礎設施恢復

NodeBB C1首份執行評審因讀檔工具要求Git根目錄，無法讀取非Git的交付材料目錄，回傳environment_error。首份評審、暫定評分與原材料全部保留；以同一prompt、schema、模型及規則補通唯讀Actor材料後，恢復評審判pass。恢復在匿名比較前完成，原Actor與功能驗收均未重跑。額外一次評審已包含於上列54次／38.5分鐘，25份來源快照包含原23份與兩份恢復程式；細節見MATERIALS.zh-TW.md及infrastructure-recovery/nodebb-images-C1。

最終核對：24份皆實際使用GPT-6.1 Sol xhigh、Provider呼叫0；執行規則22pass／2fail（兩次Tracing超時）。封存A／B、固定輸入及25份來源指紋一致，12題原工作樹與暫存條目已還原。
