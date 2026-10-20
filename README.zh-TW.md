# Masters’ Nudge

繁體中文 | [English](README.md)

> **測試通過，只證明行為；不能證明設計。**
>
> 綠燈代表現在能過。六個月後呢？

AI 可以把功能做出來、讓測試通過，程式結構卻仍靠同步狀態、特殊分支與局部補丁維持正確。需求再變，這些補救也可能繼續增加。

Masters’ Nudge 在 Codex 寫程式時加入一則簡短的結構建議。每次修改後，提供提醒的模型（Provider）唯讀檢查任務與相關程式；寫程式的模型（Actor）決定是否採納，再繼續實作與驗證。Provider 找不到具體改善方向時，就保持沉默。

## 看 Actor 真正收到提醒，再修改程式

Element 的多裝置勾選與批次登出任務中，**兩份都通過固定驗收。** 右邊的 AI 收到提醒後，下一次修改把「顯示勾選結果」和「處理點選」綁在一起，讓兩者使用同一份紀錄。

![14 秒左右聊天對照：左邊沒有提醒；右邊收到提醒後，把顯示和點選改為使用同一份紀錄。](docs/images/element-chat-replay.gif)

*聊天畫面依真實紀錄重建，訊息採節譯、提醒採白話轉述，修改以摘要呈現；中間操作與等待省略。[原始紀錄與驗收](docs/examples/element-live-recording.zh-TW.md)。*

## 效果與代價

以 **GPT-6.1 Sol xhigh 同時擔任 Actor 與 Provider**，完整交付與直接實作同為 **13/24 次**；在**雙方共同完成的 11 組程式碼比較**中，結構覆核結果為 **7 勝、0 敗、4 平**。

代價是**累計時間增加 26.9%**、**未快取輸入 Token 增加 73.1%**。基準涵蓋十二道任務、七種配置，每配置各跑 24 次；Token 比較使用 19 組有完整用量紀錄的共同位置。

[主要比較報告](benchmark/model-comparison-20261004/REPORT.zh-TW.md) · [程式碼覆核結果](benchmark/model-comparison-20261004/taste-review/README.zh-TW.md) · [測試方法與數據](benchmark/README.zh-TW.md)

後續沿用既有實作續解，已完成 Regexp、Metaflow、Tracing 三題。詳見[續解結果](benchmark/unresolved-challenges-20261004/continuation-20261017/README.zh-TW.md)、[先前探索紀錄](benchmark/unresolved-challenges-20261004/README.zh-TW.md)及[九題補充分析](benchmark/model-comparison-20261004/PRIMARY.zh-TW.md)。

## 作用原理

Actor 的後續生成受任務、既有程式與前面的解題脈絡影響。遇到問題時，沿著原本方向加一個判斷或特例，是一條容易延續的局部修補路徑。

Nudge 把另一種具體的資料與責任安排注入上下文，讓「從結構上消除補救」也成為後續生成的候選方向。它希望影響 Actor 接下來選中的 token，提高採用更好結構的機率。

Provider 用五條品味準則尋找這種方向：讓非法狀態無法表達、保持單向因果與可預測行為、讓事實只有一個權威來源，以及把必要複雜度留在真正的邊界。提醒聚焦可檢查的替代關係，讓 Actor 能判斷並實作。兩步選題、四欄格式與字元額度見[行為規格](SPEC.zh-TW.md)。

## 限制

- Actor 負責判斷提醒、實作與驗證完整交付。
- 每輪最多三則建議或兩次沉默，先到任一上限就停止。可辨識的純測試修改直接略過，不呼叫 Provider、不耗額度。
- Provider 只支援 OpenAI／Codex。只觀察明確的 `apply_patch` 修改，無法觀察沒有提供修改內容的命令列寫檔。
- 已驗證的 Windows 平台上，中斷會停止 Provider 並保留中斷故障紀錄，詳見[驗證紀錄](docs/qualification/README.zh-TW.md)。Codex 仍可能缺少對應的 `PostToolUse` 完成事件；詳見[重現與追蹤](https://github.com/openai/codex/issues/46765)。

## 開始使用

支援平台：**Windows 11 x64**。需要可由 `python` 啟動的 Python 3.10+、Git 工作區、已登入的 Codex CLI，以及受支援的 [Windows 沙箱](https://learn.chatgpt.com/docs/windows/windows-sandbox)。

1. 在 Codex 桌面版的外掛頁，選 **Add → Add Marketplace → Add from a repository**，填入 `https://github.com/shihchengwei-lab/masters-nudge`，按 **Sync**，再安裝並啟用 Masters’ Nudge。
2. 依 Codex 提示，檢查並信任外掛 Hook。
3. 開啟新對話，請 Codex：**「檢查 Masters’ Nudge 是否已就緒，顯示 Provider 模型與思考深度。」**
4. 在自己的 Git 專案交付一項正常的程式修改。修改後，請 Codex：**「顯示 Masters’ Nudge 最近的提醒紀錄。」** 可核對收到的建議與 Actor 後續改動。

Provider 預設模型為 `auto`、思考深度為 `medium`，兩項都可請 Codex 調整。修改設定或更新外掛後，重新開啟 Codex；若提示 Hook 已更新，檢查新命令後重新信任。

手動指令、設定與診斷方式見[詳細說明](docs/DEVELOPMENT.zh-TW.md#手動設定與診斷)。

## 隱私

任務原文、修改、工具結果、可完整放入共同材料額度的已修改檔案，以及檔案來源事實會傳給 OpenAI。Provider 可唯讀 Git 工作區中的未忽略檔案。完整任務起點檔案清單只保存在本機，送出時附本批路徑是否原本存在。

預設紀錄存於使用者目錄的 `.masters-nudge/data/feedback.sqlite3`，設定存於 `.masters-nudge/config.json`。`MASTERS_NUDGE_DATA_DIR` 可覆蓋位置。

## 開發

原始碼是唯一實作來源，外掛副本由建置指令產生：

```powershell
python tools/build_plugin.py --write
python tools/build_plugin.py --check
python -m unittest discover -s tests -v
```

使用、規格與開發文件見[文件索引](docs/README.zh-TW.md)。
