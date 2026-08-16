# 黎曼猜想研究日誌

## 2026-08-15 — external input resumed: normal-mode audit and causal endpoint

- Derived K0B38.1 exactly. The fourth-order Fermi normal stress factors into the two
  completed one-dimensional theta-mode factors, not a square; individual modes change sign.
- Audited Suzuki's 2025 AIF canonical-chain theorem. It is a genuine all-degree mechanism,
  but the Xi endpoint is exactly `supp F^-1[(Xi-iXi')/(Xi+iXi')] subset [0,infinity)`,
  hence RH-equivalent. Its unconditional L-function application stays at `omega>=1/2`.
- Audited cyclic Polya-frequency theta heat-kernel input. It controls spatial angle, not
  Riemann logarithmic scale plus completion.
- No numerical observation was used as proof. Live routes: nonlocal lattice Green/Rellich
  cancellation or prime/theta causal factorization without division by `E_Xi`.

## 2026-08-15 — KPS van Dantzig/Pick route

- Audited the 2024 peer-reviewed KPS theorem and archived its TeX. Theorem 4.4 is a genuine
  uniform-in-degree engine: a 1-separated Bernstein Pick interpolant of the coefficient
  recurrence generates a Laguerre--Polya characteristic function.
- Corrected the Riemann coefficient bridge directly from Fourier moments:
  `Psi(n)=2n(2n-1)m_(n-1)/m_n`, `varphi_n=Psi(n)/n`.
- Proved uniformly, using the already certified Xi radial score theorem,
  `varphi_n=2E_n[q]` and `Delta varphi_n>0` for every n. This is only the first Bernstein
  condition, not RH.
- Isolated the natural all-order target `varphi_nat(z)=2(2z-1)M(2z-2)/M(2z)`.
- Finite-precision diagnostics in `probe_vandantzig_moment_ratio.py` and
  `probe_vandantzig_pick.py` found no low-order/upper-half-plane counterexample; this is
  candidate selection only, never proof.
- Found sign/factor inconsistencies in the paper's equations (4.15)--(4.18); the general
  theorem remains usable, but its displayed Riemann matching is not imported.

## 2026-08-14：啟動、既有論證稽核與 Li 有限截斷障礙

### 證明標準

- 目標是證明 ζ 的每個非平凡零點都滿足 `Re(ρ)=1/2`。
- 數值結果只用於找反例、測試候選引理與選擇方向，不視為證明。
- 每項主張分為：已證明（附推導）、候選、已否證、未閉合缺口。
- 全程離線；未搜尋或存取網路。

### 已接收的既有結果

`argument.md` 與 `audit.md` 已否證「函數方程及共軛對稱本身推出每個零點位於臨界線」。正確結論僅是零點集合包含四點對稱軌道。這條純對稱路徑已封閉為失敗路徑，但不影響 RH 本身。

### 本輪路徑：Li 型正性

對非零複數 `ρ` 定義

`L_n(ρ)=1-(1-1/ρ)^n`。

考慮離臨界線的對稱四元組

`Q(β,γ)={β±iγ, 1-β±iγ}`，其中 `0<β<1` 且 `β≠1/2`。

其第 n 個 Li 型貢獻為

`q_n(β,γ)=Σ_{ρ∈Q(β,γ)} L_n(ρ)`。

已證明下列有限截斷障礙：對每個固定 `N` 與上述 `β`，存在 `Γ`，使所有 `γ>Γ` 均有 `q_n(β,γ)>0`（`1≤n≤N`）。推導見 `candidate_lemmas.md` 的 L1。

含義：即使前 N 個 Li 型量全部為正，也不能只靠這項有限資料排除一個很高的離線四元組。真正的 Li 判準要求所有 n 的正性；本結果不反駁它，而是排除「固定有限截斷即可完成證明」的策略。

### 本輪數值壓力測試

`experiments/li_quartet_experiment.py` 用 Python 複數算術直接計算 `q_n`，掃描多個 `β,γ,N`，並輸出最小貢獻與其 n。它同時比較漸近主項 `2n²/γ²`。這只是有限精度反例搜尋／公式除錯，不是 RH 的數值驗證。

### 下一步

1. 將 L1 的逐 n 漸近提升成帶顯式常數的誤差界，量化 `Γ(N,β)`。
2. 研究當 n 與 γ 同尺度時 `q_n` 何時轉負；這是 Li 判準偵測離線零點的可能機制。
3. 檢查從 ζ 的整函數階數、零點密度與顯式公式，能否取得排除離線四元組所需的一致 n 控制。
4. 若一致控制只是改寫 RH，明確標成循環缺口並轉往 Weil 正性或 de Branges 型結構。

## 2026-08-14：Li 四元組精確公式與共振定理

### 已證進展

把 `w_a=1-1/(a+iγ)` 寫成極座標後發現，β 與 `1-β` 對應的兩個 w 有相同辯角 θ、互為倒數的模。因而四元組貢獻有精確閉式

`q_n=4-4cosh(nλ)cos(nθ)`。

由此證明：每個固定離線四元組都對無限多個 n 產生負貢獻。對高處零點更可選共振指標 `n≈2πkγ`；只要 `πk|1-2β|>1/2`，充分大 γ 時該貢獻嚴格為負。完整推導見 `candidate_lemmas.md` 的 L3、L4。

### 反例防護

這仍未證明完整 Li 係數為負，因為其餘無限多個零點可能抵消單一四元組。研究焦點已從「四元組是否會轉負」收斂到 L5：「最大模離線零點組能否在合法的正則化和中支配其餘零點」。

### 下一步

1. 以 ξ 的 Hadamard 乘積或 Li 生成函數建立不依賴非法重排的尾界。
2. 對最大模有限相位組使用同時 Diophantine 逼近，構造共同接近相位 0 的子序列。
3. 稽核上述兩步是否只是在重證 Li 判準的已知等價方向；真正缺口仍是無條件證明全部 Li 係數非負。

## 2026-08-14：完成最大模支配尾界

### 已證進展（依賴明列的標準解析前提）

本階段先在 Li 對稱零點和公式與 `N(T)=O(T log T)` 前提下完成 L5；後續已在「Li 解析基礎與粗計數界重建」中把依賴降為由一階整函數直接得到的 `N(T)=O(T^(3/2))`。若有離線零點，最大 `|1-1/ρ|=R>1` 的有限零點組可藉同時相位逼近沿子序列產生 `-MR^n` 主項；其餘部分為 `o(R^n)`，故完整 Li 係數會無限多次為負。

關鍵尾部分割取 `T=e^{cn}`：中段由次大模 `R_2<R` 控制，高尾由每四元組 `O(n²/γ²)` 加上零點計數控制。詳見 `li_dominance_proof.md`。

### 路徑判定

Li 的「離線零點必被偵測」方向已閉合到標準解析前提；剩餘命題是無條件證明全部 Li 係數非負。這正是 RH 的等價核心，不能把等價性本身當成進展。下一輪應嘗試正性核表示並優先找符號反例或邊界項漏洞。

## 2026-08-14：Fourier 核正性路徑的反例稽核

已構造精確反例：`cos z+(1/10)cos 2z` 是正偶測度的 Fourier 變換，但因二次式根小於 -1 而有明確非實零點。再與 Gaussian 卷積，便得到嚴格正、偶、實解析、Schwartz 核，且非實零點不變。

因此「Xi 核看起來正且快速衰減，所以零點全實」已被排除。可行的 kernel 路徑必須提出並驗證更強的無限階結構；有限數值行列式或圖形不足以證明。

## 2026-08-14：Li 解析基礎與粗計數界重建

已從 `H(z)=log ξ(1/(1-z))` 的 Cauchy 係數公式推導 Li 導數生成函數，再由 ξ 的對稱 Hadamard 對數導數及 `a_(1-ρ)=a_ρ^{-1}` 推得正確的對稱零點和。這也定位了逐根展開時容易混淆正負冪的原因。

最大模支配不必依賴精確零點計數：ξ 為一階整函數經 Jensen 給出 `N(T)=O(T^(3/2))` 已足夠。把切割高度取為 `T=e^{cn}` 並令 `e^(3c/2)R_2<R`，中段仍為 `o(R^n)`；dyadic 高尾是 `O(n²T^-1/2)`。詳見 `analytic_foundations.md` 與修訂後的 `li_dominance_proof.md`。

## 2026-08-14：Li 收斂半徑／次指數判準

由 `H'(z)=Σλ_nz^(n-1)` 及零點映射 `a_ρ=1-1/ρ`，已證 RH 等價於 `limsup|λ_n|^(1/n)≤1`。離線零點的右半反射會在單位圓內造成 H' 的真極點，故不可能被係數估計隱藏。

這提供不要求 Li 逐項正性的替代目標：對每個 ε 證明 `|λ_n|≤C_ε(1+ε)^n`。但 ξ 的一階整函數性只控制 ξ，不會自動移除 log ξ 的零點極點；Euler 乘積在 z 平面只覆蓋 `|z-1/2|<1/2`。這兩個看似直接的捷徑均已標記為循環／區域不足。

## 2026-08-14：Li 算術／Gamma 二項分解

已由 Leibniz 公式與 polygamma 特值推導 λ_n 的精確有限分解，ζ 部分以 `d log[(s-1)ζ(s)]/ds=Ση_j(s-1)^j` 表示。`experiments/compute_li_from_stieltjes.py` 以 Stieltjes 常數的形式冪級數遞推離線計算 η，僅用於公式交叉檢查與量測消去。

證明障礙是整個二項變換的均勻消去。Gamma 與 η 部分分開取絕對值會產生過大的指數界；若用 ζ 正則對數的無零解析圓盤控制 η，則又把未知零點位置偷渡進假設。

## 2026-08-14：Archimedean 正性與 prime–Laguerre 邊界障礙

Gamma 的 ζ(k) 二項和已精確重寫為奇數 m 上的逐項非負級數。只取 `m≤n` 即得 Archimedean 部分下界

`(n/2)[log(n+1)-1-γ-log(4π)]+1/2`，

故其充分大時嚴格為正。Li 正性的剩餘符號風險因此集中在 η 二項變換 `E_n`。

嘗試由 Euler 乘積把 E_n 寫成 prime–Laguerre 和時，發現 z 展開中心恰位於 Euler 收斂圓盤邊界；`1/z` 極點與質數和發散必須共同正則化。未指定截斷補償便逐項讀係數是非法步驟，已記入 D4。

## 2026-08-14：Archimedean 主階與單側 η 判準

把奇數 m 級數在 `m≤n`、`m>n` 分割，利用 Taylor 餘項控制高尾，已證 `A_n=(n/2)log n+O(n)`。結合最大模負指數子序列，得到新等價式：RH 當且僅當 η 二項變換 `E_n` 的負部 n 次根 limsup 不超過 1。

所以算術攻擊不必證 E_n 或 λ_n 逐項正；只須排除 E_n 的負向指數爆炸。當前最精確未閉合命題為：對每個 ε>0 證明 `E_n≥-C_ε(1+ε)^n`，且證明不得以未知無零區域作前提。

## 2026-08-14：η 完全單調性候選的初步壓力測試

前 20 個 η 係數嚴格交錯，因而檢查 `h=((s-1)ζ)'/((s-1)ζ)` 在 `(1,∞)` 是否完全單調。其導數符號等價於 von Mangoldt 對數矩不超過極點主項的整族不等式，並非 Euler 係數正性自動給出。

40 位精度、五個 s 點、至三階的離線篩查未找到反例；更高階三次超時。此結果只保留 E1 為候選，不升格為引理。下一步應先判定完全單調矩結構是否理論上足以推出 D6 的單側二項界。

隨後已完成該抽象判定：`h_a(x)=1/(a+x)` 對 x>0 完全單調，但當 `a<1/2` 時，其 η 型二項變換 `1-(1-1/a)^n` 在偶數 n 負向指數爆炸。因此 E1 即使為真也不足以推 RH。要排除此反例所需的半平面解析性，對 ζ 恰會偷渡欲證的無零區域；此方向已降級。

最後 E1 本身亦被解析否證：h 的唯一 Laplace 測度是 Lebesgue 測度減去質數冪位置、權重 `Λ(m)/m` 的原子，故含負原子；Bernstein 定理與 Laplace 唯一性排除完全單調。低階數值全正只是有限暫態，已停止擴樣。

## 2026-08-14：Abel–prime–Laguerre 正則化

將展開點移至 `s=1+δ` 後，Euler 級數可逐項微分；有限二項變換精確產生 associated Laguerre 多項式。再以 `δ↓0` 取 Abel 極限，得到 E_n 的合法 prime–Laguerre 表示。

這修補了 D4 的收斂缺口，也暴露新的均勻性核心：對固定 n 極限存在，但 RH 所需的是 n 增大時的單側次指數界；極點補償與 prime 和各自發散，不能分別取絕對值。候選 D8 正是此聯合極限估計。

## 2026-08-14：Chebyshev–Laguerre 核與 1/2 臨界響應

D7 已經 Stieltjes 分部積分改寫為 `A(x)=x-ψ(x)` 的 Laguerre 核投影。對模型誤差 `A=x^θ`，生成函數可精確算出響應

`θ+(1-θ)[-θ/(1-θ)]^(n+1)`。

這嚴格顯示 θ=1/2 是次指數／指數負振盪的分界。它同時排除兩種捷徑：先證 `ψ(x)-x=O_ε(x^(1/2+ε))` 已等價完成 RH；對核取絕對值又會破壞恰好需要的 Laguerre 消去。真正缺口是直接控制帶符號投影，而非普通點態大小。

## 2026-08-14：Chebyshev 加權均方等價判準

以 Cauchy–Schwarz 對 Mellin 積分作解析延拓，已證任意固定 p>5 時，`∫|ψ-x|²/[x²(log x)^p]dx<∞` 等價於 RH。進一步 dyadic 分割顯示，均方界 `∫_2^X|ψ-x|²dx=O(X²log^B X)`、B<5 就足以完成證明；RH 的標準點態後果給 B=4。

這將 D8 轉成正定均方目標，避免 Laguerre 符號，但沒有降低臨界難度：任何 β>1/2 的零點都會破壞 X² 尺度。離線有限加權能量只用來檢查程式與區塊尺度，不可用來聲稱積分收斂。

均方積分已進一步完全離散化為 `Σ(ψ(k)-k-1/2)²+(N-1)/12`。展開是 `Λ(m)-1` 在 Gram 核 `N-max(m,n)` 下的二次型，所缺的是 off-diagonal 質數相關消去。僅有 PNT 的 `ψ(k)-k=o(k)` 不足：抽象 `k^θ`、`1/2<θ<1` 已提供嚴格尺度反例。

藉每單位區間上權重的單調可比性，M1 也已成為純離散級數判準：對任意 p>5，RH 等價於 `Σ[(ψ(k)-k-1/2)²+1/12]/[k²(log k)^p]` 收斂。這是可稽核的算術目標，但目前沒有收斂證明。

PNT 障礙反例已強化為非負權重：`a_n=1-[n^θ-(n-1)^θ]` 在 `1/2<θ<1` 時非負且部分和漸近 N，但中心偏差為 `-N^θ`，使平方總和超過 N² 尺度。因此「von Mangoldt 非負 + 一階 PNT」在邏輯上不足，必須使用其質數冪支撐或二階相關。

M4 二次型的對角已用 `Λ²≤(log N)Λ` 與 Chebyshev 界控制為 `O(N²log N)`；它不是瓶頸。off-diagonal 已精確改寫成位移相關 `C_h(Y)` 的雙重和。證明所需的是跨 h 的總體正向控制，不能把每個相關絕對值粗估後相加。

同一二次型亦已寫成 Fourier 積分 `∫|P_N(t)|²/|1-e^{it}|²dt`。普通 Parseval 控制未加權能量，但分母在零頻像 `t²`；PNT 只控制 t=0 單點，無法限制鄰近頻帶。下一步若走大型篩／指數和路徑，必須直接取得此低頻局部 L² 控制。

## 2026-08-14：第一輪續研——dyadic 區間方差分解

為避免直接對全部位移相關作不透明估計，將每個前綴 `[1,k]` 作 canonical binary decomposition。由 Cauchy–Schwarz 與每個長度 H 區塊至多被 H 個前綴使用，得到 M8.1：前綴平方總和受各 dyadic 尺度的對齊區間方差控制。

這給出明確充分條件：若所有 dyadic `H<N` 一致有 `V(N,H)=O(Nlog^βN)`、`β<4`，則 M2 推出 RH。稽核也顯示這不是現成突破：在 `H=N/2` 時，方差只有兩項，所需界已強迫長區間誤差達平方根尺度；PNT 的 `o(N)` 遠遠不足。因此可行的新工作必須在同一論證中跨越短尺度平均與大尺度端點，不能只引用短區間平均直覺。

新增 `experiments/dyadic_prime_variance.py`，離線計算有限 N 的 `V(N,H)`、M8 上界與主導尺度。用途僅為核對組合不等式、找出有限樣本中的困難尺度與測試候選常數；任何看似穩定的比率都不視為漸近證明。

數值到 `N=2^19` 時，M8 上界逐列覆蓋真實前綴能量，但相當寬鬆；主導 H 多次等於 `N/2`。完整節錄與限制見 `experiments/results_dyadic_variance_2026-08-14.md`。

另以 M9 封閉「只證所有短 dyadic 區間的理想平均方差，再靠端點 PNT 補足」的捷徑：構造先取常數 c、後取 -c 的零總和序列，可令所有 `H≤H_0` 的 V 不超過 N，卻使前綴能量約為 `N³/(12H_0)`。只要 `H_0=o(N)`，仍超出目標尺度。下一輪若續走此線，必須利用 `Λ` 的質數冪支撐取得真正的跨尺度耦合，而不是再強化短尺度有限實驗。

## 2026-08-14：第二輪——受約束分數部分函數與 Möbius 近似

從頭推導 `R_θ(x)={θ/x}` 的 Mellin 公式，並證明一個不依賴完整外部等價定理的充分判準：若係數滿足 `Σc_jθ_j=0` 的有限組合在 L²(0,1) 逼近 1，則任何 `Re(ρ)>1/2` 的 ζ 零點都會與有界 Mellin 評值泛函矛盾；函數方程遂推出 RH。

對最自然的 Möbius 組合 `g_N`，利用 `Σμ(n)floor(y/n)=1` 得到精確誤差分解 NB3.4。其第一個必要條件是 `sqrt(N)Σ_(n≤N)μ(n)/n→0`，而非僅有 PNT 型的調和部分和趨零。NB5 再證首個尾區間正是 `M(m)-M(N)+mA_N` 的加權平方；因此單端點 Möbius 消去仍不足。

離線計算到 `N=2^20`。NB3 下界劇烈振盪；NB5 首尾區間下界在樣本中約 0.013–0.031，未見單調下降。這只標示自然近似器的風險，不構成極限判定。結果與限制見 `experiments/results_mobius_nyman_2026-08-14.md`。

進一步觀察到受約束基底 `e_n` 在 `m=floor(1/x)` 上恰等於 `(m mod n)/n`，所以整個 L² 問題精確等距於權重 `1/[m(m+1)]` 的離散序列空間。由週期分組得到有限 digamma Gram 公式 NB6.3，從而能計算真正的無限 L² 有限維最佳距離，而非截斷積分。

到 `N=64`，最佳 `d_N²` 由 0.066 降至 0.0114，且 `d_N²log N` 約落在 0.046–0.050；原始 Möbius 與簡單 log-taper 係數明顯較差。這只提出 `1/log N` 的候選尺度。若能解析證明該尺度即已完成 RH，因此數值擬合沒有填補缺口。詳見 `experiments/results_nyman_gram_2026-08-14.md`。

NB8 將 Gram 結構再化成差分恒等式 `Δe_n=1/n-1_(n|m)`。它證明基底線性獨立，並證 `a_n=-μ(n)` 是在 `m≤N` 精確解整除方程的唯一係數；NB3 的 `A_N` 漂移正是這個局部精確解無法同時調整的常數差分。故後續若優化係數，必須量化「局部整除殘差換長尾改善」的全局變分，而不能只對 Möbius 係數加一個未證有效的平滑截斷。

NB9 用單一 `e_N` 補正 C，構造出在前 N-1 個離散點完全等於 1 的顯式插值器。它的誤差支撐縮到 `x≤1/N`，但補正係數為 `NA_(N-1)`。完整 Gram 計算顯示樣本誤差仍約 0.035–0.041，沒有隨支撐測度直接縮小；這不是極限反例，卻嚴格提醒後續證明必須同時控制振幅。

NB10 進一步把這個插值器在 `N≤m<2N` 的誤差精確寫為 `-[M(m)-M(N-1)]-NA_(N-1)`。端點修正只把 NB5 的線性漂移換成固定偏移，沒有移除長尺度 Mertens 均方核心。

## 2026-08-14：第三輪——Gram 變分、mollifier 等價與矩陣捷徑反例

以 `x=e^{-u}` 對 NB1 作 Mellin–Plancherel，得到 NB11.1：有限維距離恰是 `1+ζ(s)P_a(s)` 在臨界線、權重 `1/|s|²` 下的 L² 誤差。這確認「直接證 Gram 最佳距離趨零」與構造足夠強的 ζ mollifier 是同一核心；若先使用 `1/ζ` 在右半臨界帶解析，論證循環。

接著檢查 Gram 正元素是否帶來一般矩陣捷徑。NB12 以精確有理截斷及 `1/(M+1)` 尾界證明：索引 `{2,3,4}` 已不對角占優；二階非主子式 `G_(2,3)G_(3,4)-G_(2,4)G_(3,3)` 嚴格為負，故亦非全正矩陣。驗證器與輸出見 `experiments/verify_nyman_gram_counterexamples.py`、`experiments/results_nyman_gram_counterexamples_2026-08-14.md`。

因此，從「G 正定且元素正」直接推可控逆矩陣符號或條件數的路徑已封閉。尚可行的 NB 路徑只剩利用整除差分的特定算術結構，或直接證明 mollifier 均方；兩者目前仍承載 Mertens 長尺度消去。

## 2026-08-14：第四輪——Xi 核、TP₂ 反例與 Jensen 偶矩

K1 的 Gaussian 混合反例可取 `σ>2`。log-sum-exp 二階導數等於 `-1/σ²+Var_x(A)/σ⁴`，而位移落在 `[-2,2]` 使變異數至多 4；故反例核嚴格 log-concave，平移核 TP₂，但 Fourier 變換仍有原來的非實零點。這嚴格封閉「證 Xi 核 log-concave／TP₂ 即推出 RH」的方向。

真正與零點對應的全正性可移到 `G(w)=Xi(i√w)` 的偶矩係數。J1 證明所有階 Jensen hyperbolicity 足以推出 RH；J2 把 shifted degree 2 精確化為 `M_k²/(M_(k-1)M_(k+1))≥(2k-1)/(2k+1)`。一般 moment 的 Cauchy–Schwarz 方向相反，不能自動給此定量界。

J4 找到可解析的充分條件：若 `q(u)=-Φ'(u)/(uΦ(u))` 非遞減，兩次分部積分與 Chebyshev 協方差即可一次證明全部 degree-2 Turán 不等式。J6 再以 theta 各項與 `n=1` 支配的顯式尾界，證明 `q'(u)>0` 對所有 `u≥1`；未證區域縮到 `0<u<1`。

J7 又把緊區間問題歸約為 `(log Φ)'''≤0`：若 `S=(logΦ)'-u(logΦ)''`，則 `S(0)=0` 且 `S'=-u(logΦ)'''`。這是下一個可做解析／區間證明的單一符號命題。

有限計算在 `0≤u≤2` 未見曲率或 q' 反例，偶矩至 k=18、Jensen degree≤6、shift≤10 亦全通過。這些只做選路；完整輸出與限制見 `experiments/results_xi_kernel_jensen_2026-08-14.md`。

## 2026-08-14：第五輪——J7 區間證書與 degree 3 障礙

建立 `experiments/verify_xi_score_interval.py`。第一版直接組合 Φ 導數時因區間相依膨脹而正確失敗；改以第一 theta 項正規化，並加入 Machin 有理 π 夾界、70 位 Decimal 向外擴張、`n≥5` 的解析導數 majorant 與自適應二分後，嚴格通過整個 `0<u<1`。最弱三階上界仍為 -0.01566。結合 J6，J5 全域成立，故 J4 已證明全部 shifted degree-2 Jensen/Turán 不等式。證書輸出見 `experiments/results_xi_score_interval_2026-08-14.md`。

接著推導 degree-3 判別式 J8。若 `U=γ_(n+1)²/(γ_nγ_(n+2))`、`V=γ_(n+2)²/(γ_(n+1)γ_(n+3))`，所需恰為
`3U²V²-4U²V-4UV²+6UV-1≥0`。J5 只給 U,V≥1；序列 `(1,1,1,1/2)` 已精確證明這不足。故 degree 2 的 score 方法不能裸歸納到 degree 3，下一步必須控制相鄰 Turán 比率的失衡或建立真正的三重協方差不等式。

J10 又以 `f_ε=e^(-u²-εu⁶)` 封閉更強的捷徑。其 score `2+6εu⁴` 嚴格遞增，但 exact Fraction 的 Gaussian moment 展開給 degree-3 discriminant 首項 `-(9/16384)ε²`，故充分小 ε 時仍有非實根。驗證器見 `experiments/verify_score_not_cubic.py`。

最後 J11 將 Xi 的 degree-3 條件改寫為相鄰協方差。若 `C_k=Cov_(ν_k)(u²,q)/(2k+1)=1-1/U_k`，則所需恰為
`(C_k-C_(k+1))²≤C_kC_(k+1)[2(C_k+C_(k+1))-C_kC_(k+1)]`。這是比 q 單調更精確、但尚未閉合的下一目標。

## 2026-08-14：第六輪——J11 協方差遞推與大 k 掃描

J12 證明一個較易攻擊的充分條件：若 `0<C_k≤1/12` 且
`C_k(1-4C_k)≤C_(k+1)≤C_k`，則 J11 的 cubic 判別式必非負。證明只需寫 `C_(k+1)=C_k(1-δ)`，用 `δ≤4C_k` 對 J11 兩側作單側估計。

新增對數尺度 Laplace quadrature，避免高偶矩上溢，到 k=200 未見 C 單調或 J12 遞推失敗；最大 J11 左右比約 0.108，且隨 k 下降。形式 saddle `k≈u_kπe^(2u_k)` 給候選主項 `C_k≈(2u_k-1)/[k(2u_k+1)]`，解釋為何相對下降與 C 同為 `1/k` 級。這只是選路，結果見 `experiments/results_xi_j11_scan_2026-08-14.md`。

J10 同時顯示，`q=2+6εu⁴` 的所有導數皆非負卻仍可有負 cubic discriminant。因此一般 q 的凸性或有限／全部導數符號都不能推出 J12；必須證 Xi 特有的協方差定量遞推，或對 saddle 展開給一致誤差。

J14 發現 theta 項的精確位移 `T_n(u)=n^(-1/2)T_1(u+log n)`。在 transformed 積分以 `V=log k` 分割後，低段由 `(1-log n/v)^(2k)` 給 `exp[-2klog2/log k]`，高段由 double-exponential tail 控制。由此嚴格證明全部 `n≥2` moments 相對 n=1 比任意 k 負冪更快衰減。大 k 的 J12 因此只剩第一 theta 項的 saddle 差分估計，不再需要同時處理無限 theta 和。

## 2026-08-14：第七輪——第一 theta 項的 saddle 幾何

對 `H_k(u)=2klog u+log T_1(u)` 完全微分後，J15 已證 `H_k''<0`，故每個 k 有唯一 saddle `α_k`。saddle 方程給
`k/α_k+9/4<πe^(2α_k)<k/α_k+13/4`，曲率則夾在
`2k/α_k²+4k/α_k` 與該量加 21 之間；三、四階導數亦得到顯式界。這使大 k Laplace 展開具可行的局部尺度，但尚未產生足夠精細的相鄰 k 差分餘項。

擴充 `experiments/scan_xi_j11.py` 後，單獨 `T_1` 的數值顯示主項
`(2α_k-1)/[k(2α_k+1)]` 從下逼近 `C_k`，且 `k` 乘相對誤差由 2.15（k=20）降至 1.55（k=199），支持首修正 `3/(2k)`。小 k 主項可為負，且 J12 餘裕是 `k^-2` 級；所以這只決定下一個解析計算的精度要求，不是證明。

J17 將第一 theta 項的 J12 完全改寫成自然 exponential family 的 cumulant 走廊。若 `a(t)=log∫u^(2t)T_1(u)du`，則其二階差分是 `log u` 方差的三角核平均，相鄰差則是第三累積量的雙重平均；J12 的上下遞推因而成為 J17.5–J17.6 的顯式界。這比未結構化 Laplace 相對誤差更貼近真正需要控制的量。

同時 J18 排除直接套全域 Brascamp–Lieb 的捷徑：在 `x=log u` 下，`log T_1(e^x)+x` 於極左尾是局部凸而非凹，因 `L'(0)>0`。仍可行的版本必須切分左尾，再對 saddle 鄰域作局部強凸估計，並把尾部對方差與第三累積量的影響顯式控制。

## 2026-08-14：第八輪——左尾隔離

J19 取固定 `δ=10^-2`，以 `π>157/50` 證 `0<L'(0)<1/20`，再由 `L''<-12` 推得 `u≥δ` 時 log-u 負勢能曲率至少 `19/10000`。所以 J18 的非凹區只存在於可切除的極小左尾，主區域確實可使用局部強凸工具。

左尾不只質量，連 `|logu|^m`、m≤3 的 raw moments 都得到 J19.6 的封閉上界。粗略數值顯示 t=20 時質量上界已低於 `10^-13`、t=50 低於 `10^-133`；這只是已證公式的量級展示。尚須對主 saddle 區域取得遠強於全域常數 `19/10000` 的隨 t 曲率／cumulant enclosure。

J20 改以 x=logu 的真正 mode 工作，證明其唯一性、位置與曲率夾界，並得到精確敏感度 `x_t'=2/Λ_t`、`Λ_t'=-2B_3/Λ_t`。J21 再由局部 Gaussian 積分推得候選方差修正 `Λ^-1+B_4/(2Λ³)+B_3²/Λ⁴`。把它代入 C_k 後，k² 乘相對誤差在 k=50,100,199 為 0.768、0.730、0.719，強烈指向下一個餘項階數；但尚無一致 Taylor remainder，因此明確標為未證候選。

J21 的手算導數已由 `verify_t1_log_derivatives.py` 以 Fraction 多項式清分母精確核對，L''、L'''、L'''' 三個 residual 全為零。J22 進一步把所有高階 u 導數寫成 z=3/(2r)<1/2 的收斂級數，給出到七階的顯式 majorant。J23 則分 `[10^-2,1/4]` 與 `[1/4,∞)` 證明 `F'''<0`，所以主區域曲率嚴格遞增。這些結果準備了非對稱 Laplace tail 的證明材料，但尚未把 remainder 積分完成。

J24 已選定 `w_t=logt/sqrtΛ_t`。利用曲率遞增與 J22 majorant，證明充分大 t 時 window 曲率至少為 mode 的一半；右尾與左尾分別得到 `exp[-(logt)²/2]`、`exp[-(logt)²/4]` 因子。故尾部不再阻礙任意固定階展開，剩餘工作是六階局部 Gaussian 交叉項的顯式 enclosure 與可計算起始門檻。

## 2026-08-14：第九輪——六階 Gaussian 代數

J25 已用 exact `Fraction` 多項式運算完成 normalization、mean、raw second moment 與 variance 的全部 weight≤4 交叉項。除 J21 的
`1/Λ+B_4/(2Λ³)+B_3²/Λ⁴` 外，下一階完整 variance 修正為
`B_6/(8Λ⁴)+(2/3)B_4²/Λ⁵+(25/24)B_3B_5/Λ⁵+(109/24)B_3²B_4/Λ⁶+(25/8)B_3⁴/Λ⁷`。

同時建立局部截斷參數 `theta` 與七階 Taylor 參數 `rho`；在兩者不超過 1/2 時，指數 weight 截斷逐點誤差至多 `88theta^5+5rho`。尚待把它與 Gaussian window 尾、J24 外尾、J19 左尾共同正規化，並算出顯式起始門檻。另明確記錄：此工作即使完成也只處理 degree 3；從 degree 3 到所有 Jensen degree 尚缺獨立的全階引理。

J26 進一步把 J24/J25 的局部「充分大」換成粗門檻 `t≥10^24`。證明只用 `2<log10<12/5`、J20 mode 夾界、J22 Stirling 導數和及整數端點比較；驗證器不使用浮點。此門檻尚未包含 normalization 後的 variance／third-cumulant corridor，且太大而不適合有限 k 區間證書，因此只算局部技術進展，不算 degree 3 完成。

J27 補上兩類顯式尾矩界：一是 weight≤4 Gaussian 多項式從 `[-logt,logt]` 延伸至整線的誤差，二是真密度在 J24 window 外、但仍位於 `u≥10^-2` 主區域的左右 0 至 3 階 mode-centered moments。左尾用切線後可逐項積分出明确多項式乘 `e^[-(logt)^2/4]`；右尾與 Gaussian truncation 有更強的 `e^[-(logt)^2/2]`。仍未做的是共同 normalization 與 central cumulant 的誤差傳播。

J28 以一般 ratio perturbation 恒等式完成上述共同 normalization：從四個 raw moment errors `epsilon_0,...,epsilon_3` 明確算出 variance 與第三 cumulant 的 enclosure 半徑。這一步不假設第三累積量符號。極左尾仍須依 J19.6 作 mixture perturbation；之後的實質符號缺口是中心六階多項式經 J17 triangular averages 是否落入 J17.5–J17.6，而不是尾誤差是否夠小。

J29 再把 J19 的 `u≤10^-2` 部分視為 full law 中的極小 mixture，將其 log raw moments 明確轉成 mode-standardized 0 至 3 階 moments，並以差平方／差立方恒等式傳到 variance 與第三 cumulant。至此 J24 指定的六階局部 enclosure 各類誤差已有完整組合公式；尚未證的是中心函數經 J17 triangular kernels 後的 corridor 符號，以及可實用的低門檻。

J30 改用 bookkeeping 參數的五階 Taylor–Bell 公式後，以固定 Gaussian moments 積分 remainder，消除了 window supremum 的高次 log 損失。結合 `B_3≤-(2t+1)`、六階 exact cumulant 分子及 J27–J29 errors，已解析證得 `κ_(3,t)(logu)<0` 對所有 `t≥10^30`；端點比較全用 Fraction。這使 J17.4 的相鄰 `D` 差為負，但尚未控制其絕對值到 J17.6 下界，因此仍不是 J12 證明。

J31 由 mode 方程保留 `β` 尺度，將上述符號加強成 `|κ_3|<1/(64t²)`，並由同一 raw-moment enclosure 證 `Var(logu)<1/(40t)`。代入 J17 的三角核後，第一 theta 項對 `k≥10^30+2` 已完整通過 J17.5–J17.6，故 J12 成立。這是 degree 3 大-k 主項定理；尚須以顯式差分界把 J14 高 theta 項加回，且有限段證書門檻仍需大幅降低。

J32 從 J14.3 算出完整 theta-tail 的粗顯式界 `R_k/A_k≤2k^-100` (`k≥10^30`)。其 `log(1+R_k/A_k)` 對 D 與相鄰 D 差的擾動分別至多 `16k^-100`、`32k^-100`，遠小於 J31 的 `1/k`、`1/k²` margins。故完整 Xi 核對所有 `k≥10^30+2` 已證 J12；degree 3 剩餘有限段仍無可實用證書，且這不處理 degree 4 以上。

J33 發現舊門檻的主要損失是以 `t(logt)^j` 估 mode 導數。利用 `r≈t/β` 後，`|B_j|≤2C_jtβ^(j-1)`，在 window 內亦只需常數 4。新的 Fraction audit 在 `t=10^10` 給 cumulant approximation 相對誤差 0.012128、standardized variance 上界 1.000000073；由此證 `|κ_3|<1/(50t²)`、`Var<3/(100t)`。連同重新核對的 J14 tail，完整 Xi 的 J12 接點降為 `k≥10^10+2`，但前段仍過大，尚不能宣告全部 cubic 完成。

J34 注意到 J12 只需 polynomially small tail，遂將 Gaussian window 改成 `ell=sqrt(8logt)`。左／右尾仍有 `t^-2,t^-4`，但端點 cubic perturbation 顯著縮小。Exact audit 在 `t=10^8` 給 cumulant error ratio 0.185718、standardized variance 1.0000062，足以證 `|κ_3|<1/(32t²)`、`Var<1/(25t)`；完整 Xi 的 J12 接點再降至 `k≥10^8+2`。直接枚舉剩餘前段仍不可行。

J35 將七階 derivative remainder 也換成 mode-scale `M_7≤4C_7tβ^6`，並取 `ell=sqrt(6logt)`。在 `t=10^7` 的 exact audit 中 cumulant error／主項為 0.442381、standardized variance 1.0000534，仍足以證 `|κ_3|<1/(25t²)`、`Var<1/(20t)`。完整 Xi 的 J12 接點降到 `k≥10^7+2`；現有 absolute Bell 六階法已接近符號餘裕極限。

J36 改為符號敏感的 exact cumulant audit。因大 t 時 `A_3,...,A_6` 全負，64 個非主 monomials 中真正為正者合計只占主負項 0.000365；local/tail error 為 0.423493，仍保留嚴格負號。由此在 `t≥10^6` 證 `|κ_3|<1/(16t²)`、`Var<1/(17t)`，完整 Xi 的 J12 接點降為 `k≥10^6+2`。剩餘有限段仍須 rigorous block certificate。

J37 對下一階段作有限精度選參：在真 mode 上，`ell=sqrt(6logt)` 的 exponent bound 從 t=10³ 的約 3.08 降到 10⁶ 的約 0.33，六階中心 cumulant 相對主項則快速趨近 1。這支持先對 `[10^4,10^6]` 建 logarithmic continuous-t interval blocks；數值只決定分塊策略，不構成任何 J12 證明。

J38 已把上述構想做成 directed continuous-t certificate。694 個 1% blocks 覆蓋 `[10^4,10^7]`，每塊獨立夾 mode、Λ、B3–B7、signed center、Bell/Taylor remainder、tails 與 normalization。全區間得到 `t²|κ_3|<0.037722`、`tVar<0.064472` 且 κ3<0；最弱 block 是 `[10000,10100]`。與 J35 及重新核對的 J14 tail 接合後，完整 Xi 的 J12 門檻降至 `k≥10002`。degree 3 只剩前 10001 個 shifts，尚未做 rigorous moment certificate。

J39 將 A6 視為未知符號，所有含 A6 的中心 monomials都作最壞正估計；在 `[3800,4000]` 使用 0.1% blocks 後，836 個 continuous blocks 全通過。全域有 `t²|κ_3|<0.044060`、`tVar<0.071791`，與 `k^-20` theta-tail transfer 接合後，完整 Xi 的 J12 門檻降為 `k≥3802`。第一 block error ratio 0.987944，顯示六階 Bell-5 方法已到極限。

J40 隨即完成 weight-5 exact Gaussian algebra：加入 A7 後，第三 cumulant 新增七個明確 monomials，驗證器以 Fraction 生成並重驗既有 weight 1/3 係數。尚待 Bell-6 與 M8 enclosure；完成前 degree 3 仍缺 k≤3801。

J41 完成 weight-5/Bell-6/M8 continuous certificate。八階 J22 constant 以 Eulerian identity exact 重建；A6/A7 未假定符號。以 `sqrt(8logt)` 覆蓋 `[2600,2720]`、再接原 blocks，共 334 塊，得到 `t²|κ_3|<0.046443`、`tVar<0.075113` 且 κ3<0。與後續定理及 k^-20 theta tail 接合後，完整 Xi 的 J12 門檻降為 `k≥2601`。

J42 已以 exact algebra 加入 A8、A9，列出 15 個 weight-7 cumulant monomials，並驗證偶 weight 全消失。下一步所需 Bell-8/M10 尚未實作；degree 3 仍缺 k≤2600。

J43 完成 weight-7/Bell-8/M10 continuous certificate。`E_9,E_10` 由 Eulerian recurrence exact 重建；A6--A9 全允許未知符號。272 個 0.1% blocks 嚴格覆蓋 `[1858,2600]`，最弱 block `[1858,1860]` 的 error/negative-center 為 0.941955，且全域有 `t²|κ_3|<0.049740<1/20`、`tVar<0.078523<79/1000`。更新 J32 的有理 theta-tail transfer 後，完整 Xi 的 J12 門檻降為 `k≥1859`；degree-3 尚缺 `k≤1858`，且 degree 4+ 仍未處理。此證書以 Bell-8/M10 絕對餘項直接判定，未假設高階項自然變小。

J44 exact 推出 A3--A11 的 30 個 weight-9 cumulant monomials，並再次驗證偶 weight 全消失。J45 以直接 directed `F''<=-Lambda/2` 取代粗 `M3 w` gate，再用 Bell-10/M12 封閉餘項。84 個 adaptive blocks 覆蓋 `[937,1858]`；最弱 error ratio 0.995057，全域有 `t²|κ_3|<0.059513<3/50`、`tVar<0.086636<87/1000`。以 `k^-19` theta-tail 有理 transfer 接合後，完整 Xi 的 J12 門檻降為 `k≥938`，degree-3 尚缺 `k≤937`。最低 block 餘裕僅 0.5%，數值只用於選 blocks，結論來自 directed enclosure。

J46--J51 將 exact saddle hierarchy 推至 weight-15/Bell-16/M18。weight 11/13/15 新層各有 56/101/176 monomials；directed blocks 依次覆蓋 `[800,937]`、`[744,800]`、`[726,744]`。J51 給 `t²|κ_3|<0.064095<13/200`、`tVar<0.090035<91/1000`，以 `k^-16` theta tail 接合後，完整 Xi J12 門檻為 `k≥727`。最低 block error ratio 0.996630。改善幅度快速降為 137、56、18，故目前 absolute-Bell 加階路徑停止；degree-3 尚缺 `k≤726`。

J52 設計直接 moment 證書：逐 theta 項利用嚴格 log-concavity，以 endpoint chord 的 exponential integral 作下界、midpoint tangent 作上界，左右尾用 tangent／power bounds，高 theta 尾用 Gaussian sum integral test；最後 outward 計算 `C_k` 並核 J12.2。有限精度掃描到 k=728 的最小 recurrence margin 約 `2.0262e-6`，僅用來把目標 moment relative width 設為 `10^-7`，不構成證明。

J53 實作 directed cell Taylor quadrature：整格 F'' interval 給 quadratic 上下式，`exp(ax+bx²)` 用三階多項式逐係數積分並加 `h exp(eta)eta^4/4!` 餘項；window 外用凹性 tangent。以 `h=0.45/k` 加 J14 directed theta tail，完整 Xi 的 `[50,400]` 分四 batches 全部嚴格通過 J12，最小認證 margin `2.9422e-6`。這不是 SciPy 誤差估計。degree-3 剩 `k≤49` 與 `401≤k≤726`。

J55 稽核發現初版 cell upper 使用 down-rounded width，形式上漏約 1 ulp；修正為 lower lengths 向下、upper lengths與 F'' domain同步外擴後，完整重驗 `[1,34]`、`[35,49]`、`[50,150]`、`[151,325]`、`[326,450]`、`[451,726]` 全通過，並接 J51 `k≥727`。故所有 shifted cubic Jensen polynomials 已證 hyperbolic，有限段最小 margin `9.93675e-7`。

J56 策略稽核明確否定 cubic 升階：exact 序列 `(25,78,143,76,29)` 的兩個 shifted cubic discriminants為 `1622598480,555001200>0`，quartic discriminant卻 `-1348512563200`。degree 3 只控制四項局部比率／第三 cumulant；沒有 uniform-in-d 機制。研究停止逐 degree finite certificates，轉向 exact recurrence `J_(d+1,n)=J_(d,n)+XJ_(d,n+1)` 所需的 uniform interlacing、Jensen Hermite/Bezoutian uniform Gram factorization、或 coefficient-array PF∞。raw Hankel positivity及 translation TP2 不足。

全階 A7 把升階精確化：若 r_i 為 `J_(d,n+1)` 的根，則 `J_(d+1,n)(r_i)=J_(d,n)(r_i)`；critical values 交替符號即為新增一階全實負根的 minimal condition。pairwise compatibility 是否在 Pascal recurrence 下封閉仍未知，可能須整族 `X^jJ_(d,n+j)` common interlacing。A8 另證 naive mixture Gram 失敗：degree-2 cross kernel已是 `st-(s²+t²)/6`，尺度比 10 時嚴格負；所以 uniform Gram 必須用 Xi score/theta 結構重排，不能只靠 Phi 正性。

全階策略稽核再把 PF∞ 與 Pick 路線寫成逐點命題。令 `G=sum gamma_k w^k/k!`；若 `Im(G'/G)(z)<=0` 對全部上半平面 z，則非實零點會使 log derivative 在極點鄰域取兩種虛部符號，故被直接排除。這是真正 uniform-in-d 的充分引理；缺口是證 Xi 雙積分 `Im[G'(z)conj G(z)]<=0`。正 mixture 不封閉此性質，exact measure `3δ_1+δ_100` 已使 `h'(0)>0`。此外 J56 反例的 h 在原點通過 m=0,...,5 的六個交替導數符號，第 m=6 才以 exact 負值失敗，同時 quartic discriminant仍為負；已新增 Fraction verifier。這封閉了以有限 complete-monotonicity 批次冒充升階定理的路徑。

另釐清 cubic 的正面遺產：它只由 Rolle 給 `J_(2,n+1)` 與 `J_(3,n)` 的縱向交錯；升 quartic 需要相鄰 `J_(3,n),J_(3,n+1)` 的橫向共同交錯。J56 已嚴格分離兩者，所以 degree 3 是 induction base 而不是 induction mechanism。

Pick 路線現有一個具體 all-size 行列式版本。令 `b_m=(-1)^m h^(m)(0)/m!`；RH 型 factorization 使 b 成 Stieltjes moment sequence，故兩族 Hankel matrices `(b_(i+j))`、`(b_(i+j+1))` 對所有尺寸 PSD。反向配合解析 growth bound可重建 `h(w)=int(1+xw)^(-1)dnu`，直接得到 anti-Pick。J56 exact 反例雖有 b_0,...,b_5>0，但兩個首階 Hankel determinants已分別為 `-2119/15625`、`-610088/234375`。所以這是 degree 3 未提供的真正 determinant structure；下一步須找 Xi-specific 的 all-r Gram identity，不能有限逐 minor 驗證。

又完成對實際 J12 證明結構的強稽核。無限正序列可由 `C_1=61/1000,C_2=49/1000,C_k=6/125 (k>=3)` 與 ratio recursion exact 建成；它在每個 k 都滿足 J12.2，因而所有 shifted cubics hyperbolic，首個 quartic discriminant卻為負。Bareiss verifier 已擴充核對。故此次長篇 moment/cumulant工作得到的是嚴格但純 cubic 的 corridor，沒有 hidden all-degree induction。

A12 的最低 Gram determinant代回 Xi 型偶矩後為 `[3M_0M_1M_3+15M_1²M_2-10M_0M_2²]/(1440M_0³)`。一般正 mixing不保其符號：`(3/4)δ_0+(1/4)δ_1` 給 exact `-13/92160`，小幅移開 0 仍為負。這排除以 raw moment Gram或 Phi>0 直接完成 Stieltjes--Hankel；只剩真正使用 Xi theta/score identities 的 all-r factorization才算非循環進展。

將 PF∞/Pick/Stieltjes 明確認定為同一 obligation 的三種座標，不再當三條獨立攻面。S-fraction座標顯示 J12 的單調 C 確實給前兩個正 pivots：`a_1>0,a_2>0`；但 exact J12 chain `(17/500,4/125,29/1000,...)` 使第三 pivot `a_3` 為負。這是 degree 3 真正可保留的有限結構，也是其停止點。

進一步精確排除「C 完全單調即可升階」。取 `C_k=1/[4(k+2)]=int_0^1 t^(k-1)t²/4 dt`，它有所有 Hausdorff finite-difference signs，並嚴格滿足全域 J12；Fraction Sturm chain卻給 `J_(10,0)` 只有 6 個實根。新增 verifier 已重驗，數值未參與結論。

Pascal recurrence亦完成 closure audit：full compatible family `X^jJ_(d,n+j)` 的確在 adjacent-sum map下封閉，但 d=0 無 base，degree 3 的 individual hyperbolicity也不建立整族 compatibility。弱化到只要求所需 binomial sums則 exact 等於 higher Jensen目標，沒有獨立內容。

theta 結構的 uniform 稽核給出 exact convolution：`Phi(u)=int T_1(u+a)dmu(a)`、`mu=sum n^-1/2 delta_(log n)`；mu 的 Laplace transform恰為 `zeta(s+1/2)`。這說明大-k 時可忽略高 theta 項的 J14 機制不能轉成 fixed-shift/all-degree perturbation；全階 determinant若存在，必須控制離散 `log n` shift measure的 compound structure，而非只控制 T1 envelope。

補充正則化邊界：上述 mu 的總質量與普通正次 moments發散，僅 exponentially damped Laplace transform在 `Re s>1/2` 有限。故 standard moment Gram/Andreief不能直接使用；任何 damping removal都需重新證 compound signs，不可從 mu 的正性自動推出。

又找到 compact positive-moment 的 global-J12 exact 反例。取兩個指定 Beta 變數乘積 S，則 `M_k=E[S^k]` 是 `[0,1]` 正 measure moments；其 factorial-normalized gamma 的 C_k 是顯式 rational function。把四個 J12 numerators平移 `k=m+1` 後，Fraction verifier證每個 coefficient非負且常數正，故對所有 k成立；但 integer Bareiss給 quartic discriminant嚴格負。這比 abstract gamma反例更強，正式排除 raw moment positivity與 J12 合用即可升階。

轉查獨立 Li arithmetic route後，D9 將 D7 的 Abel pole term辨認為 `int_1^infinity x^(-1-delta)L_(n-1)^1(logx)dx`，故與 prime sum精確合成對 `Q=x-psi` 的單一 Stieltjes integral。分部積分得到 kernel `(1+delta)L_(n-1)^1+L_(n-2)^2`。這是合法 cancellation formula，不再犯 D4 的交換錯誤；但 absolute PNT-error估計會產生 factorial growth，尚缺 Q 與 Laguerre oscillation的單側一致消去。

生成函數交叉檢查發現並修正 D9 boundary：`L_(n-1)^1(0)=n`，故常數是 `-n`。D10 再用 contiguous identity與 `F(s)=int Q(e^t)e^-stdt=[1+h(s)]/s` 將 Abel kernel嚴格簡成 `L_(n-1)^2`；delta項由 F 在 s=1 的解析性消失。最後的 generating function精確回復 D1 binomial transform，完成公式內部 audit。

隨後對照現有 `chebyshev_laguerre_kernel.md`，確認 D10.3 已是 C1；故此處應計為文件同步與獨立 audit，不是新增攻面。C2 的 pure-power response已顯示 Laguerre kernel精確偵測 `theta=1/2`，所以要證其單側次指數 bound仍等價承擔零點臨界實部資訊。

建立 `strategy_audit.md`，將所有現存路線按「真正 uniform輸出／已排除捷徑／最小未閉合 inequality」對齊。Jensen一般升階假設已有 exact 反例；PF∞/Pick/Stieltjes只是一條 obligation；theta shift measure需正則化；Li/Chebyshev、Nyman及 mean-square各自停在等價承擔 RH 臨界資訊的 arithmetic estimate。後續拒絕 finite batches與等價換名。

C4 用 Laguerre三項遞推與 orthogonality證明：`Q_p<infinity` (`p>=2` integer) 使 D10 tail僅 polynomial in n，compact interval由 generating-function Cauchy bound為 `e^(O(sqrt n))`，故 E_n 絕對次指數。這完成 Li signed projection與 Chebyshev positive energy的嚴格橋接；但 M1 已說 `p>5` 的能量有限性等價 RH，故沒有獲得較弱無條件入口。

完成全目標終止稽核。RH 沒有被證明；然而 J24 起始工作已完整推到經 1-ulp 修正的全 cubic theorem，且 degree-3→all-degree、general positive moments、J12、C complete monotonicity、PF∞/Pick/Stieltjes、Pascal compatibility、theta shifts、Li/Chebyshev、Nyman與 mean-square各路均已記錄到 exact反例或最小 RH-equivalent缺口。依使用者明訂的第二終止條件，現在沒有應繼續執行的非循環候選；停止有限證書與 heuristic擴張。

## 2026-08-14：撤回全域「窮盡」宣告，重開自伴譜行列式路線

重新稽核發現，上一段只能證明當時列出的路線已耗盡，不能證明所有合理
數學攻面皆已窮盡。依 Pólya lens 的 toy-test 建議，取功能域型 factor
`P_q(T)=1+qT²`。在 central coordinate 它給 `Xi_q(z)=cos(log(q)z)`，故
`G_q(w)=cosh(log(q)sqrt(w))`。

令 A 為區間 `(0,log q)` 上 Neumann--Dirichlet 的正自伴 Laplacian。
其 eigenvalues為 `((m+1/2)pi/log q)²`，且普通 Fredholm determinant精確為
`G_q(w)=det(I+wA^(-1))`。因此 `G_q'/G_q=Tr(A+w)^(-1)`，逐點 anti-Pick；
展開 resolvent又直接給兩族任意尺寸 Stieltjes Hankel Gram PSD。完整推導
見 `spectral_toy_route.md`。

這是成功的 uniform mechanism 測試，但不免費解決 arithmetic：一般
`1-aT+qT²` 的 critical-circle bound `|a|≤2sqrt(q)` 正好等價於 boundary
phase unitary／operator self-adjoint。對 Riemann Xi 的新缺口是從 theta 或
primes 獨立構造正自伴 A 並證 `G/G(0)=det(I+wA^(-1))`；以未知零點反造 A
屬循環。研究因此重開，但 RH 仍未證。

同時完成最便宜的 type falsification：把乘法算子 U 置於
`L²(Phi(u)du)`，固然有 `Xi(z)=<1,cos(zU)1>`，但任意正 Fourier measure
都有這種自伴 matrix-coefficient 表示；K2 的非實零點反例已排除其充分性。
所以新路線必須產生 determinant／resolvent trace，而不能只說 Xi 是某個
自伴算子的 spectral transform。

依 Selberg lens 再檢查 product closure。若 `G_j/G_j(0)=det(I+wA_j^-1)`，
則 `G_1G_2` 由 `A_1 direct_sum A_2` 實現，log-resolvents及 Pick--Loewner
kernels直接相加；可數情形的精確門檻是 `sum Tr(A_j^-1)<infinity`。所以
單因子譜機制確實可組合。

但此 closure不能套到 Xi 的 theta 正和；determinant不對正 mixture封閉，
A8/K2已給低階反例。它也不能直接套逐 prime Euler factors：在
`s=1/2+iz` 中，`(1-p^-s)^-1` 的 poles為
`z=-2pi k/log p+i/2`，local factor本身不可能是正自伴 determinant。故
Riemann 候選必須先把 theta/primes全域重組。

為使下一責任可稽核，已把 resolvent條件改寫成單一 Pick--Loewner kernel
`K_h(z,zeta)=-[h(z)-conj h(zeta)]/[z-conj zeta]`。若 `h=Tr(A+z)^-1`，
則任意有限取點的 kernel matrix是 resolvent vectors的 Gram matrix。直接
由完整算術結構證此 all-point positivity（且不先假設 zero-free）是新的
uniform充分目標。

最後稽核 theta 正和是否可由 interlacing-family 保存。fixed-scale
`cosh(u sqrt(w))` 的正 spectrum為 `((m+1/2)pi/u)²`，其 counting function
是 `u sqrt(R)/pi+O(1)`。不同尺度的 counting差隨 sqrt(R) 無界，但任何
共同交錯兩序列的前綴計數差至多 1。因此 theta continuum components沒有
全域 common interlacer；不能把 component determinants直接平均。這進一步
確認若 Xi operator存在，必須是耦合全部 theta/primes後的全域新構造。

## 2026-08-14：exponential-wall archimedean core

先完成 operator route 的循環 audit：不加限制地聲稱存在正自伴 A 且
`G/G(0)=det(I+wA^-1)` 與 RH 等價；RH若真，可直接以未知 ordinates平方
造 diagonal A。因此新內容必須是由算術獨立指定 A。

接著用正軸增長排除 regular finite-interval Sturm--Liouville。功能方程、
xi 的 gamma factor與 Stirling給
`log G(w)=(sqrt(w)/4)log w+O(sqrt(w))`；普通有限區間二階算子只有
`log det=O(sqrt(w))`，譜密度不足。

找到一個密度正確的顯式 core：半線 Dirichlet operator
`A_0=-4d²/dx²+16pi²e^(2x)`。代換 `y=2pi e^x` 後，decaying solution是
`K_(sqrt(w)/2)(2pi e^x)`，故 normalized determinant為
`D_0=K_(sqrt(w)/2)(2pi)/K_0(2pi)`。large-order Bessel asymptotic正好給
Xi 同一個 `(sqrt(w)/2)log[sqrt(w)/(2pi)]-sqrt(w)/2` 主體。更精確地，
`(G/G(0))/D_0` 在正軸只長成 `C w^(9/8)`。

這導出新的 prime-relative spectral problem：構造 A_0 的正自伴 arithmetic
perturbation A，使兩 determinant比等於上述 relative factor。Euler half-
plane中 `log zeta(1/2+x)` 是 lengths `m log p`、weights `p^(-m/2)/m` 的正
Laplace series，提供 scattering/trace 候選資料；但 local factors非自伴，
必須全域 unitary coupling並由 operator analyticity完成 central continuation。
完整推導見 `spectral_archimedean_route.md`。離線數值除錯因環境缺 mpmath
未執行，所有記錄結論均來自解析 Bessel/Stirling計算。

進一步發現 theta summands 本身是 exact Morse states，而非只有 exponential
tail相似。置 `y_n=pi n²e^(2u)`、`phi_n=T_n/(2e^(u/2))`，則
`phi_n=y_n(2y_n-3)e^-y_n` 且直接微分有
`phi_n''=(4y_n²-20y_n+4)phi_n`。所以每個 n 定義一個 shifted Morse
operator `H_n=-d²+4y_n²-20y_n+4=Q_n^*Q_n`（取 ground-state Robin
boundary），phi_n為正 zero mode。一般 decaying solution精確為
`z^-1/2 W_(5/2,sqrt(1+w/4))(z)`。

raw state-sum仍不推出 determinant，但自伴 star coupling提供合法 sum
closure：共同 boundary/Kirchhoff condition的 secular equation是
`sum c_n²m_n(w)=alpha`，Weyl--Nevanlinna性在正權和下保持。這避開了
determinant正和不封閉與 fixed-scale無共同交錯的反例。新的可否證計算是
比較此 exact Whittaker Weyl sum與 Euler half-plane中的 Xi log derivative；
尚未證匹配，故不得宣稱 operator已構造完成。

P7.2 已另由 `experiments/verify_theta_morse_identity.py` 以整數 polynomial
arithmetic重建；這只是 exact algebra audit，不是有限零點或 RH 數值證書。

完成 Morse-star 的 density falsification。每個 fixed n channel都有一份
`sqrt(lambda)log lambda/(4pi)` Weyl主項，有限 N-channel star因此多出 N
倍；全 theta direct sum中 active channels約為 `lambda^(1/4)`，將有效長度
`(1/4)log lambda-log n` 對 n求和後得到 `Theta(lambda^(3/4))`，亦非 Xi
密度。energy-independent self-adjoint boundary coupling只改 lower-order
counting，不能修正主階。

Riccati expansion另給 `m_n(x²)=-x-V_n(0)/(2x)-V_n'(0)/(4x²)+...`；有限
正權 Weyl sum有 algebraic tail，而 Euler relative trace首項是
`-(log2)2^-x/(2sqrt(2)x)`。所以未作無限 renormalization的固定 star sum
連 asymptotic scale都不匹配。P8 naive assembly已解析封閉；P7只能保留為
單一 archimedean core的 auxiliary/relative channel資料。

依 nudge 補作 infinite Weyl-sum convergence audit。large-z Whittaker展開
嚴格給 `m_n(w)=-2pi n²+4+O_K(n^-2)`；因此自然 theta-decay weights可使
原和 locally normal convergence，也可減去前兩個 real constants後作
Nevanlinna-preserving renormalization。問題不在形式發散，而在 poles：
各 channel Dirichlet pole residues同號，正權 `c_n²` 不能 cancellation，
所以 level-set zeros仍繼承 union pole的 `Theta(lambda^(3/4))` counting。
signed/energy-dependent cancellation會失去固定 self-adjoint star extension。

又建立 prime Hamiltonian 的 exact type audit。`H_Pe_p=(log p)e_p` 是正
自伴，且 `zeta(s)=det(I-e^-sH_P)^-1` 在 `Re s>1` 嚴格成立；也等於 bosonic
Fock partition trace。用 `e^-a sqrt(w)` 的 subordination可把 Euler log寫成
正 Laplace transform。這是非循環 operator identity，但屬 semigroup而非
resolvent determinant，跨越 `Re s=1` 的 trace-class boundary正是未知解析
延拓責任。

local amplitude `p^-1/2` 可嵌入 unitary vertex scattering matrix，由額外
channel承擔 leakage；loop長 `log p` 便產生全部 prime-power repetitions。
然而所得 local singularities是 self-adjoint open system的 resonances，非
point spectrum。若關閉 channels，新增 mixed return orbits破壞 Euler log。
故逐 prime量子圖仍不能完成 P4.3；必須有全域 orbit-recombination identity。

## 2026-08-14：模曲面 scattering 的全域 realization 與 Blaschke 障礙

離線重建 Eisenstein constant term，得到 scalar scattering coefficient
`varphi(s)=sqrt(pi)Gamma(s-1/2)zeta(2s-1)/[Gamma(s)zeta(2s)]`
`=Lambda(2s-1)/Lambda(2s)`。所以 gamma、primes與 functional equation其實
已有同一自伴 modular-Laplacian scattering realization；G16 的「全域
recombination不存在」須修正成「存在，但只產生 resonances」。

非平凡 zeta zero rho給 scattering pole `s=rho/2`，故 RH等價於所有此類
poles在 `Re s=1/4`。ambient self-adjointness只給 physical line
`Re s=1/2` 上 `|varphi|=1`。exact Blaschke factor
`(s-a)/(s-(1-conj a))` 可把 zero放在任意 `Re a>1/2`，仍保持 boundary
unitarity、reflection、conjugation symmetry；其 phase-delay甚至是正 Poisson
kernel。故一般 scattering positivity不選出 1/4 line。

新的最小 operator obligation是對 resonance generator Z 證
`Z=I/4+iT`、T self-adjoint（或等價 normality加 scalar real part），且
positive metric必須從 modular/Hecke arithmetic獨立構造，不能由 zeros反造。
詳見 `modular_scattering_route.md`。

依 Selberg-lens nudge 補上 pointwise identity與 Weyl density之間的分布跡
測試。對 `w=x²`，prime log-derivative的 inverse Laplace kernel exact 為
`-(2sqrt(pi t))^-1 sum Lambda(n)n^-1/2 exp[-(log n)^2/(4t)]`。這是 explicit
formula中的 prime orbit heat distribution。

它嚴格排除 sign-definite trace-class additive model `A=A_0+V`：原始
Xi/core ratio有 `w^(9/8)`，不會趨 1；即使先吸收 archimedean power，prime
factor的 `2^-sqrt(w)` 超代數衰減也不容許任何非零 fixed-sign algebraic
trace moment；精確地 `w log Delta_V->Tr V`，故固定符號 V只能為零。模曲面 scattering以 signed spectral-shift distribution仍可
重現該式，故剩餘責任不是再寫一次 trace formula，而是把 signed resonance
measure升成 `Re Z=1/4` 的正離散 spectrum。

把 G17 再化成 elementary two-sided contraction lemma。若 resonance
generator Z 在同一正 Hilbert norm上使 `S(t)=exp[t(Z-I/4)]` 與 S(-t)對
t>=0皆 contractive，則
`||v||<=||S(t)v||<=||v||`，故 S 是 unitary group、
`Z=I/4+iT`。這會直接證 RH。現有 functional equation只配對 incoming/
outgoing semigroups，未給同一 positive completion；不同 norm或 indefinite
pairing不足。下一步可集中尋找 modular/Hecke-induced common norm。

以 `diag(1/4+delta+i gamma,1/4-delta+i gamma)` 作 exact toy：swap symmetry
已給 functional-equation reflection，但 centered evolution含
`e^(delta t)`，任何正等價 norm的 operator norm都至少是 spectral radius，
故不可能雙向 contractive。MS8 因而不是空泛換名；它精確加入了現有
scattering symmetry所缺的 common-metric rigidity。

接著稽核 Hecke 是否能供應 common positive norm。normalized `T_p` 的
Eisenstein eigenvalue為 `p^(s-1/2)+p^(1/2-s)`；只在 physical line為實。
即使 RH真，resonance `s=1/4+i gamma/2` 上仍通常複數，所以任何包含該
resonant state且保持 T_p self-adjoint的正 Hilbert completion都不可能。
Hecke只能透過 paired/biorthogonal form參與，不能直接完成 MS8。

完成 common-norm 的 local/model-space audit。cusp coordinate `r=log y` 中，
flat modes為 `e^((s-1/2)r),e^((1/2-s)r)`；任何 exponential weight只給
`Re kappa<alpha` 的半平面可積性。full-line weighted translation只是人工
平移譜線，half-line compression則不可逆，所以不能強制 resonance line
1/4。generic Hardy/de Branges--Rovnyak space也對任意 Blaschke zeros自動
正，只給 one-sided contraction。

global common norm最終與 Weil positivity接合：explicit formula作用於
multiplicative convolution square `g*g*`，RH下 zero side成
`sum |g_hat(rho)|²`；對所有 g非負反向亦排除 off-line zeros。這精確說明
MS8不是免費新定理。唯一合格的新輸入是把 prime與archimedean side對所有
g建立同一 arithmetic square/Gram factorization；目前尚無。

建立 `weil_square_route.md` 作 toy與Riemann機制對照。unitary Frobenius U
嚴格給 `sum c_m conj(c_n)Tr(U^(m-n))=Tr(P(U)P(U)^*)>=0`，genus-one最低
determinant正是 Hasse bound。這說明全階 square的正確形狀。

prime Hamiltonian在 critical normalization是 diagonal contraction
`p^-1/2`；similarity保持 spectrum，故任何正 metric change都不能使它在
原 space成 unitary。unitary dilation只給 matrix coefficients且新增 leakage
channels。Riemann端仍缺從 prime+gamma直接構造 `Weil(g*g*)=||V_g||²`
的 all-test identity。

依最新 nudge 將 pairing equivalence作二維 exact audit。reflection
`R(s)=1/2-conj(s)` 的 off-line orbit若由 functional equation作
incoming/outgoing配對，其 Hermitian block是
`[[0,r],[conj r,0]]`，eigenvalues `+-|r|`。故 natural pairing正定本身
便排除 off-line orbit，並非較弱能量條件；若未從 arithmetic side先證
square，宣告正定就是循環宣告 RH。

## 2026-08-14：Weil prime difference-energy 與 dilation-gap 稽核

在 centered log-variable 固定 Fourier normalization後，重建完整
prime+gamma Weil form。對每個 p，prime-power correlation精確等於
`||D_pg||²-||g||²`，`D_p=sqrt(1-p^-1)(I-p^-1/2T_(log p))^-1`。
Poisson multiplier的最小值與最大值分居 1 兩側，故 local dilation不是
contraction defect，不能逐 prime取平方。

另取 `H_R(z)=(z²+1/4)e^(-Rz²)`；pole evaluations恰為零，而 gamma form
漸近常數正比於
`psi(1/4)-log pi=-gamma-pi/2-3log2-log pi<0`。故純 gamma/pole block
可負，排除把它當正 Schur base；這是解析反例。

正向的新結構來自平移恒等式。若 g 支撐長度為 A，完整 prime side精確為
`E_A-2S_A||g||²`，其中
`E_A=sum_(n<=e^A)Lambda(n)n^-1/2||g-T_(log n)g||²>=0`。
因此 G20 不再只是抽象 W4.1，而成為 all-support 非局部 Poincare不等式
`E_A+A_infinity>=2S_A||g||²`。它一次涵蓋所有 tests，確屬新的 uniform
方向；但該不等式本身仍等價承擔 Weil positivity。下一個非循環輸出須是
adelic common dilation：由 product formula把 archimedean項辨認成 full
norm counterterm、prime difference energy辨認成 compression defect。

同輪再找到 pole--continuum completion。kernel
`e^(-(2j+1/2)|u-v|)` 的 Fourier multiplier正是
`Re(1/(j+1/4+it/2))`；取 j=0 至 3 並用 digamma recurrence，gamma加這
四個正 kernels成為 multiplier
`Re psi(17/4+it/2)-log pi`。由
`Re psi(x+iy)>=psi(x)>log(x-1/2)` 及 `15/4>pi`，此 block嚴格正定。

pole kernel扣掉四項後是 continuum kernel
`w_4(a)=e^(a/2)-e^(-5a/2)-e^(-9a/2)-e^(-13a/2)`；它在 prime可達的
`a>=log2` 上嚴格正，但 `w_4(0)=-2`，故短 archimedean endpoint layer
仍有符號。完整 Weil form exact 成
`Q_W=B_4-2R_4`，其中 B4已證正，R4是 von Mangoldt離散 measure減 w4
continuum measure的 autocorrelation discrepancy。新的最小充分命題是
對全部 compact-support g證 `2R_4(g)<=B_4(g)`。這不是證明完成，但比
抽象 W4.1多出了 canonical正 base與唯一算術誤差；後續只接受對此誤差的
uniform Gram／large-sieve／adelic projection機制。

Selberg nudge 再產生一個真正 all-order 候選。廣義 von Mangoldt
`Lambda_k=mu*log^k` 可由多重 finite-difference積分證對全部 k、n非負，
且 Dirichlet-series微分給 exact recursion
`Lambda_k log+Lambda*Lambda_k=Lambda_(k+1)`。這不是逐 degree證書，而是
完整正測度階層。稽核亦定位其斷層：log convolution在 Weil test中給
`C_g(a+b)`，是 forward/backward feature vectors的 cross pairing；普通
Gram square只給 `C_g(a-b)`。所以尚需一個結合 number operator與全部
recursion、且不引入 mixed orbits的 doubled/Fock block positivity theorem。

再稽核後修正上述 Fock期待。裸 `Lambda_k(n)` 並非 moment sequence：對
`n=p^m`、normalize `logp=1`，`q_k=m^k-(m-1)^k` 有
`q_1q_3-q_2²=-m(m-1)<0`。但正確 normalization存在：若
`r=omega(n)`，則
`j!Lambda_(r+j)(n)/(r+j)!` 是 box
`product_(p|n)[0,logp]` 上函數
`(logn-sum t_p)^j` 的 moments，因此給全部尺寸 Hankel Gram。prime powers
正好對應相鄰 logarithmic cells，零階 box mass就是 `Lambda(p^m)`。

依最新 Selberg nudge，這個成果仍未跨過核心斷層。所有 box與 recursion
都在 `a+b` convolution algebra；`delta_L` 的全部 convolution powers皆為
正測度，但 symmetrization Fourier transform `2cos(tL)` 仍取負，嚴格證明
它不推出 `a-b` group positivity。Gibbs generating function
`zeta(sigma-z)/zeta(sigma)` 也顯示 all-k positivity只把 zeros當 numerator
zeros；扣除最近的 pole以暴露 zeros時，正性便退化成 W8 signed discrepancy。
所以停止單純升 k，下一介面只接受 theta/Tate/adelic reflection把 half-line
convolution轉為 group Gram，且須獨立處理 contour residues。

archimedean正 block又得到 exact square，而不只 Fourier multiplier下界。
digamma series把
`B_4-c_4||g||²` 分成 `b=17/4+j` 的 resolvent differences；每項恰為
`int_0^infinity e^(-2ba)||g-T_ag||²da`。求和得到 W12.3：權重
`q_4(a)=e^(-17a/2)/(1-e^(-2a))` 的連續 translation-difference energy。
因此唯一缺口 W12.4 是精確的 operator large-sieve：R4 的任意長
prime-shift discrepancy須由近零 `1/(2a)` 型 logarithmic Sobolev energy
與固定 L2 mass控制。這顯示 archimedean factorization已完成，真正困難是
跨尺度 prime cancellation。

另開 `debruijn_newman_route.md` 作獨立 uniform audit。由 backward heat
`partial_tH=-partial_z²H` 推得 real simple zeros的 exact dynamics
`x_j'=2PV sum_(k!=j)(x_j-x_k)^-1`。相鄰 gap平方滿足
`(d_j²)'=4kappa_j`，`kappa_j=2-d_j²A_j`。exact infinite clock lattice有
`A_j=2/d_j²`、kappa=0，說明高處小 gaps本身不是問題；正確充分條件是
全部 j 的 integrated positive clock defect不耗盡 `d_j²(t_0)`。一般
backward heat由 quadratic toy `z²+a-2t` 證明可在正時間碰撞，故仍需
theta-specific uniform phase/spacing cone。

W13 將 W12.4 與 Mellin boundary精確接合。centered prime discrepancy
`F_4(lambda)` 在 regular `lambda=it` 上由 functional equation滿足
`2ReF_4=b_4`；Weil measure全部來自 boundary Poisson deltas，off-line zeros
則是在 Euler half-plane移往 axis時跨過的 residues。Chebyshev分部積分又給
`F_4=1+sum_(j=1)^3(s+2j)^-1-sint A(x)x^(-s-1)dx`，故此缺口與 M1
weighted L2在 residue層合流；忽略 contour residues就是循環。

依 large-sieve nudge補上逐點強度。若有任一 off-line quartet，其 zero
pairing block有負 eigenvector。對所有低 zeros作 finite polynomial
interpolation，乘 `e^(-Mz²)`：目標 block保留負值，其餘低點為零，高尾由
zero counting與 Gaussian ordinate gap趨零。所得 test是合法 Schwartz
Fourier transform，故 all-test positivity會被單一 off-line orbit反駁。
所以 W12.4確實逐點推出 RH，不只是 zero-density；任何受限 bandwidth或
average-only估計均不夠。

測試最自然的 Abel bridge：在 Euler絕對收斂區考察
`Q_epsilon=b_4-2ReF_4(epsilon+it)`，希望全 epsilon正再取 boundary limit。
W15 給解析反例。於 `epsilon=4,t=0`，只取 prime 2並用初等 rational bounds
即有 `F_4(4)>2521/24752`、`c_4<1/5`，故
`Q_4(0)<-229/61880`。因此 pole/gamma subtraction在遠離 critical line時
已破壞 scalar form positivity；不能以 Abel damping保正繞過 contour
residues。

DN 路線新增 finite-window deterministic lemma。若 gap `d_j` 周圍前後 M
個 gaps皆至多 `(1+epsilon)d_j`，則由 telescoping
`sum 1/[m(m+1)]` 得 `kappa_j^+<=4epsilon+2/(M+1)`。配合 collision budget，
高處需要約 `M>>log²gamma` 且 `epsilon<<1/log²gamma` 的 all-index、all-time
clock rigidity。這排除用平均 spacing或 density-one結果填補 DN3.2。

依 nudge再把 DN uniformity寫成 height-block theorem：M、epsilon與起始
gap下界必須是 Gamma的共同顯式函數，同時涵蓋 block內全部 indices及整段
下降時間；逐 gap事後調參不算。

建立 `tate_reflection_route.md`。theta-sum
`E_f=x^(1/2)(Theta_f-f(0))` exact 滿足 Poisson rank-two reflection，且
Mellin multiplier為 `2zeta(1/2+it)`。這是天然 positive/unitary結構；但在
ordinary L2中乘法算子的離散 zeros為 measure-zero，因此 kernel trivial、
range dense，cokernel不承載 zeros。改成能看 off-line exponential modes的
analytic rigging後，dual half-plane pairing正好回到 MS13不定 block。
因此 Poisson unitary本身不足；尚需 TR5 型 arithmetic projection/commutator
defect，且其 trace必須在 contour shift前直接重現 primes+gamma。

TR6 再核對最自然 projection。log-halfline Hardy cutoff與 convolution的
commutator HS norm exact 為 `int|a||g(a)|²da`，完全 universal；E 的 L2
range projection因 dense range等於 I。故 Poisson E、standard Hardy P及其
直接組合不能給 von Mangoldt trace，TR5 若存在必須引入新的 adelic/
arithmetic projection與 semifinite trace。

TR7 找到真正 prime-local arithmetic projection：unilateral shift的 rank-m
Toeplitz defect乘 Euler primitive `1/m` exact 給
`Lambda(p^m)p^-m/2`，並平方化 W7 prime difference energy。TR8再以
`R x Z` quadrant model稽核 product formula：real shift `m logp` 與 p-adic
shift m可取消 signed boundary indices，但 positive commutator norm把兩條
infinite strips同號相加。double-boundary finite corner只重新實現 prime
weight，仍不消 diagonal debt。因此尚缺 signed adelic index到 positive
cohomology/Schur complement的升級 theorem。

TR9/TR10 對此升級作 finite-dimensional audit。two-term complex的 Hodge
supertrace只給 `dimH0-dimH1`；perfect duality仍容許 off-line型
`[[0,1],[1,0]]` 不定 block。local Toeplitz defect space雖有 reversal與標準
sl2 positive polarization，direct sum不含 global gamma/functional equation，
tensor product又新增 mixed-prime sectors。故 global complex必須同時令
mixed sectors acyclic並構造與 scaling相容的 positive Hodge star。形式 Schur
complement不算解法，因 cross-norm bound正是 W12.4。

TR11 修正 mixed-sector判定：bosonic symmetric Fock的 positive one-particle
projection已 exact 給
`-zeta'/zeta=Tr H_P(e^(sH_P)-I)^-1`，所以 distinct-prime mixed states可在
不使用 supertrace下移除。核心改成 critical prime occupation與 gamma
oscillator間的 positive operator relative trace。

TR12 證 atomic prime lengths與 nonatomic arch continuum不存在 exact
length-intertwining isometry；必須用 wave packets並支付 commutator error。
TR13 再以 PNT尺度排除 positive cell transport：每個 prime cell寬約
`logp/p`，全部 cells推回 displacement軸的 density約 `delta^-3/2`，而
W12 q4只給 `delta^-1` budget。故 surviving map必須跨 primes使用 global
oscillatory/orthogonal frame cancellation，不能靠 quantile mass matching。

TR14 將此 frame具體化為 prime torus Kronecker restriction。Haar characters
exact orthogonal，W7 prime distance `D_A(t)` 的長時平均恰為 diagonal debt
`2S_A`；所以普通 mean large sieve只給 bad recurrence times的 density。
all-test RH需要 Paley-Wiener functions不能集中於任一 recurrence window的
uniform-in-A restriction theorem。

依 nudge稽核 Bessel門檻。prime cell mass和 continuum density sums分別為
`2sqrtX` 與 `(2/3)X^(3/2)/logX`；geometric mean在
`delta~logX/X` 時是 `delta^-1 sqrt(logX)`。故 Bessel確把 power 3/2降為
critical 1，但仍差 unbounded square-root log，且另一 Cauchy因子就是
diagonal debt。這是 global oscillatory frame的目前最小定量缺口。

TR16/TR17 曾把剩餘問題改寫為 prime-torus peak 的 first-return bound，且
Haar first chaos確有 dimension-free subgaussian tail。但 TR18 找到解析反例：
PNT partial summation給固定 t 的 raw cutoff和
`F_X(t)=X^(1/2+it)/(1/2+it)+o(sqrtX)`。取 t=1 與相位對齊的 X 序列，固定
時間已有 `asymp sqrtX` peak，故任何 `log|t|gtrsim sqrtX` 或 reciprocal-Haar
首次命中下界皆為假。這是 cutoff endpoint coherence，不是 simultaneous
prime recurrence；smooth window亦有同一 Mellin主項。可行修正只能先減去
continuum，轉而控制 `int x^(-1/2+it)d(psi-x)`，即回到 W12 centered
prime--gamma discrepancy。Haar entropy路線正式封閉。

TR18 的數值 sanity check（不作證明）取 `t=1`：相位對齊 cutoffs
`X=1620,867628` 時，`Re F_X(1)/sqrtX` 分別為
`0.8785311,0.8936762`，趨近解析常數 `2/sqrt5=0.8944272`。

熱流另補 DN8 的 exact Vandermonde action。有限 real zeros下
`Delta=product_(j<k)(x_j-x_k)^2` 滿足
`(logDelta)'=4sum_j(sum_(k!=j)(x_j-x_k)^-1)^2`。因此 backward首次碰撞
必伴隨 action發散。這提供一個比 DN7 all-gap local clock rigidity更寬的
uniform候選：對 dyadic zero blocks扣除 clock bulk並控制 boundary flux，從
theta representation證整段時間的 renormalized action有限。無窮乘積的
renormalization與 uniform flux尚未閉合，故只是具體新方向，不是證明。

DN9 補正無窮維細節。有限高度 block的 discriminant導數是
`4sum S_j^I S_j=4sum(S_j^I)^2+4sum S_j^I R_j^I`，不是純平方；exact clock
lattice中 internal square恰被外部 flux抵消。可用的正量應是 full PV
velocity action `(1/4)sum int|x_j'|^2`。simple collision會使它 logarithmically
發散，故 uniform finite-action bound確為充分條件；尚缺 theta-side bound及
block外場控制。

DN10 完成 action循環稽核。有限系統 exact 有
`int sum S_j^2=(1/4)log[Delta(t0)/Delta(t)]`；係數表示
`V=P''(C)P'(C)^-1` 又把 discriminant藏在 inverse中。因此 action bound本身
就是 separation bound。更以 `f_d=(x²-d²)e^-x²` 證所有固定階 L2 derivative
norm可一致有界，而 root velocity `f_d''(d)/f_d'(d)=(1-4d²)/d` 發散。
普通 theta/Plancherel energy不能封閉 DN9；須有 zero-sensitive frame或
all-size determinant新結構。DN路線保留為介面但暫停。

依 nudge 回頭稽核 DN9.1 交叉項。結果：同尺寸 block中它不是平均小量；
clock lattice exact 有 `sum S^I R=-sum(S^I)^2`。但 core--buffer可救遠尾：
由 `+/-` 配對與 `N_t(U)=O(UlogU)`，對 `|x_j|<=Gamma,L>=2Gamma` 有
`|R_(j,L)|<=C Gamma logL/L`，core平方和至多
`C Gamma^3 logGamma log²L/L²`；取 `L=Gamma²` 即趨零。故 tail可逐點控制，
尚未控制的是 buffer transition layer及其 clock-renormalized flux。

轉回 centered Weil後得到 W16。置 `epsilon(a)=e^-a/2[e^a-psi(e^a)]`，critical
prime-minus-continuum measure exact 滿足 `dnu=-depsilon-epsilon da/2`。
故 compact-support autocorrelation C 的 discrepancy是
`C(0)+int epsilon(C'-C/2)`，再加三個顯式 decaying endpoint kernels。
此式在 Euler/prime側直接成立並 exact 移除 TR18 endpoint coherence。
PNT只給 epsilon 的 subexponential相對改善；absolute C/C' bounds仍隨 support
爆長。最小缺口成為利用 autocorrelation positive-definiteness對 signed
epsilon證 uniform logarithmic-form bound。

W17 以 normalized modulated boxes使 autocorrelation趨近 `cos(ta)`。
W12 dominated convergence給 `B4->b4(t)`；prime側則是 W16 discrepancy的
Fejer boundary value，其 `2R4->b4(t)` 正是未解 residue極限。故 target在
每個 regular frequency皆有 Weyl sequences飽和，不能有固定 coercive gap。
先前 Bessel/Cauchy的任何常數或 sqrt-log loss都不可能由 arch margin吸收；
所需輸出必須是 sharp constant 1 的 reflection/relative-trace identity。

W16 identity另以 triangular C 的直接有限 prime sum作數值 sanity check，
`A=1,2,4` 的兩側差約 `1.8e-7,-9.5e-7,1.5e-6`（quadrature error）；此僅
檢查實作符號，解析證明仍是 W16.2--W16.4。

W18/A20 將剩餘 uniform路線 exact合併。meromorphically
`F4(lambda)=A4(lambda)/2-xi'/xi(1/2+lambda)`，而
`h(w)=G'/G=[A4(sqrtw)/2-F4(sqrtw)]/(2sqrtw)`。所以 sharp Weil reflection、
all-degree Stieltjes/Pick Gram與 positive self-adjoint resolvent trace不是三個
獨立機會，而是同一 factorization obligation。仍須從 centered primes或
theta直接構造正 measure；用未知 zeros的 partial fractions會循環。

P13 將共同 factorization target變成 explicit all-order heat trace。對
`h=xi'/xi(1/2+sqrtw)/(2sqrtw)` 逐項 inverse Laplace，得到 pole `e^(t/4)`、
一個消去 u=0 singularity的 digamma integral，以及 P12 的負 prime Gaussian
sum。RH 等價於此 Theta(t) completely monotone：正向為
`sum exp(-gamma²t)`；反向由 Bernstein+Tonelli給 h 的 positive Stieltjes
measure。這是 uniform-in-degree criterion，尚缺從 prime--gamma公式直接
建立 single positive factorization；禁止逐 derivative批次。

P14 以 `e^-t+2epsilon e^-Rt cos(Bt)` 證 Theta點wise非負仍容許 off-axis
Laplace poles；任意固定 K 的 alternating derivative signs也可由縮小 epsilon
同時保持。故 P13 只能接受 all-k proof或 single measure identity。

P15 完成 Stieltjes boundary audit。critical-line zeros在 w-plane cut上已自動
給 `m/(w+gamma²)` 的正 atoms；off-line zeros則是 cut外 poles，不影響 boundary
sign。故 boundary spectral density／time delay positivity沒有證明力；P13
所需 factorization的實質是從 arithmetic side先驗證 h 在 cut plane無額外
poles。只用 functional-equation boundary data會循環。

P16 把 P13 all-k signs改成 single Hankel-semigroup target：對每個 tau>0，
`K_tau(s,t)=Theta(2tau+s+t)` 須有 compatible Gram factorization，且 time shift
為 symmetric contraction。spectral theorem即給 positive A與 Stieltjes
measure。local prime Gaussian只給 translated heat features的 cross pairing，
且帶負號；所以 Gram必須全域耦合 primes與 gamma，不能逐 length作 norm。

依最新 nudge完成 P17 large-k audit。RH target moments由 Riemann--von Mangoldt
與 saddle method為
`Gamma(k+1/2)t^(-k-1/2)log[k/(4pi²t)]/(8pi)`。prime kernel的 exact kth
derivative含 `k!t^(-k-1/2)e^-z L_k^(-1/2)(z)`；fixed-prime envelope已是
`k!k^-1/2t^(-k-1/2)`，同 factorial base只少 log k。故任何 `C^k`、階數依賴
Cauchy loss或 absolute Laguerre sum都致命；P16 factorization必須逐 k
zero-loss且 sharp。

P18 找到 explicit free Gram。`h_A=A4(sqrtw)/(4sqrtw)` 由 right-half-plane
Poisson formula exact 等於
`int [b4(r)/(2pi)]dr/(w+r²)`，所以 gamma block本身有 positive Stieltjes
measure及 feature `sqrt(b4/2pi)e^-tr²`。但 `h_F=F4/(2sqrtw)` 的 regular
cut density由 W13恰與 h_A 相同；h=h_A-h_F 的 continuous spectrum完全取消，
只剩 critical atoms或 off-cut poles。因此 simple measure domination不可能；
需要 self-adjoint boundary/scattering spectral flow把 continuum轉成 atoms。

P19 再作 spectral-type audit：h_A measure在全 `u>0` strictly a.c.，RH target
則為 zero atoms純離散。unitary equivalence不改 spectral type；rank-one
boundary Möbius formula的 density是 free density除以正 modulus square，也
不會消失；finite-rank/trace-class perturbation同樣保留 a.c. part。因此普通
self-adjoint boundary/scattering extension被排除。只剩 singular/non-trace-class
domain change、正 cohomological quotient或獨立 target operator。

P18.1 另以 scipy double precision作非證明 sanity check：`x=0.7,2,5` 時
Poisson integral與 `A4(x)` 的差分別約 `-1.35e-14,-4.52e-13,-1.84e-14`。
解析依據仍是 right-half-plane Poisson formula，不以數值作證。

P20 測試 P19 的 singular quotient。任意 off-axis Blaschke factor已有 positive
Hardy model quotient與 real Clark pure-point measures，故「continuum可被正
quotient離散化」不限制 inner zeros位置。只有再證 centered scaling generator
self-adjoint或同 norm two-sided contractive才有 RH內容；這回到 MS8/MS11。

P21 將存活 Hodge目標落到 exact determinant quotient。積分 W18 得
`D_A=pi^-x/2 Gamma(17/4+x/2)/Gamma(17/4)`、
`D_F=C(s+2)(s+4)(s+6)/[(s-1)zeta(s)]`，且 `G/G(0)=D_A/D_F`。
在 `Re s>1`，`1/zeta(s)=det(I-e^-sH_P)` 是 prime Hamiltonian的真 Fredholm
determinant。缺口精確是把 semigroup defect/leakage complex經 singular positive
cohomology reduction升成 resolvent determinant，同時保持 quotient且不新增
mixed orbits。

P22 把 `1/zeta=det(I-e^-sH_P)` 寫成 exterior Fock supertrace。basis subset S
的 energy是 `log product(S)`、parity是 |S| mod2；unique factorization使每個
energy只有單一且 parity固定的 state。因此任何 odd Q若與 H_F commute，必為
0，prime Fock內沒有 ordinary supersymmetric acyclic pairing。parity-reversed
duplicate只會全消 Euler factor；用 arch continuum配對又遇 atomic/non-atomic
intertwiner no-go。存活 Hodge differential必須 singular/rigged且另證正性。

最新 nudge 的 Carleman疑慮經計算不成立：P17 moments有
`M_k^-1/(2k)~sqrt(et/k)`，Stieltjes Carleman sum發散；representing measure
若存在即唯一。P18則補上 independent algebra proof：functional equation使
critical-line regular點的 `xi'/xi` 純虛，故 `ReF4=b4/2`。但已把「continuous
spectrum相消」修正為「regular cut boundary density相消」；未排除 off-cut
poles前不能宣稱完整 measure equality。

P21 quotient另作非證明 numerical algebra sanity：在 `x=.7,1,2,4`，未正規化
`(D_A/D_F)/xi(1/2+x)` 均為 `0.1664169204750487`（誤差約 1e-16），符合其
為 x-independent constant。解析證明仍由 log derivatives與 gamma recurrence。

P24 發現 P21 scattering ratio完全失去 nontrivial zeros。由 G even，
`D_F(-x)/D_F(x)=D_A(-x)/D_A(x)=pi^x Gamma(17/4-x/2)/Gamma(17/4+x/2)`；
boundary phase純 archimedean，G divisor成對消去。故 Lax--Phillips若只使用
unitary scattering ratio／time delay不可能證 RH；必須保留 absolute D_F
pole divisor並從 arithmetic side證其在 imaginary axis。

P25 將 P22延伸到 unbounded operators。任何 closed densely-defined odd Q若
strong-intertwine prime spectral projections，rank-one fixed-parity eigenspaces
仍迫使 Q=0；atomic-to-P18-continuum intertwiner因 singleton projection為0亦
必為零。distributional point evaluation雖非零，卻在 L2不可 closable，不能
形成 positive self-adjoint Q*Q。故 rigged Hodge若存活，必須另證新 topology
的 positive norm、自伴 scaling及 exact determinant，不能沿用 free Hilbert
space Hodge theorem。

依 nudge 補 P26：P22 obstruction是 topology-independent。每個 squarefree
energy fiber的 superdimension固定為 `mu(n)=(-1)^omega(n)`；任何 energy-
preserving odd differential的 cohomology仍有同 Euler characteristic，acyclic
pairs也不改。改 grading使 multiplicity全正會把 `1/zeta` 改成 `sum|mu(n)|n^-s`；
跨 energy differential則破壞 heat-supertrace invariance。故 rigging須連 grading
與 generator一併重建，不能只放寬 topology。

P27 將 P24 cancellation解讀為 hidden modes。scattering ratio只見純 arch
minimal system，可任意 direct-sum off-axis hidden block而不改 phase。若能從
P21 primes構造 full conservative colligation，且 positive total metric
nondegenerately限制到 hidden subspace，hidden centered generator即 skew-
adjoint，determinant G 的 zeros全在 imaginary axis。這是精確充分機制；目前
local prime dilations只給 observable passivity並會新增 mixed returns。

P28 修正 mixed-return判定並給 exact local construction。`2x2` self-adjoint
unitary colligation的 transfer是 `(z-r_p)/(1-r_pz)`；取
`z=e^-xlogp` 後 denominator正是 `1-p^-(1/2+x)`。finite conservative cascade
給 `e^-xL_P D_P(-x)/D_P(x)`，determinant不新增 mixed-prime factors，但 zeros
仍只有 local line `Re x=-1/2`。

P29 定位 infinite obstruction：Euler區有 trace-class convergence；critical
line移除 delays後 local deviations為 `O(p^-1/2)`，而 `sum_p1/p` 發散，連
Hilbert--Schmidt infinite unitary product都失敗。gamma renormalized ratio只
留下 P24並丟失 G。故須非標準 operator-level renormalization，同時保持正
energy與 absolute D_F determinant；scalar analytic continuation不夠。

依 nudge 加 P30 density-one層。若 hidden realization存在，MS13使每個 off-line
orbit至少給一個負方向，故 `N_off(T)<=C kappa_-(T)`；負指標為 `o(N(T))`
即可推出 density-one RH，負指標恒0才是 full RH。但 P28 cutoff poles不是
zeta zeros，P29又無 spectral convergence，所以目前連 cutoff metric到 hidden
K_T的 map都沒有。合格 staged route須先證 spectral-projector convergence，
再證 normalized negative index趨0，最後用 localization消除 exceptions。

P31 區分 operator與 determinant：`direct-sum U_p` 作為 unitary Hilbert operator
其實良定，但 critical scalar product不在 determinant class。meromorphic
continuation到 `1/zeta` 所新增的 collective divisor不是 local state spectrum，
沒有 hidden spectral projectors。因此 self-adjoint prime Hamiltonian加 scalar
regularized determinant仍不能證 RH；必須有 actual resolvent/projector limit，
使 divisor真正等於 operator spectrum。

P32 測試標準 operator renormalization。`K_s=diag(p^-s)` 在 `Re s>1/q` 屬
S_q；critical line上 det_3已良定且 nonzero。exact identity
`1/zeta=det_q(I-K_s)exp[-sum_(j<q)P_1(js)/j]` 顯示 nontrivial divisor完全移到
被扣除的 scalar prime-zeta cumulants；det_q positive operator部分看不見 zeros。
提高 q只移動分界並增加 cumulants。故須把前幾 cumulants與 arch block作
operator-level sharp factorization，scalar subtraction不夠。

P33 把 P32化成 exact circularity。`log det_q=-sum_(m>=q)P_1(ms)/m` 只包含
在 `Re s>1/q` 絕對收斂的 easy high prime-power tail；missing low cumulants
等於 `logzeta` 減此 tail。以 logζ定義它們再代回 determinant只是 tautology。
因此 standard Schatten route正式封閉；必須直接把 low prime powers與 arch
channel作 positive relative trace，不能靠 scalar cumulant continuation。

P34 從 P33抽出 two-orbit核心。`m>=3` Euler-log tail在 `Re s>1/3` analytic
zero-free；全部 ζ divisor只剩 `L12=P_1(s)+P_1(2s)/2`，即形式 trace
`TrK_s+TrK_s²/2`。這兩層沒有 distinct-prime mixed states。下一 target可只
把 prime、prime-square與 P18 arch channel作 sharp positive relative trace；
成功即足以控制整個 critical strip右半，再用 functional equation完成。

P35 對 P34作 cutoff尺度稽核。critical cutoff下 prime trace約
`2sqrtX/logX`，prime-square只約 `loglogX/2`，無法直接互相 renormalize。
Möbius公式中的 `-logzeta(2s)/2` 與 square的正項只在 analytic continuation
後相消。故 two-orbit正構造仍必須先由 arch continuum sharp扣除 prime bulk，
再處理 parity-sensitive log remainder；這正回到 W16/W12，不能只用兩個
diagonal positive traces。

最新 nudge 指出 P34還有更早的循環。`P_1(s)` 原始 prime trace只在
`Re s>1` 收斂，而 Möbius continuation
`P_1(s)=sum mu(m)logzeta(ms)/m` 的 singularities本就由 `rho/m` 決定。
因此在臨界帶把 `L12=P_1(s)+P_1(2s)/2` 當成已存在的 operator trace，已使用
target zero data；`exp L12=zeta exp(-R>=3)` 只是 tautological divisor identity。
P34現降級為 Euler區 bookkeeping，非 genuine reduction；two-orbit支線在沒有
獨立 low-orbit+arch construction前暫停。

同輪重做「是否窮盡」稽核。結論是否定的：被窮盡的是已測自然捷徑，不是所有
可能證法。仍存活的獨立攻面至少有 centered Weil sharp square與 de
Bruijn--Newman global collision barrier；positive cohomology是前者的 operator
construction版本。下一輪優先推 DN 的 tapered weighted-discriminant identity
與 clock commutator bound，因這是可在不假設 RH下先完成的中介引理；不再以
更多 finite degree／moment VERIFIED批次代替 uniform機制。

隨後完成 DN12 product-taper測試。對
`E_a=sum_(j<k)a_ja_k log(x_j-x_k)^2`，exact identity為
`E_a'=4sum(a_jS_j+H_j/2)^2-sum H_j^2`，其中
`H_j=sum_(k!=j)(a_k-a_j)/(x_j-x_k)`。在 clock `x_j=jd` 上，H是 multiplier
`i(theta-pi)/d` 的 discrete Hilbert transform；對慢 profile `a_j=A(j/L)`，
`||H||_2/||a||_2 -> pi/d`。所以普通 taper的 flux cost仍為 volume order，
沒有變成 transition error。DN線若續必須發明消去此 order-zero clock symbol的
nonlocal relative counterterm；product taper正式封閉。

DN13 完成 clock flow線性化。寫 `x_j=jd+u_j`，linear generator為
`u'=-(2/d²)Lu`，`L` 的 exact symbol是
`ell(theta)=pi|theta|-theta²/2`。正能量 `Q=<u,Lu>` 滿足
`Q'=-(4/d²)||Lu||²`，並以顯式 Fourier Cauchy bound逐 gap控制。但 backward
最高 mode amplitude放大 `exp(pi²t_0/d²)`；平均 spacing
`d~2pi/logGamma` 後，充分起始 energy須達
`d²exp[-(t_0/2)log²Gamma]`。這精確顯示普通 polynomial clock asymptotic不夠，
尚需 theta-specific matching rigidity；既有 J14/J24是 moment-index估計，
不能移用。

回應新 nudge，DN14另區分 density與pointwise。平均 local energy只能在仍
全實的區間內經 Markov控制 bad-gap比例；首次 collision後 labeling失效，沒有
collision count invariant便不能推出 density-one critical zeros。P30 negative
index可作此計數器但尚缺 projector convergence。因此三條正性語言的 density
版本目前也沒有已證非平凡結果，不能把 conditional mechanism當成果。

另開 `horizontal_shift_route.md`。令 `E_a(z)=Xi(z+ia)`；其 upper-half-plane
zeros恰對應 `Re rho<1/2-a`，所以 HB threshold等於 zero strip半寬。由已知
`0<Re rho<1`，`a>=1/2` 無條件為 HB，故
`A_a=[Xi(z+ia)+Xi(z-ia)]/2` 是一個 genuine all-degree real-rooted base。
若能從 de Branges kernel K_a以不使用 zeros的 theta/prime positive-defect
identity下降到 K_(a/2)，反覆 dyadic descent與 Hurwitz會完成 RH。

一般 harmonic deformation不能提供此下降：`F=z²+1` 給
`[F(z+ia)+F(z-ia)]/2=z²+1-a²`，在 a<1失去實根。因此新缺口不是 continuity，
而是 Xi bilateral theta features從 weight `e^-au` 到 `e^(-au/2)` 的 positive
untilting theorem。a→0的一階 kernel仍與 W18正性合流，故這是新 deformation
介面而非獨立重複計數；有限 kernel批次禁止作為替代。

HS7 再測 half-shift的最自然 universal-factor猜想並得到 exact反例。正離散
Fourier measure在 frequencies 1,2 取 weights `1,2/3`，則
`F_a=cosh(a)cosz+(2/3)cosh(2a)cos2z`。令 `x=cosz`，real-rootedness恰要求
coefficient ratio `r_a>=1`。在 `a=log2`，`r=17/15`；在 a/2，
`r=5sqrt2/9<1`。所以 base全實零而 half-shift後出現非實零，雖 measure全正。
HS5不能由 positive-definite ratio或 ordinary smoothing證成，必須新增 Xi
arithmetic total positivity／centered-prime defect。

HS8 將反例提升為結構判定。untilting ratio
`r_a=cosh(au/2)/cosh(au)` 有顯式正 Fourier density
`(sqrt2 pi/a)cosh(pi t/(2a))/cosh(pi t/a)`，所以它確是 positive
convolution；但 `1/r_a(-is)=cos(as)/cos(as/2)` 有未消去 poles，依
Schoenberg criterion不是 PF_infinity。故 ordinary smoothing不可能成為
variation-diminishing descent；只剩 r_a與 Xi Phi的 coupled arithmetic
determinant可能跨過 HS7。

HS9 進一步拆開 horizontal descent的兩通道：A乘
`r_a=cosh(au/2)/cosh(au)`，B乘
`q_a=1/[2cosh(au/2)]`，且
`r_a-q_a=1/[2cosh(au/2)cosh(au)]` positive definite。q_a本身對應
PF_infinity density，但方向是 smoothing；normalized convolution有 variance
`a²/4`，把 `z²` exact送成 `z²+a²/4`。所以 scalar PF_infinity仍會把 real
zeros移出實軸；唯一未排除的是兩通道共同作用後 Xi-specific symplectic
Bezoutian正性。

HS10 完成 half-angle循環稽核。置 b=a/2，exact 有
`E_b(z+ib)=E_a(z)`、`E_b(z-ib)=Xi(z)`，故
`A_b(z+ib)+A_b(z-ib)=A_a+Xi`，B-channel則只回 B_a。任何 inverse-shift
construction都會把 endpoint Xi帶回；若將其 K_0/cross term直接列為正
remainder，就是 W18循環。可接受的 coupled identity必須從 theta/centered
primes直接證這個 cross sign。

轉回 P18/P23檢查 Carleman可能性，得到 P37。令 u=-omega，omega為 G-zero。
arithmetic heat moments exact分成 critical positive atoms的 moments C_k，加上
`sum_off m u^k e^-tu`。P18只辨認 regular cut上的 critical atoms；off-cut poles
沒有 jump，因此 moment defect完全未被 boundary density決定。Carleman可在
positive representing measure存在後證唯一，卻不能把 candidate mu_crit變成
P13 measure。故「density equality + determinacy」捷徑封閉。

HS11 依早期 nudge回到 known-GRH toy。功能域 quadratic寫成
`cos(Lz)-costheta`，Hasse bound給 theta real；兩個 sine factors帶同一
shift-independent unitary phase，因此全部 horizontal shifts同時 HB，乘積由
self-adjoint direct sum封閉。這確認成功機制不是 smoothing，而是 arithmetic
unitary Frobenius input。Riemann目前沒有其 global analog。

最後完成全 nudge與路徑 impasse稽核。所有提示均已有 theorem、反例或缺口
回應。W16/P13/HS、spectral/cohomology與 DN最後分別要求同一類尚不存在的
Xi-specific global polarization／unitary monodromy／超多項式 zero-rigidity。
在沒有新 arithmetic identity前，再做 finite degree、finite kernel、數值
moment或等價改寫不會推進。RH仍未證明。

2026-08-14 使用者解除聯網限制，研究恢復。原始文獻帶來 genuine 新輸入：
Suzuki arXiv:2606.09096 無條件構造 localized Weil Friedrichs operator及有限
區間 deficiency `(1,1)` generator；Connes--Consani--Moscovici
arXiv:2511.22755 已證 prolate candidate `k_lambda` 的 transform在開半條帶內
locally uniform趨近 `Xi`。防循環稽核確認 finite self-adjointness不等於 RH，
`lambda=0` 的 Hilbert norm仍等價 local Weil positivity。

新增 `external_spectral_inputs.md` 與 G28。由 spectral theorem導出可執行的
uniform bridge：若 residual `r=(A-mu)k` 與 separation `Delta=epsilon_2-mu`
滿足每個 `eta<1/2` 皆 `lambda^eta||r||/Delta->0`，則 ground eigenfunction
transform也趨近 `Xi`，Hurwitz完成 RH。prolate leakage為
`exp(-4pi lambda^2)` 級，定量上有餘裕；實缺口是 arithmetic intertwining與
gap。另精確算出 pole remainder為 rank-two indefinite
`2Re(conj(M_+)M_-)`，排除把 small-a Dirichlet positivity-improving直接延伸
到 all-a 的捷徑。RH未證；主攻轉 ES3，不恢復 finite certificate刷批次。

續查 Connes--Consani arXiv:2106.01715 得 ES6。`E(S_0^ev)` 無條件位於 global
Weil radical，因此 interval truncation的 localized residual exact化成 outside
tail cross form；這提供 prolate leakage到 Weil residual的正確接口。同步完成
防循環修正：小 residual只給 near-zero spectral band，不保證它是 ground；
off-line zeros若存在可產生位於下方的負 directions。故需另證不預設 positivity
的 spectral-ordering／bottom-window rank-one lemma。此點已寫入 G28/HANDOFF，
禁止把 near-radical數值吻合誤作 RH進展。

hook 要求稽核 `epsilon_2-mu`。完成 ES7：interval嵌入使 localized bottom
`epsilon_1(a)` 單調不增；Suzuki arXiv:2606.09096 明證 RH 假 iff 某個
`epsilon_1(a)<0`。所以 RH 假時 bottom之後被固定負常數壓住。若 prolate
`mu,||(A-mu)k||->0` 且 ES3 ratio趨零，spectral expansion卻迫 bottom趨零。
結論：所需 gap/order estimate本身已排除 RH 假，不是技術性 denominator；
ES3降級，停止沿單一 ground-state gap投入。

轉向兩個不經 ground 的候選。其一直接證 CCM explicit `hat k_lambda` 全實零；
其二把 Suzuki 自伴延拓的 characteristic-function ratio視為 Weyl
Nevanlinna function，嘗試先在 `Im z>1/2` 證其趨近 `i xi'/xi`。後者的 shift
依賴仍未解：若需 shift趨0即重述 Weil positivity。另完成 ES9 exact推導：
prolate ODE 的 Mellin transform滿足三項 `p+/-2` recurrence；經 `E`-map後係數
成 `zeta(p)/zeta(p+/-2)`。functional equation把 critical line兩側 channel
共軛配對，提供 bilateral Hermitian transfer matrix候選；尚須加入 truncation
boundary並證 symmetrizer不含未知 `1/zeta` poles。RH未證，數值未作證明使用。

完成 ES9.1 反循環檢查。functional equation與 Gamma recurrence給
`zeta(1-p)/zeta(3-p)=-(p-1)(p-2)zeta(p)/(4pi^2 zeta(p-2))`，所以 critical
line的左右 coefficients確實共軛。配合 Mellin inversion symmetry，三項式成
`(z^2+chi+1/4)K(iz)=R+R#`，但
`R=4pi^2 lambda^2 zeta(1/2+iz)F(5/2+iz)`。因此證 `R` 為 HB 已直接排除
off-line zeta zeros；untruncated recurrence封閉為同義改寫。保留的 genuine
target只有 hard truncation boundary：求其 finite-volume determinant並從
prolate flux證 HB，不得先丟掉 boundary。RH仍未證。

進一步完成 ES10。對 hard-truncated CCM approximant交換有限和與 Mellin積分，
得 `K_lambda=sum_(n<=lambda^2)n^-p int_(n/lambda)^lambda f(x)x^(p-1)dx`。
step function `sum_(n<=lambda x)n^-p` 在 `x=n/lambda` 跳躍；代入 prolate
Green identity時 `x^(p-1)n^-p` 精確成 `lambda^(1-p)/n`。因此 arithmetic
boundary有共同 spectral phase與 scalar `1/n`，不含 naked zeta factor。
隨即完成符號修正：jump尚乘 `q(x_n)f'(x_n)`，符號不定，且來源是 test-weight
derivative而非 ODE delta potential；所以不能稱 positive rank-one，也沒有直接
2x2 J-unitarity。新 target改為 3x3 accumulated-integral／inhomogeneous
colligation 的固定 metric與 HB cone；此 positivity尚未證。

完成 ES11。分段 state `Y=(f,qf',I)` 的 generator為
`[[0,q^-1,0],[4pi^2lambda^2x^2-chi,0,0],[w_p,0,0]]`。逐項解
`A^*J+JA=0`，唯一 fixed J只是原 Sturm 2x2 flux並在 I-channel退化；故沒有
nondegenerate 3x3 local metric。加入 frozen dual port可作 4x4 symplectic
dilation，但這對任意 forcing都成立且 Hamiltonian indefinite，不能推出實零。

Masters' Nudge 問正性需逐 n或只需累積。結論：只需累積；local no-go不排除
endpoint正性，且單 n summand通常連 inversion symmetry都沒有。精確新 target
改為完整 finite sum的 companion `B_lambda` 與 de Branges kernel (ES11.4) Gram
factorization，允許 derivative jump signs在 n-sum中 telescope。外查 canonical
systems確認標準 Nevanlinna結論需要 PSD Hamiltonian；另查 Coffey 完整 Hermite
Mellin critical-zero theorem，未找到 incomplete/prolate版本。RH仍未證。

建立 ES12 cumulative Hardy座標。將 `k_lambda` inversion-symmetrize不改 Xi偶函數
的 strip limit，並取 half-support Mellin transform `E_lambda`，則完整 approximant
`F_lambda=E_lambda+E_lambda#`。充分且 uniform 的命題是
`U_lambda=E_lambda#/E_lambda` 為 inner；依 Connes--Consani scaling-Hamiltonian
criterion，等價 `P U_lambda=P U_lambda P`。這明確只要求累積正性。原始文獻亦
顯示 individual local zeta factors不是 inner。prolate concentration只能使
Hankel defect小，未提供靠近 boundary的 uniform HB margin；故不能以 leakage
數值替代 exact inner/cumulative Gram identity。

推得 ES13 dense-core closure lemma。對 boundary-unimodular `U_j`，若 weak-star
趨 U 且 Hankel defect `(1-P)U_j f` 對 dense Hardy core每個 f強趨零，matrix
elements與 uniform boundedness即證 U為 Schur multiplier；另需 boundary modulus
retention才 inner，因 weak-star極限可失去 unimodularity。不需 defect operator
norm趨零。這給 all-mode lift候選：全部 fixed-index prolate modes各自
leakage趨零，而 Hermite limits形成 dense basis。缺口是 arithmetic ratio defect
對每個 fixed n 的 exact intertwining、ratio denominator compactness與 companion
coprimality；未完成前不能把 h0/h4或有限 modes當證明。

完成 ES14 防錯接。Poisson只給 `R E=E F`，故 prolate concentration控制的是
`E(f)` 的 inversion parity defect；ES13所需則是 boundary ratio乘法器對整個
Hardy space的 Hankel defect。兩者不是同一 operator。HS7 exact even kernel已有
nonreal zeros，證明 parity defect即使為零也不蘊含 HB；因此不存在只用 prolate
leakage的 universal intertwining。若續 ES13，必須先由 ES10 arithmetic finite
sum構造 cumulative Bezoutian/score Gram主項，leakage只能作 error。RH未證。

完成 ES15 exact cumulative score。Cauchy--Riemann給
`Im(F'conj F)=-(1/2)partial_eta|F(t+i eta)|^2`；故全實零充分 target為 vertical
modulus對 eta單調。代 ES10有限和後得到 all n,m,x,y 的 (ES15.3)，kernel含
`(r+q)e^-eta(r+q)cos(t(r-q))`，只要求總和 sign，逐項不正。`eta->0` 首階
退化為 Laguerre inequality，不能由 finite degree證書替代。ES15與 A9.3/HS5
合流；下一計算是 prolate ODE雙重分部能否令完整 derivative jumps telescope。

完成 ES16 Green分部。對單一 prolate eigencomponent，truncated Mellin integral
滿足 exact 三項式 ES16.1；aggregate boundary為
`lambda^(1-p)sum q_m f'(a_m)/m-(p-1)lambda^(2-p)sum q_m f(a_m)/m^2`。
所以先前只看 derivative jump會漏掉第二項。bulk `p+/-2` shifts帶原 m^-p，
改寫會新增 m^+/-2 channels並反覆生成無限 hierarchy，沒有 3x3 closure。
同時修正：實際 h_lambda是 h0、h4兩個不同 eigenvalues的組合，score須拆四
channels。保留候選只剩利用 chi4-chi0與 zero-integral relation的 coupled
Christoffel--Darboux/Wronskian boundary cancellation；RH未證。

最新 nudge質疑 cos oscillation無法吸入 square。完成 ES17：
`cos[t(r-q)]` 精確是 `(cos tr,sin tr)` 的 Gram kernel。定義無 r 與多一個 r
的 cumulative cosine/sine vectors v,w，ES15 score就是 `v dot w`；真正 kernel
signature來自 `(r+q)e^-eta(r+q)` 的 `[[0,1],[1,0]]`，不是 t。故正確 CD target
是四 prolate channels合計後產生 ES17.2 dissipative polarization。此 relation
尚未證，數值或 t=0 sign不算。

完成 ES18 兩 eigenvalue差分稽核，並修正 differential eigenvalue記為 omega、
concentration eigenvalue記為 chi。Green identity用 omega4-omega0可重寫
04/40 cross products，但對 00/44 eigenvalue difference為零，只成恒等式。
zero-integral coefficient relation僅在一個 Mellin點，不能消去全 t,eta diagonal
score。因此有限 CD closure未成立；剩餘充分命題是 2x2 vector-valued score
matrix在上半平面負半定，或特殊 c-direction非正，與 HS9 coupled Bezoutian
完全合流。RH未證。

聯網稽核 matrix de Branges原始文獻。Mahapatra--Sarkar 2406.15194 明確以
`E_+^{-1}E_-` matrix-inner為 de Branges pair條件，positive kernel是其結果；
operator-valued 2302.06297同樣從 positive RKHS/de Branges operator出發。
所以此工具只能包裝 ES18，不能生成缺失的 positivity；full matrix negativity
更會要求 h0、h4 diagonal各自滿足 RH-level sign，應降回 special c-direction。

找到並證明新的 all-mode prolate lemma。finite Fourier正相位支由
`h_0,h_4,h_8,...` 張成；因 differential eigenvalues嚴格遞增，
`(PW-omega0)(PW-omega4)` 在此支半正定且 kernel正好 span(h0,h4)。加上
`ell^*ell`、`ell=int` 後，kernel唯一為 CCM 的 zero-integral `h_lambda`，零亦為
simple isolated auxiliary ground eigenvalue。此結構不依 Weil positivity，是真正
uniform tower theorem而非 finite moment certificate。

隨即完成防循環檢查。CvS 2511.23257 的實零 theorem需要 convolution kernel
`D(x-y)`；上述 Q 是變係數四階微分 operator。計得
`[PW,x partial_x]=-2lambda^2(partial_x^2+4pi^2x^2)`，故 quadratic spectral
polynomial的 commutator仍有 infinite-rank四階 bulk，rank-one integral項不能
消除。下一步只接受：證 hard-truncated E-map將 Q 共軛成 log-convolution正形式
加可控 boundary，或由 Q直接導出 CCM special score direction。RH仍未證。

重新讀 Connes--Consani 2106.01715 §3，發現 ES6 的必要修正。E-radical domain
是 codimension two `f(0)=hat f(0)=0`；其 prolate formula只令 phi_n(0)=0，
Fourier parity明寫 `simeq`。CCM 2025 的 h0/h4則只令 integral zero。利用
`int h_n=tau_n h_n(0)`，two-mode剩 exact value defect
`c0 h0(0)(1-tau0/tau4)`，故先前不能稱 finite candidate exact 位於 radical。

加入 h8 後得到 exact double-zero line：在 coordinates `d_n=c_nh_n(0)`，
`d=(tau4-tau8,tau8-tau0,tau0-tau4)` 同時使 sum d與 sum tau*d為零。
並證正 phase tower上的 cubic spectral polynomial
`(PW-omega0)(PW-omega4)(PW-omega8)>=0`，加兩 functional squares後 unique
kernel就是此 line。一般 r constraints對應前 r+1 same-phase modes及
`product(PW-omega4j)`；另以 positive measure
`sum h_(4j)(0)^2 delta_tau` 的 orthogonal polynomial給 uniform Lanczos/Hankel
表示。這是 constraint升階，不是 Jensen升階；J24 六階 Gaussian與此無關。

完成 full-conjugacy falsification。order-6 positivity只在 nonlocal phase支；
全空間 local PSD須平方成 order 12。更關鍵地，PW經 E/Mellin含 p+/-2 shifts，
cubic含 p+/-6；log convolution必為 multiplier，finite-rank boundary無法消除
infinite-rank bulk。故不再攻 full Q-to-CvS conjugacy，只保留 special vector
score。Burnol canonical Sonine A_a/B_a雖 HB且 zero density同 zeta主階，無 theorem
辨認 E(g_lambda)為其 kernel/limit，space membership本身也不保 real zeros。
RH未證。

聯網後新增 ES25--ES28/G31。先把 score target由全上半平面更正為 CCM真正需要的
`0<eta<1/2`。natural half-Xi companion的 Pólya cosine kernel在原點為 concave，
且 direct HB difference於 t約17變負，故該 companion封閉；計算只作路線診斷。

對 ES10 hard cutoff完成一階端點展開：所有 `log(lambda/n)` arithmetic jumps形成
explicit Dirichlet--sine polynomial B_lambda，不能只靠 outer endpoint。lambda
2/2.5/3 scan未見 eta<1/2非實根；這不算證明，但保留 uniform high-t theorem。

外查 Freedman 2606.29555，取得 exact theta second-order identity、Volterra
boundary+tail及 `kappa=(1-s-u)/(1+s+u)` contraction。完成非循環 audit：KLM kernel
在 omega為偶，shifted-Xi de Branges kernel首項則是 omega乘 Xi Bezoutian；任何
bridge在 omega->0都必給該 Bezoutian全尺寸 Gram，正是 RH-scale anti-Pick義務。
Mellin tail可匹配，incomplete-gamma prefix仍缺 z-independent joint-Gram transport。
詳見 `volterra_klm_audit.md`。RH未證，goal維持 active。

再由 ES10 endpoint polynomial導出 T3P8 strict strip-HB lemma：若
`|q|>N+log(N!)/log(lambda)`，log-derivative bound直接給 leading companion在
`0<eta<1/2` 的 HB inequality。數值 lambda=3通過只作 diagnostic，未當證明。

更強地把 T3P4 constraint tower用於 hard endpoint：前 m+3 same-phase modes除
`f(0)=int f=0` 外再消 `f^(j)(lambda),j<m`。在 rank條件下仍是 unique positive
auxiliary ground，且一次把所有 arithmetic cutoff jumps延後到 order m；high-t
首項只剩 single outer sine。新增 Dunster 1601.00699 作 endpoint-uniform input。
尚缺 endpoint-jet generalized Vandermonde full-rank與 boundary correctors保留 CCM
central limit的 rigorous error bounds。RH未證。

T3P10 隨即關閉 fixed-m rank。small-bandwidth極限的 endpoint jets是 spectral
parameter L_k的 polynomial Vandermonde；integral row pivot k=0；center values
`P_(4k)(0)` 有 strict completely-monotone integral表示，不能落在低次 polynomial
span。analytic perturbation故只留離散 exceptional lambda-set，可選任意發散序列
避開。剩 Dunster endpoint corrector的 projective-limit與定量 conditioning。RH未證。

2026-08-14：外網恢復後查核 Dunster 1601.00699 與 Platt--Trudgian 2004.09765。
後者 rigorous驗證到 `3,000,175,332,800`，但固定高度不能覆蓋 prolate bandwidth
`c->infinity` 所造成的 drifting intermediate band；已在 T3P11 明確否決以更多
VERIFIED批次取代 global theorem。

同日取得真正解析進展：從 Xi Fourier integral與
`1/(conj(w)-z)=i int_0^infty e^[i(z-conj(w))r]dr` 直接推導
`B_Xi=(4/pi) Fourier-Laplace^* K_0 Fourier-Laplace`。偶性把 lower limit `-p`
精確變成 `|p|`，常數與 Freedman K_0 完全吻合。故原始 K_0 PSD即直接證 RH，
不需 uniform omega或未知 finite-omega de Branges transport。研究焦點縮為
omega=0 normalized quotient certificate到原始 coordinate form的解析 lift/closure；
數值 KLM grids不算證明。

續查 Freedman Problem 15.15：原稿已算出 primitive Green boundary repair=0，
且 primitive trace image完成後稠密於全 `X_R`。因此 remaining lift等價
`D_q=0`／`Gamma^*Gamma<=C`／full `Q_Phi>=0`，不是例行 density。又由 VK6
boundary Fourier density可反推 K_0 positivity，故 `K_0 PSD <=> B_Xi PSD <=> RH`
（標準 real-entire Hermite--Biehler criterion下）。新成果是 exact辨識與刪除
uniform-omega假缺口；真正 continuum Gram positivity仍未證。

又把 omega=0 same-sign kernel exact 寫成 Hankel anticommutator
`K_0^(++)=(AH+HA)/4=(1/4)d(H_lambda^2)/dlambda|0`，其中
`H_lambda(s,u)=e^[lambda(s+u)]Phi(s+u)`。這證實 Freedman dilation
monotonicity就是原 positivity的 operator form。Yafaev Hankel quasi-diagonalization
形式上導出 anti-Loewner sign-kernel，但 Phi非 completely monotone、Laplace sign
object可能為 distribution，且 reflected block未處理，故尚無 sign theorem。

VK6 再回答 degree斷層：對 exact pullback逐 z,w微分，所有 Bezoutian Taylor
matrices同時成為 monomials在 K0 form中的 Gram compressions。這是一個真正
uniform-in-degree source；cubic只是一角。研究因此不恢復逐 degree certificates，
而只攻 continuum K0/D_tr positivity。

2026-08-14：聯網補查 Burnol math/0203120 與 Dimitrov 1311.0596。Burnol的
Sonine `A_a/B_a` 是正空間的結構函數，zeta只以 evaluators/quotient出現；論文
明說一般 Sonine functions可任意加零，故沒有 `Xi=structure function`。Dimitrov
把 `W(p_1,...,p_n)`、multiaffine Lee--Yang integral與 Jensen/Appell polynomials
exact等同；普通 OP recurrence/Hankel positivity不會自動升階。

同日發現 2026-08-09 Holland 2608.08682：解析證
`n^3 log^2(n+2)>=K d^5` 的 simultaneous Jensen hyperbolicity wedge。這是有效的
uniform-in-degree/shift外部成果，但 complement仍含每個 fixed n的 arbitrarily
large d，尤其 `n=0` 全塔。derivative identity只能向高 shift傳實根；反向需要
critical-value alternation，未證。已把新可行分叉記為 K0 continuum Gram、
Lee--Yang measure closure、或 wedge-to-low-shift critical-value transport；不恢復
逐 degree有限證書。RH未證，goal保持 active。

隨即證 fixed-shift極限：若 `F(X)=xi(1/2+sqrt X)`，則
`J^(d,n)(X/d)->F^(n)(X)` locally uniformly；界
`binom(d,j)/d^j<=1/j!` 給直接 dominated convergence。故僅證 `n=0` 的 all-large-d
hyperbolicity就已由 LP closure推出 RH。這確認 Holland wedge complement不是普通
asymptotic尾巴；任何進入 fixed-n large-d的成功機制都已是 RH-scale突破。

再查 Newman--Wu 1708.08820：Lee--Yang probability class在 weak convergence下
封閉，tightness會自動供應所需 variance bound與 compact-uniform mgf convergence。
因此 statistical-mechanics分叉的精確合格輸出是構造 known finite Lee--Yang/
ferromagnetic laws `mu_N=>Phi dt/intPhi`；極限步本身已關閉。現在沒有此 coupling
construction，positive quadrature或有限 moments匹配均不足。

K0 parity另有 exact swap identity。定義
`F(p,d)=1/2 int_|p|^infty yPhi(y+d)Phi(y-d)dy`；對 x,y≥0、
`p=(x+y)/2,d=(x-y)/2`，same-sign `A=F(p,d)`，reflected `B=F(d,p)`。
所以 continuum目標可指定為構造同一 feature map T及 self-adjoint contraction S，
`A=T^*T,B=T^*ST`。Gaussian中 swap退化為 S=I；Riemann尚缺 theta modular
intertwiner。此為候選全尺寸引理，不是 positivity證明。

同日把 swap 再積分成 symmetric double-tail potential `P(q,r)`，exact 得
`K_even=-P_q`, `K_odd=P_r`。若 even-power係數 `c_m(q)` 全部 completely monotone，
兩塊即是顯式 Laplace rank-one Gram和，這是 uniform-in-degree充分定理。推得
`c_1(q)=-[R(q,q)+int_q^infinity R_1(q,t)dt]/4`；再令 `q=a^2` 並分部積分，化成
`c_1(a^2)=(4a)^(-1)int_0^infinity Phi(2a+s)[Phi(s)+2(a+s)Phi'(s)]ds`。
低階浮點 probe未見反號，但 integrand會變號，尚無 theta正重排；RH仍未證。

隨即完成必要反例稽核並淘汰上述充分條件。`c_0=P0(q,q)` 及
`-c_0'=2F(sqrt q,sqrt q)` 皆嚴格正且由 theta tail得 `O_A(e^(-Aq))` 對每個 A。
非零 completely monotone函數的正 Laplace measure在某個有限 `[0,M]` 有正質量，
故必 `>=Ce^(-Mq)`；矛盾。這是 exact obstruction，不靠數值。K0B10.2 恆等式保留，
但 coefficientwise CM／獨立 Gaussian rank-one分解正式停止；需尋找跨 anisotropy
orders的 coupled Gram或 VK8 shifted-theta factorization。

接著由 K0 pullback的 triple integral得到新 scalarization：對
`A_f(r)=int Phi(t)f(r+t)dt`, `B_f(r)=int tPhi(t)f(r+t)dt`，exact 有
`Q_K0=-Re int_0^infinity B_f conjugate(A_f)/2`。score `q=-Phi'/(tPhi)` 若常數便
直接積成 boundary square（Gaussian）；Riemann用 `c=q(0)` 後只差 residual
`E_c` 的 boundary-dominated cross inequality。J5 的 q遞增只給 kernel odd sign，
不夠控制 signed f。另查 Audenaert 1008.2943：anti-Loewner kernel的 all-size
positivity等價顯式正測度表示，故若能正則化 Yafaev theta sign-symbol並證
`sigma'/sigma` anti-Loewner，可一次關 same-sign block；distribution與 reflected
contraction仍是實質缺口。

再稽核 K0B13 是否真正降階：令 `Y_c=e^(z^2/(2c))Xi`，其 Bezoutian exact為
`e^(...)[B_Xi-XiXi/(pi c)]`；rank-one項就是 Volterra boundary square，剩餘項
仍是 gauge後完整 Bezoutian。且 Phi超指數尾不可能是非退化 Gaussian與正測度卷積，
故 backward-heat object必帶 sign/distribution。score單調沒有自動產生 positivity；
K0B13只保留作 residual factorization座標。

anti-Loewner分支再做 compatibility audit：standard ordinary nowhere-zero Laplace
symbol若有 `g=sigma'/sigma` anti-Loewner，則 `g>=0` 強迫 sigma固定正號，Phi遂為
completely monotone正 Laplace transform；K0B12超指數尾立即矛盾。因此 VK11的
直接版本關閉，只剩需重新推導 kernel的 multiplicative theta regularization可能性。

續攻 residual時找到正且兩端 decaying的 first-order primitive
`R=e^(-t/2)int_(-infinity)^t e^(s/2)Phi(s)ds`，並 exact 重排成
`Q_K0=|U(0)|^2/4+||U||^2/4-Re<LV,LU>/2`。這避免了先前二階／單側 primitive的
homogeneous infinity cancellation，但仍缺 moment graph contraction。

同時測試 theta channel-pair Gram並得到解析反證：對 `m>n` 與 points `{x,-x}`，
same-sign pair exponent為 `(n^2+m^2)pi e^(2x)`，reflected interior saddle為
`2nm pi e^(2x)`；後者較慢衰減，故 odd eigenvalue最終為負。浮點 `(1,2)` pair
已在小 x清楚呈負值，只是診斷；嚴格結論來自 exponent gap `(m-n)^2`。因此 Selberg
nudge所警告的 average-to-pointwise量詞跨越在此具體發生：完整 theta sum不能拆成
逐 pair正性。

依 Selberg nudge再檢查「平均到逐點」：令 `h(s)=-logPhi(sqrt s)`；J5使 h convex。
對 `A=F(p,d),B=F(d,p)` 在 B 用 `z^2+d^2=u^2+p^2`, `udu=zdz`，兩組 squared
arguments總和相同，而 reflected spread由
`u^2p^2-z^2d^2=(p^2-d^2)(u^2-d^2)>=0` 較大。convexity遂逐 integrand給 B≤A，
嚴格證 `K_odd(x,y)>=0` 全域成立。這是新的 continuum theorem，但只為 entrywise
sign；任意 size PSD仍缺 convexity差的 coupled Gram factorization。

再將差 exact 展成 `int int [h'(c+s)-h'(c-s)]e^[-h(c+s)-h(c-s)]` 的正 path
integral。自然 Loewner lift需 `h'` operator monotone（h operator convex），但 theta
尾給 `h'(s)~pi e^(2sqrt s)/sqrt s`，而 operator-monotone函數至多線性。故此
standard all-size升階被解析排除；scalar convexity不能再加強成普通 matrix convexity。

2026-08-14 聯網後精讀 Suzuki 2206.03682v4/2606.09096v1，並聯合
Yafaev 1303.4040 稽核 L7。新推導 K0B19--23：`L` 無界，但 whole-line
cancellation exact；`1/(1/2+i xi)` 的 causal block恰給邊界 storage，使 L7 等價
`Re<P_+M_(iXi'/Xi)P_-w,P_+w><=0` on `Ran(T_Phi)`，左邊 exact是
`-2Q_K0`。bounded Nehari 延伸由稠密 range+反號必迫 block=0，故不可行。
Suzuki `Psi_omega` 只給 positivity-preserving forward Volterra semigroup；後退到
`omega=0` 不保正，且 endpoint等價 RH。新候選是 Xi-specific unbounded
graph Gram，或一個使 screw shift 可逆保正的 theta/prime invariant subcone。
RH未證，goal active；數值未被當成證明。

2026-08-14 Masters' Nudge 要求先確認 `Ran(T_Phi)` 在 H2 是否真有餘維。
K0B24 exact 稽核得否定答案：Xi multiplier injective、dense range但不閉；
`P_+Ran(T_Phi)` 在 half-line L2/Paley--Wiener H2 稠密。故 L7 的
common-range restriction沒有降階，只是 `||hat w/Xi||_2` graph topology，
而拉回 operator就是 `-2K0`。這修正了先前可能過度樂觀的用語。

繼續稽核 parity entrywise positivity 是否來自 1D Green kernel。K0B25 證兩個
parity kernels 在 interior diagonal real analytic；任意 finite-order local differential
Green inverse都必產生 delta/derivative jump，故 Sturm--Liouville route關閉。K0B26
再證 shifted graph same-preimage transfer 對任意 Xi 都 tautologically unitary；要求
output Hardy causality則 all-shift ratio `Xi(z+i nu)/Xi(z+i omega)` 為 Schur，等價 RH。
剩餘合格目標只能是不使用 `1/Xi` 的 theta/prime local cone，或
nonlocal/infinite-order positive realization。RH未證，goal active。

## 2026-08-15：外部 PF/Hankel 輸入與 K0B27--29

- goal保持 active；未恢復任何逐 degree moment certificate。
- Schoenberg classification解析排除 raw classical Phi 的 PF∞；另核對
  arXiv:2602.20313v2 的 certified PF5 failure，只作 obstruction。
- 下載並逐式稽核 arXiv:2602.01248v1 source。發現 positive-sum closure lemma錯誤，
  以兩個 translated Gaussians給 exact negative 2x2 minor；該稿 centered symmetry
  亦與 Jacobi公式直接矛盾。
- 對其特殊 logarithmic kernel算得 exact transform
  `2C alpha^(-q)Gamma(q)zeta(2q)`；PF bridge沒有消除 zeta。
- 推導 de Bruijn flow下 Bezoutian exact四維 radial backward-heat PDE，並用
  `F_t=z^2+1-2t` exact否證 generic downward PSD preservation。
- 新保留介面：theta prekernel的 prime Euler--Volterra factorization K0B29；缺口是
  含 Archimedean completion的 common K0 storage，而非 pointwise positivity。

- K0B30 將該候選推到 completion gauge：prime weights成為 `p^-1/2`。在
  `L2(e^-2sigma x dx)` 上 partial product norm包含 Euler product，僅於
  `sigma>1/4` bounded，critical `sigma=0`發散。ordinary positive common energy
  因而關閉；只剩 signed prime--gamma telescoping，與 Weil square缺口接合。

- K0B31 推導 Bezoutian exact product rule，確認 positive real-entire factor products
  是真正 all-degree機制。核對 Shi 1502.06844 後發現其 approximants沒有 family
  收斂到 Riemann kernel/transform的 theorem，只匹配 tail與有限 central jets；故
  不能用 LP closure傳遞實零性。

- Selberg nudge要求檢查跨 `sigma=1/4` 的 uniformity。K0B32 exact算出 Shi第一族
  的 Riemann-sum limit；共同 envelope甚至給任意 exponential-weighted L1 convergence，
  但極限有 `2beta/a` tail correction，並非 Riemann Phi。新增 L10：若能構造
  `R>1/2` weighted-L1 convergence的真正 LP exhaustion，Hurwitz即證 RH。

- Masters' Nudge 反向量詞檢查成立：RH真時可取 `K_N=Phi`，故 L10存在性與 RH等價，
  已降級為驗收準則，並停止把更多 LP approximants當有限批次刷證書。
- 推導 K0B33 exact Weyl symbol：`sigma_K0(p,xi)=1/2 int_|p|^inf yW_Phi(y,xi)dy`。
  Hudson theorem解析排除 raw `W_Phi>=0`；正 Weyl symbol也不保 operator positivity。
- 將完整 theta雙和辨識成 rectangular 2D lattice theta，並推得 K0B34.3--4 的
  scale--shape differential completion與 boundary/bulk分解。這保留跨 channel
  cancellation，但尚缺 theta-specific anti-Wick/Kraus/star-square identity。
- 進一步由 `(y,v)->(t,u)` 得 K0B35：`int e^(2sy)W_Phi dy` exact等於
  `|xi_R(1/2+s+i xi)|^2`，而 tail symbol的 center Laplace transform等於其導數
  除 `8s`。Lagarias/Sondow--Dumitrescu criterion證明這些 scalar moments全正已與
  RH等價；故 modular/Mellin positivity不是降階，只保留 operator-level CP分解。
- 稽核 2026-06-01 theta-kernel preprint：two-sine compensation identity正確地重寫
  horizontal monotonicity，但 final Problem 1仍與 RH等價；其 log-concavity proof有
  未證全域單調與非完整 tail enclosure。
- 新增 K0B36 exact反例 `K=(3/2)G+[G(.-1)+G(.+1)]/2`, `G=e^(-x^2/16)`。
  它 strict log-concave且 J5型 radial score strict increasing，但 Fourier factor
  `3/2+cos z` 有 `pi +/- i arcosh(3/2)` 非實零。故 scalar score/positive amplitudes
  絕非 uniform-in-degree機制。
- 稽核 Planat 202606.1957：除明列 pre-crest與global bridge open外，其 ray-curvature
  Proposition在 `a->0` 與 `H=-2cPhi(0)^2a+O(a^3)` 直接矛盾，不能輸入。
- K0B36反例再解析加強：它亦滿足 `p'>0` 及 `R=(p^2-p')'>0` 全域，故 Planat
  Riccati scalar條件即使本身成立也不控制實零；必須有 theta-specific operator coupling。
- 稽核 Polson SSRN 6986418：摘要已明認 signed mixing measure及 RH-equivalent
  complete-monotonicity缺口；完整 normalized Xi因 Hardy real zeros亦不可能是 ID
  characteristic function。GGC路與 signed prime--gamma gap相同。
- 將完整 `(m,n!=0)` theta提升到 upper half-plane，逐項推得 K0B37
  `(D_y^2-1)H=4Delta_zH`。在 rectangular Fermi coordinates，completion exact為
  `Phi(y+d)Phi(y-d)=1/4(H_rrrr+2H_rr-3H_ss)|_(r=0)`。
- 這是首個明確排除 Gaussian-mixture反例的 theta-specific interface，但 normal
  stress為 hyperbolic `N^2-partial_s^2`，尚無正 energy/Kraus boundary identity。
- 稽核 Holland 2608.08682 原始 TeX：正規化 `gamma(n)=n!M_n/(2n)!` 正確；其
  Laguerre/Jacobi/finite-free model exact匹配 `R_0,...,R_4`，五階 multiplier stability
  真正無條件證明 `n^3log^2(n+2)>=Kd^5` 的 uniform Jensen hyperbolicity。
- 這不是 RH bridge：作者明言沒有 converse；導數只把 `(d+1,n)` 送到 `(d,n+1)`，
  無法降 shift 至 n=0，楔形補集仍無窮。
- 下載並核實 MMP 2309.10970v3：finite-free乘法卷積只 forward保持實根/交錯/lmesh；
  相異正根 polynomial 的 convolution inverse不可能仍全正根。因此不能對 Holland
  comparison model做 positive deconvolution。新增 L11/G48，停止 fixed-order擴張。
- 由 tilted moment identity導出 exact raw multiplier
  `M_d(Y)=E_n(1+U^2Y)^d`；`disc M_2=-4Var_n(U^2)<0`，故 Laguerre正平均不是
  finite-free正根factor，不能作 all-order closure。
- 建立 exact positive-coefficient reverse-shift反例
  `P=x^4+8x^3+22x^2+24x+12`：`P'=4(x+1)(x+2)(x+3)`，所有高階導數實根，
  但 P 在全部臨界點為正且無實根。generic inverse Rolle/Jensen shift徹底關閉。
- 下載並逐行稽核 claimed proof Shi 1706.08868。核心 equations 2913--2964 將
  `sum_(j=0)^m y^(2j)/(2j)!` 補 odd零項後錯寫成只到 m 的全次和；正確應到 2m。
  m=1 即遺失 y^2/2。故後續 hypergeometric tail、7n^3 boundary asymptotics與
  U/V interlacing皆不是原 approximant的 identity；不能輸入 L10。

## 2026-08-15：L12 的 Abel mixing reduction

- 核對 KPS Theorem 4.4 proof：1-separation配合 Bernstein-gamma recurrence把
  `1/W_varphi` 延成實零 entire function，再以 Laguerre theorem一次推出全部 zeros實。
- natural ratio中同一 `M` 位於 `2z-2,2z`，所以其零點所致 singularities algebraically
  相差 1；但實軸性、simple ordering與 Pick性仍未證。Taylor負奇數 poles在 ratio相消。
- 推導 J69：由 `Phi'<0` 對 normalized Xi density作右 Abel反演，無條件構造正
  mixing law `I`，使 `D=sqrt(I)·2cosTheta`；完整 Mellin recurrence即
  `varphi_nat`。這關閉正 representing measure，非 RH證明。
- 下載/核對 Hirsch--Yor 1309.7801：complete Bernstein perpetuity必使 `log I`
  multiplicatively infinitely divisible。新增必要 target `K_I''` completely monotone；
  尚缺 converse與 Pick/1-separation。
- continuation與 log-I cumulant數值 probes未見早期反例；只作候選淘汰，未當證明。
- 稽核 Durán 2026 orthogonal-combination theorem與 Romik Xi expansions：前者只在
  fixed width K、fixed coefficients下 eventually實根；Xi truncation有 K=N，故不給
  all-degree closure。記為 ES64，不轉回逐 truncation刷證書。
- 由 Hirsch--Yor Mellin Levy公式導出 J70：`4(log M)''(2s)` 的 inverse Laplace
  measure若存在，complete-Bernstein必要且必須夾在 Fermi density
  `x/(e^(x/2)+1)` 與 Bose upper envelope `x/[2sinh(x/2)]` 之間。這是新的
  uniform target；尚缺 theta representation與 converse。
- 條件式展開 J71：負奇 Taylor poles恰產生 J70 Bose upper envelope；Mellin zeros
  以 `-x exp(rho x/2)` 扣除。故 natural Pick route核心是新的 Mellin-zero
  realness/spacing theorem，不是第一差分或 positive mixing自動推出。

## 2026-08-15：J72 certified Mellin zero 與 L12 路線關閉

- 先用兩個獨立 continuation evaluator定位候選；高精度 Taylor+tail evaluation給
  `z0=-16.988364513985116996...+5.875534137135168256...i`。此階段只當診斷。
- 改用 20 次分部積分 identity，避開負整數附近 Taylor相消；安裝 python-flint，
  對 `v in [-100,log4]`、前 20 theta modes作 outward-rounded Arb complex-ball積分。
- 以 Cauchy coefficient bound
  `|f^(20)|/20! <=3|C|e^(au-Q)(4Q)^20` 控制三類遺漏：`v<-100`、`u>4`、
  `n>=21`。root box 對 `M,M',M''` 的共同 allowance保守取 `1e-100`。
- Rouché certificate 得
  `|M(z0)|<3.182e-21`、`|M'(z0)|>0.7717`、
  `sup_disk |M''|<1.933`，半徑 `1e-18` 的 margin `>7.68e-19`；故圓內恰有
  一個 nonreal zero。另證 `|M(z0-2)|>2.4058`，排除 ratio numerator cancellation。
- 結論：`varphi_nat(s)=2(2s-1)M(2s-2)/M(2s)` 在 upper half-plane有真 pole，
  不可能是 Pick/complete Bernstein。這嚴格關閉 natural L12 route，不影響 RH。
  詳細證書見 `mellin_zero_certificate.md` 與
  `experiments/certify_mellin_zero_arb.py`。
- 依最新 Selberg nudge 同步修正 J70--71：sandwich原本是 measure domination；
  轉成逐點 `A(x)` 需另證 absolute continuity與 termwise inverse-Laplace，不能把
  積分量詞自動升成解析 density。由於 J72已先關閉 natural route，此缺口留作
  方法論警告，不再優先投入。

## 2026-08-15：J73 Carlson uniqueness 關閉全部 KPS 插值

- 對任何通過 J68 data的 KPS候選，Bernstein-gamma recurrence exact給
  `1/W_varphi(n+1)=n!m_n/[(2n)!m0]`；這正是
  `F_nat(z)=Gamma(z)M(2z-2)/[Gamma(2z-1)M0]` 的整數值。
- duplication formula顯示 `F_nat` entire：`1/Gamma(z-1/2)` 恰消去 `M(2z-2)`
  的全部預定 Mellin poles。
- 核對 Patie--Savov 1604.05960 exact Stirling formula。其 universal bound
  `0<=A_phi(a+ib)<=pi|b|/2` 證 `1/W_phi` 是右半平面 exponential type，垂直
  indicators皆至多 `pi/2`。J69 moment growth、Holder、gamma recurrence對
  `F_nat` 給同一界。
- Carlson indicator theorem遂令兩個插值全域相等。J72 nonreal Mellin zero使
  `F_nat(1+rho/2)=0`，與 KPS 1-separation所給的全負實 simple zeros矛盾。
- 結論：不存在任何 eligible KPS Bernstein--Pick interpolant；不只是 natural
  ratio失敗。這是 uniform route closure，不是 RH證明。詳見
  `carlson_kps_uniqueness.md`。
- Selberg nudge質疑 Carlson type是否只對特定成員成立。反查 KPS定義與
  Patie--Savov Theorems 2.9--2.10後，此疑慮排除：`B_(P1)` 明確是 Bernstein class
  子集，而 exact Stirling identity對任意 Bernstein `phi`、全部 `a>0,b in R`成立；
  error在 `a>=1` uniform。Levy--Khintchine又直接給
  `|phi(z)|<=C_phi(1+|z|)`，故每個一般候選都具有所需半平面 exponential type。

## 2026-08-15：K0B39--40 automorphic/Wigner 稽核

- stress factor `(2mn)^2` exact annihilate `m=0` 或 `n=0` axes，故 K0B37 的
  cross theta可換成 full nonzero lattice theta而不改 target。其 Mellin transform
  是 Epstein zeta/Eisenstein series，首次取得真正 automorphic spectral interface。
- full hyperbolic Haar norm使 `N^2-partial_s^2=N^*N+(partial_s)^*partial_s>=0`，
  但 target是指定 rectangular geodesic的 point trace，不是 Haar quadratic form。
- stress trace的 s-Fourier transform exact為 `4W_Phi(y,-k)`。Hudson theorem遂排除
  raw trace為 positive-definite：非 Gaussian `Phi` 的 Wigner函數必換號。
- Kelmer--Yu second-moment theorem只給全部 lattices的 Haar square。live target縮成
  test-dependent automorphic lift，使 `Q_K0(f)` exact成 Rankin--Selberg/Haar norm。
- Lagarias--Suzuki shift theorem亦已稽核：已知 zero strip只容許不可縮 half-shift；
  `T=1` 是 Weng zeta，`T->infinity` 不局部一致收斂到 xi，不能做 LP exhaustion。
- K0B41 排除標準 full-orbit coherent/Rallis lift：其 Haar frame operator與不可約
  representation對易，故是 scalar；Riemann `K_0` 為非零 Hilbert--Schmidt compact
  operator。成功 lift必須非等變且顯式處理 cone boundary；抽象 square root是循環。
- 稽核 Suzuki 2606.09096：Theorem 5確實無條件產生 finite-interval entire real-zero
  family `W(a,theta;z)`，只需選 `lambda<lambda_a`；這是合格全階候選。
- 但 arithmetic limit的 Fourier推導先假設 RH以取 `lambda=0`。若無條件可選
  `lambda(a)->0` 且仍 `<lambda_a`，由 `lambda_a` 的 domain-monotonicity已推出 RH。
- 原 Corollary 6 的 compact convergence量詞亦須修正：`z^2xi/xi'` meromorphic，
  不可能是 entire functions在 C所有 compact上的普通一致極限。需 nowhere-zero
  holomorphic normalization及 pole-free compacta/spherical convergence。記為 K0B42/G54。
- 下載並逐頁稽核 Zenodo 19546495 claimed RH proof。其 Theorem 2把 CCM auxiliary
  self-adjoint determinant zeros誤寫成任意 test的 Weil-form square-sum spectrum。
  CCM 的正 form其實是 `QW_N-epsilon_N I`；claimed identity遺漏
  `epsilon_N||g||^2`，而 `epsilon_N>=0`正是所求 endpoint。
- compact support雖使 prime local terms有限/穩定，不能補上述 sign，也不能替代 CCM
  determinant convergence。故該 claim無效；詳見 ES69與
  `external_claim_audit_vicere.md`。

## 2026-08-15：最新 all-rank Toeplitz 外部輸入與量詞稽核

- 下載並讀取 arXiv:2607.16795 原始 TeX。其 theorem確為同時所有 rank 的 wedge：
  `D_(r,k)>0` when `k>=10^18r^3`；不是逐 degree batch。
- 稽核 q-Pascal dilation後確認它只控制 fixed `q_k,r` 的 q-Vandermonde model；actual
  remainder small parameter為 `r^3/k`，沒有 inward shift semigroup。因此臨界
  `k=O(r)` 完全未覆蓋。
- 新增 exact Desnanot--Jacobi/Toda identity；它把升 rank改寫為 determinant-row
  log-concavity，但所需 log-concavity恰等價下一 rank positivity，故沒有隱藏歸納。
- 新增 rectangular Jacobi--Trudi duality：fixed shift k的所有 rank determinant等於
  reciprocal-Xi coefficients的 fixed `k x k` moving determinant。這是真 all-rank
  reduction；fixed certified poles可給 eventual proof，但 growing k的 real-pole、
  Vandermonde conditioning與tail uniformity仍是 RH-critical balanced cone。
- 下載稽核 arXiv:2608.11520。其 contour Hankel flow在 crossing間只是 congruence；
  nonreal conjugate pair crossing產生 signature `(1,1)` indefinite jump。因此 full
  PSD等價排除 off-axis zeros，沒有獨立 arithmetic positivity input。
- degree 3不但沒有 Toda invariant，也不等於 Toeplitz rank 3；維持獨立成果分類，
  不恢復 finite certificates。詳見 `toeplitz_uniform_route.md`、ES70--71、G55。

- 續下載 arXiv:2607.02828v2 全 source/ancillary。其 finite dictionary經直接
  autocorrelation計算可加強成 exact `g_v(z)=L F_v(z)F_v(-z)`；real-axis
  zero contributions為 squares，off-axis quartet為不定 polarization。
- strict total positivity只正化 post-band archimedean tail；完整 matrix仍有
  head、signed primes與pole。source quotient降維不給 sign，cutoff diagnostics不作證明。
- full matrix是 integer-node Loewner divided differences，但單 lattice uniqueness在
  type `2pi` exact失敗：`sin^2(pi z)h(z)`保留所有 values/derivatives。故需
  complete-source Gram或非循環 all-boundary-phase theorem。記為 ES72/G56，詳見
  `finite_weil_dictionary_audit.md`。
- 將 finite prime block精確重寫為
  `sum w_q||f-S_(log q/L)f||^2-2S_c||f||^2`，確認它只是既有 W7 uniform
  coercivity 的有限帶版本。另證 spectral-type no-go：正 Borel translation-
  difference mixture只產生 absolutely continuous multiplier；Hardy theorem已
  無條件給 critical-line zeros，其 boundary distribution含正 Dirac atoms，off-line
  zeros只給局部 smooth項。因此普通正 shift
  measure completion 已關閉；共同 Gram 必須走 singular/compressed operator。
- 依 Masters' Nudge／Selberg lens修正 W6 的邏輯強度：pure-point obstruction不需
  先假設或推出 RH，Hardy 的無條件臨界線零點已足夠。
- 導出 T7 全階 identity：反覆 integration by parts把一側 Toeplitz boundary也 exact
  編入 `Phi^(2i)` moment matrix，再由 Andreief得到 derivative determinant乘正
  Vandermonde的積分。這不是 finite-degree certificate。
- 最直接的 pointwise-TP closure被 rigorously否證：`r=3`,
  `u=(.05,.10,.16)` 時 determinant enclosure全負。certificate：
  `experiments/verify_phi_even_derivative_kernel_failure.py`。T7只保留可能的 global
  symmetrization/cancellation，不宣稱 positivity。
- 稽核 Polson SSRN 6992163：integer-square `S2,C2` Thorin clocks無條件為正，但
  Xi Wald-dual measure被定義為 folded zeros `sum delta_(rho(1-rho))`；其正實支撐
  正是 RH equivalent open clause。故 Barnes-beta字典沒有從 theta/primes產生所需
  sign，記為 ES74。
- 構造 order-`1/2` exact反例 `G_A=cosh(sqrt z)+A` (`A>1`)。它有明確 nonreal
  zeros，但除常數項外與 PF-infinity 的 `cosh(sqrt z)` 完全同係數，因此所有
  `k>=r` consecutive minors仍 strict positive。這證明 ES70 的 tail wedge即使
  強化至全 tail cone也不可能單獨推出 RH；真正缺口是 uniform growing head cone
  `k<r` 的 Xi-specific reverse transport。一般結論由 Schur specialization嚴格
  證成；`experiments/verify_tail_cone_counterexample.py` 只作小範圍 exact rational
  sanity check，不作證明。記為 T6/G57。
- 稽核 arXiv:2607.24830v2：其 R2 theorem只處理 prime-free archimedean head；FEM
  lowest eigenvalue是 true infimum的 upper bound，正計算值不給正下界，且 `a>=0.6`
  已 below resolution。R6 proof明示先假設 RH。因此不補 Suzuki endpoint，數值結果
  不作證明；記為 ES73。
- 依 Selberg lens 稽核 T7 的 theta 對合：標準 `u->-u` 保持兩個 determinants、
  測度與 `u^2` Vandermonde；permutation亦同時翻轉兩 determinant。故負 patch的
  整個 signed-permutation orbit仍為負，普通 modular involution不能消去 G58。
  記為 T8/G59。
- 聯網稽核 Schatz 68頁 backward-parabolic RH稿。精確 flow
  `E_t=z^2+1-2t` 直接否證 collision bridge；另定位 WPT root-branch錯誤及
  Gronwall常數在碰撞因 zero speed發散的量詞錯誤。記為 ES75/G60，完整分析在
  `external_claim_audit_schatz.md`。
- 發現並稽核另一個全階重排 T9：將 T7 determinants的 derivatives全部分部積分到
  monomial Vandermonde，boundary exact為零。但 `A_2V_(2,1)(1,4)=-130`，故
  derivative-principle/Capelli pointwise square也失敗；只留下特殊 Phi product
  measure的 uniform integrated positivity，記為 G61。
- 稽核 Förster--Kieburg--Kösters Pólya-ensemble分類：保留 `x=u^2` Jacobian後，
  正確參數為 `nu=-1/2,omega=x^-1/2 Phi(sqrt x)`；所以 T7 local integrand正是標準 derivative-type
  matrix density。rank-3負 enclosure因此排除整個 local Pólya-ensemble/convolution
  包裝；記為 ES76/T10/G62。
- 從 T7/T10抽出未被局部反例排除的 global target T11：只把 signed joint density沿
  `tau=prod u_l^2` pushforward。其 moments exact為
  `r!prod_j[2(k+j)]!D_(r,k)`，故 `nu_r>=0` for all r會一次證全部 shifts。
  derivative-principle文獻沒有此結論，因它先假設 positive matrix density。
- 僅作策略反例篩選：double quadrature下 `r<=8,k<=29` 的上述 normalized moments，
  Hankel size至 6皆呈正；沒有找到反例。此結果明確不作證明、不作 positivity宣稱，
  只表示 T11暫列 live，記為 G63。
- 將 T11 product-level pushforward改寫為 exact一維 convolution determinant。
  若 `u_l=e^(y_l),S=sum y_l` 且
  `f_(i,j)(y)=e^((2j+1)y)Phi^(2i)(e^y)`，則
  `g_r(S)=r!det_*[f_(i,j)](S)`，Fourier側為普通 matrix determinant，且
  `dnu_r/dt=g_r(log(t)/2)/(2t)`。記為 T12/G64。
- 這個公式首次能直接篩 pointwise pushforward sign。三個 windows與 1024--4096
  grids穩定得到 `g_7(-7.65)約-4.2454e21`、`g_8(-6.90)約-7.7170e33`。
  另以 60-digit、自寫 radix-2 FFT與 determinant交叉核對，256點仍分別為
  `-4.24520596520488759e21`、`-7.71321270629148298e33`。這是很強的反例訊號，
  但尚未 enclosure truncation/discretization誤差，故不得稱嚴格反例。
- 策略決定：T11不再當作 live positivity conjecture，也不再增加 moment/Hankel
  VERIFIED batches。只允許以 interval arithmetic封閉一個負值；uniform主線轉回
  能直接作用於所有 degree的 complete prime--gamma spectral/全正性結構。
- T12負訊號已升為 rigorous T13/G65。對
  `F_(i,j)(s)=int u^(2j-s)Phi^(2i)(u)du` 取最右 `s=1` pole；分部積分把 residue
  exact化成只含 `Phi^(2m)(0)` 與奇 moments `int u^pPhi` 的 matrix `B`。
- `experiments/certify_t11_asymptotic_obstruction.py` 以 192-bit Arb、10000個
  exact rational midpoint cells、interval-enclosed二階 midpoint餘項及解析 theta/u尾界證
  `det B_7 in [-3.156096567895524060757e21,`
  `-2.883510345549506883157e21]`。所以 `g_7(S)<0` 於充分負 S，T11嚴格為假。
  這不是 RH反例：只是否證 signed determinant density沿 product pushforward後必正。
- 外部 ES70 重新下載稽核：arXiv source tar實際只有 `main.tex` 與
  `00README.json`，沒有文中聲稱的四個 ancillary modules及 36 tests。因此 q-Pascal
  algebra可由正文獨立驗證，但 Gate A/C 的 computer-assisted constants目前不可重現，
  不把 `k>=10^18r^3` wedge當成已重跑 certificate。
- Masters' Nudge指出原 T13 contour-asymptotic未展開隱含常數。已改成完全實變證明：
  permutation expansion每項只有一個最慢 `e^S` factor，將其餘 convolution吸收到
  `e^-x h(x) in L1`，dominated convergence直接給
  `lim_(S->-infinity)e^-S g_r(S)=r!det(B)`。因此 C7嚴格負確實推出充分負 S的整段
  density負，不再依賴未證 remainder。
- 聯網讀取 Dimitrov 1311.0596。其 all-n Wronskian/Lee--Yang theorem由 Leclerc
  identity exact退回 Appell/Jensen與 Turán determinants；不是從 positive measure
  推出 sign的升階 theorem。polarized double integral含 `(t-s)^2` 乘隨 n與 `x`
  旋轉的 complex powers，log-concavity不提供點態正性。記為 ES78/G66。
- Lee--Yang路只保留可驗收的 weak-limit接口：必須顯式給每個已知 ferromagnetic
  `mu_N` 並證整個 laws收斂至 normalized Xi kernel。有限 moments/Wronskians不恢復。
- 找到符合 W6 spectral-type要求的 prime Bohr/Riesz boundary realization。normalized
  critical Euler Hardy products norm恆 1但 weak趨 0；其 squared densities卻趨向對
  Haar singular的 product measure `otimes_p P_(p^-1/2)dm_p`。
- 單 prime exact有 `|D|log P_a=P_a-1`，沿 prime Kronecker flow正好產生完整
  von Mangoldt prime-power source。fractional ground-state transform進一步分解
  `P_a-1=2(|D|sqrt(P_a))/sqrt(P_a)+C_a`，`C_a>=0`、`C_a=a^2+O(a^3)`。
  原先把這說成「Gram加 Bregman debt」不完整：精確 ground-state identity還留下每個
  prime一份 `-2<H,|D|H>` kinetic debt，而 Weil multiplier沒有此 kinetic term。
- 以 digamma series完成 Archimedean analogue。置 `b_n=2n+1/2`、
  `q_N(t)=prod_(n<=N)(b_n^2+t^2)`，則
  `c_N+|D|log q_N -> Re psi(1/4+it/2)-log pi`；與 finite prime product合成
  `c_N+|D|log(q_N/P_P)`。這核對了 gamma/prime相對符號，但 nonlinear chain rule仍
  引入 absent kinetic form，divergent `c_N`也必須和 pole/global principal value共同取極限。
- Blaschke稽核再封閉 local shortcut：右半平面 zero `rho=delta+i gamma` 的 factor邊界
  modulus恆 1，actual normal derivative卻為
  `-2delta/[delta^2+(t-gamma)^2]`。因此只由 completed boundary modulus作 DtN outer
  extension會漏掉恰為 RH內容的 interior-zero項。Connes--Consani 1910.14368亦證局部
  factor ratio雖邊界 modulus 1卻非 inner，single-place inequality失敗，global Poisson
  normalization不可省。G67的 local Bregman cancellation版本關閉；singular Riesz source
  只保留作 global adelic compression的接口。
- 下載並核對 Connes--Consani 2006.13771 更新原始 TeX。其嚴格 theorem在
  `supp(g) subset [2^-1/2,2^1/2]`、兩個 Fourier evaluation歸零時，證
  `W_infinity(g*g*)>=Tr(vartheta(g)S vartheta(g)^*)>=0`；這提供真正 Sonin projection
  storage，但 support刻意避開 prime 2。finite-place推廣只被提出，未證。
- 再核對 CCM 2310.18423 與 2403.01247。finite `S` 的 determinate cyclic measure
  `|E_S|^2dt` 每個 prime factor就是 `P_(p^-1/2)/(1-p^-1)`，所以 G67 Riesz measure
  是 semilocal spectral measure的 prime部分。`theta_S` 雖把 Sonin spaces互相同構，
  dual norm distortion multiplier為 `prod|1-p^-1/2e^(-itlogp)|^2`。Kronecker與 prime
  logs有理獨立給 ambient condition number exact為
  `prod(1+p^-1/2)/(1-p^-1/2)->infinity`。故 stability沒有 uniform all-prime limit。
- 記 G68/B9：唯一合格 semilocal升級是對每個 support cutoff q直接證 finite-place Weil
  form支配 semilocal Sonin positive trace。這是 all-test theorem而非 finite moment batch；
  現有 Jacobi/prolate construction尚未給 comparison inequality。
- 核對 Burnol math/9901051 原始 TeX。`Q_p` unramified channel的 positive time-delay
  multiplier exact為 `(logp)P_(p^-1/2)(tlogp)`，而 local Weil conductor滿足
  `H_p+T_p=(logp)I`。這正好重現 B3/W5 的 wrong sign。explicit formula藉 Tate vector
  的一維 odd grading取 supertrace；所以 local positive scattering不能直接相加成 global norm。
  新的 G69 target是由 Poisson/rational-lattice complex配對或 quotient odd local directions，
  再把 local supertrace總和升成 positive cohomological trace。
- 下載稽核 Connes--Consani 2602.15941。新稿把 Riemann adele sector建成 rooted/metrized
  rank-1 divisor Picard monoid，乘法 exact對應 tensor product，explicit formula解釋成
  periodic-orbit Lefschetz trace；這提供 global coupling geometry。全文卻沒有 degree-zero
  intersection pairing、Hodge-index或 positivity theorem，semilocal段仍為既有 signed cutoff
  trace。記 G70/B11：必須另構造 relative cohomological pairing並證 Hodge sign，不能由幾何
  命名直接推出 Weil positivity。

- 稽核 semilocal maps：\(\theta_S^*\eta_S=I\) 與 scaling intertwining 給出
  uniform-in-\(S\) cross pairing，但 Euler factors 也完全相消，無法恢復 prime
  Weil distribution。same-side pairing 保留 primes，condition number 卻隨
  \(S\) 發散。記 G71/B12，關閉 primal--dual uniformity 捷徑，並直接回應
  nudge 的 \(\kappa\) 警告。
- 導出全階 identity
  \(T_{1/P_p}-T_{P_p}^{-1}=(p-1)^{-1}P_{[0,\log p]}\ge0\)。它不依 degree，
  但 trace mass \(\log p/(p-1)\) 無法對 primes 求和。gamma 與 prime delays
  在 finite truncation 中又同號為負。記 G72/B13--B14；後續只研究 joint
  renormalized contraction/determinant，不再刷有限 degree 證書。

- 下載並逐式核對 Connes--Consani arXiv:2008.10974。其 quasi-inner theorem對
  每個 finite prime set給 compact off-diagonal、Sonin kernel與 injective升階；
  但 block identity顯示 projection difference同時含 \(-C^*C\) 與 \(B^*B\)，
  full PSD等價於真正 inner。live target遂收緊為受 support/pole constraints限制的
  weighted defect domination，記 G73/B15/ES84。
- 同一 source在 \(m\) primes只給 characteristic values
  \(O(n^{-1/(2m)})\)，沒有 fixed Schatten class；一般 regularized determinant
  product又有無正號的 mixed-trace anomaly。核對 Burnol math/0112254 後確認
  adelic incoming/outgoing orthogonality本身等價於 abelian RH，co-Poisson只給
  functional equation。記 G74/B16--17/ES85。

- B13 defects彼此 commuting，故可完成 all-prime scalar renormalization：扣除
  \(A(q)I\) 後，對每個 compact time-support exact穩定為
  \(-\sum_{p<e^x}(p-1)^{-1}\) 的 multiplication operator。記 G75/B18。
  此為嚴格全階結構；其負號顯示仍需 gamma/pole跨-place domination，不能當證明。

- 對 G75做 translation stress test。\(\phi=(\partial_x^2-1/4)\psi\) 自動滿足
  兩個 pole constraints；平移不改 gamma Fourier-multiplier form，卻使 prime
  staircase expectation至少按 \(A(e^R)\) 發散。記 G76/B19：固定 gamma/pole
  storage無法支配 prime residual，必須有 \(F\)-dependent cross-place coupling。

- 由 quasi-inner unitary的 polar decomposition抽出 exact all-size identity：
  \(B^*B=P_{\ker D}+E\)、\(CC^*=P_{\ker D^*}+VEV^*\)。但再稽核發現 actual
  scaling weight不與 Hardy projection交換，不能把 weighted trace縮成單一 polar
  commutator；依 nudge「trace吸收不等於 operator不等式」撤回該升格，記 G77/B20。
- 保留 cross blocks後導出完整 cocycle：
  \(Tr(M_f^*(U^*PU-P)M_f)=\mathcal J(uf)-\mathcal J(f)\)，其中 \(\mathcal J\)
  是兩方向 Hankel Hilbert--Schmidt energies之差。local-sum所需為 restricted
  trace monotonicity，不是 operator sign；generic Blaschke/quasi-inner不保它。
  記 G78/B21，後續只攻 actual Poisson arithmetic。

- 將 Hankel cocycle Fourier反演：\(\mathcal J(f)=(2\pi)^{-1}\int x|h|^2\)，
  所以 semilocal Weil sign exact是 scattering前後第一 time moment的 restricted
  單調性，亦等於 phase-derivative平均。記 G79/B22；明確維持 trace層級，拒絕
  升格為 operator causality/positivity。

- 聯網輸入 Rodgers 2608.12315 解析否證 Montgomery--Vaughan weighted Hilbert
  inequality 的 universal 常數 `pi`；`>pi` 來自 dense half-line與 isolated
  endpoint的 rank-one coupling。這封閉 spacing-only臨界吸收，但不直接反駁
  pole-neutral arithmetic subspace。
- Burnol 1008.0617 將兩個 pole constraints精確化：support `[-x,x]` 上它們就是
  `exp(+-y/2)` 的 orthogonal complement，Gram matrix與 projection均顯式（B23）。
- 由 local Euler phase與 Plancherel導出 B24：prime項是全部 `n<exp(2x)` 的
  von-Mangoldt autocorrelation sum；兩個 pole moments容許同時減去 `dt` 與
  `dt/t`，exact residual為 `dpsi(t)-dt-dt/t`。未把 PNT數值或誤差界當成 sign
  proof；live target是此 discrepancy加 archimedean項在 B23 compression上的
  uniform inertia／正性定理。

- 將 uniform sign寫成 B25 constrained-inertia公式：合格的升階機制是證
  unrestricted Toeplitz form負指標恰為 2，並證兩個 pole evaluation的 2-by-2
  resolvent Weyl matrix負定。一般 Krein--Langer結果的前提已含所需
  Schur/negative-square性，不能循環套用。
- Laplace transform重驗 B24：centered prime measure給
  -zeta'/zeta-1/(z-1)-1/z，加入 gamma exact為 -xi'/xi。endpoint cancellation
  只隔離而未消除 zero obstruction；沒有宣稱已證 RH。

- 對照 Suzuki 2606.09096 補 B26：其 localized Weil form與 B25 ambient phase
  form相差 exact pole rank-two項 2 Re(E_+ conjugate(E_-))，只在 pole-neutral
  cone相同。故不能把 Suzuki已證的 self-adjointness／bottom continuity誤當成
  negative-index sign theorem；原文的 all-support非負仍等價 RH。

## 2026-08-15：B25的Dirichlet／oscillation策略稽核

- 由 Weil functional逐項完成 B27 exact分解：pole-removed ambient phase
  `A_x=E_x-kappa_x I`；`E_x` 是 positive arch jump energies與 finite prime jump
  energies之和。它是 closed irreducible Dirichlet form，所以任意 support上基態
  simple且 strictly positive。這是新的 uniform-in-support 結構，不是數值證據。
- exact index obligation為 `nu_-(A_x)=#{mu_j(E_x)<kappa_x}`。依 Selberg nudge
  修正量詞：零點／prime的 density-average不能替代這個逐 eigenvalue count，除非另有
  uniform form或resolvent bound。
- 證 pole-neutral實 test至少有兩次 sign changes；但 positivity improving只控制第一
  eigenfunction。arch-only scaling test又嚴格給每個 fixed N皆
  `mu_N^arch(x)->0`，故其固定 threshold以下 eigenvalue數無界。Dirichlet性加兩個
  moments本身不足；必須有真正 prime--gamma higher-mode cancellation。
- 用 Schoenberg bilateral-Laplace classification檢查最自然的全正性升格。arch Levy
  exponent在 `s=+-(2m+1/2)` 的poles經 exponentiation成 essential singularities；
  prime atoms的entire factor不能消去。因此 natural jump semigroup不是 PF-infinity。
  未恢復 finite degree/minor certificates，RH仍未證。

## 2026-08-15：theta Green/Rellich 外部輸入與定號稽核

- 下載並逐式核對 Bruinier--Funke--Imamoglu arXiv:1112.3444。其 hyperbolic
  Green current exact把 theta bulk integral轉成 geodesic period與
  `-(4pi)^-1 int(Delta f)eta`，提供 K0B39--41 可仿造的非等變模板；K0B46
  隨後確認尚缺 representation bridge。
- 對 split geodesic，截斷公式保留兩個 cusp boundary integrals；hard term漸近
  含 cusp constant terms與 negative Fourier coefficients，均無一般固定符號。
  在 eigenvalue 0，regularization另含依 spectral deformation而變的
  `B'_ell(1)`。因此沒有把 relative trace／regularized lift誤記成正範數。
- 新增 K0B44 no-go：若 smooth compactly supported `F` 滿足
  `-Delta F>=0` 且 boundary flux消失，則 `int Delta F=0` 與最大值原理迫使
  `F=0`。下一步必須利用而非刪除 cusp/source項，或證 signed bulk的完整 pairing；
  合格輸出是逐 test的 exact square identity，不是 period平均。RH仍未證。
- 核對 Kudla--Millson/Mathai--Quillen輸入：KM form是 cycle Thom form，但 level 1
  compactification `X(1)` genus zero，`S_2=H^1_(2)=0`。因此 closed geodesic只給
  exact Green transgression，不能投到非零 harmonic class後靠 Hodge norm取正；
  split geodesic仍由 cusp項承載資訊。記 K0B45/G89/ES91。
- 隨後逐 kernel比對並更正：K0B39 是 standard `R^2` Epstein theta，BFI 是
  trace-zero matrices的三維 adjoint/`Sym^2` theta，兩者無 equivariant linear map。
  Veronese只落 discriminant-zero cone且把 exponent由 quadratic變 quartic；K0 的
  rectangular geodesic也不是 BFI special cycle。故 BFI只保留為 Green/boundary
  模板，不能宣稱已接上 K0。新增 K0B46/G90/ES92，先攻真正 transmutation。
- 轉用匹配 K0 的 incomplete-Eisenstein decomposition：unfolding證 `Theta_*` 無
  cusp-form projection，Mellin spectrum只有 `zeta(2w)E(z,w)`，所以 direct Green
  construction必經 scattering ratio `zeta^*(2w-1)/zeta^*(2w)`。
- 稽核 Maass--Selberg：其正 truncated norm能在 boundary coefficient恰為零時限制
  截斷 zeta組合的 zeros；對一般 wavepacket，正 norm含 divergent `log T` baseline。
  扣除後的 phase-derivative finite part沒有符號，連同 boundary terms正回到
  B21--B23/Suzuki causal endpoint。新增 K0B47--48/G91/ES93；未把截斷正性當 RH證明。
- 導出 B31 layer-cake identity：cumulative defect
  `D_h(R)=||P_RSh||^2-||P_Rh||^2` 的全 `R` 面積正好是 scattering前後第一
  time moment之差。這把 live target降到必要量詞：只證 integrated flux square，
  不要求逐 cutoff positivity或 full causality。記 G92。
- Selberg nudge指出尚缺 mean-to-individual-zero量詞。新增 B32/W14.5：要求 area sign
  對每個 support與每個 compact pole-neutral test成立；support exact移除所有遠 prime
  powers，故得到完整 Weil positivity。off-line orbit的負 `2 by 2` block可用
  polynomial-Gaussian隔離，並以 cutoff加兩個 fixed bumps恢復 compact support與
  `E_+=E_-=0`。補正 topology：普通 Schwartz不足以控制 prime weight；Gaussian tail
  使 cutoff在 `exp((1/2+epsilon)|u|)` weighted test space收斂，負值因而保留。
  故此全稱命題確實逐零點等價 RH。
- 搜尋 Krein/Szego/Killip--Simon 型 integrated sum rule。核對 Arov-gauge theorem後
  發現其正 coefficient integral預設 holomorphic Schur spectral function；對 Riemann
  quotient，排 poles並到達 endpoint正是 Suzuki/HB缺口。pure unitary boundary令
  entropy發散，任意 transmission completion又不 canonical且不等於 phase-delay。
  新增 B33/G94/ES94，未把 sum-rule positivity循環套用。
- 逐式核對 Connes--Consani arXiv:2006.13771 的 archimedean `-2I+K`
  theorem與其 semilocal建議。證明 prime-power term在 fixed time interval上是
  compressed translation；以 modulo `log n` fibres分解得 finite-path adjacency，
  非零譜有 infinite multiplicity。端點局部 orthonormal sequence可同時落在
  `ker(E_+,E_-)`，故任意 finite-codimension restriction仍 noncompact。另算得
  `Q C_h(a)=<h',T_a h'>+(1/4)<h,T_a h>`，所以先套 Q只會引入
  essentially indefinite shifted derivative energy。新增 B34/G95/ES95：直接以
  compact remainder延伸 archimedean路徑已關閉；必須證新的 noncompact
  semilocal principal-operator inequality，不做 finite-degree/有限譜證書。
- 聯網搜尋 all-support conditional-positivity/Herglotz 輸入，並下載 Suzuki
  arXiv:2301.00421 原始碼。找到目前最具體的 uniform square candidate：
  無條件 `L2` vectors `mathfrak S_t` 由 prime sum、`zeta'/zeta`、gamma與 Lerch tail
  明確定義；其 Gram若等於 Riemann screw kernel，立即給全支撐 Weil
  positivity。稽核 zero expansion後確認不可直接套 Plancherel：`F_gamma`
  的 `L2` Gram必 PSD，而 off-line conjugate orbit所需目標為 indefinite
  `[[0,1],[1,0]]`。只在 `Theta` inner/HB 時才有 model-kernel orthogonality。
  新增 B35/G96/ES96，live proof obligation改為從無零點公式證 full arithmetic
  coisometry/optical theorem，而非 finite minors。
- 核對 indefinite Hermite--Biehler/Krein--Langer 輸入。將
  `E=A+iA'` 寫成 `A-iB` 後 `q=B/A=-A'/A`；de Branges kernel與
  generalized Nevanlinna kernel的 negative-square index相同。因此上半平面
  off-line zeros精確是 B35 contour formula的 Pontryagin residues：finite時指數計重數，
  infinite時負指數無界。新增 B36/G97/ES97。此定理提供 all-degree
  residue ledger，但 `index=0` 仍必須由新的 arithmetic/Poisson 機制證明。
- 對 finite Pontryagin index寫出 Krein--Langer factorization
  `Theta=Theta_0/B` 與 exact kernel decomposition
  `K_Theta=(K_(Theta_0)-K_B)/(B overline B)`。這將 B35 coisometry缺口
  壓成一個 uniform scalar/index命題：證 finite Blaschke denominator `B=1`；
  `K_B` 是 rank `deg B` 的完整負 residue channel。新增 B37/G98/ES98，
  後續不得以 boundary modulus one 或 Hilbert Gram把 `K_B` 丟掉。
- 依 Selberg nudge檢查 prime--Poisson是否能從計數升到 index-zero。構造 exact
  shifted-product countermodel `Xi_a(s)=xi(s+a)xi(s-a)`。它保留 centered reflection、
  conjugation與 explicit formula，且 log Euler weights為正
  `Lambda(n)(n^a+n^-a)`；但 Hardy 的無限 critical zeros被移成無限 off-line
  pairs。故線性 local-distribution/positive-weight論證必敗。新增 B38/G99/ES99；
  live target再收窄為 nonlinear single-degree-one/gamma-channel coisometry，並明記
  degree-one Selberg classification只辨識函數而不證 GRH。
- 稽核 single Euler channel的 nonlinear內容。local log coefficients
  `alpha_p^k` 的 adjacent Hankel minors exact為零；B38 shifted product則為
  `(p^a-p^-a)^2>0`。但 primitive real Dirichlet L-functions同樣通過此
  rank-one/Ramanujan/single-gamma test，故一般 rank-to-index theorem會直接證
  Dirichlet GRH，並非 degree-one classification的 corollary。新增 B39/G100/ES100；
  沒有把 local rank誤當升階證明。
- 搜尋 Jensen/Blaschke 的 all-zero scalar機制。BSY將 weighted critical-line
  `log|zeta|` integral exact寫成所有 `beta>1/2` zeros的正 mass；證 integral `<=0`
  即一次推出 RH。Kunik factorization顯示 normalized pole只令 outer與 Blaschke
  factors相消；hybrid Euler--Hadamard仍保留 zero product。新增 B40/G101/ES101，
  將此 branch收窄為 nonlinear boundary-log反向不等式，未把 equivalent criterion當證明。
- 核對 Burnol math/9910055 與 math/0001013。前者給 exact bridge
  `||P_N1||=exp(-Omega_zeta)`，所以 Nyman最佳距離
  `d^2=1-exp(-2Omega_zeta)`；BSY log mass與 NB11 uniform mollifier其實是同一
  defect。後者的 adelic causality又明確 iff abelian GRH，不能匯入為無條件 sign。
  新增 B41/G102/ES102，合併而非膨脹研究路線。
- 從 degree-one Euler factor推得 exact inner quotient
  `u_p=b_(p^-1/2)(e^(izlogp))/e^(izlogp)`。分母 exponential inner的 model space
  是無限維 Paley--Wiener interval；finite prime products的 numerator與 denominator
  coprime，故 generalized kernel已有 infinite negative squares。這把 B34 noncompact
  principal spectrum與 B10 time-delay baseline統一。新增 B42/G103/ES103；新 target
  是 cross-place Poisson partial isometry配對此 reservoir，並非 local Blaschke positivity。
- Masters' Selberg nudge否決不可計算的 abstract map。隨即展開 local filter：
  `u_p=-p^-1/2 w^-1+(1-p^-1)sum_(k>=0)p^(-k/2)w^k`。Paley--Wiener supports
  互斥，故在整個 local reservoir上 exact有 `H_p^*H_p=p^-1I`、
  `J_p^*J_p=(1-p^-1)I`；Bohr tensor product重現 `prod(1-p^-1)` collapse。
  新增 B43/G104/ES104，下一義務改成可 kernel-audit 的 completed Hankel leakage／
  Poisson diagonal recovery identity B43.5--B43.6。
- 完成該 kernel audit。finite-S negative frequencies為 `-log(d/n)`，係數
  `C_S mu(d)sqrt(d)/(phi(d)sqrt(n))`，得到 finite Mobius--Volterra formula B44。
  Tate cosine transform的 log-time kernel為 `2e^(a/2)cos(2pi e^a)`，與 prime
  measures convolution即 B45 completed kernel。natural recovery仍失敗：
  primal--dual擦除 primes，same-side不 uniform；Möbius cancellation又回到 NB11。
  記 G105/ES105並暫停此 branch，直到有不同的 explicit `R_S`。
- 重新逐段核對 Suzuki 2606.09096 的 EQ102/EQ112 與 strong-resolvent discussion。
  finite-a self-adjoint/real-zero theorem仍無條件，但 `lambda=0` discussion明確先取 RH；
  characteristic-function limit仍為 conjecture，且 `z^2xi/xi'` 的 meromorphic compact
  topology問題正如 K0B42。沒有把近期論文摘要中的「without RH」誤延伸到 conjectural
  limit，故此線未重開。
- 稽核 finite dictionary 的 Nyquist loophole。將 pole source換元成 `[0,1]` sine
  transform後，endpoint density在 `omega=1` 非零，嚴格推出 imaginary-axis growth
  `e^(2pi Y)/Y` 與 exact type `2pi`。因此 compact support不給 strict Carlson slack；
  `sin^2(pi z)h(z)` 的全 integer Hermite data為零，兩 pole constraints亦無效。
  新增 W7/G106/ES106，關閉 single-phase Pick uniqueness捷徑。
- 最新 Selberg nudge指出 off-line Li orbit以 `cosh(n lambda)` 成長，而 on-line orbit
  只為 bounded oscillation。核對後確認這正是既有 L5/D6：最大 modulus off-line shell
  finite且可 simultaneous phase approximation，故必有 exponential negative subsequence；
  cancellation義務只在該 finite off-line shell。未閉合項仍是 D10.3 prime--Laguerre
  負部次指數界，nudge沒有提供新的 arithmetic estimate，故不另開重複路線。
- 開放聯網後先查真正聲稱完成 RH 的 X.-J. Li arXiv:0807.0090v10。逐式定位
  (4.13)->(4.14) 與 (5.8)->(5.9) 的共同 quotient錯誤：`gamma in O_S^*`
  在 `C_S=J_S/O_S^*` 上作用為 identity，而 representative-dependent additive
  character不能隨之作該變數代換。故 unit-orbit summands不相同，兩個 remainder
  trace未被證為零。新增 `li_semilocal_trace_audit.md`、G107、ES107；沒有把外部
  聲稱當作證明。
- 核對 Neeb--Olafsson one-parameter reflection-positive dilation。它對 W10 box
  moments確給 all-size OS quotient與 group covariance，但 group參數是 Laplace shift，
  不是 prime length。W19進一步 exact寫出 weighted prime endpoint comb為 cell bulk
  的 distributional derivative加 boundary；微分重帶符號，完成化後就是 W16缺口。
  因此關閉 generic Hankel-to-group捷徑，保留 completed endpoint sign為唯一義務。
- 將 Li audit再降到 `S={infinity,p}`：normalized unit integral
  `int_(Z_p^*)psi_p(p^kax)d^x` 對 `k>=0,-1,<=-2` exact為
  `1,-1/(p-1),0`，與論文 Lemma 2.2 自己的 local cases一致。故 later
  「all summands identical」不只是缺證，而與先前局部權重直接衝突。正確 orbit
  remainder保留 lacunary real phases及 signed boundary，仍需 sharp global sign。
- 依最新 Selberg nudge把義務留在 Laplace/Herglotz measure。定義
  `q_1(z)=i xi'/xi(1-iz)`，其無條件正 boundary density為 zeros的
  `P_(1-beta)` Poisson kernels之和。證明 RH iff此 measure可寫成
  `P_(1/2)*nu`, `nu>=0`：off-line right zero產生 half-strip內不可消 pole；RH時
  `nu` 為 ordinates counting measure。新增 CS1--CS4/G108/ES108。
- Nakamura--Suzuki 2306.08317 的 infinite-divisibility criterion與上述完全吻合；
  `Psi>=0` 已是充分條件。新價值不是再列 equivalent criterion，而是把 arithmetic
  缺口定成相容 regularized measures的 half-Cauchy divisibility。generic inverse
  Poisson semigroup無界，local inverse exact回 B43，故仍需 conductor-one global theorem。
- 對 CS2 做反演稽核：`exp((1/2+epsilon)|D|)mu_(1+epsilon)` 與 regularizer無關，
  正好是完整 zero-ordinate measure；其 Fourier transform是 `Psi''`。因此這是
  full Weil positivity的新包裝，不是較弱義務。再令 `A=x-psi(x)`，Stieltjes分部
  積分導出 CS5.5--CS5.6 的 exact正三角 kernel公式。kernel雖正，`A` 不定號；
  classical PNT error只給既有 `exp(t/2-c sqrt(t))` absolute尺度，不能推出
  `Psi>=0`。新增 G109/ES109，下一步只接受真正的 conductor-one cancellation或
  all-configuration positive-definiteness theorem。
- 聯網找到 Freedman arXiv:2606.29555 並下載 157MB companion source。先從其座標
  Weyl核導出新的 exact identity：令 `J_omega` 為 sinh-weight tail，則
  `partial_omega J_omega=K_omega`，且 shifted-Xi de Branges核滿足
  `partial_omega D_omega=(4/pi) F K_omega F*`。因此全區間 Weyl PSD會直接推出 RH；
  新增 `weyl_debranges_derivative_bridge.md`。
- 沿 companion JSON dependency向下稽核，發現 formal `closed:true` 最早在
  Green-lift contraction失去證明：`|kappa|<=1` 不推出 `||CKE||<=1`，積分
  compression可反轉比較；二維反例已明記。boundary層又假定 indefinite fiber
  minimizer並把 concomitant定義成同一 `Q`，closure狀態則 hard-code True。
  finite Hardy/Green script自身只輸出 conditional theorem。新增
  `freedman_weyl_positivity_audit.md`、G110/ES110；沒有採信 formal RH ledger。
- 比對 Csordas 1309.0055 與 Dimitrov--Xu 1606.05011，並從 WD boundary diagonal
  導出 `partial_omega D_omega(x,x)=L_complex(Xi;x+iomega)/pi`。故 Weyl PSD連最弱
  plane-wave投影都已包含 complex Laguerre obstruction；已知 Phi log-concavity只證
  associated kernels admissible，不證 PD。Csordas更明定 all-n PD iff RH，甚至實軸
  L1仍 open。新增 WD5/G111/ES111，排除把 total positivity口號當現成升階定理。
- 將 Freedman compression缺口寫成 exact Douglas condition
  `E^*(C^*C-KC^*CK)E>=0`。由兩個 equal-mass s-bumps證 K 不保持 ker C，故不存在
  ambient quotient捷徑；只可能靠 special theta range的新 intertwiner。另新增
  `experiments/freedman_kernel_gram_scan.py`：omega=.49 的小型 point-Gram掃描只見
  `1e-14` 數值噪聲級負值，記入 `numerical_experiments.md`，明確不作證明。
- 建立 strict-log-concavity反例族。`e^-t²(1+0.1cos t)` 的 log二階導數解析
  `<=-17/9`，但 Fourier transform含 cosh factor並有顯式非實 zeros；其 Weyl Gram
  掃描亦出現穩定 `-2.43e-5` 負值。新增 WD6/G112，故後續 special theta theorem
  必須使用 modular/mode coupling，不能只使用一般 shape assumptions。
- 證明 WD7 converse：對任意 LP real entire f，vertical-shift ratios
  `f(z+iomega1)/f(z+iomega2)` 是 Schur multipliers，故其 de Branges spaces形成
  contractive chain，`partial_omega D>=0`；fixed-height double Fourier inversion再
  推回 `K_omega>=0`。與 WD3合併得 small-omega Weyl family PSD iff f全實零。
  因而 Freedman conjecture對 Xi exact等價 RH；這提供真正 all-degree升階定理，
  同時防止把 theta Douglas contraction誤列成較弱的後處理。
- 依 Selberg lens 逐式追蹤 Jacobi--Poisson 到 FW6。新檔
  `theta_poisson_douglas_route.md` 證 exact Hankel square completion TPD2：
  `16<Kf,f>=sum_sigma(||H(q_sigma,+)f||^2-||H(q_sigma,-)f||^2)`，而模偶性只給
  `q_sigma,-(t)=q_-sigma,+(-t)`。它把 minus profile 送到 opposite branch 的負半軸，
  沒有自動給正半軸 contraction。於 `omega=0`，兩 Fourier multipliers正是
  `E=Xi-iXi'` 與 `E#=Xi+iXi'`；boundary ratio `E#/E` 無條件 unimodular。若要求
  full-Hardy causality便等價它為 inner，亦即 Hermite--Biehler／RH；實際
  Douglas只在 special range，但該 statement就是 K0 PSD，VK6已獨立證等價 RH。
  scalar Poisson unitarity只閉合反射，不閉合任一版本；記 G114。
- 聯網核對 Connes--Consani 1910.14368：其 Lemma 3.4/Cor.3.5 正式證 unitary
  multiplier 的 half-space sign iff Beurling inner；Section 4.1 由 Poisson 得
  modulus-one quotient，完整 Weil sign仍列 Conjecture 4.1。Suzuki 1204.1827
  Prop.1.2亦把 shifted-xi innerness等價於相應 zero-free region，無條件 canonical
  system只在 `omega>1`。記 ES113；外部輸入確認 full-Hardy斷層，不提供缺失的
  special-range contraction。量詞修正已寫入 TPD4，未把一般 projection iff誤套 range。
- 將 Connes--Consani Sonine算子與 theta lift逐式接合：
  `J(D_u^2+D_u)J^-1=d_t^2-1/4`，確為 Xi kernel operator。但 Dirac-comb
  scalarization `C f=sum f(n)` 在 L2 不有界；N個互斥、零積分 bumps即使滿足
  `f(0)=hat f(0)=0` 仍使 `|Cf|~sqrt N`。故 ambient Poisson contraction不能穿過
  theta sampling，重現 FW2 compression錯誤。新增 TPD7/G115；只保留 actual
  Gaussian-dilation range上的專用 uniform frame estimate。
- 進一步以 Mellin cyclicity關閉該 global frame候選。Gaussian Mellin transform為
  無零 Gamma factor，Sonine微分只乘 `-(tau^2+1/4)`；comb sampling的 spectral
  symbol exact為 `zeta(1/2-it)`。uniform L2 sampling bound會迫使 critical-line
  zeta屬 L2，與 `int_0^T|zeta|^2~TlogT` 矛盾。新增 TPD8/G116。故 Poisson支線
  只剩 support-dependent renormalized defect difference，回到 B21--B32 的
  integrated mean-delay，而非一般 frame theorem。
- 搜尋近期 Laguerre 輸入並消除題名歧義：Wang--Yang證 coefficient sequence在大 n
  的 fixed-order inequality；Wagner shifted-LP證足夠高 derivative/shift；2026
  kernel稿只證 Phi log-concavity。三者皆未證 Xi 的 real-axis
  `(Xi')^2-XiXi''>=0`，更無 all-matrix升階。記 ES114；不把 TP2／tail inequalities
  誤列為 K0 positivity。
- 回應最新 Selberg nudge，新增 `defect_difference_unification.md`。由 Xi canonical
  product導出 DU1：`B_Xi(w,z)=pi^-1 sum_rho Xi(z)/(z-rho)
  Xi(conj w)/(conj w-rho)`。結合 K0B2 與 TPD2 得
  `Delta_TPD=2 sum_rho R(rho)conj(R(conj rho))`；B21--B22--B31則逐 test exact等於
  同一 zero pairing在 pole-neutral Paley--Wiener class上的值。故三種 defect正號
  是同一義務的不同座標／test pullback，不是三條獨立路徑。下一個合格輸出只能是
  把完整 renormalized area（含 boundary）直接 factor成 square。
- 稽核最短 pole-factor候選。whole-line Green kernel `e^(-|y|/2)` 證
  `ker(E_+,E_-)=(-d^2+1/4)C_c^infty(-x,x)`，支撐因兩 moments exact保留；但
  Fourier側只是 `H=(z^2+1/4)G`。該乘子在 Xi zeros非零，對每個 off-line block
  作可逆 congruence，負指標不變；time side又回 B34 shifted derivative energies。
  新增 DU6/G118，關閉 ordinary Poincare factor捷徑。
- 聯網稽核 Polson 的 Barnes beta/Thorin/Wald 路線。後期 SSRN 6992163 明確把
  folded dual Thorin positivity、LP、Weil與全 Hankel/Jacobi positivity列為同一
  RH open clause；6992161 並指出 atomwise HCM 不由 theta sum保留。較早
  arXiv:1804.10043v8 雖聲稱證 RH，但 Theorem 23 的式 (30)、(31)不是恆等式，且
  `U_star` 含 `delta_(3/4)`，使 Theorem 25 所需 `E exp(H_star)` 必發散，critical
  tilt不存在。新增 `polson_thorin_audit.md`、G119/ES115。這提供 uniform all-degree
  字典但沒有新算術 sign；不重開 finite moment certificates。
- 再往上游檢查發現同稿式 (24) 的 Frullani sign直接錯誤：
  `log(1+s/c)-s/c` 應等於 **負** 的 compensated integral。故 xi centred Levy
  distribution含 `-e^x dx` pole counterterm，而非論文所列 `+e^x dx`；prime/Gamma/
  pole 是 signed renormalized defect，Lemma 16 的 nonnegative Tonelli無法套用。
  這把 Thorin缺口 exact接回 G117，而非另一條正性來源。
- 搜得並稽核 arXiv:2602.20313v2：actual de Bruijn--Newman kernel `Phi(|u|)` 有
  certified負 5x5 Toeplitz minor。未只依作者 mpmath；新增
  `experiments/verify_phi_pf5_arb.py`，用 python-flint/Arb 320-bit balls、解析
  `<1e-70` theta tail，且以 Arb determinant及 explicit 120-term Leibniz兩路得到
  相同嚴格負 enclosure（中心 `-1.8472360734426587e-9`）。新增
  `phi_pf5_audit.md`、G120/ES116。這嚴格關閉 raw Phi PF-infinity升階路線；不把它
  當 RH數值證據，也不混同仍 RH-equivalent 的 K0/Weyl positivity。
- 對 corrected Polson signed measure作 boundary evaluation，新增
  `thorin_outer_inner_bridge.md`。exact得 `S_a(t)=log(xi(a)/|xi(a+it)|)`；由
  Williams/Ostrovsky `E(W^s)=2(2/pi)^sxi(s)`，它是 tilted characteristic-function
  modulus defect，故無條件非負。這沒有證 RH：off-line zeros形成 boundary modulus 1
  的 Blaschke inner factor，scalar `S`只重建 outer part；raw Gamma measure又違反
  Lemma 16近0 integrability。新增 G121/ES117，把 Thorin缺口與 TPD inner-causality
  exact統一。
- 將 hidden inner factor逐 zero顯式化：`rho=1/2+a+i gamma` 對 critical boundary
  phase derivative貢獻 `-2a/(a^2+(t-gamma)^2)`，共軛 zero再給 `-gamma` bump。
  新增 TOI5/G122。外部搜尋未找到 GGC/HCM Mellin theorem能由 characteristic
  positivity排除這些 bumps；WD6解析反例與 actual PF5 failure亦阻止 generic shape/
  variation-diminishing升級。剩餘義務確為 arithmetic phase cancellation。
- 回應 outer-budget nudge，新增 `outer_budget_zero_density.md`。單一 Nyman 函數
  `rho_(1/2)` 的奇偶階梯 exact給 `d^2<=1-log 2`，故
  `Omega_zeta<=C_0=-(1/2)log(log 2)`。每零點 BSY 質量下界再推出按重數
  `N_off(delta;T<=|gamma|<=2T)<=C_0(4T^2+1)/delta`。這是無數值假設的正項定理，
  但尺度太弱，不能排除零點；新增 G123，不把它列為 RH closure。
- 聯網稽核 Suzuki arXiv:2411.07436v3、Freitas math/0507368 與 Suzuki
  2301.05779，新增 `arithmetic_phase_sign_audit.md`、B46、G124、ES118--ES119。
  RH 等價於純 prime-power 函數 `g_0(t)` 最終非正；其二階 distribution exact是
  prime atoms減 pole density，Laplace transform為
  `-z^(-2)d_s log[s(s-1)zeta(s)]`。這是 phase-sensitive、非逐 degree 的合格 target。
  但 PNT error、正係數、prime-power分項、generalized Li recurrence及 conditional
  model-space norm都未提供 sign；下一步只攻正 kernel renewal／convex domination。
- 稽核 `Lambda*1=log` 的自然正 renewal。對 `H=-g_0` 卷積
  `eta=sum m^(-1/2)delta_(log m)` 後雖可完全消去 prime powers，但 Laplace multiplier
  是 `zeta(s)`，會精確消掉所有 nontrivial-zero poles。Euler--Maclaurin exact導出
  `H*eta=4(1+gamma_0)e^(t/2)+O(t)`，故其巨大正號純來自 counting pole，無 RH
  資訊。另以 support-sum 證非平凡正卷積不可能有正 inverse。新增 AP6/G125；關閉
  此 renewal，保留 AP2.2 direct square／nonvanishing restricted kernel才可續。
- 新增 `experiments/check_ap6_convolution.py`：Mangoldt convolution與 closed integer
  formula在 `t=4,6,8,10` 相合至約 `1e-11` 或更好，ratio朝解析常數
  `4(1+gamma_0)` 移動。只作 AP6 代數重驗，沒有當成 RH 證據。
- 建立不遮零點的修正版 AP7：以 causal exponential kernel平滑 `H=-g_0`，Laplace
  multiplier `(z+a)^(-1)` 無零，故 Landau oscillation論證顯示平滑後 eventual非負
  仍等價 RH。導出 exact prime weight
  `phi_a(v)=v/a-(1-e^(-av))/a^2` 與 closed baseline `C_a(t)`。此 family保留 phase，
  但未取得 one-sided bound；PNT error仍太大，故記 G126/OPEN，不作證明宣稱。
- 證明 BSY height loss 的 sharpness：`u=-log|B|` 從 `s=1` 到 `1+iT` 的 Harnack
  factor exact為 `(sqrt(1+T^2)+|T|)^2~4T^2`；單一高度 T、距線 b趨零的 Blaschke
  zero飽和此比例。新增 OB4/G127。故 G123 的 `T^2` 不是估計粗糙，單一 scalar
  outer budget不可能升成 zero exclusion；需 shifted local budgets或 phase control。
- 回應 Selberg extremal-zero nudge，新增 AP8/G128。導出單 quartet 對 `g_0` 的 exact
  項 `-4Re(cosh((a+i gamma)t)/(a+i gamma)^2)`，正峰振幅
  `2e^(at)/(a^2+gamma^2)`。若最右實部 A由有限 edge zeros取到且有 gap，edge sum是
  非零 mean-zero trig polynomial乘 `e^(At)`，故必有無界正負 excursion；聚合不能
  抵消。未閉合者精確是 supremum不取到／無限逼近 edge，BSY mass不排除此配置。
- 聯網取得 Radziejewski QJM 65 (2014) 的 weakly-bounded Mellin oscillation theorem。
  對 `f(x)=g_0(log x)`，每個 off-line zero在 `q=rho-1/2` 給 residue `-m/q^2`
  的 simple pole；標準 `zeta'/zeta` vertical estimate驗證 hypotheses，故得到
  `g_0=Omega_+/- (e^(at)t^(-M))`，不需最右 zero或 finite edge。新增 AP9/G129/
  ES120；這只關閉 aggregation caveat，沒有證 prime-side sign。
- 稽核 Suzuki 2025 version-of-record 的 shifted-window與 modulus-average結果：window
  主項為 exact zero-mean，粗 PNT無 slack；unconditional average只跨 q>=3，不能
  反演出 q=1。未把它列成 RH進展。
- 新增 AP10/G130。`H=-g_0` 的 eventual fixed-step monotonicity
  `H(t)-H(t-L)>=0` 對某 L與 RH等價，且 prime式有 capped history；再差一次雖完全
  局部化到 triangular `2L` window，卻消掉 linear drift，generic L必由 critical zeros
  產生兩號振盪。這精確關閉 compact-window pointwise-sign捷徑。
- 新增 AP11/G131。對 exponential smoothing `K_a` 改攻 derivative
  `D_a=K_a'=H-aK_a`；它有 ODE正反演且 multiplier `z/(z+a)` 不消 off-line poles，
  「存在 a使 D_a eventual非負」與 RH等價。prime weight為
  `[1-(n/x)^a]/a`。`a=1/2` 化為單一 psi integral，但仍需 sqrt-x級 cancellation；
  AP11.4現為 live arithmetic target，不以有限數值批次替代。
- 強化 AP11：RH下用 exact
  `sum_rho(1/4+gamma^2)^(-1)=2+gamma_E-log(4pi)<1` 控制全部 critical-zero振幅，
  而 `2c_0=pi/2+log(8pi)+gamma_E` 提供更大正 drift。故固定 `a=1/2` 即成立，
  AP11.6 的單一 psi integral eventual upper bound與 RH exact等價；沒有使用零點數值。
- 稽核 2026 Preprints.org 202605.1525v4 的 Chebyshev-integral claimed proof。
  核心 Lemma 9 對所有 `J_m={k:floor(N/k)=m}` 假設正 weight；exact反例
  `N=10,m=6` 給空集。floor map只取 O(sqrt N) 個值，故無法控制全部 A(m) mean
  square，後續 absolute convergence/RH結論失效。新增 PC/ES121/G132；不採用該稿。
- 續做 PC5 salvage audit：限制到非空 cells只控制 m<=sqrt(N)，所得
  `sum A(m)^2/m=O(M^2 log M)` 不優於 A=O(m)；對 N平均則權重降為 m^-3，仍只得
  trivial bound。故不能靠 floor-cell averaging修補該稿。
- 稽核 Johnston arXiv:2201.06184 的 2026 version。其可靠結果無條件止於 c=2
  weighted bias，並證 off-line omega時所有 c<1+omega有正 excursion。AP11.6
  恰是 c=3/2，故位於 RH臨界門檻；新增 AP12/ES122/G133，不再嘗試由 c=2插值。
- 聯網取得 Akatsuka arXiv:2411.19259。其 1/2-SHCN extremal principle把所有整數與
  任意 prime exponents統一壓成 renormalized partial Euler product `E_1`；boundedness
  exact等價 RH。新增 `akatsuka_multiplicative_audit.md`、ES123/G134，列為 AP11 之外
  的 all-complexity live route。
- 自行導出 `log E_1=C+int(psi-u)q(u)du+B_theta+O(1/log X)`，其中
  `q=u^-3/2(1/(2log u)+1/log^2 u)`、`B_theta>=0` 是 concavity defect。此 target以
  `1/log` damping消退 critical-line oscillations但保留 off-line growth；尚缺 uniform
  upper bound。
- 新增 `experiments/akatsuka_jump_arb.py`，256-bit ball arithmetic嚴格證 log E1 的
  p=5 jump為負、p=1327 jump為正，排除逐 prime monotonicity。這是候選機制反例檢查，
  不是 RH數值證據。
- 導出 consecutive 1/2-SHCN 的 exact secant-slope increment A4.1；其判號取決於
  `theta(x^2)-x^2` 的 sqrt-scale error。新增 `experiments/akatsuka_shcn_transition_arb.py`，
  連 transition ordering 一併嚴格驗證一正一負 increment，故 global decreasing
  Lyapunov law亦否決；只剩 eventual或 compensated telescoping版本可作候選。
- 將 SHCN extremality做 Fenchel dual，得 exact all-degree certificate A5.5：
  `G(c)=sum_p log max_e[sigma_-1/2(p^e)p^-ce]`，`V(c)` 為 `li(sqrt L)` 的顯式
  concave conjugate，且全體 normalized divisor values有界 iff `sup_c(G-V)<infinity`。
  這提供具體 uniform升階框架，但 `G<=V+C` 尚未證；展開後仍含 E1 的臨界 prime error。
- 將 dual defect完整展開：Akatsuka Lemmas 3.3/5.1 與 partial summation給
  `G(c)-V(c)=C_0+Q(x^2)+o(1)`，theta concavity/cutoff mismatch全消成 o(1)。新增
  AP14/G135；all-degree target現 exact為 logarithmically damped critical Chebyshev
  mean `Q` bounded above。
- 發現 kernel的正 mixture
  `q(u)=int_(3/2)^infinity(s-1)u^-s ds`。這把 target定位成 power-weight family的
  endpoint uniformity問題；已知更強 decay bounds不能無 uniform constant地推到3/2。
- 回應 Selberg-lens nudge，新增 `experiments/akatsuka_dual_extrema.py`。掃描143264個
  SHCN transitions／4756個 plateau stationary maxima；後段極值由接近 Y 的 frontier
  primes夾住，約60% raw G mass在 `p>Y^(3/4)`。defect約0.04246而總量約126，顯示
  是全尺度 cancellation，不是固定小 primes主導；明記數值不作證明。
- 以 explicit-formula exponent audit補解析結論：low-prime cutoff到 `Y^delta` 只保留
  off-line項的 `Y^(delta a)`，full frontier仍有 `Y^a/logY`。故不能切出固定小質數的
  zero-blind子命題；合法 frontier window仍保留 off-line poles並承擔同一缺口。
- 將 frontier no-go嚴格化為 AP15/G137：`W_delta=Q(Y)-Q(Y^delta)` 的 log-Laplace
  transform含縮放 `delta^-1 Qhat(z/delta)`。若 spectral supremum A>0，選
  `a>delta A` 的 zero singularity即可證縮放項不能抵消；W_delta遂正負無界。RH下
  `W_delta=O(1/logY)`。故 proportional tail bounded above仍 exact等價 RH。
- 稽核 Brent--Platt--Trudgian arXiv:2008.06140。即使採 RH-optimal dyadic mean square
  `I(X)<<X^2`，Cauchy--Schwarz對 Q每 block只給 `O(1/logX)`，沿 powers of 2為 harmonic
  divergence。新增 AP16/ES124/G138；ordinary positive L2 block square關閉，需保留
  cross-scale phase/telescoping。
- 新增 `selberg_fractional_square_audit.md` 與 AP17/G139。發現
  `S_alpha=L^2-alpha L'` 對 `0<alpha<1` 同時有全非負 Dirichlet係數與每個 zero
  multiplicity皆非消失的 double pole；`alpha=1/2` 等於 `(zeta^2)''/(4zeta^2)`。
  但 natural Cesaro `O(sqrt(x)log x)` remainder bound本身等價 RH；正性在主項扣除後
  不存留。依 nudge 將它降為 cross-scale identity 的 validation filter。
- 續做 denominator-clearing audit：`alpha=1/2` 完成化後的自然 Laguerre form全線
  積分只是 `int(f'^2-ff'')=2int f'^2>=0`，對任何衰減實函數成立。weighted版本有
  uncontrolled `w''` term。新增 SFS7/G140，排除把此 generic Sobolev square誤當
  Xi zero-location positivity。
- 聯網取得 Banks--Sinha arXiv:2209.11768。注意到 exact
  `a_alpha=(1-alpha)Lambda^2+alpha Lambda_2`；外部 theorem已分別把兩者的 uniform
  twisted square-root-exponent估計證成 RH等價。新增 SFS8/ES125：fractional family
  是兩個已知 RH detectors 的 robust凸組合，沒有提供新的 unconditional sign。
- 導出 SFS9/G141/strategy38 的全階結構：對 `sigma>1`，
  `(-1)^r(zeta^k)^(r)/zeta^k` 是同一 `log N` 分布的全部 moments，所有 Hankel sizes
  一次 PSD；`sigma->1+` 全分布縮放趨 Gamma(k)，k大再 Gaussian。此機制 rigorous
  uniform-in-degree，但只看 pole-local law；跨到 critical strip時正 measure表示失效，
  故沒有補 RH bridge，亦不再刷 finite moment batches。
- 聯網取得 Nakamura arXiv:1504.03438 與 Nakamura--Suzuki arXiv:2306.08317。
  外部 theorem已證 completed zeta 的 critical-strip infinite-divisibility型延拓 exact
  iff RH，RH下 Levy atoms是 real zero frequencies。新增 SFS10/ES126/G142/strategy39；
  將一般 probability continuation降級為等價座標。
- 由 Nakamura--Suzuki 式 (1.5)--(1.7) 將 AP9 的 g0 加 exact archimedean counterterm，
  得 AP18/G143/strategy40：`g_zeta=sum m_gamma(e^-iγt-1)/γ^2`。RH下是負 sin-square；
  `-g_zeta''` PD正是 Weil zero measure。故 AP sign、infinite divisibility、Weil/GNS
  三線合流為同一義務，不重複計為研究路徑。
- 回應 Selberg-lens nudge，建立 screw_convex_dual_audit.md 與 AP19/G144。
  g_zeta 的 prime part是 convex hinge sum；archimedean B在 t>=log2 嚴格凸且
  boundary可由五項正 series嚴格證。Fenchel conjugate把 sign exact離散成所有
  cumulative prime-power vertices Z_j>=B^*(Y_j)。此 family uniform all-prime，
  但立即 iff RH；沒有 global majorization前只列 equivalence，不刷 finite batches。
- 新增 experiments/screw_transition_arb.py 與 SC5/G145。以 256-bit Arb和解析
  Lerch tail嚴格證 n=16 transition正、n=32 transition負，排除逐 prime-power
  monotonicity。這是 proof-mechanism counterexample，不是有限 RH evidence；只剩
  cross-transition telescoping/transport可續。
- SC6/G146 將剩餘 target寫成 exact quantile primitive
  integral(ell-(B')^-1)。局部 integrand兩號；Lambda*1=log 的自然正 transport又由
  AP6知會消掉 zero poles。故只保留 nonvanishing、phase-preserving global transport。
- 稽核 Gaussian transport：multiplier e^(sigma q^2/2)處處非零，故 fixed-sigma
  smoothed sign仍 exact iff RH；但 inverse不保正，TPD8亦排除 Gaussian cyclic frame。
  新增 AP20/G147，確認 J24 local Gaussian enclosure不能補 all-degree bridge。
- 回應最新 Selberg-lens nudge，建立 `screw_variational_prime_bounds_audit.md`。
  partial summation精確給 slope error `A_R`，並證任何只保留 cumulative monotonicity
  與對稱 envelope 的變分 relaxation，只要 allowance不可積，其 gap下確界即為
  `-infinity`。Bellotti最新無條件 PNT error在 log座標給指數增長 allowance；甚至
  RH-scale `|psi-x|<<sqrt(x)log^2x` 也只給 `O(t^3)`。新增 AP21/ES127/G148/
  strategy42；不再優化 absolute prime bounds，轉找 phase-preserving cross-scale identity。
- 聯網稽核 Grochenig arXiv:2007.12889 的 reciprocal-Xi PF-infinity criterion。
  它是真 all-degree theorem，但平方變數下與 A20/Thorin Stieltjes measure完全合流；
  Euler expansion只控制 real-axis兩尾，中央 additive Fourier correction不保 total
  positivity。新增 `schoenberg_reciprocal_xi_audit.md`、ES128/G149/strategy43，
  不把等價座標誤算成新 proof route。

## 2026-08-16：Li 負逸出由子序列強化為 syndetic

- 稽核 Selberg nudge後確認「在線零點不能抵消離線最大殼層」已由 L5/D6
  完成，未重複計為新結果。
- 新證 LS1：最大殼層的有限相位向量在緊群軌道閉包中回返任一單位元鄰域
  的時間集有界間隔；L5 的非最大殼層 remainder 對所有大 n 一致為
  `o(R^n)`。因此 RH 假時每個固定長度的大區塊都有
  `lambda_n,E_n<=-cR^n`。
- 推出 LS2：RH 等價於對每個 epsilon，負門檻集合
  `{n:E_n<-exp(epsilon n)}` density zero；也等價於存在任意長且任意靠後的
  全好 block。這把 D10 的逐項責任嚴格放寬成平均／區塊責任。
- 外部核對 Bombieri--Lagarias 的單側次指數判準與 Voros 的 non-tempered
  oscillation；兩者不取代 LS1 的 workspace 證明。
- 未閉合：尚無由 prime--Laguerre signed transform 無條件證 density zero
  或長好 block 的估計；RH 未證。
- 外部取得 Arias de Reyna 的 ordinary-Laguerre theorem，並由 D10.4 核對
  `E_n=n a_n`；其 Parseval identity給真正 all-degree positive energy，且
  `RH iff (a_n) in ell^2 iff int|Pi-Li|^2x^-2dx<infinity`。
- Karp 的 geometric-weight Laguerre RKHS theorem要求 entire restriction；
  `Pi(e^t)-Li(e^t)` 有 prime-power jumps，無法套用。故外部結構沒有閉合
  LS2，只把新缺口精確定位為單側 weak-type density/block estimate。
- AL5 將 LS2 正定化：RH 等價於對每個 epsilon存在任意長遠端 blocks，
  其 finite Laguerre energy `sum|a_n|^2<=exp(epsilon N)`；此 energy有
  Christoffel--Darboux PSD kernel，但仍需 signed two-scale prime correlation。
- 另由 Stieltjes constants作 100-digit候選掃描，`F=(s-1)zeta(s)` 的 Taylor
  coefficients `b_n` 與 `log F` coefficients `a_n` 前 80 項皆正。只用於提出
  AL6，隨即停止 finite batch。AL6.1--AL6.2給 exact fractional-part Laguerre／
  sum-integral公式；Pringsheim證全部 `a_n>=0` 已直接推出 RH。全部 `b_n>=0`
  只給 PGF，不給 compound-Poisson infinite divisibility，故不是證明橋。
- 稽核 Suman 2026 的 Li漸近/RH claim。精確找到兩個獨立致命錯誤：
  (i) `Y(x)=L_n(log x)` 的 x導數與 `L_n(t)` 的 t導數混用，使 (53) 的 ODE消去
  無效（`n=1,x=2` 即反例）；(ii) Bernoulli Euler--Maclaurin漸近被當成收斂
  無窮級數，固定 n 時項不趨零。另記錄無界積分使用 fixed-argument Laguerre
  漸近的 uniformity缺口。新增 audit、ES130/G151/strategy45；不採納該 claim。
- 取得 Suzuki 2026-08-11頁面版本的 model-space theorem：`G_n` 無條件在 L2，
  全 Gram matrix一次 PSD；但 `lambda_n=||G_n||^2/(2pi)` 的全部等號 iff RH，
  所需 inner/Hermite--Biehler性亦 iff RH。新增 SMG1--2/ES131/G152。
- 取得 Matsumoto--Suzuki 2026 Goldbach M-function theorem。`Lambda*Lambda>=0`
  提供真正 two-scale arithmetic quantity，且 H/H1有無條件 prime formulas；
  然而 centered H bounded或 compact-support limiting law已推出 RH，conditional
  Goldbach remainder不能移作無條件輸入。新增 SMG3--4/ES132/G153/strategy46。
- 新證 SMG5/L13：Goldbach zero sum H 的 log-scale L2 energy對每個指數門檻皆
  次指數 iff RH。反向以 weighted L2 Laplace解析性和 off-line pole矛盾；不依賴
  最大殼層存在。prime formula把它變成 centered weighted-Lambda的全尺度正能量。
  新增 G154；未把尚缺的 arithmetic upper bound冒充證明。
- 稽核 Han arXiv:2505.23795：smooth `k`-Goldbach量 exact為 smooth prime sum的
  k次冪，source並證 sharp errors與 zero-free regions雙向相連。差冪分解顯示提高
  convolution degree無新 cancellation；centered二卷積又失去非負性且不是 modulus
  square。新增 SMG6/ES133/G155，關閉 ordinary Goldbach degree-lifting捷徑。
- 將 SMG5 完全展成 prime-side all-size PSD kernel。對 `b=Lambda-1`，
  `int C(X)^2X^-2dX=b^TK_Yb`，且 `K_infinity=(3max-min)/(6max^2)`；feature
  factorization對全部 matrix sizes一次成立。新增 SMG7/L14/G156。斷層從「找全階
  positivity」縮成對此特殊 signed arithmetic vector證次多項式 upper bound；PSD
  方向本身不夠，ordinary Goldbach sum-kernel亦不相容。
- 對 SMG7 作 Mellin diagonalization：`B=-zeta'/zeta-zeta` 的 s=1 poles相消，
  `Mellin(C)=B/[s(s+1)]`。L14 exact等價該 quotient在所有 `sigma>1/2` vertical
  lines的 L2有限；off-line zero residue非零，會使所在 line發散。新增 SMG8/G157，
  把剩餘 operator theorem固定為 primes-only Hardy--Mellin H2 bridge。
- 聯網核對 Ghosh--Kremnizer--Noor--Santos arXiv:2206.00434：analytic-space框架中
  evaluation可到 p=2，真正未解的是 closure/shift inverse；p<1無條件結果只給
  Re s>1，p=2正回到 Nyman--Beurling/RH。新增 SMG9/ES134/G158，排除 generic
  Hardy embedding直接補 SMG8。
- 將 centered-prime `max` Gram kernel化成 log-stationary Green kernel。證得 causal
  convolution、strictly positive rational spectral density、二階 distributional inverse
  與 endpoint tail exact公式；新增 L15/G159。block同號反例排除 generic
  coefficient-square contraction。數值至 `10^6` 僅核對公式，明記不得當 RH證據。
- 稽核 Connes--Consani arXiv:1910.14368：local sign iff inner，但 local factors不
  inner，global support補救是 Conjecture 4.1；Baez-Duarte critical L2 closure亦為
  RH等價而非無條件輸入。新增 ES135--136/G160/strategy47。
- 稽核 Selberg symmetry/Vaughan Dirichlet convolution。它提供 uniform升階代數，
  但 Mellin側是 analytic powers而非 modulus square；已知 symmetry integral只作
  origin-average，沒有 fixed-origin maximal transfer。新增 PG5/ES137/G161/strategy48，
  停止無 reflection的 convolution-degree擴張。
- 依 Selberg nudge先稽核 contraction本身。新證 exact formula：prime Green energy
  的 logarithmic growth exponent為 `2 sup(Re rho-1/2)`；所以 subexponential
  contraction exact等價 RH。新增 PG6/L16/G162，策略改追可迭代 strict exponent map。
- 建立 `xi'/xi` positive-real Pick kernel的 all-degree Gram representation（RH下），
  並證 converse。explicit off-axis quartet polynomial顯示 functional-equation boundary
  all-pass性不排除 interior poles。新增 PG7/L17/G163/strategy49。
- 稽核 optimized de la Vallee Poussin/Landau polynomial route。nonnegative
  coefficients為隔離 target zero所需，卻留下不可消的 gamma `log t` mass；signed
  coefficients則失去其他 harmonic zeros的符號。新增 PG8/ES138/G164/strategy50，
  排除靠提高 trigonometric degree取得 fixed exponent。
- 對 Selberg Riccati作 zero-local Laurent audit：任意 multiplicity與任意實部的 zero
  都是 neutral mode；identity不含 strict exponent damping，sharp Moebius RHS又依賴
  `1/zeta` poles。新增 PG9/G165/strategy51，關閉 detector間的 Selberg重排循環。
- 建立 natural reflected-Moebius Toeplitz square並稽核 continuation：critical fixed-line
  norm finite for every sigma>1/2 exact等價 RH；averaged Chowla的 shift-average量詞
  不相容。新增 PG10/ES139/G166/strategy52。
- 核對 arXiv:2206.00434 的 p<1 constants與 evaluation domain：q->1只逼近 Re s=1，
  且 cross-space source exponent發散；沒有 critical interpolation。新增
  PG11/ES140/G167/strategy53。
- 稽核 arXiv:2011.02847 Nyman Cholesky全正猜想。構造全正 lower-triangular factor、
  positive RHS但 target仍有正交殘差的 Hilbert反例，證 positivity alone不推出 RH。
  新增 `nyman_cholesky_positivity_audit.md`、ES141/G168/strategy54。

## 2026-08-16 Nyman boundary vector與 full-tail audit

- 由 Mellin公式及固定欄漸近證 `A=L^-1((k-1)/k)` 是 `s=0` residue座標，並以
  `f_k->0 in L2` 證 `A notin ell2`（L18/NC3/G169）。這解釋全正 Cholesky為何
  沒有提供 bounded closure functional。
- 構造 exact reservoir-weight Hilbert model：同時保留 strict positive L、
  `LA=(k-1)/k`、`LE=log(k)/k`、positive E、remote law與 vanishing row norms，
  但 target仍有非零 orthogonal component（NC4/G170）。因此特殊右端與 paper的
  fixed-j asymptotic仍不足；只能轉攻 full arithmetic Gram moving tail。
- 聯網取得 Werner Ehm, arXiv:2405.06349。`q=1,2` Gram/Müntz decomposition中
  truncated Möbius inversion error未估；source稱其為 major challenge，其他
  centered products也尚無 negligible theorem。`q=2` closure仍 iff RH，數值
  correlation不作證明（NC5/ES142/G171/strategy55）。
- Masters nudge 的 `cosh(n lambda)` dominance已由 L5/LS1封閉；它只重得 Li判準，
  不算新的 unconditional方向。
- 由 Ehm 的 large-ratio Bernoulli展開與 `S_q` continuity，選 fixed ratio nonzero
  window；square-free density嚴格推出 Möbius tail absolute mass為 `Omega(N)`，
  Levinson--Selberg weight後仍 `Omega(N/log N)`。新增 L19/NC5.2--5.3/G172/
  strategy56；關閉 `q=2` pointwise decay加 triangle/Cauchy 的捷徑。

## 2026-08-16：ordinary-Laguerre block／uniform-in-degree 相鄰定理稽核

- 依新的檢索約束，停止搜尋 RH claims/equivalent criteria，只查可直接填 AL5 的
  Laguerre block、large-sieve、uniform asymptotics、frame/Riesz/CD 一手文獻。
- 新建 `laguerre_block_uniform_audit.md`，先固定足夠輸出、允許算術輸入與循環
  淘汰條件；以 Stieltjes 分部積分得到 centered prime quadrature介面 LB3。
- 新證 L39：`Q_n=e^-t(L_n-L_(n-1))` 的 block Gram是離散 Dirichlet Laplacian，
  upper Riesz bound `<4`、lower `asymp H^-2`，完全 uniform in degree N。
- Lubinsky--Mate--Nevai/MZ theorem要求 positive well-spaced/Gauss nodes；prime logs
  高端不分離，且 theorem不控制 discrete-minus-continuous signed discrepancy。
- Temme/Frenzen--Wong/Vanlessen確實給全區 uniform asymptotics，但只能補 kernel；
  與 PNT envelope取絕對值仍有超線性 tail saddle。Plewa H1/L1假設亦不可由 PNT驗證。
- 結論：本線明確縮成 LB8.1 的 prime-centered signed embedding theorem。現有成熟
  Laguerre理論沒有直接填補；不再重複查一般 basis/kernel結果。RH未證，goal active。
- 稽核 Maier--Rassias arXiv:1806.05070：Theorem 2.1 給
  `sum mu(n)g(n/k)<<k^(D-z0+epsilon)` 的 fixed-power saving，但只對 `D>=2`；
  未見 `D=1`，且 `g` 到 `S_q` 尚需 transfer。新增 NC5.4/ES143/G173/strategy57。
- 核對 Ehm Corollary 3.1：reciprocity為 `S_q(1/r)=rS_q(r)+elementary`，保持
  `r=Theta(1)`；elementary block正回到未閉合 Landau/Mertens products。新增
  NC5.5/G174，否決把 moving boundary轉到 Maier--Rassias far regime。
- NC5.6--5.7 精確 refold full ratio Gram：Fourier symbol為
  `|zeta(1/2+it)|^2/|1/2+it|^(2q)`。所以全部 moving pieces的 joint limit就是
  critical Nyman closure，非較弱 lemma。新增 G175/strategy58。

## 2026-08-16：Ehm same-scale dyadic bilinear 稽核

- 把 Levinson--Selberg moving tail固定比例 box精確正規化為
  `T=B/(N log N)`；所需新算術命題是 signed `B=o(N log N)`，不是模糊的
  「Möbius cancellation」。新增 `nyman_same_scale_bilinear_audit.md`、L20、
  G176--G179、strategy59--61。
- 用 Ehm Proposition 5.1/Formula (36) 的 regularity作 exact Mellin Fourier
  separation，得到 adjacent dyadic Möbius polynomials。generic mean-value、large
  sieve與 Cauchy只給 absolute-barrier尺度，未閉合。
- additive-shift稽核顯示：逐 shift即使 `O(sqrt N)`，絕對相加仍為 `N^(3/2)`；
  MRT arXiv:1503.05121的 averaged absolute Chowla在 `H=N` 量詞更弱，不能使用。
- Guth--Maynard arXiv:2405.20552v2改善 `N^(3/4)` large values與 zero density，
  不提供本題所需 Möbius near-square-root signed product。
- 證 generic all-smooth `o(N log N)` theorem以 rank-one kernel立即推出 smooth
  Mertens square-root bound，故已是 RH-strength。Ehm線只剩特殊 kernel identity；
  全 pieces重組則回到 RH-equivalent critical Nyman norm。未證 RH，goal續行。

## 2026-08-16：single-kernel量詞、identity factory與 local-moment升階

- 依 Selberg nudge先稽核單一 `W_q`。Wiener inversion證：all-cutoff Banach-uniform
  same-block版可除掉 nonvanishing `S_q` 並恢復 rank-one Mertens square，故 RH-strength。
  fixed natural tail沒有這個量詞；lacunary coefficient countermodel排除 generic implication。
- 兩次 `log(N/n)=int dn/n` 得 Ehm natural error的 exact雙 logarithmic Cesaro式。
  `S_q=sum R_q` 的 divisor coefficient在 `u<j<=2u` 恰為 `-mu(j)`；主要 Möbius
  same-scale pair完整殘留，關閉直接 identity-factory捷徑。新增
  `ehm_single_kernel_audit.md`、L21--L22、G180--G182、strategy62--63。
- Ramaré--Zuniga arXiv:2312.05138v3 的 positivity限 `sigma>=1`，critical estimate仍
  依賴 Mertens input；新增 ES146。
- 核對 Verjovsky arXiv:2607.25002：local moment-to-point theorem給 fixed `q`
  exponent loss `1/[2(q+1)]`，unbounded `q`形成真正升階機制。新增
  `mobius_local_moment_route.md`、L23/G183--G184/ES147/strategy64；把 target統一為
  critical-arc Orlicz exponential moment，禁止逐 degree刷證書。此 target尚未證，
  RH仍未證，goal active。

## 2026-08-16：fixed-q bootstrap修正 local-moment量詞

- 對 Verjovsky arXiv:2607.25002 做二次強度稽核。若已有 Mertens exponent
  `1/2+delta`，partial summation使 rescaled critical polynomial derivative只長
  `N^delta`；同一 fixed `L^q` moment再把偏移變成 `delta/(q+1)`。由 trivial
  `delta=1/2`迭代，任一 fixed `q>=1` subpower local norm即證 RH。
- 新增 `external_claim_audit_verjovsky.md`、L24/G185--G186/ES148/strategy65，並修正
  `mobius_local_moment_route.md`：研究 target降為 q=2 sinc Toeplitz PSD quadratic，
  不再需要 all-degree moment expansion。
- 依 nudge寫出 Gibbs variational dual。所有 feasible densities產生 additive-difference
  Toeplitz kernels；SK5.2的 `R_q(j/m)` 是 ratio geometry。由 `d_u`平方只能得到一個
  supremum lower witness，無法證 upper bound且引入 fourth correlations。新增
  L25/G187/strategy66，關閉直接 dual certificate。
- 網路搜尋未發現同一 fixed-q feedback argument；只記錄完整 proof，不主張優先權。
  quadratic subpower bound仍未證，RH未證，goal active。

## 2026-08-16：critical quadratic的正譜、多尺度與 Lambert 稽核

- 新增 `mobius_local_quadratic_audit.md`。Legendre--Bessel Parseval與 discrete prolate
  各給一個 exact all-rank positive decomposition；這不是 finite degree certificate。
- prolate超指數 tail可把問題縮到約 `logN/loglogN` 個 low modes，但最低模態已是
  smooth Mertens sum；PNT級 cancellation仍離 `N^o(1)`甚遠。新增 L27/G189/
  ES149/strategy68。
- 由 `mu log=-mu*Lambda` 導出 exact multiscale remainder。所有窄 normalized arcs的
  envelope會有 `2/logN` contraction，但極窄端已包含 Mertens；fixed-c input的 `1/y`
  normalization恰吃掉 gain。新增 L28/G190/strategy69。
- Lambert identity給真正 all-scale dilation equation；critical normalized weights為
  `k^-1/2`，Mellin-scale symbol精確是 `zeta(s+1/2)`。故 generic inverse循環到 RH；
  special forcing/Gamma damping仍列為窄 live route。新增 L29/G191/strategy70。
- 稽核 arXiv:2607.09797v3：Laplace transform criterion與 explicit zero terms確認上述
  power obstruction，沒有提供無條件 bound。新增 ES150。
- Selberg nudge的 uniform-in-delta疑慮已形式化解除：每個 final epsilon只需有限次
  bootstrap，常數可退化。新增 L26/G188/strategy67。
- `experiments/local_quadratic_decomp_check.py` 只核對 normalization：N=96時 Legendre、
  prolate與 direct form誤差分別約 `8e-17`,`4e-16`；Lambert truncation誤差 `1.4e-13`。
  這些不是證明。RH仍未證，goal active。

### 同日補強：最低模態與 Lambert forcing 的強度封閉

- 對 `c=1/(2pi)`，證 `w(x)=sin x/x` 的 Mellin transform在 `Re s>0` 無零：
  `|sW(s)-1|<=sinh(1)-1<1`。因此最低 `k=0` mode的 square-root bound單獨 iff RH。
  新增 LQ2.1/L30/G192/strategy71；low-prolate modes不是較弱 producer。
- Lambert special forcing的尺度 Mellin transform精確為
  `Gamma(r+1/2)/zeta(r+1/2)`。Gamma無零，故 forcing不消 nontrivial zeros；vertical
  damping與 functional equation都不移除 off-line horizontal powers。新增
  LQ5.1/L31/G193/strategy72，關閉此 explicit-formula捷徑。
- 聯網搜尋未發現針對此 sinc-smoothed Möbius scalar的獨立正性定理。剩餘 live問題是
  找不經 reciprocal-zeta continuation的乘法正性／反射不等式。RH仍未證。

### 同日再補強：無迭代的 all-q 升階定理

- sinc weight遞減且 `sin1>1/2`。Abel summation給顯式 supremum equivalence
  `T<=S<=T/(2sin1-1)`，其中 `T=sup|A_w|`、`S=sup|M|`。
- `A_w(N)/sqrtN` 又是 critical arc normalized mean，故被每個 fixed `L^q,q>=1`
  直接控制。新增 LQ2.2/L32/G194/strategy73。
- fixed-q equivalence現在有一步、uniform-in-q/scale且不含 zeta除法的證明；L24
  derivative bootstrap保留為獨立驗證，但不再是主機制。未證輸入精確縮為
  `A_w(N)=N^(1/2+o(1))` 的無條件 arithmetic producer。RH仍未證。

## 2026-08-16：sinc Müntz正性與 bandlimited sampling稽核

- 新增 `sinc_muntz_sampling_audit.md`。compact sinc的 dilation inverse逐點為
  `b(x)=sum mu(k)f(kx)`，且 `b(1/N)`就是最小 scalar target；Mellin symbol為
  `W/zeta`。新增 L34/G195/strategy74。
- 發現真 global sign：compact sinc遞減使 `Pf<=0`。但證明 positive cone closure
  不可能：`h=-Pf` 的所有 dilations共享 `I/(kx)` tail，非負係數消 tail時也在每個
  `[epsilon,1]`消失。故 signed parity不可避免。新增 L35/G196/strategy75。
- 由 sinc bandwidth `<1/2` 導出 exact integer-sampling identity
  `sum_k|A_N(k)|^2=pi N[M(N)^2/N+sum M(n)^2/(n(n+1))]`。這是全頻率PSD，卻逐字
  等於 weak-Mertens歷史能量。新增 L33/G197/strategy76。
- dilation顯式公式只給 `M/2=sum(-1)^(r+1)A_r`；它是外部 frequency的 Poisson零值，
  係數非 `ell2`，Abel+Cauchy norm發散。新增 G198/strategy77。
- 外部 Báez-Duarte arXiv:math/0505453證 compact zero-free Mellin kernel的 strong
  closure iff RH，確認 sinc屬既有等價框架；arXiv:math/0504402亦是 convolution
  criterion。Inoue arXiv:1705.00853只在假設 weak Mertens下研究相應 mean square。
  新增 ES151--ES152。RH未證，goal active。

## 2026-08-16：signed sinc closure與 coefficient norm稽核

- 新增 `sinc_signed_closure_audit.md`。Mellin--Plancherel把任意 signed coefficients
  精確化為 `int|W|^2|1+zeta C|^2`，共同 `1/x` tail另強迫 `C(1)->0`。
  新增 L36/G199/strategy78。
- 證任何 closure sequence的自然 synthesis norm `sum|c_k|/sqrt k` 必發散：若 bounded，
  任一已知 critical zero附近 error保留固定 L2 mass；multiplicity m時 error square
  `>>K^-1/m`。故 bounded-norm projector正式排除。新增 L37/G200/strategy79。
- 核對 Selberg nudge：indicator coordinate精確為 `M(floorN/k)`；compact sinc analogue
  為 `A_w(N/k)`。all-scale identity正規化後仍有 `k^-1/2` 臨界 weights，沒有 induction
  contraction。新增 L38/G201/strategy80。
- Burnol arXiv:math/0103058給 zero multiplicity平方加權的 `1/sqrt(log scale)` Nyman
  distance lower bound；Báez-Duarte arXiv:math/0205003的 explicit upper decay假設 RH。
  arXiv:2510.18132只給 smoothed Gram block-compressibility，沒有 closure upper bound。
  新增 ES153--ES154/G202/strategy81。
- 結論：成功係數必同時有 tail cancellation、發散 signed mass及整線 mollifier error消失；
  現有 theorem沒有無條件完成第三項。RH未證，goal active。

## 2026-08-16：controlled-growth signed projector精確化

- 新證 SC7/L40：對 fixed T，約束 `C(1)=0` 的 Dirichlet exponentials仍在
  `L2(-T,T)` 稠密；Paley--Wiener transform若 annihilate它們，會在 `log k` 形成
  不可能的 exponential zero density。乘 zeta後 range仍稠密，故 local projector存在。
- 未知只剩 coefficient `K=sum|c_k|/sqrt k` 成本。sinc Mellin weight滿足
  `W=O(1/t)`；配 zeta convexity得到 tail
  `O(T^-1+K^2T^(-1/2+2eta))`。
- 因此某 `alpha<1/4` 的 `K=o(T^alpha)` local projector足以、且在存在性格式下
  等價 RH。新 target為 `kappa(T,delta(T))=o(T^alpha)`；bounded-norm no-go沒有
  排除此慢增長窗口。RH未證，goal active。
- 外部 quantitative biorthogonal theorem已核對：standard gap與 2024 no-gap版本仍要求
  power-law spectral counting/有界 condensation groups；`log k` counting為 `e^R`，
  不能代入。新增 SC9/ES156/G206。

## 2026-08-16：controlled-projector tail exponent改進與 Selberg斷層稽核

- 用經典 Ingham--Atkinson 臨界線二次矩取代逐點 convexity。dyadic summation給
  `int_T^infinity|zeta|^2/t^2 << logT/T`，故對所有 finite C 一致有
  `tail << T^-1+K(C)^2logT/T`。合格 norm從 `T^(1/4-)` 放寬到近 `T^(1/2)`；新增
  SC10，並更新 L40/G205/strategy83。
- 稽核 Radziwill arXiv:1207.6583。其 arbitrary-length mollifier theorem是 high-window
  residual lower bound `c/theta`；乘 sinc weight後只成 `c/(Ttheta)`，且 K不控制 support
  length。它不是 kappa upper bound，也不能排除任意 support projector。新增
  SC11/G207/ES157/strategy84。
- 依 Selberg nudge明確標記：本輪獨立成熟定理只控制 global tail；local
  `kappa(T,delta)`仍是 RH 等價 closure義務，尚未找到獨立性質給
  `kappa^2logT/T->0`。不得把重新參數化當證明。RH未證，goal active。
- 新稽核 Andersson arXiv:1207.4624：Pechersky density允許
  `|c_n|<=n^(-1/2+1/loglog n)`，故 K對最大 support只有 `N^o(1)`，tail修正 bounded。
  但沒有 `N(T,delta)` rate，尚不能比較 `sqrt(T/logT)`。新增 SC12/L41/G208/
  ES158/strategy85；下一局部義務縮為 effective support complexity。
- 測試能否以 coefficient ell2取代 K。遠端 consecutive support block在固定 t-window
  幾乎同相：可令 ell2 norm趨零而 `|C|`保持大於常數，且 exact `C(1)=0` 修正僅
  `O(N^-1/2)`。新增 SC13/L42/G209/strategy86，排除 support-free ell2/GCD tail bound。
- 外部 Bettin--Chandee--Radziwill twisted mean仍有 length `T^(1/2+0.01515...)` 限制；
  GCD spectral results不涵蓋超密 log cluster的固定短窗。新增 ES159。
- Masters’ Nudge促使檢查 target regularity：PNT zero-free-region餘項不能給 critical-line
  regularized reciprocal的 uniform derivatives/analytic strip；足以產生有效 coefficient
  decay的假設會偷渡 zero exclusion。新增 SC14/G210。RH未證，goal active。
- 由 SC13反例抽出正確短窗 norm：`B_T`為寬 `1/T` 的 log-frequency bins之
  ell2-of-ell1 mass。Gaussian majorant嚴格證 `int|C|^2<<TB_T^2`；再配 Ingham
  zeta四次矩與 `|C|<=K`，得到新 tail
  `T^-1+K B_T log^2T/T`。新增 SC15/L43/G211/strategy87/ES160。
- L41 envelope另有 deterministic
  `B_T^2<<1+T^-1 sum_(T<n<=N)n^(-1+2/loglog n)`；因此 cluster分散確實比 K-square
  多出約四分之一次方空間。但 Pechersky仍無 N(T,delta)或直接 `K B_T` rate，RH未證。
- 發現 sinc的低 polynomial門檻是 kernel端點 jump，不是 route硬限制。對 all-m beta
  family `f_m=x(1-x)^m1_(0,1)`，Mellin transform是 zero-free rational product且
  `|t|^(-m-1)`；由同一 mean-value論證得 tail分母 `T^(2m+1)`。新增
  SC16/L44/G212/strategy88。
- 結果：只要 local projector可證任何 finite polynomial-in-T cost，先固定足夠大 m即可
  完成 global closure；但 Pechersky仍沒有 polynomial window rate。這是 uniform升階
  機制，不是逐 m刷證書。RH未證，goal active。
- 依新驗收式重查 quantitative Müntz文獻；現有 Markov/Remez、Müntz-space geometry及
  Trefethen coefficient lower example均不給 log-integer/ζ target的 polynomial-in-window
  upper bound。新增 ES161；不以他系統 lower bound關閉本線。

## 2026-08-16 階段性收尾：證據、循環與交接稽核

- 依最新 Atle Selberg lens nudge，重驗「升 m同時更換 target/kernel」。對每一相同 C，
  `Ehat_(m,C)=W_m(1+zeta C)=(W_m/W_m0)Ehat_(m0,C)`；critical line上的 ratio為 bounded
  rational multiplier。因此 local error transfer成立，不是僅由 kernel衰減作類比。
  已同步 SC16a/L45/G213/strategy89。
- 證據分層重核：SC7 density是 Paley--Wiener zero count；SC10 tail用無條件 zeta二次矩；
  SC15用 Gaussian cluster estimate加 Ingham四次矩；SC16/16a是 beta/Gamma代數加前述
  moments；SC13是明示遠端同相 block反例；L39是直接對角化三對角 Gram矩陣。外部來源
  各只支撐相應 mature theorem，沒有以 RH proof claim或純等價判準補缺口。
- 循環風險重核：已證步驟未用 critical-line `1/zeta` regularity、Mertens臨界界或
  off-line zero exclusion。所需 polynomial local cost一旦成立便由 L45推出 RH，所以它
  仍是未證核心義務；qualitative Pechersky density及 RH-equivalent closure不能算證據。
- 已證成果：exact signed Mellin closure、tail cancellation、bounded-norm no-go、fixed-window
  density、mean-square與 cluster tail、ell2-only反例、all-order beta tail及 fixed-m升階。
- 已淘汰/封存：bounded K、support-free ell2/GCD、reciprocal regularity、small-scale
  contraction；ordinary-Laguerre generic block/asymptotic/frame檢索、SK5.2、Lambert/sinc
  recurrence暫停。這不等於排除 controlled-growth signed projector。
- 存活未證：某 fixed m0的 tail-exact local approximants具有任意 finite polynomial K cost
  或 `K B_T` cost；最具體入口是 Andersson--Pechersky construction的 effective support。
- 最新最小缺口：找 `delta(T)->0,A<infinity,C_T(1)=0`，使 local weighted error
  `<=delta(T)` 且 `K(C_T)<=T^A`（或 `K B_T<=T^A`）。
- 下一輪第一步：只量化 Andersson--Pechersky proof的 partial-support stopping mechanism，
  輸出明示 N(T,delta)或確認現有 argument無 rate；不平行開新線。
- 一致性檢查完成後停止自動續攻。RH尚未證明，goal保持 active。

## 2026-08-16 continuation：Andersson--Pechersky rate audit

- 依 Handoff-1 只核對已命名缺口，下載並逐行讀 arXiv:1207.4624 source；另核對作者宣告的
  effective follow-up arXiv:1207.5337。
- 新增 `andersson_pechersky_rate_audit.md`、L46/G214/strategy91。任意 finite atom prefix
  在 `L2` 中都有共同正交 unit direction，嚴格證 pointwise Pechersky divergence不能交換成
  uniform stopping rate。source constants依 fixed Fourier transform，沒有 N(T,delta)。
- classical proof另取 `delta_H=1/(8eH)` 與 logarithmic epsilon，顯示 literal threshold
  已非 polynomial-friendly；但這不是 optimal-support lower bound，故只關閉該 proof機制。
- 以 Hahn--Banach建立 exact target-specific dual AP2.4；它把下一 obligation縮成 special
  beta target的 polynomial norming inequality，並保留 moving extremizer的正確量詞。
- RH仍未證；controlled-growth signed projector未被反證。下一步只攻 AP2.5，不回到
  qualitative density或 all-direction frame bound。

### AP2 concrete target壓測

- 新增 `experiments/test_ap2_dual_cost.py` 與
  `experiments/results_ap2_dual_cost_2026-08-16.md`。這是 floating-point ridge heuristic，
  不是 certificate。
- `m=0,N=128` 在 `T<=12` 可見 `10^-6` 級 relative residual；視窗逼近第一 critical zero
  時，`T=14,16` 分別惡化至約 `3.9e-3,6.4e-2`，q-cost升至 `1e5--1e6`。
- `T=16` 把 N由64增至512只把 residual約 `0.067`降到 `0.057`；m=4可降至約
  `4e-4`，但只是 W_m在首零點附近較小。fixed-window density表示不能把 plateau當 basis
  反例；嚴格下一步是 critical-zero-aware polynomial-cost interpolation，而非更多 N掃描。

## 2026-08-16 continuation：one-sided Hardy producer audit

- 新證 L47/G215/strategy92：以 Poisson--Jensen對 target `exp(i omega t)` 給明示 lower
  bound，證 generic real-Sobolev/two-sided Fourier近似不能以 polynomial coefficient
  mass轉成單邊 `-log n` Dirichlet frequencies。這關閉 regularized reciprocal的 generic
  Fourier捷徑，但不反駁 special zeta target。
- 新證 L48/G216/strategy93：端點距 multiplicity-r zero為 d、local error為 delta時，
  零點局部只強迫 `K>=c(d+Cdelta^2)^(-r)`。所以首零點附近 obstruction是 polynomial，
  ridge的更劇烈成本不能外插成 exponential no-go。
- 結論：AP2.5仍 live；下一輸入必須是 `-1/zeta` 特有的 lower-half-plane
  arithmetic/Hardy factorization或同等 target-specific dual estimate。RH未證，goal active。

## 2026-08-16 continuation：MB1 exact divisor/physical audit

- 新增 L49/G217/strategy94：固定 Riesz--Möbius mollifier的 MB1，量詞、tail constraint與
  polynomial K全部明示。
- 新證 L50/AP6：Mellin--Plancherel把 global error精確化為
  `int_1^infinity |S_X(y)|^2dy/y^4`。k=1 bulk等於 Abel boundary與
  `sum n(Lambda(n)-1)(1-n/y)^m` centered prime discrepancy的同一 square。
- 新證 L51/G218/strategy95：`y>X` tail在 `X<y<2X`精確留下 fixed-log-damped
  same-scale Möbius Riesz sum。PNT partial summation的平方能量仍不趨零；fixed k補不了
  power 1/2，variable k違反量詞。
- MB1未被反證，但不再是獨立 producer；它回到既有 Nyman same-block joint cancellation。
  controlled-projector的目前具體 producer均已到明確最小缺口。下一順位轉查 ordinary-
  Laguerre LB8.1 是否其實同構於同一 block。RH未證，goal active。

## 2026-08-16 continuation：Laguerre--Möbius exact comparison

- 新增 `laguerre_vs_mobius_block_audit.md`、L52/G219/strategy96。
  `K(z)=log[(s-1)zeta(s)]` 與 reciprocal由 exp/log Bell polynomials相連，degree n混合全部
  低階；所以 AP7 same-scale Möbius block不是 LB的 linear same-block換座標。
- 將 AL5 固定成 `H_N=ceil(log(N+2))` 的 LB9.1，仍 exact iff RH；basis loss只有
  `O(log^2N)`，量詞與 uniform-in-degree斷層均關閉。
- L53 exact純冪模型證 PNT envelope與 uncentered positivity仍可有 fixed-base exponential
  Laguerre blocks，故 generic measure/Carleson producer關閉。LB9.1只剩 actual prime-power
  nodes/weights的 signed correlation。RH未證，goal active。

### LB9 explicit cutoff form

- L54/LM6 展開 finite cutoff CD square；L55/LM7 用
  `L_n-L_(n-1)=-(t/n)L_(n-1)^1` 化為 centered prime log moments的明示 binomial矩陣。
- 量詞斷層固定：N先選，Y後趨無限。fixed-N PNT constants不可交換成 uniform-in-N；
  prime-prime/continuum/cross或各 moments分估均會丟 centering並受 fixed-base condition放大。
- 下一個單一測試：Selberg convolution在此 joint metric中是否產生真正 PSD square；若只得
  analytic powers，依 strategy48判失敗。RH未證，goal active。

## 2026-08-16 continuation：Selberg kernel no-go 與 LB block 數值壓測

- 新證 L56/G221/strategy98。centered Selberg identity的二次項 exact為 eta*eta；全部 higher
  convolution hierarchy的二次核仍只能是 `h(t+u)`。LB9.2 associated-Laguerre核由最高
  bidegree證明非 Hankel。故 Selberg/higher-k不能 exact配成 LB PSD square；缺的是新
  reflected two-variable inequality。
- 新增 `experiments/test_laguerre_block_energy.py` 與結果紀錄。兩個 Cauchy半徑重算一致；
  N<=1000的 dyadic quiet minima由 `2.65e-3`降到`1.41e-7`，但序列強烈振盪。
- 修正量詞誤讀：LB要求 arbitrarily large good blocks具 subexponential upper，不要求 fixed
  negative exponential decay。有限數值亦不能排除高 off-line zero的遲發正 exponent。
- Selberg producer關閉，但 LB9.2仍 live。下一步只接受在 LM6.3完整兩腿後使用
  `Lambda(p^j)=logp` single-channel law的 cross-prime reflected identity；per-prime diagonal
  加 triangle/Cauchy不合格。RH未證，goal active。

### LB positive-producer uniformity與 local Euler測試

- 依新 strategy nudge新增 L58/G223/strategy99。正 producer須以 `exp(-o(N))` coercivity
  uniform控制 block全部 coefficient vectors及 eventual cutoff tail；可依 epsilon,N，但不可
  逐 c或 Y-subsequence選常數。
- exact生成式 `sum_n v_(p,n)z^n=-log(1-p^(-1/(1-z)))` 證 single-prime law完整固定 local
  vectors；然而 per-prime PSD漏掉 p≠q與 prime--continuum polarization，Cauchy損失隨 cutoff
  prime數發散。bare local Euler rank-one producer因此到最小失敗點。
- LB9.2仍未反證；下一核心義務是符合 LM11的 global cross-prime reflected/telescoping
  identity。RH未證，goal active。

- L59/G224/strategy100再排除 generic ratio換名：LB CD kernel也不是 `h(t-u)`。因此 live
  obligation必須保留 nontranslation-invariant Laguerre spectral projector；純 reflected
  convolution不算 producer。核心缺口正式縮為 LM11-uniform global centered prime
  quadrature。RH未證，goal active。

### stationary family structural audit 與 anchored residue bridge

- 新證 L60/G225：Euler--Bohr normalized mean annihilate一個會產生 exponential Laguerre
  blocks的 rational off-line factor，故沒有 LM11 coercivity。
- L61/G226把連續 producer失敗統一為 stationary quotienting：`t+u`、`t-u`與 normalized
  means都遺失 finite meromorphic/winding資料。後續不再測另一個 mean候選。
- L62/G227/strategy102給 exact Cauchy residue式與參數：`r_N=1-N^-1/2` 對 N-block只付
  `exp(O(sqrtN))`，但 contour到高度 `asymp sqrtN`、距 critical line `asymp N^-1/2`，並
  必須帶全部 off-line `z_rho^-n` residues。
- 因此 LB的 nonstationary逃生口與 W13/W14 sharp anchored prime--arch residue obligation
  exact合流；residue-free finite-height estimate不是較弱 theorem。RH未證，Goal active。

- 依 nudge補 L63/G228/strategy103：`LB good blocks <=> no interior residues <=> W12 all-test`，
  但 equivalence經 spectral exclusion，不是 bounded intertwiner。LB witness為 syndetic index
  excursions；W12 witness為 orbit-localizing test。不得用「合流」偷渡 LM11 coercivity。
- 針對 W12.4/LM11 named gap作有限一手檢索。arXiv:2311.08519只把 Weil sums改寫成 Bohr
  covariance/spectral integrals，所需 upper仍等價 RH；arXiv:2006.13771只完成 archimedean
  place並把 semilocal prime case列為框架延伸；1910.14368明記 Li cutoff attempt失敗。
  未找到可直接代入的 sharp constant-one prime--arch theorem。RH未證，Goal active。

## 2026-08-16 continuation：DN nonlinear relative-clock theorem

- 依 stop nudge停止增加 residue-equivalent statements，轉向可獨立證明的 DN 中介引理。
- 新證 L64/G229/strategy104。對 ordered clock perturbation，
  `E_d=sum[y-log(1+y)]` exact convex，`gradE=-S`，zero flow為 `u'=-2gradE`，且
  `E'=-2||S||^2`。Hessian是 gap-inverse-square graph Laplacian，quadratic tangent為 DN13。
- 若 `E<c_kappa`，全部 gaps `>kappa d`；Hessian norm至多
  `pi^2/(2kappa^2d^2)`，給 window-uniform backward barrier
  `E(t0)exp[2pi^2tau/(kappa^2d^2)]<c_kappa`。
- collision使 E發散；translation是已移除 null mode；checkerboard飽和 kappa趨1 exponent。
  所以 theorem嚴格存活但仍要求 `exp[-c tau log^2Gamma]` theta rigidity。
- 下一步只做 varying reference clock/buffer correction，然後判定 theta kernel能否供應 initial
  E bound。RH未證，Goal active。
## 2026-08-16：DN varying-clock/buffer correction

- 新證 L65/DN18：frozen nonuniform clock 的 relative energy是 forced gradient flow，force
  exact為 reference PV residual。Hard cutoff arithmetic clock有
  `||S^y||_2 asymp sqrt(n)/d`，所以 endpoint correction不 uniform in particle count。
- 新證 DN19：moving-reference Bregman energy多
  `-<H_y y',x-y>`；affine dilation的 deformation seminorm為
  `|d'/d|sqrt(n(n-1)/2)`。這是先前隱藏的量詞依賴。
- 存活替代是 exact co-moving comparison：兩個相同 log-gas solutions 的
  `F=||x-y||^2/2` 滿足 `-4Lambda F<=F'<=0`，並給 uniform collision barrier。
- 因 `d~2pi/logGamma`，force、drift或全域距離仍須 `exp[-c log^2Gamma]` 小。下一步只測
  exact Hermite-zero reference能否在正確 particle range匹配 theta zeros；RH未證，Goal active。
## 2026-08-16：Hermite與positive-time zero asymptotic裁決

- DN21 驗證 probabilists' Hermite zeros 經 `a(t)^2=a(0)^2+2t` 是 exact finite log-gas；但
  `H_t` zeros是 infinite system。finite block含 exterior PV force，arithmetic stress norm
  `asymp sqrt(n)/d`，故 Hermite comparison在 system-size interface失敗。
- ES164/DN22 核對 Polymath arXiv:1904.12438 Theorem 1.5：`x>=exp(C/t)` 高零點皆實，
  explicit quantile error `O(x^(-ct))`，比 DN所需 `exp[-C t log^2x]` 少一個 log exponent。
- 多步 reset 允許 step僅 `O(t/logx)`，但到 `t~C/logx` 時 error為 constant、gap為
  `1/logx`。現有最強 pointwise theorem不能啟動最後一段。
- 下一核心 obligation切到 collision-count invariant。RH未證，Goal active。
## 2026-08-16：exact checkerboard saturation

- 新證 L67/DN23：period-two infinite log gas exact滿足
  `a'=-(pi/d)tan(pi a/d)`。從 collision data `a(0)=d/2` 出發，正時間振幅為
  `(d/pi)arcsin(e^(-pi^2t/d^2))`。
- 這將 DN13 的 checkerboard由 linear stress升為 nonlinear exact反例：terminal polynomial
  rigidity或任何 clock-local Lipschitz invariant無法辨別 collision。
- 因此 smooth collision-count替代亦關閉。topological/Pontryagin counter回到 P30 projector
  convergence舊缺口，不算新路線。RH未證，Goal active。
## 2026-08-16：續作 Goal — margin與 spacetime discriminant

- L68/DN24 修正 exact checkerboard的適用邊界：一般 detector只推出
  `m_d<=omega_d(epsilon_d)`；若 margin同速指數衰減，不能宣稱 condition number必爆炸。
- L69/DN25 證 finite backward-heat discriminant theorem：time discriminant degree
  `<=n(n-1)/2`，其 interval zero-freeness exact判定 terminal real-rooted polynomial能否倒推保持實根；
  exact coefficients時可用 Sturm chain。
- DN26 以 `m!z^(2m)/(T^m(2m)!)` 證 terminal compact convergence不控制 backward spacetime；
  perturbation在 terminal趨零、time 0 constant term卻為1。故 naive polynomial resultant不能傳到 `H_t`。
- 新缺口是 theta-specific weighted entire topology與 canonical infinite resultant。RH未證，Goal active。
## 2026-08-16：spacetime Brouwer-degree collision counter

- 新證 L70/DN27。對 `F=(h,h_x)`，每個 regular heat collision的 Jacobian determinant exact為
  `-h_xx^2`，故 rectangle boundary winding以同一 orientation計數全部 collisions。
- `alpha+beta x` 是 heat-compatible transverse perturbation，將 degenerate collision納入穩定的
  nonnegative algebraic count。此路不需 entire resultant，存活於 checkerboard no-go之外。
- DN28 壓測：degree的 input stability由 boundary gap `mu_R`控制，可能極小。對 `H_t` expanding
  rectangle，winding是 top/bottom real-zero counts與 vertical flux的 exact ledger；直接讀 bottom phase
  仍是 RH改寫。
- 下一 obligation：theta integral直接構造 boundary nonvanishing homotopy與 uniform margin。Goal active。
## 2026-08-16：boundary homotopy generic no-go

- L71/DN29：positive even two-frequency heat kernel有 explicit regular collision；平滑為 positive even
  super-exponential kernel後仍存在。generic kernel positivity/decay不可能證 L70 winding zero。
- DN30 導出 phase current與 exact signed Fourier density `(1-u)e^(tu^2)Phi(u)`；time 0函數為
  `[2xi-xi']/16`，完整 prime log-derivative仍在。
- ES165 named-gap literature audit未找到可代入 theorem。下一步只接受 arithmetic signed phase的
  expanding-rectangle homotopy或 margin estimate。RH未證，Goal active。
## 2026-08-16：degenerate collision closure

- 新證 L72/DN31：multiplicity m heat collision的 parabolic leading model為 Hermite flow
  `e^(-sD^2)z^m`，intrinsic local degree `-floor(m/2)`。
- multiple-zero curves對 nonzero analytic heat solution不可能；compact collision set離散。
- 因此 L70/DN27 winding完整計入 regular與degenerate collisions，無 sign cancellation。剩餘問題仍是
  theta/primes boundary phase。Goal active。
## 2026-08-16：DN30 phase producer certified no-go

- 新增 `experiments/certify_dn30_vertical_phase_failure.py` 與結果檔。Arb 320-bit rigorously證
  `J(x_1)<0<J(x_35)`，故 actual Xi的 vertical phase velocity不定號。
- DN32明示此反例不影響 L70/L72 collision degree，只排除 monotone vertical evaluation。
- DN33/ES166：horizontal monotonicity是 first Laguerre inequality，一般不充分；完整 criterion回到
  all extended Laguerre/all-degree舊缺口。boundary-winding producer至此到最小失敗點。

## 2026-08-16：續接修正 — Fourier transfer、共同支柱與等價裁決

- 重新核對最新 HANDOFF、strategy112、L70--L73、G233--G237；確認先前把兩個 natural producer
  的失敗誤報成整條 non-naive route完成，已修正，Goal重新保持 active。
- 新證 L74/DN34：theta terminal Fourier measure的 backward multiplier為 contraction；moment-tail
  quadrature使 finite positive rational heat solutions在 fixed rectangles上 `C^1` 收斂。只要 boundary
  gap為正，Brouwer degree嚴格傳遞。DN26只是否決 polynomial/Taylor topology。
- 新證 L75/DN35：選 `e^(-(T-tau)delta^2) in Q` 與 commensurate frequencies後，finite heat flow
  成為 `(r,e^(iy))` Laurent polynomial；root-of-unity vertical sides與 rational horizontal times的
  winding可由 exact Sturm/subresultant Cauchy index決定。
- 壓測量詞：必須先 R、再 `mu_R`、最後 cutoff；DN23容許 margin超小，沒有 uniform-in-X rate。
  raw bottom `t=0` positive margin暗含 critical zeros simple，須用 regular `tau_n downarrow0` 或
  perturbation。DN29又排除由 positive rational weights直接推出 degree zero。
- 再證 L76/DN36：regular expanding zero-degree assertion恰等價RH，並非較弱 lemma。故三條路線
  只在 transfer/finite decidability上合流，沒有降低 arithmetic endpoint；沒有新 signed identity前
  封存 DN route，切回 AP2.5先做 equivalence/quantifier audit。RH未證，Goal保持 active。

## 2026-08-16：AP2.5重參數化裁決

- 核對 SC8/SC10後發現舊檔已含反向量詞、後續 handoff遺忘：RH下 global closure approximants
  每個 cost有限，故可在選 approximant後把 T延遲到 `T^A>=K`；global error又控制任意 local window。
- 新證 L77/AP8/SC17：對任意 fixed `A>0`，AP2.5/SC16.8及其 AP2.4 dual恰等價RH。
  `delta(T)->0`無 prescribed rate且允許 remote support，polynomial-in-T沒有 effective尺度內容。
- controlled-projector抽象路線因此不是下一個獨立攻面。要避開必須有 T-before-approximant 的 explicit
  same-scale coupling或 rate；既有 MB1雖符合前者，但已回到 L51 signed Möbius joint cancellation。
- 下一棒先對索引中候選做 reparameterization-immunity 篩選，再選仍有獨立中介輸出的 obligation。
  RH未證，Goal保持 active。

## 2026-08-16：general reparameterization-immunity filter

- 新證 L78：若 local error受 global error支配、每個 approximant complexity有限，則任何 unbounded
  allowance `g(T)`都可在選 approximant後用 delayed thresholds滿足。故 free-window polynomial或
  subexponential cost不含獨立 rate內容。
- 對全索引套用：AP2/kappa失敗；LB/W13與DN自然尺度固定但已 iff RH；MB1因 `X=T^B`明示而
  通過 filter，卻已在 L51回到 same-scale Möbius-prime-Abel joint cancellation且無存活 producer；
  canonical-system/all-test square仍缺可驗收 operator/domain。
- 另補 DN36的 infinity escape：DN22對每個 `tau>0`供 uniform real high-zero exterior，故 compact
  degree exhaustion確能捕捉所有 transition。
- 目前 project index沒有同時「免疫重參數化」且「有未到RH endpoint之獨立 producer」的候選。
  這不宣稱窮盡數學證法；Goal保持 active，不標完成。

## 2026-08-16：L78 escape toy與 boundary-gauge no-go

- L79用 `ell^2` truncation tail `E_N asymp N^-1/2`證 prescribed `T^-1` rate不能由 qualitative
  closure scheduling得到；確認 L78是量詞filter，不是另一個 iff-RH criterion。
- L80/DN37證 orientation-preserving gauge index formula。nonsingular extending gauge degree不變；
  straightening gauge若不可延拓，其 index exact等於被搬走的未知 winding。margin受
  `sigma_min(A)`控制，ill-conditioning不構成逃生口。
- L81/DN38證 `(H,H_x+aH)`於 simple zeros的 vertical phase velocity永遠為 `H_xx/H_x`，與
  a、`a_t`、`a_x`無關。DN32第1/35零點反號因此排除全部 first-order gamma shears。
- gauge型 nonmonotone producer到最小失敗點；direct theta-arithmetic homotopy仍未反證。Goal active。

## 2026-08-16：theta-mode truncation與 amplitude collision裁決

- 新增並通過兩份 256-bit Arb證書。L82/DN39證 first theta mode在
  `20.625346...+2.697151...i`有唯一 simple nonreal zero。
- L83/DN40以 Wronskian interval Newton證 `T_1+lambda T_2`於
  `lambda=0.916291688...`,`x=22.142377661...`有 regular real double zero；`h_2`與Hxx均不含0。
- 新證 L84/DN41：full modular derivative cancellation只在 infinite sum成立。每個 finite truncation
  `K_N'(0)>0`，故 transform real-tail為負 `x^-2`、real zeros有限；order<=1 Hadamard迫使 total
  zeros無限，所以每個 finite N都有無限 nonreal zeros。
- finite theta truncation LP base整族關閉；direct mode line亦實際撞 wall。下一候選必須保留 exact
  modular completion，不可把 arithmetic shifts當小 tail。RH未證，Goal保持 active。

- L85/DN42再把 unit partial no-go升為 entire finite span：all odd boundary jets若消失，exact
  negative-u expansion與 Vandermonde迫使 coefficients全0；否則首 odd jet給 algebraic Fourier tail。
  因而任意 nonzero finite real theta combination均有無限 nonreal zeros，有限 coefficient detour全滅。

## 2026-08-16：horizontal-shift infinite modular topology audit

- finite-mode全滅後切換既有 infinite modular family `Xi(x+ia)=A+iB`。
- 新證 L86/HS12：`(A,A_x)` collision Jacobian為 `-(1/2)partial_a(B_x^2)`，harmonic toy
  `x^2-a^2+3a-2`在 a=1,2給相反 orientations；DN27 one-sign mechanism失效。
- 新證 L87/HS13：改用 analytic `(A,B)`則 Jacobian為 `|Xi'|^2`全正，但 boundary degree正是
  argument principle；strip zero-degree iff RH。
- HS topology因此不是新 leverage；coupled Bezoutian route僅在有新 arithmetic identity時存活。
  RH未證，Goal未完成；依使用者階段收尾要求，本輪後 paused。

## 2026-08-16 continuation：HS5 schema-equivalence audit

- L88/HS14：若 `T_a,L_a` 未先由已知資料指定，positivity-preserving decomposition的存在性
  iff `K_(a/2)>=0`；`T_a=0,L_a=K_(a/2)` 給反向平凡 witness。
- 這關閉了把「待找 coupled identity」當成 active lemma的做法；它只保留作未來顯式 construction
  的驗收條件。下一步轉回 MB1作 natural-scale/equivalence audit。RH未證，Goal active。

## 2026-08-16 continuation：MB1 global reduction與 targeted literature audit

- 新證 L89/AP9/G251/strategy124：`B<2m+1`時 local window與 global norm相差 `o(1)`，所以
  MB1 iff explicit global norm沿 X-subsequence消失；T/B沒有 arithmetic內容。
- support-X Nyman/Burnol lower bound排除 power decay強化，最可能尺度僅 logarithmic。
- 只查 named converse gap：arXiv:math/0205003 與 math/0002254均辨識 Selberg log mollifier；
  前者改用 varying power tilt，後者證 additive uniform convergence但明說 endpoint weighted L2
  仍由 Riesz--Mobius scalar控制，conditional full convergence另加 zero separation。
- 因 Abel correction不同，文獻不裁決 MB1；它仍只剩 AP7.2 whole joint cancellation regression
  test。RH未證，Goal active。

## 2026-08-16 continuation：inverse-zero-derivative multiplicity audit

- L90/AP10/G252/strategy125：arXiv:1211.5191 的 conditional optimal rate依賴
  `sum|zeta'(rho)|^-2`，故先驗排除 multiple zeros；不能從 RH alone取得。
- higher Laurent residue只把依賴搬到 multiplicity階 derivatives。此結果關閉 conditional
  optimal-polynomial shortcut，但不反證 MB1；AP7.2仍是 separation-free核心。Goal active。

## 2026-08-16 continuation：AP7.2 non-literature producer audit

- 新證 L91/AP11/G253/strategy126：fixed-log residual是 sharp Abel-corrected residual的 exact
  log-Cesaro mean；energy derivative是無固定號的 cross-scale inner product。
- scalar step反例排除 generic monotonicity，Jensen則丟掉唯一可能 joint cancellation。故目前沒有
  非文獻 producer；Möbius-specific correlation theorem尚未出現，AP7.2封存為 regression test。
- 下一 construction必須 natural-scale、reparameterization-immune、separation-free。RH未證，Goal active。

## 2026-08-16 continuation：Pólya 表示切換的立即反駁

- 直接測 `Phi_s=P^(1-s)Phi^s`，其中 `P=exp(-2pi cosh u)` 且 transform為 classical
  `K_(ix)(2pi)` real-zero model。
- degree `<=8`、shift `<=40` 的 Jensen scan全過；但 worst margin恰在最大 shift且遞減，沒有
  uniform-in-degree內容。實零掃描定位第二、三零點 collision。
- 256-bit Arb/Krawczyk嚴格證明唯一 regular double zero位於
  `s=0.0031021250408869274...`, `x=13.165805196244539...` 的小盒；180--300 nodes
  另獨立穩定到50位。`Hs<0,Hxx<0`，所以增加 s 後該 pair離開實軸。
- 最小失敗點距 Pólya base僅約0.31%。此 geometric homotopy封存；下一候選不得只是換 scalar
  interpolation law或以 finite Jensen pass作依據，必須由表示本身先驗排除 collision。RH未證，
  Goal保持 active。

## 2026-08-16 continuation：exponential-wall rank-one interlacing no-go

- 改用自伴表示而非 scalar kernel homotopy：測 P3 explicit `A_0` 的 energy-independent rank-one
  boundary change。此表示若成立，自伴 Sturm理論會先驗阻止 nonreal collision。
- 256-bit Arb證 `beta_3<gamma_4<gamma_5<beta_4`，數值分別為
  `29.36991955...<30.42487612...<32.93506158...<33.38315787...`。
  同一 consecutive core gap有兩個 Xi zeros，違反 rank-one interlacing。
- finite-degree collision-free path並非空條件：逐根線性搬移即全程 hyperbolic；但套 Xi會使用未知
  target roots而循環。故下一候選須是 primes/theta先驗定義的 singular/infinite-rank domain或
  independent operator，並帶 actual resolvent/projectors。Goal active。

## 2026-08-16 continuation：fixed finite rank 的全域量詞排除

- `probe_bessel_xi_counting_discrepancy.py` 顯示到 `T=1000` 仍有
  `0<=N_Xi-N_A0<=2`；因此 finite data確會讓 rank-two看似存活。
- 針對 named counting gap只查 Dunster imaginary-order Bessel asymptotic與 Dobner unconditional
  `S(T)` large deviations。前者給 `N_A0=M(T)+O(1)`，RvM給 `N_zeta=M(T)+S(T)+O(1)`；
  後者使 S positive unbounded，故 discrepancy無界。
- fixed rank resolvent perturbation/finite-deficiency extension的 counting差由 rank一致有界，矛盾。
  所有 fixed finite rank因此嚴格排除；下一候選必須 genuinely singular/infinite-rank或 independent
  arithmetic operator。Goal active，不標完成。

## 2026-08-16 continuation：prime point-scatterer mixed-orbit no-go

- 測 genuinely unbounded/singular 的具體表示：單一 A0 channel 在 `L_p=logp/2` 放 self-adjoint
  point scatterers，使 boundary round trip精確長 `logp`。
- 二點 determinant lemma給 unavoidable cross term `-g_pg_qG_pq^2`。p=2,3 時其 shortest
  exponent length為 `log(3/2)<log2`；Euler log沒有任何 prime-power term可匹配，且後續 primes
  無法取消最短錯誤 exponent。
- 同 channel local scatterers因此在兩個 primes即失敗；分離 channels則已由 P9--P10 density no-go
  排除。下一候選須 genuinely nonlocal，選擇性保留 same-prime repetitions而消去 distinct-prime
  paths，並維持單一 arch phase volume。Goal active。

## 2026-08-16 continuation：prime defect fixed-drift no-go

- 對 named nonlocal-projector obligation直接算 local generator：在
  `L2([0,logp],e^t dt)`、boundary `f(logp)=p^-1/2f(0)` 下，exact有
  `A_p=-I/2+K_p`, `K_p` skew-adjoint。
- 因而 finite/infinite direct sum及任何 reducing positive quotient都保留 real part `-1/2`；不能把
  Euler local zeros變成 critical-axis spectrum。平移 `+1/2`會把 factor改為 `1-p^-x`，破壞目標。
- unitary dilation只把這些 zeros變成 compression resonances（P31），不是 positive spectrum；普通
  Hodge/intertwiner又已由 P22/P25排除。下一候選必須明示 singular arch--prime coupling與新的正 norm，
  不能只寫「nonlocal projector」。Goal active。

## 2026-08-16 continuation：finite drift pairing / infinite accumulation audit

- exact 2x2 toy證 opposite `+/-1/2` drifts在 `q>1/2` 時有 positive Lyapunov metric與純虛譜；
  因此 singular arch--prime acceptance condition在 finite dimension非空。
- p-th circle spacing為 `2pi/logp`。任 prime-dependent block shift `c_p`後，都可選整數 k使
  `|2pi k/logp+c_p|<=pi/logp->0`。故 infinite direct sum必在0累積，無 compact resolvent/Fredholm
  spectral determinant；任意 finite cutoff都看不到此失敗。
- 存活 coupling須先 nonlocally摧毀 prime lattices的 local accumulation，同時又不能產生 P40 的
  distinct-prime mixed orbits。目前無 explicit construction；Goal active。

## 2026-08-16 continuation：positive cross-prime cumulant dichotomy

- 對 P42 所需 mixing，寫 natural length-covariant trace-class blocks
  `K_pq=e^(-s(logp+logq)/2)B_pq`。self-adjoint positivity給 second cumulant
  `Tr(B_pqB_qp)=||B_pq||_HS^2>=0`。
- 此項 length為 `log(pq)`；Euler log對 distinct p,q係數exact為0，unique factorization排除任何
  higher cycle同長取消。故 exact determinant強迫全部 off-diagonal blocks為0。
- 結合 P42：不 mixing則0累積，mixing則 forbidden Euler cumulant。ordinary trace-class、orthogonal
  prime grading、semigroup length covariance的 nonlocal route整族封閉。只剩破壞其中至少一假設的
  singular construction；scalar regularization已有 P31--P33 projector no-go。Goal active。

## 2026-08-16 continuation：positive Euler determinant classification

- 去除 P43 的 orthogonal-grading假設：對 `K(s)=sum p^-s A_p`, `A_p>=0`，比較 exact Euler
  log-det的 p、p平方、pq係數。
- exact得 `TrA_p=TrA_p^2=1`，故每個 A_p是 rank-one projection；distinct pq再給
  `TrA_pA_q=0`，故 ranges互相正交。
- 因此 positive trace-class Euler realization唯一到 unitary equivalence，就是 prime diagonal model；
  nonorthogonal mixing沒有逃生。結合 P41--P43，此整類 ordinary positive determinant route關閉。
  signed/super與 scalar-regularized alternatives分別已有 P22及 P31--P33 no-go。Goal active。

## 2026-08-16 continuation：P21 prime-operator trichotomy handoff

- ordinary positive determinant由 P44 rigidity退化為 diagonal model，再由 P41--P43關閉。
- exact fermionic superdeterminant由 P22 unique-factorization parity與 P25 closed-intertwiner no-go關閉
  ordinary Hodge realization。
- Schatten/zeta regularization由 P31--P33證只保 easy high-power tail，hard divisor在 scalar
  counterterms且無 spectral projectors。
- 因此目前 explicit P21 operator route整體嚴格排除；「singular cohomology」在未給 positive norm、
  closed domain、self-adjoint induced generator與 spectral determinant前只是驗收規格。這不排除未知
  P21外構造。Goal保持 active，下一棒切換表示而非再包裝 prime determinant。

## 2026-08-16 continuation：translation-compensated Hodge / minimal finite audit

- prime creation乘 arch translation，exact得 `Q^2=0,[H,Q]=0` 與 scalar Hodge Laplacian。
- `sigma>1/2` bounded但 acyclic；critical `sigma=1/2` 因 `sum_p1/p` 令自然 strong-sum domain不 dense。
- 最小 finite model中，一個 prime在 `l2(Z)` 可同時保 dense domain、固定權重、compact resolvent，
  所以三條件沒有抽象矛盾。
- 兩個 primes已不同：global translations使 eigenvalue orbit `lambda-m logp-n logq` 稠密，故 spectrum
  不 locally finite。這是早於 infinite cutoff的 sharp no-go。
- 詳見 `translation_compensated_hodge_audit.md`、P45、strategy136、G262。Goal保持 active。

## 2026-08-16 continuation：executable unilateral Hodge probe

- 新 script `experiments/probe_unilateral_prime_hodge.py` 用 exact Fractions建立 finite prime/boson boxes。
- 1、2、3-prime runs全驗過 `Q^2=0`、energy commutator為0、Hodge無 off-diagonal error，kernel維數
  `2^|P|`，full supertrace等於 harmonic supertrace。
- exact結果為 `product_p(1-p^(-(N+1)s))`；top-boundary classes隨 N逃向無窮，極限為1。
- unilateral repair因此成功保 domain與 discrete spectrum，卻由 boson reciprocal factor精確消掉
  Euler data。P45/P46合併排除所有 naive additive log-prime ladders。Goal active。

## 2026-08-16 continuation：prime convex-transport executable screen

- 新候選避開 spectral shifts：從 pole density為每個 prime-power atom切等 mass、等 barycenter interval；
  disjointness若成立，hinge Jensen直接證 Suzuki B46 sign。
- `probe_prime_convex_transport.py --limit 100000 --dps 70` 解9700個 parcels；first overlap為7--8，
  大小 `0.0249504358010953773`，最大方程 residual `<9e-46`。
- 以上是高精度數值證據，尚缺 interval enclosure；不得稱嚴格 no-go。
- 合併7、8後的 parcel通過70-digit full hinge minimum test，margin約 `0.0045857897`；只證最小 pair
  數值存活，不含 uniform cluster或 infinite conclusion。
- 另修正 P46 scope：cancellation只由 complete ladder partition function推出，不由 commutator單獨推出。
  RH未證，Goal active。

## 2026-08-16 P47 completion：Arb certificate for 7--8

- `certify_prime_convex_transport_7_8.py` 以256-bit Arb與2D Krawczyk嚴格包住 n=7、8 parcels及 merged
  parcel；single overlap為 `0.02495043580109537726196 +/- 6.16e-24>0`。
- merged parcel包含兩 atoms；middle derivative在兩端異號且 strictly increasing，interval Newton包住
  唯一 stationary point。hinge minimum為
  `0.0045857897154596318447348191 +/- 6.46e-29>0`；outer intervals由單調性接到零端點。
- 故 P47 minimal single/pair case已完整嚴格裁決：single方案失敗，pair repair存活。uniform clustered
  transport仍為 G264，不由本證書推出；尤其 hinge margin隨 prime height的衰減率尚未測。
- RH仍未證，Goal未完成；本階段收尾後 paused。
