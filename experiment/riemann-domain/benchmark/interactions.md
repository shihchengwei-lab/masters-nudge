# Complete traceable Nudge interactions

> **Scope:** These are the 17 interactions with both a confirmed injection
> receipt and a matching transcript message. They are the traceable subset
> of 19 findings generated after receipt tracking began, and of 102 findings
> across the full experiment. Temporal alignment does not establish exclusive
> causation or mathematical correctness.

Return to the [benchmark report](README.md). The machine-readable source is
[`interaction_annotations.json`](interaction_annotations.json).

## Coding rubric

- **Direction aligned:** The next visible operation directly implements the Nudge's proposed check or workflow change.
- **Engaged and reframed:** The main agent explicitly addresses the Nudge but corrects or reframes its conclusion.
- **Delayed adoption:** The suggestion becomes visible only after intervening work or another Nudge.
- **Ambiguous: related work already in flight:** Related work was already running, so temporal order cannot distinguish influence from concurrency.
- **Not adopted or too late:** The next work does not follow the suggestion, or the Nudge arrives after effective termination.

## Chronological observations

### 1. Ambiguous: related work already in flight

- **Time:** `2026-08-16T00:46:40.596Z`
- **Lens:** `tao`
- **Nudge:** 已列目錄但未讀 handoff 或 audit；先讀狀態文件才能選承重缺口。
- **Next visible response:** Waited for an already-running state-file read, then extracted current state.

### 2. Direction aligned

- **Time:** `2026-08-16T00:48:55.047Z`
- **Lens:** `erdos`
- **Nudge:** 迴圈內 type 目標寫死 HANDOFF.md，其餘四檔實際未被讀取。
- **Next visible response:** Replaced the loop with explicit reads of the four missing audit/state files.

### 3. Not adopted or too late

- **Time:** `2026-08-16T00:54:38.771Z`
- **Lens:** `tao`
- **Nudge:** 尚未讀完本地狀態檔就拉外部論文，沒有已命名的 lemma 或缺口能錨定這次搜尋。
- **Next visible response:** Continued reading the already-selected external paper source.

### 4. Delayed adoption

- **Time:** `2026-08-16T01:04:49.767Z`
- **Lens:** `tao`
- **Nudge:** 「有限K未被排除」是新路線的承重前提；對具體y_m算K的數值界比再寫文件更有資訊。
- **Next visible response:** Updated the handoff first; the requested numerical test began after the following Nudge.

### 5. Direction aligned

- **Time:** `2026-08-16T01:09:10.431Z`
- **Lens:** `tao`
- **Nudge:** 連續三則 ES 均判文獻無界；K≤T^A 要直接構造或數值反駁，再開 ES 無新資訊。
- **Next visible response:** Explicitly stopped expanding literature search and started an AP2 coefficient-cost stress test.

### 6. Direction aligned

- **Time:** `2026-08-16T01:16:04.142Z`
- **Lens:** `erdos`
- **Nudge:** T=16 把 N 加倍，relL2 幾乎不動；先確認殘差是否隨 N→∞ 收斂至零，否則障礙在基底本身。
- **Next visible response:** Ran the same experiment at N=64 and N=256.

### 7. Engaged and reframed

- **Time:** `2026-08-16T01:25:51.404Z`
- **Lens:** `tao`
- **Nudge:** 成本隨距首零點距離惡化的速率是多項式還是指數級？擬合這條曲線即可判定 AP2.5 是否值得證。
- **Next visible response:** Rejected curve fitting as decisive, derived a local polynomial obstruction, and retained the route on narrower grounds.

### 8. Direction aligned

- **Time:** `2026-08-16T01:31:27.639Z`
- **Lens:** `tao`
- **Nudge:** 「全域 one-sided interpolation」仍是缺口標籤，未寫成帶量詞的可證偽命題。
- **Next visible response:** Recast the survivor as a fixed Riesz–Möbius mollifier with explicit parameters and an L2 limit.

### 9. Ambiguous: related work already in flight

- **Time:** `2026-08-16T01:55:25.568Z`
- **Lens:** `tao`
- **Nudge:** 連續排除路線後，存活需求再次停在散文階段；先把 CD 二次形式的界寫成可算的顯式不等式。
- **Next visible response:** Reported that the explicit finite-cutoff form had just been completed; generation and work overlapped.

### 10. Direction aligned

- **Time:** `2026-08-16T02:09:09.910Z`
- **Lens:** `tao`
- **Nudge:** L55 joint cancellation 無機制；先數值驗 block energy 是否真衰減。
- **Next visible response:** Explicitly adopted the stress-test order and computed real-zeta block energies.

### 11. Engaged and reframed

- **Time:** `2026-08-16T02:14:30.531Z`
- **Lens:** `erdos`
- **Nudge:** rate 從 −0.30 降至 −0.01：衰減是多項式非指數，數據否證了指數衰減前提。
- **Next visible response:** Rejected the inference because LB9 required subexponential scale, then changed the diagnostic to dyadic min/median/max.

### 12. Direction aligned

- **Time:** `2026-08-16T02:21:24.712Z`
- **Lens:** `tao`
- **Nudge:** producer 只列排除條件；LB9.2 正下界需對哪些參數 uniform 未定。
- **Next visible response:** Added a quantified uniform coercivity requirement over block vectors and cutoff tails.

### 13. Direction aligned

- **Time:** `2026-08-16T02:30:13.981Z`
- **Lens:** `tao`
- **Nudge:** 多個 producer 連續排除後，共同失敗機制是否結構性？若是，下一個 mean 候選同樣繞不過。
- **Next visible response:** Unified the failures as stationary quotienting, stopped testing normalized means, and pivoted to anchored finite-height obligations.

### 14. Direction aligned

- **Time:** `2026-08-16T02:36:06.525Z`
- **Lens:** `tao`
- **Nudge:** 「合流」本身是一條引理：LB 殘差項與 W13/W14 義務在哪個量詞層級等價，需精確陳述。
- **Next visible response:** Replaced the vague merge with three explicit implications and their witnesses.

### 15. Direction aligned

- **Time:** `2026-08-16T02:45:38.362Z`
- **Lens:** `tao`
- **Nudge:** 三向等價皆經殘差排除即各預設 RH；新義務需有獨立於 RH 的可證內容。
- **Next visible response:** Stopped adding residue-equivalent criteria and moved to an independently testable relative-clock lemma.

### 16. Direction aligned

- **Time:** `2026-08-16T03:14:41.586Z`
- **Lens:** `tao`
- **Nudge:** Goal 標記完成，但 packet 未見嚴格證明、亦未見最強路線排除紀錄與可續接交接文件。
- **Next visible response:** Audited named terminal sections before finalizing and explicitly reported that RH was not proved.

### 17. Not adopted or too late

- **Time:** `2026-08-16T03:15:27.431Z`
- **Lens:** `tao`
- **Nudge:** Checkerboard只擋smooth版；DN若存在非光滑子路徑，排除宣告尚未封閉。
- **Next visible response:** The Goal had effectively terminated; no new research operation followed.
