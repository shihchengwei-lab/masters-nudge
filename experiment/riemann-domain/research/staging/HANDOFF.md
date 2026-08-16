# Riemann research handoff — updated 2026-08-14 (Asia/Taipei)

## 執行狀態

- 目前 Codex Goal 已重新建立並持續執行。
- 目標：禁止主模型搜尋網路；持續嘗試證明黎曼猜想，記錄推導、候選引理、反例、數值實驗與未閉合缺口；不得把數值證據當證明。

> 2026-08-15 使用者已解除聯網禁令；目前允許搜尋及下載 primary mathematical
> sources。其餘 proof standards不變，數值證據仍不得當作 RH 證明。

## 當前主線

研究目前集中在 Xi 核偶矩與 Jensen 階層。degree 2 已由 J4、J6、J7 與區間證書完成；degree 3 被歸約到 J11/J12 的相鄰協方差遞推。

目前實際主線已在後續稽核中轉為 K0 continuum positivity；本段保留為歷史起點。

最新進度：

- J14：高 theta 項相對第一 theta 項為超多項式小。
- J15：第一 theta 項具有唯一 saddle，且位置、曲率及低階導數已有顯式界。
- J17：J12 改寫為 log-u 方差與第三累積量的顯式 corridor。
- J19：切除 `u<10^-2` 左尾；質量與前三個 log moments 有封閉上界。
- J20–J23：mode、曲率、參數導數、高階導數 majorant 與主區域曲率單調性已建立。
- J24：選定 `w_t=log(t)/sqrt(Λ_t)`，證左右尾超多項式小，任意固定階 Laplace 展開可局部化。

## 下一個可稽核工作

1. 在 J24 window 內，把六階 Gaussian normalization、mean、variance 交叉項全部展開。
2. 將 J21.3 的 remainder enclosure 成 `O(t^-3 polylog t)`，並控制相鄰 t 差分。
3. 從粗常數算出顯式起始門檻 `T`。
4. 對 `k<T` 建立有向區間證書，與大 k 定理接合。

## 2026-08-14 最新接續點

- J25--J43 已完成原先六階 enclosure，並逐次擴充到 weight-7／Bell-8／M10。
- `experiments/verify_j43_weight7_blocks.py` 的 272 個 directed blocks 嚴格覆蓋 `1858<=t<=2600`；與既有後段證書接合後，`kappa_3<0`、`t^2|kappa_3|<1/20`、`t Var<79/1000` 對所有 `t>=1858` 成立。
- `experiments/verify_j32_tail_transfer.py` 已在新端點以 Fraction 重驗 theta tail，因此完整 Xi 的 degree-3 J12 對所有 `k>=1859` 成立。
- degree-3 尚缺有限段 `1<=k<=1858`；下一個 saddle 工作是 weight-9／Bell-10／M12，或改建直接 moment interval certificate。
- 即使 degree 3 全部完成，也不能推出 RH；degree 4 以上仍缺統一證明或逐階證書。

其後 J44/J45 已再推進：exact weight-9 algebra、Bell-10/M12 與直接 `F''` interval 的 84 blocks 覆蓋 `937<=t<=1858`。更新 theta-tail 後完整 Xi 的 J12 現對 `k>=938` 成立；degree-3 剩 `1<=k<=937`。最低 block error ratio 0.995057，下一步應優先改作直接 rigorous moment interval certificate，而非假定繼續加階必有收益。

最新 J46--J51 已推至 weight-15/Bell-16/M18；完整接點現為 `k>=727`，degree-3 剩 `1<=k<=726`。門檻收益從 137 降到 56、18，而 monomials 增至 176，故目前 absolute-Bell 加階路徑停止。J52 已在 `xi_jensen_route.md` 指定直接 moment 的 chord/tangent directed quadrature 與 theta-tail 介面；下一步是實作並把每個 `M_k` 相對寬度壓到 `10^-7` 以下，再核對有限 J12。

J53 已完成上述實作並嚴格驗證完整 Xi 的 `50<=k<=400`；最小 J12 interval margin仍 `>2.9422e-6`。目前 degree-3 只缺 `1<=k<=49` 與 `401<=k<=726`。後段續跑 `experiments/verify_j53_direct_moment_chunks.py --start ... --stop ...`；低段不能依賴 J14 粗 tail，需實作逐 theta 項與 n-tail Gaussian-sum enclosure。

J55 已修正 J53 的 1-ulp cell-width 缺口並完成全部必要重驗；J54 覆蓋 `1<=k<=34`，J53 覆蓋 `35<=k<=726`，J51 覆蓋 `k>=727`。因此所有 shifted degree-3 Jensen polynomials已嚴格證明 hyperbolic。這只是獨立 cubic 成果，不是 RH。

依策略稽核，停止 moment 擴張與逐 degree finite certificate。J56 的 exact 序列 `(25,78,143,76,29)` 已否證一般 cubic→quartic 升階。新主線只研究 uniform all-degree 結構：`J_(d+1,n)=J_(d,n)+XJ_(d,n+1)` 的 common interlacing、全部 Jensen Hermite/Bezoutian 的 uniform Gram representation，或正確 coefficient-array PF∞。raw moment Hankel positivity、kernel log-concavity與 translation TP2 均不足。

全階策略已獨立整理於 `all_degree_route.md`。下一步從 A2.1 的 minimal compatibility cone／Wronskian closure 開始；不得回到逐 degree finite 掃描。

A9--A11/J57 新增一個真正 uniform 的目標：對 `G=sum gamma_k w^k/k!` 證 `h=G'/G` 在整個上半平面 anti-Pick，即 `Im h<=0`。這會由 log-derivative 極點的局部形狀一次排除全部非實零點；等價方向是 `c_k=gamma_k/k!` 的無限 Toeplitz PF∞。尚缺由 Xi 證逐點雙積分 `Im[G'(z)conj G(z)]<=0`。正 mixture 不封閉該符號，且 exact J56 序列雖通過 h 在 0 的前六個交替導數符號，仍 quartic 失敗；m=6 首次失敗由 `experiments/verify_finite_logderivative_not_uniform.py` 精確重驗。不得把更多有限導數／minor batches 當作進展。

A12 將同一 uniform 目標改寫為 Stieltjes--Hankel 結構：`b_m=(-1)^m h^(m)(0)/m!` 的 Hankel及 shifted Hankel matrices須對所有尺寸 PSD，再加解析 growth bound即可反推 anti-Pick。J56 反例的首兩個 2-by-2 determinants 已是 exact 負值，故 cubic 僅是 induction base，沒有這個全尺寸 Gram invariant。下一步只能找 Xi-specific、all-r 的 Gram/compound-kernel identity；禁止逐一核有限 minors。

J58/A13 已再排除「J12 比 cubic 結論強，或許可升階」：存在明確無限正序列 `C_1=61/1000,C_2=49/1000,C_k=6/125 (k>=3)`，經 ratio recursion 建出的 gamma 對每個 k 都滿足完整 J12.2，但 `J_(4,0)` exact discriminant為負。`verify_degree3_not_degree4.py` 已擴充重驗。因此 J12、variance/third-cumulant corridor以及全部 moment 證書都正式歸檔為 cubic-only；不得再把它們當 uniform seed。

J59/A14 再證 A12 最低 Stieltjes--Hankel determinant不由正 mixing自動保號：`(3/4)δ_0+(1/4)δ_1` 給 exact `-13/92160`。所以目前唯一尚未封閉的 determinant 方向，是找到真正 Xi-specific 且 all-r 的 theta/score integration-by-parts Gram；若只能核有限 minors或只用 raw moment PSD，應立即判為不合格。

J60/A15 將三種等價表述合併成單一 S-fraction obligation。J12 確實推出前兩個 pivots `a_1,a_2>0`，這是 degree 3 唯一真正可保留的 Gram seed；但另一條全域 J12 exact chain使 `a_3<0`，故沒有 pivot recursion。

J61/A16 又以 exact Sturm chain排除更強猜想：`C_k=1/[4(k+2)]` 是 Hausdorff completely-monotone sequence且全域滿足 J12，但 `J_(10,0)` 只有 6 個實根。驗證器為 `experiments/verify_complete_monotone_j12_not_uniform.py`。

J62/A17 完成 Pascal recurrence稽核：full family compatibility在 adjacent-sum map下可封閉，卻連 d=0 都無 base；只控制迭代所需 binomial sums則等同 higher Jensen目標，屬循環。下一個合格進展必須是 Xi-specific、可初始化且對 adjacent sums封閉的新 cone，或 all-r Gram factorization；等價改寫本身不算新攻面。

J63/A18 將 theta side 精確拆成 `Phi(u)=int T_1(u+a)dmu(a)`、`mu=sum n^-1/2 delta_(log n)`，而 mu 的 Laplace transform正是 `zeta(s+1/2)`。所以 T1 saddle只處理 envelope；all-r positivity的算術責任仍完整藏在 log-n shifts中。J14 高 moment-index 的 tail smallness不得當成 fixed-shift/all-degree small perturbation。

J64/A19 給更強 exact 斷層：一個 `[0,1]` 上的 compact positive measure（兩個指定 Beta variables之乘積）經 Xi 同樣的 `gamma_k=k!M_k/(2k)!` normalization後，對所有 k 滿足完整 J12，首個 quartic discriminant卻為負。`experiments/verify_beta_moment_j12_not_uniform.py` 以 coefficient-positive rational polynomials證 global J12，再以 Bareiss證負判別式。故 positive raw moments + all-shift cubic corridor也不能升階。

Jensen 一般結構稽核後，Li arithmetic 成為目前較獨立的下一介面。D9/D10 已把 Abel pole與 prime sum合法合成 `Q=x-psi(x)` 的單一 integral，並修正 boundary為 `-n`：`E_n=-n+Abel int Q(e^t)e^-t L_(n-1)^2(t)dt`。`F(s)=int Q(e^t)e^-stdt=[1+h(s)]/s` 證 delta remainder消失；generating function精確回復原 binomial transform。最小缺口是此 oscillatory integral負部的任意底數次指數界；PNT error乘 kernel絕對值太粗。

D10 與既有 `chebyshev_laguerre_kernel.md` C1 是同一公式；新增內容只算 Abel 合法化、`-n` boundary修正及 generating-function audit。C2 已證 pure power response在 exponent `theta=1/2` 精確轉折，故這條 Li/Chebyshev interface仍承擔 RH 等價臨界資訊，不能列成新的獨立捷徑。

新增 `strategy_audit.md`，把 Jensen/PF∞/theta、Li/Chebyshev、Nyman與 mean-square 各路的 uniform輸出、已排除捷徑及最小未閉合 inequality集中列出。後續只有 all-r Xi arithmetic identity、可封閉新 cone、signed Laguerre單側界、uniform mollifier或全尺度 prime correlation才算新進展；有限證書與等價換名不算。

C4 最後證實 weighted Chebyshev energy可經 Laguerre orthogonality控制全部 E_n，但可用的 `p>5` energy criterion已與 RH 等價；這不是較弱入口。`strategy_audit.md` 第 6 節已完成使用者指定的終止稽核：RH 未證，但 J24 技術線、1-ulp 重驗、degree-3獨立成果、升階反例及 Jensen/theta/Li/Nyman/mean-square目前所有可行路徑均已明確記錄到其最小 RH-equivalent缺口，且沒有剩餘具體非循環候選。只有出現新結構時才應重開。

上述「目前所有可行路徑」宣告已在重新稽核後限縮：它只涵蓋當時列出的
路線，不能代表數學上真正窮盡。研究現已重開。新增
`spectral_toy_route.md`：功能域型 toy `P_q(T)=1+qT²` 可由區間上的正自伴
Neumann--Dirichlet Laplacian精確表示成
`G_q(w)=det(I+wA^(-1))`，resolvent trace一次給 anti-Pick 與 all-size Gram。
這證明自伴譜行列式是先前漏列的 uniform-in-degree 機制。對 Riemann Xi
的下一最小缺口是從 theta/primes 獨立構造 A 並證 determinant identity；
若依未知零點反造 A 則循環。不得以此 toy 成功宣稱 RH 已證。

譜路線已再具體化於 `spectral_archimedean_route.md`。regular有限區間二階
算子因譜密度不足被排除；半線 exponential-wall
`A_0=-4d²/dx²+16pi²e^(2x)` 的 Bessel determinant精確吸收 Xi 的
archimedean增長，剩餘 relative factor在正軸僅為 `Cw^(9/8)`。下一個接續
點是把 Euler series中的 prime lengths `m log p` 建成 A_0 的全域自伴
perturbation／unitary coupling，並由 resolvent trace identity合法延拓到
central region。任意 A 的存在、未知零點 diagonalization、逐 prime直和
或非自伴 transfer determinant均不算證明。

新增 exact theta--Morse bridge：`phi_n=T_n/(2e^(u/2))` 是 shifted positive
Morse operator
`H_n=-d²+4pi²n^4e^(4u)-20pi n²e^(2u)+4` 的 zero ground state；一般
decaying resolvent solution為
`z^-1/2W_(5/2,sqrt(1+w/4))(z)`。這使 theta summands成為真正自伴
channels。下一步優先計算這些 channels 的 Weyl `m_n(w)`，測試是否存在
由 theta weights強制的 self-adjoint star coupling，其 Weyl sum在
`sqrt(w)>1/2` 精確等於 Xi/prime relative log derivative。尚未匹配前，
這只是具體候選，不是 RH 證明。

上述 naive star coupling 已由 P9 的解析 density audit否證：有限 N 個
channels多出 N 倍 archimedean Weyl主項，全 n direct sum則增長為
`Theta(lambda^(3/4))`；固定 Weyl sum的 algebraic大參數展開也不匹配 Euler
的 `2^-x/x` tail。P7 Morse identity仍保留，但只能作單一 A_0 的
trace-class relative／boundary資料。下一步不得再直接組裝 channel spectra；
必須找一個保持單份 phase volume的 global perturbation identity。

P10 另依 nudge 完成 infinite `sum m_n` 稽核：large-n有
`m_n=-2pi n²+4+O_K(n^-2)`，故和可合法收斂／減常數正則化；然而所有
Dirichlet pole residues同號，正權 star coupling無法 cancellation，coupled
zeros仍繼承 `Theta(lambda^(3/4))` density。故 countable star不是尚待補
收斂的小缺口，而是已解析封閉。主線回到單一 A_0 的 prime-relative
trace-class perturbation。

prime operator的 type亦已釐清：`H_P=diag(log p)` 正自伴且在 `Re s>1`
精確有 `zeta(s)=det(I-e^(-sH_P))^-1`；`p^-1/2` 也能由 open quantum graph
的 unitary dilation產生。但這是 semigroup／resonance determinant，不是
compact resolvent spectrum。關閉 leakage會引入 Euler log沒有的 mixed
orbits。下一個合格突破須給全域 orbit-recombination identity，把這些額外
路徑與 A_0/gamma/functional-equation terms精確合併。

全域 scattering 稽核現有更精確結論：模曲面 Eisenstein coefficient已是
`varphi(s)=Lambda(2s-1)/Lambda(2s)`，所以 gamma+zeta 的 self-adjoint global
recombination確實存在，但 zeros成為 resonances。RH等價於非平凡 poles
`rho/2` 全在 `Re s=1/4`。physical-line unitarity、reflection與正 time-delay
均被任意位置 Blaschke factor證明不足。下一接續點改為：能否由 Hecke/
modular arithmetic給 resonance generator一個正 metric，嚴格證
`Z=I/4+iT`、T self-adjoint；不得由未知 zeros反造。

依最新 nudge，P12/MS7 已補 distribution trace中間層：prime contribution
的 inverse Laplace kernel為
`-(2sqrt(pi t))^-1 sum Lambda(n)n^-1/2 exp[-(log n)^2/(4t)]`。這排除
sign-definite trace-class additive `A_0+V`，但 modular scattering的 signed
spectral shift仍可重現它。所以下一步不是再找 explicit formula，而是證
signed resonance distribution可提升為 `Re Z=1/4` 的正離散譜；這正是
目前未閉合的 positivity/normality theorem。

MS8 已把該 theorem縮成 two-sided contraction：在同一 positive resonance
norm上若 `exp[t(Z-I/4)]` 及 inverse皆 contraction，則 elementary norm夾逼
加 Stone theorem給 `Z=I/4+iT`，直接推出 RH。下一步只接受由 modular
domain／Hecke symmetry獨立構造這個 common incoming/outgoing norm；不同
norm、indefinite pairing或由 zeros反造均不算。

MS9 已否證由 Hecke self-adjointness直接造此 norm：`T_p` eigenvalue
`p^(s-1/2)+p^(1/2-s)` 在 target resonance line `Re s=1/4` 仍一般複數，
所以 resonant states不能位於保持 T_p self-adjoint的正 completion。Hecke
最多提供 paired/biorthogonal結構；下一步須查 modular boundary/energy
form，而非樸素 Hecke norm。

MS10--MS12 已完成 common-norm audit：cusp exponential weights只給半平面
integrability，generic Hardy/de Branges model space對任意 Blaschke zeros
皆正。真正的 global common norm就是 Weil explicit-formula form；其對全部
convolution squares非負與 RH等價。下一步若續此線，只接受 prime+gamma
side的 all-test-function square/Gram factorization，不能只把 Weil criterion
或 model-space positivity換名。

新增 `weil_square_route.md`：unitary Frobenius toy 的 all-test square已精確
寫出；prime diagonal contraction `p^-1/2` 又因 spectrum不在 unit circle，
不能靠換正 norm直接 unitarize。當前最小正向目標是從 prime+gamma構造
線性 `g->V_g` 並證 exact `Weil(g*g*)=||V_g||²`。任何由 zeros反造、只給
unitary dilation matrix coefficients、或留下額外 channels的方案均不合格。

MS13 另證 common pairing positivity本身已承擔 RH：off-line reflection
orbit的 Hermitian block為 `[[0,r],[conj r,0]]`，必不定。故後續不得把
incoming/outgoing pairing「假設為正」再套 MS8；必須先由 prime+gamma
給 W4.1 的 squares。

W5--W7 又把 G20 具體化。第 p 個 prime correlation是 Poisson resolvent
`D_p` 的 `||D_pg||²-||g||²`，但其 multiplier跨過 1，故 local dilation
沒有正 defect；Gaussian解析族亦證 gamma/pole block可負。真正保留下來的
新結構是：對支撐長度 A 的任意 g，prime side精確為非負
`E_A=sum_(n<=e^A)Lambda(n)n^-1/2||g-T_(log n)g||²`
減 `2S_A||g||²`。下一步只做 uniform-support coercivity W7.5 或其更強的
adelic common-isometry/projection定理；它若成功一次處理所有 tests，不是
逐 degree 證書。不得只把 W7.5 重命名為 Weil criterion。

W8 又完成一項實質 square completion：從 pole kernel轉移四個 exponential
kernels給 gamma，digamma recurrence使所得 `B_4` multiplier為
`Re psi(17/4+it/2)-log pi>=c_4>0`。於是 exact
`Q_W=B_4-2R_4`，R4只剩 von Mangoldt離散 measure與 continuum kernel
`w_4=e^(a/2)-e^(-5a/2)-e^(-9a/2)-e^(-13a/2)` 的相關差；更正：w4只在
`a>=log2` 正，`0<a<log2` 仍是 signed endpoint layer。最小缺口改為
對所有 compact-support g證 `2R_4<=B_4`。這仍是 RH-scale，不可宣稱已證；
但 archimedean base的符號問題已關閉，下一步應攻算術 discrepancy的
uniform Gram／large-sieve／adelic projection，而非回去刷有限證書。

W9 新增 Selberg all-k hierarchy：`Lambda_k=mu*log^k>=0`，且
`Lambda_k log+Lambda*Lambda_k=Lambda_(k+1)`。它是具體 uniform升階機制，
但 convolution對 autocorrelation產生 `C_g(a+b)` cross pairing，Hilbert
square則產生 `C_g(a-b)`；故仍缺不增加 mixed orbits的 doubled/Fock block
positivity。這條尚未窮盡，應優先於任何 finite-degree certificate。

W10/W11 已完成該優先 audit。裸 `Lambda_k(p^m)` 的 2-by-2 Hankel determinant
為負；正確 all-size結構是
`j!Lambda_(omega(n)+j)(n)/(omega(n)+j)!` 的 exact box-moment Gram，prime
powers對應 logarithmic cells。可是這仍只在 `a+b` 半群 convolution內。
單原子 `delta_L` 已給嚴格反例：全部 convolution hierarchy正，對稱化後
Fourier transform `2cos(tL)` 卻非正。故不再單純升 k；下一步必須找
theta/Tate/adelic reflection theorem，把 box/cell bulk轉成 `a-b` group
Gram，並證 contour shift沒有 off-line residues或 mixed orbits。這正是
G20 的跨代數缺口。

W12 已把 B4 本身完全平方化：
`B_4=c_4||g||²+int q_4(a)||g-T_ag||²da`，
`q_4=e^(-17a/2)/(1-e^(-2a))`。下一個最小命題就是 W12.4 的
operator large-sieve；R4含任意長 `log n` shifts，而 RHS只有局部
logarithmic Sobolev energy。故後續應尋找 theta/Tate reflection或真正的
prime cross-scale消去，不再花力氣於 archimedean正性或 Selberg升 k。

另有未窮盡的獨立 heat-flow路線，見 `debruijn_newman_route.md`。real zeros
滿足 `(d_j²)'=4kappa_j`；clock lattice精確有 kappa=0，所以不得用 uniform
absolute gap。最小充分目標是由 theta saddle證全部 zero indices的 DN3.2
integrated clock-defect barrier，或一個 backward-invariant clock cone。
quadratic heat toy證一般 PDE/symmetry不足；低零點 interval checks只能在
高指標 uniform theorem完成後補 base，不能代替它。

W13/W14 已完成 W12 防循環與強度 audit。regular critical-line multiplier
其實由 functional equation逐點相等；非零 Weil measure全在 boundary
deltas與 contour residues，且 Chebyshev表示直接接回 M1。另一方面，任一
off-line quartet都可用 polynomial interpolation乘 Gaussian隔離其負 pairing
block，故 all-test W12.4逐點推出完整 RH而非 density theorem。新估計若只
覆蓋固定 support/bandwidth或平均 tests，不得算完成；真正缺口仍是 contour
shift前的 Euler-side all-test reflection positivity。

W15 已封閉 natural Abel shortcut：canonical family
`b_4-2ReF_4(epsilon+it)` 在 `epsilon=4,t=0` 有 exact
`<-229/61880`，只需 prime 2。故不能從 Euler絕對收斂區建立正 forms再保正
取極限；若續 Weil主線，必須是非 scalar-damping 的 adelic/reflection
construction。

DN6 把 heat-flow缺口量化：若前後 M 個 gaps均不超過目標 gap的
`1+epsilon` 倍，則 `kappa_j^+<=4epsilon+2/(M+1)`。高處需
`M>>log²gamma`、`epsilon<<1/log²gamma` 且全下降時間一致；平均 spacing
不夠。後續 theta saddle候選須按此門檻稽核。

DN7 依 nudge要求 M、epsilon、起始 gap下界按 dyadic height block共同選定，
同時覆蓋每個 gap與全時間；per-gap adaptive或 density-one結果不合格。

新增 `tate_reflection_route.md`：natural theta-sum E有 exact Poisson
reflection及 critical-line multiplier `2zeta(1/2+it)`，但 ordinary positive
L2中 E kernel為 0、range dense，離散 zeros/cokernel不可見。exponential
analytic rigging可見 off-line modes卻重現 MS13 indefinite pairing。故下一
非循環輸出若存在，必須是 TR5 的額外 arithmetic projection/commutator
positive defect，不是 Poisson unitarity或 range quotient。

TR6 已算 standard log-halfline projection：commutator平方只等於 universal
`int|a||g(a)|²`；E range projection則是 I。故不得再以 Hardy cutoff或 E
graph/range projection作候選。尚未排除的只剩真正新的 adelic arithmetic
projection及其合法 semifinite trace formula。

TR7 已有 prime-local Toeplitz projection：rank-m defect配 `1/m` exact給
von Mangoldt prime-power weight，故 W7 positive difference energy不再缺
arithmetic square。TR8 顯示 product formula只取消 signed real/p-adic
boundary indices；positive norm中 infinite strips同號相加，finite corner
又只重現同一 prime weight。最小缺口因此是把 signed adelic index提升成
positive cohomology/Schur complement並吸收 diagonal debt，不能用 supertrace
冒充 norm。

TR9/TR10 已證 signed index取 cohomology後仍只是偶減奇；perfect duality不
排除 MS13不定 block。local prime defect有 finite-dimensional sl2/reversal
polarization，但 tensor globalization產生 Lambda不含的 mixed-prime sectors。
下一合格 theorem須先令 mixed sectors exact/acyclic，再在剩餘 cohomology
造與 scaling相容的 positive Hodge star；這會直接推出 target line。不得用
Schur complement換名，因其 cross-norm前提就是 W12.4。

TR11 修正：mixed-prime sectors其實可由 bosonic Fock的 positive
one-particle projection移除，log derivative正是 prime occupation trace。
因此剩餘重點不是 acyclic cancellation，而是 critical prime trace與 gamma
oscillator的 positive operator relative trace。

TR12 證 atomic/continuous length spectra不能 exact isometrically intertwine；
必須用 wave packets。TR13 又證正的 atom-to-cell transport displacement
density約 `delta^-3/2`，超過 W12 `q4~delta^-1` budget。下一候選必須是
跨 primes的 global oscillatory frame，普通 PNT/quantile coupling不合格。

TR14 把 surviving候選寫成 prime-torus Kronecker restriction：W7 distance的
Haar長時平均exact 是 `2S_A`，故平均正交只給 density。TR15 依 nudge算出
普通 Bessel雖把 TR13 power從3/2降至1，仍留下
`sqrt(log(1/delta))` loss並帶回 diagonal debt。下一步若續此線，必須證
uniform-in-A 的 entropy/large-sieve improvement，額外省半個 log且覆蓋
W14 orbit-localizing tests。

不得直接假設 `F'''<0` 推出整體 `κ_3<0`；J23 已明記仍缺積分比較引理。不得以有限數值掃描代替 J12 的無限序列證明。

## 其他已封閉路線

- Chebyshev 均方／dyadic 路線：M9 證短尺度理想方差仍不足，缺口在長尺度與跨尺度算術結構。
- Nyman–Beurling 路線：NB11 顯示本質仍是 ζ mollifier 均方；NB12 排除 Gram 對角占優與全正矩陣捷徑。
- Xi 核一般 log-concavity／TP₂ 不足以推出 Fourier 全實零點。

## Nudge 狀態

- Workspace profile：`frame / Riemann`，Opus 4.6，review mode `all`。
- Router 已因解析估計證據自動切換到 Selberg。
- 舊版 hook 有兩個交付缺陷：Windows CP950 可使 checkpoint JSON 輸出失敗；detached Stop reaction 只進 log/TK，未送入 Goal。重啟前必須先安裝修正版外掛。

## TR18 最新策略修正

raw first-return候選已嚴格封閉。由 PNT partial summation，固定 `t` 有
`F_X(t)=X^(1/2+it)/(1/2+it)+o(sqrtX)`；取 `t=1` 並沿 cutoff相位對齊的
`X`，固定時間就出現 `asymp sqrtX` peak，直接否證 TR16.5/TR17.4。
smooth cutoff亦保留 Mellin主項。後續若續 prime-frame，只能先減去
archimedean continuum並控制 `int x^(-1/2+it)d(psi-x)`；這回到 W12
centered discrepancy，而非 Haar entropy或首次回返問題。

## DN8 與當前未窮盡判定

新增有限 zero heat flow的 exact square law：若
`Delta=product_(j<k)(x_j-x_k)^2`、`S_j=sum_(k!=j)(x_j-x_k)^-1`，則
`(logDelta)'=4sum_j S_j^2`。backward首次碰撞必使此 action發散。因此 DN7
的 all-gap近鐘格不是唯一候選；可改尋 dyadic block的 clock-renormalized
discriminant、boundary flux與 theta-side uniform finite-action bound。

目前不能誠實宣稱所有可行證法已窮盡。尚存四類 uniform機制：centered
Weil/Tate all-test square、Xi-specific all-r Pick/Gram、單一 arch core的
singular/sign-indefinite global coupling、以及 DN8 global action。它們皆有
清楚缺口且沒有完整證明；goal保持 active。

DN9 已補 infinite-block audit：`(logDelta_I)'=4sum S_j^I S_j`，外部 zeros的
flux不可丟；clock lattice中它恰取消 internal square。後續應直接尋找 full
PV velocity action `(1/4)sum int|x_j'|^2` 的 theta-side uniform bound。
pair collision會令此 action對數發散，因此該 bound若成立確可阻止碰撞。

DN10 已完成下一層稽核：finite action等式只是 log-discriminant lower bound；
`f_d=(x²-d²)e^-x²` 又證固定階 Plancherel/Sobolev能量無法控制 root velocity。
因此沒有 zero-sensitive theta frame前，DN線暫停；下一棒轉回 centered W12
finite-cutoff，不得把 generic heat energy當 collision proof。

最新 nudge詢問 DN9.1 cross term是逐點還是平均控制。DN11 的答案：raw同尺度
block兩者皆不小，clock lattice中 cross term精確取消 internal square。
只有 core--buffer遠尾能逐點控制；由 symmetry與 zero counting，
`|R|<=C Gamma logL/L`，取 `L=Gamma²` 後 core L2 tail趨零。尚缺 buffer
transition layer的 tapered/renormalized flux，不能宣稱截塊極限已完成。

W16 已接續 centered Weil：對 `epsilon(a)=e^-a/2(e^a-psi(e^a))`，prime-minus-
continuum measure exact 為 `-depsilon-epsilon da/2`，故 finite-support C 的
form是 `C(0)+int epsilon(C'-C/2)` 加三個 decaying endpoint kernels。這在
contour shift前成立並消除 TR18 raw endpoint peak。下一缺口是利用 C 的
autocorrelation/positive-definite結構作 uniform log-Dirichlet bound；不得用
隨 A增長的 absolute PNT bound。

W17 指出 target沒有 coercive margin：normalized modulated boxes使
`C_A(a)->cos(ta)` 且 `B4->b4(t)`；prime側的 corresponding limit正是 W13
boundary/residue問題。故任何 fixed-loss／sqrt-log-loss large sieve都不可能
完成 W12。下一個合格候選必須給 sharp constant 1 的 exact reflection或
relative-trace identity。

W18/A20 已把 Weil、all-degree Pick與 spectral三線 exact合併：
`F4=A4/2-xi'/xi` 且 `h=G'/G=[A4/2-F4]/(2sqrtw)`。所以真正只剩一個
factorization obligation：不使用未知 zeros，從 W16 centered primes或 theta
構造 h 的 positive Stieltjes measure／resolvent trace。

P13 已把此 obligation寫成 explicit heat trace：Theta(t)由 pole `e^(t/4)`、
digamma integral及負的 von Mangoldt log-Gaussian sum組成，且
`h(w)=Laplace[Theta](w)`。RH iff Theta completely monotone（在既有 growth
條件下）；成功標準是一次給 all-k positive measure/semigroup factorization，
不得逐 k 刷符號。

P14 已排除弱化：Theta單純非負或任意固定 K 階 alternating derivatives均不
足；小 damped oscillatory pair是 exact反例。只接受 all-k theorem或 single
positive-measure identity。

P15：h 的 cut boundary measure其實已由 critical zeros自動給正 atoms；
off-line zeros是 cut外 poles，boundary positivity看不見。故 P13下一步必須
是 arithmetic resolvent identity並先驗證 cut-plane analyticity，不能只做
time-delay／boundary density正性。

P16：下一個正確輸出是 `K_tau(s,t)=Theta(2tau+s+t)` 的 compatible Gram，且
time shifts為 symmetric contractions；這一次給 Stieltjes measure。P17 依
nudge比較 k→∞：zero target約
`Gamma(k+1/2)t^(-k-1/2)logk/(8pi)`，而 fixed prime Laguerre derivative已
有同 factorial base。故 construction必須逐 k zero-loss；任何 `C^k`／absolute
Laguerre loss立即失敗。

P18：`h_A=A4(sqrtw)/(4sqrtw)` 已有 exact positive Stieltjes measure
`b4(r)dr/(2pi)`。然而 `h_F=F4/(2sqrtw)` 的 regular cut density與它完全相同，
故 h 的 continuum精確取消，只剩 zero atoms／off-cut poles。下一步應從此
free channel尋找 self-adjoint boundary extension或 unitary scattering spectral
flow；simple measure domination已排除。

P19：普通 boundary extension仍失敗。h_A 是全域 a.c. measure，RH target h
是純 zero atoms；unitary、finite-rank及 trace-class self-adjoint perturbations
保留 a.c. spectral type。只剩 singular/non-trace-class domain change、正的
arithmetic cohomology quotient或獨立 operator，且仍須符合 P17/P18 sharpness。

P20 已封閉 generic Hardy/Clark quotient：任意 off-axis Blaschke factor也有
positive quotient與 real discrete Clark measures。下一個 quotient若存在，
必須另有 arithmetic Hodge polarization迫使 scaling generator self-adjoint；
普通 model-space positivity不算。

P21 新 exact介面：`G/G0=D_A/D_F`，其中
`D_A=pi^-x/2Gamma(17/4+x/2)/Gamma(17/4)`，
`D_F=C(s+2)(s+4)(s+6)/[(s-1)zeta(s)]`，且 Euler區
`1/zeta(s)=det(I-e^-sH_P)`。下一步若攻 Hodge，必須把此 semigroup defect的
leakage與 P18 continuum exact配對，cohomology generator須正自伴且不得新增
mixed orbits。

P22：prime Fredholm determinant的 exterior-Fock supertrace雖 exact，但每個
squarefree energy `log n` 由 unique factorization只有一個 parity state；任何
commuting odd differential必為 0。用 arch continuum配對又有 atomic/
nonatomic no-go。故只剩 singular/rigged Hodge differential，且其 positive
polarization仍須獨立證明。

P23 回應最新 nudge：`M_k^-1/(2k)~sqrt(et/k)`，Carleman sum發散，故 moment
measure若存在是 determinate；「factorial違反 Carleman」不適用。P18的無條件
結論則嚴格限定為 regular cut boundary density equality，證明來自 critical
line上 `xi'/xi` 純虛；完整 measure cancellation仍需先排除 off-cut poles。

P24：`D_F(-x)/D_F(x)=D_A(-x)/D_A(x)`，右側是純 gamma ratio。G 的所有
nontrivial zeros因 evenness在 scattering ratio中取消；所以 boundary phase、
unitarity、time delay皆不能證 RH。singular route必須保留 absolute D_F pole
divisor並證其位於 imaginary x-axis。

P25：boundedness不是 P22唯一障礙。任何 closed strong-intertwining odd Q在
prime simple spectrum與 P18 a.c. continuum間仍為0；point-evaluation rigging
不 closable，無 positive self-adjoint Q*Q。若續 rigged Hodge，必須從頭證
新 topology正、scaling自伴與 P21 determinant identity。

P26 依 nudge補正：P22.3是純代數 fiber obstruction，拓撲放寬無效。
energy-preserving cohomology的 superdimension仍是 `mu(n)`；改 grading會改掉
`1/zeta`，跨 energy Q則破壞 heat-supertrace identity。故 exterior-Fock Hodge
路徑正式只剩「同時重建 grading+generator+determinant」的全新構造。

P27：nontrivial zeros是 P24 scattering cancellation的 hidden modes。若 P21
prime system可被全域完成成 positive conservative realization，且 hidden
subspace繼承 nondegenerate positive energy，centered hidden generator必 skew-
adjoint，會推出 RH。尚缺 absolute D_F realization、hidden metric正性與
no-extra-modes三項；boundary phase不夠。

P28：每個 Euler factor已有 exact `2x2` unitary colligation，finite cascade給
`S_P=e^-xL_P D_P(-x)/D_P(x)`，不必產生 mixed determinant factors。P29：
critical cutoff仍失敗，因 normalized deviations尺度 `p^-1/2` 且
`sum_p1/p` 發散，無 Hilbert--Schmidt/trace-class infinite product。下一步只能
尋找保持 positive energy與 absolute D_F的非標準 operator renormalization。

P30 回答 density-one nudge：若先有 hidden realization，off-line orbit逐一給
negative direction，故 `kappa_-(T)=o(N(T))` 可推出 density-one RH；full RH
需 `kappa_-=0`。但 finite Euler cascades尚未 spectral-converge到 G zeros，
所以目前不能驗證此中間層。第一步應是 renormalized spectral-projector
convergence，而非直接引用 cutoff positivity。

P31：`direct-sum U_p` 可保持 unitary，但 critical determinant不存在；把 scalar
Euler product meromorphically regularize成 D_F後，zeta divisor不是 local state
spectrum。故下一步須構造 actual resolvent/projector convergence並保持
determinant identity；scalar zeta-regularization不具 Hilbert--Polya效力。

P32：prime diagonal在 critical line屬 S_q (`q>2`)，故 det_3可良定到
`Re s>1/3`，但必為 nonzero。`1/zeta=det_3 exp[-P_1(s)-P_1(2s)/2]` 表明
全部 divisor藏在 scalar prime-zeta cumulants。下一步若續 operator路線，須
正性地實現這些 counterterms；提高 Schatten order沒有用。

P33：`logdet_q=-sum_(m>=q)P_1(ms)/m`，只含 easy high-power tail；missing
low cumulants=`logzeta`減該 tail。若用 logζ continuation補 counterterm即循環。
standard Schatten方案封閉，下一步只能直接構造 low-prime-power+arch 的
positive relative operator identity。

P34/P36 修正：`m>=3` prime-power tail在 `Re s>1/3` 確實 analytic zero-free，
但 `L12=P_1(s)+P_1(2s)/2` 的 raw trace只在 Euler區存在。`P_1` 的 continuation
由 `zeta(ms)` 的 `rho/m` singularities決定；故把 P34.4延拓入臨界帶已預設
zero divisor。P34只保留為 bookkeeping，不是 genuine reduction；沒有一個
不使用 logζ的 low-orbit+arch construction前，此支線暫停。

P35：在 s=1/2，prime cutoff約 `2sqrtX/logX`，square cutoff約
`loglogX/2`；兩層不能直接 renormalize。Möbius的 logζ(2s) cancellation只在
continuation後成立。P34若續，必須加入 P18 arch cross term，一次完成 prime
bulk與 parity remainder的 sharp positive square。

最新非窮盡稽核：不能宣稱所有可行證法已耗盡。W18把 Weil／Stieltjes／
resolvent合併為同一 obligation，但 DN heat-flow collision barrier仍是不同
攻面；arithmetic positive cohomology則仍可能提供前者所缺的 construction。
下一棒優先推 DN9--DN11 的 tapered weighted-discriminant identity與 clock
commutator estimate，因其可作非循環中介引理；並保留 W16 centered sharp
square搜尋。禁止重啟逐 degree／moment有限證書。

DN12 已把最自然的下一步做完但得到 no-go。weighted product discriminant
`E_a=sum a_ja_k log gap^2` 滿足
`E_a'=4sum(a_jS_j+H_j/2)^2-sum H_j^2`；在 exact clock上 H是 symbol
`i(theta-pi)/d` 的離散 Hilbert transform。慢 taper的 H-cost仍與 block volume
同階，故不能把 DN9 flux降成 transition error。DN若續，只能尋找先消去
clock PV order-zero symbol的非局部 relative energy；普通 taper已封閉。

DN13 找到線性層的正確 relative-clock energy：`L` 的 Fourier symbol為
`pi|theta|-theta²/2`，`Q=<u,Lu>` 可控制每個 gap。然而從固定 `t_0` backward
的 amplification為 `exp(c t_0/d²)`；在高度 Gamma、`d~2pi/logGamma` 時要求
起始 rigidity達 `d²exp[-(t_0/2)log²Gamma]`。現有 moment saddle不提供此
zero-height estimate。DN14 回應 density nudge：平均 energy在首次 collision
前最多控制 bad-gap比例，沒有 collision index/projector convergence就不能
推出 density-one RH；目前 density版亦無無條件新結果。

新增 `horizontal_shift_route.md`。`E_a(z)=Xi(z+ia)` 的 Hermite--Biehler
threshold精確等於 zero strip半寬；已知 `0<Re rho<1` 無條件給 `a>=1/2` 的
all-degree base，故 `A_a=[Xi(z+ia)+Xi(z-ia)]/2` 全實零。下一個新 uniform
候選是 HS5：直接由 theta/centered primes構造 de Branges kernels的 half-shift
positive defect `K_(a/2)=T_a[K_a]+L_a`，從 a=1/2 dyadic下降至0。toy
`z²+1-a²` 證一般 harmonic deformation不保存實根；HS必須是 Xi-specific。
其 a→0 endpoint與 W18同一正性 obligation，有限 kernel驗證不算進展。

HS7 已排除普通 positive-kernel descent：frequencies 1,2、weights 1,2/3 的
正 measure使 `F_a=cosh(a)cosz+(2/3)cosh(2a)cos2z` 在 `a=log2` 全實零，
但在 a/2 因 ratio `5sqrt2/9<1` 產生非實零。故 HS5不能只靠 Phi正性、
positive-definite untilting或 smoothing；必須有 Xi-specific arithmetic
total-positive defect。

HS8：half-shift multiplier `r_a=cosh(au/2)/cosh(au)` 確有正 Fourier density，
但 reciprocal Laplace transform `cos(as)/cos(as/2)` 有 poles，所以不是
PF_infinity/variation-diminishing。這精確解釋 HS7；horizontal路線若續，
只能尋找 r_a與 Xi theta kernel的 coupled determinant identity，不能再用
普通正卷積論證。

HS9：下降時 A/B channels的 multipliers分別是 r_a與
`q_a=1/[2cosh(au/2)]`。q_a雖 PF_infinity，r_a-q_a亦 positive definite，
但 smoothing方向可把 `z²` 送成 `z²+a²/4`，仍創造非實零。horizontal線
只剩 Xi `(A,B)` pair的 coupled symplectic/de Branges Bezoutian；任何逐 channel
正性均不夠。

HS10：令 b=a/2，有
`A_b(z+ib)+A_b(z-ib)=A_a(z)+Xi(z)`、對應 B式只含 B_a。故 half-angle
inverse shift會把 endpoint Xi/K_0直接帶回；把它藏入 positive remainder屬
循環。HS若續，必須由 theta/primes證 Xi與 smoothed B-channel的 coupled
Bezoutian sign，不能引用 unknown zeros或 limit positivity。

P37：P23 Carleman不能和 P18 regular density拼成證明。critical atoms給正
candidate measure，但 arithmetic moments另含全部 off-cut poles的
`sum m u^k e^-tu`；boundary jump看不見它們。Carleman只給已存在 positive
measure的唯一性，不給 existence或 moment equality。故此捷徑封閉，P13/P16
all-k factorization責任不變。

HS11 在 known-GRH功能域 toy確認：真正使全部 horizontal shifts HB的是
Hasse bound提供的 shift-independent unitary Frobenius phase，乘積再由自伴
直和封閉；不是正 smoothing。Riemann尚無 global analog，local prime
colligations又在 critical infinite limit發散。

目前 impasse稽核：全部 hook nudges均已回應；W16/P13/HS、spectral
cohomology、DN三類最後都缺一個 workspace內尚不存在的 Xi-specific global
polarization／unitary monodromy／`exp[-c log²Gamma]` zero-rigidity。所有普通
finite、density、boundary、Schatten、smoothing捷徑均已明確封閉。沒有新的
arithmetic identity或外部數學輸入前，目前可執行的非循環路徑已窮盡；RH
未證。

聯網恢復後的新 handoff：先讀 `external_spectral_inputs.md`。Suzuki 2026 已
無條件補上 finite-volume self-adjoint generator；Connes--Consani--Moscovici
2025 已證 explicit prolate `k_lambda` 的 transform趨近 `Xi`。新的主攻不是
再做 finite matrices，而是 ES3 uniform bridge：證
`lambda^eta ||(A-mu)k||/(epsilon_2-mu)->0`（每個 `eta<1/2`）。此式同時把
prolate leakage、Weil ground state與 Hurwitz接起來。須先由 semilocal trace
formula抽 exact intertwining／form-residual，再證 parity-sector gap。注意 pole
項是 rank-two indefinite `2Re(conj(M_+)M_-)`，generic positivity-improving
不能直接給 all-a simple-even。RH仍未證，goal恢復研究中。

ES6 更新：Connes--Consani 的 global `E`-range確在 Weil radical，故
`k=1_I E(f)` 的 localized residual exact等於 outside-tail cross form；bulk
arithmetic cancellation已有骨架。不可因此稱 ground approximation：若 RH假，
負 spectrum可在 near-zero prolate band下方。下一棒須分開證 (i) smooth
regularization + weighted tail/form-dual bound，(ii) 不使用 `A>=0` 的 bottom
spectral-ordering lemma。後者若無新結構，很可能仍是核心 RH obligation。

ES7/hook 修正：停止把 `Delta=epsilon_2-mu` 當普通 gap。`epsilon_1(a)` 隨
interval單調不增，且 Suzuki 2026 證 RH 假必有某個 bottom<0；因此此後 bottom
被固定負常數壓住。若 `mu,r->0` 且 `||r||/Delta->0`，spectral expansion反推出
bottom->0，直接矛盾。故足以完成 ES3 的 uniform gap本身就是 RH 級 ordering
theorem；ES3已降級，ES6作獨立成果保留。

下一棒主攻不經 ground 的 ES8/ES9。首選檢查 exact Mellin recurrence (ES9.2)
在 functional equation下能否寫成無未知 zeta 分母 poles 的 Hermitian bilateral
transfer matrix，從而直接證 CCM explicit `hat k_lambda` 全實零。備選為 Suzuki
自伴延拓的兩個 characteristic functions之比（Weyl `m`）：若能證 shift-free
且在 `Im z>1/2` 趨近 `i xi'/xi`，Nevanlinna normal family可完成 RH。任何需要
shift `lambda(a)->0` 或 `A_a>=0` 的版本都屬循環。詳見 ES7--ES9。

ES9.1 首輪結果：functional equation精確給 bilateral coefficients共軛，但
untruncated HB function化簡為
`R=4pi^2 lambda^2 zeta(1/2+iz)F(5/2+iz)`；證其上半平面無零已是 RH。
故下一棒不要再磨 untruncated recurrence。只計算 CCM interval truncation造成的
boundary correction，目標是把它寫成 finite-volume determinant／flux 並直接
證 HB。若計算又留下 naked `zeta(1/2+iz)`，立刻判為同義改寫。

已得到 ES10 exact finite formula：
`K_lambda=sum_(n<=lambda^2)n^-p int_(n/lambda)^lambda f(x)x^(p-1)dx`。
在 `x=n/lambda` 的 cutoff jumps經 Green identity帶權
`lambda^(1-p)/n`。注意 `1/n` 正不等於 jump positive：它還乘符號不定的
`q(x_n)f'(x_n)`，且 jump在 Mellin test weight，不在 ODE potential。故不要寫
虛假的 2x2 positive monodromy；下一棒應建含 accumulated-integral channel 的
3x3 affine／inhomogeneous adjoint colligation，再檢查是否存在不依未知 zeros
的固定 metric與 HB boundary cone。這是目前唯一未被 ES7/ES9循環稽核封閉的
spectral 子路線。

ES11 已解 3x3 local metric：唯一 fixed J 在 accumulator方向為 radical，故
逐 interval/J-unitary方案封閉。形式 4x4 dual-port dilation總能做但 Hamiltonian
indefinite，沒有 HB含義。hook/nudge 的關鍵修正是：只需所有 n **累積後**正，
不需逐 jump正；單 n甚至沒有正確 inversion symmetry。下一棒應找 natural
companion `B_lambda`，推完整 finite sum的 Christoffel--Darboux/de Branges kernel
(ES11.4)，看符號不定的 derivative jumps能否 telescope成 Gram squares。不得
用 ground Weil positivity代替此 cumulative identity。

ES12 將 cumulative target精確化：先 inversion-symmetrize `k_lambda`（因 Xi偶，
strip limit不變），取 half-support transform `E_lambda`。若
`U_lambda=E_lambda#/E_lambda` 是 inner，則 `F_lambda=E_lambda+E_lambda#` 全實零，
Hurwitz完成 RH。operator驗收式是 Hardy projection
`P U_lambda=P U_lambda P`，只針對完整 n-sum，不逐 n。Connes--Consani
arXiv:1910.14368 已說明 individual local factors非 inner。下一棒應從 ES10 finite
formula計算 cumulative Hankel defect `(1-P)U_lambda P`；近似小不夠，需 exact
zero或被全上半平面 positive margin一致支配。

ES13 是目前最重要的新 uniform lift。若 unimodular multipliers `U_lambda`
weak-star趨 U，且 `(1-P)U_lambda f->0` 對 dense `D subset H2` 逐向量成立，
則 U先屬 Schur；另證 boundary modulus不流失才 inner。可用全部 fixed-index prolate modes：每個 n leakage趨零、
Hermite limits稠密，故不必 operator-norm小。下一棒優先尋找 (ES13.2) 的 exact
E/Poisson intertwining，必須對任意 fixed n同型；另需 ratio denominator
compactness/modulus retention與 `E,E#` nonreal coprimality。這才是有限 modes升到全部的機制。

ES14 已完成 operator-type audit：`R E=E F` 只把 prolate leakage變成 inversion
parity defect，不能變成 multiplication ratio的 Hardy Hankel defect。exact even
kernel仍可有 nonreal Fourier zeros（HS7），所以不可能有只依 leakage的通用
ES13.2。後續只有在 ES10 cumulative finite sum中先找出額外 Xi-specific
Bezoutian/score Gram主項，才可用 prolate leakage估 error；否則此支線封閉。

ES15 是下一棒的直接計算式：對 symmetrized `F_lambda`，需證全部
`t real,eta>0` 的 `partial_eta|F_lambda(t+i eta)|^2>=0`。ES10.1 展開成
all `n,m<=lambda^2` 的 (ES15.3)；逐項可負，只接受完整 summation-by-parts後
的 Gram squares。先嘗試用 prolate ODE對 x,y 同時分部，看 derivative jumps
是否成 pairwise telescoping。若只得到 `eta=0` Laguerre inequality或有限
`t,eta` batches，立即判為不足。

ES16 已做單 component完整 Green 分部，公式見 ES16.1--2。端點不只
`q_m f'/m`，還有 `-(p-1)q_m f/m^2`。bulk會生成帶 `m^+/-2` 的 shifted channels，
故 3x3或逐 m telescoping不閉合。更重要：實際 `h_lambda=c0 h0+c4 h4` 不是
單一 eigenfunction；下一棒必須拆 `00,04,40,44`，用兩 eigen-equations之差
尋找 `chi4-chi0` 的 coupled Wronskian/CD identity，再檢查 zero-integral係數能否
消 boundary signed sums。若仍產生無限 m^(2j) hierarchy，prolate ODE finite
closure即封閉。

ES17 修正 nudge 中對 oscillation的疑慮：cos difference已是 rank-two Gram，
不必由分部消掉；把 cosine/sine moments組成 v，把多一個 log r 的 moments組成
w，則 score精確是 `v dot w`。真正要證的是四 prolate channels合計後的
dissipativity `w=-Cv+J beta v+e`，`C>=0,v dot e<=0`。下一棒以此 2x2 sign
geometry檢查 chi4-chi0 Wronskian，不再追逐每個 t-dependent jump square。

ES18 結果：請區分 PW differential eigenvalues `omega_nu` 與 concentration
`chi_nu`。`omega4-omega0` Green identity只能處理 04/40；00、44 diagonal
channels仍完全未定，zero-integral relation也只在單一 Mellin point成立。
因此不要再宣稱兩-mode CD自動閉合。若續此路，只接受 2x2 vector score matrix
`M(z)<=0` 的 Xi-specific Gram identity，或直接證 special coefficient direction
`c^*M(z)c<=0`；它與 HS9 coupled Bezoutian同一 obligation。

ES19--21 更新後的主線：matrix de Branges文獻把 matrix-inner/positive kernel
當假設，不能補 ES18；full matrix sign又比所需 special direction過強。新的真結構
是在 finite-Fourier正相位支 `span{h_0,h_4,h_8,...}` 上，
`Q=(PW-omega0)(PW-omega4)+ell^*ell` 無條件半正定，且 kernel恰為 CCM 的
zero-integral `h_lambda`。這提供所有同相位 modes的 auxiliary simple ground與
gap，不是 degree-by-degree證書。

但 CvS real-zero theorem要求 convolution/difference kernel；Q的 scaling
commutator有 infinite-rank differential bulk，故 auxiliary positivity本身不夠。
下一棒先計算 hard-truncated `S_lambda=1_I E` 對
`[Q,x partial_x]` 的 exact intertwining：若 arithmetic/Poisson cancellation能把
bulk化成 log-translation-invariant form加 finite boundary，即得到可套 CvS 的
新橋；若 infinite-rank bulk仍在，封閉 full conjugacy，改攻由 Q 的 quadratic
form直接導出 special score `c^*M(t+i eta)c<=0`。不得以 full matrix negativity、
一般 PSD kernel或更多 VERIFIED batches替代。RH未證，goal保持 active。

ES22--24 有重要修正。Connes--Consani exact E-radical要求
`f(0)=int f=0`；finite CCM h0/h4只滿足後者，value defect精確為
`c0h0(0)(1-tau0/tau4)`。改用 same-phase h0,h4,h8，係數
`d=(tau4-tau8,tau8-tau0,tau0-tau4)` 可 exact 消兩條件。正 phase tower上的
`(PW-omega0)(PW-omega4)(PW-omega8)` 半正定，加兩 functional squares後
此三模態 line是 unique auxiliary ground。一般 r constraints已有 r+1 modes的
uniform spectral-polynomial與 positive-measure/Lanczos表示；詳見
`three_mode_poisson_route.md`。這與 J24/Jensen degree無關。

full auxiliary form經 E 變成 CvS convolution的路已封閉：Mellin bulk的
`p+/-2` shifts在 cubic後到 `p+/-6`，finite boundary correction不可能變成
scalar multiplier。下一棒只做三件事：(i) 逐 normalization核對 Fuchs ratios並
把 CCM fixed-mode estimate擴到 n=8，證 three-mode g_lambda->h；(ii) 對 hard
endpoint smoothing給 exact double-zero且控制 strip/Weil-form residual；(iii) 直接
展開 special g_lambda 的 ES15 score，看兩條 Krylov cancellations是否使不定
radial form成 Gram。若只得到 tau-variable orthogonal polynomial實根、Sonine
space membership或一般 PSD ground，均不足。RH未證，goal active。

聯網後 ES25--ES28/G31 再重排主線。所需 score只在 `0<eta<1/2`；natural
one-sided Xi half-kernel companion已由 t約17的負 HB-difference diagnostic排除。
三模 hard cutoff的 high-t主項是所有 arithmetic jumps組成的 ES26.2
Dirichlet--sine polynomial，不是單 outer endpoint；lambda 2/2.5/3 scan尚未在
critical strip找到非實根，但數值不算證明。可行子題是證此 polynomial的 uniform
strip stability及 `O(1/z^2)` Rouché tail。

更重要的新外部輸入是 Freedman 2026 `arXiv:2606.29555` 的 theta
second-order/Volterra branch contraction。其 KLM-to-de Branges bridge仍缺。
我們的 endpoint audit給
`K_Eomega=omega B_Xi+O(omega^3)`，而 KLM kernel為 `K_0+O(omega^2)`；所以任何
bridge在 omega->0都必直接 factor Xi Bezoutian，正是 all-degree anti-Pick/RH
義務。Mellin tail可 diagonal匹配，moving incomplete-gamma prefix不可忽略；只把
z-dependent prefix trace放入 graph norm不算 bridge。詳見 `volterra_klm_audit.md`。

下一棒優先二選一：(A) 對 ES26 exponential polynomial作解析 strip-stability
證明與 uniform remainder；(B) 從 exact Mellin prefix+tail split構造單一
z-independent Hardy--Volterra joint-Gram isometry。不得重跑有限 KLM/Jensen
certificate代替。RH未證，goal active。

又新增 T3P8/T3P9。T3P8 證了一個 exact local-HB dominance lemma：endpoint jump
polynomial若 `|q|>N+log(N!)/log(lambda)` 則在 `0<eta<1/2` strict HB；目前只有
lambda=3 heuristic q通過，不能當 asymptotic theorem。更穩健的 T3P9 用第四及
更高 same-phase modes逐一強制 `g(lambda),g'(lambda),...=0`，同時保留
`g(0)=int g=0`。這會一次消所有 ES10 internal cutoff jumps到任意指定階，讓
high-t leading term成單一 outer sine。正 spectral-polynomial ground theorem自動
延伸；真正缺口是 rank及 Dunster endpoint asymptotics下 boundary correctors不改變
CCM central limit。bounded-t仍需 G31 的 Xi-Bezoutian/Volterra bridge。下一棒先證
T3P9.4 generalized Vandermonde與 fixed-m projective limit，不做更多 finite scans。

T3P10 已完成前半：以 c->0 Legendre limit、endpoint polynomial Vandermonde、
integral orthogonality與 `P_(4k)(0)` 的 strict completely-monotone表示，證 fixed m
constraint matrix除離散 lambda-set外 full rank。下一棒不必再查 rank；直接用
Dunster 1601.00699 endpoint formulas估 augmented null vector的 coefficients，證
新增 h12/h16/... boundary correctors在 compact x-window消失，保留三模/CCM limit，
並追蹤 condition number足以支撐 ES10 eta-linear remainder bound。

最新主線改由 VK6/ES32 接管。直接把 Xi Fourier integral與半線 Laplace分母代入
Bezoutian，換元 `q=t+r,q'=r-u`，利用 Phi even，已 exact 證

```text
B_Xi(w,z)=4/pi int_R^2 K_0(q,q')e^(izq-i conj(w)q')dq dq'.
```

因此 Freedman 原始 `omega=0` coordinate kernel `K_0>=0` 已足以直接證 RH；未知
finite-omega de Branges transport與 uniform omega均可暫停。真正唯一 blocker是
論文自己標出的 normalized quotient-to-original lift：必須對每個 compact test
解析證原始 quadratic form等於 closed Volterra quotient form，且 quotient positivity
本身不依 finite grid/numerical certificate。下一棒先逐段稽核其 parity reduction、
mixed derivative兩次 primitive、trace quotient與 density/closure；若任一步把原始
positivity當假設、漏 endpoint/nullspace、或只由有限 certificate外推，立即記錄。

該稽核已有結論：Problem 15.15 後段證 primitive boundary repair為零、primitive
trace image完成後等於全 `X_R`。所以真正剩餘不是 closure，而是
`D_q=0 <=> Gamma^*Gamma<=C <=> Q_Phi>=0` 的 continuum theorem；配合 VK6 的
反向 Fourier density，這與 RH-equivalent K_0 positivity同級。下一棒只接受
`D_tr` 的 explicit Volterra/Green Gram factorization或一個解析反例；有限 Schur
spectra、Moore--Penrose completion及 ker-R positivity都不算關閉。

VK6 Taylor expansion還給出先前策略稽核要求的 uniform-in-degree答案：每個尺寸的
Xi Bezoutian coefficient matrix都是同一 K0 form中 monomials的 Gram compression。
所以 degree 3仍只記獨立成果；真正升階定理是 conditional `K0 PSD => all degrees`。
不得恢復逐 degree finite certificates來反推 K0。

另 T3P11 已排除「Platt--Trudgian 固定高度＋endpoint tail」捷徑：prolate bandwidth
`c->infinity` 使 reliable tail onset漂移，留下增長 middle band。endpoint-jet tower
保留為 hard-support regularization成果，但不再是主 RH bridge。RH未證，goal active。

聯網後新增 ES36--38/G34/K0B7。Burnol Sonine positive spaces沒有把 Xi辨認成
structure function；Dimitrov OP-Wronskian/Lee--Yang條件與全 Jensen塔等價，沒有
由三項遞迴自動升階。最新 Holland 2608.08682 證 joint wedge
`n^3 log^2(n+2)>=K d^5`，是真 uniform theorem，但 wedge外仍含 `n=0,d->infinity`。
微分 `J^(d+1,n)'=(d+1)J^(d,n+1)` 不能反向，除非證全部 critical values交錯。
下一棒優先：(i) K0/D_trace continuum Hardy--Volterra Gram；或若找到具體公式，
(ii) Phi dt的 Lee--Yang measure closure；(iii) wedge向低 shift的 uniform
critical-value transport。不得把 ambient de Branges空間、OP recurrence或 wedge
內 hyperbolicity誤稱 RH。goal active。

新增 ES39/K0B8：對 fixed n，
`J^(d,n)(X/d)->F^(n)(X)`, `F(X)=xi(1/2+sqrt X)` locally uniformly；由
`binom(d,j)d^-j<=1/j!` 直接證。故只證 `J^(d,0)` all sufficiently large d
hyperbolic就等價完成 RH。Holland wedge外的 `n=0,d->infinity` 不是技術尾巴，
不得企圖只靠更高階 saddle expansion宣稱可掃除；必須有新的 continuum全正性。

Newman--Wu 1708.08820 已提供 Lee--Yang laws 的 weak-closure theorem，故模型路線
不再缺極限技術；唯一合格新構造是 finite known-Lee--Yang magnetization laws
`mu_N` 並嚴格證 `mu_N=>Phi dt/intPhi`。目前尚無 coupling/scaling formula；一般
positive quadrature不保 Lee--Yang。主線仍優先 K0/D_trace continuum Gram。

K0B9/VK9：定義 `F(p,d)=1/2 int_|p|^infinity yPhi(y+d)Phi(y-d)dy`。
half-line same-sign/reflected blocks exact是 `A=F(p,d), B=F(d,p)`；故下一個最具體
主線接口是 theta-specific `A=T^*T, B=T^*ST`，其中 S為實現 center/difference
swap的 self-adjoint contraction。generic even kernel不成立，不能只靠 abstract
parity或 finite Schur。RH未證，goal active。

新增 K0B10--11：定義 symmetric double-tail `P(q,r)` 後 exact 有
`K_even=-P_q`, `K_odd=P_r`。若 `P=sum c_m(q)r^(2m)` 的所有 `c_m` completely
monotone，兩 parity blocks同時成 Laplace monomial Gram，這是真正 all-size充分
定理。首關已化為
`c_1(a^2)=(4a)^(-1)int_0^infinity Phi(2a+s)[Phi(s)+2(a+s)Phi'(s)]ds`；
浮點 probe只顯示低階正號，非證明。下一棒先用 theta differential/modular identity
嘗試把此式化成正 Laplace measure，或找 rigorous反號；成功後才研究一般 m，禁止
退回有限 KLM／逐 degree刷證書。RH未證，goal active。

但 K0B12 已在下一輪稽核淘汰該 CM ansatz：`c_0>0`、`-c_0'>0` 都比任意
`e^(-Aq)` 衰減更快，與任何非零 positive Laplace transform必有 exponential下界
矛盾。故不要再攻 coefficientwise complete monotonicity；K0B10.2 的 exact
`K_even=-P_q,K_odd=P_r` 可留作座標，但成功分解必須耦合不同 r-orders。
主線回到 VK8 的 shifted-theta feature／Hankel-square Loewner monotonicity，並尋找
theta-specific coupled Gram；RH未證，goal active。

新增 K0B13/VK10：full-line form exact為
`Q_K0=-Re int_0^infinity B_f conjugate(A_f)/2`。令已證遞增的
`q=-Phi'/(tPhi)`, `c=q(0)`，可拆成 Gaussian boundary square與 residual；下一個
最小命題是 K0B13.6 的 boundary-dominated Volterra contraction。這同時含 reflected
block，不能用 kernel pointwise sign代替。ES41/VK11 引入 Audenaert all-order
anti-Loewner分類：若 theta Hankel sign-symbol能正則化，證 `sigma'/sigma` 的正測度
表示可關 same-sign block；尚缺 distribution regularization及 VK9 reflected
contraction。禁止再回 coefficientwise CM或有限矩陣批次。RH未證，goal active。

K0B14 警告：上述 boundary split exact等於
`Y_c=e^(z^2/(2c))Xi` 的 Bezoutian gauge；rank-one boundary之外的 residual仍是
完整困難。Phi超指數尾亦排除 positive Gaussian deconvolution。所以下一步不能只
引用 score單調，必須給 residual的 theta-specific coupled factorization或反例。

VK12/ES42 又關閉 standard ordinary anti-Loewner sign-symbol：`sigma'/sigma>=0`
會迫使 sigma正、Phi completely monotone，與超指數尾矛盾。除非先發現全新的
multiplicative theta transform並重推 kernel，否則不要再直接套 ES41；近期唯一具體
K0子目標仍是 residual coupled factorization。RH未證，goal active。

新增 K0B15/VK13：用 decaying positive primitive
`R=e^(-t/2)int_(-infinity)^t e^(s/2)Phi(s)ds`，完整 form exact為
`Q_K0=|U(0)|^2/4+||U||^2/4-Re<LV,LU>/2`；下一最小命題是 common-range graph
bound K0B15.4。K0B16 已嚴格排除逐 theta-pair Gram：對 m>n，reflected saddle
`2nm` 壓過 same-sign `n^2+m^2`，pair odd eigenvalue終為負。故必須找完整 theta和
內的跨 channel cancellation；不得把 Selberg nudge所指的積分平均偷換成逐項正性。
RH未證，goal active。

K0B17/VK14 已用 J5 radial convexity及保測度換元嚴格證
`K0(x,y)-K0(x,-y)>=0` 對所有 x,y≥0。這回應 Selberg nudge的一層量詞：完整
theta和可逐 integrand比較；但 entrywise非負不等於 kernel PSD。下一棒只接受把
convexity差表示成附加參數下的 PSD kernel／higher total positivity，或回到 VK13
common-range graph bound；不得把 pointwise sign稱作 RH證明。goal active。

K0B18 把上述 entry差 exact寫成 positive convexity path integral；但 ordinary
Loewner升階會要求 `h'` operator monotone，與其 theta超線性增長矛盾。不要再追
standard operator convexity；下一步必須利用整個 path integration geometry的
coupled Gram，或回 VK13 common-range graph。RH未證，goal active。

最新聯網接續點：K0B19--23 已回答 Selberg nudge 的 graph norm問題。
`L=D-1/2` 無界，但 whole line symmetric part exact cancellation；更重要地，
`1/(1/2+i xi)` 是負半線 causal kernel，其 positive compression恰等於 L7 的
boundary/storage 右邊。所以 L7 精確縮成

```text
Re<P_+M_(iXi'/Xi)P_-w,P_+w><=0,  w in Ran(T_Phi),
```

左邊 exact是 `-2Q_K0`，仍為 RH-equivalent。由 range 在 ordinary L2 稠密，
bounded Nehari/contraction 路徑會因反號迫 block=0，已排除；需要的是
Xi poles/zeros cancellation下的 unbounded graph Gram。

外部輸入 Suzuki 2206.03682 又給 shifted screw densities 的 exact forward
Volterra positivity semigroup，但 inverse不保正；`Psi_0>=0`本身已等價 RH。
因此新的第二候選是構造 theta/prime-specific invariant subcone，使 shift
semigroup在子錐上可逆保正。下一輪優先嘗試把此 subcone 與
`Ran(T_Phi)` graph topology 辨識為同一 canonical-system state cone；若無 exact
intertwiner，不得把等價改寫當進展。RH未證，goal繼續 active。

最新 Selberg nudge 已完成量詞稽核：`Ran(T_Phi)` 在 full L2 稠密且
不閉，投影到 positive half-line 後仍稠密，所以在 Paley--Wiener H2 中
沒有餘維。L7 的 common-range 限制沒有降階效果；只有
`||w||_G=||hat w/Xi||_2` 的 graph topology，但此 norm 拉回就是原 K0
operator。後續不得再把 range restriction 當進展。

K0B25 同時排除 finite-order Sturm--Liouville Green 猜想：兩 parity kernels在
interior diagonal real analytic，local Green inverse卻必有 delta jump。K0B26 排除
naive shifted graph cone：same-preimage graph transfer永遠 unitary，是 tautology；要求
output Hardy causality即 all-shift Xi ratio Schur，等價 RH。下一接續點只接受
不使用 division by Xi 的 theta/prime local invariant cone，或 K0 的
nonlocal/infinite-order exact positive realization。RH未證，goal active。

2026-08-15 聯網外部稽核新增 K0B27--29／ES45--47。Schoenberg解析排除 raw
classical Phi 的 PF∞，2602.20313v2另給 certified PF5 obstruction。下載的
2602.01248v1 source含兩個明確斷層：PF∞ finite positive sums closure lemma錯誤
（translated Gaussian exact 2x2反例），且 centered half-density inversion assumption
與 Jacobi公式直接矛盾。其 prekernel transform其實 exact為
`2C alpha^(-q)Gamma(q)zeta(2q)`，沒有移除 zeta困難。

另推導 de Bruijn flow下 Bezoutian的四維 radial backward-heat PDE；
`F_t=z^2+1-2t` exact證 generic downward PSD descent為假。新的唯一具體 local cone
是 K0B29/L9 的 prime Euler--Volterra product。下一接續點：嘗試構造含
Archimedean completion的 common K0 quadratic storage，使每個 prime shift resolvent
contractive並可取 infinite product；若無 telescoping defect identity，該路只是在
Euler half-plane的 pointwise tautology。不得改做有限 degree/minor batches。

K0B30 已把這個下一點再稽核：completion gauge使 factors成
`(I-p^-1/2T_(2log p))^-1`；任何 natural exponential weighted L2 的 partial-product
norm都含 Euler product，只有 weight參數 `sigma>1/4` 收斂，target `sigma=0`
發散。因此 ordinary positive common energy已關閉。若繼續，必須找 signed
prime--gamma counterterms在同一 K0 form中的 exact telescoping；這與既有 Weil
all-test square缺口相接，不得把 Euler half-plane positivity重命名為進展。

K0B31 新增 exact Bezoutian product rule；它證明 convergent real-entire LP
factorization確是合格的 uniform升階。外部 Shi 1502.06844 的 real-rooted
Pólya-like approximants卻沒有 `m->infinity` 的 kernel norm／transform locally
uniform convergence，只匹配尾部與有限 central jets。下一輪若嘗試此分支，必須
直接建立有 global domination的 LP exhaustion；更多近似圖或 jet matching不合格。

最新 Selberg nudge要求把 G41量化為跨 `sigma=1/4` 的一致估計。K0B32 已對 Shi
第一 approximant family做完：其 Riemann sum極限可顯式算出，且在任意 exponential-
weighted L1都收斂，但極限帶 `2beta/a` tail correction、不是 Riemann Phi。新增 L10
充分定理：若 real-rooted/LP kernels對 Phi在某 `R>1/2` weighted L1中收斂，Fourier
transforms在完整 critical strip locally uniform，Hurwitz直接推出 RH。下一輪只接受
真正滿足此 target convergence的 construction；逐 approximant實零或 tail matching不算。

最新 Masters' Nudge 的反向稽核已採納：RH真時取 `K_N=Phi`，所以 L10存在性與 RH
等價，只是驗收準則而非降階。K0B33--34 新增兩個 exact all-degree介面：
`sigma_K0(p,xi)=1/2 int_|p|^inf yW_Phi(y,xi)dy`，以及完整 rectangular 2D theta
的 scale--shape differential/boundary identity。Hudson theorem排除 raw Wigner
positivity，一般 positive Weyl symbol亦不足；下一棒只接受 theta-specific
anti-Wick/Kraus/star-square factorization，或 modular PDE嚴格導出此分解。

K0B35 隨後把此斷層壓到最小：
`int e^(2sy)W_Phi(y,xi)dy=|xi_R(1/2+s+i xi)|^2`，且
`int e^(2sp)sigma_K0(p,xi)dp=(8s)^-1 d_s|xi_R(1/2+s+i xi)|^2`。
Lagarias/Sondow--Dumitrescu horizontal monotonicity criterion使後者對所有 `s>0,xi`
為正恰等價 RH。因此不要再追 scalar Mellin/Laplace positivity；二維 theta路只在
能產生 operator-level anti-Wick/Kraus/star-square時保持非循環。

ES52/K0B36 又排除 2026 theta-kernel preprint所暗示的 scalar shortcut。其 two-sine
identity只重寫 Lagarias monotonicity，final positivity problem仍等價 RH；且三個
translated Gaussians的 exact反例同時滿足 strict log-concavity與 J5 radial-score
monotonicity，Fourier仍有 `pi +/- i arcosh(3/2)` 非實零。故下一步的 modular theorem
必須真正排除此反例並直接給 operator CP/Gram；positive amplitudes本身不合格。

最新 ES53--54 再稽核兩份 2026稿：Planat paired-tail paper的 ray curvature命題由
`a->0` Taylor展開 exact否證，且 pre-crest/global bridge原文仍 open；Polson Wald/GGC
paper明認 mixing measure signed、剩餘 complete monotonicity為 RH-equivalent。
所以不要沿 scalar Riccati curvature或 auxiliary infinite divisibility續寫；主缺口仍是
theta modular／signed prime-gamma cancellation的 operator CP realization。

K0B36.5 已把同一 Gaussian-mixture反例加強到 `p'>0` 與
`R=(p^2-p')'>0` 全域；所以後續禁止以更多 scalar score/Riccati derivative正號
替代 operator升階。合格新 lemma必須明確使用完整 theta格點、且對此反例失效。

K0B37 現提供這種首個 theta-specific介面：full `(m,n!=0)` lattice theta滿足
`(D_y^2-1)H=4Delta_zH`；在 rectangular geodesic的 Fermi coordinates，completion
為 `Phi(y+d)Phi(y-d)=1/4(H_rrrr+2H_rr-3H_ss)`。下一棒只攻其 K0 cone integral
是否有正 energy-flux/Green/Kraus identity。現有 factor是 hyperbolic
`N^2-partial_s^2`，所以尚非平方；不得把 PDE本身稱作進展完成。

最新外部輸入 Holland 2608.08682 是 genuine uniform-in-degree 成果：
`n^3log^2(n+2)>=Kd^5` 即有 `J^(d,n)` 相異負實根。原始 TeX正規化無誤；機制為
Laguerre/Jacobi/second-Jacobi finite-free model匹配 `R_0,...,R_4` 加五階穩定性。
但它明言沒有 partial-hyperbolicity converse，n=0 完全不在楔形。MMP 2309.10970v3
又證 finite-free只 forward保持正根/交錯，且相異正根因子的 inverse不能留在正根 cone。
因此 Jensen 路只可攻 L11：theta-specific reverse shift/common-interlacing，或完整
all-order exact factorization；禁止用更多 fixed-order matching/VERIFIED batches代替。

J66--67 又封住兩個自然補法。Riemann tilted moment的 raw Schur--Szego multiplier為
`M_d(Y)=E(1+U^2Y)^d`，其 quadratic discriminant exact為 `-4Var(U^2)<0`，所以
positive Laguerre mixture並非 positive-root finite-free factor。另
`P=x^4+8x^3+22x^2+24x+12` coefficients全正、所有 n>=1 derivatives全負實根，
但 P本身無實根；因此 generic reverse shift即使加 positive coefficients仍為假。
L11 若可行，必須有能辨識 Riemann theta/prime並固定 integration constants的結構。

Shi 1706.08868 所宣稱的 real-rooted uniform Xi approximants亦已關閉：原 TeX
equations 2913--2964 把偶次有限和 j=0..m 補零後錯改成全次和 j=0..m；正確上限
是 2m（odd支 2m+1）。m=1 即可 exact看出遺失 y^2/2。所有後續 tail identities、
`m=7n^3` sign balance與交錯因而無效。不得把該稿當 L10或 RH proof；若再找
approximant，先做 finite-index identity audit，再談 uniform convergence/Hurwitz。

## 2026-08-15 continuation: exact normal-mode audit and canonical input

K0B38 closes the naive local-energy reading of K0B37. For one `(m,n)` lattice mode,
the normal stress is exactly
`lambda^2(2mn)^2(3-2lambda m^2e^-s)(3-2lambda n^2e^s)e^-lambda A`.
It changes sign and is not a square. A theta-PDE proof must use the complete lattice sum
plus cone-boundary cancellation, not modewise heat positivity.

ES60 adds Suzuki's peer-reviewed 2025 canonical-chain theorem. Its endpoint is exact:
`u_Xi=(Xi-iXi')/(Xi+iXi')` is inner iff `supp F^-1u_Xi subset [0,infinity)`.
This is all-degree but RH-equivalent; the theorem assumes inner/HB at `t=0` and is
unconditional only for shifted ratios `omega>=1/2`. ES61 also shows cyclic Jacobi
heat-kernel TP is in the spatial angle variable, not Riemann log-time scale.

Current live paths are (a) a nonlocal Green/Rellich identity for the full 2D lattice sum,
or (b) a prime/theta causal factorization yielding Suzuki's support condition without
using `1/E_Xi`. Degree-by-degree certificates remain stopped.

## 2026-08-15 continuation: new uniform Pick--Bernstein route

ES62/J68/L12 add the first concrete external coefficient theorem that genuinely treats every
degree at once. For `m_n=int_0^infinity u^(2n)Phi(u)du`, define

```text
varphi_n=2(2n-1)m_(n-1)/m_n.
```

If these values are interpolated by a 1-separated Bernstein Pick function `varphi`, KPS
Theorem 4.4 applied to `Psi(z)=zvarphi(z)` makes normalized Xi a `D_L`/Laguerre--Polya
function and proves RH. The natural non-circular interpolant is
`varphi_nat(z)=2(2z-1)M(2z-2)/M(2z)`.

There is one genuine uniform advance: with the already proved Xi score
`q=-Phi'/(uPhi)` increasing,
`varphi_n=2E_n[q]` and
`varphi_(n+1)-varphi_n=2Cov_n(q,U^2)/E_n[U^2]>0` for every n. This closes only the
first Bernstein condition. The open work is all-order complete alternation plus a direct
Herglotz representation and real 1-separated Mellin zeros/poles. Do not replace it by finite
difference batches.

Audit warning: KPS equations (4.15)--(4.18) have a missing `i`/alternating sign and an
inconsistent factor/sign in their Riemann matching. Use the general Theorem 4.4 and J68's
direct Fourier-moment recurrence, not those displayed formulas. Diagnostics found no early
counterexample but are not proof.

## 2026-08-15 continuation：J69 / ES63

L12 得到新的 uniform reduction。令 normalized Xi law
`f_D(x)=Phi(|x|)/(2m0)`，`J=2cosTheta`。右 Abel inversion及 J5 的 `Phi'<0`
無條件給正 density `g_I`，使 `D=sqrt(I)J`；並有

```text
E[I^s]=Gamma(s+1)^2M(2s)/(Gamma(2s+1)m0),
varphi_nat(s)=sE[I^(s-1)]/E[I^s].
```

全部 KPS moments已有單一 positive、moment-determinate law，不再刷有限
Hankel/moment certificates。真正斷層：證此 `I` 是 complete-Bernstein subordinator
perpetuity，再證 meromorphic 1-separation。Hirsch--Yor forward theorem給必要條件
`log I` m.i.d.，可先攻 `K_I''` completely monotone；完成它仍需 converse。
詳見 J69、L12.1、ES63、G52。

外部稽核 ES64：Durán 2026 只證 fixed-width consecutive orthogonal combinations
eventually real-rooted；Romik Xi truncations的 width隨 degree增長，不能套成 uniform
closure。不要由此恢復有限 Hermite batches。

最新最小 target為 J70/L12.2。若
`A=L^(-1)[4(log M)''(2s)]`，KPS complete-Bernstein route必要地要求

```text
x/(e^(x/2)+1)dx <= A(dx) <= x/[2sinh(x/2)]dx.
```

這由 Hirsch--Yor harmonic-potential公式 exact推出，非數值猜測。優先尋找完整
theta lattice對 A 的正表示或反例；證 sandwich後仍需 admissibility converse與
1-separation。

J71 將 sandwich譜化：fixed poles `-(2k+1)` 正好給 upper envelope；若 Mellin zeros
`rho_j` 全負實，剩餘條件為 `sum_j exp(rho_jx/2)<=1/(e^x-1)`。尚缺
canonical-product growth與 zeros實性。優先找 nonreal M zero（可淘汰 L12）或
theta-specific real-zero theorem；有限 real-axis samples不算證明。

## 2026-08-15 continuation：J72 closes the natural KPS interpolant

已完成嚴格而非純數值的 Mellin-zero certificate。`M(s)=int u^sPhi(u)du` 的
meromorphic continuation在

```text
z0=-16.988364513985116996...+5.875534137135168256...i
```

半徑 `1e-18` 內恰有一零點。證法用 20 次分部積分、Arb balls、三類解析尾界與
Rouché；margin `>7.68e-19`。同時 `|M(z0-2)|>2.4058`，所以
`varphi_nat(s)=2(2s-1)M(2s-2)/M(2s)` 在 upper half-plane有未消去 pole，不能是
Pick/complete Bernstein。詳見 `mellin_zero_certificate.md` 與
`experiments/certify_mellin_zero_arb.py`。

因此 J72 單獨先關閉 **natural Mellin interpolant**；J69 正 mixing law是獨立成果，
不會自動升成 KPS exponent。當時尚留的「另一 Pick interpolant」可能性已由下方 J73
的 Carlson uniqueness一併排除，禁止再用有限差分批次或替代插值重開。策略回到真正
all-degree介面：K0全格點 nonlocal lift與不使用 `1/Xi` 的 Suzuki causal factorization。

Selberg nudge亦已落盤：J70.3是 measure domination；J71.2 的 density公式另需
absolute continuity與合法的 Mittag--Leffler inverse-Laplace升格。不得再把兩者混寫。

## 2026-08-15 continuation：J73 closes every KPS interpolant

J72 後剩下的「也許有另一個 Pick interpolant」也已嚴格關閉。任一 KPS候選滿足

```text
1/W_varphi(n+1)=n!m_n/[(2n)!m0]=F_nat(n+1),
F_nat(z)=Gamma(z)M(2z-2)/[Gamma(2z-1)M0].
```

Patie--Savov exact Stirling formula給 `1/W_varphi` 右半平面 exponential type與
兩個 vertical indicators `<=pi/2`。J69 moment bound、Holder及 gamma recurrence對
`F_nat` 給同一界；duplication formula又證 `F_nat` entire。Carlson theorem因此
強制兩者相等。J72 的 `rho` 使 `F_nat(1+rho/2)=0` 非實，與 KPS 1-separation所得
全負實 zeros矛盾。故 **整條 KPS interpolation route關閉**，不得以替代插值或更多
finite differences重開。詳見 `carlson_kps_uniqueness.md` 與 J73。

後續 Selberg nudge曾質疑 Carlson growth只控制特殊成員；已反向核對並排除。
KPS `B_(P1)` 的每個候選都是 Bernstein function，Patie--Savov exact formula明確對
任意 Bernstein `phi` 且全域 `a>0,b in R`成立，error在 `a>=1` uniform；
Levy--Khintchine線性 bound再給整個右半平面 exponential type。故 J73量詞保持完整。

K0B39--40 已把下一步再縮小：stress annihilates lattice axes，所以可 exact換成 full
automorphic theta；但 geodesic Fourier transform是 Wigner函數，Hudson theorem排除
raw point-trace positivity。唯一 live K0方向是對每個 test構造 automorphic lift，使
`Q_K0(f)` exact成 Haar/Rankin--Selberg norm。Kelmer--Yu只給 Haar average，尚未完成
這個 point-trace-to-Haar bridge。Suzuki causal endpoint仍為第二順位。

K0B41 又排除最標準的 full-orbit Rallis/coherent-state版本：Haar frame operator由
Schur lemma在 irreducible component上只能是 scalar identity，但 `K_0` 是非零 compact
operator。所以下一棒若續 K0，只能找含 `p>=0` cone/geodesic boundary的 **非等變**
theta lift，並直接證其 boundary correction為正；不能引用一般 Haar norm，也不能以
`K_0^(1/2)` 作定義。

Suzuki 2606.09096 另給一個可保留的 all-degree family：對每個 finite `a` 與
`lambda<lambda_a`，self-adjoint extension的 `W(a,theta;z)` entire且全實零。但不要
照抄其 conjectural Corollary 6。原推導取 `lambda=0` 前先假設 RH；若能無條件選
`lambda(a)->0`，因 `lambda_a` non-increasing已直接得到 RH。且 limit target
`z^2xi/xi'` 是 meromorphic，不可能在 C每個 compact作普通 holomorphic uniform
limit。下一棒若走此線，必須證一個不預設 endpoint positivity的 shift law，以及
nowhere-zero holomorphic normalization下、避開 denominator poles的 corrected
meromorphic compact convergence。詳見 K0B42/G54/ES68。

另已稽核 Zenodo 19546495 的 claimed proof，不可採用。它把 CCM 在 shifted form
`QW_N-epsilon_N I` 中得到的 auxiliary real spectrum，誤當成原 `QW_N` 對任意 test的
正 square-sum decomposition，漏掉 `epsilon_N||g||^2`。compact support只使 prime
terms穩定，不會證 `epsilon_N>=0` 或 determinant convergence。完整反駁見
`external_claim_audit_vicere.md` / ES69。

最新聯網輸入 ES70--71 已轉向真正 all-rank Toeplitz座標。Micha\l{}owski
2607.16795 證 `D_(r,k)>0` 於 `k>=10^18r^3`，但 q-Pascal dilation只在 fixed
`q_k,r` model內，不能把 shift往 `k=O(r)` 拉。Desnanot--Jacobi exact給
`D_(r,k)D_(r-2,k)=D_(r-1,k)^2-D_(r-1,k-1)D_(r-1,k+1)`；這說 next rank等價
preceding row log-concavity，沒有免費 induction。矩形 Jacobi--Trudi又把 fixed-k
all-rank問題對偶成 fixed-size reciprocal-Xi determinant，能解每個 certified fixed k，
但 growing k需要未知 poles的 uniform real ordering/Vandermonde control。

因此 coefficient-side真正剩 balanced cone `r,k->infinity`（特別 `k asymp r`）的
theta-specific Toda invariant或二參數 pole-tail theorem；degree 3甚至不供完整
Toeplitz rank-3 row，仍只是獨立成果。Deng--Yang--Lue 2608.11520 的 contour-Hankel
congruence flow也只在 crossings之間保 inertia；nonreal pair恰給 rank-two indefinite
jump，所以其 PSD條件是 RH等價重述。詳見 `toeplitz_uniform_route.md`、G55、ES70--71。

ES72（Groskin 2607.02828v2）又給 exact all-degree接口：
`g_v(z)=L F_v(z)F_v(-z)` 且 `<v,Q_inf v>=sum_zeta-zeros g_v(z)`，所以 real
ordinates逐項為 squares。其 strict total positivity只屬 `T>rho N` 的 post-band
archimedean tail，沒有包含 signed primes、pole與 archimedean head。完整 source的
Loewner matrices PSD仍是 localized Weil/RH endpoint。integer Hermite samples在
自然 type `2pi` 有 `sin^2(pi z)h(z)` nullspace，不能用單 lattice Carlson uniqueness
補 sign。下一棒若走此線，只接受 full prime--gamma source的 uniform Gram/Kraus，
或真正非循環的 all-boundary-phase Pick theorem。詳見
`finite_weil_dictionary_audit.md`、G56、ES72。

新增 W5--W6 no-go：有限 prime block等於正 shift-difference squares減
`2S_c||f||^2`，沒有改善既有 uniform coercivity gap；完整 Weil form亦不可能
只是正 Borel shift measure的 difference-square mixture，因其 Fourier譜為
absolutely continuous；Hardy theorem已無條件給臨界線零點及 boundary Dirac atoms，
off-line zeros局部只產生 smooth Poisson terms，故不需先假設 RH。後續共同 Gram
必須是 singular/self-adjoint compression或 boundary-residue 型，不得恢復正
shift-weight majorization。

T6/G57 再給 coefficient-side exact no-go：對任意 `A>1`，
`G_A=cosh(sqrt z)+A` 是 order `1/2` 正係數 entire function並有顯式 nonreal zeros；
但只改動 PF-infinity base `cosh(sqrt z)` 的常數項，所以所有 `k>=r` 的
consecutive Toeplitz minors仍 strict positive。故 ES70 即使由 `k>>r^3` 強化到
全 tail cone也不足；下一棒必須處理 Xi-specific growing head cone `k<r` 或證真正
reverse-shift invariant，不能只改善 tail wedge。

ES73：Kim et al. 2607.24830v2 的 Suzuki FEM實作不提供 endpoint sign。Rayleigh--Ritz
離散最低值是真 infimum的 upper bound，正值不能證真值正；`a>=0.6` 已低於解析度，
R6 又在首行假設 RH。唯一嚴格新式屬 prime-free archimedean head，故只列 diagnostic，
不得把其數值 positivity帶入證明。

T7/G58 新增 exact all-rank theta transport：正 geometric rescaling後，
`c_(k+j-i)=int u^(2k+2j)Phi^(2i)(u)du/(2k+2j)!` 對所有 indices成立，負 index的
0由偶性 boundary jets給出；Andreief把 `D_(r,k)` 寫成 derivative determinant乘
正 Vandermonde的積分。可是 `r=3`, `u=(.05,.10,.16)` 的 derivative determinant
已有 rigorous negative enclosure約 `[-17.2236262221,-17.2236261081]`。故不得宣稱
Phi even-derivative kernel TP；若續走此線，只接受全積分的 theta involution／
symmetrized square。certificate在
`experiments/verify_phi_even_derivative_kernel_failure.py`。

ES74：Polson SSRN 6992163 的 Barnes-beta/Wald字典沒有補洞。`S2,C2` 的
integer-square Thorin measures與 `C2/16` clock確為 unconditional positive；但真正
Xi dual measure直接寫成 folded zero atoms `sum delta_(rho(1-rho))`，其支撐正實軸
明列為 RH-equivalent open clause。不可把前者的 GGC positivity搬給後者。

T8/G59：標準 theta modular reflection在 log座標只是 `u->-u`，它保持
`Phi^(2i)`、偶 monomials、measure及 `u^2` Vandermonde；permutations也同時翻轉
兩 determinants。故 T7 的負 patch不會被對合到正 patch。續走 T7只接受一個會
mix derivative order/theta indices且明證 Jacobian/Vandermonde的非平凡 integrated
identity；普通 theta symmetry已關閉。

ES75/G60：Schatz backward-parabolic稿無效。`E_t=z^2+1-2t` 是同一 backward
heat flow的精確反例：實零 slice跨碰撞向後立即產生非實對及負 Pick區。原稿
Appendix C錯稱 WPT給 individual analytic roots（`+-sqrt(t-t*)`否證），Lemma 7.3
又把依賴 zero-speed的局部能量常數當成碰撞前整段的有限常數，雖速度實際發散。
詳見 `external_claim_audit_schatz.md`。下一步不要修補這條線；回到真正
Xi-specific 的 singular/discrete spectral compression，或尋找能對 complete
prime--gamma source給 all-scale positivity的新外部定理。

T9/G61：T7還可 exact把全部 even derivatives移到 monomial Vandermonde，零端
boundary因偶性消失；但新 integrand仍變號。明確地 `r=2,k=1,u=(1,4)` 時
`A_2V_(2,1)=-130`。所以不要把 Capelli／random-matrix derivative principle誤當
Gram closure。若續走，只能證 `prod Phi(u_l)du_l` 對整個 signed polynomial族的
uniform integrated positivity；這仍是 balanced cone本身。

ES76/T10/G62：Förster--Kieburg--Kösters 的 Pólya-ensemble外部分類精確辨認 T7：
`x=u^2,nu=-1/2,omega=x^-1/2Phi(sqrt x)` 時，連同 Jacobian的 joint density就是
T7 derivative determinant乘正 Vandermonde。因此 T7.4 已否證 size-3 Pólya
ensemble；其 convolution semigroup需要 density先非負，不能修復。後續不再以
random-matrix/Capelli重新包裝此 local kernel。

T11/G63 是目前新找到、未被 T7.4 排除的 uniform target。定義
`sigma_r=det[Phi^(2i)(u_l)]Delta(u^2)du` 並以 `tau=prod u_l^2` pushforward為
`nu_r`，則 exact有
`r!prod_j[2(k+j)]!D_(r,k)=int t^k dnu_r(t)`。所以只要直接證每個 `nu_r>=0`，
即可同時處理所有 rank/shift，無需 joint density pointwise正。外部 random-matrix
theorem先假設 joint positivity，不能循環套用。下一步應尋找 product-level-set的
theta/Poisson sum-of-squares或 Mellin-convolution公式。小範圍 Hankel篩選未見反例，
但純屬診斷，不得當證明。

T12/G64 更新：T11已有很強而尚未嚴格化的反例訊號。令
`f_(i,j)(y)=e^((2j+1)y)Phi^(2i)(e^y)`，則展開兩 alternants exact給
`g_r(S)=r!det_*[f_(i,j)](S)`，且 `dnu_r/dt=g_r(log(t)/2)/(2t)`；Fourier側為
`r!det[hat f_(i,j)]`。三個截斷窗與 1024--4096 grids一致給
`g_7(-7.65)約-4.2454e21`、`g_8(-6.90)約-7.7170e33`；獨立 60-digit實作亦同號且
收斂。這仍不是嚴格反例，因 tail與 discretization尚未 interval-enclose；但 T11已不應
再列 live正性候選。後續若處理它，只做一個負值的 rigorous enclosure，不刷更多 moments。
實驗：`experiments/probe_t11_pushforward_convergence.py`、
`experiments/probe_t11_pushforward_mp.py`。主研究轉回能處理所有 degree的 complete
prime--gamma spectral compression、全正性或真正升階定理。

T13/G65 最終狀態：T11已不只是數值可疑，而是 rank 7嚴格為假。Bilateral Laplace
matrix `F_(i,j)(s)=int u^(2j-s)Phi^(2i)(u)du` 的最右 pole在 `s=1`；其 residue經
分部積分化為 matrix `B`（第 0欄為 `Phi^(2i)(0)`，其餘欄為這些 derivatives與奇
moments）。將 convolution determinant按 permutations展開，每項恰有一個 column-0
最慢 factor；dominated convergence嚴格給
`lim_(S->-infinity)e^-Sg_r(S)=r!det(B)`，不需 contour餘項常數。192-bit Arb與 10000個 exact
rational midpoint cells證
`det(B_7) in [-3.156096567895524060757e21,-2.883510345549506883157e21]`。
所以 `nu_7` 在小 t有負 density interval，T11/G63正式關閉。證書：
`experiments/certify_t11_asymptotic_obstruction.py`。勿再修補或增加 T11 moments；
此結果不是負 Toeplitz minor、不是 RH反例。

ES70補充稽核：重新下載的 arXiv:2607.16795 source tar只有 `main.tex` 與
`00README.json`，缺少正文宣稱的四個 certificate modules與 36 tests。可獨立採用其
q-Pascal純代數，但不得聲稱 Gate A/C certificates已重現；而其 `r^3/k` perturbation
本來就不進入 `k=O(r)` critical cone。

ES78/G66：Dimitrov 1311.0596 的 Lee--Yang/orthogonal-Wronskian theorem雖是 all-degree，
Leclerc identity卻把它 exact化回 Appell/Jensen與 Turán hierarchy；它是 RH等價座標，
沒有 base或 closure。正 measure/log-concavity不控制 imaginary-axis Wronskian雙積分的
旋轉相位。Lee--Yang只保留一個非循環接口：顯式 ferromagnetic measures `mu_N` 各自
已有 Lee--Yang theorem，並證 whole-law tight weak convergence到 normalized `Phi dt`。
未有此 construction前，不做 finite Wronskian batches。

G67新增一條真正 singular 的 prime boundary接口。令
`F_P=prod_(p<=P)sqrt(1-p^-1)/(1-p^-1/2 z_p)`；其 infinite-polydisk H2 norm恆 1但
weak趨 0，而 `|F_P|^2dm` 趨向對 Haar singular的 Riesz product
`mu_pr=otimes_p P_(p^-1/2)dm_p`。單 factor exact滿足
`|D_theta|log P_a=P_a-1`，沿 `theta_p=tlogp` 後正好是全部 prime powers的
von Mangoldt source。再令 `h=sqrt(P_a)`，fractional ground-state identity給
`P_a-1=2(|D|h)/h+C_a`，`C_a>=0` 且 `C_a=a^2+O(a^3)`。後續嚴格 bookkeeping修正了
一個遺漏：potential改成 ground-state square時，每個 prime另留下
`-2<H,|D|H>` kinetic debt；Weil form沒有此 kinetic項。Gamma截斷雖 exact給
`c_N+|D|log(q_N/P_P)`，再做 chain rule仍無法補它。且右半平面 Blaschke zero邊界
modulus為 1、normal derivative卻非零；用 boundary outer extension取代 actual analytic
extension會恰好偷渡 RH。故 local Bregman cancellation目標已關閉。Riesz measure仍是
有效 singular source，但下一步只接受能同時提供 kinetic storage、global Poisson
normalization與 Blaschke控制的 adelic compression/trace identity。詳見
`prime_bohr_singular_route.md`。

G68以新聯網輸入把此接口放回 semilocal operator framework。CCM 2310.18423證 finite
`S` 的 Sonin spaces皆由 `theta_S` 與 Archimedean Sonin space同構；2403.01247的 cyclic
measure `|E_S|^2dt` 中，每個 prime密度恰是 B2 Poisson/Riesz factor。但 dual norm ratio
為 `prod_p|1-p^-1/2e^(-itlogp)|^2`，故 ambient condition number exact等於
`prod_p(1+p^-1/2)/(1-p^-1/2)->infinity`。所以 stability不是 uniform common norm，
不能靠 bounded similarity把 prime-free positivity升到所有 supports。

CC 2006.13771在 support `(1/2,2)` 已嚴格證 Archimedean Weil form支配 Sonin positive
trace。下一個唯一非循環 semilocal target是：每個 q、`S_q={infinity}union{p<q}`、
每個 admissible `g` with support `[q^-1/2,q^1/2]`，直接證完整 finite-prime Weil form
支配對應 semilocal Sonin projection trace。現有 2023--2024 論文只構造 space、measure、
Jacobi/prolate candidates，沒有證此 comparison；不得把 determinate positive moment
measure本身當作 Weil positivity。詳見 B8--B9/G68。

G69再用 Burnol math/9901051 定位 local scattering符號。對 `Q_p` 的 unramified channel，
positive time delay恰是 `(logp)P_(p^-1/2)(tlogp)`，而 Weil local operator是
`(logp)I-T_p`；Tate vector是一維 odd sector，explicit formula取 supertrace。故不能把
positive local time delays直接相加當證明。B9.2若要成立，必須由 global Poisson/rational-lattice
complex先配對／quotient所有 local odd directions，再證所得 ordinary/cohomological trace正。
此處是 concrete global target，不是 local scattering theorem已完成的結論。

G70核對 2026 最新 Connes--Consani 2602.15941。該稿把 adele Riemann sector建成
rooted/metrized rank-1 divisors的 Picard monoid，adelic product成 tensor product，並把 local
explicit terms幾何化為 periodic-orbit Lefschetz trace；它確實是 G69 cross-place coupling的
載體。但 source沒有 intersection pairing、Hodge-index或 positivity theorem。下一個幾何
驗收式只能是：在 relative `(Picard monoid,generic orbit)` 上構造 degree-zero pairing，
證其 Lefschetz trace exact為完整 Weil form，再不靠 zeros證 Hodge sign。只引用 trace
interpretation不得當作完成。

G71：有限 \(S\) 的 \(\theta_S^*\eta_S=I\) 雖給出 uniform primal--dual
scaling pairing，但 Euler multipliers 正好相消，故也失去 prime Weil term；
same-side pairing 保留 primes，卻重新承受 \(\kappa(\theta_S)\to\infty\)。
這條 duality 捷徑已關閉，不可再以有限 degree certificates 迴避。

G72/B13 得到真正 all-size 結構：對每個 prime，
\[
T_{1/P_p}-T_{P_p}^{-1}=(p-1)^{-1}P_{[0,\log p]}\ge0.
\]
但其自然 trace \(\log p/(p-1)\) 對 primes 發散；B14 並顯示 gamma 與
prime time delays 在截斷 Weil source 中同為負號，沒有局部抵消。下一步只
研究 joint baseline/pole/gamma/prime renormalization 所誘導的全尺度
contraction 或 determinant theorem；否則 degree 3 僅是獨立成果。

G73/B15/ES84 核對 quasi-inner source。對任意 finite \(F\)，確有 compact
off-diagonal 與 Sonin kernel injections，是 all-\(S\) 代數升階；但投影差的
Hardy diagonal blocks exact為 \(-C_F^*C_F\) 與 \(B_F^*B_F\)。full PSD等價
於 \(C_F=0\)，即真正 inner，不能由 quasi-inner推出。injection也非等距，正好
重現 Euler condition-number distortion。下一個驗收式必須是 pole-neutral、
support-limited測試錐上的 weighted defect domination。

G74/B16--17/ES85：現有 \(m\)-prime compactness只保證 singular values
\(O(n^{-1/(2m)})\)，沒有 fixed Schatten class；標準 fixed-order regularized
determinant不能直接取 all-prime limit。Burnol 的 adelic incoming/outgoing
orthogonality則已等價於 abelian RH，co-Poisson functional equation不自動給
causality。因此只保留可先證的 support-by-support contraction。

G75/B18修正 G72：「不可求和」不等於沒有 canonical renormalization。若
\(A(q)=\sum_{p\le q}(p-1)^{-1}\)，則
\(K_q-A(q)I\), \(K_q=\sum_{p\le q}(p-1)^{-1}P_{[0,\log p]}\),
在每個 compact time-support上 exact穩定為
\(-M_{\sum_{p<e^x}(p-1)^{-1}}\)。這是 all-prime operator lemma，但 limit為
負 prime staircase（漸近 \(-\log x-C_p\)），不是 positivity。下一步直接比較
gamma/pole residual與此 potential，不再處理 raw divergent prime sum。

G76/B19 隨即關閉最直接的 domination：令
\(\phi=(\partial_x^2-1/4)\psi\), \(\psi\in C_c^\infty(0,1)\)，即可 exact滿足
兩個 pole constraints。平移 \(\phi_R\) 不改 fixed gamma multiplier energy，
但 G75 prime staircase energy至少以 \(A(e^R)\|\phi\|^2\) 發散。因此 fixed
Archimedean storage + pole evaluations不能支配 renormalized local defects。
這只關閉 separated-place proof，不否證 RH；下一步必須是會隨 \(F\) 成長的真正
Poisson/Sonin cross-place term，否則轉 Suzuki causal endpoint。

G77/B20提供 all-\(S\) unweighted block identity。若
\(D_F=V_F|D_F|\)，則 positive defect exact分成 Sonin projection
\(P_{\ker D_F}\) 加 \(E_F\)，negative compact defect exact是
\(P_{\ker D_F^*}+V_FE_FV_F^*\)。非-Sonin defect spectra確由 polar map配對。
但 actual scaling weight不與 Hardy projection交換，cross blocks不可省略；先前單一
polar-commutator target已撤回。

正確 G78/B21 介面為
\[
\operatorname{Tr}(M_f^*(U_F^*PU_F-P)M_f)=\mathcal J(u_Ff)-\mathcal J(f),
\quad
\mathcal J(f)=\|PM_f(1-P)\|_2^2-\|(1-P)M_fP\|_2^2.
\]
Connes--Consani local-sum convention要求此差在 pole-neutral support cone上 \(\le0\)。
這只是 trace monotonicity，不能升成 operator PSD；operator sign等價 innerness，過強。
generic quasi-inner與兩個 constraints亦不夠，下一步必須使用 actual semilocal Poisson product。

G79/B22把 G78轉成 time-domain exact式。若 \(f=\mathcal Fh\)，則
\(\mathcal J(f)=(2\pi)^{-1}\int x|h(x)|^2dx\)，故所需只是 semilocal scattering
\(S_F\) 在 pole-neutral、support-limited \(h\) 上不增加第一 moment。相位式為
\(-(2\pi)^{-1}\int\theta_F'(t)|f(t)|^2dt\)。這是 nudge要求的 trace spectral
average層級，不是 operator positivity。B23再把 pole-neutral cone寫成
`PW_x` 中 `exp(+-y/2)` 的顯式 codimension-2 orthogonal complement；Gram matrix
為 `[[2sinh x,2x],[2x,2sinh x]]`。B24直接展開 actual finite Euler phase（不再
含糊稱 q-rough sum），得到 prime-power autocorrelation，並用 constraints精確消去
連續 endpoint densities；剩餘 measure是 `dpsi(t)-dt-dt/t`。下一步應尋找此
signed discrepancy加 archimedean項在 B23 compression上的 all-support
inertia/Schur-complement或正性定理；完整 causality與 universal spacing-only
Hilbert bound都不可當輸入。

B25把 uniform target精確成 constrained inertia theorem。若 unrestricted
A_(F,x) 可逆，則
nu_-(A)=nu_-(A|ker L)+nu_-(L A^-1 L*)；因此證 nu_-(A)=2 且 2-by-2
Weyl matrix負定即可一次完成該 support。一般 Krein--Langer定理要求事先有
Nevanlinna/finite-negative-square性，不能直接套 Xi endpoint。Laplace audit又證
B24 centered measure加 exact gamma transform就是 -xi'/xi，故下一步只能找
不預設 inner/HB 的 arithmetic index proof。

B26補正與 Suzuki 2606.09096 的字典：localized Q_W^x 等於 B25 ambient phase
form加 2 Re(E_+ conjugate(E_-))；這是 indefinite rank-two pole form，僅在 B23
constraint cone消失。Suzuki的 self-adjointness、lower bound存在與 bottom連續性
均不給 sign；原文亦證 RH假時某個 support bottom<0。

B27--B30完成 B25 的策略稽核。pole-removed phase form exact為
`A_x=E_x-kappa_x I`，`E_x` 是 arch continuous jump與有限 prime jumps組成的
irreducible Dirichlet form；故任意 support上只有基態 simple/positive。真正 index
義務是 `#{mu_j(E_x)<kappa_x}=2`，這是逐譜命題，不能以 zero-density／平均抵消代替。
兩個 pole moments雖嚴格迫使至少兩次 sign changes，仍沒有 higher-mode oscillation或
2-by-2 resolvent sign。arch-only模型的 threshold下 eigenvalue數隨 support無界，
證明 Dirichlet＋codimension two不夠。Schoenberg transform又解析排除 natural jump
semigroup為 PF-infinity：reciprocal Laplace transform在半整數格有 essential
singularities。下一步只接受 Xi-specific non-translation oscillation／arithmetic
resolvent bound；若無，B25即只是另一個RH-equivalent reformulation，應轉回非等變
theta Green/Rellich boundary cancellation。degree-3仍僅獨立成果，不恢復有限證書。

B43--B44接續非等變 theta Green/Rellich 路徑。BFI arXiv:1112.3444 在其自身
signature `(2,1)` theta setting的 exact current equation把 bulk積分寫成 geodesic period減
`(4pi)^-1 int(Delta f)eta`；split geodesic還有兩個 cusp boundary integrals，
其 hard asymptotic含任意 cusp constants與負 Fourier coefficients。零特徵值
regularization另依賴 spectral deformation的 `B'_ell(1)`。故這是可用模板但不是
K0介面或正性定理。又 `int Delta F=0` 證明非零 compactly-supported `F` 不可能同時
`-Delta F>=0` 與 boundary flux消失。live target收緊為：構造 canonical
`h -> F_h`，使完整 K0 form exact等於 bulk+period+cusp全部項，並把總和配成平方；
任何 period平均或刪除 boundary後的 pointwise定號均不合格。source已存
`external_inputs/bruinier_1112/BIFfinal.tex`，記 G87--G88/ES90。

K0B45再核對 Kudla--Millson/Mathai--Quillen方向。KM form確是 special cycle的
canonical Thom form，但 full modular curve `X(1)` genus zero，故
`S_2(SL_2(Z))=H^1_(2)=0`；closed geodesic沒有非零 harmonic class可套 Hodge norm，
split geodesic則必須保留 cusp boundary。這排除 naive cohomological positivity，
卻保留 analytic transgression coercivity：需把 BFI primitive、cusp flux與 K0 cone
cutoff的完整 pairing逐 test配平方。記 G89/ES91；RH仍未證，goal保持 active。

重要更正 K0B46：BFI/KM kernel不等於 K0B39 kernel。前者是 trace-zero matrices上的
三維 adjoint/`Sym^2` theta，後者是 standard `R^2` Epstein theta；
`Hom_SL2(Std,Sym^2 Std)=0`。Veronese `(m,n)->[m^2,2mn,n^2]` 非線性、只落
discriminant-zero cone，且把 majorant拉成 quartic。K0 rectangular geodesic亦是
base variable orbit，不是 BFI index cycle。因此 BFI current目前只是嚴格模板，
不是 exact K0 bridge。live prerequisite改為 stress+cone cutoff後的明確
intertwining/transmutation theorem，或直接為 Epstein theta構造 current identity；
記 G90/ES92。

K0B47--48改走真正匹配的 incomplete-Eisenstein 理論。unfolding證 K0 `Theta_*`
與所有 cusp forms正交，Mellin channel只有 `zeta(2w)E(z,w)`；其 scattering
coefficient是 `zeta^*(2w-1)/zeta^*(2w)`。所以 direct Epstein Green route精確回到
Suzuki/Burnol scattering endpoint。Maass--Selberg truncated norm的 positivity
含 divergent `log T` baseline；扣除後的 scattering finite part與 boundary Hankel
terms無自動符號。live target是 pole-neutral cone上把 **renormalized finite part加
全部 boundary** 配平方，不能從 unrenormalized norm推論。記 G91/ES93。

B31再把量詞降到精確最低需求。對 scattering unitary `S` 與半線投影 `P_R`，
`D_h(R)=||P_RSh||^2-||P_Rh||^2` 滿足
`int D_h(R)dR=int x(|h|^2-|Sh|^2)dx`。故只需在兩個moment cone上證 defect的
**面積**非負；不需逐 `R` 非負或 operator causality。下一步應尋找 integrated
Maass--Selberg flux square／boundary cancellation，而非把問題升成 innerness。
記 G92。

依最新 Selberg nudge補 B32：單一 defect面積只是均值；真正充分命題是對每個 support
`x` 與每個 compact pole-neutral `h` 都有面積非負。autocorrelation support使 omitted
prime powers exact不貢獻，故這已是完整 Weil form。若存在 off-line zero，其 reflection
orbit給 `[[0,m],[m,0]]` 的負方向；W14 polynomial-Gaussian隔離後，再用 smooth cutoff
與兩個 fixed bumps（B23 Gram可逆）精確修正成 compact pole-neutral test，Weil form
連續性保留負值。因此 all-support B31 area positivity逐零點等價 RH；live缺口只剩
從 arithmetic side證該 area sign，記 G93。

B33/ES94稽核 canonical-system Szego sum rules。Arov-gauge identity
`I(w)=int(tr A-2sqrt(det A))>=0` 是真 uniform coefficient square，但預設 `w`
holomorphic Schur並由此得到 `A>=0`。Riemann scattering quotient的 zeta zeros正是
meromorphic poles；證 shifted quotient到 endpoint皆Schur就是 Suzuki/HB缺口。
直接取 physical-line pure phase又使 entropy發散。加入 transmission channel不唯一，
其 modulus entropy也不等於 B31 phase-delay area。故此路只在能由 arithmetic獨立
構造 canonical positive transmission system並證 exact adjoint identity時重開，記 G94。

B34/G95/ES95繼續稽核 Connes--Consani 的 semilocal提案。其 archimedean
`Q`-form的 `-2I+K` (`K` Hilbert--Schmidt) 只能在無質數時把例外壓成
有限維。一旦 `log n<2x`，Euler quadratic form是 compressed translations；
modulo-shift fibre是 finite path adjacency，其 eigenvalues因連續 base fibre而有
infinite multiplicity。這個 essential spectrum在兩個 pole conditions或任意有限餘維
restriction後仍存在。經 `Q` 還會出現 shifted derivative energies，更不是
`L2` 上的 compact error。故不可把 primes附加到 archimedean `K`或再加
有限 constraints；live target改為直接構造含所有 active prime shifts的
noncompact principal semilocal operator，並 uniform-in-support 證 pole-neutral compression的
sign。這是 B32.2/RH-scale，不可以 finite matrices或更多 VERIFIED batches取代。

聯網後取得 Suzuki arXiv:2301.00421 原始 TeX，新增 B35/G96/ES96。
Suzuki 的 `mathfrak S_t in L2(R)` 具有無零點的 prime--gamma--Lerch 顯式公式；
若 `pi^-1<S_t,S_u>` exact等於 Riemann screw kernel，即得全支撐 Weil form的
Gram square與 RH。這是一個真正 uniform-in-support/all-degree integrated-flux
feature map，比再找 finite certificate合格。但原文只在 RH 下證 isometry，
converse又證該身分即推出 RH。精確原因是：`L2` 端 feature vectors給 PSD Gram，
off-line conjugate zero orbit的 Weil pairing卻是 `[[0,1],[1,0]]`。只在
`Theta=(A-iA')/(A+iA')` inner/HB（即 RH-facing condition）時 model kernels才
orthonormal。所以 live theorem現可收窄為：直接從 `mathfrak S_t` 無零點公式證
arithmetic coisometry/optical identity，並處理所有 nonreal-pole residues；不可預設
model-space Parseval。

B36/G97/ES97再以 indefinite Hermite--Biehler/Krein--Langer 理論量化該 residues。
`q=-A'/A`, `A(z)=xi(1/2-iz)` 的 generalized Nevanlinna kernel與 `E=A+iA'`
的 de Branges kernel同指數；每個上半平面 nonreal zero是 `q` 的 pole並提供
Pontryagin negative square。finite off-line set時 index計總重數，infinite時有限子核
負指數無界。所以 B35 的輸出可再收窄成「從算術資料證此 index=0」；
general Pontryagin theory只計數缺口，不消去它。任何積分路徑若默認上半平面
無 poles，就是丟掉正要排除的負方向。

B37/G98/ES98給 finite-index負方向的 exact all-degree分解。Krein--Langer
將 `Theta` 寫成 `Theta_0/B`，並給
`K_Theta=(K_(Theta_0)-K_B)/(B overline B)`；`K_B` rank即 Pontryagin index。
故下一個最小命題是從算術公式證 Blaschke denominator `B=1`。critical-line
modulus one、boundary antiunitarity或一般 model-space square都無法區分
`Theta_0` 與 `Theta_0/B`；若不顯式保留 `-K_B`，就是預設 index zero。

最新 Selberg nudge要求檢查 prime--Poisson 是否給計數以外約束。B38/G99/ES99
給 exact否定（對一般線性結構）：`Xi_a(s)=xi(s+a)xi(s-a)` 具 centered
functional equation、conjugation、完整 Poisson formula與嚴格正 prime weights
`Lambda(n)(n^a+n^-a)`，卻把無限多已知 critical zeros移到
`1/2+-a`，故 Pontryagin index無界。這證明只有一個新方向合格：
找不對 products additive的 nonlinear **single degree-one/gamma channel** identity，並用
Ramanujan-size local data。degree-one Selberg classification只把函數辨識為 zeta/Dirichlet L，
不證 GRH，故不補 index-zero。

其後把 single-degree-one條件做成 B39/G100/ES100 的 exact audit。單 Euler
factor的 log coefficients `alpha_p^k` 具有 local Hankel rank one，而 B38 shifted
product的 adjacent minors嚴格為 `(p^a-p^-a)^2`，所以確實排除舊反例。但 real
primitive Dirichlet L-functions也滿足 rank one、Ramanujan、單 gamma與 centered FE；
任何一般 rank-to-index theorem都會直接證 Dirichlet GRH。現有 classification沒有
這一步。合格機制須額外使用 conductor one及 `alpha_p=1` 的跨質數 nonlinear
coupling，exact導出 Suzuki coisometry；local minors不是 uniform升階。

B40/G101/ES101新增不刷 degree 的 scalar全域目標。BSY exact把 weighted
critical-line `log|zeta|` integral寫成所有右半臨界帶 zeros的正 Blaschke mass；若能
證 integral `<=0` 即得 RH。但 factorization在 `s=1` 只顯示 normalized pole由
`exp(Omega)` 與 `exp(-Omega)`相消，Euler product不迫使 mass為零。hybrid
Euler--Hadamard亦保留 zero factor。Jensen branch的唯一新 proof obligation是
Riemann-specific nonlinear prime/gamma inequality B40.3；再列等價準則不算完成。

B41/G102/ES102再將這條 scalar branch 與既有 Nyman route exact合併。Burnol證
`||P_N1||=exp(-Omega_zeta)`，故最佳 Nyman距離
`d^2=1-exp(-2Omega_zeta)`。因此 B40.3、NB11 uniform mollifier與 Blaschke/causal
defect消失是同一 obligation，不是三個獨立方向。finite projections或 truncated
products不能證極限為零／一；Burnol adelic causality本身又等價 abelian GRH。
下一步仍只接受新的 conductor-one nonlinear estimate，輸出 B35 coisometry或等價地
使上述共同 defect exact為零。

B42/G103/ES103再把 degree-one nonlinear結構提升到完整 local scattering kernel。
exact有 `u_p=b_(p^-1/2)(e^(izlogp))/e^(izlogp)`；分母 exponential singular inner
的 model space是無限維 time-interval reservoir。finite `S` 時
`K_(u_S)=(K_(N_S)-K_(D_S))/(D_S overline D_S)`，且 numerator/denominator coprime，
所以每個 finite-prime quotient已帶 infinite negative squares。這不是 off-line zero
index，而是 global completion前必須消去的 noncompact principal baseline。

live theorem因而具體化：由 rational-lattice Poisson map構造 compatible partial
isometry `K_(D_S) -> K_(N_S) direct-sum H_(infinity,pole)`，使其 defect exact等於
B32/B35 all-support form並證 residual cokernel為零。local inclusion明確為假，
只能 cross-place完成；若成功即 Suzuki coisometry/RH。

Selberg nudge指出 B42.5 若沒有可算 expression便不可證偽。B43/G104/ES104 已修正：
local Laurent expansion只有一個 anti-causal shift，並在完整 `L2(0,logp)` reservoir
上 exact給 `H_p^*H_p=p^-1I`、`J_p^*J_p=(1-p^-1)I`。Bohr tensor product的
mass為 `prod_(p in S)(1-p^-1)`，其 collapse與 B1 相同。

後續不得再只寫 abstract coisometry。下一式是用 finite completed multiplier `U_S`
明算 `H_S=P_-M_(U_S)|K_(D_S)`，再找顯式 zero-independent Poisson diagonal
recovery kernel `R_S`，使 `H_S^*H_S-R_S^*R_S` exact等於 B32 integrated defect
並 uniform定號。現成 primal--dual map消去 primes；same-side map condition number
發散，皆未完成。

B44--B45/G105/ES105已把 B43.5真正算出。finite-S負頻率唯一為 `-log(d/n)`，
係數 `C_S mu(d)sqrt(d)/(phi(d)sqrt(n))`，故 prime leakage是 finite
Mobius--Volterra operator。arch kernel exact為 `2e^(a/2)cos(2pi e^a)`；completed
kernel是它與 Laurent measures的 convolution，Hankel kernel即 `q_S(-x-y)`。

natural recovery audit為否：Möbius signs把 uniform cancellation帶回 NB11；Tate
primal--dual map擦除 primes，same-side map norm distortion發散。故本分支暫停，
除非先寫出不同的 explicit `R_S` kernel並逐式證 B43.6；不再保留 unspecified
cross-place coupling作假 live route。

最後重驗 Suzuki 2606.09096 原始 TeX 的 EQ102/EQ112：無條件部分止於 finite-a
self-adjoint extensions與 real zeros；`lambda=0` 極限動機明確在 `Under RH` 段落，
strong-resolvent／characteristic limit仍只 expected。target `z^2xi/xi'` 又需
meromorphic compact topology。故維持 K0B42 audit，不因 2026 摘要措辭而誤判已取得
index-zero外部輸入。

另檢查 finite Weil dictionary 的 strict-Carlson可能縫隙。W7/G106/ES106證 pole
source本身在 frequency endpoint `omega=1` 有非零 density，沿虛軸成長
`e^(2pi Y)/Y`，故完整 source exponential type恰為 `2pi`。compact support／prime
cutoff沒有 type slack；`sin^2(pi z)h(z)` 又在全部 integer Hermite data已為零，
pole-neutral restriction也看不見。故 single boundary phase不能靠 Carlson唯一性升成
continuous Pick positivity；all phases仍是 full Weil/RH endpoint。

最新 Selberg nudge的 `cosh(n lambda)` 觀察已對應到 L5/D6 dominant-shell theorem：
on-line contributions不能抵消 off-line exponential base；finite maximal shell又可同時
相位逼近，必產生 negative exponential Li subsequence。故 Li 路的唯一缺口仍是從
D10.3 arithmetic Laguerre integral證負部次指數，不是再處理全體 zeros cancellation。

2026-08-16 又將此 dominant-shell 結論強化為 `li_syndetic_excursions.md`
LS1--LS3：最大殼層相位在緊軌道閉包返回單位元鄰域的時間集是 syndetic，
而 L5 餘項估計對所有大 n 一致，故 RH 假時每個固定長度的大區塊都有
`E_n<=-cR^n`。於是 D10 不必逐 n 證單側次指數界；只要對每個 epsilon
證 `{n:E_n<-exp(epsilon n)}` density zero，或證存在任意長且任意靠後的
好 block，即足以推出 RH。這是實質較弱的新算術驗收格式；目前仍沒有從
prime--Laguerre 結構閉合它，故不得記成 RH 證明。

聯網後優先稽核 X.-J. Li arXiv:0807.0090v10 的完整 RH聲稱，結果見
`li_semilocal_trace_audit.md`/G107/ES107。致命斷點很具體：在
`C_S=J_S/O_S^*` 上，對 `gamma in O_S^*` 的 `x->x/gamma` 是 identity，不能
用來移除 additive phase中的 gamma；若 x指 fundamental-domain代表，則變換離開
該域。故 (4.13)->(4.14) 與 (5.8)->(5.9) 無效，兩個「same number infinitely
many times」零化不成立。Lemma 5.1 的 convolution positivity可保留，但 remainder
orbit sum仍是完整 semilocal prime--Poisson sign，沒有證明 RH。

同時由 Neeb--Olafsson reflection-positive dilation得到 W19：W10 box measure確有
all-size OS dilation，卻只把 Laplace參數的 `s+t` 轉成 `|s-t|`。prime-power endpoint
measure exact為 positive cell bulk的 distributional derivative加 `delta_0` boundary
(W19.2)；所以 endpoint提取重帶符號並回到 W16。不得再把一般 OS dilation當作
Selberg `a+b -> a-b` bridge；只有 completed endpoint derivative的 sharp sign才是新輸入。

Li audit又有 exact route identification：single-prime unit weights依 orbit exponent為
`1,-1/(p-1),0`；乘 critical Jacobian及 `1-p^-1` 後正好成 B43 的 Laurent
symbol `-p^-1/2 w^-1+(1-p^-1)sum_(k>=0)p^(-k/2)w^k`。因此修正 quotient
錯誤後，Li semilocal route精確回到 B43--B45 的 Hankel leakage與
Möbius--Volterra cross-place sign，不能計作新的獨立成功機率。

最新 Selberg nudge要求避免 derivative還原，留在 Laplace正性。已新增
`cauchy_spectral_divisibility_route.md`/G108/ES108：無條件 Herglotz boundary
measure `mu_1` 位於 `Re s=1`，RH exact等價 `mu_1=P_(1/2)*nu` with `nu>=0`。
若有 off-line `beta>1/2`，`P_(1-beta)` 的 pole落在 half-strip內且正 residue不可消；
反之 RH時 `nu` 是 zero ordinates counting measure。新 live theorem是由 conductor-one
Euler data證 half-Cauchy divisibility（或相容的 epsilon-regularized factorization），
不是再微分 bulk。generic backward Poisson不保正，local inverse仍是 B43 leakage，
所以此時是精確 uniform target，尚非證明。

隨後 CS5/G109 完成同一性稽核：regularized inverse Cauchy measure不依
`epsilon`，其 Fourier transform就是 zero counting spectrum，也即 distributional
`Psi''`。故 CS2並未把 full Weil positivity降階。另將 prime sum exact改寫成
`A(x)=x-psi(x)` 的正三角 kernel積分 CS5.6；但 `A` 不定號，而無條件 PNT error
只重現 Suzuki 原有 `exp(t/2-c sqrt(t))` 上界。下一個 live obligation是能利用
conductor-one跨質數結構的 oscillatory cancellation／直接 Bochner正定性；不得以
absolute Chebyshev bound、finite moments或更多 finite matrices冒充。

聯網後的新主線是 Freedman arXiv:2606.29555 的 coordinate Weyl kernel。已下載原稿
及 157MB companion source，並在 `weyl_debranges_derivative_bridge.md` 證明 exact
WD1--WD3：`K_omega=partial_omega J_omega` 且
`partial_omega D_omega=(4/pi) F K_omega F*`。因此若能真正證
`K_omega>=0` for all `0<omega<1/2`，從 `D_0=0` 積分便排除所有非實 Xi zeros。
這是合格的 all-degree bridge；不得用單一 omega或有限矩陣替代。

companion證書則已否決，詳見 `freedman_weyl_positivity_audit.md`/G110/ES110。
它從 lifted `|kappa|<=1` 跳到 compressed `||CKE||<=1`；一般二維例已直接反駁
該推論。Euler/boundary檔把 `B=Q=P-M` 當新 identity，且未證 indefinite fiber
minimizer存在；continuum closure又 hard-code True。後續 Boolean theorem ledgers
全依賴此缺口。下一步只攻 concrete compression的特殊 intertwining/range identity，
或直接 factor `K_omega`；若做不到，將此 route記為新的 RH-equivalent sharp target，
不能宣稱外部 proof已閉合。

WD5又給難度下界：`partial_omega D_omega(x,x)` exact是 Xi 在
`x+iomega` 的 complex Laguerre expression除以 pi，也等於 `K_omega` 的 plane-wave
quadratic form。Csordas 1309.0055只由 Phi strict log-concavity推出 associated
correlation kernels為 admissible；其全部 n 正定 iff RH，且最簡單 real L1仍是
open problem。故不可用既知 log-concavity、unimodality或有限 Turan證書填補 G110。
若續攻 direct Gram，必須新增一個超越這些性質的全 configuration identity。

FW6給下一式：真正需要
`E^*(C^*C-KC^*CK)E>=0`，或等價地在 plus-profile range構造 Douglas contraction
`T` 使 `CKE=TCE`。K不保持 ker C，因兩個 equal-mass bumps經 nonconstant kappa
加權後不再零，故一般 quotient/compression theorem不能用。只能利用 special theta
image證 range factorization；不得再以 Q-minimizer定義 E，因那已假定 signed form
有下界。NE1有限掃描與正性相容，但只屬數值 sanity check。

WD6另有解析 no-go：`phi=e^-t²(1+0.1cos t)` 滿足正、偶、strict decreasing、
super-Gaussian及 `(log phi)''<=-17/9`，但 Fourier transform的 cosh bracket有顯式
非實 zeros。因此 generic strict-log-concave/admissible theorem不可能證 Weyl PSD。
Riemann route只剩 modular theta-mode coupling；若候選 lemma未使用該耦合，就已被
WD6反例排除。

WD7現已證完整結構 equivalence。若 f為 LP，則 vertical shifts的 quotient是 Schur
multiplier，`H(f(.+iomega))` 隨 omega contractively nested；kernel monotonicity與
WD2 Fourier inversion給 `K_omega>=0`。反向是 WD3 zero exclusion。因此對 Xi：
uniform small-omega Freedman kernel PSD iff RH。這確實回答了 degree-3之後的
uniform-in-degree結構問題，但沒有提供 arithmetic sign；FW6 Douglas contraction若
被證出就已等同完整 RH，不能再稱作 technical closure。

最新 TPD/G114 已回答 modular nudge 的具體機制。Weyl form可 exact square-complete
為 `q_(sigma,+)=(1+t)e^(sigma omega t)Phi(t)` 與
`q_(sigma,-)=(1-t)e^(sigma omega t)Phi(t)` 的半軸 Hankel norm差；Poisson偶性只把
minus profile反射成 opposite plus profile並交換正負輸出半軸。`omega=0` 時其
Fourier ratio為 `(Xi+iXi')/(Xi-iXi')=E#/E`：實軸 modulus 1 無條件。若升格成
full-Hardy invariance，缺口就是 Hermite--Biehler／RH；實際 FW6只要求 special
`Ran(A_0^+)`，但那正是 K0 positivity，VK6亦已證等價 RH。故 naive
Poisson-compression已稽核關閉。下一步只接受真正 lattice-level special-range
intertwiner，或外部文獻中不預設 real zeros 的 theta-specific inner theorem；不得
再把 modular reflection、full-line unitarity或 finite Galerkin norm當 closure。

外部交叉核對 ES113：Connes--Consani 1910.14368 的一般投影引理已證 half-space
sign iff inner，且其 Poisson/semi-local續攻仍停在 Conjecture 4.1；Suzuki
1204.1827 Prop.1.2 把 shifted-xi innerness直接等價 zero-free region，無條件
canonical system只建於 `omega>1`。故目前沒有可下載搬用的 theorem 補 G114；
這兩篇證明 full-Hardy 的「unitary + projection」所省略的是 inner causality；
special range版本則仍由 K0B3辨識為 RH級正性，不能混用兩個量詞。

TPD7/G115再把 lattice-level版本具體否決到一個 operator：
`J(D_u^2+D_u)J^-1=d_t^2-1/4` 確認 Sonine微分與 Xi theta kernel完全接軌；但
Dirac-comb sampling `C f=sum_n f(n)` 在 L2、甚至 `f(0)=hat f(0)=0` 子空間上都
不 bounded（零積分互斥 bumps給 `|Cf_N|~sqrt N`）。所以 Poisson unitary不能經
sampling自動下推 Douglas contraction。下一步若續此支，只能證 C 在 concrete
Gaussian-dilation/theta image上的 uniform frame inequality，並把其 norm defect
exact辨識成 K0；一般 Sonine support、兩 moments或 ambient unitarity不再計分。

TPD8/G116已把上述「uniform frame」本身關閉：Mellin transform顯示 differentiated
Gaussian dilation orbit為 cyclic，而 comb sampling的 Riesz symbol就是
`zeta(1/2-it)`。若它在 ambient L2有 uniform bound，便迫使 critical-line zeta
屬 L2，違反經典 mean square `~TlogT`。所以 lattice方向不能再尋找單邊 bounded
sampling；只可能證兩個 sampling defects在支撐依賴 counterterm後的差有正號。
這與 B21--B32 restricted mean-delay／integrated Maass--Selberg完全合流。

ES114又排除最新 Laguerre題名造成的假入口：近期結果分別只處理 Xi係數的大-index
fixed order、足夠高 derivative/shift，或 Phi kernel的 TP2 log-concavity；沒有證
Xi 本身的全實軸第一 Laguerre inequality，也沒有 scalar-to-matrix升階。故下一步
仍應留在 renormalized defect difference，而非重開 coefficient/TP2路線。

最新 DU/G117 回答 Selberg nudge：三條 defect路徑確實是同一義務。Xi Bezoutian
canonical-product展開，加 K0B2/TPD2，將 TPD plus-minus Hankel norm差 exact化為
Weil zero pairing在 resolvent tests上的值；B21--B22--B31則是同一 pairing在 compact
pole-neutral Paley--Wiener tests上的 leakage/mean-delay/layer-cake三種座標。不要再把
它們列為獨立路徑或相互佐證。唯一 live theorem是把 **完整 renormalized** B31 area
連全部 boundary terms factor成平方；只換成 Maass--Selberg積分、未減 norm或 full
causality都不算新輸入。

DU6/G118另關閉看似最短的 pole-factor平方：兩 moments exact等價
`h=(-d^2+1/4)g` 且 g保留相同 compact support，但 Fourier乘子
`z^2+1/4` 只對每個 zero orbit作 invertible congruence，off-line負方向毫無減少；
算術側則變成 shifted derivative cross-energies。不得再把 pole-neutrality當普通
二階 Poincare coercivity；真正 square仍須耦合全部 prime shifts與 archimedean term。

最新 PT/G119/ES115 已稽核 Barnes--Thorin 外部輸入。folded zero measure的
Stieltjes/Hankel/Jacobi positivity確是一次涵蓋所有 degree 的 uniform結構，但 measure
為正實本身等價 RH，與 DU master pairing不是獨立正性來源。Polson
arXiv:1804.10043v8 的 claimed closure有可定位硬錯：式 (30)/(31)不成立，且其
`U_star` 含 Thorin atom `3/4`，故 `E exp(H_star)=infinity`，Theorem 25 的
parameter-1 tilt不可能。後來 SSRN 6992163 也把此處改列 open RH clause；6992161
說明 theta sum不保 atomwise HCM。下一步只接受 arithmetic side 對 folded log
derivative的直接 Stieltjes representation，不能用 positive characteristic function、
integer-square clocks或 finite secondary-zeta minors替代。

PT2 又定位更早的核心符號錯誤：v8 式 (24) 的 centred linear factor應帶負號，
所以真正 Levy distribution 是 `prime atoms - e^x dx + Gamma`。論文把 pole
counterterm誤列正 measure才得以用 Tonelli。任何修補都必須直接證這個 **signed
combined** sine-square transform非負；那正是 G117 renormalized prime--pole defect，
不可再拆項宣稱 GGC closure。

ES116/G120 又把「Phi自身全正」從候選中刪除。Michałowski
arXiv:2602.20313v2 的 actual-kernel 5x5 Toeplitz負 minor已由本地 Arb 320-bit ball
arithmetic重驗：theta tail有 `<1e-70` 解析界，Arb matrix determinant與120-term
Leibniz展開皆嚴格負。故 degree 3 沒有通往 raw PF-infinity的升階機制，實際 Phi
在 degree 5 已反例。此結果只關閉 ordinary translation total positivity；不得誤稱
它反駁 RH或 K0/Bezoutian/Weyl positivity。詳見 `phi_pf5_audit.md`。

TOI/G121/ES117 再收斂 Thorin義務。corrected signed sine-square transform並非未知
sign：它 exact是 `log(xi(a)/|xi(a+it)|)`，Williams--Ostrovsky Mellin tilt已無條件
證非負。未知的是 analytic reconstruction中的 Blaschke inner factor；boundary
modulus看不見 off-line zeros。故不要再攻 scalar modulus positivity。下一步必須
給含 phase與 cut-plane continuation的 renormalized Stieltjes identity，或 full G117
square直接迫使 inner factor trivial；這與 TPD4 inner-causality是同一缺口。

TOI5/G122 已把 inner缺口顯式成 Poisson phase bumps：每個
`rho=1/2+a+i gamma`, `a>0` 在 boundary derivative留下
`-2a/(a^2+(t-gamma)^2)`（連同 conjugate bump），而 modulus/Thorin scalar density
完全看不見。下一個合格輸出必須從 prime+archimedean phase證沒有這些 smooth bumps；
只證 characteristic positivity、GGC、log symmetry、log-concavity或 finite/raw PF
皆已被反例或G120排除。

最新 OB/G123 回應 outer-budget nudge。`rho_(1/2)` 的奇偶階梯給 exact
`d^2<=1-log 2`，Burnol 公式遂給
`Omega_zeta<=C_0=-(1/2)log(log 2)`；BSY 單零點質量下界再推出
`N_off(delta;T<=|gamma|<=2T)<=C_0(4T^2+1)/delta`（按重數）。這是嚴格解析
上界但只有 `O(T^2/delta)`，不能排除零點；改善有限 Nyman 近似只改善常數，令預算
為零即 RH。詳見 `outer_budget_zero_density.md`。後續若用 Li 局部化，必須提供
cancellation-free uniform 正核；不得以更多有限係數計算替代。

最新 AP/G124/ES118--119 是聯網後恢復的 phase-sensitive 算術支線。Suzuki
arXiv:2411.07436v3 證 RH 等價於
`g_0(t)=sum_(n<=e^t)Lambda(n)n^(-1/2)(t-log n)-4(e^(t/2)+e^(-t/2)-2)`
最終非正。已自行導出 `g_0''=prime atoms-(e^(t/2)+e^(-t/2))dt` 與
Laplace transform `-z^(-2)d_s log[s(s-1)zeta(s)]`。它看得見離線 zero 的 growing
phase oscillation，且不是逐 degree 證書；因此列為 live target。

但目前沒有 closure：PNT absolute error遠大於 logarithmic sign margin，`Lambda>=0`
方向相反，分開估 prime powers會失去 cancellation；Freitas generalized Li recurrence
沒有從 `tau>=2` 向 `tau=1` 的保正原理，Suzuki Li-norm equality先假定 inner/model-space
正交性。下一步只嘗試由 `Lambda*1=log` 建正 kernel renewal／完整平方，或證 prime
log-measure相對 pole density的二階 cumulative domination。詳見
`arithmetic_phase_sign_audit.md`。

AP6/G125 已立即稽核並關閉最自然的 `Lambda*1=log` recovery。令 `H=-g_0`，與
`eta=sum m^(-1/2)delta_(log m)` 正卷積；雖 prime powers 化為全整數顯式和，但
Laplace multiplier是 `zeta(s)`，恰好消掉 Hhat 在每個 nontrivial zero 的 pole。
Euler--Maclaurin 給 `H*eta=4(1+gamma_0)e^(t/2)+O(t)`，其正號只是 `s=1`
counting pole slack。非平凡正 measure亦不可能有正卷積逆（support-sum證明）。
所以不得再用此 renewal/Möbius反演；續 AP 只能直接 factor AP2.2，或找 transform
在 critical strip無零且對 restricted defect有 sign-reflection theorem 的 kernel。

AP7/G126 給一個未被 G125 否決的 minimal family。對 `H=-g_0` 與
`kappa_a=e^(-at)1_(t>=0)`，multiplier `(z+a)^(-1)` 無零，故 Landau argument證
`kappa_a*H` eventual非負仍等價 RH。算術式中 prime weight為
`phi_a(v)=v/a-(1-e^(-av))/a^2`，baseline亦已 closed form。它保留所有 zero poles，
但目前 PNT absolute error仍壓過 sign margin，沒有 one-sided theorem。詳見 AP7；
下一步應聯網／推導能直接證 AP7.3 的正 Tauberian inequality，而非做有限 t 批次。

OB4/G127 證明 outer 支的高度平方損失不可優化：`u=-log|B|` 從 `s=1` 傳到
`1+iT` 的 sharp Harnack factor是 `(sqrt(1+T^2)+|T|)^2~4T^2`，單一接近 critical
line且高度 T 的 hypothetical zero即飽和。故不得再從同一 `Omega_zeta` 微調切片；
若續 outer，必須建 shifted Nyman/evaluation local budget family，否則主攻 AP7 phase sign。

AP8/G128 回應最新 Selberg lens。單一 off-line quartet `q=a+i gamma` 對 `g_0` 的
exact項為 `-4Re(cosh(qt)/q^2)`，正峰主振幅 `2e^(at)/(a^2+gamma^2)`。若最大水平
距離 A由有限 edge zeros取到且有 horizontal gap，總 edge項是非零 mean-zero trig
polynomial乘 `e^(At)`，必有無界正負 excursions，故有限聚合不能永久抵消。

真正未閉合的是 `sup a` 不取到或無限 zeros逼近 edge；BSY的 `sum a/gamma^2`
允許此配置。下一步只接受 edge-free spectrum 的 uniform oscillation lower bound，
並須能和 AP7 prime-side inequality接合；不得再只算單 quartet。

上述 AP8 caveat現已由外部 theorem關閉。Radziejewski 的 weakly-bounded Mellin
oscillation theorem可套到 `f(x)=g_0(log x)`：每個 `q=rho-1/2=a+i gamma`
是 residue `-m/q^2` 的 nonzero simple pole，故無須最右 zero或 gap即有
`g_0=Omega_+/- (e^(at)t^(-M))`。記 AP9/G129/ES120。這不是 RH證明；真正缺口仍是
從 primes獨立產生 eventual單邊號。

最新 strategy refinement為 AP10--AP11/G130--G131。一階 increment
`H(t)-H(t-L)`（`H=-g_0`）有正 grid反演，存在 fixed L eventual非負 iff RH；但再差
一次取得 compact prime window會消掉 `c_0t` drift，generic L必因 critical zeros
正負振盪，故 local-window pointwise sign已關閉。

目前優先 live target是 exponential renewal derivative：
`K_a=int_0^t e^(-a(t-u))H(u)du`、`D_a=K_a'=H-aK_a`。存在 a使 `D_a>=0`
eventually iff RH；它的 prime weight exact為 `[1-(n/e^t)^a]/a`，multiplier
`z/(z+a)` 不消 nonreal zero poles，且 `K_a'=D_a` 提供正 sign-recovery。
下一步只攻 AP11.4 的 arithmetic upper bound／square。`a=1/2` 雖化成 AP11.6 的
單一 psi integral，且 AP11.8--AP11.10 用 exact第一 Li/Hadamard常數證明固定此 a
已足夠：RH下正 drift嚴格大於全部 critical-zero振幅。因此 AP11.6 eventual成立
exact等價 RH；現有 PNT error仍遠大於 sqrt-x slack。不得把等價改寫或更多 finite
VERIFIED batches當成 closure。

最新外部 claimed proof亦已排除：Preprints.org 202605.1525v4 企圖以 Chebyshev
mean square證 critical integral absolute convergence，但其 Lemma 9假定每個
`J_m={k:floor(N/k)=m}` 非空。`N=10,m=6` 即為空集，直接否證所需 weight下界；
floor map只涵蓋 O(sqrt N) 個值，不能控制全部 A(m)。記 PC/ES121/G132。故 AP11.6
仍沒有外部 closure，不能引用該稿。

可靠的 Johnston arXiv:2201.06184（2026 version）則定位了 AP11.6 的強度：Mertens
可無條件證 c=2 weighted bias，但任何 off-line `omega>1/2` 都使所有
`c<1+omega` 出現正 excursion。AP11.6正是 c=3/2，故是 RH boundary。記
AP12/ES122/G133；下一步不能從 c=2作 continuity interpolation，必須直接在 c=3/2
取得新 prime cancellation／square。

最新 ES123/G134 引入 Akatsuka arXiv:2411.19259 的真正 all-complexity 機制。
1/2-superior highly composite extremality把任意整數、任意多 prime exponents一次壓到
`E_1(X)=prod_(p<=X)(1-p^-1/2)^-1/exp(li(sqrt(theta(X))))`；其 boundedness exact等價
RH。這不是 degree-3 延伸，而是獨立 uniform multiplicative route。

`akatsuka_multiplicative_audit.md` 的核心式是
`log E_1=C+int(psi-u)q(u)du+B_theta+O(1/log X)`，
`q=u^-3/2(1/(2log u)+1/log^2 u)>0`，`B_theta>=0` 為 concavity defect。它比 AP11
多 `1/log` damping，critical-line項衰退而 off-line項仍 growing，故列為第二 live
target。但 positive factors不給 monotonicity：`experiments/akatsuka_jump_arb.py` 以
256-bit Arb嚴格證 p=5 jump負、p=1327 jump正。下一步只攻完整 defect uniform upper
bound或 SHCN transition Lyapunov inequality；不得以有限 product batches替代。

SHCN Lyapunov候選也已具體化：consecutive transition的 exact increment是
`(epsilon_j/2)H_j-[F(L_j+H_j)-F(L_j)]`，其 slope comparison落在
`theta(x^2)-x^2` 的 sqrt scale。`experiments/akatsuka_shcn_transition_arb.py` 嚴格證
早期 transitions各有一正一負，故 global decreasing版本已反例；若續此支，必須是
eventual或含 counterterm的 telescoping theorem，不能再只引用 SHCN local extremality。

另有更乾淨的 all-degree輸出 A5.5。令
`G(c)=sum_p log max_e[sigma_-1/2(p^e)p^-ce]`，令 `V(c)` 為
`F(L)=li(sqrt L)` 的顯式 concave conjugate；則 normalized `sigma_(1/2)` 全 n有界
exact等價 `sup_c(G(c)-V(c))<infinity`。這把所有 prime/exponent正局部極值一次處理，
是目前最具體的 uniform升階框架。未閉合引理是不用 RH-scale PNT error直接證
`G(c)<=V(c)+C`；把 G 再展回 E1而只做 absolute estimates不算進展。

最新 AP14/G135 又把此 dual bound完全 linearize。若 `2c=log(1+1/x)/log x`、
`Y=x^2`，則
`G(c)-V(c)=C_0+Q(Y)+o(1)`，
`Q(Y)=int_2^Y(psi(u)-u)u^-3/2[1/(2log u)+1/log^2 u]du`。
theta concavity與 cutoff mismatch在 dual coordinate皆為 o(1)，故 all-degree target exact
縮成 `sup Q<infinity`。kernel另有正 mixture
`q(u)=int_(3/2)^infinity(s-1)u^-s ds`。

這表示 Akatsuka route是 AP11 defect的 logarithmic Cesaro mean，而非獨立 positivity
source；優點是 critical-line oscillation衰減、只需 bounded-above。下一步只找 endpoint
3/2 uniform Tauberian/convex domination。從 c=2或任何固定 `s>3/2` 的 bounds直接取極限
不算，除非常數在 endpoint保持 uniform。

Selberg-lens nudge已實作為 `experiments/akatsuka_dual_extrema.py`，只作策略診斷。
掃描143264個 SHCN transitions後，後段局部極值由接近 `Y=log N` 的 frontier primes
夾住；在 `Y~1.58e6` 約60%的 raw G mass來自 `p>Y^(3/4)`，而 defect僅約0.04246，
是總量約126的全尺度 cancellation。不得把這些 floats當 RH證據。

解析 exponent audit同時證明固定小-prime cutoff不是較弱 closure：off-line距離 a在
frontier保留 `Y^a/logY` growth，截到 `Y^delta` 只得較小 `Y^(delta a)`。所以 exact
low-prime subtraction只能改常數，不能移除 zero obstruction。若續局部化，只能攻
renormalized frontier window的 endpoint-uniform bound；它仍保留 generic off-line poles。

此句現已升級為 AP15/G137 的 exact theorem。對任意 fixed `0<delta<1`，
`W_delta(Y)=Q(Y)-Q(Y^delta)`；log-Laplace scaling為
`Qhat(z)-delta^-1 Qhat(z/delta)`。若 off-line supremum A>0，取 `a>delta A` 的
zero singularity，縮放項奇點實部至多 `delta A`，故不可能抵消，Radziejewski給
W_delta正負無界。RH下則 `W_delta=O(1/logY)`。所以 frontier-only boundedness仍
exact等價 RH；它只減 bookkeeping，不降低定理強度。

最新 AP16/ES124/G138 又關閉 ordinary Selberg mean-square捷徑。Brent--Platt--Trudgian
給 RH下最佳尺度 `int_X^(2X)(psi-x)^2<<X^2`；即使直接贈送此 estimate，對 Q kernel
作 Cauchy--Schwarz每 dyadic block仍只有 `O(1/logX)`，跨 `X=2^k` 是 harmonic
divergence。故下一個 square必須保留跨 log-scale off-diagonal phase並 telescope；
blockwise正 L2 energy、改善常數或更多有限 zeros皆不能 closure。

最新 AP17/G139 發現 fractional Selberg family
`S_alpha=(-zeta'/zeta)^2-alpha(-zeta'/zeta)'`。`0<alpha<1` 時全部 Dirichlet係數
非負，且任一 multiplicity `m` zero保留 `m(m-alpha)` double pole；`alpha=1/2`
有 `(zeta^2)''/(4zeta^2)` 的 exact form。這證明 arithmetic positivity與 robust
zero detection可共存，但未證 RH：扣掉 `s=1` pole後的 Cesaro exponent criterion
`O_epsilon(x^(1/2+epsilon))`（所有 epsilon）已 exact等價 RH；單 zero預測的 sharper
`O(sqrt(x)log x)` 正向未證。係數正性只作用於未 renormalize總量。
完整稽核見 `selberg_fractional_square_audit.md`。下一步只接受先成立的 signed
cross-scale telescoping identity；固定尺度差分或直接重述 bounded remainder不算。

SFS7/G140 另關閉最直接的 denominator-clearing square：完成化後全線 Laguerre
integral `int(f'^2-ff'')=2int f'^2>=0` 對任意 real decaying function成立，故
zero-blind；localized weight則出現無符號的 `w''` term。不得把此 generic Sobolev
identity當成 RH輸入。

外部 ES125（Banks--Sinha arXiv:2209.11768）又給精確定位：
`a_alpha=(1-alpha)Lambda^2+alpha Lambda_2`，而兩個 summatory/twisted estimates
分別已有 RH-equivalence theorem。故 SFS family 是已知 detectors 的 robust凸組合；
它驗證 multiplicity處理，卻不供應所缺 unconditional renormalized sign。

SFS9/G141 又給真正 all-degree moment theorem：`sigma>1` 時
`(-1)^r(zeta^k)^(r)/zeta^k` 是 positive `log N` distribution的全部 moments，所有
Hankel sizes一次 PSD；pole scaling exact趨 Gamma/Gaussian。但 measure representation
不能跨越 Dirichlet收斂邊界，analytic continuation可有 nonreal zeros。故 uniform
degree已解、half-plane positivity bridge未解；不得回去刷 finite moment certificates。

外部 ES126 又證明這個 bridge本身 exact等價 RH：Nakamura 1504.03438 的 completed
zeta pretended infinite divisibility，以及 Nakamura--Suzuki 2306.08317 的 genuine
infinite-divisibility criterion，都把 critical-strip正 Levy representation與 RH等同。
所以此支不再尋找一般 analytic continuation theorem；唯一非循環版本是直接從
primes+gamma 建造正 Levy measure，否則只是 Weil/GNS positivity的機率座標。

AP18/G143 又把此機率座標與 arithmetic phase exact合流。Nakamura--Suzuki 的
g_zeta 是 g0 加顯式 gamma counterterm，且
`g_zeta(t)=sum m_gamma(e^(-i gamma t)-1)/gamma^2`；RH下負號為 sin-square和，
`-g_zeta''` 是 positive-definite zero measure。故 AP sign、Lévy infinite
divisibility、Weil/GNS不是三條獨立路：唯一非循環 target仍是從完整 primes+gamma
side直接 factor positive-definite kernel。

最新 AP19/G144/SC1--SC4 回應 Selberg-lens nudge。將 g_zeta=P-B；P是
prime-power hinge convex sum，B在 t>=log2 嚴格凸。Fenchel conjugate exact給
RH iff Z_j>=B^*(Y_j) 對每個 cumulative prime-power vertex。這是新的
all-complexity座標，但換完後即刻等價 RH；transition增量沒有自動 sign。完整推導見
screw_convex_dual_audit.md。下一步只有 prime-side global telescoping/majorization
可算 closure，更多 vertex計算不算。

SC5/G145 又以 experiments/screw_transition_arb.py 嚴格證 transition兩號：
B'(log16)>Y_16 給正 increment，B'(log32)<Y_before32 給負 increment。故逐
prime-power monotonicity已關閉；若續 SC route，只接受跨 transitions 的 global
telescoping/transport identity。

SC6/G146 將此 global identity精確化為 cumulative quantile majorization：
D(Y)=D(Y1)+integral[ell-(B')^-1]。ell-(B')^-1 已兩號；Lambda*1=log 的正
renewal會依 AP6消掉 zero poles。下一步 transport必須 nonvanishing且保留 phase。

AP20/G147 稽核 Gaussian transport：其 mode multiplier e^(sigma q^2/2)處處非零，
fixed-sigma smoothed sign仍 exact iff RH；但 backward heat不保正，TPD8已排除
Gaussian/Sonine global frame。故不回到 J24 finite Gaussian route。

AP21/G148 已依 Selberg nudge 完成 prime-bound quantile變分稽核。exact
`H=H(T)-int(Y-B')`；只保留 `Y` 單調與 `|Y-B'|<=E` 時，若 allowance含不可積遞增
函數，取 relaxed `Y=B'+E_0` 即使 gap趨負無窮。Bellotti最新無條件 PNT界在此座標
給增長的 `exp(t/2-dt^(3/5)(logt)^(-1/5))`；即使 RH-scale pointwise error也只給
`O(t^3)`。所以 absolute-envelope變分已關閉。下一步只找先成立的 signed cross-scale
arithmetic identity／off-diagonal correlation；不得把直接 primitive bound重命名為引理。

ES128/G149 又稽核 Grochenig--Schoenberg reciprocal-Xi criterion。它一次控制
PF-infinity所有 minors，但 factorization在 `u=t^2` 下正是已知 Stieltjes--Thorin
target；Euler series只在 real-axis兩尾成立，中央 additive Fourier correction不保
total positivity。故不新增平行路徑。若續 all-degree positivity，只接受直接由
theta/primes構造完整 Loewner--Whitney convolution／Stieltjes measure的 theorem。

ES129/G150/strategy44 新增外部 all-degree Hilbert輸入。Arias de Reyna 證
`Pi(e^t)-Li(e^t)` 的 ordinary Laguerre coefficients `a_n` 滿足
`RH iff (a_n) in ell^2`；D10.4 精確給 `E_n=n a_n`，Parseval energy等於
`int_1^infinity|Pi(x)-Li(x)|^2x^-2dx`。這回答了 all-degree結構是否存在：
存在，而且不是 finite certificate；但 norm finite本身 exact等價 RH。Karp 的
geometric-weight theorem要求 entire restriction，prime-power jumps使其不能由 PNT
套用。結合 LS2，下一個較弱且合格的目標是只證負指數門檻違反集合 density zero／
任意長好 block；目前仍缺相應的單側 weak-type Laguerre arithmetic theorem。

聯網又找到 Suman 2026 宣稱由 PNT推出完整 Li漸近的稿件，已建立
`suman_li_asymptotic_claim_audit.md`。兩個獨立 fatal errors：其 (6)--(7) 混淆
`Y(x)=L_n(log x)` 的 x導數與 Laguerre argument導數，故 (53) bracket不由 ODE
消失；其 (62)--(74) 又把 factorially divergent Bernoulli漸近當收斂級數。
另有 fixed-argument Laguerre asymptotic未證可一致積到無窮的缺口。新增
ES130/G151/strategy45；該稿不補 AL5，不應投入更多數值驗證。

另稽核 Suzuki arXiv:2301.05779（2026-08-11頁面版本）與 Matsumoto--Suzuki
arXiv:2409.00888。前者無條件構造 Li-indexed `G_n in L2`，故全 Gram matrix一次
PSD，但 `lambda_n=||G_n||^2/(2pi)` 對全部 n iff RH；等號需要的 `Theta` inner
亦 iff RH。後者提供 weighted-prime/Goldbach二尺度座標與 compact-support M-law
detector；`Lambda*Lambda>=0` 只在未中心化總量，扣主項後 remainder無 sign且
sharp bounds仍 conditional。新增 `suzuki_model_goldbach_audit.md`、ES131--132、
G152--153、strategy46。可續 target：centered Goldbach convolution 的 uniform
inequality，或 prime--gamma Schur-kernel factorization；不得刷 finite norms/sums。

同一 audit 新證 SMG5/L13：RH iff
`int_0^T|H(e^t)|^2dt=O_epsilon(e^(epsilon T))` 對所有 epsilon。若能量次指數，
H的 Laplace transform在 `Re w>0` 解析；off-line rho會在 `w=rho-1/2` 造成非零 pole。
由外部 prime formula，這是 centered weighted-Lambda discrepancy的顯式正能量，
比 pointwise H bounded弱。新增 G154；目前仍缺無條件 centered/off-diagonal upper bound。

外部 Han arXiv:2505.23795（2026-08-11頁面版）再證 smooth weighted PNT與
k-Goldbach error對 zero-free region有 converse。因 `F_k=Psi^k`，固定 k升階只是
同一 PNT error的差冪分解；centered `(Lambda-1)*(Lambda-1)` 係數兩號且是 analytic
square，不是 modulus square。新增 SMG6/ES133/G155；禁止以增加 Goldbach degree
取代 SMG5真正的 reflected/off-diagonal energy estimate。

SMG7/L14 又把 SMG5 prime-side exact展成 all-size Gram matrix：對
`b_n=Lambda(n)-1`，energy為 `b^T K_Yb`，
`K_Y=int_max(m,n)^Y(1-m/x)(1-n/x)x^-2dx`，且
`K_infinity=(3max-min)/(6max^2)`。K對任意 matrix size PSD；這是真 uniform
determinant structure。尚缺且唯一有內容的是 `b^TK_Yb=O_epsilon(Y^epsilon)`
upper bound。新增 G156；kernel依 max，不可用 ordinary m+n Goldbach positivity偷換。

SMG8/G157 再完成 Mellin diagonalization：`B=-zeta'/zeta-zeta` 在 s=1 pole相消，
`Mellin(C)=B/[s(s+1)]`；L14 iff 此 quotient在每條 `Re s>1/2` 的 vertical L2
norm有限。off-line zero給 B非零 pole並使該線 norm發散。故 live operator target是
不預設 pole-free的 primes-only Hardy--Mellin H2 extension；現成 coefficient square
估計只覆蓋 Re s>1。

外部 arXiv:2206.00434 的 analytic-space zero-free framework已核對 SMG8斷層：
bounded functionals可到 p=2，但 closure (C3) 未解；p<1的 cross-space shift inverse
只重得 Re s>1。p=2 closure就是 Nyman--Beurling/RH。新增 SMG9/ES134/G158；
不得以 generic Dirichlet-Hardy embedding或 compact-open density冒充 H2 bridge。

PG1--2/L15 新增真正 uniform算子結構：在 `t=log X`，
`F=e^(-t/2)C(e^t)` 是離散 forcing `(Lambda(n)-1)/sqrt(n)` 與固定 causal Green函數
`g=e^(-u/2)-e^(-3u/2)` 的卷積；其頻譜密度明確且所有尺寸 strictly PD。full-tail
Gram norm與 truncated L14 energy之差也有 `S0,S1` exact正公式。block係數反例證
generic coefficient-square contraction不可能，必須用特殊 arithmetic cancellation。

聯網稽核 Connes--Consani arXiv:1910.14368 與 Baez-Duarte。local operator sign等價
innerness，但各 local factor非 inner；global Poisson+support補救仍是明列 conjecture。
critical Nyman closure則 exact等價 RH。新增 `prime_gram_green_audit.md`、ES135--136、
G159--160、strategy47。live target縮成 global prime--gamma support-preserving
contraction；不得引用 Weil positivity/innerness/critical closure作輸入。

PG5 又稽核 Selberg symmetry：`Lambda log+Lambda*Lambda=mu*log^2` 是真正
uniform convolution identity，但 Mellin側為 analytic Riccati square，沒有 modulus
square／reflection。外部 short-interval symmetry bounds只平均 interval origin，
不能給 fixed-origin L14 maximal bound。新增 ES137/G161/strategy48；若無新的
deterministic average-to-maximal mechanism，不再升高 Dirichlet convolution degree。

Masters' Selberg nudge要求先判定 contraction是否已等價 RH；PG6/L16 已完成：
centered-prime Green energy的 logarithmic power exponent exact等於
`2 sup_rho(Re rho-1/2)`。故 `exp(o(T))` contraction就是 RH，不是外加引理。
後續若走 Selberg self-improvement，必須先證 strict exponent `theta<1`，再有可迭代
`Phi(theta)<theta`；一般 PNT error的 exponent仍為 1。

PG7/L17 同時建立 `M=xi'/xi` 的全階 positive-real Pick kernel；RH下有 zero-vector
Gram分解，反向 holomorphic PSD排除全部右半平面 poles。Euler--gamma資料在外半平面
可算，但 positivity延至 critical half-plane exact等價 RH。off-axis quartet polynomial
證 functional-equation boundary all-pass性不足。新增 G162--163/strategy49；停止在
Green/Hardy/inner/Nyman四個等價 endpoint間繞行，改攻 quantitative exponent map。

PG8/ES138 再稽核第一個 strict exponent的經典候選。Landau/de la Vallee Poussin
nonnegative coefficient polynomial必支付至少與 target coefficient同量的 gamma
`log t` cost，故現代高 degree最佳化仍只改善 `1-c/log t` 常數。signed polynomial
可形式消 gamma，但其他 harmonic zeros失去符號；控制它們就是新的 global
correlation缺口。新增 G164/strategy50；不再做 cosine polynomial degree刷證書。

PG9/G165/strategy51 完成 Selberg exponent-map本體檢查：在 multiplicity m zero旁，
Riccati兩側 principal part同為 `m(m-1)/(s-rho)^2`，simple zero double pole正好消掉；
故任意 `Re rho` 都是 neutral mode，identity本身不可能給 `Phi(theta)<theta`。
估 RHS `mu*log^2` 又直接碰 `1/zeta` poles。AP11/AP14/Green/Pick現統一列為
RH-equivalent detectors；新輸入只能是獨立 signed-Moebius estimate或 reflected square。

PG10/ES139/G166/strategy52 稽核 remaining reflected-Moebius方向。`|1/zeta|^2` 在
`Re s>1` 確有 all-size Toeplitz PSD係數式，但 damped norm若對每個
`sigma>1/2` 有限，off-line zero所在 line立刻有不可積 pole，故 exact等價 RH。
averaged Chowla屬 additive shift-average，不能控制 fixed Mellin norm；Ng的條件結果
又顯示 negative moments即使在 RH下仍細緻。現有 Mobius平均 theorem不是新 bridge。

PG11/ES140/G167/strategy53 再核對 `p<1` Hardy constants：cross-space inverse條件
`q<p/(1+p)` 使 `q->1-` 時 source p趨無窮，而 evaluation只覆蓋
`Re s>1/q>1`。所以此 endpoint逼近的是 PNT line，不是 critical line；不可與 PG10
的 fixed-line pole Lp integrability混用。

外部前沿掃描另稽核 Bellemare--Langlois--Ransford arXiv:2011.02847 的 Nyman
Cholesky positivity conjecture。它確為 all-size determinant結構，但作者未知其是否
imply RH；NC2 更給 abstract exact反例，顯示全正 lower-triangular Cholesky與正 RHS
仍可保留非零 orthogonal residual。新增 `nyman_cholesky_positivity_audit.md`、
ES141/G168/strategy54；不做更多 entry batches，除非有消滅 residual的 quantitative
closure theorem。

## 2026-08-16：Nyman特殊右端與固定欄漸近稽核

- 新增 L18/NC3：`A=L^-1((k-1)/k)` 精確等於 Gram--Schmidt basis上的
  `s=0` Mellin residue向量，且 `A notin ell2`。若平方可和，其代表向量會對
  `f_k->0 in L2` 取值趨 1，矛盾。故全正猜想控制的是不連續 boundary functional，
  不是 `E=L^-1(log k/k)` 的 closure energy。
- NC4 給更強 exact countermodel：保留 strict positive Cholesky、真正的
  `F_k=log k/k`、`a_k=(k-1)/k`、positive E、固定欄 law
  `2L_kj/F_k->A_j` 及 `||f_k||->0`，仍有正交殘差。所以下一步不能再靠 signs、
  fixed-column asymptotics或有限 determinants；必須使用 full ratio-dependent
  Nyman Gram／Möbius moving-tail structure。
- 外部新增 Ehm arXiv:2405.06349。其 `q=2` 更強 Sobolev damping仍 iff RH，
  quadratic decomposition中首個明確未閉合項是 truncated Möbius inversion error，
  作者稱為 major challenge並擱置；其餘 centered products也只具 empirical
  correlation。新增 NC5/ES142/G169--G171/strategy55。
- 最新 Masters nudge 指出 off-line `cosh(n lambda)` 終會壓過 on-line項；此已由
  L5/LS1 的最大殼層與 syndetic負逸出嚴格涵蓋，結論就是 Li criterion，未重複列為
  新證明方向。
- RH仍未證。下一最小合格工作：對 Ehm 的 `E_a^(q)(N)` 或等價 full Nyman
  moving-row tail尋找不預設 `1/zeta` critical continuation的 uniform arithmetic
  inequality；若只估固定欄、有限 Gram entries或觀察 Mertens correlation，不算進展。
- L19/NC5.2--5.3 再證 moving-boundary absolute no-go：`S_q` 在固定 ratio window
  離零，square-free pairs使裸 Möbius absolute tail為 `Omega(N)`；Levinson--Selberg
  outer weight後仍 `Omega(N/log N)`。所以 `q=2` 的 `x^-4` far-tail decay不夠，
  必須保留 signed two-variable Möbius cancellation。新增 G172/strategy56。
- 外部 Maier--Rassias arXiv:1806.05070 對相關 cotangent kernel在
  `k^D<=n<2k^D,D>=2` 證 fixed-power saving；但它只覆蓋 `n>=k^2`，kernel也非
  `S_q` 本身。未找到 `D=1` 同尺度 extension。新增 ES143/G173/strategy57；可作
  remote-tail工具，不能補主要 moving boundary。
- Ehm Corollary 3.1 reciprocity只有 `r<->1/r` 加 elementary terms；fixed-ratio
  window仍是 fixed-ratio，elementary terms回到未證 negligible的 Landau/Mertens
  products。新增 NC5.5/G174，關閉以 reciprocity偷渡到 `D>=2` 的捷徑。
- NC5.6--5.7 將 full Gram Mellin對角化；moving tail與所有 elementary pieces
  重組後正是 critical Nyman mollifier norm。新增 G175/strategy58。故 Ehm分解不是
  新的獨立 detector；下一步只接受不使用 critical `1/zeta` 的 same-scale signed
  Möbius bilinear theorem。

## 2026-08-16 continuation：Ehm same-scale bilinear 強度稽核完成

- 新增 `nyman_same_scale_bilinear_audit.md`。固定比例 `m<N<n` box精確為
  `T_(q,N)=B_(q,N)/(N log N)`，其中
  `B=sum mu(m)mu(n)W_q(m/N,n/N)`；單獨消去 tail需要 `B=o(N log N)`。
- Mellin separation精確給 adjacent Möbius Dirichlet polynomials `A_N(t)C_N(t)`。
  generic Cauchy/large sieve/absolute Fourier integral只回到 `O(N/log N)`，沒有
  `o(1)`。這不是提高 `q` 或 Sobolev damping能補的缺口。
- 寫成 additive shifts後，即使每 shift猜想級 `O(sqrt N)`，取絕對值仍為
  `N^(3/2)>>N log N`。MRT averaged Chowla在 `H=X=N` 只給 `o(N^2)` 且丟掉
  shifts間符號；新增 ES144/G177/strategy60。
- Guth--Maynard arXiv:2405.20552v2針對約 `N^(3/4)` generic large values，未達
  Möbius near-square-root signed product，zero-density亦不能排除所有離線零點；新增
  ES145/G178。
- L20/NS6證明若所需 `o(N log N)` 對所有 smooth kernels成立，rank-one kernel
  立即給 smooth Mertens square-root bound並證 RH。故 generic uniform theorem會循環；
  唯一可能較弱的是 `S_q`-specific exact identity，但全部 corrections重組又是 NC5.7
  的 RH-equivalent Nyman norm。
- 結論：RH仍未證。Ehm支線在 NS1.3 暫停；除非取得保留完整二維符號的
  kernel-specific cancellation／reflected positivity，不再刷有限證書或 numerical
  VERIFIED batches。Goal保持 active。

## 2026-08-16 continuation：single-kernel nudge、divisor no-go 與 local moments

- Selberg-lens nudge要求先判定單一 `W_q` 強度。新增
  `ehm_single_kernel_audit.md`：fixed natural cutoff、all cutoffs、norm-uniform cutoffs
  是三個不同命題。
- 在 `S_q` 不離零的 rectangle，local Wiener lemma給 `1/S_q` 的 `L1` separated
  representation。若同核估計對完整 Wiener algebra具一致量詞，可恢復 rank-one；
  same-block版遂直接蘊含 RH。natural tail只有 separated fixed cutoff，L20不能直接套用。
- superlacunary coefficient blocks可令固定 ratio-window bilinear form恒零而 partial sums
  線性大，嚴格排除 fixed-tail的 coefficient-generic implication。這不反駁 Möbius-specific
  theorem，但證明其必須使用乘法算術。
- SK4得到 natural Ehm error的 exact雙 logarithmic Cesaro式。再展開
  `S_q=sum R_q` 得 `d_u(j)=sum_(d|j,d<=u)mu(d)`；在 `u<j<=2u` 精確有
  `d_u(j)=-mu(j)`。所以 divisor/identity-factory在主要帶逐字保留 Möbius pair，
  沒有轉成 prime positivity或 far ratio。新增 L21--L22/G180--G182/strategy62--63。
- 核對 Ramaré--Zuniga arXiv:2312.05138v3：log-smoothed `mu/n^sigma` positivity只在
  `sigma>=1`，complex estimate保留 `int|m_q|`/`1/zeta`，不能補 same-scale。
- 新增 `mobius_local_moment_route.md`。Verjovsky arXiv:2607.25002 給真正 uniform
  degree-to-exponent map：fixed `q` loss `1/[2(q+1)]`，unbounded `q`才到 RH。
  LM3.1 的 critical local Orlicz inequality一次控制所有 degrees，且等價 RH；這是合格
  all-degree正 target，但 deterministic Möbius subgaussian producer尚未找到。
- RH仍未證；goal active。Ehm fixed scalar仍是 live但 divisor直路關閉；local moment線
  只接受 all-degree Orlicz/tail mechanism，不刷 finite moments。

## 2026-08-16 continuation：fixed local moment bootstrap 與 Orlicz dual audit

- 新增 `external_claim_audit_verjovsky.md`。核心新定理：對任一 fixed finite `q>=1`，
  critical arc local norm `B_(q,c)(N)=N^o(1)` 已 iff RH；不需要 unbounded `q`。
- 證法：若 `M(x)=O(x^(1/2+delta+epsilon))`，重縮放
  `F_N(u)=P_N(u/N)` 後兩次 partial summation給
  `||F_N'||=O(N^(delta+epsilon))`。local spike inequality用同一 `q` 將
  `delta->delta/(q+1)`；從 `delta_0=1/2` 有限迭代至任意 epsilon。
- 因此 Verjovsky main theorem仍正確但非 sharp；Remark 3.4 的 fixed-q limitation只是一
  次套用 Corollary 3.3，忽略 feedback。新增 L24/G185/ES148/strategy65。
- 最小 target降為 `q=2` 單一 all-size PSD Toeplitz form
  `N^-1 sum mu(m)mu(n)sinc(2pi c(m-n)/N)=N^o(1)`。這有真正 exponent map，不是
  finite certificate；但 MRT/Davenport只給 exponent仍為 1 的 log saving，尚未證 target。
- 依 Selberg nudge導出 exact Gibbs dual：Orlicz upper bound iff對每個 probability
  density `w` 控制 additive Toeplitz quadratic by entropy。SK5.2是 multiplicative
  ratio kernel；平方 `d_u`只造一個 lower-bound witness並升成四階，不能作 upper
  certificate。新增 L25/G187/strategy66。
- RH仍未證，goal active。下一步集中於 quadratic target的 arithmetic producer或 exact
  ratio-to-additive transmutation，不再追高 moments。

## 2026-08-16 最新 handoff：q=2 quadratic 的三個全尺度座標

- 新增 `mobius_local_quadratic_audit.md`、L26--L29、G188--G191、ES149--ES150、
  strategy67--70。
- Selberg nudge量詞已封閉：fixed-q bootstrap對每個 final epsilon只需有限迭代，
  不要求 loss/constant uniform in delta；q=2 criterion保持有效。
- exact Legendre--Bessel與 discrete-prolate均為 all-rank PSD分解。prolate tail可在
  `J~logN/loglogN` 後降至 subpower，但前 J 個 low modes（k=0已是 smooth Mertens）
  無 square-root arithmetic bound。
- `mu log=-mu*Lambda` 的 exact scale integral只在控制所有窄 arcs時有 `2/logN` gain；
  該 envelope在 `c'->0` 已含 Mertens。fixed-c估計的 normalization恰使 gain消失。
- Lambert identity產生 all-scale equation
  `G_N+sum_(k>=2)k^-1/2G_(N/k)=small`，但 transfer symbol為
  `zeta(s+1/2)`；generic coercivity循環到 reciprocal-zeta。只保留利用 special forcing、
  Gamma decay/functional equation的非 generic transfer為 live窄路。
- 外部 arXiv:1905.08354、1509.02646只補 prolate spectral tail；arXiv:2607.09797v3
  的 Laplace criterion仍是 `Gamma/zeta` explicit formula，未給無條件臨界 bound。
- 下一步：先測 Lambert special-forcing能否經 functional equation形成排除
  `Re rho>1/2` 的正能量/反射式；若仍只等價改寫，轉攻 low-prolate modes的 joint
  multiplicative cancellation。不得刷 finite moments/eigenvalues。RH未證，goal active。

### 補充修正

- Lambert special forcing已測完並關閉：scale Mellin transform為
  `Gamma(r+1/2)/zeta(r+1/2)`，zero-free Gamma不消 zeta zeros，functional equation
  只反射 poles（LQ5.1/L31/G193/strategy72）。
- low-mode判讀亦再縮小：取 `c=1/(2pi)`，第一個 Legendre mode
  `sum mu(n)sin(n/N)/(n/N)` 的 Mellin weight在 `Re s>0` 無零，故其
  `N^(1/2+o(1))` bound本身 iff RH（LQ2.1/L30/G192/strategy71）。不再把 joint
  low-prolate estimate列為較弱目標。
- 下一 live route：只尋找此 sinc-smoothed scalar的直接乘法正性／反射 inequality，
  或新的 q=2 arithmetic factorization；不得以 Mellin除以 zeta、finite modes或
  spectral numerics冒充 producer。RH未證，goal active。

### 最新主引理（優先於 exponent bootstrap）

- LQ2.2/L32：對 `w(x)=sin x/x`，正 Volterra式給
  `sup|A_w| <= sup|M| <= (2sin1-1)^-1 sup|A_w|`。
- `A_w/sqrtN` 是 `c=1/(2pi)` critical arc的 normalized mean，故任一 fixed
  `L^q` subpower bound一步推出 RH。這完全回答 degree斷層與 nudge的 constant疑慮：
  升階機制對所有 q相同、無迭代。
- 現在唯一最小缺口：直接證 sinc-smoothed Möbius scalar的 square-root-subpower bound；
  該 scalar本身已 RH等價，數值、PNT log saving或 finite PSD都不夠。

## 2026-08-16 最新 handoff：sinc Müntz/sampling 路完成強度稽核

- 新增 `sinc_muntz_sampling_audit.md`、L33--L35、G195--G198、ES151--ES152、
  strategy74--77。
- compact sinc的 exact dilation source `b=sum mu(k)f(kx)` 在 `x=1/N`就是 target，
  symbol `W/zeta`；Báez-Duarte strong kernel theorem確認 closure iff RH。
- `Pf<=0` 是新的全域 sign，但 `h=-Pf` 的 dilations共享 `I/(kx)` tail。已證 closed
  positive cone不能逼近 target，所以 signs/μ parity不可移除。
- exact sampling energy：
  `sum_(k in Z)|A_N(k)|^2=pi N[M(N)^2/N+sum_(n<N)M(n)^2/(n(n+1))]`。
  它是 all-frequency PSD，卻是 weak-Mertens energy；現有 theorem無 subpower bound。
- sinc dilation formula導出的 alternating sample reconstruction係數非 `ell2`，沒有
  uniform coercivity。下一步不得再用 Müntz rename、positive entries或 sampling numerics。
- 下一 live問題：尋找 signed dilation coefficients的 uniform tail cancellation theorem，
  或能以 bounded-norm projector隔離 `A_N(1)` 的 multiplicative arithmetic結構。
  RH未證，goal active。

## 2026-08-16 最新 handoff：bounded signed projector排除

- 新增 `sinc_signed_closure_audit.md`、L36--L38、G199--G202、ES153--ES154、
  strategy78--81。
- signed closure error精確為
  `int|W(1/2+it)|^2|1+zeta(1/2+it)C(1/2+it)|^2dt`；tail必要條件是
  `C(1)=sum c_k/k->0`。
- 已證任何成功 sequence都須 `sum|c_k|/sqrt k->infinity`；critical zeros排除
  bounded-norm projector。故上一 handoff的 bounded-projector選項正式關閉。
- Selberg nudge已精確吸收：indicator時 k座標為 `M(floorN/k)`，sinc時為同一 target
  `A_w(N/k)`；normalized weights `k^-1/2` 臨界發散，遞迴沒有收縮。
- Burnol只給必要 lower rate；Báez-Duarte explicit decay是 conditional on RH；recent
  Gram compression不給 target upper bound。
- 下一 live問題只剩：設計允許 coefficient norm發散、精確消 tail，卻能無條件控制整條
  critical-line error的 signed arithmetic coefficients。若只是 truncated μ mollifier，需先
  提供超越 PNT/zero-free-region的新 uniform estimate，否則仍循環。RH未證，goal active。

## 2026-08-16 最新 handoff：ordinary-Laguerre block線結論明確

- 新增 `laguerre_block_uniform_audit.md`、L39、G203--G204、ES155、strategy82。
- AL5所需輸出先固定為任意長遠端 block的 `sum|a_n|^2<=exp(epsilon N)`；循環淘汰
  條件包括 `g e^-t/2 in L2`、unit-disk Hardy控制、Mertens臨界界與零點排除。
- exact Stieltjes介面：`a_n=int e^-t(L_n-L_(n-1))d[Pi(e^t)-Li(e^t)]`。block energy
  是 prime-power nodes減 `e^t/t dt` 主項的 centered quadrature dual norm。
- basis端已真正 uniform：difference Gram eigenvalues為
  `2-2cos(j*pi/(H+2))`，只產生 `H^2` condition loss。Temme/Frenzen--Wong/
  Vanlessen亦提供全區 uniform asymptotics。
- Lubinsky--Mate--Nevai/MZ large sieve只處理 positive well-spaced或 Gauss nodes；
  `log p` 高端不分離，且取 positive total variation會丟掉主項 cancellation。Plewa
  Hardy theorem則要求目前不可驗證的 H1/L1輸入。
- 所以本線唯一未閉合 theorem為 LB8.1：centered prime measure在移動 Laguerre
  blocks上的 `exp(o(N))` signed embedding。未找到可直接代入的成熟定理；一般
  asymptotics/frame檢索到此停止。
- 下一順位依策略稽核轉回 controlled norm growth 的 signed projector。只排除
  bounded `sum|c_k|/sqrt k`；不得把 L37誤寫成整條 signed projector關閉。RH未證，
  goal active。

## 2026-08-16 最新 handoff：controlled-growth signed projector仍 live

- 新增 SC7--SC8、L40、G205、strategy83。固定窗口內，`C(1)=0` 的 Dirichlet
  polynomials仍稠密；Paley--Wiener zero-counting給 elementary proof。乘 zeta後因 zeros
  只有 measure zero，local target仍可任意逼近。qualitative local existence已解。
- 未解的是 norm cost。令 `kappa(T,delta)` 為 local error `<=delta` 時最小
  `K=sum|c_k|/sqrt k`。critical zeros使 delta趨零時 kappa必發散，但不排除慢增長。
- `W(1/2+it)=O(1/t)` 配 zeta 二次矩給更新後 tail
  `O(T^-1+K^2logT/T)`。所以只要找到 `delta(T)->0` 且
  `kappa(T,delta)^2logT/T->0`，即完成 global closure/RH；RH方向可後選 T滿足，
  故這是精確 controlled-projector格式。
- 下一棒只查 clustered frequencies `log k` 的 quantitative completeness、biorthogonal
  norm或 finite-window controllability一手定理，驗收標準是實際推出上述 polynomial
  cost。bounded inverse已排除但整條 signed route未關閉；SK5.2、Lambert/sinc遞迴暫不
  重開。RH未證，goal active。
- 已查 standard/asymptotic-gap與 2024 no-gap biorthogonal estimates；前者需 gap，後者
  仍需 power-law counting與有界 condensation cardinal。`log k` 的 exponential counting
  不符合，故沒有取得 kappa upper bound（SC9/ES156/G206）。

## 2026-08-16 最新 handoff：mean-square tail把 norm門檻提升到近平方根

- SC10以 Ingham--Atkinson theorem
  `int_0^X|zeta(1/2+it)|^2dt<<XlogX` 取代逐點 convexity，嚴格得到
  `int_(|t|>T)|W|^2|1+zeta C|^2 << T^-1+K^2logT/T`。
- 因而 controlled projector的充分條件更新為：找 `delta(T)->0` 且
  `kappa(T,delta)^2logT/T->0`；任意 `K=o(T^alpha),alpha<1/2` 足夠。舊的
  `alpha<1/4` 門檻已作廢。
- SC11稽核 Radziwill arbitrary-length mollifier lower bound：它只給 high-shell
  `c/theta`；經 sinc weight成 `c/(Ttheta)`，且 K不控制最大 support，不能變成 kappa
  upper/lower bound。標準 Selberg mollifier在 fixed `theta<1` 亦只給固定 shell mean
  error，不解 compact low-frequency approximation。
- Selberg nudge的核心警告已落實：kappa格式本身仍等價 RH。這次真正獨立的新 input
  只有 mean-square tail改進；local coefficient-cost upper bound仍缺。下一步只接受
  能直接證 tail-exact `kappa^2logT/T->0` 的特殊 target theorem，不再查一般 mollifier
  比例、RH宣稱或等價判準。RH未證，goal active。
- 另有一個部分性結構：Andersson--Pechersky bounded-coefficient density可選
  `|c_n|<=n^(-1/2+1/loglog n)`，使 K對 support N只有 `N^o(1)`，且 exact tail修正
  bounded（SC12/L41）。但 source完全不給指定 `(T,delta)` 所需 N；所以目前最窄 live
  義務是 effective support complexity，必須實際推出 `K(N(T,delta))^2logT/T->0`。

## 2026-08-16 最新 handoff：ell2/GCD繞道被 cluster反例排除

- SC13/L42取遠端 block `d_n=1/M,N<n<=N+M`，另以 d1精確消 `C(1)`。若
  `N>>TM`，block在 `[T,2T]` 幾乎完全同相，所以 shell energy有固定正下界；但
  `sum|d_n|^2=1/M+o(1)`。因此不存在對 arbitrary support有效的 ell2-only tail bound。
- Bettin--Chandee--Radziwill twisted second moment仍限 polynomial length；GCD spectral
  norm是充分長平均的 arithmetic kernel，不能處理固定窗中的超密 log cluster。
  support/spacing條件不可刪除（ES159/G209/strategy86）。
- 依 Masters’ Nudge另核對 regularity循環：PNT餘項只控制 Re s近 1，不能給
  regularized reciprocal在 critical line的 uniform analytic/Sobolev常數。用這種
  coefficient decay必先證 zero exclusion，故目前淘汰（SC14/G210）。
- effective support complexity仍是 live gap；可能的新 theorem必直接控制 max support
  或每個 log-cluster的 signed mass，並最終驗證 `K^2logT/T->0`。RH未證，goal active。

## 2026-08-16 最新 handoff：cluster-aware tail criterion

- SC15/L43定義 `B_T^2=sum_j(sum_(j/T<=logn<(j+1)/T)|c_n|/sqrt n)^2`。
  Gaussian majorant給 `int_T^(2T)|C|^2<<TB_T^2`；配 Ingham無條件四次矩，得到
  `global tail<<T^-1+K B_T log^2T/T`。
- 因而 controlled projector現在有兩個充分驗收式：SC10的 `K^2logT/T->0`，或較細的
  `K B_T log^2T/T->0`。後者直接利用 coefficient在 log scale上的分散。
- 對 Andersson envelope嚴格有
  `B_T^2<<1+T^-1 sum_(T<n<=N)n^(-1+2/loglog n)`；power bookkeeping約把可容許 K
  從 `T^(1/2)` 放寬到 `T^(3/4)`，但 slowly varying factors必保留。
- 尚缺的不是 generic tail theorem，而是 local approximation本身的有效 N(T,delta)，
  或直接控制實際 Pechersky coefficients的 `K B_T`。Masters’ Nudge的 regularity警告仍
  生效：不得用 `1/zeta` analytic strip或 critical Sobolev常數補此缺口。RH未證，goal active。

## 2026-08-16 最新 handoff：beta kernel吸收任意 fixed polynomial cost

- SC16/L44改用 `f_m=x(1-x)^m1_(0,1)`；其 Mellin transform
  `m!/prod_(r=1)^(m+1)(s+r)` 在 Re s>0無零。common tail及 exact signed closure公式
  全部保留。
- 對每個 fixed m，二次矩 tail為
  `T^(-2m-1)+K^2logT/T^(2m+1)`；cluster版為
  `T^(-2m-1)+K B_Tlog^2T/T^(2m+1)`。
- 因而 sinc所得 1/2、3/4 exponent不是本質門檻。若能對某 local construction證
  `K<=T^A` 或 `K B_T<=T^A`，A只要有限，先選一個 fixed m>A便足以推出 global
  closure/RH。這是 all-order解析升階，不是 finite-degree certificate。
- 唯一尚缺：Andersson--Pechersky沒有任何 polynomial-in-window rate；`N^o(1)`只相對
  support，仍不夠。下一檢索只找 quantitative approximation theorem能給某有限 A。
  不得讓 m隨 approximant任意長大，亦不得用 reciprocal regularity偷渡 RH。goal active。
- quantitative Müntz相鄰文獻已按此較弱門檻重查；只找到他 basis的 coefficient lower
  growth、Markov/Remez與幾何性質，沒有 `log n` spectrum的 polynomial-in-window upper
  theorem（ES161）。本線仍 live，但不能用更多 qualitative density替代該義務。

## 2026-08-16 安全交接點（本輪階段性收尾）

### 狀態結論

RH **尚未證明**；persistent goal保持 active，禁止標記完成。本輪停止新研究與外部檢索，
停在等待使用者輸入的安全交接點。

### 已證結果

1. signed Müntz error有 exact Mellin表示 `Ehat_(m,C)=W_m(1+zeta C)`；exact common-tail
   cancellation為 `C(1)=0`。
2. bounded `K=sum|c_k|/sqrt k` projector不可能；near-zero lower bound明示 K必發散。
3. fixed T上 tail-exact Dirichlet polynomials具有 qualitative local density。
4. sinc/beta tail已有無條件二次矩與 cluster版本；support-free ell2-only bound有明示反例。
5. beta family zero-free且給任意 fixed order decay；若 local cost為任何 finite polynomial，
   固定較大 m即可吸收。
6. 最新 nudge已重驗：同一 C滿足 `Ehat_m=(W_m/W_m0)Ehat_m0`，ratio在 critical line
   bounded，故換 `f_m,h_m`後 local error可轉移。這只證升階合法，不產生 polynomial bound。
7. ordinary-Laguerre difference block的 Riesz loss只有 `H^2`且不依 degree endpoint；
   uniform-in-degree basis斷層已關閉。

### 已淘汰或暫停的路線

- 已反證機制：bounded-norm projector、support-free ell2/GCD tail control、把 smaller-scale
  recurrence當 contraction。
- 因循環拒絕：用 critical-line reciprocal smoothness、Mertens臨界界或 zero exclusion
  生成 coefficient decay。
- 暫停而非證偽：ordinary-Laguerre一般 large-sieve/asymptotics/frame檢索；未解部分是
  prime-centered signed quadrature。SK5.2 Orlicz與 Lambert/sinc recursion亦維持封存。
- 不再檢索宣稱 RH proof或只提出 RH等價判準的論文。

### 存活但未證的候選與最小缺口

唯一主線是 controlled-growth signed projector。最小充分義務為：對某 fixed `m_0`，找
finite `A`、`delta(T)->0`與 finite `C_T`，使

```text
C_T(1)=0,
||W_(m_0)(1+zeta C_T)||_L2(|t|<=T)<=delta(T),
K(C_T)<=T^A,                                         (Handoff-1)
```

或最後一條改為 `K(C_T)B_T(C_T)<=T^A`。beta升階與 tail theorem使 (Handoff-1)推出
global closure再推出 RH；目前它沒有證明。Andersson--Pechersky只給 coefficient envelope及
support-relative `N^o(1)`，沒有 `N(T,delta)`，所以不能代入。

### 證據與循環核對

- 內部 algebra/counterexample：SC7、SC13、SC15、SC16、SC16a及 L39。
- 外部成熟 input：Atkinson/Ingham zeta moments、Andersson--Pechersky density、已記錄的
  Laguerre uniform asymptotics/large-sieve applicability checks；它們未補 Handoff-1。
- L45是「若 Handoff-1則 RH」的 conditional theorem，不是 RH證明；qualitative density、
  coefficient envelope、核衰減都不得替代 Handoff-1。

### 下一次直接續攻的第一步

只處理 Andersson--Pechersky proof中的 finite partial-support stopping mechanism：抽出可明示
的 `N(T,delta)`或確認其 compactness/selection論證不提供 rate，然後立即代入 Handoff-1
驗收。在此步有明確結論前，不展開其他支線、不新增 VERIFIED批次。

## 2026-08-16 continuation：Andersson stopping-rate入口已稽核

- 已新增 `andersson_pechersky_rate_audit.md`、L46/G214/strategy91，並讀取
  arXiv:1207.4624 原始碼及 arXiv:1207.5337 follow-up。
- Andersson proof只證 `forall fixed f, exists N(f,R)` 型 pairing divergence。任意 finite
  prefix在 infinite-dimensional `L2` 中都有共同正交 unit direction，故不能交換成
  Handoff-1 所需的 window-uniform stopping rate。這關閉該 proof機制，不反證
  polynomial-cost approximants。
- 下一最小 obligation 已改寫成 exact Hahn--Banach dual。令
  `y_m=W_m(s)`、`a_(m,n)=W_m(s)zeta(s)(n^-s-n^-1)`；則需證

```text
|<y_m,f>| <= delta(T)||f||
              + T^A sup_(n>=2) sqrt(n)|<a_(m,n),f>|.  (Handoff-2)
```

- `C(1)=0` 已吸收到 atoms，dual coefficient norm與原 K相差至多 factor 2。finite-prefix
  orthogonality顯示 all-target frame bound過強；Handoff-2 的 target term不可刪。
- critical-zero lower bound只排除 bounded K，尚未排除 finite A。因此 Handoff-2 存活，
  RH仍未證，goal保持 active。下一步只找 special target `y_m` 的 norming/duality機制；
  若再只得到 fixed-direction divergence，立即判不合格。

### Handoff-2 初步數值壓測（非證明）

- `experiments/results_ap2_dual_cost_2026-08-16.md` 顯示 ridge候選在視窗接近第一 critical
  zero時成本/誤差急遽惡化；N=64到512僅緩慢改善。m=4因 W_m衰減而降低常數，但不能
  消除 `delta(T)->0` 時固定零點造成的 K發散。
- 這沒有給 polynomial upper或 super-polynomial lower。下一棒只做 zero-neighborhood-aware
  AP2.5 inequality；不得把浮點 plateau當 completeness反例，也不再刷 N。

## 2026-08-16 continuation：Handoff-2 producer邊界再縮小

- L47/AP4.1 以 Poisson--Jensen嚴格反證 generic smoothness producer：即使 target只是
  `exp(i omega t)`，單邊負頻 H-infinity/Dirichlet多項式在 `K<=T^A` 下也不能令長窗
  absolute L2 error趨零。故 real-Sobolev regularization、two-sided Jackson後再轉
  `-log n` frequencies的路線關閉。
- L48把首零點極端參數定量為
  `K>=c(d+Cdelta^2)^(-r)`（d為端點距離、r為 multiplicity）。這只是 polynomial
  lower obstruction，所以不以數值爆炸淘汰 special zeta target。
- 唯一下一步：證 `-1/zeta(1/2+iz)` 特有的 lower-half-plane arithmetic/Hardy
  factorization可給 Handoff-2，或對這個特定 target證 super-polynomial no-go。一般
  density、smoothness、更多 support掃描均已不合格。RH未證；goal保持 active。

## 2026-08-16 continuation：MB1收尾與路線切換

- L49/AP5固定 explicit Riesz--Möbius polynomial-cost候選；L50/AP6給 exact physical
  energy與 k=1 centered prime bulk identity。
- L51/AP7證 `y>X` 首 moving block仍是 same-scale signed Möbius Riesz sum。任意 fixed k
  只給 log damping；PNT平方能量不趨零。MB1可能靠 prime/boundary/tail joint cancellation
  成立，但這逐字回到既有 NC5/L20 RH-scale缺口，沒有新 producer。
- controlled-projector目前三個 producer裁決：Andersson rate量詞失敗；generic
  Sobolev-to-one-sided有 L47反例；fixed Riesz mollifier回到 same-block Möbius。路線本身未
  被反證，故 Goal不完成；但在無新 joint-cancellation identity前封存。
- 下一順位：ordinary-Laguerre LB8.1。第一步只做 exact dual comparison，判定
  prime-centered moving Laguerre block是否與 AP7/NC5同構；若同構立即合併封存，若保留
  不同 geometry再推其 signed embedding。RH未證，goal active。

## 2026-08-16 continuation：LB9.1 成為目前核心 obligation

- `laguerre_vs_mobius_block_audit.md` 證 Laguerre與 AP7沒有 linear same-block isomorphism；
  exp/log relation會混合全部 lower degrees，故 prime-linear geometry不是已封存 Möbius block
  的換名。
- 核心命題固定為 `H_N=ceil(log(N+2))`：對每個 epsilon，arbitrarily large N上
  centered prime measure在 block `Q_N,...,Q_(N+H_N)` 的 dual norm至多
  `exp(epsilon N/2)`（LB9.1）。此式 exact iff RH。
- pure-power L53反例排除只用 positivity、PNT cumulative envelope或 generic signed
  Carleson theorem。下一步只能找 actual prime-power nodes/weights的 deterministic signed
  correlation；basis asymptotics、positive MZ與 pointwise PNT不再重開。
- RH尚未證；goal active。

### LB9.2 可計算驗收式

- L54/LM6.3 已把 block energy寫成 finite prime cutoff Y的完整 CD centered square；L55再
  寫成 `R_j(Y)` centered log moments經 associated-Laguerre binomial matrix的
  `sum|U_n(Y)|^2/n^2`。
- 不可交換量詞：先 N、後 Y趨無限。逐 moment PNT或分開估 prime/continuum/cross都不合格。
- 下一步只把 Selberg identity代入 LM7，檢查是否有 PSD/conjugate square；若沒有，actual
  prime-specific producer亦關閉到最小點。Goal保持 active。

## 2026-08-16 continuation：LB9 Selberg裁決與數值存活測試

- L56/LM8--LM9完成嚴格 substitution audit：Selberg及全部 higher `Lambda_k` hierarchy對
  centered measure的二次核只能是 `h(t+u)`；LB9.2 associated-Laguerre核由最高 bidegree
  證明非 Hankel。故 analytic convolution不能 exact產生 PSD block square。這關閉 Selberg
  producer，不反證 LB9.2。
- 新增 Cauchy-FFT script/results。radii .99/.985交叉檢查，N<=1000的 quiet minima與
  envelope整體下降但強烈振盪；最後 dyadic區間 minimum `1.41e-7`、median `9.10e-5`、
  maximum `7.70e-4`。
- 數值只證候選沒有在低 N立即失敗。LB要求 subexponential good blocks而非 fixed-rate
  exponential decay；高 off-line zero rate可為 order `(beta-1/2)/gamma^2`，有限掃描不能排除。
- 核心 obligation仍為 LB9.2。下一 producer測試：在完整 LM6.3兩腿上利用 actual local law
  `Lambda(p^j)=logp`尋找 cross-prime reflected identity。若只得 per-prime diagonal positivity、
  one-leg convolution或 triangle/Cauchy，立即記錄失敗並封存。RH未證；Goal保持 active。

### 下一棒的 uniform 驗收門檻

- L58/LM11：任何 positive producer須以 `kappa_N=exp(-o(N))` 的 coercivity同時控制 block內
  所有 coefficient vectors，且對 full eventual cutoff tail `Y>=Y_0(N,epsilon)`成立；可依
  epsilon,N，不可依 c或只沿 Y-subsequence。其 operator upper與 remainder亦須 `exp(o(N))`。
- LM12已排除 bare local Euler assembly：single-prime generating identity雖 exact，但
  per-prime PSD不含 cross-prime/continuum polarization，triangle/Cauchy常數隨 Y發散。
- 因此下一研究點不是再展開 Euler factors，而是尋找符合 LM11的 global cross-prime
  reflected/telescoping identity。LB9.2與Goal均保持 active。

- L59又證 pure log-ratio/reflection核 `h(t-u)` 也不等於 LB CD核。所以下一棒不可泛搜
  autocorrelation theorem；唯一精確 obligation是 nontranslation-invariant moving Laguerre
  CD projector上的 LM11-uniform centered prime quadrature。沒有新 comparison theorem前，
  這條路線保持 live但不得以換名增加進度。

## 2026-08-16 continuation：stationary family關閉，LB anchored端合流 W13/W14

- L60/LM14以 `R=(s-rho)/(s-a)` 證 Euler--Bohr normalized mean看不見單一離線因子，卻
  LB blocks fixed-exponential；故無 LM11 coercivity。
- L61把 Selberg sum、generic ratio與所有 normalized means統一為 stationary quotienting
  no-go。這是共同結構，不再逐一開 mean候選。
- L62 exact式：
  `(2pi i)^-1 int K'(z)z^-n dz=n a_n+sum ord_F(w)z_w^-n`。
  取 `r_N=1-N^-1/2`，boundary loss `exp(O(sqrtN))`，s-contour高度 `asymp sqrtN`且距
  critical line `asymp N^-1/2`。任何 off-line residue仍給 fixed exponential。
- 裁決：LB的唯一 nonmean producer與既有 W13/W14 anchored boundary-residue義務合流，不能
  以 finite-height/residue-free Cauchy estimate另算新路線。下一步應回到 contour shift前的
  centered prime--arch sharp identity；RH未證，Goal active。

### 合流量詞與外部相鄰定理裁決

- L63：A=每 epsilon有 unbounded LB good blocks，B=無 interior residues，C=W12.4 all-test；
  exact `A<=>B<=>C`。A failure是 nearest-shell syndetic coefficient excursions；C failure是
  W14單-orbit test。沒有 direct norm intertwiner或 LM11 coercivity constant。
- 因而下一棒不能以「W12等價」當 proof；仍須在 primes/gamma側構造 sharp anchored identity。
- named-gap外部檢索核對三個 primary sources：Bohr covariance為 reformulation、
  Connes--Consani為 archimedean-only、Scaling Hamiltonian明記 Li cutoff sign步驟失敗；沒有
  現成 W12.4 theorem。詳 ES163。Goal active。

## 2026-08-16 continuation：切換至獨立 DN nonlinear barrier

- residue三向等價只保留作防循環，不再算進展。新核心改為 DN varying-clock theta rigidity。
- L64/DN15：`phi(y)=y-log(1+y)` 的 pair-relative energy exact滿足 `gradE=-S`；finite window
  boundary-clock zero flow為 convex gradient flow，`E'=-2sumS^2`。Hessian及所有 constants
  uniform in window size，未假設 RH。
- DN16：`E<c_kappa=kappa-1-logkappa` 強迫 gaps `>kappa d`，且
  `E(t0)exp[2pi^2tau/(kappa^2d^2)]<c_kappa` 是 rigorous backward no-collision condition。
- checkerboard證 exponent sharp至常數極限；zeta高度仍需
  `exp[-(tau/2+o(1))log^2Gamma]` initial energy。最小未解項是 varying clock+buffer exact
  correction，以及 theta-side全 block bound。RH尚未證，Goal active。
### 2026-08-16 continuation：clock/buffer已算清

- L65/DN18：frozen nonuniform clock 的 exact force為 PV residual `S^y`；`n` 點 hard cutoff
  arithmetic clock有 `||S^y||_2 asymp sqrt(n)/d`，不能當 uniform endpoint error。
- DN19：moving clock另有 Bregman drift `-<H_y y',x-y>`；affine spacing drift成本為
  `|d'/d|sqrt(n(n-1)/2)`。naive local mean-spacing implementation至此嚴格排除。
- 存活 target：theta zero flow與 exact co-moving log-gas reference 作 centroid-aligned `ell^2`
  比較。其 energy有 `-4Lambda F<=F'<=0`，但 initial all-particle error仍須
  `exp[-c log^2Gamma]`。
- 下一步壓測 scaled Hermite-zero self-similar reference 的 bulk density、window size及累積誤差；
  Goal active，RH未證。
### 2026-08-16 continuation：Hermite/Polymath route audit

- DN21：scaled Hermite zeros是 exact finite log-gas，但 finite/infinite mismatch使 theta block帶
  exterior PV force；buffer norm仍 `asymp sqrt(n)/d`。Hermite最小失敗點已定位。
- ES164/DN22：Polymath 1904.12438 Theorem 1.5 給高零點 `O(x^(-ct))` rigidity與
  `x>=exp(C/t)` range。DN barrier需 `exp[-C t log^2x]`；一步少一個 log exponent。
- 多步 reset 只能到 `t~C/logx`，此時 theorem誤差不是 gap-scale。ordinary positive-time
  Riemann--Siegel asymptotic嚴格不足，但未證真誤差不可能更小。
- 下一條路線：first-collision count／Pontryagin-index 型 invariant；若仍依 projector convergence，
  則記回既有 P30 缺口。Goal active，RH未證。
### 2026-08-16 continuation：DN exact sharpness

- L67/DN23：`x_j=jd+(-1)^j a(t)` 是 exact nonlinear solution，且
  `sin(pi a(t)/d)=sin(pi a(0)/d)e^(-pi^2t/d^2)`。取 `a(0)=d/2` 在 0 collision，
  terminal訊號仍僅 log-squared exponential。
- 故 DN energy exponent不是估計鬆弛；所有 clock附近連續 terminal collision counters均由此
  反例。只有 topological/history invariant存活；P30已知卡 actual projector convergence。
- DN smooth-terminal主線至此嚴格排除。下一階段不得再換 norm重做同一件事。
### 2026-08-16 continuation：new Goal margin/resultant phase

- L68/DN24：checkerboard no-go正確形式為 `m_d<=omega_d(epsilon_d)`；fixed margin不穩定，
  shrinking margin若與訊號同速則未排除，但須 `o(m_d)` arithmetic precision。
- L69/DN25：finite polynomial已有 exact spacetime discriminant/Sturm collision counter，time degree
  至多 `n(n-1)/2`。
- DN26：terminal locally-uniform polynomial approximation不在 backward heat下收斂；explicit
  monomial perturbation terminal趨零而過去 constant term為1。故 naive Taylor/Jensen resultant transfer失敗。
- 下一 named obligation：找 theta-specific weighted entire norm，使 `e^(TD^2)` 與 canonical
  resultant/Fredholm regularization同時收斂；否則本線回到 P30 actual determinant gap。Goal active。
### 2026-08-16 continuation：topological collision degree

- L70/DN27：`F=(H,H_x)` 在 `(t,x)` rectangle的每個 regular collision orientation皆
  `-H_xx^2`；所以 boundary winding exact、無抵消地計 collisions。degenerate情形以
  `alpha+beta x` transverse heat perturbation定義 multiplicity。
- 此 invariant避開 smooth terminal norm與 infinite resultant，為目前存活主線。
- DN28：certification仍依 boundary gap `mu_R`；expanding rectangle公式若只化成 time-0 real-zero
  count就是 RH改寫。下一步必須從 theta integral直接給 vertical+bottom boundary homotopy及 margin。
- Goal active，尚未證 RH。
### 2026-08-16 continuation：boundary phase reduced to arithmetic sign

- L71/DN29：positive/even/smooth/super-exponential heat kernels仍可 generic collision；generic Fourier
  positivity route已排除。
- DN30：`H_t+iH_t'` 的 Fourier density exact為 `(1-u)e^(tu^2)Phi(u)`；bottom為
  `[2xi-xi']/16`，包含完整 prime logarithmic derivative。
- ES165沒有 adjacent phase-homotopy theorem。topological counter仍存活，但唯一核心 obligation現為
  theta/primes直接控制 expanding rectangle的 signed boundary phase與 nonvanishing margin。
- Goal active；不得把 degree identity或 gamma-only phase當 RH進展。
### 2026-08-16 continuation：degenerate collisions closed

- L72/DN31：multiplicity m collision經 parabolic scaling收斂到 Hermite model，local degree
  `-floor(m/2)`。所以 DN27 winding exact計生成的共軛 pairs，無需 regularity假設。
- nonzero analytic heat solution沒有 persistent multiple-zero curve；compact內事件離散。
- topological ledger本身現已閉合；唯一 live obligation仍是 DN30 signed arithmetic boundary phase。
### 2026-08-16 continuation：boundary-phase producer closed

- L73/DN32：320-bit Arb certificate證 actual Xi的
  `partial_t arg(H_t+iH_t')` 在第1與第35零點反號；vertical monotone homotopy嚴格為假。
- L70/L72 collision-degree theorem與此符號無關，仍為正確 ledger。
- DN33/ES166：horizontal phase只給 first Laguerre inequality，一般不充分；full version回到既有
  all-degree Jensen/de Branges target。
- spacetime winding的兩個 natural producers均已排除；任意 nonmonotone homotopy尚邏輯可能，但目前
  只會重述 bottom real-zero count。這是本階段最小失敗點與可續接邊界。

### 2026-08-16 continuation：修正完成誤判；三路合流但 Goal active

- L74/DN34證 theta terminal Fourier topology下 finite positive rational quadratures對
  `(H,H_x)`作 fixed-rectangle `C^1` convergence；boundary gap為正即傳遞 degree。故 DN26只關閉
  polynomial/Taylor transfer，不能關閉 non-naive entire transfer。
- L75/DN35把 commensurate quadrature寫成 rational Laurent polynomial；compatible rectangle的
  winding可由 exact Sturm/subresultant Cauchy index決定。finite decision本身也不再是缺口。
- hidden dependencies：量詞是先 R、後 margin、再 cutoff；`t=0` raw gap暗含 zero simplicity，應取
  regular `tau_n>0`。DN23顯示 cutoff未必 uniform，DN29顯示 positive rational weights仍可 collision。
- L76/DN36證 regular expanding rectangles的 degree全0 iff RH。因此共同支柱沒有嚴格弱化問題；
  三路只閉合技術 transfer，不能以此宣稱接近證明。
- DN route在沒有新 theta-specific signed identity前封存。下一棒切回仍未被反例關閉的 AP2.5，
  第一步只查其 target-specific norming inequality是否也經 bounded inverse直接等價RH；若是就停止，
  若否才壓測 polynomial cost。RH未證，Goal保持 active。

### 2026-08-16 continuation：AP2.5亦為 RH-equivalent，暫不切回

- L77/AP8/SC17證 AP2.5/SC16.8 iff RH。正向是既有 beta-tail closure；反向在RH下先取 finite
  global approximants，再把 window T選到 `T^A>=K`，local error由 global error控制。
- 這正是 SC8/SC10早已記錄、後續 handoff遺失的量詞。remote support允許且 delta無指定速率時，
  polynomial-in-T可完全重參數化，不能算 independent leverage。
- 因此不再切回 Pechersky/AP2.5。避免此坍縮的候選必須在 approximant之前固定自然 scale，或有
  prescribed rate；explicit MB1符合 scale要求但已於 L51/strategy95回到 signed same-scale Möbius gap。
- 下一步：只做 research index 的 reparameterization-immunity篩選，選出尚未等價坍縮且有可證中介
  theorem的一條。RH未證，Goal保持 active，絕不標完成。

### 2026-08-16 continuation：全索引 reparameterization-immunity 篩選

- L78一般化 AP8：只要 global closure存在，任何 finite cost都能藉後選更大T滿足任意 unbounded
  `g(T)`；local error由 global error控制。free-window complexity bound因此沒有獨立尺度內容。
- AP2/kappa被此 filter關閉為等價 endpoint；LB/W13與DN則已有 L63/L76 iff RH裁決。DN36另補
  DN22 uniform high-zero exterior，排除 collision從 spatial infinity逃過 compact ledger。
- MB1是唯一明示 `X=T^B`、免疫 scheduling的 approximant，但 L51已把其最小剩餘項定為
  same-scale signed Möbius-prime-Abel joint cancellation，現有三個 producer均失敗。
- spectral/canonical-system方向尚無 primes/theta先定義且可驗收的 positive domain/operator，不能列
  active lemma。這只是目前 project index的嚴格篩選，不是窮盡所有RH證法。
- Goal保持 active且不標完成。下一個候選必須先通過 L78，再接受反例、uniform-in-degree與量詞壓測。

### 2026-08-16 continuation：L78 escape確認與 gauge route裁決

- L79給最小 `ell^2`反例：global closure與 free-window approximation成立，但 natural cutoff下
  `E_N asymp N^-1/2`，所以 prescribed `T^-1` rate失敗。L78只是 filter，rate-coupled route可有
  真正新增內容。
- L80/DN37：`wind(AF)=wind(F)+ind(A)`；任何延拓至rectangle的 `GL^+(2)` gauge有 index 0，
  degree不變。不可延拓 straightener的 index就是未知 winding；singular gauge則以
  `sigma_min(A)`丟失 boundary margin。
- L81/DN38：所有 `(H,H_x+aH)` shears在 simple zero保留 vertical velocity `H_xx/H_x`，故
  DN32 actual反號不能用 gamma/log-derivative normalization修掉。
- 此結果只關閉 coordinate/gauge型 nonmonotone producer；直接 theta-arithmetic nonvanishing homotopy
  仍邏輯可能。Goal保持 active，下一候選仍須通過 L78與 gauge-index audit。

### 2026-08-16 continuation：finite theta truncations全部排除

- L82/DN39與 Arb script證 first-mode transform有 simple nonreal zero；它不是 LP base。
- L83/DN40與第二份 Arb script證 `T_1+lambda T_2`直線在 `lambda=0.916291688...` 發生
  regular amplitude collision。第二 mode不是可保 nonvanishing的小 perturbation。
- L84/DN41給全N解析 no-go：finite partial kernel在0留 `K_N'(0)>0` modular cusp，transform
  沿 real axis為負 `x^-2` tail，real zeros有限；order<=1 Hadamard則證 nonreal zeros無限。
- 因而 defects只可能隨N逃向無窮遠；任何 finite theta truncation都不能作 collision-free reference。
  這不否決 DN34 general degree transfer，也不決定 full infinite Xi。
- 下一棒只接受從起點保留 exact modular completion的自然尺度 construction；mode coefficient繞路
  還須另證避開 collision wall。RH未證，Goal active，不標完成。

- L85/DN42補上 path-topology裁決：任意 nonzero finite real theta combination都因未完成的 modular
  boundary jet而有 fixed-sign algebraic Fourier tail，並有無限 nonreal zeros。finite mode span與 LP
  cone只交於0；所以不論直線或非單調 detour皆不能提供 collision-free endpoint。
- 下一條合格 deformation必須在每個參數值都已是 infinite modular completion；Goal繼續 active。

### 2026-08-16 continuation：horizontal-shift infinite modular audit

- 以 `Xi(x+ia)=A+iB` 測試 genuinely infinite family。L86/HS12證 `(A,A_x)` collision orientation
  可正可負；explicit harmonic quadratic在同一路徑已有相反 local degrees。
- L87/HS13改用 analytic pair `(A,B)`可得 one-sign `|Xi'|^2`，但 degree逐字是 Xi zeros的
  argument-principle count；regular strip exhaustion zero-degree iff RH。
- 因而 HS在 topology層沒有中介優勢：要麼 cancellation，要麼直接RH endpoint。只有新的
  theta/prime coupled Bezoutian identity才可重開 HS5。Goal保持 active，不標完成。

### 2026-08-16 continuation：HS5 existence schema降級

- L88/HS14證：未先指定 `T_a,L_a` 時，`K_(a/2)=T_a[K_a]+L_a` 的存在式與
  `K_(a/2)>=0` 等價；反向的平凡 witness是 `T_a=0,L_a=K_(a/2)`。
- 因此「需要 coupled Bezoutian identity」只是驗收規格，不是目前已有內容的候選 lemma；HS5在
  出現不使用 target positivity定義的 theta/prime operator/remainder前封存。
- 下一棒回到通過 natural-scale filter 的 MB1 test form，先查其量詞是否再坍縮成 global
  Nyman closure，以及有無獨立 rate內容。RH未證，Goal保持 active。

### 2026-08-16 continuation：MB1 window/global 與文獻量詞裁決

- L89/AP9：對 `0<B<2m+1`，window外 tail自動 `o(1)`，所以 MB1 iff同一 explicit
  Riesz--Mobius family的 global norm沿某 `X_j->infinity`消失；T與B只是截窗參數。
- Burnol support lower bound給 squared error `>=c/logX`，因此 polynomial prescribed-rate版本
  不可能，L79型 rate escape不能直接用在這族。
- 定向外搜只服務此反向 lemma：Báez-Duarte 2002列出相同 Selberg log weight但改用 varying
  power tilt完成 conditional construction；Conrey--Myerson 2000的 uniform sawtooth theorem仍在
  endpoint weighted L2卡住，且所述收斂另需 zero separation。沒有 RH-alone反向可移植到含
  `a_X` Abel correction的 MB1。
- MB1保持 explicit test form但沒有獨立 producer；唯一未解式仍是 AP7.2 whole signed square。
  RH未證，Goal保持 active。

### 2026-08-16 continuation：MB1 residue producer的 multiplicity audit

- L90/AP10/G252/strategy125核對 Bettin--Conrey--Farmer arXiv:1211.5191：conditional optimal
  rate使用 `sum|zeta'(rho)|^-2` bound，已隱含全部 zeros simple；RH本身不含 simplicity。
- multiple zero若改以 higher Laurent principal parts處理，會新增至 multiplicity階導數的 uniform
  bounds，不能把 hidden dependence消失。
- 因此 known optimal-polynomial theorem不能補 MB1的 RH-only converse，更不能作無條件 producer。
  AP7.2必須 separation-free地閉合；RH未證，Goal active。

### 2026-08-16 continuation：AP7.2 internal producer audit

- L91/AP11 exact證 `R_(e^L)=L^-1 integral_0^L Q_vdv`，其中 `Q_v`是 sharp
  Abel-corrected Möbius residual；所以 fixed-log smoothing的全部內容是 cross-scale cancellation。
- energy derivative為 `(2/L)(Re<A_L,Q_L>-||A_L||^2)`，generic無固定號；scalar `1,-1,1`
  step path使 energy先降後升。Jensen只回到更強 sharp-error estimates。
- 因此 AP7.2現在沒有非文獻 producer。只有先給不使用 critical reciprocal/zero exclusion的
  Möbius-specific cross-scale correlation identity才可重開；double-integral改寫本身不算。
- MB1在此最小失敗點封存。Goal保持 active；下一條須是新的 natural-scale explicit construction。

### 2026-08-16 continuation：Pólya geometric interpolation certified no-go

- 立即可算候選取 `Phi_s=exp((1-s)log P+s log Phi)`，`P=e^(-2pi cosh u)`；起點 transform
  `K_(ix)(2pi)`全實零，終點為 Xi kernel。
- 低階 Jensen (`degree<=8, shift<=40`) 全過但 worst case黏在最大 shift，沒有尾部控制。
- `experiments/certify_polya_geometric_collision.py` 以256-bit Arb、theta-tail與 `u>=3` 尾球、
  2D Krawczyk嚴格證明 `(s,x)=(0.0031021250408869274...,13.165805196244539...)`
  附近有唯一 regular `H_s=H_x=0`；Jacobian排除0，且 `Hs,Hxx<0`。
- 因而第二、三 real zeros在 s增加時成對離開實軸。這條表示切換已嚴格排除；不要改用另一個
  scalar interpolation law續命。下一棒只接受表示本身帶有 collision-exclusion identity的候選。
  RH未證，Goal active，不標完成。

### 2026-08-16 continuation：A0 rank-one boundary candidate certified no-go

- 非 homotopy候選取 P3 exponential-wall self-adjoint core `A_0`，嘗試以 energy-independent
  rank-one boundary condition產生 Xi determinant；必要條件是 Dirichlet/target spectra逐 gap交錯。
- `experiments/certify_bessel_core_interlacing_failure.py` 以 Arb interval Newton及 rigorous
  `zeta_zero` balls證 `beta_3<gamma_4<gamma_5<beta_4`。一個 consecutive core gap已有兩個
  Xi zeros，故 rank-one representation嚴格失敗。
- 這不排除 singular/infinite-rank domain change或 independent arithmetic operator。下一棒只接受
  先驗給出 domain、positive norm、resolvent/projectors與 determinant identity的具體候選；抽象
  self-adjoint existence仍循環。Goal active，不標完成。

### 2026-08-16 continuation：all fixed finite rank A0 perturbations excluded

- 低端 probe 到 `T=1000` 給 `0<=N_Xi-N_A0<=2`，所以 rank-two finite evidence存活；不可由此
  推全域。
- Dunster Bessel phase給 `N_A0=M(T)+O(1)`；Riemann--von Mangoldt給
  `N_zeta=M(T)+S(T)+O(1)`；Dobner unconditional omega theorem使 S positive unbounded。
  因而 counting discrepancy無界。
- 任 fixed-rank self-adjoint resolvent perturbation或 finite-deficiency domain extension的 counting差
  由 rank有界，故全部排除。P19剩餘範圍現嚴格縮為 genuine singular/infinite-rank domain或
  independent arithmetic operator，且必須先驗給 actual resolvent/projectors。Goal active。
- min--max另排除所有 bounded additive `A_0+V`（故含 trace-class/Hilbert--Schmidt）：A0 energy gaps
  趨無窮，bounded shifts只容 eventual counting差至多1，和 S-omega無界矛盾。存活 P4 必須是
  unbounded but resolvent-comparable domain change。

### 2026-08-16 continuation：single-channel prime scatterers excluded

- 具體 singular候選：在一份 A0 channel 的 `L_p=logp/2` 放 self-adjoint point scatterers；單 prime
  boundary orbit length正好 `logp`。
- exact two-point determinant含 `-g_2g_3G_23^2`，其 WKB exponent length為
  `2(L_3-L_2)=log(3/2)<log2`。Euler log只含 `m logp`，故此最短 mixed-prime orbit無處抵消。
- 同 channel local construction嚴格排除；separate-channel版本已有 P9--P10 Weyl density no-go。
  尚存者必須 nonlocal 地禁掉所有 distinct-prime paths、保留 same-prime powers，且只有一份 arch
  phase volume。Goal active，不標完成。

### 2026-08-16 continuation：prime-space nonlocal projector excluded

- local defect有 exact positive weighted model，但 generator滿足
  `A_p=-I/2+K_p`, `K_p^*=-K_p`；spectrum正是 `-1/2+2pi i Z/logp`。
- 此 scalar real drift在任何 reducing positive subspace或 compatible Hilbert cohomology quotient中
  不變，uniform in prime cutoff。平移到 imaginary axis會把 Euler factor從
  `1-p^(-1/2-x)`改成 `1-p^-x`。
- 因此 prime defect space內的 nonlocal positive projector已排除。較大 unitary dilation只把 Euler
  zeros當 resonances；尚存者須是 explicit singular arch--prime coupling，帶新 positive norm、
  self-adjoint induced generator與 absolute determinant identity。Goal active，不標完成。

### 2026-08-16 continuation：modewise arch--prime pairing fails only at infinite cutoff

- finite 2x2 block `L=[[-1/2,q],[-q,1/2]]` 在 `q>1/2` 有 explicit positive G且 G-skew；
  所以 drift cancellation不是空泛要求。
- p-circle frequencies `2pi k/logp` 經任意 blockwise shift `c_p`後，仍有一點距0至多
  `pi/logp`。p趨無窮即在0產生 infinite spectral accumulation，resolvent不 compact。
- 因而 finite prime cutoffs可全正且全實譜，卻沒有 determinant-class infinite limit。下一棒只能找
  cross-prime nonlocal mixing；它還必須避開 P40 forbidden mixed orbit。Goal active。

### 2026-08-16 continuation：positive cross-prime determinant mixing excluded

- natural block `K_pq(s)=e^(-s(logp+logq)/2)B_pq` 的 second log-det cumulant在 length
  `log(pq)` 給 `||B_pq||_HS^2>=0`。
- Euler log對 p不等於q的 pq係數為0；unique factorization排除其他 cycle同長取消。因此 exact
  Euler determinant迫使 `B_pq=0`，不能使用 P42 所需 cross-prime mixing。
- 合併裁決：block diagonal有0 accumulation；positive cross mixing有 forbidden cumulants。
  determinant-class/orthogonal-prime/length-covariant整族關閉。下一候選必須明示破壞哪項並仍提供
  positive spectral projectors；只寫 zeta regularization不合格。Goal active，不標完成。

### 2026-08-16 continuation：positive Euler determinant realization is uniquely diagonal

- 不假設 prime sectors orthogonal。若 `K(s)=sum p^-sA_p`, `A_p>=0 trace class` 且 determinant
  exact為 `product(1-p^-s)`，Dirichlet coefficient comparison給
  `TrA_p=TrA_p^2=1` 與 `TrA_pA_q=0`。
- positivity遂強迫每個 A_p為 rank-one projection且不同 ranges正交。故任何 positive realization
  都退化為 obvious prime diagonal operator，不能用 hidden nonorthogonal mixing逃 P42/P43。
- ordinary positive determinant route至此整類關閉。只剩 signed/super、regularized或真正非
  trace-class constructions；前兩者已有 P22、P31--P33最小失敗點。Goal active，不標完成。

### 2026-08-16 continuation：P21 explicit prime-operator route closed

- `prime_operator_trichotomy.md` 統一三類：positive determinant由 P44/P41--P43關閉；fermionic
  superdeterminant由 P22/P25關閉 ordinary Hodge；Schatten regularization由 P31--P33關閉
  spectral-projector解讀。
- 所以目前 strongest explicit prime-operator route已嚴格排除並完成可續接 handoff。未明示 norm/
  domain/projectors的「singular cohomology」不再列 active candidate，也不宣稱所有未知 operator
  construction已排除。
- Goal暫維持 active；下一棒必須換表示並先給可立即反駁的 concrete object，不能再改寫 P21。

### 2026-08-16 completion audit correction：terminal not met

- `COMPLETION_AUDIT_2026-08-16.md` 逐條核對 Goal。RH未證。
- P21 strongest explicit prime-operator route不是單點 producer失敗，而是 positive determinant、
  ordinary super/Hodge、standard regularization三類皆有整類 no-go與最小失敗點。
- 但「尚未給 concrete singular norm/domain」只表示沒有 producer，不等於 singular route class已被
  嚴格排除。第二終止條件因此未滿足，撤回 complete判定。
- Goal保持 active；下一步直接測 translation-compensated arch--prime differential，而非等待抽象構造。

### 2026-08-16 continuation：translation-compensated Hodge sharp no-go

- prime creation配 arch unitary translation，exact有 `Q^2=0,[H,Q]=0` 與
  `{Q,Q*}=sum p^(-2sigma)I`；此候選避開 ordinary Hodge的 unique-energy obstruction。
- 最小 finite audit：一個 prime在 `l2(Z)` 可同時保 dense domain、fixed weight、compact resolvent；
  但兩個 primes的 eigenvalue orbit `lambda-Zlogp-Zlogq` 因 log ratio irrational而稠密，故不 locally
  finite。global unitary translation route在兩 primes即失敗。
- infinite critical `sigma=1/2` 又因 prime harmonic divergence使自然 Q domain不 dense；cutoff
  normalization則消滅每個 fixed prime weight。
- 推導見 `translation_compensated_hodge_audit.md`、P45、strategy136、G262。Goal仍 active；下一候選
  不得再靠 additive log-prime spectral shifts，否則直接繼承 two-prime dense-orbit obstruction。

### 2026-08-16 continuation：unilateral repair exact experiment

- 已依照「不要再寫同一障礙」實作 `experiments/probe_unilateral_prime_hodge.py`；exact rational runs
  對1、2、3 primes全部 PASS。
- backward boson shifts確實避開 P45 dense orbit，並保 `Q^2=[H,Q]=0`、dense domain及 locally
  finite spectrum；但每條 ladder的 trace `(1-p^-s)^-1` 精確消掉 fermionic Euler factor。
- finite box cohomology為 boundary corners，supertrace
  `product_p(1-p^(-(N+1)s))->1`。因此雙向 additive shifts死於 dense orbit，單向 shifts死於 exact
  Euler cancellation。
- Goal仍 active。下一候選必須非 additive log-prime ladder，並先提供 executable observable。

### 2026-08-16 continuation：local prime convex transport screen at 7--8

- 非 operator-shift候選直接使用 Suzuki B46 measure：為每個 `p^k` 從 pole density
  `e^(u/2)+e^(-u/2)` 切一段等質量、重心 `log(p^k)` 的 parcel；若 parcels互斥，Jensen即證
  `g_0(t)<=0`。
- `certify_prime_convex_transport_7_8.py` 以256-bit Arb/Krawczyk嚴格證第一 overlap在7與8的 local
  pair已出現，正下界約 `0.02495043580109537726`。
- 合併7、8後，Arb證唯一 interior hinge minimum約 `0.004585789715459631845>0`；outer pieces由
  monotonicity非負。因此 pair cluster嚴格存活；仍未證 uniform cluster size或 infinite transport。
  結果見 `experiments/probe_prime_convex_transport_results.md`。
- scope correction：P46 Euler cancellation只對 complete one-sided tensor ladder通用；`[H,Q]=0`
  單獨不推出 cancellation，finite ladder的反例因子是 `1-p^(-(N+1)s)`。

### 2026-08-16 階段收尾（terminal not met）

1. **嚴格排除**：P45 global unitary translation在兩 primes產生 dense eigenvalue orbit；critical
   strong-sum domain不 dense。P46 complete one-sided tensor ladder exact消去 Euler factor；finite-box
   boundary formula亦為代數恒等式。這些結論不擴張到所有 `[H,Q]=0` differential。
2. **P47已嚴格完成**：256-bit Arb/Krawczyk證 single parcels在7--8有正 overlap；merged 7--8
   cluster的唯一 interior hinge minimum亦有正下界，配合 outer monotonicity得到全部 t 的 inequality。
   這只裁決 minimal single/pair case，不是全域 clustered theorem。
3. **仍未閉 obligation**：clustered parcels能否以 uniform complexity覆蓋所有 prime powers並保持
   disjointness與全部 hinge inequalities；更上層的 DN30 arithmetic boundary phase/B46 global sign仍未證。
   P47/G264只是一個 branch-specific producer，不是三條原始路線的共同機制；共同 obligation仍是
   expanding arithmetic zero-degree。
4. **下次最值得續接**：實作 deterministic greedy cluster sweep，優先量測 cluster size與 hinge minimum
   隨 prime height的衰減；若 margin趨0，uniform route直接失敗。只有 finite screen存活後才找定理。

黎曼猜想仍未證明。這只是階段交接；原始 Goal未完成、目前依使用者要求 paused，未達任何
terminal condition；下次可由上述第4點恢復。
