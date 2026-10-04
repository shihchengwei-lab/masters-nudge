# Sol xhigh＋Sol medium：12題各兩次

本輪只新增F24份，Actor為GPT-6.1 Sol xhigh，Provider為GPT-6.1 Sol medium。主要比較C（Sol xhigh直接做）與E（Sol xhigh＋GPT-6 Astra medium）；兩組原交付、分數與歷史評審票保留。

**F對C：契約退步、品味持平；F對E：契約進步、品味進步。**

| 指標 | C xhigh直接做 | E xhigh＋Astra | F xhigh＋Sol |
|---|---:|---:|---:|
| 契約完成（同原條款補查） | 13/24 | 10/24 | 11/24 |
| 至少一次完成的題數 | 7/12 | 7/12 | 8/12 |
| 兩次都完成的題數 | 6/12 | 3/12 | 3/12 |
| 原凍結驗收完成份數 | 13/24 | 12/24 | 12/24 |
| Actor累計分鐘 | 393.9 | 383.8 | 502.9 |
| 每完成一份的分鐘（含失敗成本） | 30.3 | 38.4 | 45.7 |
| 送達提醒數 | 0 | 27 | 41 |
| Provider故障數 | 0 | 0 | 0 |
| Actor用量缺失份數 | 2 | 2 | 5 |

## 配對品味與花費

### F對C

契約退步，淨增-2份：新增F完成3份，失去原完成5份。共同完成8對，匿名品味F勝3、C勝3、持平2，判為持平。

全部24份Actor時間變化+27.7%。Token採雙方用量完整的19/24對；缺失不當0，完成率與耗時仍包含全部24份。

| 用量 | C | F | F變化 |
|---|---:|---:|---:|
| 未快取輸入Token | 1,959,887 | 2,961,902 | +51.1% |
| 快取輸入Token | 27,412,608 | 43,205,760 | +57.6% |
| 輸出Token | 386,774 | 473,977 | +22.5% |

排除配對：nodebb-images/1、tracing-1523/1、tracing-1523/2、regexp-404/2、clap-2297/1。

### F對E

契約進步，淨增+1份：新增F完成4份，失去原完成3份。共同完成7對，匿名品味F勝7、E勝0、持平0，判為進步。

全部24份Actor時間變化+31.0%。Token採雙方用量完整的19/24對；缺失不當0，完成率與耗時仍包含全部24份。

| 用量 | E | F | F變化 |
|---|---:|---:|---:|
| 未快取輸入Token | 2,587,243 | 2,961,902 | +14.5% |
| 快取輸入Token | 34,152,576 | 43,205,760 | +26.5% |
| 輸出Token | 422,577 | 473,977 | +12.2% |

排除配對：nodebb-images/1、tracing-1523/1、tracing-1523/2、regexp-404/2、clap-2297/1。

## 逐題完整交付

| 題目 | C | E | F | F對C | F對E |
|---|---:|---:|---:|---|---|
| nodebb-images | 2/2 | 0/2 | 1/2 | 退步 | 進步 |
| ansible-type-tags | 1/2 | 1/2 | 1/2 | 持平 | 持平 |
| element-sessions | 2/2 | 2/2 | 2/2 | 持平 | 持平 |
| flipt-segments | 2/2 | 1/2 | 1/2 | 退步 | 持平 |
| openlibrary-index-state | 0/2 | 0/2 | 1/2 | 進步 | 進步 |
| proton-mailbox-retry | 2/2 | 2/2 | 2/2 | 持平 | 持平 |
| flipt-storage-cache | 2/2 | 1/2 | 2/2 | 持平 | 進步 |
| fb-metaflow-stubs | 0/2 | 0/2 | 0/2 | 持平 | 持平 |
| tracing-1523 | 0/2 | 0/2 | 0/2 | 持平 | 持平 |
| proton-untrusted-keys | 2/2 | 2/2 | 0/2 | 退步 | 退步 |
| regexp-404 | 0/2 | 0/2 | 0/2 | 持平 | 持平 |
| clap-2297 | 0/2 | 1/2 | 1/2 | 進步 | 持平 |

## 執行條件與審計

F與E使用同一凍結桌面CLI 0.159.2及SHA 34549ded6e2aee87c911c62d025e52e26c488683d0f489cd68f756baef1a6df6；Actor xhigh、Provider medium、任務、基底、凍結工具／定稿prompt、兩工作槽、每Actor30分鐘、最多3則提醒與2次沉默停止均相同，僅換Provider模型。C使用較早CLI 0.159.0／SHA86e8ef1013f98df51fdeea446597f7e3ca32e454d1d4d8c0402a68b03c311d70；F-C是配置效益比較，包含此執行檔差異。

三臂Flipt與Clap的六份交付使用相同原條款fixture，Clap另有原基底正向對照。原score-v3不修改，摘要另保留frozen_completed及已確認缺口；盲評僅比較共同完整交付。兩位Astra medium交換X/Y順序，意見不同才第三位，使用相同凍結準則。未復現的靜態契約疑點另列，不自動扣分。失敗與超時保留，不重抽、不修Actor交付。

評審56次、累計49.8分鐘，輸入4,882,285（快取3,270,912）、輸出56,286Token。評審與原生補查花費另列；Actor時間含等待Provider，Token含Actor＋Provider（C僅Actor）。沒有逐次金額帳單，不將Token當成實際金額。

[完整數據](E:/masters-nudge-benchmark/sol61-f-xhigh-sol-provider-12case-20261002/results-summary.json)、[材料與harness程序](E:/masters-nudge-benchmark/sol61-f-xhigh-sol-provider-12case-20261002/MATERIALS.zh-TW.md)、[來源指紋](E:/masters-nudge-benchmark/sol61-f-xhigh-sol-provider-12case-20261002/harness-source-manifest.json)、[原資料指紋](E:/masters-nudge-benchmark/sol61-f-xhigh-sol-provider-12case-20261002/reference-manifest.json)、[完整性核對](E:/masters-nudge-benchmark/sol61-f-xhigh-sol-provider-12case-20261002/final-integrity.json)、[原條款補查](E:/masters-nudge-benchmark/sol61-f-xhigh-sol-provider-12case-20261002/diagnostics-status.json)、[盲評疑點](E:/masters-nudge-benchmark/sol61-f-xhigh-sol-provider-12case-20261002/blind-contract-concerns.json)。
