# Element 有／無工具案例：裝置勾選

本頁整理 2026-09-30 至 10-02 六臂研究中 `element-sessions` 的 **A1／B1**，沒有新增模型呼叫。選這組是因為 Actor 模型、深度、CLI、任務及基底相同，且能從第一份修改、原始提醒及後續修改追到採納關係。

## 任務與共同條件

使用者要能勾選多個裝置、看見選取數量、取消選取，並在一次請求中登出全部選取裝置；切換篩選須清空選取，成功登出須刷新，取消驗證須解除載入。完整[任務契約](../../benchmark/sol61-six-arm-20261002/protocol/evaluation/cases/element-sessions/task.md)另有既有介面及測試識別字要求。

| 條件 | A1 | B1 |
|---|---|---|
| Actor | GPT-6.1 Sol medium | GPT-6.1 Sol medium |
| Provider | 無 | GPT-6.1 Sol medium |
| Codex CLI | 0.159.0 | 0.159.0 |
| 起始提交 | `7a33818bd7ec89c21054691afcb6db2fb2631e14` | 相同 |
| 任務提示 SHA-256 | `3b18c0f0c91e930ad7d97ae4ae3586c0369faf7195dddbf8eac5c41cd05ee10a` | 相同 |
| 本輪完整交付 | 通過 | 通過 |
| 反饋／沉默／故障 | 沒有 Provider | 1／1／0；一則已送達 |
| 匿名品味結果 | 兩位評審均選 B1 | 勝出 |

## 差別在哪裡

`FilteredDeviceList` 支援兩種用法：自己管理勾選，或由外部頁面提供勾選清單與更新方法。

A1 把 `selectedDeviceIds`（清單）與 `setSelectedDeviceIds`（更新方法）各自設為可選，再分別找後備來源。以下是最終修改的原文節錄：

```tsx
selectedDeviceIds?: DeviceWithVerification['device_id'][];
setSelectedDeviceIds?: (deviceIds: DeviceWithVerification['device_id'][]) => void;

const selectedDeviceIds = controlledSelectedDeviceIds ?? localSelectedDeviceIds;
const setSelectedDeviceIds = setControlledSelectedDeviceIds ?? setLocalSelectedDeviceIds;
```

只傳清單時，畫面讀外部清單，點擊卻寫本地清單；只傳更新方法時，畫面讀本地，點擊卻交給外部。這兩種不完整組合都能通過 A1 的型別介面。

B1 第一份修改也有同樣的獨立後備來源。Provider 回傳的四欄原文是：

```text
OBSERVED: FilteredDeviceList: ids??local,set??own
WHY: 單邊 prop 可能使選取更新失效
STRUCTURE: selection props 成對或皆省略；同源讀寫→checked/count/signOut
REQUIRED: 選取、計數與批次登出使用同一組 IDs
```

B1 下一份產品修改要求兩者一起存在或一起省略；執行時也用同一個判斷選擇來源。最終修改原文節錄：

```tsx
type Props = DeviceListProps & ({
    selectedDeviceIds: DeviceWithVerification['device_id'][];
    setSelectedDeviceIds: (deviceIds: DeviceWithVerification['device_id'][]) => void;
} | {
    selectedDeviceIds?: never;
    setSelectedDeviceIds?: never;
});

const isControlled = controlledSelectedDeviceIds !== undefined && onSelectionChange !== undefined;
const selectedDeviceIds = isControlled ? controlledSelectedDeviceIds : localSelectedDeviceIds;
const setSelectedDeviceIds = isControlled ? onSelectionChange : setLocalSelectedDeviceIds;
```

這是把同一個選取狀態的讀取與修改責任一起表達，而非事後補同步。後續 Actor 訊息也明述已收緊介面、要求 IDs 與更新函式成對提供。

## 評審判了什麼

兩位 GPT-6 Astra medium 評審看匿名程式，第二次交換 X/Y，均偏好 B1。共同依據是：型別排除半套選取輸入，執行時讀寫也由同一個所有權判斷決定。兩位也認為 A1 的登出 hook 責任分離較好：A1 通知已登出哪些 ID，由頁面清理選取；B1 直接把選取更新函式交給 hook。整體勝負由前面的選取來源約束決定，沒有說 B1 每一處都較好。

實際頁面兩份都成對傳入，完整交付均通過。因此本例呈現的是介面如何排除容易接錯的組合，不是 A1 的現行頁面已出現勾選失效。原始 Actor 紀錄另有需求指定的新 `data-testid` 導致舊快照不一致；本輪固定驗收、執行規則及完整交付判定均通過，不將 Actor 所報的每項公開測試等同正式判分。

## 如何沿原始證據核對

材料都在 repo 的[原始證據包](../../benchmark/sol61-six-arm-20261002/evidence.zip)。用檔案總管開啟，或依 [harness 說明](../../benchmark/sol61-six-arm-20261002/HARNESS.zh-TW.md)解壓後讀取：

| 包內路徑 | 核對內容 |
|---|---|
| `runs/A/element-sessions/A1/final.patch` | 沒工具的最終程式 |
| `runs/B/element-sessions/B1/provider-attempts.json` | 第一則的 `detail.packet` 是採納前修改；`detail.raw_output` 是原始提醒；第二次的材料記錄後續成對修改 |
| `runs/B/element-sessions/B1/final.patch` | 成對型別與共同來源判斷的最終程式 |
| `runs/B/element-sessions/B1/actor-events.jsonl` | 原始行動與「已收緊選取 API」訊息 |
| 兩份 run 的 `launch.json`、`result.json` | 模型、深度、任務、基底、耗時及提醒結果 |
| `evaluation/A/element-sessions/A1/`、`evaluation/B/element-sessions/B1/` | 固定驗收原始日誌 |
| `judges/B/element-sessions/trial-1/A-B/pair.json` | 匿名對應、交換順序、兩張票與完整理由 |

最終 patch SHA-256：A1 為 `7499742cfd483b139b6c0e83b35617d5f45bb7cce092466cbec4540ca9f0cdd8`；B1 為 `f95b677ecfebbfc6d0f7747335d43ce9b8d7bf29c551d933c2e68a0e42de847b`。程式來源與授權見封存評測的[來源說明](../../benchmark/sol61-six-arm-20261002/protocol/evaluation/ATTRIBUTION.md)。

本例是完整研究中的一組可追溯採納案例；工具整體的契約完成、品味配對與花費仍以[七臂完整報告](../../benchmark/sol61-six-arm-20261002/REPORT.zh-TW.md)為準。
