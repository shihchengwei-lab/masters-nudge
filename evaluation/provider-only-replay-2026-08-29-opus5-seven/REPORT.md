# Seven-Packet Reviewer-only Replay: Sol vs Opus 5

日期：2026-08-29
來源：正式 positive-examples-v5 A/B 中實際產生 finding 的 7 個 first-change packet

## 結論

這輪不支持把 Reviewer 直接換成 Claude Opus 5。

- Opus pipeline 可運作：7/7 都產生 finding，0 provider error。
- 路由沒有增加多樣性：Opus 與原 Sol 都是 Linus 6、Lamport 1。
- 現行 52 字契約相容性差：Opus 只有 1/7 合規，6/7 為 `over_52_characters`；原 Sol 7/7 合規。
- 去識別配對盲評：Sol 7 勝、Opus 0 勝、0 平手。
- 兩者都能提出明確偏好，且都沒有 review friction；主要差距是 Opus 的承重理由較少貼合 packet。

目前最窄的判斷是：**跨家族確實改變措辭與局部關注點，但在這 7 個真實 decision point 上，Opus 更常產生合理外觀、證據對齊較弱的品味主張，沒有形成有用的互補視角。**

## 方法

1. 從 t01、t02、t03、t04、t05、t07、t10 的原始 turn、evidence 與 review log 重建 packet。
2. 對每題枚舉 evidence-record 前綴，要求恰好一個前綴命中原 `source_fingerprint`。
3. 使用正式實驗當時的 `frozen-plugin`，保持 Router、persona、base prompt、positive examples、schema 與輸出契約不變。
4. 保留原 Sol finding，不重跑對照 Provider；只呼叫 `anthropic / claude-opus-5`。
5. 將同一 packet 與兩條 Nudge 去識別，X 位置分配為 Opus 4 題、Sol 3 題，由獨立 ephemeral judge 按預先凍結 rubric 評分。

凍結 `inputs.json` SHA-256：`0444862b9324a701f5248413f64d3aeae43641a563a153850b9032483c8161ce`。

## 逐題差異

| Task | 盲評 | 主要差異 |
|---|---|---|
| t01 | Sol | Sol 明確把「正生成元查表」與「冪次方向」分工；Opus 要移除 index 特例，但替代資料流較不明確。 |
| t02 | Sol | Sol 符合 packet：partial 解包後，參數併入 args/kwargs；Opus 反對合併，理由是未被 packet 支持的重複傳參。 |
| t03 | Sol | Sol 直接守住可見需求的原生集合順序；Opus 選擇空集合特例，但沒有說出關鍵語法理由。 |
| t04 | Sol | Sol 命中 skipped 路徑不應註冊清理的邊界；Opus 的重入／tearDown 兩次情境未出現在 packet。 |
| t05 | Sol | 兩者都反對 `q == 1` 特例；Sol 額外守住正常乘積求值並把錯誤定位在 Add 分配特例。 |
| t07 | Sol | Sol 明確保留負零，符合可見 regression；Opus 把 `-0.00` 當成應修掉的漏出，直接牴觸 packet 預期。 |
| t10 | Sol | Sol 同時處理 metaclass MRO 與不得執行 getter；Opus 只有抽象的責任歸屬，漏掉 metaclass 查找需求。 |

## 評分維度

| 維度 | Sol | Opus |
|---|---:|---:|
| `specific_preference` | 14/14 | 14/14 |
| `load_bearing_reason` | 14/14 | 10/14 |
| `actionability` | 14/14 | 13/14 |
| `review_friction`（越低越好） | 0 | 0 |

這表示 Opus 的問題不是回到 review 式問答，也不是不敢表態。Opus 每題都能給出具體方向；問題是方向背後的理由較常脫離當下 packet 的事實與需求。

## 契約與運作成本

- Opus finding：7/7。
- 合規輸出：1/7；超過 52 字：6/7。
- Lens：Linus 6、Lamport 1，與原 Sol 完全相同。
- Sol latency 中位數：19.449 秒，最大 22.497 秒。
- Opus latency 中位數：25.262 秒，最大 26.943 秒；中位數約增加 29.9%。
- Claude CLI 回報 7 題 Router＋Generator cost 合計約 USD 0.880778；這是 CLI 回報值，不等於已確認的實際帳單扣款。

依目前「語義由 Provider 負責、機械層不否決」的設計，超長 finding 仍會保留並注入；這次沒有用機械層刪除或改寫 Opus 輸出。

## 限制

- 只有 7 個 packet，且全部來自同一批 SWE-bench first-change decision point，不能代表所有任務。
- 配對 judge 是 `gpt-5.6-sol`，可能存在同家族自我偏好。7–0 不能單靠票數視為無偏估計。
- 不過 t02、t07、t10 的差異可直接對照 packet：Opus 分別反對所需的參數合併、誤讀負零預期、漏掉 metaclass MRO；因此結果不只是文風偏好。
- Reviewer-only replay 沒有主模型，無法觀察採納或 patch 影響；它只衡量 intervention 本身的品質與契約相容性。
- 原 Sol 是 live first-change 輸出，Opus 是事後 deterministic packet replay；兩者 packet、prompt 與 schema 相同，但執行時間與 Provider surface 不同。

## 決策

現階段不值得直接花 10 題完整 A/B/C 成本。若要繼續 Opus 路線，下一個 gate 應先修 Anthropic-specific prompt／positive examples，使同一批 replay 至少達成：

1. 7/7 符合 52 字契約；
2. 不再出現與 packet 明示預期衝突的 finding；
3. 使用非 Sol 或人工第二評分者複核後，才進入主模型正式實驗。
