# Three.js WebGPU Black Hole Saturation Protocol V2

Status: draft preregistration. Unity／URP 的 `PROTOCOL_V1.md` 與既有 manifest
保持凍結；V2 是獨立的 Three.js／WebGPU 實驗，不以 V2 結果回填或改寫 V1。

## 1. 來源與邊界

- 上游：[`dgreenheck/webgpu-black-hole`](https://github.com/dgreenheck/webgpu-black-hole)
- 固定 commit：`cf2fca75a9e774449057cbebe2197129249d96b8`
- 授權：repository 根目錄的 MIT License；`public/cloud.png` 沒有另外列出來源，
  執行前仍須把資產來源檢查結果寫入 manifest。
- 技術：Three.js、TSL（Three.js Shading Language）與 WebGPU。
- 視覺主體：Schwarzschild 黑洞、重力透鏡、吸積盤、程序化星空／星雲、
  Doppler／blackbody 色彩與 bloom。

實驗必須在獨立、乾淨的 workspace 從固定 commit 開始。不得把 Unity harness、
舊候選實作或後見之明答案複製進去，也不得把未完成結果放進 `experiment/`。

## 2. Domain-fit eligibility gate

「適合 Three.js」不是 engine adapter 的宣告。本 protocol 只把這個固定的
`webgpu-black-hole` 工作負載標為 `unconfirmed`，不代表 Three.js
專案普遍適合 Shader domain。

baseline profiler 必須證明主要可控成本位於 TSL／WebGPU shader、raymarch、
render／compute pass 或 GPU resource pipeline，才可把 manifest 改成 `eligible`。
判斷必須引用 source symbol、browser trace 或 GPU timestamp evidence。

若主要瓶頸位於 JavaScript 主執行緒、DOM／Tweakpane、資產載入、網路、build
tool 或與 shader 無關的瀏覽器排程，判定為 `not-eligible`，改用 software domain
或另立混合實驗；不得靠 adapter 詞彙把工作硬歸入 Shader domain。

## 3. 適配層

V2 不修改 Unity／URP contract，也不改寫既有 Persona：

1. `domain=shader` 先原樣保留共同 base prompt、六個 Persona、Unity／URP
   router 與問句契約，不預先加入 Three.js production adapter。
2. Three.js benchmark harness 獨立負責瀏覽器畫質、效能與裝置證據。
3. baseline 與第一輪既有 Shader domain smoke 必須記錄實際錯誤路由、URP
   語意污染或無法表達的證據欄位。
4. 只有可重現失敗指出缺口時，才為 workspace evidence schema、router mapping
   或 prompt overlay 分別新增最小適配；沒有失敗證據便不改 runtime。

因此 V2 manifest 的 `engine_adapter` 在 baseline 前保持 `null`，適配需求由實際
run evidence 決定，不由 protocol 預設。

## 4. Outcome-only Goal

只把下列 Goal 給主 Agent：

> 在固定視覺、動畫、瀏覽器、硬體與量測契約下，交付可重現的 Three.js WebGPU 黑洞 Pareto 前沿，並保留每個候選的假設、變更、原始量測與判定紀錄。

主 Agent 的 Goal 不提 Masters' Nudge、Persona、預期反應或評分帶。

## 5. 宣稱邊界

本實驗不宣稱 Masters' Nudge 改善研究成果、效能、畫質、搜尋效率或 Agent
能力。Masters' Nudge 只是一條同步記錄的工具事件流；報告只能描述：某個問題
何時生成、是否送達，以及主 Agent 後續留下什麼可見反應。

RH 本來就是未解猜想；V2 改用可直接量測但沒有單一已知最佳解的圖形最佳化任務。
這仍不能證明全球最佳解，也不能把時間順序當成因果。

## 6. 固定視覺與動畫契約

baseline 前先固定並雜湊：

- upstream source、lockfile、production build 與所有 shader source；
- viewport、device pixel ratio、tone mapping、color space、bloom 與 exposure；
- cinematic camera path、相機參數、動畫時間序列、seed 與 UI 參數；
- event-horizon silhouette、photon／Einstein ring、雙側透鏡吸積盤、溫度漸層、
  turbulence 動態、星空／星雲與 bloom envelope 的 golden frame sequence；
- 允許的靜態、時序與亮度差異門檻及其 baseline noise 來源。

門檻必須在第一個候選前凍結。若現有程式無法 deterministic replay，先只修 harness；
任何視覺演算法改動都必須另列為候選，不得混入 baseline。

## 7. 效能與相容性契約

manifest 在第一個候選前固定：

- OS、browser build、flags、WebGPU adapter、driver、power mode、解析度；
- warmup、sample window、repetitions、冷／熱啟動規則與背景程序政策；
- CPU frame time、GPU timestamp query（支援時）、FPS p50／p95、dropped frames、
  shader／pipeline compilation、resource-size proxy 與 device-loss 記錄；
- production build hash、每次 run 的 raw samples 與 screenshot／frame hashes。

手機效能與溫度只能由真實裝置量測。desktop viewport 或裝置模擬不能當成手機
熱度證據；沒有真實裝置時，mobile 與 thermal 結論一律標成 `unverified`。

## 8. 搜尋空間與候選

搜尋單位是「有 profiler 證據的 bottleneck hypothesis × 能讓機器少做工作的
mechanism」。同一 cell 的參數調整是 refinement，不得假裝成新機制。

第一個候選前凍結下列 coverage inventory；執行中可以新增發現到 gap ledger，
但不得刪除或改名來提早關閉搜尋：ray integration／step scheduling、raymarch
budget／early exit、gravitational lensing、accretion-disk distance field、blackbody
color／temperature profile、Doppler／redshift、disk edge／radial window、turbulence／
procedural noise、nebula、starfield、bloom／post-processing，以及 fixed-material／
platform specialization。

每筆候選至少包含：

- stable ID、parent frontier、source／contract hash；
- bottleneck family、直接證據與可否證預測；
- mechanism family、預期消失的 GPU／CPU 工作；
- 唯一主要變更、編譯與執行證據；
- raw performance samples、visual／temporal checks、失敗與 device loss；
- accepted、dominated、invalid、infeasible 或 contract-violating 判定；
- 候選前可見計畫及其間的 Nudge event IDs。

候選預算固定為 50 個技術上不同且具資格的 search cells，編號 A01–A50；A00
只代表 baseline，不計入預算。refinement 沒有固定數字上限，也不占候選預算。
duplicate、無證據猜測與只換名稱的變體須拒絕並留在 rejection ledger，不能用來
補足 50 個候選。

## 9. 飽和停止條件

停止規則固定為 `candidate-budget-and-saturation-gates`。未完成 A01–A50 時，
即使暫時沒有新 frontier point 也必須繼續。完成 50 個候選後，只有下列條件同時
成立才可標記 `observed-search-saturation`：

1. profiler 支持的 hypothesis／mechanism coverage map 沒有未走訪 cell；
2. 每個仍被證據支持的 mechanism family 都有至少一個有效量測；
3. 對目前 bottleneck map 完成兩次完整 coverage sweep，沒有新的非 dominated
   frontier point，且差異落在凍結的量測雜訊／信賴區間內；
4. profiler 仍指出同一剩餘瓶頸；
5. 所有剩餘提案都有可稽核理由：duplicate、dominated、infeasible、缺乏證據，
   或違反固定視覺／相容性契約；
6. 每個 accepted frontier point 都完成規定 repetitions 與 clean replay。

若 50 個候選已用完但任何條件不成立，只能標記 `phase-close-unsaturated`。這只表示
在固定 source、工具鏈、硬體、contract 與預先凍結的 coverage map 下觀察到飽和，
不得寫成全球最佳或所有 Three.js／WebGPU 裝置都飽和。

## 10. Nudge 完整紀錄

從主 Agent 第一個 task event 開始，每則 Nudge 分開記錄三個事件：

- `generated`：provider、model、prompt／source fingerprint、時間、finding 或錯誤；
- `delivered`：pending／injected／expired／superseded／failed 與 receipt 時間；
- `main_response`：下一個可見主 Agent 訊息或決策、event range 與內容 hash。

每則 finding 都必須是開放問句並以「？」收束。若輸出不是問句、缺少 generated、
delivered 或 main_response 任一層，該互動不得列入完整 trace；缺口與分母仍須保留。

報告可以列出內容相似、時間先後、主 Agent 是否明確回應，以及後續候選結果；
不得使用「改善、促成、影響、成功率、增益」等因果或效果用語。Nudge trace
不完整時，最佳化量測仍可個別報告，但不能宣稱完成長任務工具觀察。

## 11. 必要產物

開始候選前：

- frozen `run-manifest.json` 與 hash；
- clean source proof、license／asset audit；
- deterministic baseline、golden sequence 與 baseline noise；
- benchmark scripts、candidate schema、coverage map 與 Nudge event schema；
- provider transport／receipt smoke，確認三層事件都能閉環。

run 後：

- 所有候選、refinement、rejection、failure 與 raw evidence；
- Pareto frontier、coverage sweeps 與 saturation 判定；
- 完整 Nudge event stream 及缺口分母；
- 重建步驟、依賴 lockfile、來源與產物 hashes；
- 明確列出的 mobile、thermal、cross-browser、因果與人工視覺未驗證項目。

正式結果使用新的 `evaluation/results/threejs-webgpu-black-hole-<run-id>/`；draft、
半成品或 live workspace 不進產品 repository。
