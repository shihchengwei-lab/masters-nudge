# Element 有／無 Nudge：真實紀錄聊天對照

錄製日期：2026-10-12。這是新做的一組對照，兩份都從相同基底獨立開始；沒有接續舊答案，也沒有為畫面、功能或品味重抽。

首頁使用[14 秒左右聊天對照](../images/element-chat-replay.mp4)。左邊是沒有提醒的真實嘗試，右邊是有提醒的真實嘗試。兩邊從相同任務獨立開始，聊天逐步出現；右邊多了中途提醒，接著兩邊分別顯示已保存修改的白話摘要。

![左右聊天對照：沒有提醒與有提醒後的實際修改](../images/element-chat-replay.gif)

**這是聊天畫面重建，非 Codex 原始介面或螢幕錄影。** AI 訊息採中文節譯，提醒採白話轉述，英文原文保存在來源檔。「它實際改了什麼」是修改紀錄摘要，不冒充 AI 發言。沒有新增「我接受提醒」之類原紀錄不存在的回應，也沒有模擬打字。左右各自節錄，不是同步耗時比較；中間操作、等待與第二則提醒略過。

修改差異是：沒有提醒的一邊，顯示勾選結果與處理點選仍各自決定紀錄來源；有提醒的一邊，收到提醒後的下一次修改把兩者成對提供，共同決定紀錄來源。這個約束保留在最終答案。這說明實際採納的結構改動，不表示左邊在本次驗收中發生勾選錯亂；兩邊均通過本次固定驗收。

第一則提醒為 `12:48:51.472 UTC`，下一次產品修改為 `12:49:20.907 UTC`。成對型別節錄已逐行核對，確實保留在 B 最後 Patch 中。右邊 AI 的前後訊息則分別為 `12:47:54.413 UTC` 與 `12:50:07.170 UTC`。

[聊天重播來源](element-live-recording/chat-replay-source.json)保存左右英文原話、中文節譯、實際提醒、完整下一次工具呼叫、事件時間與修改摘要的程式依據；[媒體核對紀錄](element-live-recording/chat-replay-integrity.json)保存影片指紋。英文 README 使用[英文聊天版](../images/element-chat-replay.en.mp4)，同一組紀錄、同樣 14 秒；其指紋見[英文媒體核對紀錄](element-live-recording/chat-replay-integrity.en.json)。可用 `python tools/render_chat_replay.py` 重建中文版，或加上 `--language en` 重建英文版，不呼叫 Actor 或 Provider。

[67 秒原錄影剪輯](../images/element-live-comparison.mp4)另保留供稽核。其「實際下一次修改」標題依工具呼叫時間設定，但畫面仍停在前一份輸出，沒有清楚拍到相關結構修改，因此不再作為首頁展示。

## 看到了什麼

左邊直接實作並交付。右邊的第一份產品修改也把選取清單與更新方法各自設為可選，接著實際收到：

```text
OBSERVED: FilteredDeviceList: split fallbacks
WHY: Can discard selection
STRUCTURE: Selection props: neither or both; one owner for IDs
REQUIRED: Toggles update selection and count
```

下一份產品修改加入成對的 `Props` 型別，並以共同判斷選出讀寫來源。第二則 Nudge 隨後提醒先收窄 `Props` 才解構清單與更新方法；Actor 的下一份產品修改依此調整。成對約束保留在最後答案中。

**兩份都通過本次固定驗收。** 這裡呈現的是提醒對後續修改的影響：原本可各自提供的兩項輸入，改為一起提供或一起省略，排除容易接錯的組合。這次沒有新增匿名評審或品味勝負票，亦不宣稱 B 的每一處程式都優於 A。

## 錄影與字幕

背景是新執行時，以 FFmpeg 擷取傳統主控台視窗的真實 Codex CLI 畫面。沒有重新繪製程式碼、播放舊事件冒充新操作，或替 Actor 編寫發言。

Nudge 經同步 MCP Hook 送入 Actor 上下文，終端機顯示的送達紀錄會很快被後續輸出捲走。因此影片把**實際送入 Actor 的四欄原文**放在字幕區，附上標明「字幕譯意」的中文說明。提醒時間與下一份 `apply_patch` 呼叫來自本輪真實上下文與事件時間。

兩條線各自壓縮，完成的一側停留在交付畫面，**不能用影片左右長度或畫面位置比較耗時**。字幕下的固定驗收結果，是 Actor 結束後獨立執行的檢查；不是改寫 Actor 當時說了什麼。

Actor 自行跑的公開測試仍各有三個既有快照因需求指定的新 `data-testid` 不一致而失敗，原測試與快照沒有修改。這些公開測試輸出保留在影片及原始紀錄；本次固定驗收使用原研究的已公開驗收套件，兩份均通過。兩種測試結果不能混為同一項判定。

## 本次配置與結果

| 項目 | A：沒有 Nudge | B：有 Nudge |
|---|---|---|
| Actor | GPT-6.1 Sol medium | 相同 |
| Provider | 無 | GPT-6.1 Sol medium |
| 基底 | `7a33818bd7ec89c21054691afcb6db2fb2631e14` | 相同 |
| 任務 | Element 多裝置勾選與批次登出 | 正文相同；公開測試 helper 路徑指向各自獨立目錄 |
| CLI | 0.159.1，同一執行檔 | 相同 |
| Actor 時限 | 1800 秒 | 相同 |
| Actor 實際耗時 | 372.125 秒 | 459.625 秒，包含同步 Provider 等待 |
| 固定驗收 | 通過，107 項測試記錄 | 通過，107 項測試記錄 |
| 已送達提醒／沉默／故障 | 無 Provider | 2／2／0 |

錄影使用原 A／B 研究的凍結工具與 Sol medium 配置，沒有改動本機平常使用的 Provider 選擇。原 A／B 研究使用 CLI 0.159.0；這次可用的是 0.159.1，所以本次展示另列，不混入原七臂排名。沒有另加採納提示、手動修改答案或依結果重抽。

## 原始證據

- [紀錄包](element-live-recording/evidence.zip)：兩份任務、實際啟動參數、CLI 原始輸出、最後 Patch、Provider 嘗試、固定驗收原始日誌及執行腳本。包內 `source-index.json` 保存逐檔 SHA-256；不包含私人登入憑證。
- [剪輯切點與實際上下文](element-live-recording/edit-manifest.json)：各段來源時間、倍速、停格，以及兩則 Nudge 的原文和下一次實際工具呼叫。
- [A 最後 Patch](element-live-recording/A-final.patch)、[B 最後 Patch](element-live-recording/B-final.patch)。
- [結果與用量](element-live-recording/results-summary.json)、[影像與證據指紋](element-live-recording/integrity.json)。缺失用量保留為未知，不當作零。
- [原公開任務與條款](../../benchmark/model-comparison-20261004/protocol/evaluation/cases/element-sessions/task.md)、[原始驗收契約](../../benchmark/model-comparison-20261004/protocol/evaluation/cases/element-sessions/contract.json)。

本機完整未剪輯錄影、獨立解題工作目錄與原始 session 保留在 `E:\masters-nudge-benchmark\element-live-capture-20261012\`。公開素材另存影像 SHA-256，沒有把登入資料加入 repo。原題目已有修改與 Git 暫存狀態的指紋，在執行前後一致。

## 重建剪輯

有本機完整錄影時，從 repo 根目錄執行：

```powershell
python tools/edit_live_capture.py E:\masters-nudge-benchmark\element-live-capture-20261012
```

素材製作需要 FFmpeg、Python 與 Windows 微軟正黑體。這個命令只重新剪輯已保存的錄影，不啟動 Actor 或 Provider；切點由原始上下文與錄影時間推導。

原歷史 A1／B1 的[程式結構案例](element-sessions.zh-TW.md)與[七臂品味覆核](../../benchmark/model-comparison-20261004/taste-review/README.zh-TW.md)保留不變。程式來源與授權見[來源說明](../../benchmark/model-comparison-20261004/protocol/evaluation/ATTRIBUTION.md)。
撤下的 14 秒節錄、剪輯腳本與切點紀錄保存在本機實驗目錄的 `edited/rejected-preview/`，不再作為首頁展示。
