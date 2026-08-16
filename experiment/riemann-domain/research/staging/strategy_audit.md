# RH 研究路線稽核（2026-08-14）

本文件只記錄目前 workspace 中已實際推導的路線、嚴格反例與最小未閉合
obligation。數值只可選候選；表中「排除」均有解析證明或 exact verifier。

| 路線 | 真正 uniform 輸出 | 已排除的捷徑 | 最小未閉合項 |
|---|---|---|---|
| Xi Jensen | 所有 degree 的 hyperbolicity | degree 3、global J12、C 完全單調、positive raw moments 均不足 | Xi-specific all-r Gram 或可初始化且對 Pascal adjacent sums 封閉的 cone |
| PF∞ / Pick / Stieltjes | infinite Toeplitz PF∞；等價地 `G'/G` anti-Pick；等價地全部 Stieltjes Hankel pivots非負 | 三者只是同一 obligation；正 mixture與有限 pivots不足 | 直接由完整 theta arithmetic證 all-size signs |
| Theta mixture | compound determinant的逐尺寸正性 | 第一 theta saddle、正 shifts、high-moment theta-tail smallness不足 | 同時控制 T1 envelope與 `sum n^-1/2 delta_(log n)` 的算術結構 |
| Li / Chebyshev | `E_n` 負部任意底數次指數；等價 D10 signed Laguerre bound | finite Li positivity、prime項逐項符號、PNT error乘 kernel絕對值不足 | `Q=x-psi` 與 `L_(n-1)^2` 的 uniform 單側 oscillatory cancellation |
| Nyman–Beurling | 受約束 mollifier L2 error趨零 | 自然 Möbius端點、Gram對角占優、Gram total positivity不足 | 臨界線上近似 `-1/zeta` 的一致 mollifier estimate |
| Chebyshev mean square | RH-scale weighted/dyadic prefix energy | PNT一階資訊、只控短 dyadic scales不足 | 全尺度 `Lambda-1` correlation／低頻 L2 控制 |
| 自伴譜行列式 | `G/G(0)=det(I+wA^(-1))`，一次給 resolvent anti-Pick 與 all-size Gram | 事後把未知零點平方指定為 spectrum 屬循環 | 從 theta/primes 獨立構造正自伴 A 並證 determinant identity |

Li 列在 2026-08-16 有一項嚴格放寬：LS1 證 RH 假時負指數逸出為
syndetic，所以 uniform 逐項 bound 並非必要。只要證任意指數負門檻的
違反集合為 density zero，或取得任意長的好 n-block，已足以推出 RH。
新的最小缺口是從 D10 signed Laguerre arithmetic 證這個密度／block 輸出；
它仍不能由 PNT error乘核絕對值或有限 VERIFIED batches取得。

## 1. degree 3 的最終分類

1-ulp 修正後的 J55 證明完整且只屬 cubic。它提供：

- `J_(2,n+1)=J'_(3,n)/3` 的 Rolle interlacing；
- log-derivative Stieltjes S-fraction 的前兩個正 pivots。

它不提供相鄰 cubics 的橫向 common interlacing，也不提供第三 pivot。
以下 exact results 封閉所有目前提出的低階升階猜想：

- `experiments/verify_degree3_not_degree4.py`：所有 shifted cubics甚至 global J12仍可
  quartic失敗；
- `experiments/verify_finite_logderivative_not_uniform.py`：有限 complete-monotonicity
  signs與前兩個 pivots不升階；
- `experiments/verify_complete_monotone_j12_not_uniform.py`：J12 加 C 的 Hausdorff
  complete monotonicity仍在 degree 10 失敗；
- `experiments/verify_beta_moment_j12_not_uniform.py`：compact positive raw moments加
  global J12仍在 quartic失敗。

結論：停止所有逐 degree／逐 minor／逐 moment certificate。

## 2. 三個「全正」名稱其實是一條路

令 `G(w)=sum gamma_k w^k/k!`、`h=G'/G`。下列目標互相轉換：

- `c_k=gamma_k/k!` 的 PF-infinity；
- `Im h(z)<=0` (`Im z>0`)；
- `b_m=(-1)^m h^(m)(0)/m!` 的兩族 all-size Stieltjes Hankel PSD；
- 全部 S-fraction pivots非負。

它們提供不同證明介面，但不是四個獨立成功機率。若沒有從 Phi 或 theta
arithmetic導出的 independent sign identity，只是 RH 的等價重寫。

## 3. theta arithmetic 的精確責任

`Phi(u)=int T_1(u+a)dmu(a)`，其中

`mu=sum_(n>=1)n^(-1/2)delta_(log n)`，

且 `int e^(-sa)dmu=zeta(s+1/2)` (`Re s>1/2`)。mu 只有局部有限性；總
質量及普通正 moments發散。故 standard finite-moment Gram/Andreief不能
裸用，damping removal亦須另證保 sign。

J14 只說 coefficient index很大時高 theta terms相對小；它不控制固定
shift `n=0` 且 Jensen degree趨無限的 regime。這是 saddle route無法自然
uniformize 的精確原因。

## 4. 仍可接受的新進展門檻

下一個候選只有符合下列至少一項才算推進：

1. 給出 all-r Gram/compound factorization，且 integrand或 operator positivity
   可直接由完整 Xi theta arithmetic驗證；
2. 給出比 full compatibility弱、可由 Xi 初始化、且在
   `F_j -> F_j+F_(j+1)` 下封閉的新 cone；
3. 對 D10 的 signed Laguerre transform給不預設右半臨界帶 zero-free 的
   單側次指數 bound；
4. 對 NB11 建不預設 `1/zeta` 解析性的 uniform mollifier estimate；
5. 對 Chebyshev prefix energy建立真正跨所有 dyadic scales的算術相關界。

以下不再計為進展：更多 finite VERIFIED batches、有限數量 pivots/minors、
positive-mixture argument、只用 PNT `psi(x)=x+o(x)`、或把上述等價判準換名。

C4 已確認 Li/Chebyshev兩列也不是獨立成功機率：`Q_p<infinity` 經 Laguerre
orthogonality直接使全部 E_n次指數；但在可由 RH 反推的 `p>5` 範圍，M1
已證此 energy criterion等價 RH。正定化移除了 kernel符號，沒有降低尺度。

## 5. 當前判定

RH 尚未證明。Jensen/moment的一般性升階候選已被精確反例窮盡；尚未排除
的是 Xi/zeta 特有的 all-size arithmetic identity。Li/Chebyshev與 Nyman
路線各有合法但等價承擔 RH 臨界資訊的單一介面，workspace目前沒有可閉合
的無條件 estimate。

## 6. 舊終止條件稽核（已由第 7 節撤回其完備性）

使用者允許兩種終止：完整 RH 證明，或「已明確記錄並窮盡目前可行研究
路徑」。本 workspace 達成的是第二種，不是第一種：

1. J24 指定的六階 local Gaussian enclosure已由 J25--J29 完成，後續
   exact hierarchy、directed moments及 1-ulp 修正重驗在 J55 接成完整
   degree-3 theorem。
2. degree 3 到 all degree 的斷層已由 abstract、global-J12、Hausdorff-C
   及 compact-positive-moment 四層 exact counterexamples逐步封閉。
3. Jensen/PF∞/Pick/Stieltjes/common-interlacing 的非獨立性、可封閉 cone
   與無 base/circular 邊界已寫入 A9--A19。
4. theta arithmetic的離散 shift measure、發散 moment/regularization責任
   已定位；first-theta saddle不能 uniformize fixed-shift degree。
5. Li/Chebyshev 已降成經 Abel 合法化且常數 audit完成的單一 Laguerre
   projection；C2/C4 證其臨界 power response及正定 energy版本仍精確承擔
   RH 尺度。
6. Nyman 已降成 NB11 uniform mollifier；natural Möbius、diagonal dominance
   與 total positivity捷徑均有嚴格障礙。
7. Chebyshev mean-square 已定位到全尺度 prime correlation/low-frequency
   energy；PNT與短尺度 variance反例證不足。

目前沒有尚未執行、且不預設 RH-equivalent estimate的具體候選引理或
verifier。繼續新增有限 degree/minor、等價變換或 heuristic scans會違反
既定停止規則。故依使用者指定的「目前可行路徑已窮盡」條款，本輪研究可
結束；此判定不表示 RH 已解決，也不排除未來出現真正新結構後重新開啟。

## 7. 重開稽核：先前並未窮盡所有合理攻面

使用者要求重新檢查「已窮盡」是否過強。答案是肯定的：第 6 節只窮盡了
當時已具體化的 Jensen/moment、Li/Chebyshev、Nyman 與 mean-square 路線，
不能量化成對所有未來數學構造的窮盡。

`spectral_toy_route.md` 已在 `P_q(T)=1+qT^2` 的 known-critical-circle toy
上完成最便宜測試。Neumann--Dirichlet Laplacian A 滿足

`cosh(log(q)sqrt(w))=det(I+wA^(-1))`,

其 resolvent trace一次給 anti-Pick 與兩族所有尺寸 Hankel Gram PSD。這
證明「獨立自伴 operator -> spectral determinant」是一個先前未單列、且
結構上能處理所有 degree 的介面。

toy 也顯示核心沒有消失：一般 quadratic factor 的 critical-circle bound
恰對應 boundary phase unitary。Riemann 情形若事後以未知零點造 operator，
仍是循環。新路線的最小非循環 obligation 是從 theta/primes 獨立構造正
自伴 A，並證 `G/G(0)=det(I+wA^(-1))` 或等價 resolvent identity。

另須區分兩種完全不同的 operator 表示。由正 Fourier measure 自動得到的
`Xi(z)=<1,cos(zU)1>` 只是自伴 U 的 matrix coefficient，K2 已證不足；
只有 determinant／resolvent trace 型表示才產生所需全尺寸正性。

乘積 closure 已完成稽核：兩個 spectral determinants 的乘積由正自伴算子
直和實現，Pick--Loewner kernels相加；可數乘積只需 inverse trace norms
可加。但 Xi theta representation是和，不受此 closure 保護；zeta 的逐
prime Euler factor在 `s=1/2+iz` 又各有 `Im z=1/2` 的 poles，不能各自作
正自伴 determinant。故可行 operator 必須全域重建，不能逐 theta component
或逐 prime local factor拼裝。

正和的另一可能 closure（common interlacing）也已對 fixed-scale theta
components排除：`cosh(u sqrt(w))` 的 eigenvalue counting為
`N_u(R)=u sqrt(R)/pi+O(1)`；不同 u 的 counting差無界，而共同交錯要求差
至多 1。故全域 operator若存在，必須耦合後重新產生 spectrum。

進一步的循環／密度稽核見 `spectral_archimedean_route.md`。任意正自伴 A
滿足 Xi determinant 的「存在」本身等價 RH；但 regular finite-interval
Sturm--Liouville又因只有 `O(sqrt(lambda))` 的 counting，無法匹配 Xi 的
`sqrt(w)log w` determinant growth。新的具體 core 是
`A_0=-4d²/dx²+16pi²e^(2x)`：其 determinant
`K_(sqrt(w)/2)(2pi)/K_0(2pi)` 由 Bessel/Gamma 漸近精確匹配 Xi 的全部
archimedean exponential growth，relative factor只剩 polynomial growth。
新最小缺口因此收斂為：由 prime lengths `m log p` 構造 A_0 的全域
self-adjoint perturbation並證 relative determinant identity。

theta 與此 core 又有 exact Morse bridge。令
`phi_n=T_n/(2e^(u/2))=y_n(2y_n-3)e^(-y_n)`、
`y_n=pi n²e^(2u)`；直接微分給
`[-d²/du²+4y_n²-20y_n+4]phi_n=0`，且可 factor成 `Q_n^*Q_n`。
一般 resolvent solution是
`z^(-1/2)W_(5/2,sqrt(1+w/4))(z)`。因此 theta summands精確來自 shifted
positive Morse channels，而非僅漸近相似。

這也開出一個未被 determinant-sum反例排除的介面：以 self-adjoint star
boundary condition耦合 channels時，secular equation是正權 Weyl
m-functions之和。尚缺的是證這個 exact Weyl sum重現 Xi log derivative；
在此之前只算候選，不算 RH 進展完成。

後續 Weyl-density audit 已排除其 naive 版本。有限 N 個 Morse channels會
產生 N 份 `sqrt(lambda)log lambda` 主項；全部 n channels的 phase-volume
總和更為 `Theta(lambda^(3/4))`，皆與 Xi 的單份
`Theta(sqrt(lambda)log lambda)` 不符。固定 boundary coupling不改此主階。
故 Morse identity只能作 A_0 的 auxiliary/relative data，不能把 channels
直接 star-assemble 成 Xi spectrum。

infinite-sum 收斂也已補齊：`m_n(w)=-2pi n²+4+O_K(n^-2)`，故可用
square-summable boundary weights或減去 real constants正常收斂。但各 m_n
的 Dirichlet poles有同號 residues，正權 `c_n²` 無法 cancellation；Weyl
level-set zeros遂繼承 union poles 的 `Theta(lambda^(3/4))` 密度。故不是
「和未定義」造成失敗，而是任何標準 self-adjoint positive star sum即使
定義良好仍有錯誤譜密度。

因此目前狀態改為「研究重開」：沒有 RH 證明，也沒有聲稱此 operator 已
存在；但不再聲稱所有可行研究路徑已窮盡。停止規則仍禁止有限 degree／
minor batches。

prime side另有 exact self-adjoint但錯 type 的表示：對
`H_P=diag(log p)`，`zeta(s)=det(I-e^(-sH_P))^-1` (`Re s>1`)。這是
semigroup/partition determinant；`p^-1/2` 可由帶 leakage 的 unitary
scattering dilation產生，但 local singularities是 resonances。關閉 leakage
會新增 mixed periodic orbits。因此此表示證明 prime Hilbert space並非問題，
也精確定位缺口在「open resonance determinant -> compact resolvent
determinant」的全域轉換。

`modular_scattering_route.md` 顯示 gamma+zeta 的全域 self-adjoint scattering
recombination其實已存在：`varphi(s)=Lambda(2s-1)/Lambda(2s)`。RH 等價於
非平凡 scattering poles全在 `Re s=1/4`，而非 physical line `1/2`。
任意位置的 half-plane Blaschke factor同時滿足 boundary unitarity、reflection
與正 Poisson time-delay，故這些一般 scattering性質仍不足。缺的是 resonance
generator在非平凡子空間上的強 identity `Z=I/4+iT`、T self-adjoint。

依 nudge 再加入 distribution trace test。Euler contribution的 inverse
Laplace kernel是
`-(2sqrt(pi t))^-1 sum Lambda(n)n^-1/2 exp[-(log n)^2/(4t)]`。它排除
`A=A_0+V` 且 V sign-definite trace-class 的 additive模型：未修正 Xi/core
ratio先有 `w^(9/8)`，修正後 prime factor又是 `O(2^-sqrt(w))`，與任何非零
固定符號 trace moment的 algebraic resolvent tail不符。modular scattering
仍以 signed spectral-shift distribution通過此測試；缺口是把它提升為正
離散 point-spectrum measure。

MS8 將缺口改成可操作的 two-sided contraction lemma：若同一正 Hilbert
norm下 `exp[t(Z-I/4)]` 及其 inverse對 t>=0皆 contraction，兩者互夾即迫使
unitary，從而 `Z=I/4+iT`。目前 scattering只給 forward/incoming與
backward/outgoing的不同空間或 pairing；尚缺由 modular/Hecke arithmetic
證它們共享同一 positive norm。

Hecke 作為該 norm來源的 naive 版本亦被 MS9 排除：Eisenstein的
`T_p` eigenvalue `p^(s-1/2)+p^(1/2-s)` 只在 physical line自動為實；RH
target resonance line `Re s=1/4` 上仍一般複數。故 resonant states不能直接
加入一個保持 T_p self-adjoint 的正 completion。Hecke至多提供 paired/
biorthogonal資料。

common norm 的兩個自然構造亦完成稽核。cusp exponential weight只選
integrability half-plane；full-line時只是把 translation line人工平移，
half-line時又只有不可逆 compression。Hardy/de Branges--Rovnyak kernel則
對任意 Blaschke zeros自動正，仍只給 one-sided contraction。

全域 common norm精確等同 Weil explicit-formula quadratic form：在 RH下
zero side為 `sum |g_hat(rho)|²`，而對所有 convolution squares非負亦反推
RH。故下一個非循環輸出必須是 prime+archimedean side的 all-test-function
square factorization；僅把 Weil form命名為 norm不算進展。

`weil_square_route.md` 以 unitary Frobenius toy精確展示合格輸出：
`sum c_m conj(c_n)Tr(U^(m-n))=Tr(P(U)P(U)^*)>=0`，一次涵蓋所有 tests。
Riemann prime contraction `diag(p^-1/2)` 不能藉 similarity變 unitary（spectrum
不在 unit circle）；unitary dilation只給 compressed matrix coefficients並
新增 channels。故缺口是 prime+gamma Weil form的真正 all-test square，
不是換 norm或擴大空間本身。

MS13 精確回答 pairing nudge：functional-equation reflection
`s->1/2-conj(s)` 的 off-line二點 orbit，其 natural Hermitian pairing block
為 `[[0,r],[conj r,0]]`，必有一正一負 eigenvalue。因此 pairing正定本身
已強制 fixed line `Re s=1/4`，等價承擔 RH；只有 prime/gamma square先驗
證正才是非循環進展。

## 8. Weil prime form 的新 uniform 介面

先前「只剩 W4.1」仍過於抽象。`weil_square_route.md` W5--W7 已在
log-variable 重建 exact operator：第 p 個相關 form是
`||D_pg||^2-||g||^2`，其中 `D_p` 是 translation 的 Poisson resolvent。
其 multiplier跨過 1，所以逐 prime dilation不給 defect positivity；另有
解析 Gaussian test證 gamma/pole block本身可為負，排除直接 Schur base。

但利用 `-2Re<g,T_ag>=||g-T_ag||^2-2||g||^2`，支撐長度 A 的完整 prime
項可精確寫成非負的 prime-power difference energy `E_A` 減去
`2S_A||g||^2`。因此尚未窮盡的具體路徑是證 uniform-in-A 非局部 Poincare
不等式 W7.5，最好由一個包含 finite primes與 archimedean place的共同
adelic isometry/projection theorem推出。這若成功會一次處理所有 tests；
它不是 degree-by-degree 擴張。尚未完成之處是共同 isometry，而不是更多
Weil criterion改名。

W8 再改善此介面：利用 digamma recurrence，把 pole kernel中的四個
exponential positive kernels轉入 gamma，得到嚴格正 multiplier
`Re psi(17/4+it/2)-log pi`。完整 form遂成 `Q_W=B_4-2R_4`；`B_4` 已有
無條件 coercive norm，`R_4` 只含 von Mangoldt measure與顯式 continuum
kernel `w_4` 的相關差（`w_4` 在 `a>=log2` 正，但短端點區間有符號）。
這是真正的新結構性化簡；但 `2R_4<=B_4` 對所有
tests仍是尚待證的 RH-scale算術不等式，不能以 PNT或 total variation替代。

Selberg identity另給真正 all-k 的正階層：`Lambda_k=mu*log^k>=0` 且
`Lambda_k log+Lambda*Lambda_k=Lambda_(k+1)`。這是目前最具體的升階候選；
障礙是 additive convolution在 autocorrelation test中形成 `a+b` cross
pairing，而 Hilbert squares形成 `a-b`。下一研究點是能否用 number operator
與整個 hierarchy構造無額外 mixed orbits的 doubled/Fock block positivity。

後續 audit 已把此候選再分類。正確的 all-size object是
`M_j(n)=j!Lambda_(omega(n)+j)(n)/(omega(n)+j)!` 的 box-moment Gram；裸
`Lambda_k(p^m)` 甚至 2-by-2 Hankel即失敗。box Gram雖為真，仍只在
`a+b` convolution algebra；單原子 `delta_L` 證明此正性不蘊含
`a-b` positive-definiteness。故「繼續升 k」停止；唯一可能的 bridge須
來自 theta/Tate/adelic reflection，並另證沒有 off-line residue。

W12 進一步關閉 archimedean square本身：`B_4` exact 等於正 mass
`c_4||g||²` 加權重 `e^(-17a/2)/(1-e^(-2a))` 的連續 translation-difference
squares。故 G20 已不是「找任意 square」，而是證 W12.4：長 prime-shift
discrepancy由局部 logarithmic Sobolev energy控制。這個 cross-scale
operator large-sieve才是目前最小、非有限維的算術輸出。

W13 顯示 W12.4 與 Chebyshev/Mellin列其實在 boundary-residue層合流：
regular critical-line points上 functional equation給 exact multiplier equality
`2ReF_4=b_4`，正 zero measure只來自右側 Poisson boundary deltas；off-line
zeros則是 contour-crossing residues。故 pointwise multiplier比較沒有餘裕，
而「無額外 residues」正是 RH。真正新證法須在 Euler側、contour shift前
產生 reflection positivity。

W14 已確認 large-sieve輸出的強度：polynomial interpolation乘 Gaussian可
隔離任一 off-line quartet的負 pairing block，故 all-test W12.4逐點推出
RH。這也建立驗收門檻：若新估計只對固定 bandwidth、平均 ordinates或
有限-dimensional tests成立，它只能給 density資訊，不算閉合 G20。

natural Abel continuation亦已由 W15封閉：canonical regularized family
`b_4-2ReF_4(epsilon+it)` 在 `epsilon=4,t=0` 已嚴格為負，證明只用 prime 2
與 rational constant bounds。故不能從 Euler絕對收斂區的局部正性連續
降到 boundary；新的 reflection機制必須不是此 scalar damping family。

natural non-scalar Tate reflection也已分類。theta-sum E exact intertwines
Fourier與 log-reflection，Mellin multiplier是 `2zeta(1/2+it)`；但 ordinary
L2中 multiplier的離散 zeros是 measure-zero，E有 dense range及 trivial
cokernel。能看 off-line points的 exponential rigging則重現 MS13 indefinite
pairing。剩餘非循環輸出只能是額外 arithmetic projection/commutator的
positive trace defect，而非 Poisson unitary或 E range quotient本身。

standard Hardy projection也已由 TR6封閉：其 convolution commutator平方
只是 universal `int|a||g(a)|²`；natural E range projection是 I。任何合格
TR5 construction必須新增真正 arithmetic/adelic projection與合法 semifinite
trace，而非重組這兩個 projections。

TR7 提供第一個真正 arithmetic projection進展：prime-local Toeplitz
rank-m defect乘 primitive `1/m` 正好給 von Mangoldt prime-power weights，
所以 W7 difference energy已有全尺寸 projection squares。未閉合點縮為
adelic index cancellation：必須在保持正 Hilbert trace時吸收發散 diagonal
debt TR7.6並接上 W12 arch squares；supertrace或 scalar renormalization不合格。

TR8 又證 product formula只自然取消 orientation-sensitive signed indices；
positive `X^*X` trace中 real/p-adic infinite boundary strips同號相加。有限
corner normalization可重現 prime weights但不消 debt。故 adelic trace formula
本身仍不足，須有額外 positive cohomology/Schur theorem。

TR9/TR10 將此 theorem具體化：index下降到 cohomology仍只是偶減奇；需
與 scaling相容的 positive Hodge star才會迫使 `Re s=1/4`。local Toeplitz
defects已有 sl2/reversal polarization，但 tensor product新增 mixed-prime
orbits。global complex必須先令 mixed sectors acyclic，再證剩餘 pairing
Hodge-positive；Schur complement所需 cross-norm bound本身就是 W12.4。

TR11 改善此判定：mixed sectors其實可由 symmetric Fock的正 one-particle
projection移除，log derivative exact 是 prime Bose occupation trace。故
不必先解全域 acyclic complex；核心只剩 critical prime trace與 gamma
oscillator之間的 positive operator-level relative trace。這比 signed
cohomology目標更窄，但 contractivity仍未證且等價承擔 W12.4。

TR12 再排除 exact spectral matching：atomic prime lengths不能 isometrically
intertwine到 nonatomic arch length multiplier。合格 map必須是 noncommuting
wave-packet frame，其 smearing error由 W12 Dirichlet norm控制；frame bound
仍是待證核心。

TR13 顯示最便宜的 positive transport也失敗：prime cells的 aggregate
small-displacement density比 q4 budget多半個 power。故任何 surviving
relative-trace map必須是 global oscillatory frame，而非 monotone mass
coupling；普通 PNT不夠。

TR14 給 global oscillatory candidate的精確形式：prime torus Haar正交成立，
且 diagonal debt是 Kronecker distance的長時平均。缺口不是平均 frame，而是
uniform Paley-Wiener restriction，須禁止任意 W14 test集中於稀有 simultaneous
prime-phase recurrences；單純 rational independence只給 density。

TR15 顯示普通 Bessel已接近但未達門檻：power正好降到 1，仍有
`sqrt(log)` loss與未吸收 debt。這是 global oscillatory frame目前最小的
定量缺口。

TR16 顯示 point peak是更強門檻：Haar norm約 `logX`，identity/recurrence
peak約 `sqrtX`。需把每個大 peak收費為 `log|t|gtrsim sqrtX`，且常數對
`A`/`S_A`一致；否則只給 density或 finite-cutoff結果。

TR17 排除「entropy常數必隨維度退化」的疑慮：first chaos有 dimension-free
subgaussian tail。若 prime-log flow的 first return obey reciprocal Haar scale，
可得 `logt>=cX/log²X`。尚缺的是這個 deterministic Diophantine hitting
theorem，而不是 Haar/Bessel本身。

## 9. 獨立 uniform 路徑：de Bruijn--Newman heat flow

新增 `debruijn_newman_route.md`。real simple zeros滿足 exact
Calogero--Moser dynamics；相鄰 gap有 `(d_j²)'=4kappa_j`。exact clock lattice
的 repulsion/crowding完全抵消，故高處 gaps趨零不構成障礙，真正量是 clock
defect的時間積分。此路徑若能由 theta saddle一致證 DN3.2，會一次處理全部
zeros；但一般 backward heat與 kernel positivity不足，尚無該 uniform barrier。

DN6 又把 barrier量化：finite-window clock condition推出
`kappa_j^+<=4epsilon+2/(M+1)`。因此所需 theta theorem必須給每個 gap
約 log-squared寬窗口內的 inverse-log-squared相對 rigidity；平均 pair
correlation或多數 gaps正常均不足。

DN7 明定驗收格式：M、epsilon與起始 gap下界須按 height block一致選定、
涵蓋每個 index和整段時間。adaptive per-gap或 density-one結果不算 RH
barrier。

## 10. TR18 對 prime-torus entropy 的終止稽核

raw hitting theorem為假，而非僅缺工具。固定 t 下 PNT partial summation
產生 `X^(1/2+it)/(1/2+it)` 的 `sqrtX` endpoint coherence；沿 X 子序列，
t=1 已命中 Haar極小的 peak set。故 prime-torus entropy只能保留為平均座標。
正確 quantity必須先扣 arch continuum，再控制 `d(psi-x)`；這使路線回到
centered W12 operator inequality，沒有獨立捷徑。

## 11. 未窮盡路徑的重新排序

不能再聲稱數學上「一切可行路徑」已窮盡。目前仍有四種 genuinely uniform
mechanisms；它們都有明確驗收門檻，但都尚缺新定理：

1. centered Weil/Tate relative trace：證 W12.4 的 all-test operator square，
   且在 contour shift前成立。這是最具體主線。
2. Xi-specific Pick--Loewner／all-r Gram：直接 factorize `K_(-G'/G)`；不得
   退回有限 minors或只用 positive mixture。
3. 單一 archimedean core上的 singular/sign-indefinite global arithmetic
   coupling：須同時證 self-adjointness與完整 relative determinant identity；
   standard Morse star與 sign-definite trace-class potential已排除。
4. de Bruijn--Newman global action：DN8 的 finite system identity
   `(logDelta)'=4sum S_j^2` 可容許 rare small gaps。需建立 height-block
   renormalized discriminant、boundary flux及 theta-side uniform action bound。

modular scattering的 common norm已併入第 1 項；raw prime-torus entropy由
TR18排除。這四項不是四個近完成證明，而是四種尚未被反例封閉的 uniform
機制。下一輪優先 DN8 renormalization或 centered W12 finite-cutoff identity，
因兩者已有 exact square law可供推導。

DN8--DN9 隨後由 DN10 降級：完整有限系統的 velocity action積分精確等於
log-discriminant下降，沒有比 no-collision弱；而近雙根 Schwartz entire
family證 ordinary Fourier Sobolev norms不能控制 zero-sampled velocity。
所以第 4 項只有在找到新的 zero-sensitive theta sampling/frame identity時
才重開。當前操作主線回到第 1 項 centered W12 finite-cutoff form。

centered W16/W17 又收緊第 1 項：prime-minus-continuum是 normalized
Chebyshev error的一階 distribution，而 modulated boxes在每個 regular
frequency形成 equality Weyl sequence。因此「再改善一點 large-sieve常數」
不是存活策略；需要 exact sharp reflection、isometry或 relative trace。

W18/A20 又證第 1、2、3 項在 analytic target層其實合流：
`h(w)=[A4(sqrtw)/2-F4(sqrtw)]/(2sqrtw)`。它們仍可能提供不同構造來源，
但不能當作三份獨立證據；共同核心是從 primes/theta先驗產生 h 的正
Stieltjes measure。

P13 是合流後仍具操作性的座標：直接對 Euler half-plane的 h inverse Laplace，
得到 explicit prime--gamma Theta(t)。證 Theta completely monotone對全部
k,t 等價於構造 h 的 Stieltjes measure，因此一次處理任意 degree。下一研究
只尋找 Theta 的 single positive-measure／semigroup factorization，不做有限
derivative certificates。

P15 防止把 P13降成 boundary positivity：Stieltjes cut measure的正性對既有
critical zeros是自動的，RH內容全在「沒有 off-cut poles」。所以只有能從
arithmetic side同時給 positivity與 cut-plane analyticity的 factorization
才算進展；phase/time-delay sign不算。

P16/P17 把「single factorization」具體化並量出 sharpness：Theta Hankel kernel
須是 Gram且 shifts contractive；其 target moments與單 prime Laguerre項已有
同一 factorial base。故可行構造必須 global、all-size、逐階零損失，不能靠
高階估計常數或 termwise absolute bounds。

P18 提供第一個 explicit positive free channel，但也證 measure-majorization
版本失敗：h_A與 h_F 的 regular Stieltjes densities逐點相等。真正 construction
必須是 sharp self-adjoint spectral transformation（continuous spectrum轉為
zero atoms），不是 density inequality。

P19 排除 ordinary boundary/scattering實作：free measure全域 a.c.，target在
RH下純 point；finite-rank/trace-class self-adjoint changes與 unitary maps保留
a.c. spectral type。存活 operator route因此必須 genuinely singular或
cohomological，不能只是標準 extension theory。

P21 顯示 independent arithmetic determinant其實已存在，但 type錯誤：prime
Euler product是 `det(I-e^-sH_P)` 的 semigroup defect，而 RH需要
`det(I+wA^-1)` 型 resolvent。剩餘非循環 operator工作就是構造保持 exact
quotient的 singular positive cohomology functor；名稱替換不算。

P22 顯示 ordinary supersymmetry也不是該 functor：prime exterior spectrum因
unique factorization無 opposite-parity degeneracy，commuting odd differential
必為零。任何真正 cohomology construction必須離開 bounded exact spectral
intertwining，並承擔新的 positivity theorem。

P23 修正 nudge audit：P17 的 Gamma(k+1/2) growth滿足而非違反 Carleman，
所以 moment uniqueness沒有遺失。P18目前只宣稱由 functional equation嚴格
證得的 regular cut boundary-density equality；off-cut analyticity仍是完整
measure statement與 RH的未閉合部分。

P24--P27 完成 singular-Hodge audit。scattering ratio因 G even精確退化成純
gamma phase；exterior Fock的 fiber Euler characteristic又阻止只靠 topology
改造 grading。剩餘唯一明確 sufficient mechanism是 absolute D_F 的 full
conservative arithmetic realization，且其 hidden G-subspace必須繼承正
nondegenerate energy。證此 hidden metric正性就是尚未取得的新 theorem。

P28/P29 顯示 finite conservative Euler realization確可做到且不新增 mixed
determinant factors；失敗點是 critical infinite cascade。local deviations的
square sum為 `sum_p1/p=infinity`，所以 standard positive unitary-product與
determinant topology都不收斂。新的 theorem必須是 operator-level
renormalization並保留 absolute divisor。

P32 排除 standard Schatten-renormalization補救：det_3在 critical line附近
operator-theoretically良定且 nonzero，所有 zeta divisor被移到 scalar prime-
zeta cumulants。故「正 operator + regularized determinant」仍未把 RH資訊放進
spectrum；counterterms必須自身有新的 positive realization。

P33 完成 Schatten終止稽核：det_q只是絕對收斂的 `m>=q` Euler-log tail，
missing cumulants精確含回 logζ。故提高 regularization order或以 logζ定義
counterterms均屬等價改寫，沒有新的 positivity。

P34 經 nudge 重審後只能保留為 Euler-log bookkeeping。`m>=3` tail在
`Re s>1/3` 確實獨立 analytic且 zero-free；但 `P_1(s)` 的 continuation具有由
`zeta(ms)` 零點產生的 logarithmic singularities。故在臨界帶把
`P_1(s)+P_1(2s)/2` 當成已定義的 two-orbit trace，已預設 target divisor。
它只標記「若有獨立 construction，應匹配哪些 Euler terms」，不是完整 divisor
reduction，也不是 proof-complexity simplification。

P37 完成 moment-determinacy防循環稽核。critical boundary atoms的 positive
measure雖無條件存在，但 arithmetic heat moments另含每個 off-cut pole的
`u^k e^-tu` defect。P18 regular density equality不控制此 defect；P23
Carleman只保證「若 positive representing measure存在則唯一」，不能證存在。
因此 boundary moments + determinacy沒有繞過 P13 all-k positivity。

P24 顯示 Lax--Phillips boundary scattering亦不存活：P21 quotient與 G evenness
使 D_F(-x)/D_F(x)精確退化為純 arch gamma ratio。任何只看 phase/unitarity的
construction都丟掉 zero divisor；必須控制 absolute Jost determinant。

P25 又排除「只把 Q改成 unbounded」：closable exact spectral intertwining仍
由 atomic/continuous projection型態迫使 Q=0；distributional evaluation不
closable。真正 rigging必須同時新建且證明 positive topology，不能借用既有
Hilbert Hodge positivity。

## 10. 2026-08-14 非窮盡性與下一輪路徑稽核

目前不能宣稱窮盡一切可行證法。已窮盡的是本專案中已具體測過的一批自然
捷徑；而且 W18 已證其中 Weil／Stieltjes／resolvent 三種說法是同一
factorization obligation，不能重複計數。仍存活但尚未構造完成的機制有：

1. centered prime--arch all-test square：直接從 W16 distribution構造 sharp
   constant-one factorization；任何 fixed loss、absolute PNT bound或事後 zero
   measure均不合格。
2. de Bruijn--Newman global collision barrier：用 tapered block discriminant
   保留 DN9 external flux，先證一個與 RH無關的 weighted identity及 clock-model
   uniform commutator bound，再尋 theta-side zero-sensitive estimate。
3. arithmetic positive cohomology／canonical system：必須由 primes/theta先定義
   domain、metric與 generator，再證 P21 determinant；由 zeros反造或只用
   scattering phase均屬循環。

三者中第 1 與第 3 最終落在同一 spectral positivity obligation，但 construction
語言不同；第 2 是真正不同的動力學攻面。下一輪優先做第 2 的 tapered identity，
因它有可獨立證明或否證的中介引理；同時只保留第 1 的 exact-square搜尋，不再
擴張 finite-degree／finite-moment證書。

DN12 隨即完成此中介測試：對 product weights `a_ja_k`，weighted
discriminant的 flux commutator在 exact clock上就是離散 Hilbert transform，
其慢 cutoff成本仍是 volume order。故普通 taper被否證；DN攻面只剩帶非局部
clock-PV counterterm的 relative energy。這仍是邏輯上未排除的不同機制，但
在提出該 counterterm前不應列為正在收斂的證明路線。

DN13 給出該 nonlocal線性能量：clock displacement的生成元有 symbol
`pi|theta|-theta²/2`，其 `H^(1/2)` energy可逐 gap控制。然而固定時間 backward
放大率是 `exp(c t_0/d²)`；在 zeta高度即 `exp(c t_0 log²Gamma)`。因此需要
matching超多項式的 theta zero-rigidity，而非普通 clock asymptotic。DN14依
nudge區分 density版：平均能量在首次 collision前可界 bad gaps比例，但沒有
collision index／spectral projector便不能推出 density-one critical zeros。
目前 density版也未產生無條件新定理。

## 11. horizontal-shift HB descent：新增的 uniform deformation介面

`horizontal_shift_route.md` 給出先前未單列的 all-degree base。置
`E_a(z)=Xi(z+ia)`；所有 nontrivial zeros在 `0<Re rho<1` 使 `a>=1/2` 時 E_a
無條件為 Hermite--Biehler，所以
`A_a=[Xi(z+ia)+Xi(z-ia)]/2` 全實零。其 exact HB threshold就是 zeta zero
strip的半寬，故不能由 zeros反證。

新的可構造問題是 HS5 half-shift descent：從 K_a的正 Gram直接以 theta/primes
造 `K_(a/2)` 的 positive defect。若可反覆下降即證 RH；generic harmonic
deformation由 `z²+1-a²` 反例否證，所以必須是 Xi-specific。此路線在 a→0
仍與 W18同一 positivity obligation，但提供一個真 base與升階介面，值得與
W16 centered arithmetic feature配對；有限 kernel positivity不算進展。

HS7 對最自然的 untilting捷徑給 exact positive-measure反例。兩頻率正 cosine
measure可在 `a=log2` 全實零、降至 `a/2` 後非實零。因此正 Fourier kernel、
positive-definite multiplier或普通 convolution smoothing皆不能提供 HS5；
若續此線，必須找到 Phi/prime shifts特有且能跨越此反例的 total-positive
defect identity。

HS8 顯示 untilting multiplier本身確為 positive definite，卻不是
PF_infinity：其 reciprocal Laplace transform `cos(as)/cos(as/2)` 非 entire。
所以「正卷積」與「variation diminishing」的斷層完全顯式；後續若沒有
mu_a--Phi coupled determinant identity，horizontal descent暫停。

HS9 排除「先抽共同 PF_infinity smoothing」：imaginary channel multiplier
`q_a=1/[2cosh(au/2)]` 的確 PF_infinity，且 r_a-q_a也 positive definite；但
PF_infinity convolution在此是會消滅 sign changes的方向，`z² -> z²+a²/4`
已產生 imaginary zeros。只有 A/B聯立的 de Branges Bezoutian可能保存 HB。

HS10 又顯示 half-angle duplication的 real channel exact含回 Xi：
`A_(a/2)(z+ia/2)+A_(a/2)(z-ia/2)=A_a(z)+Xi(z)`。所以任何 descent若把
Xi/K_0項當已知 positive remainder，便只是 W18換名。只有直接由 arithmetic
integral證 Xi與 smoothed B-channel的 coupled Bezoutian sign才是新進展。

HS11 在 known-GRH功能域 quadratic上確認成功機制：
`cos(Lz)-costheta=-2sin[(Lz+theta)/2]sin[(Lz-theta)/2]`，且 Hasse bound使
theta real、monodromy unitary；同一 factorization對所有 horizontal shifts
同時 HB，有限乘積由自伴直和封閉。Riemann缺的正是 shift-independent global
unitary arithmetic phase；local Euler colligations在 critical limit不收斂。

## 12. 目前研究 impasse 稽核

所有已收到 nudge均已轉成明確回應；沒有尚未執行的具體提示。現存路線與
最小缺口如下：

1. W16/W18/P13/HS：須由 centered primes或 theta直接構造 all-test coupled
   positive Bezoutian／Stieltjes measure。boundary density、Carleman、scalar
   smoothing及 continuation均已證不足或循環。
2. spectral/cohomology：須構造 shift-independent global unitary/self-adjoint
   arithmetic generator並保留 absolute determinant。finite Euler cascade、
   trace-class、Schatten、ordinary Hodge與 scattering phase均已封閉。
3. DN heat flow：須有 `exp[-c log²Gamma]` 級 zero-height theta rigidity或新的
   collision index。ordinary taper、Sobolev/action及平均 density機制均不足。

三者最後都需要目前文件中不存在的 Xi-specific global polarization；繼續做
finite degree、finite kernel、數值 moments或等價判準不會推進。沒有新的
arithmetic identity／外部數學輸入前，目前可執行的非循環研究路徑已窮盡。
這不是 RH為假的判定，也不是完整證明；只是本 workspace 現有方法的研究
impasse。

## 13. 聯網後重開：K0 exact bridge、joint wedge 與 Lee--Yang closure

第12節的「現有路徑已窮盡」已被新外部輸入與新 identity取代，不再是最新狀態。
VK6/K0B2 exact證 `B_Xi=(4/pi)T^*K0T`，把最短主命題縮成 continuum `K0>=0`；
Freedman quotient certificate仍只差 `D_trace=C-B^*A^+B>=0` 的 genuine
Volterra/Green Gram，而非 finite closure。

Holland 2608.08682另證 `n^3log^2(n+2)>=Kd^5` 的 joint Jensen wedge；但
A21 的 `J_(d,n)(X/d)->F^(n)(X)` 顯示 fixed `n=0,d->infinity` 本身就是 RH，
不能靠提高 asymptotic階數視為普通尾區。Newman--Wu 1708.08820則關閉
Lee--Yang weak-limit步驟；若能構造 finite known-Lee--Yang laws弱收斂到
`Phi dt/intPhi` 即足夠，現缺 explicit model。

所以目前真正可行研究接口更新為：

1. `K0/D_trace` 的 continuum Hardy--Volterra contraction或 Gram identity；
2. finite ferromagnetic/known-Lee--Yang laws 到 `Phi dt` 的 explicit weak-limit
   construction；
3. Holland wedge向低 shift的 critical-value alternation transport。

2、3目前只有清楚驗收條件，尚無 construction；1已有 exact target與 signed
feature form，仍是優先主線。不得恢復 finite Jensen/KLM batches。

## 14. 新全階候選的即時淘汰與保留

K0B10 曾提出把 double-tail potential的每個 anisotropy係數各自作 completely
monotone Laplace feature。它確實會 uniform推出所有 sizes，但 K0B12 已嚴格證
此 ansatz不可能：非零 `c_0`／`-c_0'` 具 faster-than-every-exponential tail，
而正 Laplace transform必有某個 exponential下界。低階導數正號因此不構成
升階證書；此分叉已停止。

保留下來的新結構是 K0B13/VK10：完整 K0 form不是係數逐階和，而是兩個 shifted
theta Volterra transforms的 cross-energy。Gaussian score constant時它 exact
成 boundary square；Riemann只差 theta deviation residual的 boundary contraction。
這容許 anisotropy orders耦合，避開 K0B12 obstruction。另 ES41 將 VK8 formal
anti-Loewner kernel分類成 operator-monotone正測度表示；若能正則化 theta
sign-symbol，便是 same-sign block的 genuine all-size theorem。

因此不能再宣稱「一切可行路徑已窮盡」。目前有兩個具體、可被證明或反例否決的
continuum子目標：K0B13.6 residual contraction，以及 regularized theta symbol的
ES41.1 representation；前者同時涵蓋 reflected block，優先於後者。兩者目前都
未證，且不得用 finite spectra或 score pointwise sign代替。

K0B14 已再確認前者仍是 RH-scale而非免費降階：boundary split是乘上
`e^(z^2/(2c))` 的 Bezoutian gauge，且 positive Gaussian deconvolution被 Phi尾部
嚴格排除。故 K0B13.6 只有在出現新的 theta coupled factorization時才算突破；
單靠 J5 score monotonicity不列為可完成證明。

VK12/ES42 同時淘汰 ES41 對 standard Laplace symbol的直接套用：anti-Loewner
log-derivative會強迫 positive symbol與 complete monotonicity，違反 Phi尾部。
因此第14節兩個子目標中只保留 K0B13 residual；另一個必先發明不同的 theta
multiplicative transform並重新推導 all-size kernel，不能視為現成路線。

## 15. positive primitive、Selberg量詞與 radial convexity 的最新稽核

K0B15/VK13 已把完整 form重排為有限 storage減 moment-graph cross term，避免
homogeneous primitive的假消去。K0B16 隨即以 exponent gap `(m-n)^2` 排除逐
theta-pair PSD；這具體驗證 Selberg nudge所指出「積分／總和正性不能無條件升為
逐 summand正性」。

完整 theta和仍有一層可嚴格關閉：J5 score單調等價 radial h convex，K0B17的
保測度換元遂證 odd block所有 entries非負。K0B18又顯示 standard Loewner matrix
lift不可能，因 `h'` 超線性而非 operator monotone。故目前不能靠 scalar convexity
繼續升階；唯一合格 K0突破是 L7/VK13 common-range graph factorization，或一個
真正利用 z/s path integration與 theta channel總和的 PSD decomposition。

## 16. 聯網後的 L7/screw 戰略結論

1. L7 不是尚待估計的 ordinary operator norm。`L` 無界，但 causal rational
   block exact給完 boundary/storage；剩餘只有 `iXi'/Xi` 的 off-diagonal
   common-range flux，且它 exact等於 `-2Q_K0`。
2. generic bounded Hankel/Nehari 工具太強：稠密 range上的單邊符號若可以
   ordinary norm 連續延伸，反號即迫 block=0。所以必須是 Xi-specific
   unbounded graph factorization。
3. Suzuki shifted screw family是一個真正 uniform-in-shift 半群，但只向右保正。
   從 `omega>=1/2` 降到 0 需要一個可逆 invariant subcone；現有文獻無此
   theorem，而 full-cone backward positivity 已等價 RH。

因此不恢復 finite degree/certificate。新的優先順序是：(A) 對
`Ran(T_Phi)` 構造可關閉 `iXi'/Xi` poles 的 graph Gram；(B) 構造
shifted-screw semigroup 的 theta/prime invariant subcone。兩者可能是同一個
canonical-system state cone的 Fourier/time 兩種座標，但目前無 intertwiner。

Selberg nudge 又消除一個可能的語言誤導：`Ran(T_Phi)` 投影到
half-line 後在 `H2` 稠密，沒有餘維。因此後續不再把 L7 稱為
「只需對受限子空間證不等式」；它是同一 dense domain 在不同 graph
topology的 RH-equivalent form。同時，K0 parity kernels的 analyticity 排除
finite-order local Sturm--Liouville Green route。優先級因此再縮為：

1. 不除以 Xi 便可辨識的 theta/prime invariant cone；
2. nonlocal/infinite-order resolvent 的 exact positive realization；
3. 直接 K0 coupled Gram。

## 17. PF／Hankel／heat-flow 外部輸入稽核（2026-08-15）

這輪外部搜尋沒有提供 RH 證明，但把三個容易誤判為 uniform升階的方向精確分開。

1. **raw total positivity已排除。** Schoenberg要求 PF∞ transform zero-free；classical
   Phi 的 transform是 Xi，因此已有 real Xi zeros即否證 PF∞。2602.20313v2的
   certified PF5 negative minor再給 finite-order barrier，但不拿電腦證書代替 RH。
2. **PF atoms不能靠正相加升階。** 2602.01248 的關鍵 closure lemma錯誤；兩個
   translated Gaussians的正和有 exact negative `2 by 2` minor。該稿特殊 kernel的
   transform其實是 `2C alpha^-q Gamma(q)zeta(2q)`，zeta difficulty沒有消失。
3. **bounded positive Hankel theorem不適用。** K0 same-sign block是 Hankel
   anticommutator，而真正 L7 flux只能在 unbounded Xi graph上定義。ordinary bounded
   sign theorem會被 dense-range反號論迫使成零。
4. **heat flow給 exact all-size PDE但無 generic descent。** K0B28把 Bezoutian flow
   化成四維 radial backward heat；`z^2+1-2t` 是 exact PSD-to-indefinite反例。

仍保留的新接口只有 K0B29/L9 的 prime Euler--Volterra factorization。它比「找某個
theta cone」具體：每個 prime是 positive causal shift resolvent；但必須找到同一個
含 Archimedean completion的 K0 energy及 telescoping defect。這是目前下一個可做的
all-degree問題。若無法產生該 common energy，就應把此分支記為 Euler half-plane
tautology，而不是再做 finite minors。

K0B30 隨即完成 L9 的 ordinary-norm audit：completion後 prime weights為 `p^-1/2`，
加權 translation norm把 partial products化成參數 `1/2+2sigma` 的 Euler product；
只有 `sigma>1/4` bounded，target `sigma=0`發散。故 prime-positive cone沒有提供
half-shift descent，只把 Euler absolute half-plane換成 operator語言。主線退回
signed prime+gamma telescoping／K0 coupled Gram；這兩者是否可 exact辨識是下一個
非循環問題。

K0B31/ES48 又確認 product closure本身可升任意 degree，但目前沒有可收斂到 Xi 的
positive entire factorization。Pólya-like real-rooted approximants只作 tail與有限
jet matching，沒有 `m->infinity` 的 LP convergence。後續若走 approximation路線，
驗收標準必須是 exponential-weighted kernel convergence足以推出 transforms locally
uniform；否則仍是有限特徵擬合。

依最新 Selberg nudge，K0B32 已把這個標準量化成 exponential-weighted L1 convergence。
Shi第一族甚至在所有 weights都收斂，但 exact收斂到錯誤 LP kernel；原因是 modes
`k/m` 在 1 附近累積，令 fixed-m tail estimate不 uniform。故 approximation分支只在
出現真正以 Phi為極限、跨 `sigma=1/4` 的 LP exhaustion時重開。

再依 Masters' Nudge 作反向量詞稽核：上述 LP exhaustion的「存在性」本身與 RH
等價（RH真時取 constant family）。所以它只能是驗收規格，不能再列作研究降階。
目前恢復的 all-degree支線是 K0B33--34：完整二維 rectangular theta product加
completion differential operator。它的明確成敗測試是能否產生 anti-Wick/Kraus/
star-square；Hudson 已排除 raw Wigner positivity，一般 Weyl-symbol positivity亦不夠。

K0B35 又完成反向稽核：Wigner的 center Laplace transform exact為
`|xi_R(1/2+s+i xi)|^2`，tail Weyl symbol的 transform是其 `s` 導數除 `8s`。
Lagarias criterion使「所有這些 scalar transforms為正」本身與 RH等價。因此
二維 theta分支不得再以 Mellin positivity／horizontal modulus monotonicity當中間成果；
唯一尚未循環的目標是 operator-level completely-positive factorization。

外部 2026 theta-kernel two-sine分解亦經反例稽核。K0B36 的三個 translated
Gaussians同時有 strict log-concavity與 J5型 radial-score monotonicity，Fourier卻含
exact nonreal zeros。因此 positive amplitudes／score anisotropy不是 theta-specific
升階；該支線只在 modular identity能排除 K0B36 並直接給 CP factorization時保留。

Holland 2608.08682 改變了 Jensen 支線的評價：現在確有一個非有限證書的
uniform-in-degree 楔形定理，`d=O(n^(3/5)log^(2/5)n)`。但它明確沒有 converse，
且 n=0 全部在楔形外。MMP finite-free theorem只保持 forward positive-root cone；
其 inverse obstruction排除直接 deconvolution。故不恢復逐 degree/moment證書，亦不以
更高 fixed-order ratio matching替代斷層。Jensen支線只保留兩個硬目標：Xi-specific
reverse shift，或全階 exact finite-free/PF factorization；否則主線仍是 K0 operator CP。

另已完整稽核 Shi 1706.08868 的 claimed real-rooted uniform approximants。其核心
even/odd finite sum在補零項時把正確上限 `2m` 錯寫成 `m`；後續 incomplete-gamma
tail、`m=7n^3` boundary dominance及 U/V interlacing全建立在錯誤 polynomial上。
所以這不是可採用的 L10 construction，也不因其宣稱 Hurwitz結論而重開 LP近似支線。

2026-08-15 外部輸入稽核再得到兩個界線。K0B38 將 K0B37 normal stress逐格點化為
`lambda^2(2mn)^2(3-2lambda m^2e^-s)(3-2lambda n^2e^s)e^-lambda A`；它會換號，
所以雙曲 PDE沒有隱藏 local square。Suzuki 2025 提供真正全階 canonical-chain
語言，但抵達 Xi endpoint等價證
`supp F^-1[(Xi-iXi')/(Xi+iXi')] subset [0,infinity)`。
下一步只保留兩種合格突破：(i) 完整格點和的 nonlocal Green/Rellich cross-channel
平方；(ii) 不使用 `1/E_Xi` 的 theta/prime causal factorization。spatial cyclic heat
TP、逐格點能量與 shifted inner chains都不跨越 endpoint。

新增 ES62/L12 後，策略排序調整：Pick--Bernstein moment-ratio成為目前最具體的
coefficient-side all-degree路徑。它不是恢復 finite moment certificates；單一函數
`varphi_nat(z)=2(2z-1)M(2z-2)/M(2z)` 若能證為 1-separated Pick--Bernstein，
KPS Theorem 4.4 立即處理全 degree。J5 已給其 integer values全部嚴格遞增，僅是
第一個 Bernstein層。後續應集中找 Mellin-ratio 的 Herglotz/Stieltjes representation
或解析反例；不得以更多有限差分 VERIFIED 代替 complex Pick證明。

J69--J71 完成後，L12 的最新評價更精確。正 moment law不再是缺口：Abel反演已
無條件構造單一 positive、moment-determinate mixing variable `I`。真正 all-degree
gate是其 Mellin cumulant的 inverse-Laplace measure是否滿足 Fermi--Bose sandwich
J70.3；條件式 J71又顯示這等價新的 Mellin-zero realness/spacing問題。故優先順序為：

1. 找到 `M` 的 certified nonreal zero，直接淘汰 natural L12 interpolant；或
2. 從 theta lattice證 J70 measure sandwich與 harmonic-potential admissibility；
3. 若兩者皆無，回到 K0B37--38 nonlocal Green/Rellich operator factorization。

Durán 2026 fixed-width orthogonal-combination theorem不改變排序，因 Xi truncation
width隨 degree增長。禁止恢復 finite Hermite/Jensen/moment batches。

## 18. J72 後策略重排（2026-08-15）

第一項成敗測試已完成：Arb/Rouché certificate 嚴格找到 `M` 的 nonreal zero，且
排除 `M(rho-2)` 同時為零。故 natural `varphi_nat` 有上半平面 pole，L12 natural
Pick--Bernstein route關閉。J69 Abel mixing保留為獨立正表示成果；它沒有提供任意
degree升階 theorem。另一個穿過相同 integer data的 Pick interpolant只有在能由
theta資料統一構造並證 1-separation時才重開，不做 finite differences搜尋。

同時修正 J70--71 的邏輯層級：Fermi--Bose sandwich是 measure inequality；逐點
density/exponential-sum式還缺 absolute continuity與 canonical inversion。這個缺口
不是靠更多 VERIFIED samples可補，但因 J72 已有更早的解析 obstruction，暫停此支線。

目前 live 排序：

1. K0B37--38：完整二維 theta lattice sum的 nonlocal Green/Rellich、Kraus或
   completely-positive factorization；必須利用跨 mode cancellation，逐 mode符號已否證。
2. Suzuki endpoint：從 theta/prime資料直接構造 causal support，不得先使用
   `1/E_Xi`、inner/HB或 RH-equivalent scalar modulus monotonicity。
3. Jensen只保留 Xi-specific reverse shift或真正 all-order exact factorization；
   Holland wedge與 degree 3都不能反推 `n=0` 全 degree。

這三條都是真正 uniform-in-degree target；逐 degree moment/Hermite/Jensen證書繼續停止。

## 19. J73：KPS 替代插值也被 Carlson uniqueness 關閉

J72 後保留的抽象可能性現已排除。KPS recurrence使所有候選的 `1/W_varphi` 在正整數
具有相同 Xi coefficient samples。Patie--Savov Stirling formula與 J69 moment bound
證 candidate及 natural coefficient interpolant皆在 Carlson class；indicator sum至多
`pi<2pi`，所以整數資料唯一決定整個函數。J72 的 nonreal zero與 KPS全負實零點結構
矛盾。

因此 Pick--Bernstein/KPS 不再是 live route；這是完整 all-degree策略的否定性稽核，
不是 RH成果。優先順序改為：

1. K0B39 的 automorphic test-dependent lift，目標是 point trace exact變成 Haar/
   Rankin--Selberg square；K0B40/Hudson已排除 raw geodesic positivity，K0B41/Schur
   已排除 full-orbit equivariant Haar frame。只剩含 cone boundary的非等變 lift。
2. Suzuki endpoint causal support，必須直接由 theta/prime factorization得到。
3. Xi-specific determinant/PF∞或 reverse-shift theorem；沒有新 uniform mechanism前不
   恢復任何 fixed-degree certificates。

Suzuki 2606.09096 的 finite-interval characteristic functions可併入第 2 項，但只保留
修正版目標：無條件 shift `lambda(a)<lambda_a` 下的 meromorphic compact convergence。
`lambda(a)->0` 本身已跨越 Weil positivity；而 `z^2xi/xi'` 有 poles，不能宣稱是 entire
functions在 C全部 compact上的普通一致極限。finite-a全實零仍不是 endpoint bridge。

外部 claimed proof Zenodo 19546495 所稱「weak convergence已足夠」沒有改變此判斷：
它把 shifted positive form `QW_N-epsilon_N I` 的自伴 spectrum偷換成 unshifted
`QW_N` positivity，漏掉 ground term。故 compact-support stabilization不是新的 bridge。

## 20. 最新 Toeplitz uniform theorem 的策略位置

ES70 的 `k>=10^18r^3` consecutive-minor positivity是真正 uniform-in-rank進展，
但只在遠尾 wedge。其 q-Pascal group不移動 actual coefficient shift，不能作 reverse
transport。Exact Toda condensation雖給 rank elevation formula，所需 invariant正是
前一 determinant row的 log-concavity，等價待證 next rank；J55 cubic不提供它。

Rectangular Jacobi--Trudi duality把 fixed k的全部 ranks壓成 fixed-size reciprocal-Xi
determinants，證明 fixed-shift eventual positivity可系統化；但 uniform growing k需
控制 growing real pole packet，未越過 unknown zeros。故 coefficient-side只保留一個
明確 live theorem target：balanced cone `k asymp r` 的 theta-specific Toda cone或
不預設 pole reality的 two-parameter dual determinant estimate。ES71 contour-Hankel
inertia只把 nonreal zeros標成 indefinite jumps，沒有提供此 cone。

ES72 將 finite Weil方向也壓到同一層級：`g_v=L F_vF_v#` 是 exact square transport，
但 post-band archimedean TP不是 complete-source positivity。Loewner/Pick重寫有
critical sampling nullspace `sin^2(pi z)h(z)`，不能靠 integer data唯一化。故 spectral
優先目標進一步具體化為 signed prime atoms與 gamma head的同一 Gram/Kraus；若只增加
cutoff、finite eigenvalue或孤立 tail minors，均不推進。

進一步的 spectral-type audit 關閉「正 shift measure」版本的共同 Gram：其
difference-square form必為 absolutely continuous Fourier multiplier，而 Hardy
已無條件保證 boundary Weil source含 critical-zero Dirac atoms；off-line poles在該
局部只給 smooth Poisson terms。故後續只保留能產生離散奇異譜的 self-adjoint
compression／boundary-residue Gram；不再嘗試以更多正 translation weights壓住
signed primes。

Toeplitz側亦新增 exact量詞反例：`cosh(sqrt z)+A` (`A>1`) 保留 PF-infinity base
除常數項外的全部 coefficients，故所有 `k>=r` minors strict positive，卻有顯式
nonreal zeros。這把目標從含糊的「改善 cubic wedge」收緊為 Xi-specific
head-to-tail reverse theorem／uniform growing `k<r` cone；單純擴大 tail區域沒有
證明力。

T7 提供一個新且真正 uniform 的 theta接口：全部 Toeplitz minors同時成為
`det[Phi^(2i)(u_j)]` 對正 Vandermonde的 Andreief積分，連負 coefficient index的
zero boundary也由 Phi偶性保留。但 rank-3 derivative determinant已有 rigorously
negative open set，故「pointwise derivative TP」路線關閉。只剩能在整個多重積分
上配對負區域的 theta involution／sum-of-squares；有限抽樣或局部符號沒有作用。

## 21. Green/current 外部輸入後的精確 live target

BFI arXiv:1112.3444 在其 signature `(2,1)` theta setting提供 exact非等變模板，
但其式為 geodesic period減 `int(Delta f)eta/(4pi)`；split case另有 cusp boundary integrals，零
eigenvalue regularization還依賴 spectral deformation的 `B'_ell(1)`。所以這不是
現成正性。緊支撐且 boundary-free 的 `-Delta f>=0` 版本又被 `int Delta f=0`
與最大值原理迫成平凡。

Kudla--Millson/Mathai--Quillen也不能免費補洞：`X(1)` genus zero，level-1
`H^1_(2)=0`，closed geodesic只留下 exact transgression；split geodesic的 cusp
資料則不可刪。故 theta主線目前只接受一個結果：構造 canonical `h -> F_h`，逐 test
證 `Q_K0(h)` exact等於 BFI bulk、period、cusp及 deformation corrections的完整總和，
再把 **總和** 配成 norm。relative trace平均、單獨 period square、Maass--Selberg
truncated norm或 cohomological Hodge norm都尚未給這個 adjoint identity。

更嚴格的 kernel audit（K0B46）把優先序再前移一層：BFI/KM 是三維 adjoint/
`Sym^2` theta，K0B39 是二維 standard Epstein theta；兩者沒有 equivariant linear
intertwiner。quadratic Veronese只落 isotropic cone並把 exponent變成 quartic。
因此在攻 bulk/cusp定號以前，先要證 stress+cone cutoff層級的 transmutation，或替
Epstein theta本身構造 Green/Rellich identity。若無這一步，BFI只作 boundary
bookkeeping模板，不算已接上 K0。

正確的 Epstein replacement又使兩條主線合併：`Theta_*` 是 incomplete Eisenstein
series，unfolding後與所有 cusp forms正交；Mellin spectrum只含
`zeta(2w)E(z,w)`，故其 Green/resolvent boundary資料就是
`phi(w)=zeta^*(2w-1)/zeta^*(2w)`。Maass--Selberg給正 truncated norm，但正主項按
`log T`發散，renormalized scattering finite part不繼承符號。這不是新的 theta
捷徑，而是 B21--B23/Suzuki causal endpoint的 automorphic版本。當前唯一 live
義務因此是：在 pole-neutral cone與 K0 cone cutoff下，把 finite time delay與全部
incoming/outgoing boundary terms exact配成平方；若只引用未減 baseline的 norm，
量詞與 renormalization均不合格。

B31進一步避免過度升格。所需 mean-delay sign exact等於 cumulative projection defect
`||P_RSh||^2-||P_Rh||^2` 對 `R` 的積分非負；不要求 defect逐 `R` 非負，也不要求
operator causality。故最窄 live theorem是 pole-neutral cone上的 **integrated
Maass--Selberg flux square**。這仍是 uniform-in-support命題，但嚴格弱於 innerness，
保留了新的可能性。

Selberg nudge要求的 mean-to-zero bridge已在 B32補齊。B31只有在量詞為「每個
support、每個 compact pole-neutral test」時才足夠；此時 autocorrelation support
使 semilocal phase exact等於 full Weil form。任何 off-line orbit都有不定
`2 by 2` block，W14 localization加 compact cutoff/moment correction會產生一個負
test。因此 integrated-flux theorem若完成便是完整 RH，不只是 density結果；反之，
只證平均於 h、平均於 R以外再平均 support/zeros的估計仍不合格。

Krein/Szego sum-rule分支亦完成前提稽核。Arov-gauge identity雖把 spectral entropy
寫成 positive Hamiltonian coefficient integral，但 `w` holomorphic Schur是入口前提；
對 modular scattering，證此條件到 endpoint已承擔 RH-facing pole exclusion。純相位
boundary使 entropy退化，任意 transmission dilation則缺 canonical arithmetic choice
與 B31 adjoint identity。因此它目前不是 integrated-flux square，只是成功機制的模板。

Connes--Consani archimedean positivity的升階點也已精確定位。無質數時，
`Q`-remainder是 `-2I+K` 且 `K` Hilbert--Schmidt，所以可靠有限 constraints
處理 exceptional modes。含質數後，每個 `log n` 產生 compressed translation；
modulo-shift fibre的 path spectrum有 infinite multiplicity，故是真正 essential part，不是
compact defect。codimension-two pole neutrality不改變此事實；先套 Q 還將其變成
shifted derivative energies。因此「archimedean square + compact prime correction」路徑停止。
唯一合格升階機制是把全部 active shifts當作新 principal operator，直接證
`P_x^0 A_x P_x^0>=0` 對所有 `x`成立。這是 uniform all-support theorem，
尚未證，也不會以 finite spectral batches代替。

新的最高優先介面是 Suzuki arithmetic screw-line coisometry。它不是 degree-by-degree
路線：`mathfrak S_t` 已無條件、無零點地由完整 prime/gamma 資料定義，
且一個 two-variable Gram identity就同時覆蓋所有 support。與 B31 相比，這正是
integrated flux square的明確 feature map；與 B32 相比，它的全稱量足以逐零點。

但不得把它誤讀為已完成的 factorization。無條件 zero expansion在 off-line orbit
上將「正 `L2` Gram」與「indefinite conjugation block」並列；二者一致本身即
RH。因此下一步只接受 arithmetic-level 證明：直接計算
`P_D^*P_D` 的核，證它 exact等於 screw kernel，或將差異寫成全部
nonreal-pole residues後以獨立算術機制消去。不接受先假設 `Theta` Schur/inner、
Hermite--Biehler 或 model-space Parseval，因這些已等價地含有所求結論。

Pontryagin refinement給了這個缺口的 uniform 整數 invariant。對
`q=-A'/A`，negative-square index計算 upper-half-plane off-line zeros；它正是
Suzuki Gram與 Weil indefinite pairing之間的 residue debt。因此後續若有 contour/
Plancherel proof，必須顯式產生這個 finite-or-infinite-index correction；沒有 correction
的公式只在已預設 RH 時成立。這條路不再刷任何 finite minors，只攻一個
all-support 命題：prime--gamma arithmetic為何迫使該 Pontryagin index為零。

finite-index情形已可再簡化成 Krein--Langer denominator problem。
`Theta=Theta_0/B` 後，負部份 exact是 finite-rank `K_B`；所以「建構一個正
Hilbert feature map」只會表示 `Theta_0` channel，無法自動表示完整 Weil form。
目前只有一個可驗收的新定理：從 Euler/Poisson/gamma normalization 推出
`B=1`。這是 all-degree、all-support，且完全排除再刷 finite certificates。

Selberg lens對「prime--Poisson能否給計數以外約束」的答案現為：一般線性形式
不能。shifted product `xi(s+a)xi(s-a)` 以嚴格正 Euler log weights與 exact
functional equation/Poisson formula產生無界 off-line index。所以后續不再嘗試從
`Lambda(n)>=0`、local trace additivity、functional-equation symmetry或一般 Selberg-class axioms推
`B=1`。可能成功的論證必須同時：(i) degree one/single gamma channel；
(ii) Ramanujan-size coefficients；(iii) nonlinear，不對 Euler products additive；(iv) exact產生
Suzuki coisometry或消去 `K_B`。現有 degree-one classification沒有第 (iv)。

degree-one的 local nonlinear結構現已精確化：每個 Euler factor的 log coefficient
sequence是 Hankel rank one，確實排除 shifted-product反例。然而 Dirichlet L-functions
也有同樣結構；所以任何只依 local rank、Ramanujan與單 gamma的升階定理至少強到
Dirichlet GRH。後續只接受額外 coupling：使用 conductor one及所有 `alpha_p=1`
的全域一致性，輸出 B35 coisometry／`B=1`；local determinant identities不算
uniform mechanism。

另開一條嚴格 all-degree 的 scalar Jensen branch。BSY mass
`Omega_zeta=sum_(beta>1/2)log|rho/(1-rho)|` 對每個 off-line zero皆正，故證
critical-line weighted `log|zeta|` integral `<=0` 足以完成 RH。這比逐 degree
certificate合格，但 pole-normalized Euler product只給 inner/outer factors互相補償，
hybrid Euler--Hadamard仍含 zero factor。優先問題可二選一：(a) B35 full arithmetic
coisometry；(b) B40.3 nonlinear boundary-log upper bound。只重述 BSY/Jensen
factorization或以截斷 Euler product忽略 zero remainder的工作停止。

Burnol的 quantitative Nyman theorem進一步證明 (b) 並非與舊 Nyman列獨立：若
`d` 是最佳 Nyman距離，則 `d^2=1-exp(-2Omega_zeta)`。故目前實質仍是一個
conductor-one defect，可由兩個介面攻擊：B35 的 full arithmetic coisometry，或
NB11/B40 的 uniform mollifier／boundary-log estimate。有限 projection、有限
Blaschke product與完整 operator causality（後者已 RH-equivalent）均不降低缺口。

degree-one local rank-one現在有更強的 operator形式。每個 local scattering ratio是
`Blaschke inner / exponential inner`；分母 model space無限維，正是 primes加入後的
noncompact principal debt。故「所有 local factors皆 all-pass／inner quotient」不給
positivity，direct sum甚至保留 infinite negative squares。唯一新增而合格的結構命題是
cross-place Poisson partial isometry B42.5：把全部 denominator reservoirs嵌入
numerator加 archimedean/pole reservoir，且剩餘 defect exact為 Suzuki/Weil form。
若沒有這個 compatible coisometry，不再以 local factorization或 finite constraints
宣稱升階。

依 Selberg nudge，上一段只有在給出解析式後才算候選。B43現已給局部完整式：
Hankel leakage為 `p^-1I`，causal part為 `(1-p^-1)I`，Bohr tensor product質量按
Euler product塌縮。cross-place研究只保留 B43.5--B43.6 這個可證偽版本：從
completed semilocal multiplier逐 Laurent/gamma kernel明算 leakage，並給 explicit
Poisson diagonal recovery；餘項須 exact是 B32 且定號。若 `R_S` 仍未寫出 kernel，
或只引用 abstract existence，就停止該候選。

B44--B45已執行上述 kernel 門檻。prime diagonal leakage是 coefficient
`C_S mu(d)sqrt(d)/(phi(d)sqrt(n))` 的 finite Volterra sum；gamma kernel是
`2e^(a/2)cos(2pi e^a)`，completed Hankel kernel完全 explicit。稽核仍否定 natural
map：primal--dual取消 prime data，same-side無 uniform bound，剩餘 signs就是 NB11
的 Möbius cancellation。因此 cross-place branch不再 active；只有提出不同且具體的
`R_S(x,y)` 後才重開，不以「Poisson應該耦合」作 placeholder。

finite Loewner dictionary也沒有 hidden strict-type升階。pole source的 frequency support
觸及 1 且 endpoint density非零，故 type exact為 `2pi`；compact support仍在 Nyquist
boundary。`sin^2(pi z)h(z)` 同時消所有 integer values/derivatives，pole-neutral
restriction不改變。故 single-phase PSD不能靠 Carlson uniqueness擴張到 all phases，
不得把它列為新的 uniform Pick theorem。

## 22. 外部semilocal trace與OS dilation稽核

Li 0807.0090v10 看似直接提供所需全域 positivity，但兩個關鍵 zero-remainder
arguments有同一商空間錯誤。`gamma in O_S^*` 對 `C_S=J_S/O_S^*` 的乘法是
identity；不能同時把 quotient變數視為已取商，又用 representative
`x/gamma` 改變 additive character。若固定基本域 section，該變換不保 section。
因此 unit-orbit terms沒有被證為 identical，Theorems 1.3--1.4不成立。可保留的
`V_S(h)>=0` 只給正主塊；未消失的 cross remainder正是 B32 sharp semilocal gap。

Neeb--Olafsson 則回答 W11 的 abstract問題：positive Hankel semigroup確可 OS-dilate
成 group covariance。但 W19顯示其 group coordinate是 Laplace parameter；算術
prime powers位於 box spectral measure的 endpoints。endpoint comb等於 bulk的
distribution derivative加 boundary counterterm，微分不保正。故這個 theorem
不能作為 uniform升階橋，除非再證 completed endpoint derivative的 sharp constant-1
bound；而後者就是 W12/W16，不是較小命題。

Li修正版的 local內容也已辨識：unit-orbit三段權重配 critical scaling後 exact等於
B43 local scattering Laurent series。故外部 trace聲稱若去掉錯誤的 orbit collapse，
剩下的不是未知新 operator，而是 B44--B45 已顯式化的 Mobius--Volterra completed
Hankel kernel。後續只可能在該完整 kernel上證 cross-place sign；不能再以 Li 的
positive convolution主塊或 unit multiplicity宣稱已控制 remainder。

## 23. Laplace正性不微分：half-Cauchy divisibility

Selberg nudge可嚴格實現為 CS2：先在 zero-free line `Re s=1` 取
`q_1=i xi'/xi(1-iz)` 的無條件正 Herglotz measure `mu_1`，再要求它屬
`P_(1/2)` 對正測度的 range。這一次不需從 box bulk取 distribution derivative；
RH converse由 analytic strip內的 Poisson poles直接完成，因正 residues不能取消。

但「positive measure經 backward Poisson仍 positive」不是一般 theorem。其 inverse
Fourier multiplier `e^(|t|/2)` 無界；對 local Euler factors展開正好是 B43 的單一
anti-causal leakage，global coefficients又是 B44 Möbius--Volterra signs。故 CS2
提供新的清楚 spectral-measure量詞，卻沒有把 sign藏掉。唯一合格續攻是從所有
`alpha_p=1` 與 conductor one證 compatible Cauchy divisibility；finite moments、
普通 infinite divisibility at `Re s>1`、或 forward smoothing positivity都不足。

## 24. Weyl核的omega導數橋與真正的compression斷層

Freedman coordinate kernel提供一個比 KLM包裝更直接的 all-degree介面。WD1--WD3
證 `partial_omega D_omega=(4/pi) F K_omega F*`；因此全區間
`K_omega>=0` 積分成 shifted-Xi de Branges positivity，足以推出 RH。這條 bridge
已閉合，剩餘義務完全位於原始 Weyl kernel的 uniform positivity。

外部 companion沒有閉合該義務。它把 lifted multiplier contraction
`|kappa|<=1` 直接提升成 integrated/compressed `||CKE||<=1`，但 `C` 不等距且不與
`K` commute；FW2二維反例證一般推論為假。Euler orthogonality只在先行假定
indefinite fiber minimizer後得到 `Q(f_x,h)=0`，而把 boundary form再定義為同一 Q
不能推出 norm domination。此處正是 constrained moment positivity本身，不是可由
閉包定義消除的技術尾項。

故此 route只保留兩個可驗收輸出：(a) 對 concrete theta-Volterra `C,E,K` 寫出並
證明特殊 intertwiner/commutator identity，使 compression真的 contractive；或
(b) 直接 Hilbert-Gram factorization `K_omega(a,b)=<v_a,v_b>`，uniform於 omega。
任何 finite stress test、Galerkin norm<1、或 downstream `closed:true` 不再計分。

WD5再排除「用既知 theta log-concavity補洞」的可能。`K_omega` 的 boundary
plane-wave quadratic form就是 Xi 的 complex Laguerre expression；而 Csordas定理
只由 log-concavity得到 associated kernels admissible，所有 degree 的 PD才 iff RH。
所以 G110不是 ordinary total-positivity theorem的直接 corollary。除非找到能同時
控制所有 correlation degree／所有 test configurations的新 theta identity，否則
這條線只是把 RH重新表成 Weyl positivity，不能視為比 CS2 或 full Weil更弱。

operator層的唯一非循環接口現為 FW6 Douglas condition。
`C^*C-KC^*CK` 在 ambient lifted space不定號，且 K不 descends through C；所以
「pointwise Cayley multiplier + compression」不是升階定理。若沒有明寫 special
theta range上的 T、其 kernel及 uniform norm proof，Green/Volterra分支即視為停在
full signed moment form，不再接受抽象 minimizer或 closure命名。

WD6再設一個必要過濾器：即使 positive even admissible kernel具有 uniform strict
log-concavity，也可能有非實 Fourier zeros及負 Weyl方向。故「Phi比一般 kernel更
log-concave」不是 Riemann-specific升階機制。新候選必須明確使用 theta modular
identity或整個 n-mode coupling，並直接驗 FW6；否則不列為 live path。

WD7完成所求 uniform-in-degree定理：對適當 real entire f，small-omega coordinate
Weyl kernels全 PSD iff f屬 LP。正向來自 vertical-shift de Branges spaces的
contractive nesting，反向來自 zero exclusion。故此結構不是 degree 3 的有限延伸，
而是一次涵蓋所有 degree/configurations；但對 Xi它 exact就是 RH。

策略上，Freedman branch現在不再被當作可能只差 functional-analysis polish的捷徑。
FW6、direct Gram、omega-Loewner monotonicity三者是同一 RH-equivalent target。
只有新的 prime/modular identity能無條件證其中之一時才算進展；引用 LP product、
HB innerness（small omega時已假設 RH）或一般 de Branges subspace ordering皆循環。

## 25. theta--Poisson 到 Douglas 的具體斷層

TPD2提供 FW6 的更透明版本：Weyl quadratic form是 `q_(sigma,+)` 與
`q_(sigma,-)` 兩組半軸 Hankel norm之差。模方程只證兩 profile經 reflection與
branch swap相等；它把正半軸問題移到負半軸，沒有提供 causality。

這不是措辭上的缺口。`omega=0` 時對應 full-line scattering ratio exact為
`E#/E=(Xi+iXi')/(Xi-iXi')`。Poisson/evenness只給 boundary unitary；使其保留
**整個** Hardy subspace所需的 innerness就是 Hermite--Biehler criterion。FW6只需
special `Ran(A_0^+)`，故不能直接套 full-space iff；但 special contraction就是
`K_0>=0`，由 VK6/K0B3仍等價 RH。scalar theta trace在兩種正確量詞下都沒有自動
跨過 projection。

保留的唯一 modular 研究方向是：在尚未先把 lattice sum壓成 Phi前，構造一個
Poisson unitary 的特殊 half-space compression，並驗證它 descend 到 TPD2 的
`A^- = T A^+`。若不能展示這個 exact range identity與 `||T||<=1`，便不再把
「利用模性」列作實質進展。

TPD7顯示即使不先壓成 scalar `Phi`，naive lattice lift也有同一 compression錯誤。
Sonine `D_u^2+D_u` 的確共軛為 Xi 的 `d_t^2-1/4`，但 Poisson comb sampling在
L2及 pole-neutral codimension-two subspace上不 bounded。故 ambient Fourier
unitary的半空間 contraction不能穿過 theta trace。可驗收的 lattice方案必須額外
證 Gaussian dilation range是一個對 comb sampling有 uniform bound的 frame，且
frame defect不是未減的發散 baseline，而 exact等於 K0 quadratic form。

TPD8又證 global frame不存在：dilation Mellin空間中 comb sampling symbol是
`zeta(1/2-it)`，其 mean-square按 `TlogT` 發散。故任何合法 Poisson證明必須同時
保留 plus/minus（或 incoming/outgoing）兩側，使共同發散 sampling baseline在
quadratic-form層 exact相消；先分別估兩側必失敗。這把 TPD2 Douglas與 B31
integrated flux辨識為同一剩餘 target。

## 26. defect三重表示不是三條路

DU1--DU3 現已給 exact master pairing
`W_0(H)=sum_rho H(rho)conj(H(conj rho))`。TPD/K0是它在 Xi-resolvent family上的
Hankel norm-difference pullback；B21、B22、B31是它在 pole-neutral Paley--Wiener
class上的 Hardy leakage、mean moment、cumulative area。後三者逐 test相等；前者
test class不同但共享同一 zero block，all-test positivity同樣等價 RH。

因此策略機率不能再把 TPD Douglas、semilocal mean delay、Maass--Selberg flux相加。
它們只保留一個成功條件：找到一個 arithmetic identity，將完整 finite-part area
（不是未減 truncated norm）寫成正平方。任何新的 representation若沒有同時提供
sign mechanism，只是 G117 的另一個座標。

pole constraints本身也沒有隱藏的降階。DU6將其 exact解為 compactly supported
Green range `h=(-d^2+1/4)g`；zero pairing只受可逆 multiplier congruence，負指標
不變。故「先除 `(z^2+1/4)` 再證局部 Poincare」不能成為新路，除非後續 inequality
仍完整包含 prime translations；那就回到同一 G117 master form。

## 27. Barnes/Thorin folding是uniform字典，不是新的正性來源

Polson 的 folded Thorin measure把任意 degree 的 secondary-zeta Hankel/Jacobi條件
統一成一個 Stieltjes measure問題，形式上符合停止逐 degree刷證書後所要的全階
結構；但對 xi，證該 measure正實就已等價 RH。它與 DU master zero pairing只差
folding/spectral coordinates，不應計為獨立路徑。

外部稿所稱無條件 critical-centre GGC closure已由 `polson_thorin_audit.md` 排除：
除了錯誤的 square-root代數，其自身 Thorin atom `3/4` 已使必要的 parameter-1 tilt
發散。後來 SSRN 稿也明確退回 RH-equivalent open clause。策略上只保留一個新措辭
的驗收標準：從 arithmetic theta/prime side直接證 folded log derivative為 Stieltjes
function。characteristic-function positivity、Barnes clocks、atomwise HCM與有限 Hankel
minors皆不計分。

並且 v8 式 (24) 把 concave linear factor的 centred increment符號寫反。正確輸入是
`prime atoms - e^x dx + Gamma` 的 signed measure，不是各項正 measure。故 Thorin
route 的唯一可能修補就是證 **合併後** sine-square transform全正；逐項 Tonelli
不可用。這與第26節 full finite-part area的 counterterm cancellation是同一義務。

## 28. raw Phi total positivity路線由actual PF5 witness關閉

不再把「也許 Phi 本身 PF-infinity」列為 uniform-in-degree候選。ES116/G120 對 actual
de Bruijn--Newman kernel給 size-5 translation Toeplitz負 minor；本地 Arb與 Leibniz
雙重 enclosure已獨立重驗。這不是 generic no-go，而是 Riemann kernel本身的反例。

degree 3應繼續只列獨立有限成果；某 fixed configuration 的 degrees 2--4正號不能
升階，因同 configuration在5即負。保留的全階結構只有 exact K0/Bezoutian/Weyl、
folded Thorin或 Weil forms；它們不能被 raw Phi translation total positivity替換。

## 29. Thorin route的scalar sign已閉合；剩下的是outer/inner斷層

TOI1--TOI3 顯示 corrected combined sine-square transform其實無條件非負，因它只是
`log(xi(a)/|xi(a+it)|)`，而 normalized vertical ratio是 positive random variable
Mellin tilt的 characteristic function。後續不得再把證此 scalar sign列為目標。

真正欠缺的是從 boundary modulus重建 analytic reciprocal時排除 invisible Blaschke
factor。這與 TPD 的 boundary unitary versus Hardy innerness完全相同；若只用 modulus、
Poisson integral或 positive Phi，必然只得到 outer part。驗收標準須明含 phase/cut-plane
continuation，或直接由 full defect square迫使 inner factor trivial。

TOI5把驗收對象再具體化：每個 off-line quartet在 boundary phase derivative留下兩個
寬度 `a=Re(rho)-1/2` 的 Poisson bumps，而 modulus完全看不見。候選 theorem若沒有
控制 Hilbert-transform phase與這些 absolutely-continuous bumps，就仍只處理 outer
part。Williams--Ostrovsky GGC law沒有現成 theorem排除此項；WD6與G120分別否決
generic log-concavity及 raw PF-infinity替代。

## 30. outer budget可量化 inner 損傷，但高度衰減不足

BSY--Burnol scalar defect不是只能定性使用。`rho_(1/2)` 的奇偶階梯結構給
`Omega_zeta<=-(1/2)log(log 2)`；每個 `1/2+a+i gamma` 離線零點至少消耗
`a/[gamma^2+(a+1/2)^2]`。因此 dyadic strip 的離線零點數有顯式
`O(T^2/delta)` 上界。

這回答了 nudge，但沒有改變主策略：權重在高處按 `a/gamma^2` 消失，無法把整數
計數壓成零；更好的有限 Nyman 證書只降低固定預算，除非證其極限為零，而那就是
RH。Li kernels只有在另得 cancellation-free uniform positivity時才可能改善此斷層。
不得以更多有限 Nyman 或 Li 係數數值批次代替該 sign theorem。

## 31. 恢復一條 phase-sensitive 的純算術路徑

外部 ES118 將 inner 缺口具體降成 Suzuki `g_0(t)` 的 eventual nonpositivity。它的
二階 distribution 正是 prime atoms 減連續 pole density，因此可視為一個
second-order convex domination 問題；與 outer modulus不同，它會看見離線 zero
造成的 growing oscillation。這是一參數全域 theorem target，不是逐 degree 刷證書。

此路目前只接受三類機制：完整差的 square factorization、保留 prime-power cancellation
的 renewal identity、或可證局部不等式到 eventual sign 的真正 variation-diminishing
定理。PNT absolute error、`Lambda>=0`、complete-monotonicity改名及 generalized Li
finite checks均已稽核不夠。主攻可轉為 `Lambda*1=log` 是否存在正 kernel recovery；
若反演必須使用 Möbius signed coefficients，則須再找額外平方結構。

AP6 已否決最自然的 `Lambda*1=log` 正 recovery：與整數 counting measure卷積在
Laplace 空間乘上 `zeta(s)`，恰把所有待偵測 zero poles消掉；所得整數式的正主項
是無條件 `4(1+gamma_0)e^(t/2)`。這不是接近 sign closure，而是 smoothing 抹除
inner defect。且非平凡 positive convolution inverse 不存在。

所以 AP 支下一步不得再用 `zeta` multiplier或 Möbius反演改名。合格 kernel需滿足：
其 transform在整個 critical strip無零（不能遮掉候選 zeros），並在 `g_0` 所屬的
restricted class上有可證的 sign-reflection theorem；或者直接對 AP2.2 factor square。

AP7 提供符合此濾網的最小 family：causal exponential kernel的 transform
`(z+a)^(-1)` 無零，故 eventual sign與 RH 的等價性在 smoothing後仍保留；算術側
prime weight變成顯式 `phi_a(v)=v/a-(1-e^(-av))/a^2`。此 family可作外部 one-sided
Tauberian theorem的搜尋接口，但目前 PNT error未改善。不要因 multiplier無零就宣稱
sign recovery；下一步必須實際證 AP7.3 的 eventual inequality。

OB4/G127 另證 outer-budget 支的 `T^2` 天花板是 sharp hyperbolic geometry，而非
可優化常數。單一 Blaschke zero已飽和從 `s=1` 到 `1+iT` 的 Harnack factor。
因此不得再嘗試由同一 `Omega_zeta` 做更細切片來宣稱 improved zero density；新的
outer輸入必須是 shifted Nyman/evaluation local budget family，否則應留在 AP phase sign。

AP8 回應 Selberg extremal-configuration nudge。finite isolated rightmost layer已可嚴格
處理：每個 quartet有 `e^(at)` 正峰，多個同 edge zeros形成非零 mean-zero trig
polynomial，必取兩號，不能靠全和永久抵消。這不是新假設下的 RH證明，因一般 zero
set可有不取到的 horizontal supremum；BSY budget也允許高處無限逼近。

所以下一個合格 theorem被縮成：對滿足 zeta zero-counting、functional symmetry與
BSY mass的 edge-free spectrum，給 Laplace sum的 uniform oscillation lower bound，
且能與 AP7 prime-side upper bound比較。重算單 quartet或假定 maximal zero不再計分。

## 32. edge-free oscillation已外部閉合；live target改為有正反演的 AP11

Radziejewski 的 weakly-bounded Mellin theorem已移除第31節最後的 spectral caveat。
對 `f(x)=g_0(log x)`，任一 off-line zero `q=a+i gamma` 都是 residue
`-m/q^2` 非零的 simple Mellin pole；標準 `zeta'/zeta` partial fractions與
unit-height zero count驗證 theorem hypotheses，故無論 spectral supremum是否取到，
都有 `g_0=Omega_+(e^(at)t^(-M))` 與 `Omega_-`。所以不再研究 extremal-zero聚合；
它只是 failure detector，未產生 Euler-side sign。

Suzuki 的 shifted-window式與模數平均亦已稽核。window kernel的 continuum main term
exact為0，沒有 PNT slack；論文的 unconditional negative average只跨 `q>=3` 模數，
不能反演到 principal `q=1`。這些不是 sign closure。

AP10顯示差分局部化的邊界：一階 increment `H(t)-H(t-L)` 有正 grid反演，且「存在
L eventual非負」等價 RH；二階 increment雖只含長度 `2L` prime window，卻消掉
`c_0t` drift，critical-line poles迫使 generic L正負振盪。不得再追 compact-window
pointwise sign。

目前最合格的 live kernel是 AP11：`K_a=e^(-at)*H`、`D_a=K_a'=H-aK_a`。
`D_a>=0` eventual使 K_a單調並給 H下界；RH反向可取小 a，故「存在 a」等價 RH。
其 prime weight `[1-(n/x)^a]/a` 非負且飽和，multiplier `z/(z+a)` 不消 nonreal
zero poles，並有 ODE正反演。下一個實質突破必須是 AP11.4 的 arithmetic upper
bound或等價 square。AP11.8--AP11.10用 exact第一 Li/Hadamard常數證固定 `a=1/2`
已足夠：RH下正 drift嚴格壓過全部 critical-zero振幅；故 AP11.6 對充分大 x成立
exact等價 RH。這個單一 psi integral仍需 sqrt-x級 cancellation，粗 PNT不夠。
Helson/Dirichlet-convolution moment positivity只處理 product/sum semigroup，
未補 prime correlation的 ratio/difference group斷層。

外部搜尋另找到 Preprints.org 202605.1525v4 的 claimed Chebyshev-integral proof，
但 PC2給 exact反例：其全局 mean-square extraction假定每個 floor cell J_m非空；
`N=10,m=6` 已否證。故不得引用其 `O(X^2 log^2 X)` mean-square或 absolute
integrability來補 AP11.6。這條外部捷徑已解析關閉。

相對地，Johnston arXiv:2201.06184 是可靠的門檻輸入：Mertens方法只無條件給
c=2 weighted bias；其 theorem顯示 off-line omega使所有 c<1+omega 出現正
excursion。AP11.6 的 c=3/2因此恰為 RH boundary。策略上不再嘗試把已知 t^-2
不等式用參數連續性推到 t^-3/2；必須在臨界點取得新的 prime cancellation或 square。

## 33. 新增 all-complexity 乘法座標，但不誤報為上界

Akatsuka arXiv:2411.19259 補上所需 uniform mechanism：乘法性與 1/2-superior highly
composite extremality把所有整數、所有 prime exponents一次壓到 `E_1(X)`；其
boundedness exact等價 RH。這不是 degree-3 延伸，而是獨立的 all-complexity route。

`akatsuka_multiplicative_audit.md` 的 A2.1 顯示它比 AP11 多一個 `1/log u` damping，
critical-line oscillations會衰減，故可與 AP11 並列。但 positive Euler factors不給
單調性：A3.1 的 rigorous Arb countercheck已有兩號。驗收標準是證完整
linear-plus-concavity defect uniformly bounded above，或在 SHCN transition sequence
上建立可 telescoping 的 Lyapunov inequality。absolute PNT error或有限 prime batches
均不能計為進展。

A5.5再給一個更適合「升階定理」的表述：SHCN envelope與 smooth normalization作
Fenchel dual後，RH target成為一參數 positive local free-energy inequality
`G(c)<=V(c)+C`；G對每個 prime、每個 exponent取獨立最大，故一次涵蓋所有 complexity。
這應優先於任何新增 finite degree 證書。但展開 G 會回到 E1/critical PNT error；只有
不預設該誤差的 uniform dual domination才算新突破。

## 34. dual route與 AP11 已合流成一個較柔和的線性 endpoint

A6/AP14把 `G-V` 展開後，theta concavity及 SHCN cutoff mismatch全部是 o(1)；唯一
主 defect為 `Q=int(psi-u)q(u)du`。因此 Akatsuka不是獨立第三個 prime cancellation，
而是 AP11 critical integral的 logarithmic Cesaro mean。這仍是策略改善：critical-line
oscillation被衰減，target從 eventual pointwise barrier降成 bounded-above。

下一步只攻 `sup Q<infinity`。A6.6 的 positive Mellin mixture可作工具，但不得從
`s>3/2` 或 c=2 的單點/緊子區間 bound直接取 endpoint；若常數不 uniform，極限正是
G135。若找不到 endpoint-uniform Tauberian/convex theorem，兩條 arithmetic支線應視為
同一缺口而非相互佐證。

## 35. Selberg lens定位：不可切成固定小質數子題

依 nudge 做的 SHCN plateau掃描顯示，早期最大值雖由17/19夾住，漸近區局部極值則由
接近 Y 的 frontier primes夾住；free-energy mass也以 `p>Y^(3/4)` 最大。這確認 G-V
的微小 defect不是少數小 primes主導，而是 bulk smooth term與全 prime scales抵消。

因此策略上不追「驗完若干 dominant primes後證 tail容易」。explicit formula顯示正相反：
任何 off-line zero的 growing term由 frontier尺度保留，low-prime cutoff只有較小 exponent。
唯一可能的分割是 subtract exact low scales後，直接證 renormalized frontier window有
endpoint-uniform bound；這仍是 G135，而非較弱 zero-blind 命題。數值掃描只用來否決
錯誤切割，不計為證明進度。

AP15把此 no-go升級為解析定理。對 proportional window `Q(Y)-Q(Y^delta)`，縮放項的
spectral abscissa只有 `delta A`；任何位於 `(delta A,A]` 的 zero singularity在差中
保留，Radziejewski迫使兩號無界。因此 frontier-only boundedness仍等價 RH。後續可用
此 window減少低-prime bookkeeping，但不能宣稱它降低了定理強度；真正突破仍須給
frontier arithmetic cancellation，而非再切更多固定比例層。

## 36. ordinary Selberg mean square亦非所需 square

ES124/AP16 顯示，即便使用 RH下最佳 dyadic mean-square尺度，absolute Cauchy--Schwarz
仍留下 `sum_k 1/k`。所以「找一個全正 L2 energy控制每個 prime block」不是 AP14 的
升階定理；它必然失去使 logarithmic mean收斂的 zero phase。後續若稱 square closure，
必須展示跨 block off-diagonal terms如何 telescope或形成 bounded primitive。只給
`I(X)<<CX^2`、改善 C、或有限高度 zero sum均不達驗收標準。

## 37. fractional Selberg square列為 validation filter，不列為 closure

新 family `S_alpha=L^2-alpha L'` 證明正 Dirichlet係數與 robust nontrivial-zero
double poles可以同時存在；`0<alpha<1` 不受未知 zero multiplicity影響。

依 Selberg-lens nudge先做 scaling audit後，自然 Cesaro critical bound仍 exact排除
所有 off-line zeros，故只是一個 RH criterion。策略上不刷數值，也不把 holomorphic
square誤認為 modulus square。只有找到 unconditional signed telescoping identity，
並在扣除 `s=1` pole後留下可由 arithmetic positivity控制的 remainder，才恢復此支
為 live closure route。

## 38. all-degree moment mechanism已存在；不得把 half-plane bridge省略

SFS9 將全部 `(zeta^k)^(r)/zeta^k` 同時實現為一個 positive `log N` moment sequence，
所以任意 degree Hankel PSD不是問題。其 pole scaling更 exact趨 Gamma/Gaussian。
這回答「degree 3能否升階」：在 `Re(s)>1` 可以一次升到全部 degree；但該結構是
pole-local且 zero-blind。真正斷層是正 measure不能由 Dirichlet收斂域無條件延拓到
critical strip。後續不得再計算有限 moments；只接受能跨越此 boundary且不預設
zero-free region的 positivity-preserving continuation theorem。

## 39. probability continuation route降級為 exact RH coordinate

ES126 已證 infinite-divisibility型 critical-strip continuation與 RH等價。因此 SFS9
不能再以一般 Levy/Bochner延拓 theorem列為 live closure。只有直接由 primes+gamma
建造正 Levy measure而不先引用 zero frequencies，才會是新機制；否則它與 Weil/GNS
positivity是同一義務。

## 40. AP sign、Lévy exponent、Weil square三線合流

AP18 顯示加入 exact archimedean counterterm後，g0成為 zero measure的二次 primitive。
其 pointwise負號、conditional negative definiteness、以及 `-g''` positive
definiteness依序是同一 spectral positivity的不同強度；足以反推 RH者仍是完整
CND/Weil層級。後續只保留一個 live target：不用 zero expansion，直接把完整
prime--gamma distribution factor成正定 kernel。不能將三種表述相互當作外部佐證。

## 41. Selberg-lens nudge：Fenchel vertex family亦立即等價 RH

SC1--SC3 把 g_zeta 的 primes顯式公式轉成 cumulative prime-power polygon；所有
vertices壓過 B conjugate iff RH。這是合格 all-complexity reduction，但不是較弱
positivity theorem。依 nudge停止把換座標當進展：只有能由 Euler/prime-power結構
獨立證明 SC4 defects全非負的 telescoping/majorization，才重新啟用此支。

SC5/G145 已用 rigorous opposite-sign witnesses排除逐 transition monotonicity。
此後不得以更多 vertex batches替代全域 identity；只有跨多個 prime powers仍保留
signed cancellation的 telescoping/transport theorem符合驗收標準。

Gaussian transport符合 nonvanishing要求但未通過 sign-producer要求：AP20證它對任一
fixed variance仍 exact等價 RH，inverse又不保正；TPD8排除相應 frame bound。故不重啟
J24 finite Gaussian route，除非出現新的 backward-heat positivity theorem。

## 42. Selberg quantile變分：absolute PNT bounds 不足，必須保留 phase

AP21 將 nudge 的建議做成完整 relaxation theorem。exact slope identity為
`Y=2e^(t/2)-1+A_R`，其中
`A_R=e^(-t/2)R(e^t)+(1/2)int_1^(e^t)R(u)u^(-3/2)du`，而
`H=H(T)-int(Y-B')`。若只以 `|Y-B'|<=E` 與 `Y` 單調作變分，任何不可積的遞增
allowance都容許 `Y=B'+E_0`，使 gap趨負無窮。

最新 Vinogradov--Korobov PNT error在此座標給指數增長 allowance；甚至
`R=O(sqrt(x)log^2x)` 的 RH尺度 magnitude也只給 `E=O(t^3)`。因此不再尋找更好
pointwise constants或以 envelope做 linear programming。SC route只有加入 signed
cross-scale/off-diagonal arithmetic constraint才保持 live；該 constraint必須先於
RH criterion成立，不能直接寫成所求 primitive boundedness。

## 43. reciprocal-Xi PF-infinity 不另計一路

ES128 是真正 uniform all-degree theorem，但 Schoenberg factorization在平方變數下
逐字等於既有 Stieltjes--Thorin正 measure target。Euler product只能展開 real-axis
tails，中央 Fourier correction是未控加法，不能用 PF convolution closure吸收。
因此策略上只保留一個共同 target：直接由 theta/primes產生完整 positive
Stieltjes measure／Loewner--Whitney convolution factorization。只證 reciprocal
kernel非負或 positive-definite仍不足；finite minors亦不重啟。

## 44. ordinary-Laguerre Parseval：全階正能量已取得，但尺度仍等價 RH

Arias de Reyna 的外部 theorem與 D10.4 合併給 `E_n=n a_n`，其中 `a_n`
是 `Pi(e^t)-Li(e^t)` 的 ordinary Laguerre coefficients，且 RH iff
`(a_n) in ell^2`。這一次確有 all-degree orthogonal/Parseval mechanism，回答了
「是否只有有限 degree」：不是；全階結構存在。斷層在 arithmetic norm finite，
它本身 exact等價 RH。LS2 將可接受輸出放寬到負指數門檻的 density zero／長好
block；尚無 weak-type Laguerre theorem從 PNT或 Selberg正係數推出它。

AL5 提供更適合全正性的等價版本：只需對每個 epsilon找到長度趨無限的
遠端 blocks，使 ordinary-Laguerre coefficient energy `sum|a_n|^2` 次指數。
這是有限-rank Christoffel--Darboux PSD quadratic form，且嚴格弱於 global ell2。
下一個可接受輸入因此可具體寫成：由 prime arithmetic直接證某些任意長 index
blocks 的 AL5 energy bound；全域 M1尺度或逐係數 D10 bound都不再是必要格式。

## 45. 新 Li 漸近 claim 不提供 closure

Suman 2026 稿件看似正好提供由 PNT到全部 Li coefficients 的 uniform estimate，
但原文核心消去式用了錯誤的 chain rule：`Y(x)=L_n(log x)` 的 x導數與 Laguerre
argument導數被混用，故 (53) 不是 ODE左邊。後段 Bernoulli無窮和亦發散。
因此不能把此 claim當外部 breakthrough，也不能藉修正記號沿用其 remainder估計。

策略訊息是負面的但明確：pointwise PNT envelope乘 Laguerre fixed-argument asymptotic
仍未控制 AL5 的 signed block energy。續行只接受保留 off-diagonal/cross-scale phase
的 theorem；不再追此稿的逐 n absolute-bound架構。

## 46. Suzuki Gram / Goldbach M-function：全階座標新增，義務未消失

Suzuki 的 `G_n` 將每個 degree放入同一 `L2`，所以全 Gram matrix無條件 PSD；
但 RH內容全在 `lambda_n=||G_n||^2/(2pi)` 的識別。識別所需 `Theta` inner正好
等價 Hermite--Biehler/RH，故此線與 Weil/de Branges全正合流，不重啟 finite norms。

Goldbach `r_2=Lambda*Lambda` 是少數真正保留 prime two-scale coupling且係數非負的
外部介面。惟論文的 centered secondary term `H` bounded iff RH；`r_2` 總量扣主項後
無 sign，conditional remainder不能作輸入。續行只接受 centered convolution 的
uniform inequality／tightness theorem；普通 positivity或 compact-support假設不算 closure。

SMG5 進一步把 pointwise boundedness放寬為次指數 `dX/X` L2 energy，仍 iff RH。
此判準以 Laplace pole直接排除任一 off-line zero，且 prime formula完全顯式；因此
Goldbach支線下一個最小 target改為此 centered energy的 `O_epsilon(Y^epsilon)`，
不必先證逐點 square-root error。它仍需要真正 off-diagonal cancellation。

Han ES133 又排除「提高 Goldbach convolution degree」：smooth `F_k=Psi^k`，
sharp remainder藉差冪分解逐字回到 `Psi-x`；centered convolution則失去係數正性。
因此只保留 reflection/conjugation 型 autocorrelation或能直接控制 SMG5 energy的
新 identity。固定 k的更多正 Dirichlet/additive coefficients不算新路徑。

SMG7 已把 live target固定成單一 all-size PSD matrix `K_Y`。這滿足使用者要求的
uniform-in-degree結構，不再有 degree 3斷層；新斷層是對 arithmetic vector
`Lambda-1` 的 quadratic-form上界，而一般 PSD只給下界。後續只攻 max-kernel的
reflected/order correlation或同一 kernel的 operator contraction；sum-kernel
Goldbach estimates與 finite principal minors皆不再計入。

SMG8 將同一 max-kernel以 Mellin transform對角化。下一個 theorem不再模糊：必須
從 arithmetic side把 `(-zeta'/zeta-zeta)/[s(s+1)]` 的 vertical H2 control由
`Re s>1` 推到每個 `Re s>1/2+a`，且不能預設 pole-free。若只證 averaged lines、
避開 zero real parts、或使用 analytic continuation本身，都不能排除離線 poles。

ES134 進一步關閉 generic Hardy-space捷徑：現有 theorem已把 bounded evaluation與
closure分開，前者到 p=2可做，後者在 p=2正是 RH。只在 p<1成立的 cross-space
`(I-S)^(-1)` bound不能插值到臨界 Hilbert norm；compact-open density亦太弱。

## 47. log-stationary Green化簡：保留，generic contraction與 local-inner捷徑關閉

PG1--2/L15 將 `max` kernel完整化成對數平移不變的 causal Green Gram：單一二階
stable filter與嚴格正頻譜同時處理所有 degree/scale。這是結構進展；finite minors
或 degree刷證書不再需要。exact endpoint tail也已分離。

但 block同號係數給 `Q>>N` 而 weighted coefficient square僅 `O(1)`，所以任何不使用
`Lambda-1` 特性的 universal Hilbert contraction必為假。Connes--Consani又證 local
factor不 inner，global support補救仍是 Conjecture 4.1；Baez-Duarte critical closure
則與 RH等價。續行只接受 global Poisson/prime--gamma support identity直接產生
`exp(o(T))` forcing bound，不能把 conjectural Weil sign或 Nyman closure當引理。

## 48. Selberg symmetry稽核：有升階代數，沒有升階正性

Selberg identity及其 higher convolution版本確實是所有 degree的統一機制；但 Mellin
側只有 `L^2,L^3,...` analytic powers，沒有 conjugation，不能控制 L15的 spectral
modulus square。short-interval Selberg integral提供 origin-average，L14則要求固定
原點的 nested maximal control。除非找到保留 `Lambda-1` 結構的 deterministic
average-to-maximal theorem，停止擴張 Dirichlet convolution degree。

## 49. Selberg nudge後的 contraction稽核：endpoint等價 RH，改追 exponent map

PG6精確證 Green energy exponent為 `2 sup(Re rho-1/2)`。所以原訂
`exp(o(T))` global contraction不是中間引理，而就是 RH。Hardy extension、inner
kernel、Weil/Nyman closure也同層，不應彼此循環引用。

研究單位改成 quantitative exponent：先找無條件 `theta<1`，再要求 Selberg/global
Poisson機制給 `Phi(theta)<theta` 並可迭代至 0。若 theorem只給相對 PNT error
`exp(-c log^a Y)`，energy power exponent仍為 1，不算第一步。

PG7另給 completed logarithmic derivative的 all-degree Pick kernel，但其 interior
PSD exact等價 RH。functional-equation boundary模一性被 explicit off-axis quartet
all-pass model否決，故停止只操弄 boundary reflection；必須產生 interior sign。

## 50. Landau polynomial barrier：degree優化不能產生第一個 fixed exponent

外部最佳化文獻與 PG8一致：在能逐項丟棄其他 zeros的 `a_k>=0` class，target
coefficient必伴隨至少同量的 gamma `log t` mass；所以任意 degree只改進
`1-c/log t` 的 c，不能給 `sup beta<1`。signed coefficients雖可消 leading gamma，
卻把未知 harmonic-height zeros變成 adverse terms。除非取得新的全局 zero-correlation
sign，停止 trigonometric polynomial degree optimization。

## 51. Selberg exponent-map檢查：zero modes為中性，純 identity路線關閉

在任意 zeta zero附近，Selberg Riccati identity兩側 Laurent主部逐項相同；simple
zero的 double pole恰消，位置實部完全不受限制。因此它不能自行把 exponent theta
壓成較小 Phi(theta)。RHS的 Moebius convolution若要 sharp估計，又需要控制
`1/zeta` poles。除非有獨立 signed-Moebius/reflected-square theorem，停止以 Selberg
identity重排 AP11、AP14 或 Green detector。

## 52. reflected Moebius square：conjugation取得，但 continuation exact等價 RH

`|1/zeta|^2` 的確把 mu變成 all-degree PSD multiplicative autocorrelation；然而把
此 norm從 absolute-convergence half-plane推到所有 `sigma>1/2`，任一 off-line zero
都在 `sigma=beta` 造成不可積 pole，故又是 RH endpoint。現有 averaged Chowla只平均
additive shifts，量詞不足。除非有新的 fixed-line reciprocal-zeta theorem，停止以
已知 Mobius randomness宣稱 reflected-square closure。

## 53. near-`p=1` Hardy嘗試關閉：evaluation half-plane方向錯誤

外部 `H^q,q<1` closure雖完整，但其 bounded evaluations只在 `Re s>1/q>1`；
`q->1-` 仍只到 PNT邊界。cross-space inverse同時要求 source `p->infinity`，沒有
可穿越 q=1 的同空間 bound。停止把 pole的 local Lp threshold與 Nyman Hardy exponent
混為一談。

## 54. Nyman Cholesky全正：uniform determinant存在，但不控制 closure norm

外部 conjecture符合所有 degree一次的形式；然而 NC2證 entrywise Cholesky
positivity與 positive target coordinates不排除額外正交分量。RH內容仍在
`||L^-1F||^2=1`，不是 L 的 signs。故不投入 finite entry驗證；只有能定量消滅
orthogonal residual的 theorem才可重開此線。

## 55. Nyman特殊資料稽核：boundary vector發散，完整 Gram tail才可能有用

NC3/L18辨識出固定欄極限是 `s=0` Mellin residue，座標向量必不在 `ell2`。
NC4再證即使加入 exact `F_k=log(k)/k`、`a_k=(k-1)/k`、positive `E`、
remote-column law及 `||f_k||->0`，仍可抽象保留正交殘差。因此不再嘗試從
entrywise signs或固定欄漸近直接推出 RH。Ehm 2024 的 full Gram decomposition
指出一個具體新接口是 truncated Möbius inversion error的 uniform bound；其餘
centered Landau/Mertens products亦未被證明 negligible，而 `q=2` smoothing本身仍
RH等價。後續只接受利用 ratio-dependent `S_q(n/m)`／整除結構控制全部 moving
row tail的 theorem。

## 56. Ehm moving boundary：Sobolev加權不取代 Möbius phase

NC5/L19把 inversion error拆成 coefficient-correction與 `n>N` Möbius tail。
由 `S_q` 的 fixed-ratio非零區間及 square-free density，tail的 absolute mass在
`q=1,2` 均至少線性尺度（Levinson--Selberg outer weight後仍 `N/log N`）。故停止
利用 `S_2(x)=O(x^-4)` 作逐項 tail estimate：那只控制 far ratio，漏掉
`m,n asymp N`。唯一可續的是保留符號的 two-scale Möbius bilinear estimate，或把
correction/tail exact重組成一個已有獨立正性／正交性的全域 transform。

## 57. cotangent-sum文獻：fixed power saving尚未抵達同尺度

Maier--Rassias已證相關 `mu(n)g(n/k)` 在 `n about k^D,D>=2` 有 fixed-power saving；
這不是普通 PNT bound，值得保留為 far-tail工具。但 Ehm inversion error的 absolute
barrier集中於 `n/k=Theta(1)`，且 `S_q` 與 `g` 仍需轉換。搜尋未見 `D=1` extension。
因此不得把 far-ratio theorem外插至 moving boundary；合格突破仍須同尺度 bilinear
Möbius estimate或 exact reciprocity把同尺度 box送到已控制區且不新增 boundary term。

Ehm的實際 reciprocity已核對為 `r<->1/r` 加 explicit elementary terms；它保持
fixed-ratio尺度，elementary terms又回到未閉合的 centered Landau/Mertens products。
所以後一種「送到已控制區」並未發生，正式關閉此自然捷徑（G174）。

## 58. Ehm decomposition不是獨立 detector

NC5.6--5.7 證 full ratio kernel的 Fourier symbol就是
`|zeta(1/2+it)|^2/|1/2+it|^(2q)`。故 inversion tail、correction及 elementary
products若全被控制，合起來就是原 Nyman mollifier norm；不能把它們拆成多條路後
互相引用。只保留一個研究問題：是否有不經 critical `1/zeta` 的同尺度 Möbius
bilinear theorem。沒有此新輸入時，Ehm座標已完成強度稽核但未證 RH。

## 59. 同尺度門檻已精確化：`B_N=o(N log N)`

NS1把 Levinson--Selberg moving tail的固定比例 box寫成 `B_N/(N log N)`，其中
`B_N` 是 `asymp N^2` 項的 signed Möbius雙和。Mellin separation把它變成相鄰
dyadic Möbius Dirichlet polynomials的積；generic Cauchy、large sieve與 absolute
Fourier integral都停在 `N/log N`，不是 `o(1)`。故不再以更強 Sobolev decay或一般
Hilbert estimate重攻此 box。

## 60. ordinary Chowla 甚至猜想級逐 shift bound仍不足

把雙和依 `h=n-m` 展開後，需要同時保留 shift內與 shifts間兩層 cancellation。
逐 shift `O(sqrt N)` 後取絕對值仍有 `N^(3/2)`；MRT averaged Chowla只保證
`o(N^2)` 型 absolute average。後續不得以「已知 Möbius平均隨機」代替完整 signed
二維 theorem。

## 61. generic bilinear升格會直接循環到 RH

若 `o(N log N)` 對所有 smooth two-variable kernels成立，rank-one kernel立即給
smooth Mertens square-root bound並證 RH（L20）。所以唯一可能較弱的新輸入必須精確
使用 `S_q`/inversion corrections；然而全部 pieces聯合控制即 NC5.7 的 RH-equivalent
Nyman norm。Ehm支線至此暫停，除非找到新的 kernel-specific reflected positivity或
signed cancellation identity；finite certificates與更多 VERIFIED batches不重啟。

## 62. Selberg nudge：single kernel 的量詞分界已封閉

full same-block、Banach-uniform cutoff版可由 Wiener inversion除去 `S_q`，故仍直接回到
rank-one Mertens/RH。fixed Levinson tail scalar則沒有此退化；lacunary block模型證明
固定 ratio bilinear消失可與巨大 partial sums共存。後續不得再用 L20錯封自然 tail，
也不得把一個 fixed-cutoff估計誇成 generic kernel theorem。

## 63. divisor/identity-factory捷徑在首帶逐字失敗

雙 logarithmic Cesaro式是新 exact座標，但 `u<j<=2u` 上 truncated divisor sum恰為
`-mu(j)`。因此主要同尺度 Möbius phase完全保留；Ramaré--Zuniga的 `sigma>=1`
positivity只控制 scalar smoothed sums，不能穿過 `R_q(j/m)`。除非找到首帶與
`j>2u`/Landau corrections的 exact反射平方，暫停此改寫。

## 64. critical local Orlicz positivity（最小 target 由 65 降至 q=2）

Verjovsky的一次估計給 `q -> 1/[2(q+1)]`；Orlicz LM3.1一次生成全部 finite `q`且
等價 RH。strategy65進一步證 fixed q=2已足夠，故 Orlicz不再是最小 target，但仍是
有效全正版本。禁止逐 degree刷 moments不變。

## 65. local moment degree斷層由 exponent bootstrap真正關閉

VA2--VA4顯示不必證 arbitrarily high moments：任一 fixed `q` subpower local norm會把
Mertens exponent displacement反覆除以 `q+1`。因此停止 LM2 的高階 sinc expansion；
live target降為 `q=2` 單一 all-size PSD Toeplitz form VA4.4。這不是 finite certificate，
而是帶明確可迭代 exponent map的 uniform theorem。

## 66. Orlicz dual未連上 SK5首帶

Gibbs dual要求所有 entropy densities的 additive Toeplitz quadratic upper bounds；
SK5.2只能造一個 multiplicative-ratio signed witness。平方該 witness既只給 lower bound，
又升成 fourth order。停止直接以 divisor coefficient充當 Orlicz dual certificate；只有
exact ratio-to-difference transmutation或對所有 densities的 arithmetic inequality才可重開。

## 67. fixed-q bootstrap通過 Selberg nudge量詞稽核

對每個 final epsilon只走有限 exponent chain，逐步 loss可預先分配；不要求 constants
uniform in delta。保留 q=2 criterion，不退回 unbounded moments或 finite certificates。

## 68. prolate/Legendre只作低模態定位，不作「譜衰減即證明」

允許用 spectral decay嚴格丟掉高模態；但前 `logN/loglogN` 個 Möbius projections沒有
arithmetic bound。除非取得 joint low-mode square-root theorem，不再以更多 eigenvalue
數值或有限 PSD驗證宣稱進展。

## 69. `mu log` 尺度式沒有 fixed-arc contraction

所有窄 arc的一致控制已含 Mertens point value；fixed arc則 loss恰為 1。暫停單靠
Minkowski/Cauchy重跑 LQ4，只接受 convolution主項的新 signed bilinear估計。

## 70. Lambert dilation保留為 special-forcing transfer問題

all-scale identity是真結構，但 generic inverse symbol為 `1/zeta(s+1/2)`。禁止假設
uniform coercivity；只在能利用 RHS、Gamma decay或 functional equation排除 off-line
power modes而不先假設 zero-free half-plane時重開。

## 71. low-prolate joint estimate降格：首模態已 RH-strength

對 `c=1/(2pi)`，Legendre `k=0` weight有 zero-free Mellin transform。其 square-root
bound單獨 iff RH。因此不再把「聯合控制前 logN/loglogN modes」描述成較弱目標；
只有能直接產生 sinc-smoothed Möbius cancellation的新算術正性才算進展。

## 72. Lambert special-forcing/Gamma route正式關閉為等價改寫

forcing Mellin numerator為 zero-free Gamma，不能消 denominator zeros；functional
equation亦只反射。停止從 explicit formula本身尋找免費 coercivity，除非加入一個
不預設 RH的正能量或 pole-location theorem。

## 73. 以 positive Volterra取代 derivative bootstrap作主升階機制

L32對所有 fixed `q>=1` 使用同一 local mean，再以顯式 supremum contraction恢復 Mertens。
保留 L24作獨立檢查，但後續引用 fixed-q equivalence時優先用這個無迭代證明。研究 target
降成 sinc-smoothed單一 scalar；不得再宣稱 degree/constant量詞是缺口。

## 74. Müntz source inversion不列為新 proof producer

compact sinc的 inverse source在 `1/N`就是目標和，symbol為 `W/zeta`。Báez-Duarte
general theorem亦把此類 zero-free compact kernel的 closure列為 RH等價。停止把 source
kernel的重新命名視為進展。

## 75. sign-definite `-Pf` 只允許 signed closure

positive cone因共同 `1/x` tail嚴格不能逼近 compact target。若研究其 Gram/closure，
必須先提出控制 signed coefficients及 tail cancellation的 uniform theorem；finite positive
entries或 Perron eigenvector不夠。

## 76. sampling Parseval只作強度定位

all-sample energy已 exact refold成 Mertens歷史平方。不得用 weak Mertens conjecture、
數值 sampling或 truncation error作上界。只有能特別隔離 `k=1` 且係數 norm不發散的
arithmetic projector才可重開。

## 77. sinc dilation boundary relation關閉

alternating reconstruction係數非 `ell2`，與先前 Nyman boundary-vector障礙同型。
停止以 Abel limit加 Cauchy估計；任何新 sampling identity必須帶 uniform coercivity。

## 78. signed closure只接受同時控制 tail與 critical-line error的 theorem

候選係數必證 `C(1)->0` 且 weighted mollifier error趨零；只做其中之一不算進展。
W是 zero-free outer factor，不能用 kernel smoothing掩蓋 zeta zeros。

## 79. bounded coefficient projector正式排除

critical zeros迫使 `sum|c_k|/sqrt k->infinity`。後續不得再尋找 uniform weighted-ell1
inverse；合格設計必須容許 coefficient mass增長並定量控制其造成的其他頻率誤差。

## 80. smaller-scale dilation recurrence不作 induction gain

依 nudge，k-th coordinate本身是 scale N/k的 Mertens/sinc target。`k^-1/2` 臨界和
沒有 contraction。除非找到保留 k間 signed cancellation的 theorem，不以「尺度變小」
宣稱進展。

## 81. Burnol lower bound與 sparse Gram只作必要性稽核

zero-induced distance lower bound、conditional approximants及 off-diagonal compression都不
提供 closure upper bound。禁止從 matrix compressibility或預期 optimal rate外插 RH。

## 82. ordinary-Laguerre block線完成相鄰定理稽核

`laguerre_block_uniform_audit.md` 先固定唯一輸出 AL5 block energy，再逐條代入
polynomial large sieve、MZ、uniform Plancherel--Rotach、Riemann--Hilbert與 Hardy
inequalities。結論是 basis/kernel端已有真正 uniform-in-degree結構，甚至 difference
Gram的 condition number只作 `H^2` 成長；但所有成熟 sampling theorem控制 positive、
well-spaced/Gauss nodes，不能估 prime nodes減連續主項的 signed discrepancy。故本線不再
查一般 Laguerre asymptotics或 frame theorem；只在找到可直接給 LB8.1 的 centered
quadrature/signed Carleson theorem時重開。下一順位恢復 controlled-growth signed
projector；strategy79只排除 bounded norm，沒有排除定量發散 norm。

## 83. signed projector改以最小局部控制成本為主 target

SC7--SC10證 fixed frequency window的 tail-exact approximation總能做到；qualitative
completeness不足，因 coefficient norm可能爆炸。定義 `kappa(T,delta)` 為 local error
`<=delta` 的最小 `sum|c_k|/sqrt k`。經 zeta 二次矩改進後，唯一合格輸出是找
`delta(T)->0` 使 `kappa(T,delta)^2logT/T->0`（任意 `alpha<1/2` 的 polynomial cost
即足夠）。這會直接推出 global closure；反之 RH下可對 fixed approximants後選 T。
後續只找 clustered frequencies `log k` 的
quantitative controllability/biorthogonal norm theorem；bounded inverse仍排除，但整條
signed route保持 live。SK5.2與 Lambert/sinc遞迴不重開。

## 84. mollifier mean-value theorem只作 applicability filter

Atkinson/Ingham二次矩是獨立 input，已實際把 tail exponent從 `1/4` 提高到 `1/2`。
Radziwill arbitrary-length lower bound則因 sinc weight在高 shell為 `T^-2`、且 K不限制
support length，不能控制 kappa。停止一般 mollifier比例/零點文獻檢索；只有能直接給
tail-exact local approximation的 coefficient-cost **upper bound** 才重開。不得把 kappa
定義或 `1+zeta C` 的零點插值性質當成義務縮小。

## 85. Pechersky只保留為 support-complexity子問題

bounded-coordinate Dirichlet approximation可把 K對 support N壓到 `N^o(1)`，所以不是
完全無用的 generic density；但 fixed-window density沒有 N對 window/accuracy的 rate。
後續可查的唯一窄題是 Andersson/Pechersky construction的有效 support bound，驗收式為
其 coefficient envelope下直接推出 `K(N(T,delta))^2logT/T->0`。只重述 density判準、
逐座標 bounded或 support次冪 norm都不算完成。

## 86. 不以 support-free ell2/GCD norm取代 K

SC13的同相遠端 block反例排除任何 `A(T)||d||_2^2` 型 uniform shell bound。twisted
second moment只在 support length受 T控制時可用；GCD spectral theorem亦不是超密
frequency的短窗 frame。後續 quadratic改進必明列 max support或 local log-cluster norm，
並檢查 Pechersky construction是否實際控制它。另依 nudge，regularized reciprocal的
smoothness不得當作 PNT推論；uniform critical regularity先視為 zero-exclusion循環。

## 87. controlled projector新增 cluster-product驗收式

除 SC10的 `K^2logT/T` 外，SC15證更細充分條件
`K B_T log^2T/T->0`。後續不必強求 max support本身小；若能直接構造 coefficient
envelope及 signs使解析度 `1/T` 的 cluster norm B_T足夠小，也可過關。任何引用
large-sieve/frame theorem必逐字核對它控制的是此短窗 cluster norm，而非長平均 GCD
kernel或裸 ell2。

## 88. signed projector改用 fixed beta kernel吸收任意 polynomial cost

SC16是 all-order解析公式，並非恢復逐 degree certificate。後續搜尋 local
controllability時，不再要求 exponent低於 1/2或3/4；只要取得任何 finite A的
`K<=T^A`（或 `K B_T<=T^A`），即可先選一個 fixed `m>A` 完成 tail。這大幅降低
相鄰 theorem驗收門檻，但 qualitative density、support-subpower及 constants依 T任意
退化仍不算 polynomial theorem。升 m只能在取得 finite A後一次完成；其合法性來自
`W_m/W_m0` 的 critical-line bounded multiplier。不得讓 m隨 approximant無控制增長後
冒充 fixed criterion。

## 89. beta升階的 target-change nudge裁決

nudge正確要求不能只憑「kernel ratio bounded」推斷任意新 target可逼近。本 family另有
exact事實：同一 C滿足 `Ehat_m=W_m(1+zeta C)`，所以
`Ehat_m=(W_m/W_m0)Ehat_m0`；target與 generator共同更換後 residual不變。由 critical-line
bounded multiplier可嚴格轉移 local error，且 `C(1)=0`不變。因此升階機制保留。

但這沒有證 polynomial coefficient cost。唯一 live驗收式仍是某 fixed m0存在
`delta(T)->0`與 finite A，使 tail-exact local error趨零且 `K<=T^A`，或
`K B_T<=T^A`。此式一旦證得即推出 RH，故候選 theorem若假設 `1/zeta`、Mertens critical
bound或 zero exclusion，立即標記循環。

## 90. 階段性停攻與下一棒

- ordinary-Laguerre：basis/uniform-degree問題已解；generic adjacent theorem不適配 prime
  signed discrepancy，暫停。不是宣稱 arithmetic quadrature不可能。
- signed projector：bounded-norm及 ell2-only繞道已排除；controlled polynomial-growth
  版本保持唯一主線。
- SK5.2與 Lambert/sinc recursion：無直接新 input前不重開。
- 下一輪第一步：量化 Andersson--Pechersky proof的 finite partial-support rate，立即對照
  strategy89驗收式；若只得 qualitative convergence，明確記為不合格。
- 本輪不開新支線；RH未證，goal保持 active並停在安全交接點。

## 91. Andersson rate audit：關閉 generic Pechersky uniformization，保留 target-specific dual

已逐行核對 arXiv:1207.4624 Theorem 3 proof。其核心輸入是
`forall f!=0, sum_n|<f,x_n>|=infinity`；任意 finite prefix卻有共同正交 unit direction，
所以不能交換成 `exists N(T,R) forall f`。Hadamard-product與 zero-deletion估計只對 fixed
f，Pechersky theorem本身亦無 stopping modulus。故 strategy85 的 Andersson proof抽
rate入口正式關閉；不宣稱真實 optimal cost為 super-polynomial。

下一棒仍在同一 controlled-projector主線，但改用 exact target-specific Hahn--Banach dual。
對 fixed beta target `y_m`，finite-prefix polynomial K存在 iff對每個 f有
`|<y_m,f>|<=delta||f||+K max_n sqrt(n)|<a_(m,n),f>|`。下一工作只攻此 special-target
norming inequality；all-target frame bound既過強又被正交反例否決。critical-zero no-go只
要求 K發散，尚未排除 finite polynomial，所以路線保持 live。RH未證，goal active。

## 92. regularized reciprocal只准走 one-sided arithmetic Hardy 路

L47以 Poisson--Jensen明示反例封閉一個自然捷徑：一般 smooth target即使有任意固定階
Sobolev polynomial bound，也不能以 polynomial coefficient mass轉成單邊 `-log n`
Dirichlet frequencies。對 `exp(i omega t)`，任何 `K<=T^A` 的下半平面 H-infinity
approximant都有不趨零的 absolute L2 lower bound。

因此 AP2/Handoff-2 若續攻，只接受 special zeta target的 lower-half-plane
factorization、outer/inner算術 identity或等價的 target-specific dual estimate。實軸
regularization後套 generic Fourier/Jackson、或把 two-sided modes用 superoscillation換成
one-sided modes，正式淘汰。這仍不排除 special target的 polynomial K；RH未證，goal active。

## 93. critical-zero極端參數裁決：保留 AP2.5，不外插 ridge爆炸

L48嚴格給端點距 zero為 d、multiplicity r時的 lower bound
`K>=c(d+Cdelta^2)^(-r)`。故首零點附近已知 obstruction只是 inverse-distance/error的
polynomial；m=4只改 W_m常數，不改此結構。數值 ridge成本的更劇烈增長不能當
super-polynomial no-go。

策略上 AP2.5仍存活，但下一證明必須處理 global one-sided interpolation；局部 zero
估計、更多 N掃描或 generic real smoothness都不再提供裁決力。

## 94. 下一 producer 固定為 MB1，不再使用「one-sided interpolation」泛稱

L49/AP5把候選固定為 logarithmic Riesz--Möbius mollifier
`C_X=M_X(1)-M_X(s)`、`X=T^B`。tail constraint exact，K無條件為 polynomial；驗收只剩
fixed `m,k,B`、`2m+1>B` 的 weighted critical-line mean MB1是否沿 unbounded sequence
趨零。

後續先做 exact divisor-coefficient/mean-square展開並標出 diagonal、off-diagonal與 Abel
boundary。若 absolute value、PNT或既有 mean-value theorem停在非零 main term，記錄最小
失敗點；若 signed structure存活，再推嚴格 bound。不得更換成任意優化 coefficients後把
數值小誤差當 MB1證據。RH未證，goal active。

## 95. MB1裁決：保留為 test form，停止當作新 producer

L50把 bulk化成 centered prime-square；L51又證 `y>X` 精確留下 moving same-scale Möbius
block。任何 fixed logarithmic Riesz order只給 log gain，PNT error在平方能量中仍差一個
power 1/2。讓 k隨X增長違反 fixed-parameter量詞；把 tail與 prime/boundary分開估則可能
丟掉唯一 joint cancellation。

因此 MB1命題未被反證，但已回到先前 NC5/L20 的 RH-scale signed same-block obligation，
不再算獨立攻面。controlled-projector路線的三個具體 producer（Pechersky rate、generic
Sobolev-to-one-sided、fixed Riesz--Möbius）均已到最小失敗點。下一順位轉到既有
ordinary-Laguerre LB8.1，先只核其 centered prime measure是否有不同於同一 Mertens block
的 exact dual；若同構，立即合併封存。RH未證，goal active。

## 96. Laguerre comparison裁決：geometry不同，下一步鎖定 LB9.1

L52證 LB與 AP7只由 nonlinear triangular exp/log相連，沒有 same-block isomorphism；因此
Laguerre prime-linear CD geometry保留。AL5量詞已固定為 `H_N=ceil(log(N+2))` 的 LB9.1，
仍 iff RH，且 basis condition loss僅 `O(log^2N)`。

L53再排除 positivity+PNT-envelope producer：純冪 centered model完全符合這些 generic
inputs卻有 fixed-base exponential Laguerre coefficients。後續只接受 actual prime-power
nodes/weights的 signed correlation，例如能直接控制 LB9.1 CD quadratic form的 deterministic
prime theorem；generic measure、pointwise PNT與 positive sampling theorem不再檢索。

## 97. LB9.2 驗收格式固定為 finite cutoff joint moment square

L54的 LM6.3 是完全可算的 centered CD quadratic；L55再把它寫成 centered prime log
moments經 binomial矩陣的 Euclidean norm。後續 theorem必直接保留 cutoff Y上的三項 joint
cancellation，並在先 N後 Y的量詞下給 `exp(o(N))`。

下一步只測 Selberg identity/higher convolution在 LM7 metric中是否真正產生 PSD square。
若仍只是無 conjugation的 analytic moment products（strategy48的既有警告），即記為
prime-specific producer失敗；不再以「Selberg symmetry」名稱保留模糊候選。

## 98. Selberg substitution裁決：uniform all-k algebra仍只見 t+u

L56完成 strategy97。centered Selberg identity的二次項是 eta*eta；higher hierarchy的任意
二次 variation也只能產生 `h(t+u)`。LB associated-Laguerre CD核由最高 bidegree直接證非
Hankel。因此 Selberg不是 LB9.2 producer；這是 exact all-k裁決，不是 finite matrix猜測。

依數值 nudge，L57另掃描真實 block energy。N<=1000有明顯 quiet blocks且 dyadic envelope
整體下降，但 `log B_N/N`靠近0只表示 polynomial/subexponential尺度，並未否證 LB；LB從未
要求 fixed-rate exponential decay。有限掃描也不能排除高 off-line zero的遲發 exponential。
路線存活，下一 producer限於完整兩腿的 reflected cross-prime identity。

## 99. producer驗收補上 positive lower bound 的完整 uniformity

L58把新正 form的門檻定為 LM11.1：coercivity對 block全部 coefficient vectors及 eventual
cutoff tail一致，lower loss僅 `exp(-o(N))`；epsilon,N dependence允許，c dependence與
Y-subsequence不允許。這是 LB9量詞真正需要的正下界，不要求 all N。

LM12隨即測試最自然 local producer。`Lambda(p^j)=logp` exact固定 Euler local vectors，卻不
控制 cross-prime/continuum polarization；per-prime PSD加 Cauchy的常數隨 cutoff發散。故 local
single-channel law不足，下一步只保留 global reflected/telescoping identity。

## 100. reflection語言再收窄：Toeplitz ratio square亦非 CD square

L59以同一 bidegree obstruction證 LB核不是 `h(t-u)`。因此 global reflected identity若只是
translation-invariant ratio autocorrelation，仍不合格。live theorem現在只能精確稱為：對
moving nontranslation-invariant Laguerre CD projector的 centered prime quadrature，取得
LM11-uniform subexponential coercivity。這仍未證，且 exact iff RH endpoint。

## 101. stationary producer family 統一裁決

L60先以 rational factor證 normalized Euler--Bohr mean沒有 LM11 coercivity；L61再將其與
`h(t+u)`、`h(t-u)` no-go統一為 stationary quotienting。此類方法會抹掉有限 meromorphic
perturbation，LB卻對它指數敏感。因此不再測任何 normalized mean或 translation-invariant
kernel候選；更好的 mean constant不改 topology。

## 102. nonstationary Cauchy路線與 W13--W14 exact合流

L62的 anchored residue formula固定全部參數。取 `r_N=1-N^-1/2` 時，boundary Cauchy loss
為 subexponential，contour高度 `asymp sqrtN`、critical-line距離 `asymp N^-1/2`；但所有
off-line residues必須保留。略去它們即 RH，保留則產生 LB fixed exponent。

因此 LB最後的 nonmean producer不是新攻面，而是既有 W13/W14：在移動 contour以前由
centered primes+gamma/boundary構造 sharp positive identity。普通 finite-height zeta bound、
argument mean或 residue-free continuation均已判循環。

## 103. LB--W13/W14 合流的量詞已精確化

L63證 LB good-block、residue-empty、W12 all-test三命題等價，但沒有 direct norm
intertwiner。LB failure由 nearest shell在每個 fixed-length遠端 interval觸發；Weil failure則
由一個 test定位單 orbit。這阻止把較弱-looking block criterion誤當成已由 W12 arch square
控制；除非先完成完整 residue exclusion，兩個算術不等式仍各自未證。

外部 named-gap檢索只找到 reformulations：Bohr covariance paper把 Weil sum表示成
covariance/spectral integrals並把 RH留成 covariance upper；Connes--Consani只完成單
archimedean place，general semilocal prime case仍是預期框架。均未供 W12.4 sharp theorem。

## 104. 停止 residue-equivalent criteria；DN15給獨立 nonlinear theorem

依最新 stop nudge，不再把 `LB<=>residue-empty<=>W12`視為推進；它只作防循環索引。研究切到
DN relative-clock。L64/DN15證 `phi(y)=y-log(1+y)` pair energy的 gradient exact是負 zero
velocity，故 heat zero flow為 convex gradient flow；DN16給 window-size independent Hessian、
gap與 backward bootstrap constants。這是無條件 finite-window theorem，不經 RH residue排除。

checkerboard使 exponent在 kappa趨1時 sharp，故它沒有消去 DN13 的
`exp[-c tau log^2Gamma]` threshold。下一合格進展只接受兩項獨立內容：varying-clock/buffer版本
的 exact relative energy，或 theta-side對此明示 E_d 的超多項式 initial bound。平均 gap統計、
新的等價判準與 finite numerics不算。
## 105. varying-clock quantifier audit：hard cutoff失敗，exact co-moving版本存活

DN18 暴露 frozen reference 的 `S^y` forcing；hard cutoff norm隨 `sqrt(n)/d` 增長。
DN19 又暴露 moving Bregman deformation，affine spacing drift隨 `n|d'/d|` 增長。
故「局部 spacing慢變，所以端點可忽略」在 uniform-in-degree量詞下嚴格失敗。

切換到 surviving target：比較兩個 exact log-gas solutions。Euclidean relative energy有 convex
contraction及相同 sharp backward exponent，但要求 theta zeros 對 exact co-moving reference 的
全粒子 exponential `ell^2` rigidity。下一步先測 Hermite-zero self-similar reference。
## 106. Hermite與Polymath asymptotic壓測

Hermite exact finite flow因 `H_t` infinite exterior field失敗；截 block重現 DN18 buffer norm。
只搜尋已命名 positive-time zero rigidity後，Polymath Theorem 1.5 給 `O(x^(-ct))`。與 DN sharp
backward exponent逐量詞比較：一步少一個 `logx`；多步在 `t=C/logx` 端點喪失 gap-scale
closeness。故停止把 ordinary Riemann--Siegel asymptotic當候選。

DN只剩兩種 grounded continuation：證 `t<=C/logx` 的新 super-polynomial theta rigidity，或找
不受 checkerboard backward exponent支配的 collision-count invariant。現優先後者。
## 107. exact checkerboard closes the smooth collision-count escape

DN23 exact解在 `t=0` collision、`t0` 距 clock僅
`exp[-pi^2t0/d^2]`，嚴格飽和 nonlinear barrier。故不能再期待以另一個 smooth terminal
energy改善 log-squared exponent；那會被此解直接反例。下一類 counter必須記錄 topology/history。
既有唯一具體候選 P30 Pontryagin index又缺 actual spectral-projector limit，所以不重開該舊缺口。
## 108. 非光滑 margin修正與 finite resultant裁決

DN24 將 checkerboard no-go精確化為 `m_d<=omega_d(epsilon_d)`。承重條件是 uniform stability
相對 separation margin，不是 differentiability。fixed-margin Boolean counter必不穩定；同速 shrinking
margin則仍可能，但 arithmetic certificate必比 margin更精確。

DN25 的 discriminant是第一個真正 topological/history counter：finite degree可由單一
`Disc(e^((T-t)D^2)P_T)` 與 Sturm chain完全決定。DN26 隨即以 high-degree monomial證 compact
terminal convergence在 backward heat下失敗，故 naive Taylor-resultant route最小失敗點是 spacetime
graph-norm convergence。下一步只接受 theta-specific weighted norm + canonical resultant limit；否則
不重述 finite equivalence。
## 109. resultant被 boundary degree取代；topological route真正存活

DN27 利用 heat PDE得 universal orientation `-H_xx^2`，所以 rectangle boundary winding無抵消地
計 collision。這比 finite resultant更適合 entire `H_t`，不需 infinite product regularization。

壓測後承重點移到 boundary gap `mu_R`：integer output雖 fixed-margin，輸入 homotopy仍可能
log-squared exponentially ill-conditioned。對 expanding rectangles，公式會退化成 top time與
time 0的 real-zero count差。故下一步不是再證 degree identity，而是找 theta-side explicit boundary
homotopy；bottom phase不得用 unknown zeros化簡。
## 110. boundary homotopy只剩 arithmetic signed phase

DN29 的 two-frequency exact collision及 smooth positive approximation關閉所有 generic positive-kernel
證法。DN30 的 phase current雖給 clean vortex conservation，bottom transform density為
`(1-u)Phi(u)` 且函數為 `2xi-xi'`；sign channel不可避免。

ES165未找到 adjacent theorem：Rodgers--Tao方向為 Lambda lower bound，Polymath只控
`x>=exp(C/t)`，shifted LP只控 fixed degree/high derivatives。故 topological route存活但 arithmetic
obligation已明示為 expanding-rectangle signed phase control；不得再以 topology本身算進展。
## 111. DN27 genericity移除

DN31 的 parabolic blow-up將任意 multiplicity m collision化為 Hermite model
`e^(-sD^2)z^m`，local degree `-floor(m/2)`。所以 boundary degree無 cancellation的結論不依
regular collision假設；transverse perturbation只作等價 bookkeeping。後續不得再以 degenerate
collision作 objection，也不得用 genericity掩蓋真正的 arithmetic boundary gap。
## 112. boundary-winding producer最小失敗點

Arb certificate在 actual Xi zeros證 vertical phase velocity反號，嚴格關閉 monotone-in-t homotopy。
改用 monotone-in-x只得到 first Laguerre inequality；ES166確認一般不充分，all-extended版本與既有
Jensen/de Branges all-degree target相同。

因此 L70/L72保留為新的 exact collision ledger，但沒有降低 arithmetic obligation。spacetime winding
主線最強的兩個可檢驗 producer均已排除；不再以 boundary topology名稱重開 all-degree positivity。

## 113. 三條殘餘實作合流：transfer閉合，arithmetic degree仍未閉合

L74/DN34修正先前過度悲觀的 DN26 裁決。theta terminal Fourier measure下 backward multiplier是
contraction；finite positive rational quadratures對 `(H,H_x)` 在 fixed spacetime rectangles上
`C^1` 收斂，且 boundary margin一旦為正就傳遞 Brouwer degree。故 polynomial resultant不收斂
不等於 entire transfer不可能。

L75/DN35再把 commensurate quadrature寫成 rational Laurent polynomial，exact Sturm/Cauchy-index
可決定每個 finite boundary winding。至此「weighted entire topology」、「finite approximant」、
「nonmonotone homotopy」三者只剩同一承重點：actual theta/prime weights的 expanding degrees為0。

uniform audit：量詞只能是 `R -> mu_R -> cutoff`；反向要求 cutoff只依X會需要新的 margin lower
bound。`t=0` raw margin暗含 simplicity，應以 regular positive slices處理。DN23排除 generic
polynomial precision，DN29排除 generic positivity。

## 114. equivalence audit：共同支柱本身就是 RH

L76/DN36證 regular positive-time exhaustion的 zero-degree assertion iff RH。故 strategy113只消除
三份重複的技術包裝，沒有把 endpoint換成較弱 obligation。DN29、DN32、DN33已分別排除 generic
positive weights、vertical sign及 first horizontal Laguerre sign；目前沒有獨立 producer。

裁決：DN topological route保留 L70/L72/L74/L75作可用工具，但在出現新的 theta-specific signed
identity前封存為 RH-equivalent endpoint。下一順位回到尚未被反例或 equivalence audit關閉的 AP2.5
target-specific one-sided Hardy norming inequality；先判它是否也經有界逆映射直接等價RH，再做任何
估計。Goal保持 active。

## 115. AP2.5切換前即被一般重參數化擊中

L77/AP8/SC17完成 strategy114要求的 equivalence audit。SC8/SC10已有但後續遺忘的反向量詞是：
RH若真，先選 global closure approximant，再把 window T延遲到其 finite K以下任何 fixed power。
因此 AP2.5/SC16.8 iff RH；remote support與無指定速率的 `delta(T)->0`使 polynomial cost不含
effective same-scale資訊。

故不切回 AP2.5，也不再量化 Pechersky stopping constant。真正避開此 no-go須預先把 approximant
綁定T；既有唯一 explicit MB1已在 strategy95回到 same-scale Möbius joint cancellation。下一階段先
做全索引的「reparameterization immunity」篩選，只保留 parameter在 approximant之前固定、且有
獨立可證中介輸出的候選；Goal保持 active。

## 116. reparameterization-immunity 全索引篩選

L78證一般 scheduling lemma：qualitative global approximants若存在，任何 finite complexity都能靠
後選更大的 window T塞進任意 unbounded allowance `g(T)`，local error又不超過 global error。
所以 free-window polynomial/subexponential cost不是中介進展。

套回現有候選：AP2/kappa失敗；LB/W13與DN有自然 scale但已直接 iff RH；MB1因 coefficients由
`X=T^B`預定而免疫，然而 L51已把其唯一剩餘內容定位為同尺度 Möbius-prime-Abel joint cancellation，
三個 producer均失敗。spectral/canonical-system候選尚無獨立定義的 positive domain/operator。

裁決：目前沒有候選同時滿足「免疫重參數化」與「已有未達RH endpoint的可證中介 producer」。這是
嚴格的 project-index結論，不是數學上窮盡所有證法。Goal保持 active；下一個新候選進場前必先通過
L78，再接受反例與 uniform量詞壓測。

## 117. L78 escape audit：rate coupling確有獨立內容

L79以 `ell^2` target `1/n`及前N截斷證 `E_N asymp N^-1/2`。qualitative closure成立，free-window
`N<=T,E_N->0`亦成立，但 `E_N<=T^-1`嚴格不可能。故 L78只是 scheduling filter，不是把所有
定量候選宣告等價 endpoint；prescribed rate/same-scale formula確實能逃逸。

## 118. natural-scale gauge候選裁決

L80/DN37給 `wind(AF)=wind(F)+ind(A)`。任何 nonsingular extending `GL^+(2)` gauge之 index為0，
不能改 collision degree；nonextending straightener把未知 degree原封不動放進 gauge index。
margin同時乘 `sigma_min(A)`，所以 singular gauge不是繞過 conditioning。

L81/DN38又證 first-order shear `(H,H_x+aH)`在每個 simple zero有 invariant vertical velocity
`H_xx/H_x`。DN32 actual Xi反號因此對所有 gamma/log-derivative shear仍成立。裁決：座標型
nonmonotone homotopy producer關閉；只有直接 theta-arithmetic nonvanishing homotopy仍邏輯存活。
Goal保持 active，不把此 producer no-go當作整條路線完成。

## 119. theta-mode homotopy的起始端與直線路徑均嚴格失敗

L82/DN39以 Arb證 first-mode transform有 simple nonreal zero；所以 first-mode saddle與 positive
kernel shape不足以提供 collision-free base。L83/DN40再證加入 T2的 amplitude直線在
`lambda=0.91629...` 穿過 regular collision。這不是 L80 gauge換名，也不是 numerical margin疑慮，
而是自然尺度 kernel path的 actual common zero。

## 120. all-finite theta truncation family結構性關閉

L84/DN41觀察 modular evenness的 cancellation只在 infinite sum完成：每個 finite K_N都有
`K_N'(0)>0` cusp，從而 `H_N(x)~-K_N'(0)/x^2`、real zeros有限。order<=1與 Hadamard再證
total zeros無限，所以 nonreal zeros無限。非實 defects可隨N逃向無窮遠，但不在任何 finite N消失。

裁決：所有「finite theta truncation先LP，再傳到full kernel」路線嚴格排除。存活 construction必須
自起點保留 exact modular completion與 arithmetic shifts；若只沿 mode coefficients繞路，還須先證
避開 codimension-one collision wall，而不能以 winding tracking預設答案。Goal保持 active。

## 121. finite-mode nonmonotone detours由 boundary-jet theorem全部排除

L85/DN42把 strategy120從 unit partial sums升到任意 finite real coefficients。若全部 odd jets在0
消失，negative-u expansion的 Vandermonde moments迫使 coefficient vector為0；否則首個 odd jet
產生 fixed-sign algebraic Fourier tail，配 order<=1 Hadamard即有無限 nonreal zeros。

所以有限 mode span的 nonzero部分完全不交 LP cone。二模 collision wall是否可在 coefficient plane
繞行已不再重要：任何 detour endpoint仍非LP。此 route嚴格排除；下一候選必須是每一步都保留
infinite modular completion的 deformation，而不是 finite truncation後取極限。Goal保持 active。

## 122. infinite modular候選 HS 的首個 topological obligation已裁決

L86/HS12：real-zero collision map `(A,A_x)` 的 local degree為
`-(1/2)partial_a(B_x^2)`，可正可負；explicit harmonic quadratic在兩個 collisions給相反 signs。
所以 horizontal shift沒有 DN27 one-sign ledger。

L87/HS13：analytic map `(A,B)`恢復 `|Xi'|^2` one-sign orientation，但其 degree就是 ordinary
argument-principle zero count，regular strip exhaustion的 zero-degree iff RH。裁決：HS family通過
infinite modular要求，卻在 topological第一關分岔成 cancellation或RH endpoint；沒有新的中介 counter。
HS5只在出現獨立 theta/prime coupled Bezoutian identity時重開。Goal保持 active。

## 123. HS5不再以「待找 identity」占據 active obligation

L88/HS14作 existence-schema audit：在 `K_a>=0` 下，未指定的
`K_(a/2)=T_a[K_a]+L_a`（`T_a`保正、`L_a>=0`）iff target `K_(a/2)>=0`，因反向可取
零算子與 `L_a=K_(a/2)`。所以目前所謂 coupled Bezoutian identity沒有候選公式或可獨立
壓測的判準，確是瓶頸改名。HS5保留為未來 construction的驗收規格，不列目前 strongest route。

下一步回到唯一通過 L78 natural-scale filter 的明示 test form MB1，但先只做 equivalence/rate
audit；若仍只有 RH-scale joint cancellation而無獨立 producer，就記錄後再尋新 construction。
Goal保持 active。

## 124. MB1的 window尺度被消去，但 explicit sequence沒有被消去

L89/AP9把極端參數與量詞算清：只要 `0<B<2m+1`，window tail為 `o(1)`，故 MB1 exact等價
同一 fixed-log Riesz--Mobius family的 global norm沿 `X_j`消失。B不是 arithmetic scale；真正自然
parameter只有 coefficient cutoff X。Burnol lower bound `error^2>=c/logX`又排除 polynomial-rate
強化，不能靠 L79 escape另造較易 lemma。

定向文獻 audit顯示同一 Selberg weight的 pointwise/uniform additive結果早已存在，但 passage到
weighted L2正卡 small-variable Riesz--Mobius scalar；已述 conditional convergence還加了 zero
separation，不能當 RH-alone反向。故 MB1既未成 iff，也沒有新 producer；目前只保留 AP7.2作
精確 regression test，不把 T-window或舊 uniform convergence當進展。Goal保持 active。

## 125. MB1 residue shortcut在 multiplicity極端參數失敗

L90/AP10對 2012 optimal-polynomial theorem作 hidden-dependence audit。其 inverse-`zeta'` moment
一開始就排除 multiple zeros；RH不提供此條件。higher-order residue regularization又需 multiplicity階
derivative constants，沒有 uniform-in-multiplicity closure。因此不以 conditional optimal
`1/logX` asymptotic支援 MB1，也不把 simplicity當無害 genericity。存活 obligation必須
separation-free；目前仍只有 AP7.2 exact joint square。Goal保持 active。

## 126. 回答 producer audit：exact Cesaro座標存在，但沒有 sign mechanism

L91/AP11把 fixed-log mollifier寫成 sharp Abel-corrected residual的 log-Cesaro mean，並給 exact
energy derivative。這是非文獻的結構化簡，但不是 producer：generic scalar step path已否決
scale monotonicity，Jensen又回到更強 sharp estimates。故 AP7.2目前確實沒有獨立候選 identity；
唯一可重開條件是先給 Möbius-specific cross-scale signed correlation theorem，而不能把 double
integral本身列為 lemma。

裁決：MB1 test form封存於此最小失敗點。Goal仍 active；下一棒須設計新的 explicit、自然尺度、
通過 L78且不依賴 zero separation的 construction，不能再從 AP7.2換 norm或拆項。

## 127. Pólya geometric interpolation：低階全過但立即 regular collision

- **候選**：`Phi_s=P^(1-s)Phi^s`，從 `K_(ix)(2pi)` real-zero model連到 Xi，且每個 s保留
  infinite smooth kernel，避開 finite-theta cusp。
- **壓測**：Jensen degree `<=8`、shift `<=40`無反例，但 margins隨 shift降且 worst恰在 cutoff；
  finite test不約束 all-degree tail。
- **嚴格裁決**：Arb/Krawczyk證 `s*=0.0031021250408869274...`,
  `x*=13.165805196244539...` 有唯一 regular double zero，`Hs,Hxx<0`。故 real pair在 s>s*後
  成為 nonreal pair，候選在距起點約0.31%即失敗。
- **後續 filter**：不測同一路徑的 reparameterization；新表示必須先給 independent
  collision-exclusion mechanism，不能只靠 endpoint、positivity或 finite Jensen evidence。

## 128. A0 rank-one boundary表示：collision-exclusion存在，但譜交錯失敗

- **機制**：P3 exponential-wall core為顯式自伴算子；energy-independent rank-one boundary change
  的 spectra由 Sturm theorem逐 gap交錯，確實能先驗排除 complex collision。
- **直接反例**：Arb嚴格證 `beta_3<gamma_4<gamma_5<beta_4`；同一 consecutive core gap含兩個
  Xi zeros，故不可能是 scalar Robin/Weyl level set。
- **量詞裁決**：finite hyperbolic polynomials可逐根搬移，故 collision-exclusion filter非空；但
  target-root path對 Xi循環。下一候選必須是 arithmetic-defined singular/infinite-rank domain或
  independent operator，且 actual spectral projectors先於 determinant continuation存在。

## 129. fixed-rank extreme-height audit：rank two低端存活、全域仍嚴格失敗

- **finite screen**：到 `T=1000`，`N_Xi-N_A0`只取0、1、2；因此用低 zeros排 fixed rank會停在
  rank two，這是明確 quantifier trap。
- **uniform theorem**：Bessel phase與 RvM exact給 discrepancy `S(T)+O(1)`；unconditional
  `S(T)=Omega_+((logT/loglogT)^(1/3))` 型結果使其無界。
- **operator consequence**：fixed-rank resolvent difference的 spectral shift/counting差一致有界。
  故所有 fixed finite rank排除，不只 P38 的 rank one。下一候選若沒有 genuine infinite-rank
  projectors與 domain construction，不列 active operator route。
- **加強**：bounded additive `A_0+V` 由 min--max與 A0 energy gaps趨無窮也只能有 eventual
  discrepancy至多1；所以 additive trace-class/Hilbert--Schmidt全滅。只剩 unbounded、
  resolvent-comparable domain change或 independent operator。

## 130. prime point scatterers：單 channel有 mixed orbits，分 channel有過大 density

- **候選**：`L_p=logp/2` 的 self-adjoint local scatterers讓 first return length等於 Euler `logp`，
  且一份 channel保住 correct arch density。
- **exact failure**：two-point determinant的 `-g_pg_qG_pq^2` 產生 length
  `2|L_p-L_q|`。p=2,q=3即為 `log(3/2)`，短於所有 Euler lengths且 coefficient非零。
- **dichotomy**：同 channel違反 Euler orbit alphabet；separate channels由 P9--P10增加 spectral
  density。下一 operator必須有 arithmetic nonlocal selection rule，不能是 ordinary local potential/
  point interactions。

## 131. prime defect drift：positive projector不能把 `Re=-1/2` 搬到 critical axis

- **exact identity**：weighted interval realization給 `A_p=-I/2+K_p`、`K_p` skew-adjoint；這正實現
  local Euler zero line而非 critical axis。
- **uniformity**：direct sums、reducing subspaces與 compatible positive Hilbert quotients都繼承
  `A+A*=-I`。所以 cutoff、prime degree或 nonlocal orthogonal projector皆無逃生。
- **hidden cost**：加 `I/2`可使 generator conservative，但 determinant變成 `1-p^-x`；保正與保 exact
  Euler weight不可同時。unitary dilation則只保存 resonance determinant。
- **裁決**：prime-only positive projector關閉；只接受明示 singular arch--prime norm/domain的候選。

## 132. opposite-drift pairing：finite positive，infinite cutoff非 locally finite

- **finite viability**：2x2 block有 explicit positive Lyapunov metric，故 P41後的 arch coupling
  requirement不是空集合。
- **uniform failure**：prime frequency lattice spacing `2pi/logp->0`；任 blockwise spectral shift
  都留一個 eigenvalue於 `pi/logp` 內。infinite direct sum遂在0累積。
- **量詞裁決**：`forall finite P exists positive G_P` 不推出存在 infinite determinant-class G；
  缺的是 uniform local spectral finiteness，而不只是 condition number。
- **下一門檻**：cross-prime mixing須消除 accumulation，卻不得產生 P40 mixed Euler lengths。

## 133. positive determinant cumulant dichotomy closes natural nonlocal mixing

- **identity**：self-adjoint cross block在 second cumulant貢獻 Hilbert--Schmidt square。
- **arithmetic separation**：其 length `log(pq)` 對 distinct primes在 Euler log係數為0，且由 unique
  factorization不可能被 same-prime/higher cycles取消。
- **結論**：exact Euler determinant令全部 cross blocks為0，隨即回到 P42 accumulation。
- **scope**：嚴格排除 ordinary trace-class determinant + orthogonal positive prime grading + natural
  semigroup length covariance。任何新候選須明說放棄哪一假設及如何仍得到 actual projectors。

## 134. positive Euler determinant rigidity：nonorthogonal grading也自動對角化

- **coefficient test**：p與 p平方係數迫使 positive A_p滿足 `TrA_p=TrA_p^2=1`，即 rank-one
  projection；pq係數迫使 distinct projections orthogonal。
- **uniform conclusion**：不是只殺某個 mixing ansatz；所有 trace-norm positive Dirichlet
  realizations都 unitary-equivalent於 diagonal prime operator。
- **route impact**：P41 drift、P42 accumulation、P43 mixed-cumulant三者現涵蓋 entire ordinary
  positive determinant class。剩餘 proposal必須離開 positivity或 ordinary determinant class，並補
  spectral-projector loss。

## 135. P21 prime-operator trichotomy：目前 explicit route整體關閉

- positive trace-class：P44 rigidity + P41--P43 no-go。
- signed/super：P22/P25 排除 ordinary closed Hodge/intertwiner。
- regularized：P31--P33 把 hard divisor定位在 scalar counterterms，沒有 projectors。
- **裁決**：不再以「singular cohomology」本身作候選。重開須先提供 positive norm、closed domain、
  induced self-adjoint generator與 determinant=spectrum theorem。下一 strategy必須換表示。

## 136. translation-compensated Hodge：最小分界在兩個 primes

- prime creation配 arch unitary translation可 exact得 `Q^2=0,[H,Q]=0,{Q,Q*}=sum p^-2sigma I`，
  真正離開 P22 ordinary pairing。
- 一個 prime在 `l2(Z)` 有 dense domain、原權重與 compact resolvent，故三驗收條件本身不互斥。
- 兩個 primes時，translation covariance令 eigenvalue orbit含
  `lambda-m logp-n logq`；log ratio irrational使 orbit稠密，locally finite spectrum失敗。
- infinite critical cutoff另有 `sum1/p` divergence，使自然 Q domain不 dense；逐 cutoff normalization
  則消滅 fixed local weights。
- 裁決：global unitary translation route已由 two-prime spectral no-go關閉。若改 partial/nonunitary map，
  必須重新證 positivity、CAR、closability，不能沿用 P45.1。

## 137. executable unilateral repair：不是 domain失敗，而是 exact Euler cancellation

- bosonic backward shifts把 two-sided group改成 one-sided semigroup，成功避開 log-ratio dense orbit。
- exact sparse audit對1--3 primes驗證 `Q^2=[H,Q]=0`、diagonal Hodge Laplacian及預測 kernel。
- 每個補償 ladder的 trace是 fermionic Euler factor的倒數；finite box只給
  `product(1-p^(-(N+1)s))`，極限為1。
- 裁決：任何「一個 prime creation配一條完整 one-sided boson ladder」的 tensor-product repair都
  neutralizes Euler data。下一候選不能靠 additive log-prime ladder（雙向有 P45，單向有 P46）。

## 138. non-operator convex transport：single-atom嚴格失敗，pair cluster嚴格存活

- sufficient certificate：把 pole density分成 disjoint parcels，各 parcel與一個 prime-power atom等
  mass、等 barycenter；Jensen一次給全部 t 的 B46 sign。
- 256-bit Arb/Krawczyk證7、8 single parcels overlap有正下界，故 naive逐 atom allocation嚴格失敗。
- 合併7、8後，Arb證唯一 middle minimum有正下界；outer hinge pieces由單調性非負，pair cluster對
  全部 t嚴格存活。
- 量詞界線：`one cluster works` 不推出 uniform-in-cutoff cluster theorem。完全 unrestricted global
  allocation仍只重述 full convex-order/RH obligation。
- scope界線：hinge transport只屬 B46/DN30 arithmetic producer，不是 entire transfer、finite decision、
  nonmonotone homotopy三路共有機制；三路共同 obligation仍是 expanding arithmetic zero-degree。
- P46 scope同步收窄：Euler cancellation是 complete one-sided ladder theorem，不是 `[H,Q]=0` theorem。
