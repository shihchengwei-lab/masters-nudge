# 尚未閉合的缺口

## G1：Li 係數的無條件控制（核心）

`analytic_foundations.md` 已由 ξ 的對稱 Hadamard 分解推導 Li 零點和，並僅以一階整函數的粗計數完成 L5。逐項 `λ_n≥0` 是原始充分目標；D6 已縮弱為只需 η 二項變換的負部次指數，M1 又轉成 Chebyshev 加權均方。三者目前皆無無條件證明。

## G2：Li 和式的合法重排

`analytic_foundations.md` 已指定完整對稱軌道與高度極限；L5 的高尾在四元組層級絕對收斂。仍禁止把未配對的逐零點條件收斂和任意重排；若後續改用不同測試函數，必須重新證明其收斂合法性。

## G3：正性核／算子尚未構造

可能方向是把 `λ_n` 寫成顯然非負的積分、平方範數或正算子的二次型。但任何候選表示都必須逐步核對等號、邊界項與核的符號；目前尚無有效構造。

## G4：可能的等價改寫／循環

「證明所有 Li 係數非負」本身是 RH 的等價路徑。若候選估計的關鍵假設已隱含零點在臨界線，必須判為循環，而不是進展。

## G5：Fourier 核所需的強結構未知

`positivity_kernel.md` 已以 Gaussian 混合反例證明：嚴格正、偶、實解析、Schwartz 核仍可有非實 Fourier 零點。Xi 核若要導出 RH，必須證明更強的全正性或等價結構；目前既無精確選定的充分定理，也未驗證其假設。

## G6：Li 次指數上界

`li_radius_criterion.md` 證明 RH 等價於 `limsup|λ_n|^(1/n)≤1`。這比逐項正性弱，但仍缺少無條件係數估計。ξ 的一階整函數增長不能跨過 `log ξ` 在未知零點造成的極點；Euler 乘積映到 z 平面也只覆蓋 `|z-1/2|<1/2`，不足以控制整個單位圓。

## G7：算術二項變換的消去

`li_arithmetic_decomposition.md` 已證 `A_n=(n/2)log n+O(n)`，並將 RH 等價縮成 `E_n` 的負部沒有指數成長。D7 已建立合法 Abel–prime–Laguerre 公式，但尚無在 n、δ 聯合極限下保存極點–質數消去的單側界 `E_n≥-exp(o(n))`。

`li_syndetic_excursions.md` 的 LS1 又證：RH 假時負指數 `E_n` 不是任意稀疏
子序列，而是 syndetic（有界間隔）。所以逐項 `E_n>=-exp(o(n))` 可放寬為：
對每個 epsilon，`{n:E_n<-exp(epsilon n)}` 只須有 density zero；等價地只須
在任意靠後位置找到任意長的好 block。這是新的嚴格放寬，但仍缺能由
D10.3 的 signed Laguerre arithmetic 無條件推出該密度／block 結論的估計。

## G8：η 完全單調性路徑已否證

`eta_complete_monotonicity.md` 已用 Laplace 測度的負質數冪原子嚴格否證 h 的完全單調性；其抽象 `h_a(x)=1/(a+x)` 反例又證完全單調性即使成立也不足以控制 η 的 binomial transform。此路徑已封閉。

## G9：Chebyshev–Laguerre 帶符號投影

`chebyshev_laguerre_kernel.md` 已將 E_n 寫成 `A(x)=x-ψ(x)` 對 Laguerre 核的 Abel 投影，並證純冪 `x^θ` 在 θ=1/2 發生精確相變。點態界 `A=O_ε(x^(1/2+ε))` 本身已等價導向 RH；對核取絕對值則丟失臨界振盪。尚無介於兩者之間、可由算術直接證明的單側投影界。

## G10：Chebyshev 加權均方

`chebyshev_mean_square_criterion.md` 證明，對任意 p>5，`∫|ψ-x|²/[x²(log x)^p]dx<∞` 等價於 RH；特別地 `∫_2^X|ψ-x|²dx=O(X²log^B X)`、B<5 即足夠。尚無無條件證明達到 X² 尺度；引用任何此類均方界前必須稽核是否已假設 RH。

M4 把此缺口精確化為 `Λ(m)-1` 前綴和的平方總和，亦即 Gram 核 `N-max(m,n)` 下的二階相關消去。PNT 只給前綴 `o(N)`，M5 已用抽象序列證明這不足。
M6 已證對角項僅 `O(N²log N)`；全部難度位於位移相關 `C_h(Y)` 的雙重和。逐位移粗界無法達標，尚缺跨 h 的整體消去機制。
M7 的 Fourier 恒等式把同一缺口定位成 `Λ-1` 指數和的零頻局部 L² 質量；普通 Parseval 與 PNT 單點值都不足。

M8 又把前綴平方分解成 dyadic 區間方差。若所有尺度 H 都有 `V(N,H)=O(Nlog^βN)`、`β<4`，即可推出 RH；但 `H≈N` 的條件本身已要求平方根尺度的長區間誤差。短區間平均結果不能在沒有新論證時補上這個大尺度缺口。
M9 以先正後負的零總和序列嚴格證明：即使所有 `H≤H_0=o(N)` 都有理想方差 `V≤N`，前綴能量仍可達 `N³/H_0≫N²`。缺口因此確定在長尺度／跨尺度算術結構。

## G11：受約束分數部分函數／Möbius 近似

`nyman_beurling_route.md` 已離線證明：若受約束的有限分數部分函數組合能在 L²(0,1) 逼近 1，則 RH 成立。自然 Möbius 近似器的誤差由 NB3.4 精確分成 `(N-H_N)A_N²` 與非負截斷除數卷積尾，因此至少需要 `sqrt(N)A_N→0`。NB5 又把首個尾區間化為長度 N 的 Mertens 增量平方。兩者目前都沒有無條件趨零證明；利用 `1/ζ` 在右半臨界帶解析來估計會循環。

NB6 將受約束基底精確離散化，有限維最佳距離為 `d_N²=1-v^TG^(-1)v`。數值呈現約 `const/log N` 的尺度，但解析證明 `d_N→0` 本身已足以推出 RH；目前缺少能控制 Gram 逆矩陣且不偷渡 ζ 無零性的結構。

NB9 的端點修正可在前 N-1 點精確插值 1；NB10 證其首個尾區間仍是 Mertens 增量平方。縮小誤差支撐不能免除振幅／長尾控制。

NB11 證明 `d_N` 正是臨界線上受約束 Dirichlet 多項式 mollify `-1/ζ` 的加權 L² 誤差。NB12 已用精確有理反例排除 Gram 對角占優與全正性；不能靠這兩種一般矩陣逆界完成 NB7。

## G12：Xi 核偶矩／Jensen 階層

`xi_jensen_route.md` 的 J1 把 RH 的充分目標定為所有階 Jensen 多項式 hyperbolic。J2 將全部二次條件化為偶矩比；J4 證明 score 比率 `q=-Φ'/(uΦ)` 單調即可推出這整個二次族。J6 與 J7 的有向外捨入證書已完成全域 `q'>0`，所以全部 shifted degree-2 Jensen 不等式現已證明。

J8 顯示 degree 3 另需相鄰 Turán 比率滿足二變數判別式 `F(U,V)≥0`；單有 `U,V≥1` 不足，且 `(1,1,1,1/2)` 給精確反例。degree 任意增長的統一 hyperbolicity 仍是核心缺口。

J10 更證明一般單調 score 也不足：`f_ε=e^(-u²-εu⁶)` 有嚴格遞增 q，但充分小 ε 的 degree-3 判別式為負。J11 把 Xi 的 degree-3 缺口精確化為相鄰 tilted 協方差 `C_k,C_(k+1)` 的變化率不等式；目前未證。

J10 的 q 甚至所有導數皆非負，故一般 convexity／高階導數符號也不足。J12 給出較強但簡單的充分遞推 `C_k(1-4C_k)≤C_(k+1)≤C_k`、`C_k≤1/12`；數值至 k=200 通過，但尚缺對所有 k 的解析證明。

J14 以精確位移 `T_n(u)=n^(-1/2)T_1(u+log n)` 證明高 theta 項對第 2k moment 的相對貢獻為 `e^{-c k/log k}` 級。故充分大 k 的 J12 已嚴格降到 n=1 saddle；剩餘缺口是對該單項 moment 的相鄰 log 差分給多項式級顯式餘裕。

J15 已證第一 theta 項每個 moment 有唯一 saddle，並給位置、曲率及三、四階導數的顯式界。J16 的離線比較提示 `C_k=C_k^(0)[1+3/(2k)+O(k^-2)]`，但尚未推導該修正，亦未證可承受相鄰差分的顯式餘項。由於 J12 餘裕本身為 `k^-2` 級，一般的相對 `O(1/k)` Laplace 估計仍不足；有限 k 最後也需要有向區間證書。

J17 已把這個要求精確化：`D_k=Δ²log A_k` 是 tilted `log u` 方差的三角平均，而 `D_(k+1)-D_k` 是第三累積量的平均；J12 等價於 J17.5–J17.6 的明確 corridor。尚缺能同時給 size 與相鄰差分的 enclosure。J18 證明 log-u 密度在極左尾並非 log-concave，因此不能直接以全域 Brascamp–Lieb 關閉缺口；可行的局部版本還須證左尾誤差足夠小。

J19 已完成上述第一半：切在 `u=10^-2` 後主區域顯式強 log-concave，左尾質量及前三個 log raw moments 有 `10^(-4t)` 型封閉界，對 t≥20 足以忽略於任何多項式級 J12 餘裕。仍缺的是主區域隨 t 增長的 sharp 局部曲率展開，以及把它轉成方差和第三 cumulant 的上下界；僅用 J19 的固定強凸常數太粗。

J20 已給真正 log-u mode 的精確曲率與參數導數；J21 找到數值上達相對 `O(k^-2)` 的第一 cumulant 修正。核心未閉合點現縮成：在一個隨 k 選取的 mode window 內，對五階以上 Taylor 項給一致 majorant；在 window 外用凹性給 exponentially small tail；並讓所得 remainder 經 k 的相鄰差分後仍足以保住 J12 約 `k^-2` 的 margin。

J22 已提供任意固定階導數 majorant，J23 已證主區域曲率隨 log-u 嚴格增加。剩下的技術工作不再是導數符號，而是選擇 window 並把左右尾與 Taylor remainder 的常數壓到 `o(k^-2)` 的 J12 margin 以下。此外，`F'''<0` 是否足以推出整個 tilted 分布 `κ_3<0` 尚未在本文證明，禁止直接使用。

J24 已證 `w_t=logt/sqrtΛ_t` 使左右尾超多項式小，且 window 內任意固定階 Taylor 項都有明確漸近 majorant。未閉合部分縮成兩個可稽核項目：(i) 把六階展開的 normalization、mean、二階矩交叉項全部 enclosure 成 J21.3 的 `O(t^-3 polylog t)` 餘項；(ii) 從粗常數算出一個有限起始 T，讓區間證書只需覆蓋 `k<T`。

J25 已精確完成六階 Gaussian 的 normalization、mean、raw second moment 與 variance 交叉項，並給出局部 weight 截斷的顯式誤差 `88theta^5+5rho`。尚未閉合的是把截斷 Gaussian 多項式尾、J24 外尾、J19 左尾全部轉成同一 normalized cumulant enclosure，及由粗常數算出實用的顯式 T。即使這完成，也只關閉 degree 3；目前沒有從 cubic Jensen hyperbolicity 推到所有 degree 的轉換引理，這是獨立的全階缺口。

J26 已給局部條件的第一個數字門檻 `T_0=10^24`，並以整數算術核對。它只證 J24 window 與 J25 weight remainder 在此後合法，尚未證 J17 corridor；而且門檻大到不能與逐 k 區間證書實用接合。降低門檻本身不是邏輯必要，但若不保留 `r≈t/β` 及 Gaussian 加權，有限段驗證將不可行。

J27 已顯式控制 J25 Gaussian 多項式由 window 延伸到整線的尾誤差，以及真密度在 J24 主區域左右外尾的 0 至 3 階 mode-centered moments。現在 degree-3 大 t enclosure 的技術缺口只剩：把 J19 極左尾、J25 局部 remainder、J27 tails 經共同 normalization 傳到 central variance／third cumulant，並核對 J17 corridor 的符號 margin；尚不可從各 raw bound 直接宣告 cumulant 符號。

J28 已完成主區域共同 normalization 的誤差傳播，給 variance 與第三 cumulant 的顯式有理 enclosure；它刻意不使用未證的 `F'''<0⇒κ_3<0`。剩餘 technical bookkeeping 是把 J19 極左尾作 mixture perturbation 加回。真正的符號工作則是證 J28 的中心多項式在 J17 triangular averages 後落入 corridor；誤差超多項式小本身不決定中心項符號。

J29 已把 J19 極左尾以 normalized mixture 恒等式加回，並給其對 variance／third cumulant 的封閉誤差。故 J24 所指定的六階 enclosure bookkeeping 已完成到可代入有限初等 bounds 的形式。當前主缺口轉為解析符號比較：J25/J28 的中心函數經 J17.3–J17.4 積分後是否滿足 J17.5–J17.6；此外 `T_0=10^24` 仍需大幅壓低才適合有限區間證書。

J30 用 Gaussian 加權的五階 Bell remainder 取代 window supremum，並以 exact endpoint audit 證得 `κ_(3,t)(logu)<0` 對所有 `t≥10^30`。因此大 t 的 `D_(k+1)-D_k<0` 已有點態來源；但 J17.6 還需要其負 magnitude 不超過 `|log(p_k/p_(k+1))|`。三角核平滑不會破壞負號，卻可能不足以保留 corridor 所需的定量界，這是當前最直接缺口。

J31 已進一步證 `|κ_(3,t)|<1/(64t²)` 與 `Var_t(logu)<1/(40t)` (`t≥10^30`)。這兩個點態 magnitude bounds 經 J17 triangular kernels 後，完整證出第一 theta 項對所有 `k≥10^30+2` 的 J17.5–J17.6，因而滿足 J12。大 k 尚缺的是把 J14 的 `n≥2` theta-tail 用顯式差分常數轉移到完整 Φ；有限段門檻仍極不實用。

J32 已用 J14.3 的顯式常數證 `epsilon_k≤2k^-100` (`k≥10^30`)，並把二、三階 log-moment 差分擾動壓入 J31 margins。因此完整 Xi 核對所有 `k≥10^30+2` 已滿足 J12，亦即 shifted degree-3 Jensen 在此大-shift 區域 hyperbolic。degree 3 現只缺有限但天文大的前段；degree 4 以上仍完全未由此推出。

J33 保留 mode 尺度，將導數 majorant 改進為 `|B_j|≤2C_jtβ^(j-1)`，並以新 exact endpoint audit 把完整 Xi 的 J12 接點降至 `k≥10^10+2`。這仍不足以逐 k 驗證：degree 3 的有限缺口是 `1≤k<10^10+2`。若不再降低解析門檻或建立能覆蓋大參數區塊的 interval monotonicity certificate，直接枚舉不可行。

J34 將 standardized window 從 `logt` 改為 `sqrt(8logt)`；`t^-2` 左尾已足以保護 J12 margins，且大幅降低 cubic boundary perturbation。新的完整 Xi 接點為 `k≥10^8+2`。有限 degree-3 缺口縮至約一億個 shift，仍需參數分塊／更高階展開，不能把「有限」誤當作已可驗證。

J35 又把七階 Taylor majorant 改為 window 內的 `4C_7tβ^6`，配合 `ell=sqrt(6logt)` 將完整 Xi 接點降至 `k≥10^7+2`。端點 cumulant error 已達主項的 0.442，表示現有六階、絕對值 Bell enclosure 再粗降門檻的餘裕有限。下一可行技術路徑是更高 weight 展開或 logarithmic parameter-block interval certificate。

J36 保留 `A_3,...,A_6<0`，對 exact 64-term cumulant 分子只累加真正可能抵消主項的 monomials；正中心修正僅為主項的 0.000365。連同 local errors 後，完整 Xi 的 J12 接點降至 `k≥10^6+2`。finite degree-3 缺口現約一百萬個 shift，仍缺能一次覆蓋參數區塊的有向區間證書。

J37 已指定下一個可稽核介面：對連續 t 的 logarithmic blocks 以 directed interval mode、相關 B_j/Λ enclosure 和 block-specific sqrt-log window 輸出 cumulant／variance bounds。有限精度診斷只表明 `t≥10^4` 可能有餘裕，尚沒有任何 block certificate；`10^2–10^4` 可能需要更高階或直接 moments。

J38 已完成 J37：694 個 directed blocks 嚴格覆蓋連續 `t∈[10^4,10^7]`，再與 J35 接合，證得完整 Xi 對所有 `k≥10002` 的 J12。degree-3 finite gap 現為 `1≤k≤10001`。下一步可行規模已從「百萬點」降成約一萬個 moments，但仍必須用 rigorous integration/tail certificates，不能以 SciPy quadrature 的 heuristic error 代替。

J39 允許 A6 未知符號並在低端使用 0.1% blocks，把 continuous certificate 延伸至 t=3800；完整 Xi 的 J12 門檻現為 `k≥3802`。第一 block 的 local-error ratio 已達 0.987944，故 Bell-5 六階 enclosure 在此實際耗盡。J40 已精確加入 A7 與七個 weight-5 cumulant monomials；尚缺 Bell-6／M8 解析 remainder，這是繼續下推門檻的首選路徑。

J45 已完成 weight-9/Bell-10/M12 directed enclosure，並以直接 `F''` interval 取代 J43 的粗 Lipschitz 曲率 gate。84 個 adaptive continuous blocks 覆蓋 `[937,1858]`；最弱 `[937,938]` 的 error ratio 0.995057。全域有 `t²|κ_3|<3/50`、`tVar<87/1000`，以 `k^-19` theta-tail transfer 接合後，完整 Xi 的 J12 對所有 `k≥938` 成立。degree-3 finite gap 現為 `1≤k≤937`。本階只剩約 0.5% 符號餘裕；首選下一路徑是直接 rigorous moment intervals，weight-11/Bell-12 則須先評估 combinatorial majorant。即使 cubic 全關閉，degree 4 以上仍是獨立缺口。

J46--J51 又 exact 擴到 weight 15／Bell-16／M18，連續門檻依序降到 801、745、727；目前完整 Xi 的 J12 對所有 `k≥727` 成立，degree-3 gap 為 `1≤k≤726`。新增 weight 層的 monomial 數 56、101、176，而門檻收益 137、56、18，最低 block 餘裕皆約 0.3--0.5%；故目前 absolute-Bell 加階引擎已實用耗盡。J52 已寫出直接 moment chord/tangent interval 介面，但尚未完成 verifier；有限精度掃描顯示所需相對 moment width 約 `10^-7`，這不是證明。degree 4+ 仍是獨立缺口。

J53 已實作二階 cell Taylor＋三階 exponential polynomial 的 directed quadrature；解析餘項為 `h exp(eta)eta^4/4!`，外尾用凹性 tangent，高 theta 用 J14 directed upper。完整 Xi 的 `[50,150]`、`[151,250]`、`[251,325]`、`[326,400]` 全通過，最小認證 J12 margin `>2.9422e-6`。degree-3 現只缺 `1≤k≤49` 與 `401≤k≤726`；低段須逐 theta 項 enclosure，後段可續跑同一 verifier。degree 4+ 仍未閉合。

J55 修正 J53 cell width 的 1-ulp 幾何缺口後，已重驗 `[1,34]`、`[35,49]`、`[50,150]`、`[151,325]`、`[326,450]`、`[451,726]`，並與 J51 的 `k≥727` 接合；所有 shifted degree-3 Jensen polynomials 現已嚴格證明 hyperbolic，最小有限段 margin `>9.9367e-7`。這只關閉 cubic 層級。

J56 用 exact 正序列 `(25,78,143,76,29)` 證兩個 shifted cubic discriminants 皆正、quartic discriminant卻為 `-1348512563200`，嚴格否證一般 degree-3→4 升階。現有 C_k 遞推只控制四個係數／variance與 third cumulant，沒有 uniform-in-d 結構。已停止逐 degree finite certificates；主缺口改為證 `J_(d,n)` 與 `XJ_(d,n+1)` 的 uniform common interlacing、全部 Jensen Hermite/Bezoutian matrices 的 uniform Gram representation，或正確 coefficient-array PF∞。raw moment Hankel positivity與 translation TP2 都不足。

A7 現把 uniform 缺口精確寫成 critical-value signs：若 r_i 是 `J_(d,n+1)` 的根，則 `J_(d+1,n)(r_i)=J_(d,n)(r_i)`，故需對所有 d,n 證交替符號；尚無證據 pairwise compatibility 在 Pascal recurrence 下封閉，可能需要整族 `X^jJ_(d,n+j)` common interlacing。A8 顯示 naive positive-mixture Gram 在 degree 2 已有符號不定 cross kernel `st-(s²+t²)/6`，所以任何 uniform Gram factorization 必須實質使用 Xi 的 score/theta 結構。

A9--A11 給出目前最明確的 uniform 候選：若 `h=G'/G` 在上半平面逐點滿足 `Im h<=0`，其極點局部形狀立即排除 G 的非實零點；等價 PF∞ 版本則要求 `c_k=gamma_k/k!` 的單一無限 Toeplitz array 全正。真正未閉合點是由 Xi 的 mixture 證逐點雙積分符號 A9.3。正 mixing 不保此符號；`3δ_1+δ_100` 已在原點導數給 exact 反例。J56 序列更精確通過 `(-1)^m h^(m)(0)>0` 至 m=5，卻在 m=6 失敗且 quartic 非實根，故有限 log-derivative signs 不能替代全 Pick／PF∞ 結構。

degree 3 可保留的升階種子只有 Rolle 關係 `J_(2,n+1)=J'_(3,n)/3`，即每個 cubic 與其 shifted quadratic 交錯。degree 4 卻要求 `J_(3,n)` 與 `J_(3,n+1)` 的橫向 compatibility；J56 反例證前者不推出後者。因此已有 cubic theorem 是 base case，不含 induction step。

A12 把 anti-Pick 改成正確的 all-size determinant 目標：`b_m=(-1)^m h^(m)(0)/m!` 必須同時使 Hankel 與 shifted Hankel matrices PSD；加解析 growth bound後，Stieltjes representation會一次推出全實負零點。這不是 raw moments。最低 determinant為 `(gamma_0 gamma_1 gamma_3+gamma_1² gamma_2-2 gamma_0 gamma_2²)/(2 gamma_0³)`；J56 反例取 exact 負值 `-2119/15625`，故 cubic theorem不含此 Gram 結構。尚缺由 Xi score/theta 對所有 matrix sizes 建同一個 Gram factorization。

A13 更直接排除 J12 hidden induction：取 `C_1=61/1000,C_2=49/1000,C_k=6/125 (k>=3)`，再由 ratio recursion 建無限正 gamma。它對所有 k 精確滿足完整 J12 corridor，故所有 shifted cubics hyperbolic；但 `J_(4,0)` 的 exact discriminant仍為負。於是 J12 的全 k covariance/third-cumulant控制也只能列為 cubic-only lemma，不能作任何 degree induction invariant。

A14 將 A12 最低 Hankel determinant寫成 `[3M_0M_1M_3+15M_1²M_2-10M_0M_2²]/(1440M_0³)`；正 scale measure `(3/4)δ_0+(1/4)δ_1` 使其 exact 為 `-13/92160`。故全階 Gram若存在，不能來自 raw moment positivity或直接正 mixing；必須有 Xi-specific、對所有 matrix sizes 同時成立的 theta/score 重排。

A15 精確回答 degree 3 留下多少 determinant 結構：J12 可推出 log-derivative Stieltjes S-fraction 的前兩個 pivots `a_1,a_2>0`，因 `det H_2^(0)=q^4(1-C_1)[C_1-(1-C_1)C_2]/2>0`；但不推出 `a_3`。J12-compatible exact chain `C_1=17/500,C_2=4/125,C_k=29/1000 (k>=3)` 給 `a_3=-17279199581/205062500000`。所以這是一個有限 seed，不是 pivot recursion。

A16 排除更強的自然猜想：`C_k=1/[4(k+2)]` 同時是 Hausdorff completely-monotone sequence並對所有 k 滿足 J12，但 exact Sturm chain 證 `J_(10,0)` 只有 6/10 個實根。故 J12 加全部 C finite-difference signs仍不是 uniform-in-d 機制。

A17 完成 recurrence closure audit。整族 `F_j=X^jJ_(d,n+j)` 若 full compatible，Pascal map `F_j -> F_j+F_(j+1)` 確會保持 compatibility，這是真升階定理；但 d=0 base被 `1+X²` 否證，degree 3 個別 hyperbolicity也不給 family compatibility。只要求迭代產生的 binomial combinations則由 exact identity直接等同所有 higher Jensen hyperbolicity，屬循環改寫。

A18 精確定位 theta route 的算術障礙：`Phi(u)=int T_1(u+a)dmu(a)`，其中 `mu=sum n^-1/2 delta_(log n)`，而其 Laplace transform是 `zeta(s+1/2)`。因此 first-theta saddle/score不能單獨產生 all-r positivity；正 shifts又不保 Gram/Pick。J14 的 theta-tail smallness只對高 moment index，不是固定 shift下 uniform-in-degree 的擾動定理。

A18 的 mu 只有局部有限性；總質量及普通正次 moments發散。故不能裸用 finite-moment compound/Andreief positivity；指數 damping只在 `Re s>1/2` 產生 ζ transform，而移除 damping或正則化是否保 signs正是額外未證責任。

A19 給目前最貼近 Xi moment setting 的 exact 反例：令 S 為 `Beta(21/40,199/40)` 與 `Beta(9/2,33/4)` 兩獨立變數之乘積，取其 compact positive moments並作相同 factorial normalization。四個 J12 inequality numerators在 `k=m+1` 後全具非負有理 coefficients，故 global J12嚴格成立；但首個 quartic discriminant為負。故「positive raw moments + all-shift J12」仍只關 cubic，raw Hankel PSD不能補成升階。

Li 路線 D9 現已合法合併 Abel 極點補償與 prime sum：`E_n(delta)=int x^(-1-delta)L_(n-1)^1(logx)d[x-psi(x)]`，分部積分後成 Q 與單一 Laguerre kernel 的 oscillatory integral。D6 的最小未閉合 inequality是此 integral負部的任意底數次指數界。PNT error加 kernel絕對值會產生 factorial moments，方向太粗；必須保留算術 oscillation。

D10 修正並簡化 D9：因 `L_(n-1)^1(0)=n`，boundary是 `-n`；bracket在 Abel limit化成單一 `L_(n-1)^2`。令 `F(s)=int Q(e^t)e^-st dt=[1+h(s)]/s`，h 在 1 解析，嚴格證明額外 `delta L^1` 項消失。生成函數 audit完全回復原 binomial transform。當前精確缺口為 D10.3 的單側次指數 Abel--Laguerre bound。

`strategy_audit.md` 現集中記錄路線邊界。尚存的非循環缺口只有：Xi-specific all-r arithmetic identity／可初始化封閉 cone、D10 signed Laguerre bound、NB11 uniform mollifier，或全尺度 Chebyshev correlation。Workspace目前沒有可由既有估計閉合其中任何一項的無條件機制。

C4 已把 D10 與 M1 精確接合：若任一 integer `p>=2` 的 `Q_p` finite，Laguerre recurrence/orthogonality給 tail norm `O_p(n^(p/2))`，compact t區只為 `e^(O(sqrt n))`，故全部 `E_n` 絕對次指數。但 `p>5` 時 Q_p finite已與 RH 等價，較小 p 更強；所以 Hilbert-space正定化沒有產生較弱可證假設。

終止稽核見 `strategy_audit.md` 第 6 節。此研究未證 RH；已達成的是使用者允許的另一終止條件：目前 workspace 中所有具體可行路徑均已推到明確的 RH-equivalent arithmetic obligation，低階／positive-mixture／finite-certificate捷徑均有 exact反例，且沒有尚待執行的非循環候選。未來若有新的 Xi-specific all-r identity、封閉 cone或 arithmetic estimate，應從該新輸入重開，而非續刷 finite batches。

K2 另以嚴格 log-concave、TP₂ 的 Gaussian 混合反例證明：平移核的二階全正性本身不足以控制 Fourier 非實零點。

## G13：獨立自伴算子／譜行列式尚未構造

`spectral_toy_route.md` 證明此機制在功能域型 toy `P_q(T)=1+qT²` 上完全
成立：一個正自伴 Neumann--Dirichlet Laplacian A 給
`G_q=det(I+wA^(-1))`，其 resolvent trace一次產生 anti-Pick 與 all-size
Stieltjes Gram positivity。故先前「已窮盡所有可行路徑」的全域宣告過強。

Riemann Xi 的未閉合點是：從 theta/primes 獨立定義正自伴、compact-
resolvent A，並證 `G(w)/G(0)=det(I+wA^(-1))`。若用未知 Xi 零點平方指定
A 的 spectrum，論證循環。toy 的一般 quadratic 版本顯示自伴性本身正好
承擔 critical-circle arithmetic bound，所以目前尚未降低 RH 核心難度。

乘積封閉本身沒有缺口：spectral determinants由 operator direct sums相乘，
對應 Pick--Loewner kernels相加。真正障礙是 Xi theta結構為正和而非乘積，
而逐 prime Euler factors各自在 central coordinate有上半平面 poles。因此
G13 需要全域 operator／Loewner-kernel reconstruction，不能逐 component
組裝。可直接檢查的目標是對 `h=G'/G` 證
`-[h(z)-conj h(zeta)]/[z-conj zeta]` 的所有取點矩陣 PSD，且證明不得預設
G 無非實零點。

fixed-scale determinant 的 common-interlacing 平均亦不可行：尺度 u 的
eigenvalue counting為 `u sqrt(R)/pi+O(1)`，不同尺度的差無界，與共同交錯
所需的 count difference至多 1矛盾。此為解析排除，不是有限數值測試。

## G14：archimedean core 的 prime-relative 自伴 perturbation

`spectral_archimedean_route.md` 已排除任意／regular finite-interval A，並
構造顯式正自伴 core
`A_0=-4d²/dx²+16pi²e^(2x)`。其 determinant
`D_0=K_(sqrt(w)/2)(2pi)/K_0(2pi)` 與 Xi 在正 w 軸的 archimedean增長匹配，
且 `(G/G(0))/D_0~Cw^(9/8)`。

未閉合點是從 prime lengths `m log p` 與 weights `p^(-m/2)/m` 獨立構造
A_0 的正自伴 perturbation/extension A，使 resolvent difference trace
class並證 determinant ratio等於 Xi relative factor。Euler series只在
`sqrt(w)>1/2` 絕對收斂；解析延拓必須由 operator本身給出，不能預設 zeta
zero-free。逐 prime direct sum因 local upper-half-plane poles而失敗。

## G15：shifted Morse channels 的 Weyl sum 尚未匹配 Xi

每個 theta summand 已 exact factor為正 Morse channel的 ground state：
`phi_n=T_n/(2e^(u/2))` 滿足
`[-d²+4pi²n^4e^(4u)-20pi n²e^(2u)+4]phi_n=0`，一般 resolvent solution
為 Whittaker `W_(5/2,sqrt(1+w/4))`。這提供從 theta arithmetic獨立定義
的自伴 building blocks。

自伴 star coupling可使 secular equation成 `sum c_n²m_n(w)=alpha`，因此
和式可在 Weyl-function層級合法封閉。目前缺口是找出由 theta/primes
強制的 `c_n,alpha`，並證該 Weyl sum等於 Xi logarithmic derivative或 P4
relative factor。還須處理 countable boundary space、renormalization及
determinant normalization。若 Whittaker expansion與 P5.3不匹配，此路應
解析封閉。

P9 已完成此首輪匹配並否證 naive 版本：有限 N-channel star有 N 倍 Xi
Weyl主項，全部 n channels則為 `Theta(lambda^(3/4))`；此外固定有限 Weyl
sum的大 x修正是 algebraic，而 prime relative trace始於 `2^-x/x`。所以
不得再把 raw star assembly列為候選。尚未排除的是只保留單一 A_0 phase
volume、把 Morse channels壓成 trace-class relative perturbation或 boundary
counterterm的全域構造；這需要新的 exact identity。

P10 已補齊無窮和細節：`m_n=-2pi n²+4+O_K(n^-2)`，所以正權和確可用
theta-decay weights或 real-constant subtraction定義；但 poles的 residues
同號，無法正權消去，level-set zeros仍為 `Theta(lambda^(3/4))`。因此標準
countable self-adjoint star亦正式封閉，不再列作未決 convergence問題。

## G16：prime semigroup determinant 尚未轉成 compact resolvent determinant

`H_P=diag(log p)` 已給 exact
`zeta(s)=det(I-e^(-sH_P))^-1` (`Re s>1`)；prime powers亦可由 self-adjoint
open quantum graph的 unitary dilation產生。但前者是 semigroup determinant，
後者的 singularities是 resonances。兩者都不推出 Xi zeros為 self-adjoint
point spectrum。

缺口是構造一個全域、保持單份 A_0 phase volume的 compact/self-adjoint
system，把 open prime channels關閉且證新增 mixed orbits精確重組成 gamma、
functional equation與 pole-cancellation terms。沒有此 orbit identity時，
P11 只是 Euler product的 operator改寫。

## G17：modular scattering generator 的實部未固定為 1/4

模曲面 Eisenstein scattering已 exact 給
`varphi(s)=Lambda(2s-1)/Lambda(2s)`，因此全域 gamma+zeta recombination
並非缺失。RH 等價於其非平凡 poles `s=rho/2` 全在 `Re s=1/4`。

ambient Laplacian自伴只給 `Re s=1/2` 的 scattering unitarity；任意位置
Blaschke factor證 unitarity、reflection symmetry與正 time-delay均不足。
真正缺口是由 modular/Hecke arithmetic在 resonance space構造 positive
metric並證 generator `Z=I/4+iT`、T self-adjoint。若只由 resonance locations
定義 metric即循環。

## G18：signed spectral-shift distribution 尚未提升為正離散譜

prime orbit已有 exact heat-distribution formula P12.2。它否證 positive／
negative trace-class additive potential，但與 modular scattering的 signed
Birman--Krein spectral shift相容。故「取得 explicit trace formula」本身
不再算缺口；真正缺的是一個 positivity/normality theorem，把該 signed
continuous-resonant distribution識別為 `Z=I/4+iT` 的 point-spectrum trace。
目前沒有此提升，且 Blaschke MS4/MS5證一般 unitarity與 phase positivity
不足。

## G19：incoming/outgoing semigroups 缺共同正 norm

MS8 證明：若 resonance generator Z 的 centered group
`exp[t(Z-I/4)]` 在同一 Hilbert norm下雙向 contractive，便自動 unitary並
推出 RH。現有 modular scattering只給 incoming/outgoing的 functional-
equation pairing，沒有證兩者是同一 positive resonance space上的互逆
contractions。構造此 common norm是新的明確充分目標；由 zeros位置反造
權重不合格。

MS9 又排除最直接的 Hecke completion：target resonance line上的 Hecke
eigenvalues一般為複數，與 positive space中的 self-adjoint T_p矛盾。故
G19 所需 common norm不能同時保留原 automorphic L2 的全部 Hecke
self-adjointness；若有構造，必須使用不同的 modular boundary/energy form。

MS10/MS11 又排除 local cusp weights與generic Hardy/model spaces：前者只選
半平面或人工平移 continuous line，後者對任意 Blaschke zeros都正。MS12
把剩餘缺口認定為 Weil quadratic form的 arithmetic square factorization。
宣告 Weil form正本身等價 RH；須直接在 prime+gamma side產生 all-test-
function Gram identity才算閉合。

## G20：Weil form 缺 arithmetic all-test square

function-field型 unitary toy已有 W1.1 的 exact Gram；Riemann prime
contraction則由 spectrum invariant證明不能在原 space unitarize。所需新
輸入是完全由 primes/gamma定義的線性 map `g->V_g`，使
`Weil(g*g*)=||V_g||²` 對所有 admissible g成立。unitary dilation若留下額外
channels或 mixed orbits不合格。此 identity一旦成立即證 RH；目前未構造。

MS13 顯示不能把「functional-equation pairing正定」列作額外已知輸入：
每個 off-line reflection pair的 Gram block有 signature `(1,1)`，所以正定
本身已等價排除該 pair。G20 的 square必須在 zero decomposition以前由
arithmetic建立。

W5--W7 已將此缺口再縮小。每個 prime 的 Poisson operator滿足 exact
W5.6，但 multiplier跨過 1，故 local dilation不是 contraction defect；
W6 又以 Gaussian解析族證明未修正 gamma/pole form可為負，不能作正 base
norm。正向結果是：對支撐長度 A 的任意 g，prime side精確成非負平移差
平方
`E_A=sum_(n<=e^A)Lambda(n)n^(-1/2)||g-T_(log n)g||^2`
減去 `2S_A||g||^2`。因此 G20 收斂為 uniform-support coercivity W7.5，
或更強的 adelic common-dilation/projection identity。這是 all-test 機制，
不是有限 degree 證書；目前仍缺 archimedean full norm與 prime compression
之間的非循環 isometry。

W8 另完成 pole--continuum square completion：把四個 kernels
`e^(-(2j+1/2)|u-v|)` (`j=0,1,2,3`) 從 pole kernel轉給 gamma後，正好以
digamma recurrence得到 multiplier
`Re psi(17/4+it/2)-log pi>=c_4>0`。故完整 form精確為
`Q_W=B_4-2R_4`，其中 `B_4` 是已證正 norm，`R_4` 是 von Mangoldt離散
measure相對 W8.4 continuum kernel的 autocorrelation discrepancy；該 kernel
只在 `a>=log2` 為正，短 archimedean interval仍是 signed endpoint layer。當前最小
缺口可寫成單一 all-test inequality `2R_4<=B_4`。此式仍承擔 RH 尺度，
尚無算術證明；但 gamma block符號與 continuum counterterm已閉合，不再是
模糊的 square-factorization要求。

W9 發現一個尚未窮盡的 all-order Selberg hierarchy：全部 generalized
von Mangoldt `Lambda_k=mu*log^k` 非負，且
`Lambda_k log+Lambda*Lambda_k=Lambda_(k+1)`。它提供真正的升階遞迴；
但 convolution在 Weil test上產生 `C_g(a+b)` 的 forward/backward cross
pairing，而 norm square產生 `C_g(a-b)`。目前缺一個保持 W9.3 且不新增
mixed orbits的 Fock/block positivity theorem。

W10 修正 Fock 猜法：裸 `Lambda_k(p^m)` 的 2-by-2 Hankel determinant為
`-m(m-1)(log p)^4<0`；但以 `r=omega(n)` 位移並乘 `j!/(r+j)!` 後，
exact 成 box moments，故所有尺寸 Hankel Gram皆正。W11 依 nudge完成
跨代數 audit：box Gram仍只控制 `a+b` convolution；`delta_L` 的正
convolution hierarchy已有 symmetrized Fourier transform `2cos(tL)` 取負的
反例。故 G20 現在明確需要 theta/Tate/adelic reflection theorem，把
half-semigroup convolution轉成 group autocorrelation，且不能在 contour
shift時預設 off-line residues消失。

W12 已把正 base `B_4` 完全平方化：
`B_4=c_4||g||²+int e^(-17a/2)/(1-e^(-2a))||g-T_ag||²da`。
因此不再缺 archimedean factorization；唯一缺口是 W12.4 的 operator
large-sieve inequality。其 RHS只控制局部 `1/(2a)` 型 translation energy，
而 R4含任意長 `log n` shifts，故必須使用真正的 prime discrepancy消去，
不能由正測度或 total variation推出。

W13 完成防循環 audit。prime discrepancy transform `F_4` 在 regular
imaginary-axis points由 functional equation逐點滿足 `2Re F_4=b_4`；Weil
form的全部非零內容來自 boundary Poisson deltas與跨 contour的 off-axis
residues。其 Chebyshev表示 W13.5 又直接接回 M1 weighted L2 criterion。
因此 W12.4不是獨立於 Chebyshev的第二個缺口；若先 meromorphically移到
critical line再忽略 residues，便已假設 RH。

W14 補足 nudge要求：以 finite interpolation乘 horizontal Gaussian，可在
任一 off-line quartet上取 MS13負 eigenvector、消掉全部低零點並壓掉高尾。
故 W12.4 的 all-test版本逐點排除每一個離線 orbit，確實推出完整 RH，
不是僅 zero-density。後續任何 proposed large-sieve bound必須覆蓋這類
orbit-localizing tests；只對平均或受限 support class成立不夠。

W15 又以 `epsilon=4,t=0` 的 exact rational bounds否證 natural Abel bridge：
`Q_4(0)<-229/61880`。所以 canonical pole/gamma subtraction後的 Euler forms
在絕對收斂區已非正，不能靠 damping正性與極限保正完成 W12.4。

`tate_reflection_route.md` TR1--TR4 已完成 natural Poisson reflection audit。
theta-sum operator E在 Mellin座標只是 multiplication by
`2zeta(1/2+it)`；ordinary positive L2中其 kernel為 0、range dense，離散
zeros及所有 off-line zeros都不形成 cokernel。改用 exponential analytic
rigging雖可見 resonances，reflection pair又回到 MS13不定 block。故尚缺
TR5 型、contour shift前由 arithmetic projection/commutator產生的 exact
positive defect。

TR6 又算出 standard log-halfline projection的 commutator norm恰為
`int|a||g(a)|²da`，完全不含 arithmetic；E range projection則因 range dense
而為 I。故 TR5 必須是新的 adelic/arithmetic projection，不能由兩個現成
projections直接組合。

TR7 已找到 prime-side arithmetic projection：local unilateral shift的
rank-m Toeplitz defect配 `1/m` orbit factor，exact 給
`Lambda(p^m)p^(-m/2)`，並平方化整個 W7 prime difference energy。剩餘缺口
不是 prime weights，而是 divergent diagonal debt TR7.6 如何在同一正
adelic/archimedean module內由 product formula抵消；scalar subtraction已由
W15否證。

TR8 定位 adelic斷層：real與 p-adic boundary shifts確由 product formula
取消 signed indices，但 positive commutator norm把兩條 infinite strips相加。
double-boundary corner雖可再給 `log p` 正 weight，仍只重現 TR7/W7，未消
diagonal debt。缺的是把 signed index提升為正 cohomology/Schur complement
的 theorem。

TR9 證明「取 cohomology」本身不會把 signed index轉正：two-term complex只
給 `dimH0-dimH1`，off-line dual pair仍是 signature `(1,1)`。須另造與 scaling
相容的 positive Hodge star；該相容性會直接強制 target line。TR10 顯示
local prime defect確有 canonical finite-dimensional polarization，但 tensor
globalization會產生 Lambda不含的 mixed-prime sectors。尚缺同時使 mixed
sectors acyclic並在剩餘 cohomology上證 Hodge-Riemann positivity的 global
complex。Schur complement亦不免費：主塊正性與 cross-norm bound須另證，
後者會直接重寫 W12.4。

TR11 修正 mixed-sector部分：bosonic Fock的正 one-particle reduction exact
給 `-zeta'/zeta=Tr H_P(e^(sH_P)-I)^-1`，故 mixed primes可在不使用
supertrace下移除。剩餘缺口更集中：critical prime occupation非 trace-class，
須與 gamma oscillator構造 operator-level positive relative trace/isometry；
scalar subtraction由 W15否證。

TR12 證 atomic prime-length space與 nonatomic arch continuum間不存在非零
exact length-intertwining isometry。故 operator-level relative trace必須以
wave packets模糊 lengths，並由 W12 q4 translation energy支付 commutator
error；真正缺口成為一個 arithmetic frame bound。

TR13 又排除 positive atom-to-cell transport：prime cell寬約 `logp/p`，其
aggregate displacement density約 `delta^-3/2`，嚴格超過 W12
`q4(delta)~delta^-1` budget。故所需 frame必須跨 primes有 oscillatory/
orthogonal cancellation，不能只靠 PNT quantile matching。

TR14--TR16 將此缺口化成 prime-torus return problem。Haar long-time mean只
等於 diagonal debt，Bessel仍差 `sqrt(log)`；而 cutoff-X polynomial的 Haar
norm約 `logX`、identity peak約 `sqrtX`。要逐點支付 recurrence peaks，尚缺
TR16.5 型 uniform first-return bound `log|t|gtrsim sqrtX`。任何節省常數若
隨 `S_A~sqrtX` 退化，便不能在 `A->infinity` 封閉。

TR17 顯示 Haar entropy本身其實 dimension-free：`sqrtX` peak measure至多
`exp[-cX/log²X]`，若有 reciprocal-measure級 first-return bound就遠強於
所需門檻。真正缺的是 deterministic prime-log Kronecker hitting theorem；
unique ergodicity不能把小 Haar measure自動轉成首次返回下界。

TR14 將 surviving frame寫成 prime-torus restriction。W7 `E_A` 是 Kronecker
orbit distance `D_A(t)` 對 `|H|²` 的積分，而 `2S_A` 恰是 D_A 的 Haar長時
平均。故普通 equidistribution/large-sieve只給 density；尚缺對全部
Paley-Wiener tests、uniform-in-A 的 recurrence-window uncertainty bound。

TR15 稽核 nudge：Bessel orthogonality把 displacement power降至 1，但精確
尺度仍為 `delta^-1 sqrt(log(1/delta))`，比 q4多 square-root log；且另一
Cauchy因子就是 diagonal debt。尚需額外半 log的 arithmetic cancellation。

## G21：de Bruijn--Newman backward collision barrier

`debruijn_newman_route.md` 已推導 simple real zeros的 exact gap dynamics
`(d_j²)'=4kappa_j`，其中 `kappa_j=2-d_j²A_j`；exact clock lattice有
`kappa_j=0`，所以 absolute minimum-gap策略不可能 uniform。要由 real-zero
時間下降至 0，尚缺 theta-specific、對全部 j一致的積分 collision budget
DN3.2或 backward-invariant clock cone。一般 heat PDE與 even/real kernel
由 DN4 quadratic toy證明不足。

DN6 已給 deterministic finite-window sufficient lemma：若目標 gap周圍前後
M 個 gaps皆不超過其 `(1+epsilon)` 倍，則
`kappa_j^+<=4epsilon+2/(M+1)`。要支付高處 inverse-log-squared gap budget，
需約 `M>>log²gamma`、`epsilon<<1/log²gamma` 且對全部 j、全部下降時間一致。
平均 spacing或 density-one clock行為不能滿足此門檻。

DN7 依 nudge補上 uniformity：每個 dyadic height block必須共同選
`M(Gamma),epsilon(Gamma),h_*(Gamma)`，同時覆蓋全部 gaps與全部下降時間，
並滿足 DN7.3。逐 gap事後選參數或 density-one rigidity只能給 density結果。

## 已明確封閉的失敗路徑

- 僅由 `ξ(s)=ξ(1-s)` 與共軛對稱推出逐點位於臨界線：被 `argument.md` 的四點多項式反例否證。
- 由任意固定數量的 Li 型正性條件排除所有高處離線四元組：被 L1 否證。
- 由「某一四元組對 `q_n` 為負」直接推出完整 Li 係數為負：裸推論無效；必須使用 L5 的最大模、同步相位與尾界論證。
- 僅由 Xi 的 Fourier 核正、偶、光滑、快速衰減推出全實零點：被 `positivity_kernel.md` 的 Gaussian 混合反例否證。
- 對第一 theta 項在 `x=log u` 後直接假設全域 log-concavity／強凸並套 Brascamp–Lieb：J18.2 顯示極左尾的 log 密度二階導數為正，假設不成立。
- 僅由 ζ 正則對數導數完全單調推出 η 二項變換無負向指數成長：被 `eta_complete_monotonicity.md` 的 `1/(a+x)` 反例否證。
- ζ 正則對數導數本身完全單調：被其唯一 Laplace 測度在質數冪處具有負原子嚴格否證。

TR18 又封閉 raw prime-torus first-return候選。PNT給 fixed t asymptotic
`F_X(t)=X^(1/2+it)/(1/2+it)+o(sqrtX)`；沿相位對齊的 X 序列，在 t=1
已有 `asymp sqrtX` raw peak。因此小 Haar measure與 dimension-free entropy
不能阻止極早命中。必須先扣除 continuum Mellin主項；剩餘 centered quantity
是 `int x^(-1/2+it)d(psi-x)`，其所需 uniform square-root尺度控制正是
尚未解的 prime--gamma/W12 缺口。TR16--TR17 不再列為候選證法。

DN8 開出尚未窮盡的 global collision mechanism。有限 zeros的 Vandermonde
有 exact square law `(logDelta)'=4sum_j S_j^2`，所以 backward collision必使
action發散。缺口是為 Xi 的 dyadic height blocks定義 clock-renormalized
discriminant、控制 boundary flux，並由 theta heat kernel給 uniform-in-height
且涵蓋整段時間的 finite-action bound。這比 DN7逐 gap近鐘格條件弱而合理，
但尚無所需 theta-side估計。

DN9 指明 renormalization不可省略：有限 height block有 external-zero flux，
純 Vandermonde square只在完整有限系統成立。正確充分量是 full PV zero
velocity action；collision使其對數發散。缺的是對 expanding blocks及
`t downarrow 0` 一致的 action bound，或等價的 DN9.1 boundary-flux控制。

DN10 顯示這個 gap沒有被 energy換名解掉：有限 action精確等價 discriminant
lower bound；companion-matrix公式的 inverse亦以 discriminant為分母。
Schwartz entire反例 `f_d=(x²-d²)e^-x²` 的固定階 L2導數一致有界，但
zero velocity約 `1/d`。故 ordinary theta Sobolev/Plancherel bounds不足；
尚缺 zero-sensitive sampling／de Branges frame／all-size determinant identity。

DN11 回答截塊極限：raw DN9.1 cross term在 clock lattice已與 internal square
同階，不能用 block average丟掉。加大 buffer後，遠尾可由 zero symmetry與
`N(U)=O(UlogU)` 得 pointwise `O(Gamma logL/L)`；`L=Gamma²` 時 core L2
tail趨零。剩餘精確缺口是 transition layer的 tapered/clock-renormalized
flux identity，而不是遠端 zero tail。

W16 已把 centered finite-support介面寫成 exact distribution identity：
`dnu=-d[e^-a/2(e^a-psi(e^a))]-(1/2)e^-a/2(e^a-psi(e^a))da`。
因此 R4 的非 endpoint部分是 `C(0)+int epsilon(C'-C/2)`。缺口不是 raw
prime peak，而是 signed Chebyshev error對全部 autocorrelations的 uniform
log-Dirichlet form bound；absolute-value或 ordinary PNT估計不合格。

W17 再加 sharpness門檻：modulated long boxes的 C 趨近任意 `cos(ta)`，B4
趨近 b4(t)，所以 W12在 regular spectrum上被 Weyl sequences飽和。任何
strict-contraction、fixed-loss或 sqrt-log-loss bound皆不可能完成；必須是
constant 1 且能處理 boundary residues的 exact reflection/relative trace。

W18/A20 精確識別 `h=G'/G` 與 centered Weil discrepancy：W12、anti-Pick/
Stieltjes all-r Gram及自伴 resolvent determinant是同一缺口的不同座標。
目前缺的是 Euler/theta-side positive measure factorization，不是再找等價名稱。

P13 給最具體的新 all-order版本：explicit prime--gamma inverse-Laplace trace
Theta(t) 必須 completely monotone。它一旦有 single positive Laplace measure
factorization即推出 RH；但公式含負 von Mangoldt Gaussian sum，尚無 all-k
square/semigroup identity。有限 k sign checks不填此缺口。

P14 給嚴格有限階 no-go：正 base exponential加任意小 damped oscillatory pair
可通過 Theta非負及任意預定有限 K 的 derivative signs，卻仍有 off-axis
Laplace poles。故驗收門檻確須 all-k／single factorization。

P15 指出 single factorization的 analyticity責任：cut上的 critical zeros本來
就給正 Stieltjes atoms，off-line zeros藏成 cut外 poles。boundary positivity
不足；尚缺 Euler/theta-side resolvent identity同時排除所有 off-cut poles。

P16 將缺口定為 Hankel kernel `Theta(2tau+s+t)` 的 all-size Gram與 contractive
shift；local prime heat convolution只是 translated cross pairing，沒有正 norm。
P17 再給 uniform-in-k門檻：zero moments與 fixed-prime Laguerre derivatives有
相同 factorial/exponential base，僅差 aggregate `log k`。任何 exponential-in-k
或 absolute-value loss都不能閉合；需要 exact zero-loss identity。

P18 已構造 arch free Stieltjes measure `b4(r)dr/(2pi)`，但 arithmetic h_F
在 regular cut上有完全相同 density。目標 h 的 continuous part因此精確相消；
剩餘正 zero atoms不能由普通 submeasure subtraction產生。缺的是一個
self-adjoint boundary/extension mechanism實現此 spectral flow並排除 off-cut
resonances。

P19 限縮此 mechanism：standard finite-rank/trace-class boundary perturbation
保留 h_A 的 a.c. spectrum，不能產生 P19.1 的純 zero atoms；unitary scattering
亦保 spectral type。缺口必須是 singular domain change、經證正的 arithmetic
quotient，或獨立 operator construction。

P20 排除 generic positive model quotient：單一任意位置 Blaschke zero已有
positive model space及 pure-point Clark measures。存活 quotient必須額外帶
arithmetic polarization，使 scaling generator self-adjoint／two-sided unitary；
此額外條件仍未證。

P21 給 arithmetic input的 exact determinant：`1/zeta(s)=det(I-e^-sH_P)`，
完整 `G/G0` 是 arch gamma determinant除以 rational-times-prime defect
determinant。尚缺的 Hodge theorem須把 open semigroup leakage與 P18 continuum
exact配對，並在 cohomology留下 positive self-adjoint generator；不得新增
Euler product沒有的 mixed orbits。

P22 排除 standard fermionic Hodge實作：unique factorization使 exterior prime
Fock每個 energy `log n` 的 parity唯一，故 commuting odd differential只能為
零。arch continuum又不能 bounded exact intertwine atomic energies。尚缺的
只能是 singular/rigged differential及其非循環 positive polarization。

P23：P17 factorial moments其實滿足 Carleman，故 uniqueness不是缺口。
P18.4 的 regular density equality由 functional equation獨立證得；真正未閉合
仍是 h_F 的 cut-plane analyticity。不得把 boundary density equality誇大成
off-RH下的完整 spectral-measure cancellation。

P24 排除 scattering-phase singular route：exact ratio `D_F(-x)/D_F(x)` 等於
純 gamma ratio，G zeros全部取消。boundary unitarity與 time delay不含 RH
資訊。尚缺的是 absolute D_F divisor的 positive polarization，而非其 ratio。

P25 排除 fixed-Hilbert singular differential：closed strong spectral
intertwiner在 prime simple spectrum及 arch a.c. spectrum間必為零；point
evaluation型 rigging不 closable。尚缺的只能是帶新 positive topology的
nonstandard completion，而其 positivity/self-adjointness本身須證。

P26：即使不要求 closable，energy-fiber Euler characteristic `mu(n)` 仍是純
代數 invariant。只改 topology不能把負 parity變正；改 grading會改 Euler
determinant，跨 energy differential則失去 P21.4 invariance。尚缺全新的 graded
generator construction，而非 exterior Fock rigging。

P27 把 surviving operator gap定位成 hidden-state energy：G divisor在 scattering
ratio中完全不可觀測。須由 absolute D_F建立 full conservative arithmetic
realization，並證 hidden invariant subspace帶 nondegenerate positive metric且
determinant恰為 G。boundary unitarity本身不提供此 metric。

P28 已構造 finite prime conservative cascade，並修正「必有 mixed factors」
的過強說法：scalar cascade determinant可保持 Euler product。P29 的真正缺口
在 critical infinite limit：`sum_p1/p` 發散，無 Hilbert--Schmidt product或
Fredholm determinant convergence。尚缺 operator-level positive
renormalization，不能只用 meromorphic scalar continuation。

P30 定義可驗收的 partial mechanism：hidden negative index若為 `o(N(T))`，
由 orbit signature可得 density-one RH；full RH需 index恒0。當前首要缺口仍是
P28 cutoff state到 G-zero spectral projectors的 convergence，未建立前無法
從 finite positivity推任何 zero-density結論。

P31：positive direct-sum prime colligation存在；缺的是 determinant-class
connection。meromorphic/zeta regularization產生的 D_F divisor不是該 operator
spectrum。P30所需 convergence必須是 resolvent與 spectral projectors的 actual
operator limit，不能只是 scalar regularized determinant。

P32：Schatten det_3其實可在 `Re s>1/3` 定義並跨 critical line，但它無零；
zeta divisor全在 scalar counterterms `P_1(s)+P_1(2s)/2` 的 logarithmic
continuation。尚缺把這些 cumulants納入 positive operator cancellation；提高
regularization order不解 RH。

P33：det_q精確只等於 high prime-power tail的 exponential；low cumulants等於
`logzeta`減該 easy tail。用 analytic continuation補 cumulants就是循環。
尚缺的是 low prime powers+arch的直接 operator identity，而非更高 Schatten
regularization。

P34 經 P36 修正後不是獨立 divisor reduction。高 prime powers確為
`Re s>1/3` 的 zero-free analytic factor，但 `TrK_s+TrK_s²/2` 只在 Euler區
有直接 trace意義；其臨界帶 continuation由 `P_1(s)` 的 `rho/m` singularities
決定。用 logζ反向定義 low cumulants是獨立於 P33 的循環。尚缺的是完全不使用
zeta divisor的 low-orbit+arch operator construction；沒有它，two-orbit說法只
是 bookkeeping。

P35：prime與prime-square cutoff divergences分別為 `sqrtX/logX` 與 `loglogX`，
不同階，不能直接形成 positive relative trace。Möbius log cancellation只在
analytic continuation後出現。尚缺含 arch cross term的 sharp square，同時
完成 bulk subtraction與 parity remainder cancellation。

## G25：仍未窮盡，但剩餘方向須有可證偽中介引理

「已列路徑到達 RH-equivalent缺口」不等於「所有數學路徑已窮盡」。目前仍有
兩個不同攻面：W16/W18 的 centered arithmetic sharp square，以及 DN9--DN11
的 heat-flow collision barrier。前者下一個合格輸出是獨立的 positive
factorization；後者下一個合格輸出是 tapered weighted-discriminant identity
加 uniform clock commutator estimate。沒有這類中介輸出時，新的等價判準、
finite degree證書或 numerical positivity都不算新路徑。

P37 排除 Carleman shortcut。P15 critical atoms確給正 measure `mu_crit`，但
arithmetic moments與其 moments之差正是
`sum_off m u_rho^k exp(-t u_rho)`。regular cut density看不見 off-cut poles，
故 P18沒有證 moment equality。Carleman只在 positive measure已存在後給唯一，
不能從 candidate boundary measure補出存在性。

DN12 已完成其中第一個可證偽測試，但結果是否定的。weighted product taper
的 exact flux commutator在 clock lattice上是 multiplier
`i(theta-pi)/d` 的離散 Hilbert transform；慢 taper的平方成本與 block volume
同階，並不集中在 transition layer。故 DN線若續，須構造先扣除 clock PV
symbol的非局部 relative energy；普通 cutoff discriminant不再是候選。

DN13 找到正確的 linearized relative energy `Q=<u,Lu>`，其中
`ell(theta)=pi|theta|-theta²/2`，且 `Q<d²` 足以控制每個 gap。但從固定
`t_0` backward到 0 會把最高 lattice mode放大 `exp(pi²t_0/d²)`；以
`d~2pi/logGamma` 計，起始 energy須小到
`d²exp[-(t_0/2)log²Gamma]`。現有 theta moment saddle沒有給 zero-height層的
這種超多項式 clock rigidity。DN14又確認平均 energy目前不能跨過首次
collision轉成 density-one zero theorem；仍缺 collision index或 projector
convergence。

## G55. Toeplitz uniform wedge與 balanced critical cone

ES70 提供新的 genuine uniform-in-rank theorem：Xi ordinary coefficients的
consecutive Toeplitz minors `D_(r,k)` 在 `k>=10^18r^3` 全正。其 q-Pascal group
只作用於固定 `q_k,r` 的比較模型，控制參數恰為 `r^3/k`，沒有 `k->k-1` 的 shift
transport；所以不能從 wedge推到 `k=O(r)`。

兩個 exact 全階座標亦已寫清。Desnanot--Jacobi/Toda identity把 rank `r` positivity
等價成 rank `r-1` determinant row的 log-concavity，故不是自動 induction；矩形
Jacobi--Trudi把固定 `k` 的 growing-r determinant換成 fixed `k x k` reciprocal-coefficient
determinant。後者可由前 k 個 certified real poles作 fixed-k eventual proof，但 k 一起
增長時需要 growing Vandermonde與 tail的 uniform sign/conditioning，正撞上未知 zeros。

所以 degree 3仍沒有升階作用；它甚至不給完整 `D_(3,k)` row。剩餘 coefficient-side
缺口已縮成 balanced cone `r,k->infinity`、尤其 `k asymp r` 的 theta-specific Toda
invariant或二參數 Jacobi--Trudi pole theorem。ES71 contour-Hankel flow亦不補此缺口：
無 crossing時只作 congruence保 inertia，nonreal pair crossing恰是 indefinite jump，
全 PSD要求等價 RH。詳見 `toeplitz_uniform_route.md`。

## G26：horizontal-shift Hermite--Biehler descent

對 `E_a(z)=Xi(z+ia)`，HB threshold精確等於 zeros水平偏移的 supremum。
無條件 strip `0<Re rho<1` 給 `a>=1/2` 的 all-degree HB base，且
`A_a=[Xi(z+ia)+Xi(z-ia)]/2` 全實零。若能由 theta/primes證一個顯式 positive
kernel half-shift identity `K_(a/2)=T_a[K_a]+L_a`，即可 dyadic下降至 Xi並證
RH。一般 harmonic flow不保存此性質，toy `z²+1-a²` 已否證；缺口是 Xi-specific
untilting positive defect。只驗有限 kernel或用 unknown zeros定義 T_a均不合格。

HS7 又排除只靠 positive Fourier measure的 half-shift。正 measure frequencies
`1,2`、weights `1,2/3` 給
`F_a=cosh(a)cosz+(2/3)cosh(2a)cos2z`；在 `a=log2` 的 ratio為 `17/15>1`
而在 `a/2` 為 `5sqrt2/9<1`，前者全實零、後者有非實零。故 HS5必須使用
Xi-specific arithmetic total positivity；positive-definite smoothing不夠。

HS8 精確分類該 smoothing：`r_a=cosh(au/2)/cosh(au)` 的 Fourier density為
正的 `(sqrt2 pi/a)cosh[pi t/(2a)]/cosh[pi t/a]`，但 reciprocal bilateral
Laplace transform `cos(as)/cos(as/2)` 有 poles，故不是 PF_infinity。
因此缺口是此正卷積與 Xi theta kernel的 coupled total positivity，不是證
r_a positive definite。

HS9 顯示 A/B channels分別由 r_a與
`q_a=1/[2cosh(au/2)]` smoothing。雖 q_a是 PF_infinity且 r_a-q_a仍 positive
definite，方向仍錯：normalized q-convolution把 `z²` 精確送成
`z²+a²/4`，會創造 imaginary zeros。故缺口不是兩個 scalar total-positive
operators，而是它們作用於 Xi `(A,B)` pair後的 coupled symplectic Bezoutian。

HS10 的 duplication audit：若 b=a/2，則
`A_b(z+ib)+A_b(z-ib)=A_a(z)+Xi(z)`，而 B-channel只回 B_a。故 inverse-shift
下降必然顯式帶回 endpoint Xi；把相應 K_0/cross Bezoutian塞進「positive
remainder」即循環。合格 HS5 identity須從 theta/primes直接證該 cross sign。

HS11 的 known-GRH toy顯示成功所需 input：功能域 factor由 Hasse bound得到
shift-independent unitary Frobenius phase，因而所有 horizontal shifts同時
HB並可由直和組合。Riemann尚無對應 global unitary arithmetic monodromy；
local prime colligations不在 critical infinite limit收斂。

## G27：目前共同 blocker

W16/P13/HS、spectral cohomology與 DN三個最後攻面，分別要求 global arithmetic
polarization、positive hidden generator、或超多項式 zero-rigidity；現有
identities均未提供。所有普通升階、smoothing、boundary、trace regularization、
finite certificate與 density shortcut已由本文反例或循環稽核封閉。除非取得
新的 Xi-specific arithmetic identity，目前沒有剩餘可執行的非循環步驟。

## G28：聯網後重開的 finite-volume/prolate uniform bridge

2026 Suzuki 已無條件構造每個有限 `a` 的 localized Weil operator、deficiency
`(1,1)` 微分生成元與全實零 characteristic function；故「finite-scale hidden
self-adjoint generator 不存在」已不再是 blocker。Connes--Consani--Moscovici
又已嚴格證 explicit prolate candidate `k_lambda` 的 Fourier transform在
`|Im z|<1/2` closed substrips locally uniform收斂到 `Xi`。

剩餘斷層可壓成單一 uniform bridge。若 `r=(A-mu)k`、
`Delta=epsilon_2-mu>0`，spectral theorem給 ground-space distance至多
`||r||/Delta`；要升成 strip-uniform Fourier convergence，充分條件是每個
`eta<1/2` 皆 `lambda^eta||r||/Delta ->0`。prolate leakage本身為
`exp(-4pi lambda^2)` 級，量級足夠；尚缺把它非循環地傳到 arithmetic Weil
residual並控制 parity-sector gap的 exact intertwining theorem。這是新的
all-scale可證偽路徑，不是 finite certificate。詳見 `external_spectral_inputs.md`。

進一步由 Connes--Consani 的 `E`-radical 得 exact identity：截斷
`k=1_I E(f)` 對 interval test的 Weil residual只等於外部 tail的 cross form。
因此 bulk intertwining其實已存在，剩 smooth-domain與加權 tail estimate。
但此 identity只定位 near-zero spectrum；RH若假，負 eigenvalues仍可在其下。
故真正尖銳的 G28 blocker是 spectral ordering（證 prolate near-zero band位於
bottom且 rank one），不是只把 residual做小。任何用 `A_a>=0` 證 ordering均循環。

ES7 已把此警告升成 theorem-level audit。localized bottom `epsilon_1(a)` 隨
`a` 單調不增；Suzuki 2026 又證 RH 假時某個 `epsilon_1(a_0)<0`。故其後皆
`epsilon_1(a)<=-c`。若 prolate `mu,r` 趨零而 `||r||/(epsilon_2-mu)->0`，
spectral expansion反迫 `epsilon_1(a)->0`，矛盾。因此 hook 所問的分母下界
確會在 RH 假時退化／失去 bottom ordering；證出足夠 uniform gap本身已是 RH
核心，不是 residual之後的常規 perturbation。ES3降級，ES6 boundary-radical
identity保留為獨立成果。

新的 G28 分叉是不使用 ground：(A) 直接由 prolate--`E` intertwining證 explicit
`hat k_lambda` 全實零；(B) 由 Suzuki finite-volume extensions 的 Weyl
`m`-functions在 `Im z>1/2` 證趨近 `i xi'/xi`，再用 Nevanlinna normal family。
(B) 尚須證 shift-free cross-ratio；若需 `lambda(a)->0` 就再次等價 positivity。
ES9 已導出 prolate ODE 經 Mellin/`E` 後的 exact `s->s+/-2` zeta-ratio recurrence，
下一個具體檢查是 functional equation能否給不含未知 `1/zeta` poles 的 Hermitian
transfer-matrix symmetrizer。詳見 `external_spectral_inputs.md`。

ES9.1 已完成首輪檢查：functional equation確使兩側係數精確共軛，middle為實，
但所得 HB 候選
`R(z)=4pi^2 lambda^2 zeta(1/2+iz)F(5/2+iz)` 仍顯式含 critical zeta因子。
`R` 上半平面無零已直接排除 `Re rho<1/2` 的 off-line zeros，故 untruncated
transfer只是 RH 同義改寫。唯一未封閉的新機會是保留 CCM hard truncation，
把 ES6 boundary項變成不含 exact zeta因子的 finite-volume HB determinant；
不得先令 boundary消失再聲稱 positivity。

ES10 把保留 boundary 的問題有限化：
`K_lambda=sum_(n<=lambda^2)n^-p int_(n/lambda)^lambda f(x)x^(p-1)dx`。
cutoff step在 `x=n/lambda`，Green identity的 jump權重精確化為共同相位
`lambda^(1-p)` 乘 scalar `1/n`。但 jump另乘符號不定的
`(lambda^2-x_n^2)f'(x_n)`，且位於 test weight而非 ODE potential；不能稱為
positive rank-one或直接用 2x2 J-unitary。新的 target須是含 accumulated-integral
channel的 3x3/inhomogeneous colligation及其固定 metric positivity；尚無此 sign，
故 RH仍未閉合。

ES11 解完 local metric equation：3x3 system唯一 fixed conserved Hermitian form
在 accumulator方向退化，故逐 interval固定-J proof不可能。4x4 frozen-dual-port
symplectic dilation雖存在，但對任意 forcing都存在且 Hamiltonian indefinite，
不蘊含 HB。依 nudge修正：這不排除 **累積** 正性；正確未閉合式是找 companion
`B_lambda`，把完整 `n<=lambda^2` 和的 de Branges kernel (ES11.4) 寫成 Gram
factorization。逐 n 不需正，符號項可望遠鏡；但目前尚無 cumulative identity。

ES12 給 cumulative identity的 operator座標。symmetrized approximant仍趨近 Xi；
其 half-support transform `E_lambda` 滿足 `F_lambda=E_lambda+E_lambda#`。故只需
證完整 ratio `U_lambda=E_lambda#/E_lambda` inner，等價 Hardy projection
`P U_lambda=P U_lambda P`、亦等價 ES11.4 kernel正。Connes--Consani 已顯示
individual local factors不是 inner，確認只能靠累積 cancellation。prolate
leakage只給 approximate Hankel defect，沒有 uniform boundary margin時不足以
排除非實零；缺口是 exact cancellation或全上半平面 coercive domination。

ES13 提供具體 all-mode升階：若 boundary-unimodular `U_lambda` weak-star收斂，
且其 Hankel defect在 dense Hardy core逐向量趨零，則極限 multiplier屬 Schur；
再有 boundary modulus retention才 exact inner。不需 operator-norm defect或逐 n positivity。fixed-index prolate functions
趨近 dense Hermite basis，故可能提供此 core。尚缺：(i) arithmetic ratio defect
與每個 fixed-n leakage的 exact intertwining；(ii) ratio denominator compactness
及 modulus retention；
(iii) companion coprimality。前幾 mode數值不足。

ES14 排除把 prolate leakage直接餵給 ES13。Poisson exact intertwining只是
`R E=E F`，控制 output的 inversion parity；Hardy target是 multiplier
`(1-P)M_U P` 對全部 inputs。even/inversion defect為零的 kernel仍可有 nonreal
Fourier zeros（HS7 已有 exact反例），故不存在只靠 parity leakage的 universal
Hankel bound。ES13若續，必須另有 Xi-specific cumulative Bezoutian/score Gram
term；prolate leakage只能控制其 error，不能提供 positivity主項。

ES15 把剩餘 cumulative sign展開：HB/anti-Pick等價
`partial_eta|F_lambda(t+i eta)|^2>=0` 對全部 `t,eta>0`。ES10 給其 exact
all-(n,m) 四重和 (ES15.3)，個別 jump可負，只要求總和重排為 Gram squares。
`eta->0` 首階只是 Laguerre inequality，有限 moment/degree結果不足。此 target
與 A9.3/HS5同一 obligation；唯一新機會是 finite arithmetic/prolate coordinates
允許 summation-by-parts telescoping。

ES16 完成第一次 Green 分部。單 eigencomponent有 exact recurrence (ES16.1)，
aggregate boundary除 `q_m f'/m` 外還有 `-(p-1)q_m f/m^2`，不得漏項。bulk的
`p+/-2` shifts帶不同 `m^+/-2` channels，反覆後生成無限 arithmetic hierarchy，
3x3/逐 m不閉合。且實際 h_lambda是 chi_0、chi_4不同的兩 eigenfunctions組合；
ES15須拆四 channels。唯一尚可能有限閉合的是由 `chi_4-chi_0` 與 zero-integral
coefficient relation產生 coupled Christoffel--Darboux/Wronskian identity。

ES17 回應最新 nudge：`cos[t(r-q)]` 本身就是
`(cos tr,sin tr) dot (cos tq,sin tq)` 的 rank-two PSD Gram，故 t-oscillation
可完整吸收。真正不定性是 `(r+q)e^-eta(r+q)` 的 signature `(1,1)`。
ES15 sign等價兩個 cumulative vectors `v,w` 滿足 `v dot w<=0`。所需 CD輸出
應是 ES17.2 的 dissipative polarization；兩 prolate modes若不能在四 channels
合計後產生 positive symmetric part，望遠鏡仍不成立。

ES18 將兩-mode Wronskian做到底：`omega4-omega0` 只可重寫 04/40 cross
channels；00、44在 `L_x-L_y` 下 eigenvalue difference為零，無法解出。
zero-integral係數只是一個 Mellin point的線性關係，不能消全 `t,eta` diagonal
scores。故正確剩餘 theorem是 2x2 vector-valued score matrix全上半平面負半定，
或至少其特殊 c-direction非正；這正是 HS9 coupled Bezoutian，非免費 CD closure。

## G29：matrix de Branges 與新 prolate auxiliary ground state 的斷層

外部 matrix/operator-valued de Branges 理論均把 matrix inner/positive kernel
列作輸入，沒有由兩個 prolate modes產生 sign；要求 full 2x2 score negativity
還會強迫每個 diagonal mode單獨為 HB，屬 RH-level過強命題。故只保留 CCM
zero-integral coefficient direction。

另一方面有新的無條件 all-mode theorem。於正 finite-Fourier phase支
`H_+=closure span{h_0,h_4,h_8,...}`，

```text
Q_lambda=(PW-omega_0)(PW-omega_4)+ell^*ell >=0,
ker Q_lambda=span{h_lambda}, ell(f)=int f.
```

所以 `h_lambda` 是具有 auxiliary gap 的唯一 ground state，完全不依 RH／Weil
ordering。這不是 finite degree certificate。但 CvS 實零 theorem要求差核
`D(x-y)`；`Q_lambda` 是變係數四階 operator，且與 scaling generator的 commutator
有 infinite-rank bulk。剩餘缺口是證 arithmetic truncation `1_I E` 將此正形式
變成 log-convolution/Toeplitz form（至多可控 boundary），或直接推出 special
score direction。單獨引用 `Q_lambda>=0` 不足，因任意函數皆可人工成為 PSD
operator的唯一 kernel。

## G30：exact double-zero 修正與 full conjugacy no-go

ES6 的 global E-radical需要 `f(0)=int f=0`。finite CCM h0/h4 combination只
exact 滿足 integral zero；其 value defect為
`c0 h0(0)(1-tau0/tau4)`。Connes--Consani 2021 的原 prolate vectors亦只
exact 消 value，Fourier parity明寫為 approximate。因此 two-mode不可直接稱
exact radical input。

加入同 phase h8 後，三 modes可 exact 消兩 constraints，係數有閉式
`d=(tau4-tau8,tau8-tau0,tau0-tau4)`。在正 phase tower，三個相鄰 spectral
factors之積半正定；更一般 r constraints有 r+1 modes的 uniform theorem與
positive discrete measure/Lanczos表示。這是新 all-mode structure，但不是
Jensen degree升階。

full operator經 E 共軛成 CvS convolution的希望已被排除：Mellin bulk含
`p+/-2` shifts，cubic含到 `p+/-6`，finite boundary rank不能把它變成 multiplier。
剩餘唯一 target是三模態 special direction的 cumulative HB score。另須把
Fuchs leakage ratio、fixed n=8 uniform asymptotic與 hard-support smoothing寫成
完整 estimate，才能稱 exact E-radical approximant converges to Xi。

## G31：strip target、endpoint tail 與 Weyl--Volterra 新分叉

全平面 HB target已降為足夠的 `0<eta<1/2`。natural one-sided Xi half-kernel
companion在此帶內已有明顯 modulus-difference負值 diagnostic，故不能靠 Pólya
凸核 criterion。三模 hard cutoff的高頻不是單 endpoint，而是 ES26.2 的 truncated
Dirichlet--sine polynomial；目前未見 critical-strip反例，但需 uniform
Hermite--Biehler theorem及 remainder Rouché bound，浮點 scan不算證明。

新的獨立 all-size輸入是 Freedman 2606.29555 的 Weyl--Volterra branch
contraction。其 KLM-to-de Branges橋並非形式 equivalence：`omega->0` 時橋必直接
factor Xi Bezoutian `B_Xi`，即先前 all-degree anti-Pick義務。Mellin tail可對角
intertwine，真正缺口是 incomplete-gamma moving prefix。下一個合格工作只有兩種：

1. 對 ES26 endpoint polynomial證 strip stability並建立 uniform high-frequency
   remainder theorem；或
2. 從 theta atoms構造 z-independent Hardy--Volterra isometry，同時搬運 prefix與
   tail，exact產生 `B_Xi` Gram。

只重跑 KLM finite certificates、把 z-dependent target trace加入 graph norm、或
引用 abstract Moore--Penrose repair，都不能關閉 G31。

## G32：endpoint-jet tower 的 rank 與 central-limit 缺口

新增 T3P9/ES29：用 `m+3` 個 same-phase modes，同時消 E-radical兩 constraints與
前 m 個 endpoint jets。這使全部 arithmetic cutoff的內部 jumps統一延後，留下
single-sine high-frequency主項，是目前最具體的 uniform smoothing/升階機制。

rank項已完成；未閉合處有兩個，且均需 theorem而非更多 root scans：

1. 用 Dunster endpoint asymptotics證新增 boundary modes的 central coefficients
   消失，故 fixed-m approximants仍 locally uniformly趨 Xi；
2. 建立 eta-linear HB margin的 uniform integration-by-parts/Rouché bound。

此 tower只能處理 high-t與hard-support；bounded-t special score仍由 G31 的
Xi-Bezoutian/Volterra prefix bridge承擔，不能以收斂本身倒推。

## G33：exact K_0--Bezoutian bridge已關；只剩原始 K_0 positivity

新的 VK6/ES32 直接算出

```text
B_Xi(w,z)=4/pi int int K_0(q,q')e^(izq-i conj(w)q')dq dq'.
```

所以先前 G31 所稱「未知 Hardy--Volterra isometry」在 `omega->0` tangent並非
必要：Fourier--Laplace evaluation map已給 exact pullback。若證原始 coordinate
kernel `K_0` 在 compact tests上 PSD，cutoff limit即給 Xi Bezoutian全尺寸 PSD，
從而 RH。這是目前最短的精確充分定理。

但 Freedman 現有 normalized quotient certificate仍未等於原始 quadratic form；
論文自身把 quotient-to-original closure列為 external gap，而且其中若含 finite/
numerical certificate不能替代解析 positivity。下一棒應只稽核 `omega=0` 的 parity、
mixed-derivative、Volterra primitive與 closure：證每個 compact test的原始 Q 等於
closed quotient Q，且 quotient positivity不依 finite grid。uniform omega與
finite-omega branch transport皆可暫停。

另已否證以固定 Platt--Trudgian height補 endpoint tail：bandwidth c無界使可靠
tail onset漂移，留下增長的 middle band。這不能取代 K_0 global positivity。

進一步稽核 Freedman Problem 15.15：primitive Green boundary repair其實為零，
且 primitive trace image在完成後稠密於整個 `X_R`；故不存在只需在較小 image上
證 repair消失的捷徑。剩餘 `D_q=0` 等價 `Gamma^*Gamma<=C`、等價 full form
`Q_Phi>=0`。有限 Schur complement正譜僅為 diagnostic。下一個合格突破必須是
`D_tr` 的 explicit continuum Gram integral，不能再引用 abstract quotient theorem。

VK6 的 Taylor expansion另給真正的升階答案：全部 Bezoutian coefficient matrices
都是同一 K0 form中 `{1,q,...,q^N}` 的 Gram compressions。這是 uniform-in-degree
結構；但它以 K0 PSD為共同前提。degree 3獨立成果不提供此 premise，任何有限 N
驗證也不能回推 continuum positivity。

## G34：外部全階輸入稽核後的剩餘斷層

Burnol Sonine空間提供正 ambient de Branges geometry，但沒有 `Xi=structure
function` 的 target identification；一般 Sonine函數可有任意附加零。Dimitrov 的
orthogonal-polynomial Wronskian／Lee--Yang wave function逐式等價於全 Jensen塔，
普通 moment Hankel positivity或 Karlin--Szego real-axis Wronskian定理不提供所需
rotated全階符號。

Holland 2608.08682 新證 uniform wedge
`n^3 log^2(n+2)>=K d^5`，是真正的 degree--shift 聯合 theorem；但其 complement
仍含 `n=0, d->infinity`。關係
`(J^(d+1,n))'=(d+1)J^(d,n+1)` 不能反向傳遞實根，除非另證 critical-value
alternation；該 alternation本身就是低-shift RH-scale positivity。

因此目前可行而非循環的研究分叉縮成三個：

1. 證 `K0`／`D_trace` continuum Gram或 Hardy--Volterra contraction；
2. 把 `Phi(t)dt` 表成已知 Lee--Yang measures 的保零封閉極限；
3. 找一個從 Holland wedge 向下傳 shift 的 uniform critical-value/interlacing theorem。

其中 2、3 尚無具體 representation/inequality；在出現前主線仍是 1。這不是窮盡
所有想像，而是排除了把 positive ambient space、OP三項遞迴或 high-shift wedge
誤當成低-shift全階證明的跳步。

另 ES39 精確量化 wedge complement的硬度：fixed n 時
`J^(d,n)(X/d)->F^(n)(X)` locally uniformly，`F(X)=xi(1/2+sqrt X)`。因此只要證
`J^(d,0)` 對所有 sufficiently large d hyperbolic，就已由 LP closure直接證 RH。
這排除「再改善 joint asymptotic便自然覆蓋 n=0」的想法；要跨入該區必須引入
K0/Lee--Yang/critical-value之類真正 RH-scale全正性，而非提高 wedge常數或階數。

route 2 現有一個嚴格 closure theorem：Newman--Wu 1708.08820 保證 Lee--Yang laws
的 weak limit仍 Lee--Yang。因此不缺極限定理，缺的是一族可寫出的 finite
ferromagnetic magnetization laws `mu_N` 及 `mu_N=>Phi dt/int Phi` 的證明。任意
quadrature、有限矩匹配或只近似 Phi尾部不保 Lee--Yang，不能充當此 construction。

K0B9/VK9 又把主線的 reflected contraction具體化：若
`F(p,d)=1/2 int_|p|^infty yPhi(y+d)Phi(y-d)dy`，則 half-line blocks是
`A=F(p,d), B=F(d,p)`。現在所缺可精確要求為一個 theta-specific feature
intertwiner `A=T^*T, B=T^*ST, S=S^*, ||S||<=1`。沒有 S時這仍只是
`-A<=B<=A` 的座標化；generic smooth-even counterexample阻止一般性定理。

K0B10--11 提供另一個 uniform接口：symmetric double-tail potential
`P(q,r)=sum c_m(q)r^(2m)` 若每個 `c_m` 都 completely monotone，兩 parity kernels
便同時成 Laplace monomial Gram和，直接關閉所有 sizes。缺口是證
`(-1)^k c_m^(k)>=0` 對所有 `m,k`；目前連首個 `c_1` 也只化為 exact 一維 theta
積分 (K0B11.2)，數值正號不算證明。近期優先嘗試 `c_1` 的正 Laplace重排；若它
失敗或出現 rigorous反號，立即淘汰此充分條件而不影響 K0等價主線。

K0B12 已給 rigorous淘汰：`c_0(q)>0` 與 `-c_0'(q)>0` 都因 theta double-tail而
比任意 `exp(-Aq)` 更快衰減；非零 completely monotone函數則必下界於某個
`C exp(-Mq)`。故 coefficientwise Bernstein--Gram不可能成立，低階交替導數正號
只是有限階假象。剩餘全階路線必須耦合不同 r-orders，或回到 VK8 的 shifted-theta
feature／Hankel-square Loewner monotonicity；不得再追 coefficientwise CM。

K0B13/VK10 又把 full-line form exact壓成
`Q_K0=-Re<B_f,A_f>/2`。以已證遞增 score `q=-Phi'/(tPhi)`、`c=q(0)` 拆成
Gaussian boundary square `|A(0)|^2/(4c)` 與 residual `-Re<E_c,A>/2`。pointwise
odd sign不控制 arbitrary complex f；缺口是 boundary-dominated Volterra
contraction (K0B13.6)。ES41/VK11 則給另一 all-size接口：若能把 theta Hankel
sign-symbol正則化，證 `sigma'/sigma` 具有 anti-Loewner正測度表示即可關 same-sign
block；但 distribution regularization與 reflected block皆未閉合。

K0B14 又完成非循環稽核：K0B13 的 boundary/residual拆分正是
`Y_c=e^(z^2/(2c))Xi` 的 Bezoutian gauge identity；residual仍承擔原 all-size
困難。Riemann超指數尾也排除 `Phi=Gaussian*positive measure`，所以不能由 score
單調宣稱 positive heat deconvolution。只有直接 theta factorization residual才算
進展。

VK12/ES42 進一步關閉 standard anti-Loewner symbol捷徑：ordinary nonzero sigma若
有 anti-Loewner `sigma'/sigma>=0`，便固定正號，使 Phi completely monotone，與
超指數尾矛盾。只有改變 reconstruction的 theta/multiplicative symbol尚未排除，
但不能再直接引用 VK8.5/ES41。主線優先 K0B13 residual的直接 coupled factorization。

K0B15/VK13 現以 decaying positive first-order primitive R 給有限 storage identity
`Q_K0=|U(0)|^2/4+||U||^2/4-Re<LV,LU>/2`。真正缺口是 common-range graph bound
K0B15.4；`R>0` 或普通 Cauchy--Schwarz皆不足。K0B16並以解析 saddle exponent
嚴格否證逐 theta-pair PSD：off-diagonal `(n,m)` reflected contribution比 same-sign
慢衰減，pair odd eigenvalue終為負。故必須利用完整 theta和的跨 channel cancellation，
不能把平均正性提升成逐 integrand／逐 channel正性。

K0B17/VK14 利用 J5 的 radial convexity與保測度換元，已嚴格證 full
`K_odd(x,y)>=0` 對所有 half-line points；這成功把完整 theta和的積分平均降成逐
integrand比較。但 entrywise positivity仍不等於所有 Gram matrices PSD。剩餘精確
缺口是將 convexity差 factor成一族 PSD kernels（或證相應 higher total positivity），
不可把 pairwise sign當 all-size positivity。

K0B18 已把 pointwise正差寫成雙正積分；但其 standard matrix lift要求 h operator
convex／`h'` operator monotone，而 `h'(s)~pi e^(2sqrt s)/sqrt s` 超線性，解析排除
此路。故剩餘不是再證更強 scalar convexity，而是為整個 z/s path integral找
theta-specific coupled Gram。

## G35. L7 的斷層已縮成 unbounded log-derivative Hankel flux

K0B19--22 回答了 nudge 所問的 compression/norm：`L=D-1/2` 確實
無界，但 whole-line graph 有 exact symmetric cancellation。更強地，
`1/(1/2+i xi)` 是負半線 causal kernel，其 positive compression 恰等於
L7 的全部 boundary/storage 右邊。故剩餘缺口只是

```text
Re<P_+M_(iXi'/Xi)P_-w,P_+w><=0,
w in Ran(T_Phi).                                  (G35.1)
```

且左邊 exact 為 `-2Q_K0`。所以 G35.1 不是比 RH 弱的 norm lemma，
而是原 continuum positivity 的最小 off-diagonal 版本。由 range 的 ordinary
`L2` 稠密性，bounded Nehari/contraction 路徑不可能；必須找帶 Xi-zero
cancellation 的 graph topology Gram。

## G36. 聯網後的 shifted-screw 斷層

Suzuki 2206.03682 的 `Psi_omega` 有 explicit positivity-preserving forward Volterra
semigroup，並無條件給 `omega>=1/2` 的正性。但 inverse 不保正，且
`Psi_0>=0` 本身等價 RH。所以外部輸入沒有關閉 half-shift descent；
它只把新的合格缺口定為：構造一個 theta/primes 可驗證的 proper
invariant subcone，使 forward semigroup 在此子錐上可逆保正。

## G37. Selberg nudge 結論：H2 值域稠密，L7 沒有子空間降階

`C_Phi` 是 injective dense-range nonclosed convolution operator；`P_+Ran(C_Phi)` 在
`L2(R_+)` 稠密，所以 Fourier/Paley--Wiener 後在 `H2` 也稠密。
common-range 只有 graph norm 不同，沒有餘維。graph norm拉回後的
bounded operator就是 K0，所以沒有比 RH 弱的 hidden contraction。

## G38. local Green 與 naive shifted-graph cone 兩條路徑關閉

K0 parity kernels在 interior diagonal real analytic，故不可能是任意 finite-order
local differential/Sturm--Liouville Green inverse；後者必需 delta jump。另一方面，
shifted graph spaces的 same-preimage transfer對任意 Xi都 unitary，是 tautology；
要求 output-side Hardy causality即要求 `Xi(z+i nu)/Xi(z+i omega)` all-shift
Schur，等價 RH。所以仍可行的只有不使用 division by Xi 的
theta/prime local cone，或 nonlocal/infinite-order Gram/resolvent。

## G39. PF∞ 正和、generic heat descent已關；prime common energy仍未閉合

外部輸入沒有補上 all-degree positivity。raw classical Phi 由 Schoenberg zero-free
必要條件已解析排除 PF∞，且 arXiv:2602.20313v2 給 certified PF5反例。Watson
2602.01248 的 Markov-cycle PF∞結論依賴錯誤的「positive sums preserve PF∞」Lemma；
translated Gaussian的 exact `2 by 2` determinant已否證，該稿的 standing centered
symmetry亦直接不成立。

de Bruijn flow下 Bezoutian雖有 exact `R times R^3` radial backward-heat PDE
K0B28.2，但 polynomial `z^2+1-2t` 證明由已知正時刻向 `t=0` 的 generic descent
不保 PSD。這兩條都不能成為免費升階。

目前新而具體的未閉合點是 K0B29/L9：theta prekernel有 exact prime Euler--Volterra
factorization。需找到 **同一個** 含 Archimedean completion的 K0 quadratic storage，
使所有 prime shift resolvents contractive並容許 infinite-product closure。沒有此
common energy時，它只是在 Euler收斂半平面的 pointwise positivity；zeta的 analytic
continuation困難完全未被處理。

## G40. prime-local positive cone只活在 absolute Euler half-plane

completion normalization把 K0B29 的 Euler factors變成
`(I-p^-1/2 T_(2log p))^-1`。在 natural exponential weighted L2 中，finite prime
product norm於 zero frequency精確含 Euler product
`prod_p(1-p^(-(1/2+2sigma)))^-1`；因此 uniform boundedness需要
`sigma>1/4`。critical target是 `sigma=0`，而 Archimedean polynomial與 shifts
commute，不能改善此 divergence。

所以「每 prime positive contraction + monotone infinite product」並非新的降階機制，
只重述 `Re zeta>1` 的 absolute convergence。若續 prime路線，唯一未排除型態是
signed gamma/pole counterterms與 primes在 **同一** quadratic form中 telescoping；
這正是 `weil_square_route.md` 的 all-test square obligation。需要新的 explicit
identity，不能再把 positive Euler resolvents本身列為候選突破。

## G41. real-rooted approximants缺少的正是 LP-limit theorem

K0B31 的 Bezoutian product rule確認「real-entire positive factors + locally uniform
limit」會是真正全 degree升階。但 Euler factors不 entire，Shi 1502.06844 的
Pólya-like kernels也只匹配 tail與少數 central jets，沒有 family趨向 Riemann Phi
的 norm／transform convergence。若補 locally uniform transform convergence，LP
closure已立即證 RH。因此 approximation路線的最小缺口是構造一個有 global
domination的 convergent LP exhaustion；更多尾部/有限 jet匹配不算進展。

## G42. 跨 sigma=1/4 的一致估計：現有 family極限可算且錯誤

依 Selberg nudge重寫 G41：缺口不是「每個 approximant實零」，而是 family在穿過
Euler absolute boundary後仍以 Phi為極限的 uniform estimate。K0B32 對 Shi第一族
完成此檢查；它在任意 exponential-weighted L1 中收斂，但極限是

`cosh(a)+2beta[sinh(a)/a-(cosh(a)-1)/a^2]`

乘 Pólya envelope，並帶 `2beta/a` algebraic tail correction，所以不是 Phi。
這是 limits `m->infinity`、`t->infinity` 不可交換的 exact反例。

尚未閉合的 L10 要求某個真正 LP family滿足 K0B32.5。該單一 estimate已足以用
Hurwitz證 RH；在沒有 construction前，不得以 tail ratio、有限 jets、有限 zeros
matching或逐 degree實根性代替。

## G43. LP exhaustion 是等價條件；二維 theta--Weyl 分解仍缺完全正性

Masters' Nudge 的反向檢查修正 L10：RH若真，取 `K_N=Phi` 的常值族即滿足 L10；
故 L10與 RH等價，不是降階。除非能從無條件的 theta／prime operations構造 family，
否則 approximation分支停止。

K0B33--34 提供新的 all-degree精確介面：K0的 Weyl symbol是 Riemann Phi Wigner
function的 weighted tail，而完整 theta channel乘積是 covolume-fixed rectangular
2D lattice theta，completion後給 K0B34.4 的 scale--shape differential identity。
斷層也已明確：Hudson theorem迫 raw Wigner變號；正 Weyl symbol亦不足以保 operator
positive；K0B34.4 的 bulk與 boundary各自無固定號。所需新定理必須是 theta-specific
anti-Wick／Kraus／star-square factorization，或一個把 modular scale--shape PDE
轉成該 factorization的升階定理。僅再證 pointwise symbol sign或有限 minors不合格。

## G44. Weyl symbol的 scalar Laplace positivity已與 RH等價

K0B35 證

```text
int exp(2sp)sigma_K0(p,xi)dp
 = [8s]^-1 d/ds |xi_R(1/2+s+i xi)|^2.
```

Lagarias horizontal logarithmic-derivative criterion使右邊對所有 `s>0,xi` 正，恰好
等價 RH。故不能把「證 `sigma_K0>=0`」或「證它所有 exponential moments正」視為
較弱中間引理；前者還比所需更強，後者已 exact等價。K0B34 的 modular theta PDE
只有在能直接導出 operator Kraus/star-square、而非再導出上述 scalar monotonicity時，
才可能構成真正升階。

## G45. positive two-sine amplitudes不是升階；需 theta-specific coupling

ES52 的 scalar compensation identity最後仍要求一個與 RH等價的全域 oscillatory
integral為正。K0B36 更以 exact kernel證明：正、偶、analytic、Schwartz、strict
log-concavity與 `-[log K]'(x)/x` strict increasing可同時成立，而 Fourier transform
仍有 `pi +/- i arcosh(3/2)` 非實零。故 J5與 gradient anisotropy不能單獨關閉任意
degree。未閉合條件必須排除該 Gaussian mixture，亦即明寫 theta modular lattice
coupling並產生 operator-level completely-positive factorization；否則只是另一個
RH-equivalent scalar reformulation。

## G46. 最新 Riccati/paired-tail/GGC 外部稿未提供缺失的 operator positivity

ES53 對 Planat paired-tail稿找到原點 Taylor contradiction，其 pre-crest與 global
bridge原文亦仍 open；不能採用其 curvature chain。ES54 的 Wald/GGC稿明認 mixing
measure signed，剩餘 complete monotonicity在目標區域與 RH等價。故 Riccati scalar
curvature、paired oscillatory blocks、probabilistic infinite divisibility三種語言都尚未
產生 K0的 CP/Gram分解；未閉合點仍是 signed prime--gamma／theta modular cancellation
如何在 operator level合成正平方。

K0B36.5 又把反例加強到 `p'>0,R=(p^2-p')'>0`，所以最新 paired-tail稿的 Riccati
輸入即使修正 local公式後也不可能成為一般 zero-location theorem。缺口不是再證更多
scalar derivatives有正號，而是找只對完整 theta格點成立的 matrix/operator identity。

## G47. hyperbolic theta PDE後只剩 normal-stress positivity

K0B37 是目前未被 Gaussian-mixture反例排除的 theta-specific all-degree介面：完整
2D lattice theta滿足 scale--shape PDE，completion在 rectangular geodesic變成
`N^2-partial_s^2` 的 normal stress。缺口是證其 K0 cone integral為正 energy flux。
標準 wave/heat energy不能直接套，因符號是 hyperbolic、資料只在 geodesic normal
jet，且 `(m,n!=0)` subtraction不給完整 automorphic positive state。若無一個明寫的
Green identity與正 boundary norm，這仍只是 K0的微分改寫。

## G48. uniform Jensen 楔形與 RH之間是無窮 reverse-shift 斷層

ES56 已提供真正任意 degree 的結構：Holland 的 finite-free comparison一次證明
`d <= c n^(3/5)log^(2/5)(n+2)`。所以「degree 3是否有升階機制」的回答仍是沒有；
新增的升階來自外部五階穩定性，而非 degree 3 證書。

尚未關閉的是整個楔形補集，尤其 `n=0` 的全部 degree。已知操作方向為
`(J^(d+1,n))'=(d+1)J^(d,n+1)`，只能 degree下降、shift上升；inverse Rolle一般為假。
finite-free交錯也只在 forward convolution保持，且正根 inverse由 ES57明確排除。
因此不得以更多 fixed-order matching冒充閉合。合格突破只可能是 L11 的
Xi-specific reverse shift/common interlacing，或完整 all-order positive factorization。

## G49. raw moment mixing與 generic reverse shift皆已排除

J66 證 Riemann tilted moments的自然 multiplier polynomial在 degree 2 已因
`-4 Var(U^2)<0` 非雙曲，故「正 Laguerre mixture」不能直接轉成 finite-free正根
factor。J67 又證即使 coefficients全正且所有 shift `n>=1` 的 derivative/Jensen
tower皆雙曲，也不推出 shift 0。故 L11 不可由一般 moment positivity、Rolle或
interlacing inversion得到；必須加入一個對 theta/prime kernel特有、且能固定積分常數
的全階 identity。

## G50. claimed real-rooted Xi approximants 經 exact audit 失敗

ES59 找到 Shi 1706.08868 的核心偶/奇截斷 index error：`2j` 次有限和被錯改成
只到 `j=m` 的全次和，而非到 `2m`。因此其 hypergeometric tail與 interlacing
並非原 approximant的定理，不能填 L10。這也再次說明「uniform convergence」本身
不是缺口；必須對同一個正確定義的 approximant嚴格證 LP/實根，且所有截斷量詞
保持固定 target。現無此 family。

## G51. canonical causal support與 theta heat positivity停在 endpoint/變數斷層

ES60 把全階 de Branges機制壓成清楚 support target：
`u_Xi=(Xi-iXi')/(Xi+iXi')` 的 inverse Fourier transform須支撐於正半軸。
但 `u_Xi inner iff RH`，而 theorem在辨識 `t=0` endpoint時先假設 inner/HB。
尚缺的是不用 `1/E_Xi` 或 zeros 的 theta/prime causal factorization；shifted
`omega>=1/2` chains不能自動逆傳到 `omega=0`。

ES61 的 Jacobi heat-kernel total positivity則在 spatial angle，Riemann需要
log-time/scale translation與 completion後 cone kernel。K0B38 的 exact格點式含
兩個換號因子，不是 local positive stress。故 theta-PDE路只剩完整格點和的
nonlocal Green/Rellich cancellation；普通 heat semigroup TP、逐 mode squares、
或 cyclic determinant皆不足。

## G52. Pick--Bernstein route 已有真升階 theorem，缺口是 complex Mellin ratio

ES62/J68 與先前 fixed-degree moment路本質不同：全部 Xi coefficients由單一序列
`varphi_n=2(2n-1)m_(n-1)/m_n` 編碼；若其 theta-local Mellin插值
`2(2z-1)M(2z-2)/M(2z)` 屬 Bernstein Pick 1-separation class，KPS Theorem 4.4
一次推出 LP/RH。

J5 已無條件證全部一階差分 `Delta varphi_n>0`。目前斷層是：

1. 證全部 complete-alternating finite differences，而不是再列有限批次；
2. 證 upper-half-plane imaginary part非負的 Herglotz representation；
3. 證 Mellin continuation的 zeros/poles皆在正確實軸位置並相隔一單位。

正實軸 moment log-convexity只給第一層；Gaussian-mixture反例表明 score單調不會
自動給 Pick。KPS paper自身的 Riemann equations有 sign/factor錯誤，不能把其
「possibility」段誤讀成已證 Xi屬 `D_P`。這條路保留，因它首次提供具體
uniform-in-degree升階 theorem與可由 theta Mellin資料直接攻擊的非循環 target。

J69/ES63 已關閉一個子缺口：KPS moments確有由 Abel反演顯式構造的正、
moment-determinate law `I`，且 normalized Xi law是 arcsine scale mixture。尚未閉合：

1. 證 `I` 是 subordinator exponential functional，即
   `sE[I^(s-1)]/E[I^s]` 為 Bernstein；
2. 進一步證該 exponent complete/Pick；
3. 證其 meromorphic zeros/poles實、simple且滿足 KPS ordering。

Hirsch--Yor 只給 forward theorem。`g_I>=0`、moment determinacy、甚至
`log I` infinitely divisible都不單獨推出 1--3。故不得把 Abel positivity誤報為
KPS membership；下一個 uniform target是 L12.1，加上一個足以反推 complete
Bernstein exponent的 converse。

J70 提供更小的解析缺口：先證 `4(log M)''(2s)` 有正 inverse-Laplace measure A，
再證 Fermi--Bose sandwich (J70.3)。這一次同時控制所有 derivatives／degrees，
而非有限差分。尚未有 theta-specific representation給 A；一般 log-concavity或
score monotonicity不推出它（K0B36.5仍是反例警告）。sandwich完成後仍需證
harmonic-potential admissibility與 KPS separation，故不能提前宣告閉合。

J71 的逐點式原先還隱含一個量詞跳躍：J70只給 inverse-Laplace measure的支配；
要得到 density及逐點 exponential sum，須另證 absolute continuity、global
Mittag--Leffler growth與 termwise inversion。Selberg nudge 正確指出這才是形式斷層。

J72 現已用可重跑的 Arb/Rouché certificate證出
`rho=-16.988364513985...+5.875534137135...i` 附近的真 Mellin zero，並排除
`M(rho-2)=0`。故 natural `varphi_nat` 在 upper half-plane有 pole，L12 natural
interpolant路線關閉；先前 J70/J71 不再是 live proof target。這也解釋為何不能從
J69 的 positive mixing law推到 complete Bernstein/Pick。

J73 已進一步排除「不同 KPS interpolant」：`1/W_varphi` 與 natural coefficient
interpolant在正整數相同，兩者由 Patie--Savov/J69 bounds同屬 Carlson class，故必全域
相等；J72 的 nonreal zero與 KPS全負實零點矛盾。因此 G52/L12整條 KPS路線關閉，
不能由替代插值或 finite-difference batches重開。主線回到 K0全格點 nonlocal
CP/Green identity、Suzuki causal factorization，或真正的 all-degree determinant/
升階 theorem。

## G53. 全格點 automorphic lift只把缺口移到 point trace -> Haar square

K0B39 證 stress operator含 `(2mn)^2`，故座標軸 modes全被消去；cross theta可 exact
換成完整非零格點 theta。這取得 `SL_2(Z)` automorphy及 Epstein/Eisenstein Mellin
展開。K0B40 同時證沿 rectangular geodesic的 Fourier transform正是 `4W_Phi(y,-k)`；
由 Hudson theorem，非 Gaussian的 `Phi` 不可能有全正 Wigner函數。故 raw geodesic
trace／matrix coefficient positive-definite路線嚴格關閉。

剩餘合格缺口是 test-dependent lift：對每個 test `f` 構造 automorphic object，使完整
`Q_K0(f)` exact等於 Haar/Rankin--Selberg norm。一般 Siegel-transform second moment
只平均全部 lattices，不能推出 standard rectangular basepoint的符號。

K0B41 再排除 full-orbit coherent/Rallis捷徑：Haar frame operator在 irreducible
constituent上依 Schur lemma是 scalar identity；`K_0` 卻是非零 Hilbert--Schmidt compact
operator。故 lift必須是含 cone boundary的非等變 truncation，並單獨證 boundary
correction正；以抽象 `K_0^(1/2)` 定義 lift是循環。

## G54. Suzuki 2026 的 real-zero exhaustion缺 shift control與合法 meromorphic limit

K0B42/ES68確認 `W(a,theta;z)` 對每個 finite `a`、每個 `lambda<lambda_a` 無條件
entire且全實零，是真正 all-degree family。可是原 arithmetic limit在推導時先假設 RH
以取 `lambda=0`。任何無條件合法且 `lambda(a)->0` 的選擇，因 `lambda_a` 隨 `a`
non-increasing，已直接推出全部 `lambda_a>=0`／RH。

原文宣稱收斂到 `z^2xi/xi'` 亦不能按字面在 `C` 每個 compact普通一致成立，因 target
meromorphic。修正版必須要求 nowhere-zero holomorphic normalization，並在 denominator
zeros之外作 locally uniform或 spherical convergence。尚缺的是不預設 endpoint
positivity的 global shift law與此 meromorphic compact convergence；finite-a實零性不補此缺口。

ES69 排除一個聲稱繞過此缺口的「weak convergence」論證。finite CCM form真正已知的是
`QW_N-epsilon_N I>=0`；auxiliary self-adjoint spectrum全實不給原 `QW_N>=0`。
任何 square-sum formula都必保留 `epsilon_N||g||^2`，除非先證
`epsilon_N>=0`。compact support只穩定 prime terms，不能刪除此項或取代 determinant
convergence。

## G56. finite Weil dictionary只正化 archimedean tail，完整 source仍無 Gram

ES72 exact給 `g_v(z)=L F_v(z)F_v(-z)`，且完整 finite matrix quadratic等於
所有 zeta zeros的 `g_v` 和；real zeros逐項為 squares。全尺度 PSD因此就是
localized Weil positivity/RH。

新增 strict-TP theorem只處理 `T>rho N` 的 post-band archimedean increment。
archimedean head、signed prime atoms及 pole term沒有共同 Gram；tail norm也不能
uniform支配趨近零的 ground margin。Loewner重寫另有 critical sampling nullspace：
`sin^2(pi z)h(z)` 同時消全部 integer values與 derivatives，所以單 lattice Carlson
不能辨認 arithmetic source。若用所有 boundary phases消除此 nullspace，所需
positivity又回到完整 localized form。合格新輸入只能是 complete source的
prime--gamma Gram/Kraus factorization或非循環 shifted-lattice Pick theorem。
詳見 `finite_weil_dictionary_audit.md`。

W5--W6 又關閉一類假 completion：prime block雖可寫成正 translation-difference
squares 減去 `2S_c||f||^2`，但完整 Weil form不可能是正 Borel shift measure的
difference-square mixture。後者必有 absolutely continuous Fourier multiplier；
Hardy theorem已無條件給 critical-line zeros，其 boundary log-derivative直接含正
Dirac atoms，而 off-line zeros局部只給 smooth Poisson terms，不能消去。故 G56 的共同 Gram必須具有
singular spectrum、非平移不變 boundary channel或 residue compression，不能再以
正 shift-measure majorization 充當候選。

## G57. 全 tail Toeplitz positivity仍不推出 real zeros

`G_A(z)=cosh(sqrt z)+A` (`A>1`) 是 order `1/2`、全正係數 entire function，且
`[+-arcosh(A)+(2m+1)pi i]^2` 給明確非實零點。可是它只改動 PF-infinity 函數
`cosh(sqrt z)` 的常數項；對 `k>=r`，Toeplitz block全部 indices至少為 1，故
`D_(r,k;G_A)=D_(r,k;cosh sqrt z)>0`。所以即使 ES70 wedge被加強到整個 tail cone
`k>=r` 仍不能推出 RH。所缺不是更好的 tail constant，而是 Xi-specific 的
head-to-tail reverse transport，或 uniform growing `k<r` reciprocal-pole theorem。

## G58. Phi even-derivative Andreief 是全階 transport，但 integrand 在 rank 3 變號

正 geometric normalization後，分部積分的全階版本為
`c_(k+j-i)=int u^(2k+2j)Phi^(2i)(u)du/(2k+2j)!`，即使 index負也由偶性 boundary
jet exact給 0。Andreief遂把任意 consecutive Toeplitz determinant寫成
`det[Phi^(2i)(u_l)]` 乘正 Vandermonde的積分。這是真正保留 head boundary 的
uniform identity。

但 pointwise Gram在 `r=3`, `u=(.05,.10,.16)` 有 rigorous interval
`[-17.22362622207346,-17.22362610808933]`，嚴格為負。故不能用 derivative-kernel
TP直接完成；若保留此線，必須找到積分層級的 involution/symmetrization，使 signed
區域成 squares，而非逐點取正。

## G59. 標準 theta 對合不修復 G58

log-theta 模組對合是 `u->-u`。`Phi^(2i)(u)`、偶次 monomial、`u^2`
Vandermonde與測度全都不變；座標置換則同時翻轉兩個 determinants，乘積仍不變。
所以 signed-permutation orbit內 integrand恆同號，G58 的負 patch只會配到同號副本。
若要保留 T7，必須另造會混合 derivative order或 theta summation indices的全局
identity，並 exact證 Jacobian及 Vandermonde weight匹配；普通 modular reflection已關閉。

## G60. backward heat Pick positivity不能跨碰撞反傳

Schatz 2026 的核心 collision bridge被 `E_t=z^2+1-2t` 精確否證：上方時間零點
全實且 `Im(-E'/E)>0`，跨過 `t*=1/2` 後零點成非實對且該量在上半平面有負區。
論文把 WPT錯用為 individual analytic root branches，並把依賴 zero-speed bound的
能量常數當成碰撞前整段的有限常數；實際速度按 `|t-t*|^-1/2` 發散。故 backward
Carleman/Kato沒有提供 RH方向。詳見 `external_claim_audit_schatz.md`、ES75。

## G61. derivative-to-Vandermonde transfer亦只移動符號缺口

T7 可再次 exact分部積分，把 `det[Phi^(2i)]` 的全部 derivatives移到正
Vandermonde；零端 boundary terms由 Phi與 polynomial的偶性逐項消失。可是所得
`A_r V_(r,k)` 仍變號：`r=2,k=1,(u_1,u_2)=(1,4)` 時 exact為 `-130`。
因此 Capelli／random-matrix derivative principle沒有給 pointwise Gram。剩餘命題是
特殊 iid measure `prod Phi(u_l)du_l` 對整族 signed symmetric polynomials的
uniform integral positivity，未比 balanced Toeplitz cone更容易。

## G62. Pólya-ensemble／random-matrix包裝不繞過 G58

外部分類 ES76 顯示，令 `x=u^2,nu=-1/2,omega(x)=x^-1/2 Phi(sqrt x)`，則
`D_(-1/2)=u^-1 d_u^2u/4`；連同 `dx=2u du`，其 size-r joint density就是
T7 determinant乘 `u^2` Vandermonde。故 G58 rank-3負 patch同時嚴格否證此 weight的 size-3 Pólya
ensemble。既有 convolution/transform closure以前提 density非負，不能套在此 signed
weight上。random-matrix命名沒有新增升階機制。

## G63. 尚存的全局候選：只證 determinant pushforward正

令 signed T7 density `sigma_r=det[Phi^(2i)(u_l)]Delta(u^2)du`，再由
`tau=prod u_l^2` pushforward成一維 `nu_r`。則 exact有
`r! prod_j[2(k+j)]!D_(r,k)=int t^k dnu_r(t)`。因此若能 uniform證每個
`nu_r>=0`，便一次處理所有 rank與shift；不需 joint density逐點正。

這條路未被 G58排除，也不由 ES76自動給出：derivative-principle theorem假設原
matrix density已正，而此處 size 3已 signed。所缺是 product level sets上的 theta
sum-of-squares／Mellin convolution公式。浮點篩選 `r<=8,k<=29` 的 normalized moments
及 size<=6 Hankel matrices未見負值，但這不是證明，也不確認 pushforward measure正。

## G64. T11 的 pointwise pushforward 正性有穩定 rank-7/8 負訊號

令 `u_l=e^(y_l), S=sum y_l`，並設
`f_(i,j)(y)=e^((2j+1)y)Phi^(2i)(e^y)`。兩個 determinant展開後 exact得到
`g_r(S)=r!det_*[f_(i,j)](S)`，且 `dnu_r/dt=g_r(log(t)/2)/(2t)`。
這直接測試 G63所需的 pointwise sign，而不是再測 moments。

三個截斷窗、1024--4096點的 double FFT一致給
`g_7(-7.65)約-4.2454e21`、`g_8(-6.90)約-7.7170e33`；獨立 60-digit FFT與
自寫高精度 determinant在 256點亦給負值並向上述數值收斂。故 G63不再列為 live
positivity候選。尚缺的是 truncation/discretization的嚴格 enclosure，才能把負值升為
正式反例；在此以前不得稱已證否。但繼續刷 normalized moments或 Hankel batches無法
處理此缺口，因 signed density可有許多正 moments。

## G65. G63/T11 已由 rank-7 漸近係數嚴格關閉

T12 的 bilateral Laplace matrix為
`F_(i,j)(s)=int u^(2j-s)Phi^(2i)(u)du`。其最先極點 `s=1` 只在第 0欄。
令 `A_m=Phi^(2m)(0),mu_p=int u^pPhi(u)du`，並定義

`B_(i,0)=A_i`；對 `j>=1`，若 `i>=j` 則
`B_(i,j)=(2j-1)!A_(i-j)`，若 `i<j` 則
`B_(i,j)=(2j-1)!mu_(2(j-i)-1)/(2(j-i)-1)!`。

把 convolution determinant按 permutations展開，每項恰有一個 column-0 factor。
對 `f_(i,0)*h` 將 integrand寫成
`[e^(-(S-x))f_(i,0)(S-x)][e^(-x)h(x)]`；第一因子有界並趨 `A_i`，第二因子
absolute integrable。dominated convergence exact給
`lim_(S->-infinity)e^(-S)g_r(S)=r!det(B)`，不需任何 contour餘項常數。
192-bit Arb、10000個 exact rational midpoint cells與嚴格二階餘項得到

`-3.156096567895524060757e21 <= det B_(r=7)`

`<= -2.883510345549506883157e21 <0`。

theta尾、`u>=2`尾及原點 derivatives尾均有解析上界並由同一程式 assertion。
故 `g_7(S)` 在充分負的整段為負，`nu_7` 不是正測度；G63/T11 已正式否證。
這只關閉 auxiliary pushforward positivity，不產生負 Toeplitz minor，也不否證 RH。
後續不得再嘗試修補 T11 或刷其 moments。

## G66. Lee--Yang orthogonal-Wronskian重寫沒有產生 base或 closure

ES78 將 `Fourier(Phi)`全實零等價成所有 orthogonal-polynomial Wronskians
`W(p_2,...,p_n;ix)<0`。Leclerc identity顯示這些就是 Appell/Jensen Turán hierarchy；
雙積分 kernel含隨 `n,t,s,x` 旋轉的 complex phase，正 measure、log-concavity或已證
degree 3都不固定其 sign。因此不能逐 n刷 Wronskians，也不能把 Karlin--Szego在 real
axis的 sign直接旋到 imaginary axis。

此路唯一非循環輸出仍是 A22 的整體 construction：顯式 `mu_N` 各自屬已知
ferromagnetic Lee--Yang class，且 tight weak convergence到 `Phi(t)dt/int Phi`。
目前外部文獻沒有給這個 coupling/scaling limit；故只保留接口，不列為已推進證法。

## G67. prime Bohr奇異測度給 exact source；local ground-state shortcut已關閉

臨界 Euler factors的 normalized Hardy product
`F_P=prod sqrt(1-p^-1)/(1-p^-1/2 z_p)` 有 norm 1卻 weak趨 0；普通 common energy
確實失去全部 boundary norm。但 squared densities weak-*趨向 infinite Riesz product
`mu_pr=otimes_p P_(p^-1/2)dm_p`，且由 Kakutani criterion與 `sum 1/p=infinity` 知其
對 Haar為 singular。這符合 G56要求的 singular boundary channel。

更重要的是 exact identity
`|D_theta|log P_a=P_a-1`；沿 `theta_p=t log p` 後即為全部
`2sum_(p,k)(log p)p^(-k/2)cos(kt log p)` prime-power source。令
`h=sqrt(P_a)`，fractional chain rule又給
`P_a-1=2(|D|h)/h+C_a`，其中 `C_a>=0` 且 `C_a=a^2+O(a^3)`。但精確 form bookkeeping
顯示原先「只剩 Bregman debt」漏了一項：把 potential改寫成 ground-state square時，
每個 prime還產生 `-2<H,|D|H>` kinetic debt；Weil form本身沒有這個 kinetic項，pole
有限秩與 Archimedean multiplier也不自動補它。

Gamma端可嚴格截斷：若 `b_n=2n+1/2`、`q_N=prod_(n<=N)(b_n^2+t^2)`，則 digamma series
給 `c_N+|D|log q_N -> Re psi(1/4+it/2)-log pi`。和 finite-prime density合起來確為
`c_N+|D|log(q_N/P_P)`，但對其再做 chain rule仍引入同一 absent kinetic form，且 divergent
constants須由 global principal-value normalization耦合。

更根本地，右半平面 zero的 Blaschke factor在邊界 modulus恆為 1，卻對 normal derivative
貢獻 `-2delta/[delta^2+(t-gamma)^2]`。把 actual analytic extension換成 boundary outer
extension會恰好丟掉 off-critical zeros，也就是偷渡 RH。故 local Riesz＋fractional
ground-state版本已關閉；仍存活的只可能是同時供應 kinetic storage、global Poisson
normalization與 Blaschke控制的 adelic compression/trace identity。詳見
`prime_bohr_singular_route.md`。

## G68. semilocal Sonin穩定不是 uniform common norm；只剩 support-by-support projection

CCM 2310.18423/2403.01247 把 G67 接到真正 semilocal Hilbert space。finite `S` 的
cyclic spectral measure為 `|E_S(t)|^2dt`，而每個 finite prime factor
`|L_p|^2=P_(p^-1/2)/(1-p^-1)`，所以 B2 Riesz density正是其 normalized prime部分。
同時 `theta_S` 把 Archimedean Sonin space同構到 semilocal Sonin space。

但 dual-coordinate norm ratio是
`m_S(t)=prod_p|1-p^-1/2 exp(-itlogp)|^2`。由 prime logs的有理獨立與 Kronecker，
ambient condition number exact為
`prod_p(1+p^-1/2)/(1-p^-1/2)`，並因 `sum p^-1/2=infinity` 發散；scalar renormalization
不能改善。故 finite-S stability沒有提供 all-prime common Hilbert limit，也不能把
Archimedean正性以 bounded similarity傳到 finite-prime Weil form。

CC 2006.13771 已在 prime-free support `(1/2,2)` 證
`W_infinity(g*g*)>=Tr(vartheta(g)S vartheta(g)^*)>=0`。真正 live target是對每個 q，
在 `S_q={infinity}union{p<q}` 與 support `(q^-1,q)` 證相同 semilocal projection
inequality；這是 all-test、support-by-support命題，若全部成立即給 RH。現有文獻只構造
space/measure/operator並把比較列為 strategy，未證 inequality。詳見
`prime_bohr_singular_route.md` B8--B9。

## G69. p-adic time-delay雖正，Weil local term是 wrong-sign supertrace

Burnol math/9901051 對 unramified `Q_p` exact給非負 time-delay
`T_p=(logp)P_(p^-1/2)(tlogp)`，但 local Weil conductor是
`H_p=(logp)I-T_p=-(logp)(P-1)`。所以 G67的 prime source就是「scalar baseline減
positive time delay」，不是 positive local Hamiltonian。其 trace formula必須把 Tate vector
設為一維 odd sector後取 supertrace。

因此 direct sum/tensor local positive scattering operators不能給 Weil positivity：只要 odd sector
仍存在，positive operator的 supertrace便無固定正號。B9.2 真正要求 global Poisson/rational-lattice
complex先把 local odd directions配對或 quotient，再讓 cohomological ordinary trace等於全部 local
supertraces。現有 local theorem沒有證此 global quotient正；詳見 B10。

## G70. 2026 arithmetic Jacobian給 global monoid，未給 intersection/Hodge positivity

Connes--Consani 2602.15941 將 Riemann adele sector辨認成 rooted/metrized rank-1 divisor
的 Picard monoid，adelic product成 tensor product，explicit formula成 periodic-orbit
Lefschetz trace。這提供 G69 local odd sectors可被 global耦合的幾何載體。

但原始 TeX沒有定義 degree-zero bilinear intersection form，也沒有 Hodge-index或 positive
trace theorem；semilocal部分仍是帶 divergent generic-orbit與 signed local remainders的既有
cutoff trace formula。故幾何名稱不補正號。可驗收新定理必須在 relative pair
`(Picard monoid,generic orbit)` 上構造 pairing、證其 trace exact等於 Weil form，再由不使用
zeros的 Hodge sign推出非負。此命題目前完全未閉合，詳見 B11。

## G71. Semilocal duality的uniformity正好消去所有prime資料（已關閉）

有限 \(S\) 時 \(\theta_S^*\eta_S=I\)，且兩映射 intertwine scaling，故
\[
\langle\theta_S f,V_S(h)\eta_Sg\rangle
=\langle f,V_\infty(h)g\rangle.
\]
這雖 uniform-in-\(S\)，但 local Euler multipliers 完全相消，結果不含 prime
Weil term。保留 primes 的 same-side form 則帶 \(m_S\) 或 \(m_S^{-1}\)，其
condition number \(\kappa(\theta_S)\to\infty\)。所以以 primal--dual pairing
繞過 \(\kappa\) 的路線不可行；uniformity 同時抹除了算術內容。詳見 B12。

## G72. Local all-degree defect已找到，但其prime trace不可求和（OPEN）

Hardy--Toeplitz factorization 給出精確全階公式
\[
T_{1/P_p}-T_{P_p}^{-1}=\frac1{p-1}P_{[0,\log p]}\ge0.
\]
這是 degree 3 所沒有的 all-size operator structure；然而其自然 trace 質量
\(\log p/(p-1)\) 對 primes 發散。Gamma 與 prime model-space time delays 又
以相同負號進入截斷 Weil source，不能逐局部抵消。尚缺把 baseline、pole
evaluations、gamma 與所有 primes 同時納入的 renormalized contraction 或
determinant theorem；不得再用有限 degree VERIFIED 批次代替。詳見 B13--B14。

## G73. Quasi-inner是all-S代數結構，不是正性升階（OPEN）

對任意 finite \(F\)，外部 theorem 證 \(C_F=(1-P)U_FP\) compact，並給
Sonin injections \(D(F,F'):S(u_F)\hookrightarrow S(u_{F'})\)。這是具體
all-finite-\(S\) 結構。但對 \(Q_F=U_F^*PU_F\)，投影差 \(Q_F-P\) 的
兩個 diagonal blocks為 \(-C_F^*C_F\) 與 \(B_F^*B_F\)。要求整個
\(Q_F-P\ge0\) 等價於 \(C_F=0\)，即把 quasi-inner 偷換成真正 inner。

可驗收缺口因此是：在 pole-neutral、support-limited convolution-square cone
上，證 positive defect 的 weighted trace 支配 negative compact defect。現有
kernel injection不是等距，norm distortion正重現 \(\kappa(\theta_S)\)。詳見 B15。

## G74. Fixed-order determinant與免費adelic causality均不可用（OPEN）

若 \(m=|F|\)，quasi-inner theorem只保證
\(\mu_n(C_F)=O(n^{-1/(2m)})\)，故保證的 Schatten exponent需 \(q>2m\)；
沒有 fixed \(q\) 通過 all-\(S\)。標準 regularized determinant還帶無正號的
mixed-trace anomaly。另一方面 Burnol 的 adelic theorem 已證
\(\mathcal D_+\perp\mathcal D_-\) 等價於相應 abelian RH；co-Poisson
functional equation本身不給 orthogonality。故 global Poisson/causality若不另證
support-by-support contraction，只是 RH 等價換名。詳見 B16--B17。

## G75. Prime defect可canonical renormalize，但留下負 staircase（OPEN）

令 \(A(q)=\sum_{p\le q}(p-1)^{-1}\)。B13 的 commuting interval defects滿足
\[
\left(\sum_{p\le q}\frac{P_{[0,\log p]}}{p-1}-A(q)I\right)f
=-\left(\sum_{p<e^x}\frac1{p-1}\right)f(x)
\]
對每個 compactly supported \(f\) 在 sufficiently large \(q\) 後 exact成立。
所以 divergent trace有 canonical scalar counterterm與 all-prime core limit；但
limit是負 multiplication potential，漸近 \(-\log x-C_p\)，不給 Weil
positivity。新缺口是 gamma/pole residual對此 staircase的 support-constrained
domination。詳見 B18。

## G76. Fixed gamma/pole storage不能支配renormalized prime staircase（已關閉）

取 \(\phi=(\partial_x^2-1/4)\psi\), \(0\ne\psi\in C_c^\infty(0,1)\)。則
\(\int e^{\pm x/2}\phi=0\)。平移 \(\phi_R(x)=\phi(x-R)\) 仍滿足兩個 pole
constraints；任何 fixed gamma Fourier-multiplier energy保持不變。但 G75的
prime potential energy至少為 \(A(e^R-)\|\phi\|^2\to\infty\)。故固定
Archimedean form加 pole evaluations不可能 uniform支配 prime staircase。

這不否證 Weil positivity，因 B13 defect不是完整 prime term；它否證的是 places
彼此分離後再靠 scalar renormalization拼合的策略。必須加入隨 \(F\) 變動的
semilocal Poisson/Sonin cross-place storage。詳見 B19。

## G77. Quasi-inner defect的polar cancellation是全階block結構（已修正）

令 \(D_F=V_F|D_F|\) 為 lower-right Hardy block的 polar decomposition，
\(K_F=\ker D_F=S(u_F)\)。unitarity exact給
\[
B_F^*B_F=P_{K_F}+E_F,\qquad
C_FC_F^*=P_{\ker D_F^*}+V_FE_FV_F^*.
\]
所以 positive/negative compact remainders由 \(V_F\) 精確配對；正側多出的正是
semilocal Sonin projection，負側只多 finite cokernel。但這只是 unweighted block
identity。actual scaling weight不與 Hardy projection交換，cross blocks不能省略；先前
把缺口寫成單一 polar commutator過強，現已撤回。詳見 B20。

## G78. 完整義務是signed Hankel-energy trace monotonicity（OPEN）

令 \(R_F=U_F^*PU_F-P\)，\(F=M_f\)，並定義
\[
\mathcal J(f)=\|PM_f(1-P)\|_2^2-\|(1-P)M_fP\|_2^2.
\]
exact block calculation（保留全部 weight cross terms）給
\[
\operatorname{Tr}(F^*R_FF)=\mathcal J(u_Ff)-\mathcal J(f).
\]
在 Connes--Consani local-sum convention，所需 sign是右側 \(\le0\)，且只要求
pole-neutral、support-limited test cone；不能升格成 \(R_F\le0\)，後者等價於
\(u_F^*\) inner，已知過強。elementary Blaschke rank-one例亦顯示 quasi-inner class
加兩個 constraints不自動給此 trace sign。真正缺口是 actual arithmetic \(u_F\)
的 Poisson-specific Hardy-energy monotonicity。詳見 B21。

## G79. Semilocal缺口等於restricted mean time-delay，不是operator causality（OPEN）

若 \(f=\mathcal Fh\)，則
\[
\mathcal J(f)=(2\pi)^{-1}\int x|h(x)|^2dx.
\]
所以 G78 exact等於：對指定 support與兩個 exponential-moment constraints，
semilocal scattering \(S_F=\mathcal F^{-1}M_{u_F}\mathcal F\) 滿足
\[
\int x|S_Fh(x)|^2dx\le\int x|h(x)|^2dx
\]
（Connes--Consani local-sum convention）。這是平均 delay的 trace inequality；不得
升成 operator order或完整 causal support。後者由 Burnol已知等價 RH。可行新輸入必須
直接控制 q-rough co-Poisson sum的 first moment。詳見 B22。

## G80. pole-neutral cone已有exact投影，但compressed sign仍未證（OPEN）

Burnol 的 vanishing-condition Paley--Wiener 理論在 `z=+-i/2` 可直接化成
B23：support `[-x,x]` 上排除的兩向量是 `exp(+-y/2)`，Gram matrix 為
`[[2sinh x,2x],[2x,2sinh x]]`。constraint geometry與隨 support變化的
Krein system都已顯式；缺口是證 `P_x^0 T_F P_x^0>=0`。可驗收的 uniform
候選是此 compression 的 inertia/Schur-complement theorem；有限 eigenvalue
批次仍不合格。

## G81. endpoint主密度被pole條件精確消去；剩下prime discrepancy（OPEN）

B24 證 finite-prime phase平均 exact為
`-2 Re sum_(n<q) Lambda(n)n^-1/2 C_h(log n)`。兩個 pole moments又給
`Re int (exp(lambda/2)+exp(-lambda/2))C_h(lambda)dlambda=0`，故 prime sum
可無誤差改寫成對 `dpsi(t)-dt-dt/t` 的配對。Rodgers weighted-Hilbert反例
封閉 universal spacing-only臨界吸收；但真正剩餘的是此 signed discrepancy
加 archimedean項在全部 B23 test cone上的 sign。PNT error取絕對值太粗，不能
當作證明。

## G82. all-size Schur-complement target已精確化，但一般理論不能免費給index（OPEN）

B25 令 A_(F,x) 為 unrestricted phase Toeplitz form、L_x=(E_+,E_-)。
可逆時 constrained inertia exact為
nu_-(A)=nu_-(A|ker L)+nu_-(L A^-1 L*)。所以合格 uniform theorem是
同時證 nu_-(A)=2 與 2-by-2 Weyl matrix L A^-1 L*<0。外部
generalized-Nevanlinna／truncated-Toeplitz文獻只在先有 Schur或
finite-negative-square性時給此結構；把 Xi endpoint直接宣告屬該類即循環。
B25.4--B25.5另核對 B24 centered prime measure加 gamma正好重建
-xi'/xi，zero information沒有消失。

## G83. Suzuki localized Weil form與B25 phase form只在constraint cone相同

B26 exact計算 pole term為 2 Re(E_+ conjugate(E_-))，所以 Suzuki 的 Q_W^x
等於 B25 ambient phase form加一個 indefinite rank-two form；在 ker(E_+,E_-)
上才相同。Suzuki已證 Q_W^x 的 self-adjointness、lower boundedness與 bottom
continuity，但也證 RH假等價某個 support的 bottom變負。故不能由這些 operator
facts推出 B25 index/sign；仍需新的 arithmetic inequality。

## G84. ambient phase有exact Dirichlet分解，但只控制基態（OPEN）

B27 無條件證明 pole-removed phase form
`A_x=E_x-kappa_x I`，其中 `E_x` 是 archimedean continuous jumps加全部
`n<exp(2x)` prime jumps的 irreducible Dirichlet form。因此其 semigroup
positivity-improving、最低 eigenfunction唯一且嚴格正。這是真 all-support 結構，
不是 finite certificate；但 exact target變成
`nu_-(A_x)=#{mu_j(E_x)<kappa_x}`。B25需要逐 support 證門檻恰落在第二、第三
eigenvalue之間，ground-state positivity完全沒有給這個 counting bound。

## G85. 兩個moment只給two-sign-change；尚缺uniform oscillation/resolvent theorem（OPEN）

B29 證 `E_+=E_-=0` 的非零實函數至少有兩次 sign changes，這是
`{exp(-y/2),exp(y/2)}` Chebyshev system的精確內容。要推出 constrained positivity，
仍需證 `E_x` 在 threshold `kappa_x` 下的全部 spectral subspace具有相應
oscillation/Chebyshev性，並證 B25 的 2-by-2 Weyl matrix負定。一般 Dirichlet理論只
給第一 eigenfunction；arch-only模型更有 `nu_-(E_arch-kappa_infinity I)->infinity`，
所以不能靠 positivity-improving 加 codimension two 關缺口。

## G86. natural jump heat kernel的PF-infinity路徑被解析排除

B30 對 full-line jump semigroup套 Schoenberg classification。arch jump density
`k(u)=sum_(m>=0)exp(-(2m+1/2)u)` 使 reciprocal bilateral-Laplace transform的
log在 `s=+-(2m+1/2)` 有 poles，exponential遂有 essential singularities；finite
prime atoms只乘 entire nowhere-zero factor，不能消去。因此 natural convolution
semigroup不可能 PF-infinity，不能提供 all-minor variation-diminishing升階。
尚未排除 Xi-specific、非 translation-invariant 的 sign-regular kernel，但它必須是
新的 arithmetic theorem，不能由 Markov/Dirichlet性自動取得。

## G87. BFI theta Green模板的 bulk/cusp correction未定號（OPEN）

BFI 的 current equation exact給
`int f varphi_0=(1/2)e(m tau)int_c f-(1/(4pi))int(Delta f)eta`；這是目前
一個形式上吻合 K0B39 所需的非等變 Green/Rellich 模板；K0B46/G90說明它尚非
K0 kernel的 exact介面。即使在 BFI setting內，一般 `Delta f` 仍可變號。
對 split geodesic，截斷邊界另含 cusp constant terms與 negative Fourier
coefficients；在 eigenvalue `0` 的 regularization又出現依 spectral deformation
而變的 `B'_ell(1)`。故現有 theorem不給逐 test正性。缺的是 canonical
`h -> F_h`，使 K0 form等於 bulk、period及所有 cusp項的完整總和，並把該總和
寫成 nonnegative norm；相對跡平均或 period square不能取代此等式。

## G88. 緊支撐 superharmonic 定號捷徑不可能非平凡

若企圖以 `-Delta F_h>=0` 直接定 K0B43 bulk 項，又要求 `F_h` 緊支撐且邊界 flux
消失，則 `int Delta F_h=0` 迫使 `Delta F_h=0`，最大值原理再給 `F_h=0`。
因此所有非平凡候選必須保留並精確利用 cusp flux／source singularity，或允許
signed Laplacian並證 global pairing；不能同時把 boundary丟掉且靠 pointwise
superharmonicity完成正性。

## G89. level-1 harmonic cohomology沒有可用的Hodge正空間

Kudla--Millson form雖是 geodesic cycle的 canonical Thom form，但 `X(1)` genus
zero，故 `S_2(SL_2(Z))=H^1_(2)=0`。closed geodesic current只能是 exact
transgression；split geodesic則必須攜帶 cusp boundary資料。故不能把 K0 stress
投到非零 harmonic cohomology，再由 Hodge norm推出 positivity。若使用
Shintani/Kudla--Millson norm，還必須證其 adjoint pullback **exact等於** `Q_K0(h)`；
只得到 cycle-period squares會改變問題。

## G90. BFI/KM 與K0 theta之間尚缺representation bridge（OPEN，優先於G87定號）

K0B39 用 standard `R^2` lattice的 Epstein theta；BFI/KM 用 trace-zero matrices的
三維 adjoint／`Sym^2` theta。`Hom_SL2(Std,Sym^2 Std)=0`，故無 equivariant linear
識別。Veronese `(m,n)->[m^2,2mn,n^2]` 雖自然，卻只落 discriminant-zero cone且將
BFI quadratic majorant拉成 quartic，不是 K0 Gaussian exponent。K0 rectangular
geodesic也只是 basepoint orbit，不是 BFI index cycle。故 G87 的 Green-current
公式目前僅是 architecture；先須構造施 stress與cone cutoff後仍 exact的
intertwiner/transmutation，或為 Epstein theta直接建立 current identity。

## G91. direct Epstein Green route等同continuous scattering endpoint（OPEN）

K0B47證 K0 `Theta_*` 是 incomplete Eisenstein series，與全部 cusp forms正交；其
Mellin channel是 `zeta(2w)E(z,w)`，scattering coefficient為
`zeta^*(2w-1)/zeta^*(2w)`。故直接 Green/resolvent法不會產生新的 discrete Hodge
square，只會回到 scattering phase與 cusp residues。Maass--Selberg truncated norm
雖非負，但含發散的 `log T` baseline；扣除後 finite part無一般符號。缺口等同在
pole-neutral cone上證 renormalized time delay加全部 boundary Hankel terms非負，
亦即 B21--B23/Suzuki endpoint的同一問題。

## G92. 所需只是cumulative defect的面積，不是逐截斷causality（OPEN）

B31 exact證若 `D_h(R)=||P_RSh||^2-||P_Rh||^2`，則 desired mean-delay sign等價
`int_R D_h(R)dR>=0`。所以不必證每個 `R` 的 defect非負，更不必證
`S^*P_RS-P_R>=0`；後兩者是過強的 causality/stochastic dominance。這留下較弱的
uniform機制：在 pole-neutral cone上把 **積分後** 的 flux（含 Maass--Selberg
finite part與 boundary corrections）exact配平方，即使 `D_h(R)` 本身變號。

## G93. 已補上area均值到逐零點的全稱量詞；剩下的是證area sign（OPEN）

B32說明需要且足夠的命題是：對每個 `x>0` 與每個
`h in C_c^infinity(-x,x) cap ker(E_+,E_-)`，B31 cumulative defect面積非負。
support使所有未納入的 prime powers exact零配對，所以這是完整 Weil form，不是
finite-prime近似。若有 off-line zero，W14 的 two-point indefinite orbit可由
polynomial-Gaussian隔離；再以 smooth cutoff及兩個 fixed bumps精確恢復 compact
support與 pole moments；Gaussian tail使近似在 Weil distribution所需的 exponential
test topology收斂，負值仍保留。故此 all-support area statement逐一排除
off-line zeros並等價 RH。尚缺的不是 mean-to-zero bridge，而是從 prime/gamma side
無條件證 B32.2。

## G94. canonical-system Szego sum rule在Schur前提處循環

B33核對 Arov-gauge sum rule：其非負係數 integral確是 uniform square，但 theorem
預設 spectral function在上半平面 holomorphic Schur，並由此得到 positive
Hamiltonian。對 `zeta^*(2s-1)/zeta^*(2s)`，排除 poles並把 shifted quotient延伸到
endpoint已是 Suzuki/de Branges 的 RH-facing缺口；physical-line純相位又令標準
entropy `log(1/(1-|w|^2))` 發散。任意加入 transmission channel不唯一，且其 entropy
不是 B31 phase-delay area。故除非先從 arithmetic構造一個 canonical transmission
system並證其 coefficient energy exact等於 B32.1，Szego sum rule不能提供 sign。

## G95. archimedean compact-remainder法不能把質數當compact error（OPEN的新principal problem）

B34給出 exact obstruction。在支撐區間 `I=(-x,x)` 上，每個活躍
prime-power `a=log n<2x` 給壓縮平移 `P_I(T_a+T_-a)P_I`。將 `I`
依 modulo `a` 分解後，每條 fibre是 finite-path adjacency matrix，其非零
eigenvalues因 base fibre無限維而有 infinite multiplicity；因此是 essential spectrum。
在左端小區間取無限 orthonormal sequence還可同時滿足 `E_+=E_-=0`，
故 codimension two乃至任意 finite-codimension restriction都不使其 compact。

Connes--Consani 無質數證明的 `-2I+K` (`K` Hilbert--Schmidt) 因而無法
以「把 Euler terms加入 `K`」升到 semilocal。先套
`Q=-d^2/du^2+1/4` 更會產生 shifted derivative energies，並非 `L2` 上的
bounded compact perturbation。下一個合格 theorem必須把全部 active shifts納入
新的 **noncompact principal semilocal operator**，並對每個 support證其 pole-neutral
compression定號。目前尚無此 uniform operator inequality；這是 B32.2 的
最窄 arithmetic-side缺口。

## G96. Suzuki arithmetic screw-line Gram identity是all-support square，但coisometry尚未證（OPEN）

B35核對 arXiv:2301.00421/2606.09096。`mathfrak S_t in L2(R)` 有完全無需
零點的 `zeta'/zeta + finite prime sum + gamma + Lerch tail` 公式。若能無條件證
`pi^-1<S_t,S_u>=g(t-u)-g(t)-g(-u)+g(0)`，就會將全部 Weil kernel
寫成一個明確 `L2` Gram，並一次推出所有 support的 B32.2/RH。這是
目前最貼近 integrated-flux square的 uniform mechanism。

斷層也已精確：零點展開的 feature vectors `F_gamma` 在 `L2` 產生 PSD
Gram matrix；Weil spectral pairing在非實 conjugate orbit上則需
`[[0,1],[1,0]]` indefinite block。只在 RH 下 `Theta=(A-iA')/(A+iA')`
是 inner/Hermite--Biehler，`F_gamma` 才是 orthonormal model kernels。所以不可以
Plancherel、model-space Parseval或「boundary modulus one => Schur」代替證明。合格的新輸入
必須直接從 prime--gamma 公式證 `h -> pi^-1/2 P_(Dh)` 對 screw form
是 arithmetic coisometry，並完整處理非實 poles的 residue defect。

## G97. screw-line residue defect的Pontryagin負指數即off-line zero數（OPEN：缺index-zero算術定理）

B36套用 indefinite Hermite--Biehler/Krein--Langer theory。對
`A(z)=xi(1/2-iz)` 取 `q=-A'/A`，其 generalized Nevanlinna kernel與
`E=A+iA'` 的 de Branges kernel只差 `A(z)overline(A(w))` 因子。若 off-line
zeros有限，negative-square index正是上半平面 nonreal poles的總重數；若無限，
finite restrictions的負指數無界。所以 B35 contour/Gram 差異中不可丟的
residues有一個 exact all-degree invariant，不是小 compact error。

但現有 general theorem只「計數」負方向，不證其為零。直接證 `q` Nevanlinna、
`Theta` Schur或 `E` Hermite--Biehler均已是 RH-equivalent。新的合格輸入必須
使用 prime--gamma/Poisson 資料證 Pontryagin index為零，不能用無極點的
Hilbert contour formula先行假設。

## G98. finite-index時的最小缺口是Krein--Langer Blaschke denominator `B=1`

B37將 generalized inner ratio寫成 `Theta=Theta_0/B`，其中 `Theta_0` inner，
`B` 為 degree `kappa` 的 finite Blaschke product。核有 exact分解
`K_Theta=(K_(Theta_0)-K_B)/(B overline B)`；因此全部 off-line residue debt
就是 rank-`kappa` 的負 kernel `K_B`。無限指數時，有限 restrictions上出現
任意高 degree的同類 denominator。

這將 arithmetic coisometry的最小缺口寫成 `B identically 1`。但 boundary
`|Theta|=1` 無法區分 `Theta_0` 與 `Theta_0/B`；只使用 critical-line
unitarity或 antiunitary involution的 square必然看不到 `K_B`。必須有一個使用
prime--gamma analytic continuation/Poisson normalization的新 sum rule，exact證明該
Blaschke mass/degree為零。

## G99. 線性prime--Poisson結構只能計帳，不能迫使index zero

B38給出 exact countermodel：`Xi_a(s)=xi(s+a)xi(s-a)`, `0<a<1/2`。它是
entire、滿足 `Xi_a(1-s)=Xi_a(s)` 與 conjugation symmetry，且 Euler logarithm的
prime-power coefficients是 `Lambda(n)(n^a+n^-a)>0`，並有完整 Poisson explicit
formula。但每個 Riemann critical-line zero都被移到 `Re(s)=1/2+-a`；Hardy
的 infinitely-many theorem故給無界 Pontryagin index。

因此「positive prime weights + exact Poisson + functional equation」不提供計數以外的
index-zero約束。該 model的精確差異是 degree two、兩個 gamma channels與
`n^a` coefficient growth；故合格新定理必須非線性地使用 **single degree-one
channel + Ramanujan-size local data**，且不能對 products additive。degree-one Selberg
classification只辨識 zeta/Dirichlet L-function，不證其 GRH，所以也不消去 `K_B`。

## G100. local degree-one rank排除B38，但沒有local-to-index升階定理

B39把 single Euler channel寫成 exact nonlinear invariant：
`L_p=(1-alpha_p p^-s)^-1` 的 log coefficient sequence `alpha_p^k` 之全部
adjacent Hankel minors皆零；B38 shifted product的 minors則為
`(p^a-p^-a)^2>0`。所以 degree-one限制確實排除舊反例。

斷層在全域：real primitive Dirichlet L-functions同樣有 local rank one、Ramanujan、
單 gamma與 centered FE。一般 `local rank one => index zero` theorem會直接證
Dirichlet GRH；現有 degree-one classification沒有此步驟。指定 `alpha_p=1` 雖唯一化
為 zeta，仍缺把跨質數 rank identities耦合成 B35 coisometry的機制。local rank是
候選 identity的必要篩選器，不是 uniform升階。

## G101. BSY壓成單一正Blaschke mass，但反向sign仍OPEN

B40給 all-degree scalar target：
`Omega_zeta=(2pi)^-1 int log|zeta(1/2+it)|/(1/4+t^2)dt`
exact等於 `sum_(beta>1/2)log|rho/(1-rho)|>=0`，且 equality iff RH。若能由
Riemann-specific prime/gamma結構證同一 integral `<=0`，便一次排除全部 off-line
zeros。

但 `s=1` 的 inner--outer factorization只給
`1=zeta_B(1)B_zeta(1)=exp(Omega_zeta)exp(-Omega_zeta)`；pole normalization與
Euler product不迫使任一因子為一。hybrid Euler--Hadamard也明列 zero product。
最小缺口是 B40.3 的 critical-line log-modulus反向不等式；再證一個 BSY/Jensen
等價準則不算進展。

## G102. BSY scalar branch與Nyman uniform mollifier是同一defect

Burnol定量 theorem給 `||P_N 1||=prod_(beta>1/2)|1-1/rho|=exp(-Omega_zeta)`。
故若 `d=dist(1,N)`，exact有 `d^2=1-exp(-2 Omega_zeta)`。B40.3、NB11的
`d=0`、以及相應 inner/causal defect消失不是三條獨立路，而是同一全域缺口。
finite Nyman projections或 truncated Blaschke products只能近似，不能證極限恰為零／一。
Burnol adelic causality又已等價全部 abelian L-functions的 RH，不能當無條件輸入。

## G103. degree-one local scattering的分母是無限維singular-inner reservoir

B42精確分解
`u_p=L_p(1/2-iz)/L_p(1/2+iz)=b_(p^-1/2)(e^(iz logp))/e^(iz logp)`。
分子、分母皆 inner，但分母 exponential inner的 model space是長度 `log p` 的
無限維 Paley--Wiener reservoir。finite prime set時分母為
`D_S=exp(iz sum_(p in S)logp)`，且與分子無 common inner factor；kernel exact為
`(K_(N_S)-K_(D_S))/(D_S overline D_S)`，故已有無限負平方。這給 B34 noncompact
principal channel的 inner-factor版本，任何 finite-codimension pole restriction都不夠。

合格的 global theorem現可寫成 compatible arithmetic partial isometry
`K_(D_S) -> K_(N_S) direct-sum H_(infinity,pole)`，其 norm defect exact為 B32/B35
all-support form，並證 residual cokernel為零。逐 prime inclusion為假，故只能由
cross-place Poisson map完成。這不是 proof；尚缺的正是該 coisometry。

## G104. abstract cross-prime map已降成explicit Hankel leakage identity

依 Selberg nudge修正 G103：只說「找 partial isometry」不可證偽，不算研究義務。
B43將 local quotient展開；在 `K_(e^(izlogp))=L2(0,logp)` 上 exact有
`H_p^*H_p=p^-1 I`、`J_p^*J_p=(1-p^-1)I`。Bohr tensorization因此產生
`prod_(p in S)(1-p^-1)` 的 coisometric mass；其 collapse正是 B1 endpoint。

唯一合格的 cross-prime命題改為 B43.5--B43.6：以 finite completed semilocal
multiplier明算 Hankel leakage，並給 zero-independent 的 Poisson diagonal recovery
kernel，使餘項 exact為 B32 integrated defect且 uniform nonnegative。B12 map消掉
primes，B8 same-side map condition number發散，故兩個現成 map均未完成此式。

## G105. diagonal coupling已明算，但natural recovery失敗

B44將 finite-S prime leakage寫成有限 Mobius--Volterra sum：負頻率為
`-log(d/n)`，係數 `C_S mu(d)sqrt(d)/(phi(d)sqrt(n))`。B45再由 Tate cosine
transform給 `k_infinity(a)=2e^(a/2)cos(2pi e^a)`；completed kernel exact為
`q_S=k_infinity*nu_S`，Hankel kernel為 `q_S(-x-y)`。

結果仍未定號。Mobius signs把 uniform cancellation帶回 NB11--NB13。natural Tate
primal--dual pairing由 B12 exact消去 primes；same-side pairing由 B8.5失去 uniform
bound。故 B43 branch暫停：除非寫出不同的 explicit `R_S` 並核對 B43.6，不把
「可能有 cross-place map」列為 live mechanism。

## G106. compact-support slack不能修復single-lattice Pick uniqueness

finite dictionary的 pole source可改寫成 `[0,1]` 上 sine transform，density在
frequency `omega=1` 嚴格正；故沿 imaginary axis有
`|psi_0(iY)|>=c_L e^(2pi Y)/Y`，exponential type exact為 `2pi`。完整 source
因此恰在 Carlson/Nyquist boundary，不因 prime cutoff或 compact support降成 strict
type。`sin^2(pi z)h(z)` 又在所有 integer values及 derivatives全零，所以兩個
pole-neutral constraints也無法辨識它。單 phase全階 Loewner positivity不能靠
strict-type uniqueness升成 continuous Pick positivity；all phases仍等價 full Weil form。

## G107. 外部semilocal trace聲稱的unit-orbit collapse不成立

`li_semilocal_trace_audit.md` 核對 Li 0807.0090v10。其 Theorems 1.3--1.4
都靠把 `C_S=J_S/O_S^*` 中的 `x` 作 `x->x/gamma`，再宣告 unit-orbit summands
相同。可是 `gamma in O_S^*` 在 quotient中是 identity；additive phase
`Psi_S(xv)`又不對 representatives invariant。若固定 fundamental-domain section，
`x/gamma`一般離開 section。故 (4.13)->(4.14)、(5.8)->(5.9) 的變數代換無效，
兩個 remainder traces沒有被證為零，論文不構成 RH證明。

修正後的義務是保留所有 distinct unit phases，直接證 orbit sum為零或具所需 sign。
這正是 semilocal Poisson/prime cancellation，而非 quotient multiplicity；與 B32/W12
的 sharp all-test positivity同級。W19另證一般 OS dilation雖可把 box Hankel kernel
轉成 group covariance，prime endpoints卻是 bulk的 distribution derivative加 boundary，
所以也沒有越過此 gap。

單 prime檢查使錯誤更不可迴避：對 `gamma=p^k`，canonical local-unit integral
依 `k>=0,k=-1,k<=-2` 分別為 `1,-1/(p-1),0`，正是該文 Lemma 2.2 的三種
weights。故 summands實際已被局部計算證明不相同。修正版必須控制留下的 lacunary
real phases與 signed `k=-1` boundary；這就是 Euler local scattering，不是可用
absolute convergence消掉的重複項。

## G108. Selberg nudge的Laplace版本是half-Cauchy spectral divisibility

`cauchy_spectral_divisibility_route.md` 定義無條件 Herglotz函數
`q_1(z)=i xi'/xi(1-iz)`。其正 boundary measure exact為
`mu_1=sum_rho P_(1-beta)(x+gamma)dx`。RH等價存在正實測度 `nu` 使
`mu_1=P_(1/2)*nu`：RH時 `nu` 是 ordinates counting measure；若有
`beta>1/2`，寬度 `1-beta<1/2` 的 Poisson kernel在 `|Im z|<1/2` 內有
不可消 pole，與此 factorization矛盾。

這把三條 derivative-sign斷層統一成單一 all-degree measure target
`exp(|D|/2)mu_1>=0`。它不需 endpoint微分，但 backward Poisson operator無界；
generic positivity不保其 range。Euler側合格定理是對所有 `epsilon>0` 證同一正
`nu` 的 `mu_(1+epsilon)=P_(1/2+epsilon)*nu`，並可取相容極限。local inverse
exact重現 B43 leakage，故目前仍缺 conductor-one cross-prime divisibility theorem。

## G109. Cauchy反演沒有降低成較弱的正性問題

CS5證明 `exp((1/2+epsilon)|D|)mu_(1+epsilon)` 與 `epsilon` 無關；若為正測度，
它就是零點 ordinates counting measure，其 Fourier transform distributionally等於
`Psi''`。所以 half-Cauchy criterion雖避開「對 arithmetic bulk取導數」的表面操作，
實質仍是 full Weil all-support positivity，不能靠 finite moments或有限矩陣替代。

另以 `A(x)=x-psi(x)` 對 prime sum作 Stieltjes分部積分，得到 CS5.6 的 exact公式：
`Psi(t)` 是正三角 kernel對 signed Chebyshev error `A` 的積分，加完全顯式的
archimedean項。`A` 不定號；現有 zero-free-region absolute bound只重現
`exp(t/2-c sqrt(t))` 尺度，遠不足以證下界零。故新 proof input必須是 conductor-one
的 oscillatory cancellation／正定性定理，不能只是 PNT誤差絕對值估計。

## G110. Freedman全-omega Weyl證書在compressed contraction處失效

`weyl_debranges_derivative_bridge.md` 的 WD1--WD3 給一個可保留的精確結果：若
Freedman座標核 `K_omega` 對每個 `0<omega<1/2` PSD，則
`partial_omega D_omega=(4/pi) F K_omega F*`；由 `D_0=0` 積分即得 shifted-Xi
de Branges核正性，進而推出 RH。這補上該文自述欠缺的最後 transform bridge，且
不是有限證書。

但 companion source 的 Weyl正性並未成立。核心程式只由
`|kappa(s,u)|<=1` 宣告 `||C K E||<=1`，其中 `C` 是 s-積分。一般反例
`C=[1,1]`, `K=diag(1,-1)`, `v=(1,-1)` 給 `Cv=0`、`CKv=2`，故 pointwise
contraction不能穿過 compression。所謂 boundary theorem又把 `B` 定義成
`P-M=Q`，並假定 indefinite `Q` 的 fiber minimizer存在；Euler消邊界只是重述，
沒有提供缺少的 norm inequality。closure script另將三個連續性狀態直接 hard-code
為 True；有限 Green representer檔自己的 theorem仍是條件句。

詳見 `freedman_weyl_positivity_audit.md`。所以新外部輸入沒有證明 RH；它把 live
all-degree義務縮成：對 concrete `C,E,K` 證真正的特殊 intertwining/range theorem，
或直接把 `K_omega(a,b)` factor成 Hilbert Gram，且須 uniform於整個 omega區間。

## G111. Weyl positivity的對角已包含complex Laguerre判據

WD5 exact算得，對 `z=x+iomega`，
`partial_omega D_omega(x,x)=(|Xi'(z)|^2-Re(Xi''(z)overline{Xi(z)}))/pi`；
再由 WD2.3，它就是 `K_omega` 對 truncated plane waves的極限 quadratic form。
所以即使不看 full matrix，Weyl PSD已必須證 Xi 的 complex Laguerre inequality。

Csordas 1309.0055證 Riemann kernel的 strict log-concavity只使
`K_n(t)=int Phi(s+t)Phi(s-t)s^(2n)ds` 保持 admissible；所有 n 的正定性 iff RH，
而最簡單實軸 `L_1>=0` 尚列 open problem。故 theta log-concavity、單峰性、
有限 Turan inequalities不能修補 G110。direct Gram route只有在產生真正
all-configuration factorization時才算新結構。

FW6將 G110再精確化為
`E^*(C^*C-KC^*CK)E>=0`，等價 Douglas contraction factorization。
`I-K^2>=0` 不足；而且 nonconstant `kappa(s,u)` 明確不保持 integration map C 的
kernel（兩個 equal-mass bumps即可反例）。故任何修正版必須在 special theta image
上獨立構造 contraction T；以同一 signed Q 的 minimizer定義 E 是循環的。

## G112. strict log-concavity也沒有提供uniform Weyl升階

WD6構造 `phi=e^(-t^2)(1+0.1cos t)`。它正、偶、admissible、嚴格遞減，且解析有
`(log phi)''<=-17/9`；但 Fourier transform exact為
`sqrt(pi)e^(-z^2/4)[1+0.1e^(-1/4)cosh(z/2)]`，有顯式非實零點。因此由 WD3，
其 small-omega Weyl family不可能全正。NE1在 omega=.49 也找到相對
`-2.43e-5` 的負方向，只作 consistency check。

所以 G110不能由 Phi的已知 positivity、unimodality、admissibility或 strict
log-concavity完成；任何 uniform theorem必須使用 Riemann-specific modular/theta
mode coupling，且輸出 FW6 Douglas condition，不能只列 shape inequalities。

## G113. uniform Weyl positivity exact等價Laguerre--Polya／RH

WD7補上 converse。若 real entire `f` 屬 LP，則
`R_12=f(z+iomega_1)/f(z+iomega_2)` 對 `omega_2>omega_1>0` 是 C+ 的 Schur
multiplier：每個 real-zero factor是兩個到 lower-half-plane zeros的距離比，Gaussian
factor也有 modulus `<=1`。故 de Branges spaces `H(E_omega)` 隨 omega contractively
增加，`D_omega2-D_omega1>=0`，所以 `partial_omega D_omega>=0`。WD2 fixed-height
Fourier inversion再給 coordinate `K_omega>=0`。

反向由 WD3：任一 `(0,omega_0)` 上全 family PSD即排除所有 nonreal zeros。因此對
Xi，Freedman uniform Weyl positivity iff RH。這是尋找的真正 uniform-in-degree
結構，卻也證 special theta Douglas contraction不是 RH之前的普通技術 lemma；證出
它本身就是 RH proof。後續只能尋找 arithmetic/modular機制證 WD7正向的假設，不能
再由 generic de Branges chain倒推。

## G114. Jacobi--Poisson只給boundary unitarity；half-line causality仍是RH

TPD2把 Weyl form exact寫成兩組半軸 Hankel norm之差。Jacobi 模偶性確實進入
Douglas式，但只給 `q_(sigma,-)(t)=q_(-sigma,+)(-t)`：minus output對應 plus
transform的負半軸，而非同一正半軸 range 上的 contraction。

在 `omega=0`，`hat q_+=Xi-iXi'=E`、`hat q_-=Xi+iXi'=E#`。比值 `E#/E`
在實軸 unimodular是無條件的；若要求它保持整個 Hardy half-space，就必須 inner，
也就是 Hermite--Biehler／RH。嚴格說 FW6 只需 `Ran(A_0^+)` 上的 contraction，不能
由 full-space criterion直接偷換；但該 restricted statement就是 `K_0>=0`，而
VK6/K0B3已獨立證它等價 RH。故兩種版本都不是 Poisson full-norm equality的結果。
只有一個明確的 lattice-level special-range intertwiner（含 range與 norm proof）
才會是新輸入，且 WD6排除了所有只依 scalar偶性／shape的版本。

## G115. Poisson lattice unitary不能穿過Dirac-comb sampling

log-scale共軛 exact 給 `J(D_u^2+D_u)J^-1=d_t^2-1/4`，故 Sonine differential
operator確與 Xi kernel相接。但 theta取值還需 `C f=sum_n f(n)`；TPD7用 N個互斥
零積分 bumps 構造 `||f_N||_2=1`、`f_N(0)=hat f_N(0)=0` 而
`|Cf_N|~sqrt(N)`。所以連 pole-neutral subspace上 C都不 bounded。

因此 ambient Poisson unitary／half-space projection的 contraction不能直接 descend
成 FW6；這正是新的 compression 斷層。尚可行的最窄 lemma 是對 concrete
Gaussian-dilation theta range證 uniform sampling/frame inequality，並證其 defect
exact等於 TPD2/K0 form。若只引用 Poisson、Sonine兩個 moments或一般 sampling，路徑關閉。

## G116. actual Gaussian/Sonine range 的 global frame bound亦由zeta mean-square否決

Mellin 對角化 dilation後，Gaussian的 Mellin transform是無零 Gamma factor，
`D_u^2+D_u` 只再乘 `-(tau^2+1/4)`，故 differentiated Gaussian orbit仍 cyclic。
Dirac-comb sampling在此 cyclic model中的 Riesz symbol exact為
`zeta(1/2-i tau)`。若 C 對該 range有 uniform L2 bound，Riesz theorem會迫使此
symbol屬 L2；經典 `int_0^T|zeta(1/2+it)|^2~TlogT` 直接矛盾。

故 G115 所留 global frame lemma也關閉。lattice/Poisson方向只剩支撐依賴且經
counterterm重整的 **difference of sampling defects**；必須讓共同 cusp baseline
exact相消並留下 K0 form。這就是既有 restricted mean-delay/integrated
Maass--Selberg義務，不能以單邊 sampling boundedness完成。

## G117. 三個defect sign是同一zero pairing；只剩平方機制（OPEN）

DU1--DU3 證明精確統一。Xi Bezoutian的 zero expansion使 TPD Hankel norm差等於
`2 sum_rho R(rho)conj(R(conj rho))`；B21 leakage cocycle、B22 mean delay與 B31
cumulative area則對同一 compact pole-neutral test逐式相等，並由 explicit formula
等於 `sum_rho H(rho)conj(H(conj rho))`。所以它們不是三個不同 sign obligations，
而是同一 indefinite zero pairing在 resolvent與 Paley--Wiener test classes上的 pullback。

尚未閉合的是唯一一件事：在不先假設 zeros real/innerness下，把每個 support的
完整 renormalized B31 area（共同 baseline及全部 incoming/outgoing boundary均保留）
寫成 norm square。Maass--Selberg若只提供未減 truncated norm，或另一個 defect積分
表示，仍是同義改寫而非進展。

## G118. 兩個pole moments可exact消去，但只是負指標不變的congruence

DU6證 `ker(E_+,E_-)=Q C_c^infty(-x,x)`，`Q=-d^2+1/4`；Green convolution因兩
moments而在支撐外exact消失。Fourier側 `H=(z^2+1/4)G`。此乘子在 Xi zeros上
非零，故對每個 off-line conjugate pair只作可逆 diagonal congruence，`+/-` inertia
不變。算術側則產生 B34 的 shifted derivative cross-energies。

因此 pole factorization沒有把 G117降成普通 Poincare inequality；若後續估計只用
`h=Qg`、local derivative coercivity或有限 codimension，必然仍缺 prime-shift符號。

## G119. folded Thorin positivity是全階結構，但外部 critical-line tilt失敗

Polson 的 folded-zero/Thorin dictionary確實一次涵蓋所有 degree：dual Thorin
measure正、Stieltjes/Hankel/Jacobi全正、LP與 Weil positivity彼此等價。對 xi，
該 measure 是 `sum_rho delta_(rho(1-rho))`；它為正實 measure本身就是 RH，不能由
`Xi(t)/Xi(0)` 是 characteristic function或 integer-square Barnes clocks推出。

arXiv:1804.10043v8 所宣稱的 closure有顯式錯誤。Theorem 23 的式 (30)、(31)按稿面
不是恆等式；更決定性地，其 `U_star=delta_(3/4)+...` 使 `H_star` 含 rate 3/4
exponential summand，所以 Theorem 25 所需 `E exp(H_star)` 必為無窮，參數 1 tilt
不存在。SSRN 6992163 後稿也把 dual positivity明列為 RH-equivalent open clause。

更上游的式 (24) 已符號反轉：`log(1+s/c)-s/c<0`，正確 Levy integrand前應有
負號，所以 (22) 的 pole contribution 是 `-e^x dx`，不是 `+e^x dx`。修正後
prime atoms、Gamma與 pole baseline構成 signed renormalized measure；Lemma 16 的
nonnegative-measure/Tonelli不能套用。這把缺口直接辨識為 G117 的 prime--pole defect。

故這條路提供合格的 uniform target但沒有 arithmetic sign。不得重開有限 secondary-
zeta moment證書；只有無條件把 folded logarithmic derivative寫成 Stieltjes transform
的全域 theta/prime factorization才會關閉缺口。詳見 `polson_thorin_audit.md`。

## G120. actual Phi 的 ordinary total positivity在degree 5嚴格失敗

arXiv:2602.20313v2 給 actual de Bruijn--Newman kernel `K(u)=Phi(|u|)` 的
5x5 Toeplitz負 minor。已用獨立 python-flint/Arb 320-bit balls重驗，theta tail解析
widen `1e-70`，matrix determinant與120-term Leibniz分別得到彼此重疊且全負的
enclosure，中心約 `-1.8472360734426587e-9`。詳見 `phi_pf5_audit.md` 與
`experiments/verify_phi_pf5_arb.py`。

所以 degree 3不只缺升階定理；raw translation-kernel PF-infinity對實際 Phi為假。
這不反駁 K0/Bezoutian/Weyl positivity，因其是不同 signed derivative/correlation
kernel；它只關閉以 Phi普通 Schoenberg全正性作 uniform mechanism 的路線。

## G121. Thorin boundary density可無條件為正，但看不見Blaschke inner factor

修正 prime--pole sign後，對 `a>1` 的 combined sine-square transform exact為
`S_a(t)=log(xi(a)/|xi(a+it)|)`。Williams/Ostrovsky Mellin law使 normalized ratio
成 tilted `log W` characteristic function，故 `S_a>=0` 無條件；臨界線亦同。

然而 modulus只決定 outer factor。若有 `Re rho>1/2` zeros，其 half-plane Blaschke
product在 boundary modulus為1，完全不改 `S_(1/2)`。此外 raw Gamma measure近0
使 Polson Lemma 16 的 integrability假設失敗，仍需 archimedean renormalization。
所以 boundary density正不等於 analytic Stieltjes/GGC closure；缺口是證 hidden inner
factor為常數，亦即 RH。詳見 `thorin_outer_inner_bridge.md`。

## G122. off-line inner factor是顯式Poisson phase bumps；一般Mellin/GGC性質不排除

右側 zero `1/2+a+i gamma` 的 half-plane Blaschke factor在 critical boundary
modulus為1，但 phase derivative exact給 `-2a/(a^2+(t-gamma)^2)`；共軛 pair再加
中心 `-gamma` 的同型 bump。故 RH缺口可具體寫成：renormalized arithmetic phase
不得含任何 `a>0` 的 absolutely-continuous Poisson bump。

搜尋未找到 GGC/HCM Mellin transform定理能由 boundary characteristic positivity
排除此 inner項。WD6 的 positive even strict-log-concave entire-moment density已有
off-axis zeros，actual Phi 又非PF5。因此只靠 positive Mellin law、log symmetry、
shape或 raw variation diminishing 都不夠；必須輸入 prime/archimedean phase cancellation。

## G123. outer scalar預算只給 `O(T^2/delta)` 離線零點界

單一 Nyman 函數 `rho_(1/2)={1/(2x)}-(1/2){1/x}` exact 給
`d^2<=1-log 2`。結合 Burnol 公式，
`Omega_zeta<=C_0=-(1/2)log(log 2)`。對 `rho=1/2+a+i gamma`，BSY 質量滿足
`log|rho/(1-rho)|>=a/[gamma^2+(a+1/2)^2]`，故按重數

`N_off(delta;T<=|gamma|<=2T)<=C_0(4T^2+1)/delta`。

這是嚴格、無消去的 inner 損傷上界，但尺度不能迫使計數為零。改善有限 Nyman
近似只改善常數；令預算趨零正是 RH。Li 核若無額外 uniform 正號，其較佳高度
局部化仍受跨零點消去阻擋。詳見 `outer_budget_zero_density.md`。

## G124. 純 prime phase sign 已有一參數 target，但缺二階 cumulative domination

Suzuki ES118 證 RH 等價於
`g_0(t)=sum_(n<=e^t)Lambda(n)n^(-1/2)(t-log n)-4(e^(t/2)+e^(-t/2)-2)`
最終非正。其 `g_0''` 是 prime atoms 減 pole density，Laplace transform為
`-z^(-2)d_s log[s(s-1)zeta(s)]`。這保留 inner phase，且不是 fixed-degree route。

目前缺口是把此完整 signed difference寫成正平方或證二階 convex-order domination。
`Lambda>=0` 方向相反；PNT absolute error遠大於 logarithmic sign margin；prime powers
分項估計會產生 `(log x)^2` slack。Freitas generalized Li recurrence沒有逆向保正原理，
Suzuki Li-norm identity又先用 inner/model-space正交性。詳見
`arithmetic_phase_sign_audit.md`。此支列為 live arithmetic target，但尚無 sign lemma。

## G125. `Lambda*1=log` 正卷積精確消掉 zero poles，不能作 recovery

對 `H=-g_0` 與 `eta=sum m^(-1/2)delta_(log m)`，正卷積 `R=H*eta` 可化為只含
`H_N`、`sum m^(-1/2)` 與 `sum (log n)/sqrt(n)log(x/n)` 的整數式。但 Laplace
multiplier 正是 `zeta(s)`，會精確消掉 `Hhat` 在所有 nontrivial zeros 的 poles。
Euler--Maclaurin 給

`R(t)=4(1+gamma_0)e^(t/2)+O(t)`，

故其巨大正號來自 `s=1` counting pole，與 RH 無關。非平凡正 measure也不可能有
正卷積逆；support argument迫使正 inverse pair皆為 point mass。因此自然
`Lambda*1=log` renewal 關閉。AP/G124仍可留作 target，但下一個 kernel必須不消
zero singularities，並另證 restricted sign recovery。詳見 AP6。

## G126. zero-free exponential smoothing保留全部 zero poles，但 sign仍OPEN

對 `H=-g_0` 取 causal kernel `e^(-at)1_(t>=0)`，multiplier `(z+a)^(-1)` 無零，
所以 Landau oscillation theorem給：convolution `E_a` eventual非負仍等價 RH。
`E_a` 有 AP7.3--AP7.4 的顯式 prime-tail公式，沒有 AP6 的 zero cancellation。

但 kernel只把 triangular weight換成
`phi_a(v)=v/a-(1-e^(-av))/a^2`；現有 PNT absolute errors仍遠大於 sign margin，
未找到 one-sided Tauberian／Euler-product inequality證其定號。故這是合格的 live
smoothing family，但尚未降低核心 arithmetic sign。

## G127. BSY 單基點傳播的 `T^2` 損失由 Harnack sharpness 強制

對 `u=-log|B|`，BSY只控制半平面基點 `s=1` 的 `u=Omega_zeta`。Harnack inequality
到 `1+iT` 的最優因子為
`(sqrt(1+T^2)+|T|)^2=4T^2+O(1)`。一個位於高度 T、距 critical line為 b 的
單 Blaschke zero在 `b->0` 時 exact達到此比例。因此 G123 的 `T^2` 不是粗估；
只用單 scalar outer budget的任何論證都不可能改善高度量級。必須取得 shifted local
budgets或 phase/winding控制。詳見 OB4。

## G128. 最右 zero 層若隔離則必迫使 `g_0` 正 excursion；一般 spectral edge可不取到

一個 quartet `q=a+i gamma` 對 `g_0` 的 exact貢獻是
`-4Re(cosh(qt)/q^2)`，正峰主振幅為 `2e^(at)/(a^2+gamma^2)`。若最大 `a=A>0`
由有限個 edge zeros取到且有 horizontal gap，edge sum為非零 mean-zero
trigonometric polynomial乘 `e^(At)`，故必有無界正負 excursions；聚合不能關閉。

尚未閉合的是 `sup a` 不取到或無限 zeros逼近 edge的情形。BSY質量
`sum a/gamma^2<infinity` 不排除此配置，也不給 spectral gap。Landau theorem只給
定性 oscillation；仍缺能在 prime-side inequality中使用的 uniform positive-peak
下界。詳見 AP8。

## G129. edge-free 聚合已由 Mellin振盪定理處理；真正缺口仍是 prime-side單邊號

對 `f(x)=g_0(log x)`，每個 off-line zero `q=a+i gamma` 都在 Mellin transform
產生 residue `-m/q^2` 的非零 simple pole。Radziejewski weakly-bounded Mellin
theorem配合標準 `zeta'/zeta` vertical estimates，給

`g_0(t)=Omega_+(e^(at)t^(-M))` 且 `Omega_-(e^(at)t^(-M))`

（某有限 M），不要求最右 zero、有限 edge或 gap。因此 G128所留的無限聚合問題
不是後續 blocker。尚未閉合且直接承擔 RH的命題仍是從 primes獨立證
`g_0(t)<=0` eventually，或對 AP7 zero-free smoothing證 eventual positivity。
外部 theorem只有 failure detector，沒有 sign producer；不得把它誤報為證明。

## G130. 一階 increment是較弱的 RH target；compact-window二階 increment不可定號

令 `H=-g_0`。AP10證

`RH iff 存在 L>0，使 H(t)-H(t-L)>=0 eventually`。

正向用 RH下 `H=c_0t+O(1)`；反向用 increment positivity給 H下界，再由 G129的
off-line負 excursion排除離線零點。這提供可沿 grid正向迭代的 sign-recovery，且
prime式 AP10.1只有 capped past加最近 L-window；目前仍無 upper bound。

再取二階差分雖把 prime sum完全局部化到 `(e^(t-2L),e^t]` 的 triangular weight，
卻消掉 `c_0t` drift。其 multiplier `(1-e^(-zL))^2` 對 generic L不消 critical-line
zero，故 Radziejewski theorem迫使正負振盪；不能要求 eventual定號。真正剩餘 target
是 AP10.1 的一階 increment，不是更多 local-window sign batches。

## G131. AP11 derivative-renewal同時保留 zero poles與正 sign-recovery

對 AP7 exponential smoothing `K_a`，改攻 `D_a=K_a'=H-aK_a`。若 D_a eventual
非負，K_a單調且 H有下界；G129立刻推出 RH。RH反向由 `H=c_0t+O(1)` 並取足夠小
a成立，所以「存在 a使 D_a eventual非負」與 RH等價。

prime式的權重為非負飽和核 `[1-(n/x)^a]/a`，multiplier `z/(z+a)` 不消非實
zero poles；這是目前最具體的 restricted sign-recovery kernel。未閉合處是 AP11.4
的 one-sided upper bound。`a=1/2` 雖化成單一 `psi` integral AP11.6，但 PNT error
仍壓過 `sqrt(x)` slack。

AP11.8--AP11.10 又以 exact Hadamard常數證明不必量化 existential a：固定
`a=1/2` 已有

`RH iff (sqrt(x)/2)int_1^x psi(u)u^(-3/2)du <=x-1-log x`

對所有充分大 x成立。這是有解析 margin的固定 prime integral target；等價式本身
仍不是 closure，所缺正是其 unconditional upper bound。

## G132. recent Chebyshev mean-square claimed closure由空 floor cells否證

Preprints.org 202605.1525v4 的新輸入不能使用。其 Lemma 9 對所有 m宣稱
`sum_(floor(N/k)=m)k/N>=1/(2m)`；`N=10,m=6` 左側空和為0，右側為1/12。
floor map只取 `O(sqrt N)` 個值，故不能控制所有 `A(m)=psi(m)-m` 的平方和。
後續 critical mean-square與 integral convergence失去依據。AP11.6仍OPEN；詳見 PC2。

## G133. known weighted Chebyshev bias止於 c=2；AP11需要臨界 c=3/2

AP11.6等價於 AP12.1 的 `R(u)u^-3/2` partial integral upper bound。Johnston可由
Mertens bounds無條件處理 c=2，但其反向 oscillation theorem證任何 off-line
`omega>1/2` 在所有 `c<1+omega` 產生正 excursion；特別涵蓋 c=3/2。
故從 c=2向下插值會在3/2前承擔完整 zero資訊，沒有現成 continuity/monotonicity
propagation。未閉合者仍是 critical c=3/2 的 exact upper barrier。

## G134. 全階乘法極值已找到；斷層是 renormalized Euler product 的 uniform bound

Akatsuka 的 1/2-SHCN theorem一次處理所有質因數數目與所有 prime exponents：任意 n
的 normalized `sigma_(1/2)` 由某個 `E_1(p_r)` 控制，而 RH exact等價
`sup_X E_1(X)<infinity`。因此現在已有 uniform-in-complexity mechanism。

但 mechanism只完成 reduction。`log E_1` 含臨界 weighted Chebyshev linear term及
非負 theta concavity defect；兩者的 uniform upper bound未由 Euler-factor positivity
推出。exact prime jumps已有一正一負的 Arb witness，排除逐 prime monotonicity。
真正缺口是完整 defect bounded above，或 SHCN ratios 的全域 Lyapunov inequality；
有限 `E_1`／`a(n)` 計算不得替代。詳見 `akatsuka_multiplicative_audit.md`。

進一步的 A5.5 已把 uniform mechanism寫成 exact凸對偶：
`G(c)=sum_p log max_e[sigma_-1/2(p^e)p^-ce]`，而 `V(c)` 是
`li(sqrt L)` 的顯式 concave conjugate；所有 n有界 iff `sup_c(G-V)<infinity`。
這是合格的 all-degree certificate，但尚缺 `G(c)<=V(c)+C`。若證明只把 G 展開後套
absolute PNT error，仍回到同一臨界斷層。

## G135. convex dual已消去 theta二次項；唯一缺口是 linear logarithmic mean

AP14/A6證 `G(c)-V(c)=C_0+Q(x^2)+o(1)`，其中
`Q=int(psi-u)u^-3/2(1/(2log u)+1/log^2 u)`。所以 Akatsuka route不再有兩個需分別
控制的 defects；uniform all-degree bound exact等價 `Q` bounded above。

但這也顯示它不是新的 positivity source：Q是 AP11 defect的 `1/log` damped mean。
kernel雖是 `s>=3/2` power weights的正 mixture，已知 `s>=2` bias不能推到 endpoint；
off-line zero仍使 Q出現 growing positive excursion。未閉合引理就是直接證 A6.4，
不能以 concavity、positive mixture或較強權重的 bounds冒充。

## G136. 數值定位排除固定主導質數；RH obstruction在 frontier prime scales

依 Selberg lens，`akatsuka_dual_extrema.py` 掃描 143264 個 transitions。後段 plateau
極值由接近 `Y=log N` 的新 primes夾住；在 `Y~1.58e6`，約60%的 raw G mass來自
`p>Y^(3/4)`，而 defect僅約0.04246，是全尺度抵消。這只是策略數值，不是 RH證據。

explicit-formula尺度亦支持 no-go：off-line距離 a給 full frontier `Y^a/logY`，截到
`Y^delta` 只剩較低 exponent `Y^(delta a)`。故固定小 primes可精確扣除但不會移除
RH obstruction；真正局部子題仍須控制 renormalized frontier window，而該 window
保留 generic off-line poles。沒有因此切出 zero-blind 的較弱 closure。

## G137. proportional frontier window有精確 no-cancellation theorem，仍等價 RH

AP15令 `W_delta(Y)=Q(Y)-Q(Y^delta)`。其 log-Laplace transforms相差縮放
`delta^-1 Qhat(z/delta)`。若 off-line supremum A>0，任取 real part `a>delta A`
的 zero singularity；縮放項所有 singularities至多在 real part `delta A`，故不能
抵消。於是 W_delta有正負 unbounded excursions。RH下 W_delta為 `O(1/logY)`。

所以對每個 fixed delta，W_delta bounded above仍 exact等價 RH。這關閉「扣除所有
`p<=Y^delta` 後也許剩下容易 tail」的希望；localized tail是較乾淨座標，不是較弱定理。

## G138. blockwise mean-square positivity在臨界 log damping仍差 harmonic summability

即使假設 RH-scale `int_X^(2X)R^2<<X^2`，AP16的 Cauchy--Schwarz每 dyadic Q-block只
給 `O(1/logX)`；沿 `X=2^k` 為 harmonic divergence。故不能期待普通 Selberg L2
square或更好有限常數直接證 Q bounded。所缺不是同一 block的 coercivity，而是跨
log-scales的 signed phase/telescoping cancellation；丟掉 cross terms即無法 closure。

## G139. fractional Selberg square 保留全部 zero multiplicity，卻未提供 renormalized positivity

`S_alpha=(-zeta'/zeta)^2-alpha(-zeta'/zeta)'` 對 `0<alpha<1` 有全非負
Dirichlet係數，且每個 multiplicity `m` 的 zero有非零 double pole `m(m-alpha)`。
因此 arithmetic positivity 與 robust zero detection 可以共存。

斷層在主項扣除：其一階 Cesaro remainder 的 separation-free exponent bound
`O_epsilon(x^(1/2+epsilon))`（所有 epsilon）本身即等價 RH；sharp
`O(sqrt(x)log x)` 正向未在此宣稱。係數正性只控制未扣除的正總量。尚缺的是 signed
cross-scale identity，使主 pole exact telescope且餘項成真正非負 energy；固定尺度
差分或直接宣稱 critical remainder bounded皆只是換皮 RH。

## G140. 清除 fractional denominator後的自然 Laguerre square是 zero-blind

`alpha=1/2` 的 `(zeta^2)''/(4zeta^2)` 乘回 denominator並完成化後，最自然的
critical-line form是 `f'^2-ff''`，`f(t)=xi(1/2+it)`。全線積分 exact等於
`2int f'^2>=0`，對任意 real decaying f皆成立；加 weight則多出
`-(1/2)int w''f^2`，不再自動正。因此 denominator-clearing雖產生真 square，卻在
integrated level完全 zero-blind；pointwise版本所需 sign又沒有 prime-side來源。

## G141. uniform all-degree Hankel positivity存在，但只描述 `Re(s)>1` 的 pole-local law

對 `P(N=n)=d_k(n)n^-sigma/zeta(sigma)^k`，全部
`(-1)^r(zeta^k)^(r)/zeta^k` 是 `log N` moments，故任意尺寸 Hankel matrices一次
PSD。`sigma=1+epsilon` 下，`epsilon log N` 全 moment/Laplace transform趨
`Gamma(k,1)`，再由 k大得到 Gaussian。這是具體 uniform-in-degree mechanism。

但 probability representation只在 `Re(s)>1`；到 critical line必須作 meromorphic
continuation，而正 measure的 Laplace transform在其 continuation可有 nonreal zeros。
所以這個全階結構只看見 zeta pole的 universal local law，不能限制 continued zeros。
缺口不是更多 moments，而是把 positivity跨過收斂邊界的 theorem；若 theorem本身
要求 continuation zero-free到 `Re(s)>1/2`，即為循環。

## G142. infinite-divisibility bridge有外部 exact equivalence，不能當一般延拓引理

ES126 顯示 completed zeta distribution在 1/2<sigma<1 的 pretended infinite
divisibility全域成立 iff RH；另一個 exp(g_zeta) 的 genuine infinite divisibility
亦 iff RH。故把 SFS9 的 compound-Poisson/Hankel正性跨入 critical strip並非較弱
子題；沒有新 arithmetic construction時，宣稱 Levy measure保持正只是在 zero side
先假設 RH。

## G143. completed arithmetic phase 的 Lévy positivity就是 integrated Weil positivity

AP18 的 g_zeta 是 g0 加顯式 gamma counterterm，且
`g_zeta=sum m_gamma(e^(-i gamma t)-1)/gamma^2`。RH下負號是 sin-square和；
`-g_zeta''` 的 positive definiteness正是 real zero spectral measure。故從 arithmetic
side證 g_zeta 為 infinitely-divisible exponent，與 Weil quadratic form全正是同一
uniform obligation。此合流排除把 probability、AP sign、Weil/GNS當三條獨立路徑。

## G144. screw convex dual完成全 prime-power reduction，但 vertex domination仍是 RH

AP19/SC3 將連續 sign exact離散成 Z_j>=B^*(Y_j) 對所有 prime powers。
這提供 uniform-in-complexity polygon，不需逐 degree證書；然而 Fenchel duality只
證明它與 g_zeta<=0 等價，沒有產生 vertex sign。所缺是 prime-power cumulative
polygon對 smooth archimedean conjugate的 unconditional global majorization；
宣稱該 majorization即宣稱 RH。

## G145. SC4 transition逐項單調律已有 rigorous正負反例

experiments/screw_transition_arb.py 以 outward-rounded Arb及解析 Lerch tail證
B'(log16)>Y_16，故該 increment正；同時證 B'(log32)<Y_before32，故該
increment負。因而 vertex defects不能由逐 prime-power同號累積證明。這不影響
SC3 exact criterion；它把剩餘候選縮成真正跨 transitions 的 telescoping/transport。

## G146. 剩餘 SC 缺口是 quantile primitive；正 renewal transport會消零

SC6 將 vertex defect exact寫成 prime階梯 quantile ell 與 smooth quantile
tau=(B')^-1 的累積差。SC5證 integrand兩號，故只能攻 primitive majorization。
自然的 Lambda*1=log 正 transport在 Mellin側乘 zeta，依 AP6精確消掉 nontrivial-zero
poles，不能證仍等價 RH的 SC3 target。合法 transport必須 nonvanishing並保留 phase。

## G147. Gaussian是 nonvanishing transport，卻仍只給 exact RH smoothing

AP20 的 Gaussian multiplier e^(sigma q^2/2)不消任何 zero pole，所以 fixed-sigma
eventual sign仍 iff RH；但 backward heat不保正，且 TPD8已排除 Gaussian cyclic
range的 global frame捷徑。故 J24 local Gaussian證書不能藉 heat smoothing升到
all-degree／prime-side sign。

## G148. 已知 prime envelope 的 quantile變分下確界為負無窮

AP21/SV1 精確給 `H(t)=H(T)-integral_T^t(Y-B')`。若只保留 `Y` 單調及對稱界
`|Y-B'|<=E`，而允許某個非負遞增、不可積的 `E_0<=E`，則 relaxed cumulative
`Y_*=B'+E_0` 合法且使 gap趨 `-infinity`。Bellotti 2508.02041 的最新無條件 PNT
界導出 `E_0` 尺度 `exp(t/2-dt^(3/5)(log t)^(-1/5))`，不可積；即使只取
RH-consequence尺度 `|psi(x)-x|<<sqrt(x)log^2x`，SV1.3仍只給 `E=O(t^3)`，也不可積。

故 Selberg nudge 的變分法若只用 absolute prime bounds，確實無法 closure；這是
relaxation內的解析反例，不是數值判斷。尚缺 signed cross-scale correlation、比
monotonicity更強的 prime-power離散約束，或在特定 arithmetic range 上可正反演的
nonvanishing transport。直接假設 primitive有界即重述 RH criterion。

## G149. Schoenberg reciprocal-Xi 是全階等價座標，並與 Stieltjes--Thorin 合流

ES128/SRX1 給 `RH iff F(t)^(-1)` 的反 Fourier核為 PF-infinity，確實一次控制所有
translation minors。但 Euler Dirichlet expansion只在實軸兩尾合法；中央區間只能以
additive Fourier correction接回，而 total positivity不對加法封閉，Mobius係數亦兩號。
Schoenberg factorization本身又等價 A20/G119--G122 的 positive Stieltjes/Thorin
measure。因此不把它重複列成新路徑。尚缺的仍是不用 zeros、直接由 theta/primes
構造 Loewner--Whitney convolution factors或 all-minor determinant identity。

## G150. ordinary-Laguerre Parseval 是全階正能量，但仍停在 RH-equivalent L2

`li_laguerre_l2_external_audit.md` 由 D10.4 與 Arias de Reyna 外部 theorem
核對 `E_n=n a_n`，其中 `a_n` 是 `Pi(e^t)-Li(e^t)` 的 ordinary Laguerre
係數；RH exact等價 `(a_n) in ell^2`，亦等價
`int |Pi(x)-Li(x)|^2x^-2dx<infinity`。這是真 uniform-in-degree Parseval
結構，但比 LS2 的 density-zero 負尾目標更強。Karp 的 geometric-weight
theorem要求 entire restriction，而 prime-power jumps排除直接套用。尚缺的是
只控制負指數門檻之 density/block 的單側弱型 Laguerre estimate。

AL5 再把此弱型目標正定化：RH 等價於對每個 epsilon存在長度趨無限的遠端
index blocks，使 `sum|a_n|^2<=exp(epsilon N)`。有限 block energy由 ordinary
Laguerre Christoffel--Darboux kernel給 PSD 二次型。此條件比 global ell2弱，
但其 arithmetic 展開仍需要 `Pi-Li` 的 signed two-scale correlation；kernel PSD
不等於 pointwise positive，absolute PNT envelope仍不足。

AL6 又稽核 conformal Taylor positivity。`F=(s-1)zeta(s)=sum b_nz^n` 的
`b_n` 有 fractional-part/associated-Laguerre exact formula；前 80 項 `b_n,a_n`
正只是候選掃描。即使全部 `b_n>=0` 也只給 damped PGF；需要
`a_n=[z^n]log F>=0` 才是 compound-Poisson，而 Pringsheim立即顯示此條件已
推出 RH。故停止 finite sign batches，缺口仍是 uniform Levy/weak block theorem。

## G151. Suman 2026 的 Li 漸近 claim 有兩個獨立致命錯誤

`suman_li_asymptotic_claim_audit.md` 核對原稿 (5)--(7)、(53)--(54)：令
`Y(x)=L_n(log x)` 時，正確方程是
`x^2 log(x)Y''+xY'+nY=0`；原稿卻把 `Y',Y''` 換成 Laguerre 對 argument 的
導數而保留 `x,x^2`。`n=1,x=2` 已給 exact反例。因此 (53) bracket不為零，
核心 zero-sum identity (54) 無效。

此外 (62)--(74) 把 Bernoulli Euler--Maclaurin 漸近寫成收斂無窮和；由
`|B_(2k)|~2(2k)!/(2pi)^(2k)`，固定 n 時項不趨零。固定 argument 的 Laguerre
漸近 (44) 亦未證可在無界積分中一致使用。故該 claim不能補 AL5，也沒有留下
uniform signed prime correlation。

## G152. Suzuki 的全階 L2 Gram matrix 與 Li coefficient之間仍缺 RH 等號

`suzuki_model_goldbach_audit.md`：每個 `G_n` 無條件屬於 `L2(R)`，故
`Q_mn=<G_m,G_n>/(2pi)` 對全部 indices一次 PSD。外部 theorem卻是
`RH iff lambda_n=Q_nn` 對所有 n。等號證明需要
`Theta=E#/E` 為 inner，而 Suzuki亦證 `Theta inner iff RH`。因此普通 Gram正性
不能傳到 Li正性；尚缺 primes+gamma給出的 operator identity／Schur-kernel factorization。

## G153. Goldbach positivity只在未中心化層級；compact M-law 已是 RH detector

Matsumoto--Suzuki 給
`H(X)=sqrt(X)/2-X^(-1/2)sum_(n<=X)Lambda(n)(1-n/X)+small`，且
`H=O(1) iff RH`。Goldbach `r_2=Lambda*Lambda>=0` 是真正二尺度 quantity，
但 `X^2/2` 扣除後的 remainder無 sign，已知能隔離 `H` 的 error bounds仍假設 RH。
其 compact-support value-distribution converse亦先推出 H bounded，故是 detector。
缺口是 centered Goldbach convolution 的無條件 square-root cancellation，不是更多
finite positive sums。

## G154. Goldbach--Chebyshev 次指數 L2 能量是較弱正判準，仍缺 upper bound

SMG5/L13 證 RH iff 對每個 epsilon，
`int_0^T|H(e^t)|^2dt=O_epsilon(exp(epsilon T))`。反向使用 Laplace解析性，
不需最大 real-part zero。藉 Matsumoto--Suzuki (6.1)，此量是 centered weighted
prime discrepancy的顯式 nonnegative all-scale energy，比 `H=O(1)` 弱。
然而無條件 PNT envelope只給指數級上界；`r_2>=0` 亦未控制 centered square。
這是新的可接受 interface，不是已完成 RH proof。

## G155. smooth k-Goldbach 是同一 PNT error 的代數冪，無升階增益

Han arXiv:2505.23795 證 smooth weighted PNT/Goldbach error與 zero-free regions的
雙向關係。exactly `F_k=Psi^k`，故
`F_k-x^k=(Psi-x)sum_(j=0)^(k-1)Psi^j x^(k-1-j)`；提高 fixed k只重標度
同一 centered error。`(Lambda-1)*(Lambda-1)` 又有兩號，contour中是 analytic
square而非 modulus square。故不能以更多 Goldbach convolution degrees代替
SMG5 的 centered L2/off-diagonal upper bound。

## G156. SMG5 有 explicit all-size PSD prime kernel，但缺特殊向量 upper bound

SMG7 對 `b_n=Lambda(n)-1` exact給
`int_1^Y C(X)^2X^-2dX=b^T K_Y b`，其中
`K_Y(m,n)=int_max(m,n)^Y(1-m/x)(1-n/x)x^-2dx` 對任意尺寸 PSD，且
`K_infinity=(3max-min)/(6max^2)`。這是真正全 degree/determinant structure。
斷層是 RH需要 `b^T K_Yb=O_epsilon(Y^epsilon)` 的上界；PSD方向相反。
kernel依 max而非 m+n，故 additive Goldbach positivity不能填補。

## G157. L14 的 Mellin symbol 精確是 `(-zeta'/zeta-zeta)/[s(s+1)]`

SMG8 證 L14等價於上述 quotient在每條 `Re s=sigma>1/2` 的 vertical L2 norm有限。
`s=1` pole已相消；任一 off-line zero在 B留下 residue `-m_rho`，使其所在 vertical
line norm發散。這把 operator target固定成 Hardy--Mellin H2 bridge。普通 Dirichlet
coefficient square estimate只在 `sigma>1` 合法，functional equation亦只反射 poles；
尚無 primes-only contraction把 norm跨到 1/2。

## G158. 一般 Hardy-space closure只無條件到 `p<1`，臨界 `p=2`仍是 RH

ES134/SMG9 核對 arXiv:2206.00434：bounded evaluations不是主障礙；真正缺的是
closure (C3)／同空間 shift inverse。cross-space theorem在 `p<1` 成立但只給
`Re s>1`；`p=2` 才對應 `Re s>1/2`，其 closure回到 Nyman--Beurling。
因此一般 Dirichlet-Hardy embedding不能補 SMG8 的 primes-only H2 extension。

## G159. `max` kernel 可化成全尺度 Toeplitz--Green kernel，但仍只平滑 forcing

PG1/L15 證 `sqrt(mn)K_infinity(m,n)=k(|log(m/n)|)`，
`k(d)=(3e^(-d/2)-e^(-3d/2))/6`，頻譜密度為
`1/[(t^2+1/4)(t^2+9/4)]`。所以所有矩陣尺寸同時 strictly PD，且二階穩定
Green算子完全顯式。斷層沒有消失：要上界的是 `Lambda-1` 的特殊 forcing。
block同號係數反例排除任何 generic `Q<=C sum|b_n|^2/n` contraction。

## G160. semi-local Weil positivity目前仍停在 global support conjecture

Connes--Consani arXiv:1910.14368 的 Lemma 3.4 把 operator sign等同 innerness；
各 local factor ratio實際不 bounded-inner。作者用 global Poisson normalization與
support補救的核心是 Conjecture 4.1。Baez-Duarte則給 RH-equivalent critical L2 closure，
沒有無條件 closure vector。因此這些外部輸入定位了合格方向，尚未提供 L15 contraction；
引用 innerness、Weil positivity或 critical Nyman closure都會循環。

## G161. Selberg Dirichlet-convolution升階沒有產生 conjugate positivity

PG5 核對 `Lambda log+Lambda*Lambda=mu*log^2`；Mellin側是
`-L'+L^2=zeta''/zeta`。這是 uniform-in-degree/scale代數，但 `L^2` 是 analytic
square，不是控制 SMG8所需的 modulus square。higher convolution identities同樣
缺 reflection。已知 Selberg/symmetry integrals又只平均 interval origin，不能控制
固定原點的每尺度 `C(X)`。缺口可精確寫成 deterministic maximal transfer；若以
`Y^epsilon` loss證成即已透過 L14證 RH，現有 almost-all theorem沒有這一步。

## G162. live Green contraction的 subexponential版本本身就是 RH

PG6/L16 證 energy logarithmic exponent exact為
`2 sup_rho(Re rho-1/2)`。因此尋找 `exp(o(T))` contraction、SMG8全部 critical
Hardy lines、innerness與 critical closure不是四個獨立方向，而是同一 RH endpoint。
新進展必須是可獨立證明的 strict exponent improvement，最好帶可迭代 map；否則只是
把 RH改名。普通 PNT subexponential relative error並未把 energy exponent降到 `<1`。

## G163. prime--gamma positive-real kernel已全階化，但 interior positivity仍等價 RH

PG7/L17 給 `K_M=(M(z)+conj M(w))/(z+conj w)`；RH下是 zeros boundary vectors的
all-size Gram，反向 PSD+holomorphy排除右半平面 poles。Euler series只在外半平面
直接給資料。functional equation只固定 boundary all-pass性；off-axis quartet的 even
polynomial證明同樣 boundary symmetry可共存於 interior poles。因此不能從模一邊界
或 reflection單獨升成 Schur/positive-real interior。

## G164. Landau正三角多項式法固定只能給高度依賴零區

PG8：標準可丟棄其他 zero terms的 class要求 `a_k>=0,a_1>0`；explicit formula的
gamma cost至少 `(a_1/2)log t`，故提高 degree只能改善常數，仍平衡在
`1-beta asymp 1/log t`。若允許 signed coefficients令 `P(0)=0` 消 gamma主項，
其他 harmonics的 zero terms立刻失去符號；分別估計又恢復 `log t` 背景。
所以此法不能產生 L16所需第一個 fixed `theta<1`，除非先有新的 harmonic-zero
global correlation inequality。

## G165. Selberg Riccati在任意 zero exponent上局部中性

PG9 對 multiplicity m 的 zero比較 Laurent主部：`-L'+L^2` 與
`zeta''/zeta` 都是 `m(m-1)/(s-rho)^2+O((s-rho)^-1)`。此消去不依賴
`Re rho`，所以 classical Selberg identity沒有 `theta -> Phi(theta)<theta` 的
spectral damping。把 RHS估成 `mu*log^2` 又引入 `1/zeta` poles。故 AP11、AP14、
Green、Pick 等 detectors不能靠 Selberg algebra互相證明；需要新的 signed-Moebius
estimate或 reflected square。

## G166. natural reflected-Moebius square的 critical continuation仍 exact等價 RH

PG10：`|1/zeta(s)|^2` 在 `sigma>1` 給 mu coefficients的真正 all-size Toeplitz
PSD form；但要求 damped norm在每個 fixed `sigma>1/2` 可積，off-line zero所在
直線立即出現不可積 pole，故 exact等價 RH。averaged Chowla控制 additive
shifts/origins，不是 fixed Mellin line；Ng的 Mertens distribution結果在 RH外還需
negative-moment輸入。現有 signed-Moebius theorem不能補 G165。

## G167. `p<1` Hardy closure趨近的是 `Re s=1`，不是 critical half-plane

PG11/ES140：外部 cross-space inverse要求 `q<p/(1+p)`；`q->1-` 時 source p趨無窮，
且 evaluation範圍始終只有 `Re s>1/q>1`。所以其 constants即使最佳化也只回到 PNT
boundary，不能與 PG10 fixed-line pole integrability的 p混用，更不能插值至 H2/RH。

## G168. Nyman Cholesky全正猜想即使成立也不推出 closure

`nyman_cholesky_positivity_audit.md`：arXiv:2011.02847 Conjecture 9 是真正
all-size bordered determinant/Cholesky positivity。但 NC2 構造
`H=ell2 direct-sum Ru`、strictly positive lower-triangular L與 positive RHS，使全部
Cholesky entries正而 target仍有 u正交殘差。故全正本身不推出 `d_n->0`；尚需
`sum|(L^-1F)_j|^2=1`，這正是 Nyman/RH endpoint。

## G169. Nyman固定欄漸近落在不連續 Mellin boundary

L18/NC3 證 remote vector `A=L^-1((k-1)/k)` 正是 `s=0` Mellin residue在
orthonormal basis的座標，而且 `A notin ell2`。因此 conjectural `A_j>=0`
不給 bounded positive functional，也不能用 Hilbert duality控制
`E=L^-1(log k/k)`。缺的不是再證更多 `L_kj>0`，而是 full arithmetic Gram核的
uniform row-tail theorem。

## G170. 特殊右端、remote law與 vanishing row norms合起來仍不足

NC4 給 exact Hilbert countermodel，同時滿足 strict positive Cholesky、
`LA=(k-1)/k`、`LE=log(k)/k`、`E_j>0`、每固定欄
`2L_kj/F_k->A_j` 以及 `||f_k||->0`，但 `||E||_2<1` 且 target仍有正交殘差。
所以 Nyman路線剩餘合格輸入只能是餘數／整除／Möbius full kernel的 uniform
定量估計；上述資料包本身已有反例。

## G171. Ehm q=2 Gram smoothing仍留下 RH-equivalent inversion error

arXiv:2405.06349 的 `q=2` 權重雖比標準 Nyman多兩次頻率衰減，其 closure仍 iff RH。
quadratic decomposition中一個明確未估項是 truncated Möbius inversion error
`E_a^(q)(N)`；作者稱它為 major challenge並擱置。其餘 centered Mertens/Landau
products也只由 empirical correlation支持，尚無 negligible theorem。故不能以更強
Sobolev damping避開 critical closure。

## G172. Ehm inversion tail的固定比例 boundary禁止 absolute estimates

L19/NC5.2--5.3 證 `S_q` 在某固定 ratio window離零，而 square-free pairs有正密度；
因此 Möbius tail取絕對值後，裸係數為 `Omega(N)`，Levinson--Selberg outer weight仍為
`Omega(N/log N)`。`q=2` 只改善 `n/m->infinity`，對 `n/m=Theta(1)` 無效。下一個
合格 theorem必須是 signed two-variable Möbius correlation或與 `(a-mu)` 項的 exact
recombination；triangle inequality、逐 dyadic block Cauchy與 kernel pointwise decay關閉。

## G173. 現有 cotangent--Möbius fixed-power saving只在 far-ratio區

Maier--Rassias arXiv:1806.05070 Theorem 2.1 對相關 Wilton/cotangent kernel證
`sum_(k^D<=n<2k^D)mu(n)g(n/k) << k^(D-z0+epsilon)`，但明定 `D>=2`。
這是實質 cancellation，卻只觸及 `n>=k^2`；Ehm缺口的主要 box是 `n,k asymp N`。
而且 `g` 與 `S_q` 尚需 integral transfer。未找到 `D=1` primary theorem，故此外部
輸入不能補 G172，只可能處理 remote tail。

## G174. Ehm reciprocity保持 same-scale，不能把 G172送到 far-ratio

Corollary 3.1 為 `S_q(1/r)=rS_q(r)+P_q(r,log r)`。所以 compact fixed-ratio
window只映到另一 fixed-ratio window；`n/m=Theta(1)` 不會變成 `n>=m^2`。
初等 `P_q` 代回後正產生 paper已列出的 Landau/Mertens products，而它們也未證
negligible。故 reciprocity本身不是 Maier--Rassias `D>=2` theorem到 `D=1` 的橋。

## G175. Ehm全部 moving pieces重組後就是 critical Nyman norm

NC5.6--5.7 將 full Gram精確對角化為
`int |zeta(s) sum_(n<=N)a_n n^-s|^2 |ds|/|s|^(2q)`。因此若同時證 inversion
tail與 centered Landau/Mertens products達到所需極限，正是 explicit mollifier的
critical closure，而非 positivity/reciprocity自動給的較弱 lemma。新算術 theorem
仍須在不使用 `1/zeta` critical continuation下直接處理 G172 same-scale cancellation。

## G176. moving-boundary 的精確門檻是 signed `o(N log N)`

NS1把 `m<N<n` 固定比例 dyadic box精確寫成
`T_(q,N)=B_(q,N)/(N log N)`，其中
`B_(q,N)=sum mu(m)mu(n)W_q(m/N,n/N)`。因此單獨消去此 tail需要
`B=o(N log N)`。absolute sum與 generic Mellin Cauchy/large-sieve都只給
`T=O(N/log N)`；`q=2`遠端 decay不改變此門檻。

## G177. averaged Chowla 丟掉了跨 shift 的必要 cancellation

寫 `h=n-m` 後有 `asymp N` 個 shifts。即使每一 shift都有 conjectural
`O(sqrt N)` correlation，取絕對值相加仍為 `N^(3/2)>>N log N`。MRT 的
`sum_h|correlation_h|=o(HX)` 在 `H=X=N` 只給 `o(N^2)`，且其 absolute value
消去 `h` 間符號。所需新 theorem必須是完整二維 signed sum。

## G178. Mellin separation 顯示 generic large-value 工具尺度不足

NS2把 dyadic box精確分成 adjacent Möbius Dirichlet polynomials `A_N(t)C_N(t)`。
Guth--Maynard改善的是 generic polynomial在 `N^(3/4)` 附近的大值計數；本題需要
Möbius-specific near-square-root或同強度的 integrated signed product。zero-density
仍容許 exceptional off-line zeros，沒有導出 G176。

## G179. generic all-smooth 修補本身已是 RH

L20/NS6：若 G176 的 `o(N log N)` 對所有 smooth kernels成立，取 rank-one kernel
即得 smooth Mertens `O_epsilon(N^(1/2+epsilon))`，從而 RH。故只剩 kernel-specific
identity有可能是較弱的 upstream lemma；但把 Ehm所有 pieces exact重組又回到
G175 的 critical Nyman norm。這就是該支線目前的邏輯斷層。

## G180. single-kernel 問題必須區分 fixed cutoff 與 uniform cutoff

SK1--SK3回應 Selberg nudge。對完整 Wiener cutoff algebra具一致量詞時，可由 local
Wiener inversion除掉 nonvanishing `S_q`，same-block版遂恢復 rank-one Mertens square
並蘊含 RH。natural moving tail只有一個 separated-cutoff scalar，無此 implication；
superlacunary coefficient countermodel嚴格排除 coefficient-generic捷徑。

## G181. natural Levinson error是雙 logarithmic Cesaro，但沒有額外正性

SK4.1--SK4.2將 inner與outer `log(N/n)` 權重完整寫成兩次 `du/u` averaging。這保留
所有符號，可作 proof interface；但 averaging沒有自動產生平方或 operator contraction。

## G182. divisor identity factory在 `u<j<=2u` 精確退回 Möbius pair

SK5/L22：truncated divisor coefficient `d_u(j)` 在首個 moving band等於 `-mu(j)`。
因此 Ramaré--Zuniga identity factory雖是 all-scale algebra，無法把主要 same-scale box
變成 prime positivity；其現有 estimates又明確保留 `m_q(t)` absolute integral或限於
`sigma>=1`。此線不補 NS1.3。

## G183. critical local moments的 source degree map（由 G185 強化）

arXiv:2607.25002 的一次估計給 fixed `q` loss `1/[2(q+1)]`，source用 unbounded `q`
達 RH。G185/VA4證明這不是最小量詞：同一 `q` 的 derivative feedback可迭代，故只需
q=2 quadratic。高階 sinc Gram hierarchy仍正確，但不再是 live最小 target。

## G184. local Orlicz target是單一 all-degree正不等式，但仍等價 RH

LM3/L23 的 critical-arc exponential moment一次控制所有 `q`，並與 RH等價。global
Parseval只給 `q=2`；Davenport的任意 log-power saving與 averaged Chowla都未給
`N^eta` local high moments。只有直接的 deterministic Möbius subgaussian mechanism
才算此路進展，random-sign heuristic不算證明。

## G185. unbounded moment degree不是必要；fixed `q` 有 exponent bootstrap

VA2--VA4/L24修正 G183的強度判讀。source的 `1/[2(q+1)]` 是第一次套 derivative
bound的 loss；所得 Mertens improvement會把 rescaled polynomial derivative從 trivial
`N^(1/2)` 改為 `N^delta`，再用同一 `q` 得 strict map
`delta->delta/(q+1)`。所以 `q=2` quadratic criterion已 iff RH，不需高 degree。

## G186. 新最小 quadratic target仍缺 power-to-subpower producer

RH等價於每個 `epsilon>0`

```text
1/N sum_(m,n<=N)mu(m)mu(n)sinc(2pi c(m-n)/N)=O_epsilon(N^epsilon).
```

MRT averaged Chowla只使此 form至多 `o(N)`（quantitative僅 log gain），Davenport也只
給 `N/log^A N` 型 normalized square；兩者 power exponent仍為 1。L24能迭代 Mertens
exponent，不能把這個 quadratic form的固定 power loss自行消掉。

## G187. Orlicz entropy dual與 Ehm divisor kernel幾何不相容

VA6--VA7/L25：dual densities產生 additive-difference Toeplitz kernels；SK5.2保留的是
multiplicative-ratio `R_q(j/m)`。把 `d_u`平方可得到一個 nonnegative density，但只為
supremum提供 lower witness且引入 fourth correlations。故 Selberg nudge的直接 dual
certificate測試為 negative；若要橋接必須先有 exact ratio-to-additive transmutation。

## G188. Selberg nudge的 uniform-loss疑慮已由有限迭代量詞解除

LQ1/L26把 `P(delta)=>P(delta/(q+1))` 的 epsilon選擇寫明。任意最終 epsilon只用有限
步，常數不需 uniform in delta；所以 fixed-q equivalence仍成立。此項不是新 RH缺口。

## G189. prolate/Legendre正性只移除高模態，低模態仍缺 square-root cancellation

LQ2--LQ3/L27給 exact all-rank PSD decomposition。超指數 eigenvalue decay可控制
`J~logN/loglogN` 後的 tail，但 `k=0` 已是 fixed smooth Mertens sum。PNT級
`N exp(-o(logN))` square仍遠大於 `N^o(1)`；需要 joint low-mode arithmetic theorem。

## G190. `mu log` multiscale的表面 `1/logN` gain被窄 arc normalization吃掉

LQ4/L28：若只知 fixed-c energy，`Q_(cy)<=Q_c/y` 恰抵消 integrand的 `sqrt y`，
無 strict contraction。若假設所有窄 arc envelope，`c'->0` 又直接包含 Mertens/RH。

## G191. Lambert all-scale identity在 critical normalization精確退回 zeta symbol

LQ5/L29 的 dilation weights為 `k^-1/2`，絕對與平方和皆發散；Mellin-scale symbol為
`zeta(s+1/2)`。因此 uniform inverse會循環到 reciprocal-zeta obstacle。尚未排除的
窄路是利用 RHS special forcing與 Gamma damping建立只允許 critical oscillatory modes的 theorem。

## G192. 第一個 positive spectral mode已獨立承載 RH

LQ2.1/L30證 `w(x)=sin x/x` 的 Mellin transform在 `Re s>0` 無零，故
`sum mu(n)w(n/N)=N^(1/2+o(1))` iff RH。prolate/Legendre截尾沒有把問題降到一組
較弱 low modes；最底 mode已是完整 reciprocal-zeta detector。

## G193. Lambert special forcing的 Gamma numerator不消任何 nontrivial zero

LQ5.1/L31把尺度 transform寫成 `Gamma(r+1/2)/zeta(r+1/2)`。Gamma無零，
所以 special RHS與 functional equation不提供 off-line pole cancellation。G191所留的
special-forcing窄路關閉；除非有獨立 pole-location/正能量 theorem。

## G194. fixed-q degree斷層已有無迭代的 positive Volterra closure

LQ2.2/L32：critical local mean是 sinc-smoothed Mertens sum；因 sinc weight在選定小 arc
上遞減且 endpoint值大於 `1/2`，其 Abel--Volterra operator在 supremum norm有顯式
positive inverse constant `(2sin1-1)^-1`。所以任一 q的 local subpower norm一步給 RH，
完全避開 uniform iteration疑慮。未閉合處只剩如何無條件證該 scalar/local norm。

## G195. compact sinc的 Müntz inverse在 `x=1/N`逐字等於 target

SM1/L34：dilation-zeta operator的 source為 `sum mu(k)f(kx)`，Mellin symbol
`W/zeta`；zero-free `W`不消任何 off-line zero。這條 factorization是等價座標，不是 producer。

## G196. sign-definite Müntz generator的 positive cone被共同 tail排除

SM2--SM3/L35：雖有 `-Pf>=0`，所有 dilations在 infinity共享 `I/(kx)` tail。
非負係數若消 tail即在任意 compact away from zero消失，不能逼近 `f`。必須使用 signed
coefficients，故全域正性沒有關閉 parity gap。

## G197. bandlimited sampling全正能量就是 weak-Mertens energy

SM4/L33：所有 integer samples的平方和精確等於
`pi N[M(N)^2/N+sum M(n)^2/(n(n+1))]`。已知 PNT只給 exponent仍為 2 的
subexponential saving；weak Mertens log bound是未證假設，不能代入。

## G198. sinc dilation顯式式只給 non-ell2 boundary reconstruction

SM5的 `M/2=sum(-1)^(r+1)A_r` 是 bandlimit在 frequency `1/2` 的 Poisson零值；
coefficient sequence不在 `ell2`，Abel regularization的 norm發散。故無 coercive isolation。

## G199. signed sinc closure的 exact error仍是 Nyman mollifier norm

SC1/L36：Mellin error為 `W(s)(1+zeta(s)C(s))`，tail另要求 `C(1)->0`。
W無零，故沒有 kernel zero可遮蔽 off-line zeros；這不是較弱 optimization。

## G200. bounded synthesis projector被 critical zeros嚴格排除

SC3/L37：若 `sum|c_k|/sqrt k` bounded，任一已知 critical zero附近 error保留固定
L2 mass。closure迫使該 norm發散；因此「bounded-norm隔離 A_1」不是 live機制。

## G201. Selberg nudge揭示 smaller-scale recursion但沒有 contraction

SC5/L38：indicator座標是 `M(floorN/k)`；sinc座標是 `A_w(N/k)`。normalized recursion
的 `k^-1/2` weights臨界發散，必須先控制所有小尺度同一 target，沒有 inductive gain。

## G202. Nyman distance lower bounds與 Gram compression都不給 upper closure

Burnol只證 zero-forced `1/sqrt(log scale)` lower bound；Báez-Duarte explicit decay假設 RH；
arXiv:2510.18132只證 smoothed Gram off-diagonal decay。三者均不補 SC1.1 的無條件 upper bound。

## G203. Laguerre block的 basis端已 uniform，缺口是 prime-centered quadrature

LB3/L39把 `a_n` 寫成 `Q_n=e^-t(L_n-L_(n-1))` 對
`d[Pi(e^t)-Li(e^t)]` 的 pairing；block energy是此 signed functional在移動
Laguerre subspace上的 dual norm。difference family的 Riesz loss只有 `H^2`，Temme/
Frenzen--Wong/Vanlessen亦已給全區 uniform asymptotics。故「degree升高造成 basis
失控」不是缺口。真正未證的是 LB8.1 的 `exp(o(N))` centered quadrature estimate。

## G204. 成熟 MZ/large-sieve theorem的節點假設不適配 prime logs

Lubinsky--Mate--Nevai 型 polynomial large sieve以自然尺度上 well-spaced nodes和
positive sampling weights為輸入；Laguerre尺度要求 t-spacing為常數階，而 `log p`
spacing趨零。Christoffel/Gauss-node theorem亦不接受 prime weights。即使使用 positive
Carleson embedding，取 total variation會刪除 discrete--continuous主項 cancellation；
用 cumulative discrepancy又回到 PNT envelope的超線性 tail saddle。現有相鄰定理
不能直接代入，且沒有偷渡 RH；缺的是新的 arithmetic signed embedding theorem。

## G205. controlled signed projector的斷層是 quantitative completeness cost

SC7/L40證 fixed window內 tail-exact Dirichlet polynomials無條件可使
`1+zeta C`任意小；local existence不是缺口。可是 Paley--Wiener zero-density證明不給
coefficient norm。由 sinc cutoff的 `W=O(1/t)` 與 zeta 經典二次矩，global tail可改進為
`O(T^-1+K^2logT/T)`；合格 projector只需 `K^2logT/T->0`，特別是任意
`K=o(T^alpha),alpha<1/2`。尚無此 quantitative nonharmonic approximation upper bound。
L37只排除 K bounded，與此 live target不衝突。

## G206. 現有 moment-method biorthogonal estimates排除超密 log spectrum

SC9/ES156：standard與 no-gap controllability theorem仍假設 asymptotic gap、power-law
spectral counting或 bounded condensation cardinal。`{log k}` 的 counting為 exponential，
任意固定尺度的 cluster cardinal無界；現有 norm upper bounds不能代入。這不證 kappa
必超過 `T^alpha`，只表示需專為超密 one-sided frequencies及特殊 target設計的 theorem。

## G207. 長 mollifier 下界不轉成 controlled-projector 上界

SC11/ES157：Radziwill 對長度 `N=T^theta` 的 normalized mollifier residual給
`>=c/theta`，但本問題在 `[T,2T]` 的 weight約 `T^-2`，故只留下約
`c/(Ttheta)` 的 shell mass；而 K不控制最大 support N。定理另有 normalization與
coefficient hypotheses，亦不是 kappa class自動滿足。它既不能產生 SC10.5 的 upper
bound，也不能排除任意 support的 controlled projector。Selberg nudge的斷層因此仍在：
獨立均值性質只改善 global tail，local kappa控制尚等價於原 closure義務。

## G208. coordinate envelope不等於 window-uniform norm cost

SC12/ES158：Andersson--Pechersky density允許選
`|c_n|<=n^(-1/2+1/loglog n)`，使截至 support N 的 K只有 `N^o(1)`，且 exact tail
修正 bounded。這是比 SC7更強的 coefficient結構；但 theorem不估為了 window T、誤差
delta所需的 N。沒有 `N(T,delta)` 上界，就不能把 `N^o(1)`轉成
`K^2logT/T->0`。缺口由「單係數大小」精確縮成「有效 support complexity」，仍未閉合。

## G209. coefficient ell2小不控制超密 log-frequency clusters

SC13/L42：遠端 consecutive block可有 ell2 norm趨零、K約 1，卻因
`log(N+j)-logN=O(M/N)` 而在任意固定 shell保持相干、產生固定正能量；exact tail
constraint只需一個 `O(N^-1/2)` constant修正。故 GCD spectral norm或 twisted second
moment若沒有 length/spacing條件，不能作 support-free tail theorem。live版本必控制
每個 log-scale cluster的 signed mass，不能只控制全域 ell2。

## G210. reciprocal regularity不可由 PNT餘項搬到 critical line

SC14依 Selberg nudge稽核：regularized `1/zeta` 的 derivative/analytic strip常數隨
critical/off-line zeros退化。PNT zero-free-region餘項只在 Re s近 1給資訊，不能證
uniform-in-regularization 的 critical-line coefficient decay。若新 theorem的假設含此
regularity，須標記為 zero exclusion循環。

## G211. cluster-aware tail已改善，但 Pechersky沒有 cluster-cost rate

SC15/L43把 global tail充分條件改善為 `K B_T log^2T/T->0`，其中 B_T是 log-frequency
寬 `1/T` bins的 ell2-of-ell1 mass。SC12 coordinate envelope確給
`B_T^2<<1+T^-1 N^o(1)`，所以相較 K-square門檻可多取得約 `T^(1/4)` 空間。
然而 Andersson theorem仍不限制完成指定 local target時的 N，也不直接保證實際選取
coefficients的 `K B_T` rate。最小 live輸出現在可二選一：有效 N(T,delta)，或直接
tail-exact Pechersky construction的 cluster-product bound。

## G212. tail smoothing已吸收所有固定 polynomial，但未證 local cost polynomial

SC16/L44提供 zero-free beta kernel的 all-order ladder：任意 fixed m把 K-square tail
分母提升至 `T^(2m+1)`。所以 sinc的 `T^(1/2)`門檻不再是 signed route的本質斷層；
若 local projector有任何有限 polynomial exponent，整條路即可閉合。現有
Andersson--Pechersky theorem卻完全沒有 window/support rate，不能推出 polynomial cost。
由 `W_m/W_m0` 的 bounded rational multiplier，同一 coefficients可從 m0升到任意較大
fixed m，故量詞不循環。下一外部 theorem的最小驗收標準因此降為：對某 fixed beta
kernel證 `kappa_m(T,delta(T))<=T^A`，A只需有限；不得只證 `N^o(1)` as a function
of support。

## G213. target-change nudge已解，但 polynomial-cost缺口原封不動

對同一 finite C，beta family滿足

```text
Ehat_(m,C)=W_m(1+zeta C)=(W_m/W_(m_0))Ehat_(m_0,C).
```

`W_m/W_(m_0)` 在 critical line bounded，故同一 coefficients的 window-local weighted
error確可從 `m_0`轉移到任意 fixed `m>=m_0`，且 `C(1)=0`不變。最新 nudge所警告的
generic target-change問題在此由 exact common-residual identity排除。這只驗證升階，沒有
產生 coefficients；核心缺口仍是無條件證某 fixed `m_0`、finite A、`delta(T)->0`及
tail-exact `C_T` 使

```text
||W_(m_0)(1+zeta C_T)||_L2(|t|<=T)<=delta(T),
K(C_T)<=T^A
```

或 `K B_T<=T^A`。若證得即推出 RH；假設 critical-line `1/zeta` regularity、Mertens臨界
界或 off-line zero exclusion的輸入均屬循環。

## 2026-08-16 階段缺口清單（canonical）

1. 最新最小缺口是 G213：任意 finite polynomial-in-window local coefficient-cost upper。
2. 存活入口是量化 Andersson--Pechersky support complexity，或直接控制實際 coefficients
   的 `K B_T`；兩者都必須給 window T的 rate。
3. 已淘汰機制：bounded norm、support-free ell2/GCD、reciprocal regularity、critical
   smaller-scale recursion；未淘汰 controlled unbounded norm。
4. 已停線：ordinary-Laguerre一般 block/asymptotics/frame theorem、SK5.2 Orlicz、
   Lambert/sinc遞迴；只有可直接填 prime-centered quadrature或 G213的新定理才重開。
5. qualitative density、RH-equivalent closure與 L45 conditional implication都不是 G213的
   證明。RH尚未證明；本階段停止續攻。

## G214. Andersson--Pechersky stopping-rate抽取失敗於量詞交換

`andersson_pechersky_rate_audit.md` / L46 已核對 arXiv:1207.4624 source。Pechersky
輸入只給每個 fixed direction的 pairing series發散；任意 finite prefix在
infinite-dimensional `L2` 中都有共同正交 unit direction，因此不存在由該輸入推出的
uniform finite-prefix coercivity。source的 Hadamard/zero-count常數亦依 fixed direction，
classical specialization的明示起點對 H已極大，仍沒有 stopping rule。arXiv:1207.5337
只 explicitize non-vanishing lower bounds，不補 approximation support rate。

這關閉的是 Andersson proof作為 G213 producer，不是 G213命題。下一最小缺口改成
L46.1/AP2.5 的 target-specific dual inequality：對 `y_m=W_m` 與
`a_(m,n)=W_m zeta(n^-s-n^-1)` 證 polynomial K的 norming bound。它保留 moving
extremizer的正確量詞；若只證 fixed f的 divergence，仍不合格。

## G215. real-Sobolev / two-sided Fourier producer被 one-sided Hardy反例排除

L47/AP4.1對最簡 target `exp(i omega t)`給明示 Poisson lower bound：負頻 H-infinity
多項式若 coefficient mass `K<=T^A`，在 `[-T,T]` 的 absolute L2誤差不可能趨零。
所以即使 regularized `-1/zeta` 的實軸 derivatives可用 epsilon負冪與 zeta convexity作
polynomial控制，也不能先作 two-sided Fourier近似再無代價轉成 `-log n` frequencies。

G213/Handoff-2仍未被反證；但下一 producer必須使用 `-1/zeta(1/2+iz)` 的特殊
lower-half-plane算術解析結構。只列 Sobolev norm、Jackson theorem或 generic
superoscillation density均不合格。

## G216. 首零點距離不是 exponential no-go

L48把數值惡化拆出嚴格局部部分。對 multiplicity-r zero、端點距離 d與 local error
delta，任何 approximant只被強迫 `K>=c(d+C delta^2)^(-r)`。所以零點局部形狀與
fixed beta weight只給 polynomial lower bound；不能由 T約14附近的 ridge plateau宣稱
Handoff-2需 exponential cost。尚未閉合的是跨全部頻率的 one-sided arithmetic
interpolation，而非單零點 neighborhood。

## G217. MB1：明示 polynomial Möbius mollifier的 weighted critical mean

下一缺口不再寫成抽象「global interpolation」。L49/AP5固定 logarithmic Riesz weight，
`X=T^B`、`C_X=M_X(1)-M_X(s)`；它 exact滿足 `C_X(1)=0` 且
`K(C_X)<<T^(B/2)+logT`。唯一未證式是 fixed `m,k,B`（`2m+1>B`）及某
`T_j->infinity` 上的 MB1 weighted L2極限。

MB1若真即由 SC16 tail推出 RH；目前 PNT、standard mollifier shell theorem、local zero
lower bound均不證也不反證。下一步必須直接展開 `1-zeta M_X+a_X zeta` 的 signed
divisor coefficients或取得等價 weighted mean identity；只換平滑權或做 finite numerics
不算閉合。

## G218. MB1 tail回到 moving same-scale Möbius gap

L51/AP7精確證 `y>X` omitted-divisor tail；在首 block `X<y<2X` 就是帶 fixed
`(logX)^(-k)` damping的 Möbius Riesz sum。PNT/Mertens zero-free-region bound經 partial
summation與平方積分後仍給不趨零的 `X exp(-2c(logX)^alpha)/(logX)^(2k)` 尺度。
所以 fixed Riesz smoothing不能把 absolute/PNT cancellation升到 MB1。

H項或可與 L50的 prime discrepancy及 Abel boundary消去，故未反證 MB1；但這個 explicit
producer沒有提供獨立於 NC5/L20 的新槓桿。唯一剩餘式是 AP7.2 全組合的近平方根 joint
cancellation，分項 triangle或 k隨X增長均不合格。

## G219. LB9.1 是不同 geometry，但 envelope/positivity producer有 exact反例

`laguerre_vs_mobius_block_audit.md` / L52證 ordinary-Laguerre blocks控制
`[z^n]log[(s-1)zeta(s)]`；reciprocal route由 exp/log Bell polynomials相連，會混合全部
低階，故 AP7不是 LB 的 linear same-block換座標。LB prime-linear geometry保留。

量詞已固定成 `H_N=ceil(log(N+2))` 的 LB9.1，仍 iff RH。L53以
`g_theta(t)=exp(theta t),1/2<theta<1` 構造 exact Laguerre exponential coefficients；此
模型同時滿足 PNT absolute envelope且可來自正 uncentered measure。因此 cumulative PNT、
positivity及只讀這些資料的 signed-Carleson theorem不能證 LB9.1。尚需 actual
prime-power nodes/weights的 correlation；一般 measure theorem已排除。

## G220. LB9.2 已化為 finite prime log-moment joint norm

L54/L55把核心式完全顯式化：prime cutoff Y下，LB block energy是 CD kernel的
prime-prime、prime-continuum、continuum-continuum完整 centered square；亦等於 centered
log moments `R_0(Y),...,R_(N+H-1)(Y)` 經 associated-Laguerre binomial matrix後的
`sum|U_n|^2/n^2`。

隱藏量詞是先選 N再令 Y趨無限；fixed-N PNT moment convergence不給 uniform-in-N
subexponential constant。逐 moment或三個 CD terms分開估會被 binomial fixed-base condition
放大並刪掉 centering。下一唯一 producer是能直接控制此 joint metric的 prime-power
correlation；Selberg convolution若只產生 analytic powers而沒有 square sign仍不合格。

## G221. Selberg全階升階被 exact kernel geometry排除為 LB9 producer

L56/LM8--LM9把「analytic square無 conjugation」升成有限代數證明。Selberg與全部
`Lambda_k` recursion對 centered prime measure的二次核只能是 `h(t+u)`；LB9的
associated-Laguerre核不是 Hankel，最高 bidegree即矛盾。故 one-leg Selberg substitution、
coefficient positivity或 higher-k induction不能產生所需 PSD。

這不反證 LB9.2；缺口收窄為 reflected two-variable prime correlation。下一步若只控制
per-prime diagonals再 triangle/Cauchy，仍會丟 cross-prime cancellation；合格輸入必須在
LM6.3 完整兩腿形成後使用 `Lambda(p^j)=log p` 的 single-channel結構。

## G222. 數值 quiet blocks 存活，但 finite range不能裁決 fixed positive exponent

L57與 results md：N到1000時 dyadic minima與 envelope整體下降但強烈振盪；兩個 Cauchy
半徑重算一致。這不是 RH證據。off-line rho映到
`|1-1/rho|^2=1-(2beta-1)/|rho|^2`，高 gamma可令正 exponential rate極小且 crossover
遠超計算範圍。另需避免量詞誤讀：LB要求 good blocks為 `exp(o(N))` upper，不要求可觀察
fixed negative exponential decay rate。

## G223. positive producer的 uniform參數與 local-Euler最小失敗點已固定

L58/LM11規定 coercivity必須 uniform於 block內所有 c及 eventual cutoff tail Y，lower constant
只允許 `exp(-o(N))`；可依 epsilon,N，不可逐 c或逐 Y-subsequence選擇。這補上先前只列排除
條件、未寫正下界參數的缺口。

LM12又把 `Lambda(p^j)=logp` exact總成每 prime local vector，但 per-prime PSD漏掉所有
cross-prime及 prime--continuum項；Cauchy的 prime-count損失隨 Y發散。因此 bare local rank-one
Euler law已失敗。核心義務現在是符合 LM11的 global cross-prime reflected/telescoping identity；
這不是再做 local Euler factor algebra可得到。

## G224. generic reflected convolution仍不是 LB9 的 exact geometry

L59證 J既非 `h(t+u)`亦非 `h(t-u)`。所以下一缺口不能泛稱「找 ratio square」；它必須是
moving Laguerre CD projector本身的 global centered prime quadrature，或對該 projector有
LM11規格的 subexponential coercive comparison。此結果關閉語言換名，不反證 LB9.2。

## G225. Euler--Bohr cross-prime正性在 LB topology 上有精確零空間

L60/LM14：單一 `R=(s-rho)/(s-a)` 在每條 `sigma>1` normalized vertical B2 seminorm為0，
但若 `Re rho>1/2>Re a`，Laguerre disk含 interior log singularity並有 fixed-exponential
blocks。因此 long-time mean-square、Bohr orthogonality與 random Euler L2均無 LM11正下界。
把 mean equality直接升成 critical-strip analytic equality會預先排除該 factor，是 hidden
zero-free transport。

## G226. 多個 producer 的共同失敗是 stationary quotienting

L61統一 L56/L59/L60：sum/difference convolution只見 stationary kernels，而 normalized
translation mean又 annihilate所有 localized L2 perturbations；LB moving projector則
nontranslation-invariant且對 finite meromorphic factors敏感。因此任何下一個 mean候選同樣
失敗，不再逐一測常數。唯一可能逃生口必須 anchored並保留 finite-height boundary/winding。

## G227. anchored逃生口 exact合流 W13--W14 residues

L62給 `D=K'` 的 Cauchy residue式。`r_N=1-N^-1/2` 對 degree N只付
`exp(O(sqrtN))`，但 s-contour已到距 critical line `asymp N^-1/2`、高度 `asymp sqrtN`，且
必須計入每個 `Re rho>1/2` residue `z_rho^-n`。故 residue-free finite-height estimate已是
RH；合格 identity只能在 contour shift前把 prime--arch boundary/residues exact配成正 form。
這與 W13/W14同一 obstruction，LB不再算獨立 anchored producer。

## G228. 「合流」只在 residue-empty量詞等價，不是 norm intertwiner

L63精確定義 A=每 epsilon有 unbounded LB good blocks、B=無 disk interior residues、
C=W12.4 all-test，並證 `A<=>B<=>C`。A=>B用 nearest shell syndetic excursions；B=>A由
Cauchy--Hadamard且給 all sufficiently large N；C=>B用 W14 localization；B=>C用 critical
zero squares。

A失敗的 witness是每個 remote fixed-length index interval中的大係數；C失敗的 witness是一個
orbit-localizing test。沒有已證的 block-to-Weil bounded map或 LM11 constant。故「合流」不
允許拿 W12.4當 LB producer；它只證兩個 endpoint透過 off-line residue集合為空邏輯等價。

## G229. DN nonlinear relative energy已閉合；theta initial rigidity仍缺

為回應「新義務須有獨立可證內容」，L64/DN15--DN17構造
`E_d=sum[y-log(1+y)]`。它是 finite-window uniform convex barrier，zero log-gas flow exact為其
negative gradient flow；非線性 gap barrier與 backward bootstrap均已嚴格證明，未使用 RH。

極端壓測顯示 exponent sharp於 checkerboard：高度 Gamma仍要求 initial energy
`exp[-(tau/2+o(1))log^2Gamma]`。故真正未閉合的不是 nonlinear collision functional，而是：
(i) 把 local constant clock換成 zeta varying clock並控制 buffer flux；(ii) 從 theta kernel對
每個高 block證上述超多項式 initial energy。pair correlation、mean energy與 polynomial clock
asymptotic不滿足全稱量詞。
## G230. naive varying clock已排除；exact co-moving theta approximation仍缺

L65/DN18--DN20 算出所有隱藏項。Frozen nonuniform clock帶 PV force `S^y`；`n` 點 arithmetic
hard cutoff 的 force norm為 `asymp sqrt(n)/d`。Moving clock另帶
`-<H_y y',x-y>`，affine dilation seminorm exact為
`|d'/d|sqrt(n(n-1)/2)`。兩者都不 uniform in degree。

唯一存活的無 forcing 版本是把 theta zeros 與同一 log-gas 的 exact reference solution比較；
其全域 `ell^2` 誤差仍須在每一高 block 達 `exp[-c log^2 Gamma]`。目前沒有此 theorem，亦未
證明它不可能；最小缺口是先選定 exact reference 與 particle range，再給含累積誤差的 bound。
## G231. Hermite reference與現有 positive-time asymptotic皆未閉合

DN21：Hermite zeros確為 exact finite co-moving log gas，但 `H_t` 是 infinite system；截取 block
立即帶回 `ell^2` size `sqrt(n)/d` 的 exterior PV field。全粒子比較又有 semicircle density 對
Riemann--von Mangoldt density的不相容，故最小失敗點是 finite/infinite interface。

DN22/ES164：Polymath all-high-zero theorem只有 `x^(-ct)` precision；barrier需
`exp[-C t log^2x]`。多步 reset 仍卡在 `t~1/logx` endpoint。下一個合格輸入必須是該端點以下
的 super-polynomial rigidity，或不同於 backward smoothness的 collision invariant。
## G232. smooth terminal collision counters由 exact checkerboard排除

L67/DN23 構造真 nonlinear collision trajectory，於正時間只留下
`exp[-pi^2t/d^2]` displacement。這不只是 Hessian worst mode，而是 barrier sharpness反例。
因此以 terminal spacing、任意與 clock局部 Lipschitz的 norm、或 `x^(-ct)` asymptotic建立
collision count皆失敗。存活 counter只可能是 topological/spectral-history invariant；P30
Pontryagin index屬此類，但既有 audit顯示其 projector convergence尚不存在。
## G233. margin量詞已修正；finite discriminant閉合而 entire transfer失敗

L68/DN24 修正 G232：exact checkerboard排除 fixed-margin或 margin較慢衰減的 stable detector，
不排除 signal本身以 `epsilon_d` 同速消失的非光滑 surrogate。後者的驗收必含 `o(m_d)` error。

L69/DN25 建立 exact finite polynomial spacetime discriminant及 Sturm collision counter。
DN26 的 monomial counterexample證 terminal local-uniform polynomial convergence不受 backward heat保持；
因此 resultants不能由 Taylor/Jensen cutoffs自動收斂。尚缺 theta-specific weighted entire topology與
canonical infinite resultant/Fredholm limit；若只從 collision set定義 regularization即循環。
## G234. spacetime winding存活；缺 uniform theta boundary homotopy

L70/DN27 避開 infinite resultant：`(H_t,H_t')` 的 rectangle Brouwer degree以同一負 orientation
計全部 collisions。它不受 smooth-terminal checkerboard直接反例，是真正 topological/history invariant。

但其 certification radius為 boundary上 `sqrt(H_t^2+H_t'^2)` 的 minimum，仍可指數小。
DN28顯示 expanding rectangle的 winding等價 top/bottom real-zero count差（另含 vertical flux）。
下一缺口只接受 theta integral直接給 boundary nonvanishing homotopy與 margin；若重述
`H_0+iH_0'` phase或假設 bottom winding，即為 RH real-zero count改寫。
## G235. generic kernel structure排除；bottom signed theta phase仍缺

L71/DN29 證 positive even smooth rapidly-decaying heat kernel仍可 regular collision，故不能從
`Phi>0` 或 Fourier smoothing取得 L70 winding zero。DN30把 bottom field exact寫成 signed transform
`(1-u)Phi(u)`，亦即 critical line上的 `[2xi-xi']/16`。下一 theorem必須保留 prime log-derivative；
gamma-only phase、positive measure或 shifted finite-degree Laguerre inequalities皆不合格。
## G236. degenerate-collision ledger已閉合

L72/DN31 以 parabolic Hermite blow-up取代 DN27 的 genericity假設：multiplicity m collision的
local degree為 `-floor(m/2)`。nontrivial analytic heat solution的 multiple-zero set在 compact中離散，
故 total winding是所有退化事件的非負 pair multiplicities總和。topological counter不再漏
`H_xx=0` 事件；剩餘缺口仍純粹是 DN30 arithmetic boundary phase，而非 collision regularity。
## G237. natural boundary-phase producers已關閉

L73/DN32 以 rigorous Arb sign balls否決 actual Xi的 fixed-sign vertical phase velocity。
DN33/ES166顯示 horizontal phase的 first Laguerre inequality一般不充分；補全 extended inequalities
即回到既有 all-degree RH obligation。故 DN27 topological ledger雖嚴格成立，現無獨立 producer可算
其 expanding-rectangle winding。任意 nonmonotone homotopy若直接指定 bottom winding，便是 real-zero
count改寫。

## G238. DN26是錯 topology 的 no-go；Fourier graph transfer其實閉合

L74/DN34用 terminal theta Fourier measure構造 positive symmetric finite quadratures，並在每個
fixed spacetime rectangle取得 `(H,H_x)` 的 `C^1` 收斂。backward multiplier
`e^(-(T-t)u^2)` 是 contraction；只需 terminal measure的前三 moments。因此 high-degree
monomial反例不排除此 topology，entire degree transfer不再是 live gap。

仍不可交換量詞：先固定 boundary-nonzero rectangle R，才有 `mu_R>0`，再把 quadrature error
壓到 `o(mu_R)`。DN23容許 margin為 log-squared exponential；所以本結果沒有提供 uniform-in-X
cutoff，也沒有自行計出 winding。

## G239. 三條殘餘路線的共同支柱是 arithmetic zero-degree，不是 convergence

L75/DN35把 commensurate rational quadrature化為 `(r,e^(iy))` 的 Laurent polynomial；相容
rectangle的 boundary winding可由 exact Cauchy index/Sturm chains決定。故 finite decision、
entire transfer與 arbitrary nonmonotone homotopy不再是三個獨立缺口：共同未證項是從 actual
theta/prime weights對 expanding exhaustion證這些 degrees全為0。

若直接在 `t=0` 假設 unperturbed positive margin，便預設所有 critical-line zeros simple，強於RH；
須改用 regular `tau_n>0` 或 DN27 perturbation。另 DN29的 positive rational two-frequency collision
證 positivity/evenness與 algebraic decidability不決定 degree值。

## G240. common pillar沒有降低未知範圍：zero-degree exhaustion iff RH

L76/DN36證 regular `tau_n downarrow0` expanding rectangles全部 degree為0恰等價RH。同號 local
degree給 `zero degree => no collision`；DN22在每個 positive-time strip供 uniform real high-zero
exterior，排除 zeros從無窮遠進入；real-rooted positive-time functions的 locally-uniform limit給
RH。反向由 de Bruijn preservation與 DN31 Hermite local model成立。

因此三路合流只閉合 representation/convergence/finite-decision，不產生嚴格弱於RH的中介 lemma。
目前最小失敗點是：DN29、DN32、DN33後沒有 theta-specific signed producer可證這個 endpoint。
此路線不再以「nonmonotone homotopy可能存在」當進展；須有新 arithmetic identity才可重開。

## G241. AP2.5的 polynomial window是可重參數化的 RH 等價條件

L77/AP8/SC17修正 G214--G216 後續索引。SC8/SC10其實早已寫出反向：RH下先取任意 finite
global closure approximants，再把 T選得遠大於其 finite cost，即可滿足任意 fixed polynomial
`K<=T^A`與 local `delta(T)->0`。正向由 SC16.8 tail theorem推出RH。因此 AP2.5 iff RH。

最小失敗是量詞順序，不是尚待改善的 Pechersky常數：`approximant -> choose T` 使 polynomial-in-T
敘述失去同尺度內容。只有 explicit `C_T`、support與T的先驗 coupling，或 prescribed delta rate，
能阻止重參數化。MB1曾提供前者，但已由 L51回到 same-scale signed Möbius cancellation；不能把
抽象 AP2.5再當下一條獨立路線。

## G242. reparameterization-immunity成為所有 approximation routes的先行驗收

L78把 AP8抽象化：只要 local error受 global error支配，任何趨無窮 complexity allowance `g(T)`
都可在RH/global closure下由後選 T滿足。因此 polynomial、subexponential甚至指定任意慢增長的
free-window cost本身皆無獨立內容。

索引篩選結果：AP2/kappa類失敗此關；LB/W13與DN degree雖自然尺度固定，已由 L63/L76直接
等價RH；MB1是目前唯一明示 same-scale approximant，通過重參數化 filter，但其 producer已在
L51最小化為 signed Möbius joint cancellation，尚無獨立 inequality。canonical-system/all-test square
尚未定義可驗收 operator/domain，不能列為 active lemma。Goal因此保持 active，不宣稱路線窮盡。

## G243. L78不是 closure等價：prescribed rate是最小逃逸結構

L79的 `ell^2` truncation toy同時證 qualitative global closure與 free-window approximation，卻由
exact tail `E_N asymp N^-1/2`否決 `N<=T,E_N<=T^-1`。所以 reparameterization filter沒有把所有
定量 approximation route先驗判成 RH；它精確要求一個不可後選T消去的 rate或 same-scale law。

## G244. boundary gauge straightening只搬移 winding obstruction

L80/DN37證 extending orientation-preserving gauge不改 degree；若 boundary gauge把 phase拉直，
其不可延拓 index exact帶回原 winding。`sigma_min(A)`又顯示 ill-conditioned gauge直接損失 margin。
L81/DN38進一步證最自然 shear `(H,H_x+aH)`在 simple zeros的 vertical phase velocity invariant，
故 DN32反號無法由 gamma/log-derivative normalization修復。

這嚴格關閉 gauge-straightening作為 nonmonotone homotopy的獨立 producer，不關閉一個直接由 theta
arithmetic證明 nonvanishing的真正 homotopy。後者仍須提供新 structure，而不能只選座標。

## G245. first-mode theta homotopy base被 certified nonreal zero排除

L82/DN39的 Arb interval-Newton box嚴格含一個 simple nonreal zero。故 J14/J15 的 first-mode
saddle良性不等於其 Fourier transform屬LP；以 `T_1`作已知 zero-degree endpoint的 mode homotopy
在第一步就失敗。承重差異必須來自完整 arithmetic `log n` shifts，不能只用 envelope。

## G246. 第二 mode不是小 perturbation：amplitude path有 regular collision

L83/DN40對 `T_1+lambda T_2`證 `lambda*=0.91629...`、`x*=22.14237...` 的 regular double zero。
所以 direct mode-amplitude boundary homotopy確實穿過 `(H,H_x)=0`；這不是 margin估計太粗，
而是 actual two-mode obstruction。任何繞行 coefficient space的 nonmonotone path若要存活，須另證
它沒有被 collision hypersurface拓撲分隔，不能只追蹤同一直線。

## G247. modular cusp證所有 finite theta truncations皆非 LP

L84/DN41將有限掃描升為全N theorem。每個 finite partial kernel在0的右導數嚴格正；只有 infinite
modular sum令導數歸零。故其 cosine transform沿 real axis為 `-K_N'(0)/x^2+o(x^-2)`，real zeros
有限；order<=1 Hadamard factorization又強迫 total zeros無限，於是 nonreal zeros無限。

結論：非實 defects在每個 finite N都存在，只能隨 N向無窮遠逃逸。這嚴格關閉「有限 theta modes
先全實根、再 convergent transfer」整族，不關閉 DN34的一般 quadrature degree transfer，也不決定
full infinite kernel。下一可接受路線必須從一開始保留 exact modular completion。

## G248. finite coefficient detours亦全滅：LP cone與 finite theta span只交於0

L85/DN42用 `u->-infinity` 的 exact power expansion與 finite Vandermonde證：任意 nonzero finite
real theta combination必有某個 nonzero odd boundary jet。其 cosine transform遂有 fixed-sign
algebraic real tail、real zeros有限，而 order<=1迫使 nonreal zeros無限。

因此 G246 的 codimension-one collision wall不需逐路徑做 topology分類：有限 mode space中根本沒有
nonzero collision-free LP endpoint。繞開已證二模 collision只會把非實 defects移到其他高度。
唯一逃生必須是 genuinely infinite、在每一步已完成 modular boundary jets的 construction。

## G249. horizontal-shift infinite completion的 topological dichotomy

L86/HS12壓測第一個 measurable obligation：`(A_a,A_(a,x))` 的 collision orientation為
`-(1/2)partial_a(B_x^2)`，harmonic PDE不定號；單一 quadratic toy已有相反 orientations，故
不能無抵消計數。L87/HS13若改用 analytic pair `(A,B)`，orientation恢復全正，但 degree exact
成為 Xi zeros的 argument principle，expanding zero-degree iff RH。

因此 horizontal shift雖在每個參數都保留 infinite modular completion，仍無兼具「同號」與
「弱於直接 zero count」的 topological invariant。HS5 coupled Bezoutian identity仍邏輯可能，
但 topology本身沒有降低其 arithmetic positivity obligation。

## G250. HS5 coupled Bezoutian目前只有驗收格式，沒有候選 identity

L88/HS14證明，未指定 `T_a,L_a` 的存在敘述與 target `K_(a/2)>=0` 完全等價，因為
反向可取 `T_a=0,L_a=K_(a/2)`。所以「尋找 coupled arithmetic identity」不能本身算一個
未證 lemma；重開本線至少要先提供由已知 theta/prime data定義、且不使用 target positivity的
具體 operator/remainder。現有索引沒有此物件，HS5降級為 acceptance specification。

## G251. MB1的 T/B量詞無新增內容；global explicit family仍未裁決

L89/AP9證 `B<2m+1` 時 window complement自動 `o(1)`，所以 MB1 iff explicit global
Riesz--Möbius norm沿某 `X_j->infinity`消失。這不是 L78的 arbitrary-approximant scheduling：
coefficients仍由 X固定；但 T、B不再是 leverage。Burnol lower bound排除任何 power-rate版本。

定向核對 arXiv:math/0205003 與 math/0002254：同一 Selberg log weight早已被辨識；uniform
sawtooth convergence不足以控制端點 weighted L2，而 RH-alone對此 fixed family的反向 convergence
沒有在這些來源中證成。額外 Abel correction亦使舊結果不能直接套用。最小 gap仍為 AP7.2整個
prime/Abel/moving-Mobius signed square，不能拆項估計。

## G252. optimal-polynomial residue route隱含 simplicity，不能補 MB1 converse

L90/AP10核對 arXiv:1211.5191：其 `sum|zeta'(rho)|^-2` hypothesis在任一 multiple zero處即
失效，所以比 RH嚴格強，不能在量詞中省略。對 multiple zeros改用 higher Laurent residues只把
缺口升成所有相關 derivatives的 uniform control。故「RH下 optimal Selberg mollifier已收斂」不是
可用輸入；MB1仍須 separation-free地處理 AP7.2 whole square。

## G253. AP7.2的唯一 internal decomposition是無固定號的 log-scale correlation

L91/AP11證 fixed-log residual exact為 sharp Abel-corrected residuals的 log-Cesaro平均。
其 energy derivative由 `Re<A_L,Q_L>-||A_L||^2`決定，generic Hilbert geometry無符號；Jensen
上界則要求更強的 sharp-error average。故現在沒有可驗收的非文獻 producer。下一次重開必須先
提出 Möbius-specific cross-scale correlation identity/inequality，且其 proof不能使用 critical
`1/zeta`或 zero exclusion；否則只是 AP7.2換座標。

## Pólya geometric interpolation 的最小失敗點（已閉合）

`Phi_s=P^(1-s)Phi^s` 雖通過低階 Jensen screening，卻在
`s=0.0031021250408869274...`, `x=13.165805196244539...` 發生 certified regular
double zero。Arb Krawczyk image嚴格內含且 Jacobian排除0；`Hs,Hxx<0`決定 real pair向 nonreal
方向離開。故缺口不是提高 finite degree，而是缺一個從表示本身推出的 uniform
collision-exclusion identity；換 scalar interpolation law不算新路線。

## G254. A0 rank-one boundary change由低端 interlacing嚴格排除

若 Xi determinant來自 P3 core `A_0` 的 energy-independent rank-one self-adjoint boundary
condition，Sturm oscillation要求 target spectrum在每個 consecutive Dirichlet gap至多一點。
Arb certificate卻給 `beta_3<gamma_4<gamma_5<beta_4`，所以必要條件在第四、五 Xi zero即失敗。
尚存 gap不是再調 Robin parameter，而是明示 singular/infinite-rank domain或 independent arithmetic
operator，並證 positive domain、resolvent convergence及 divisor=spectrum；缺任一項都只是
Hilbert--Pólya existence改名。

## G255. fixed finite rank 的全域 counting obstruction（已閉合）

到 `T=1000` 的數值差仍在 `[0,2]`，所以 rank-two低端檢查不失敗；但 imaginary-order Bessel
phase給 `N_A0=M(T)+O(1)`，RvM給 `N_zeta=M(T)+S(T)+O(1)`，而 unconditional S-omega
使差值無界。fixed-rank resolvent/domain perturbation的 counting difference由 rank有界，故任何
固定有限 rank均不可能。尚存 obligation明確為 genuine singular/infinite-rank domain或 independent
operator的正 norm、closed resolvent、spectral projectors及 exact determinant identity。

此外 A0 energy gaps由 Bessel individual asymptotic趨無窮；bounded additive perturbation的 indexed
eigenvalue shifts由 operator norm一致控制，故其 high-energy counting差至多1，也與無界 discrepancy
矛盾。additive trace-class/Hilbert--Schmidt已包含在此 no-go；不可再以「small global potential」重開。

## G256. local prime scatterers的 forbidden `log(3/2)` orbit（已閉合）

單一 A0 channel在 `L_p=logp/2` 放 local self-adjoint scatterers雖能產生 boundary--p length
`logp`，但二點 determinant必含 `G_pq^2`。p=2,3遂產生 `log(3/2)` mixed length，短於
Euler最小 length `log2`且無可取消。分離 primes到獨立 channels又由 P9--P10 造成過大 Weyl
density。剩餘 gap因此不是調 couplings，而是構造一個 nonlocal arithmetic selection rule：禁止全部
distinct-prime paths、保留每個 prime的 repetitions，並維持單一 arch phase volume與 positive norm。

## G257. prime-only nonlocal positive projector保留 fixed `-1/2` drift（已閉合）

在 exact weighted interval model中，local Euler generator為 `A_p=-I/2+K_p`、`K_p` skew-adjoint。
任 direct sum、reducing positive subspace或 adjoint-compatible Hilbert cohomology都繼承
`A+A*=-I`，所以無法得到 critical-axis self-adjoint spectrum。把 generator平移 `+I/2`又會把
factor改成 `1-p^-x`。較大 conservative dilation不違反此結論，但 Euler divisor只成為 compression
resonance。尚存 gap須明示 singular arch--prime coupling，且新 norm不能只是 prime weighted norm的
subspace/quotient。

## G258. finite positive arch pairing沒有 infinite locally-finite limit（已閉合）

每個 finite prime cutoff都可用 explicit 2x2 positive metric消去 `+/-1/2` drift；但 p-th mode lattice
spacing為 `2pi/logp`。任 prime-dependent shift後仍有 eigenfrequency距0至多 `pi/logp`，所以
infinite sum在0無限累積、resolvent不 compact。這嚴格展示量詞錯序：逐 cutoff存在 positive metric
不提供 determinant-class limit。尚存 construction必須 cross-prime混合以摧毀 local lattices，並同時
滿足 G256 的 no-distinct-prime-orbit constraint。

## G259. positive cross-prime mixing與 exact Euler cumulants不相容（已閉合）

natural semigroup grading下，p--q off-diagonal block在 log determinant的 second cumulant產生
`||B_pq||_HS^2 e^(-slog(pq))`。Euler log對 distinct composite pq的係數exact為0；unique
factorization排除同長 cancellation。因此 positive determinant fidelity強迫 block diagonal，而 G258
又證 block diagonal infinite pairing不 locally finite。剩餘 gap只能在 non-trace-class、nonorthogonal
grading或非標準 length covariance中找 explicit construction；必須同時補 actual positive projectors，
不能只給 scalar continued determinant。

## G260. positive Euler determinant rigidity排除 nonorthogonal grading（已閉合）

對任 positive trace-class Dirichlet realization `K(s)=sum p^-sA_p`，exact Euler determinant的
p、p平方、pq coefficients依次強迫 `TrA_p=1`、`TrA_p^2=1`、`TrA_pA_q=0`。所以 A_p是互相
正交的 rank-one projections，模型唯一到 unitary equivalence。nonorthogonal feature space不能消除
G258 accumulation而保持 determinant。剩餘 gap只可能使用 signed/super或 non-trace-class
renormalization；必須另證 positive induced spectrum，不能從 scalar determinant繼承。

## G261. P21目前全部 explicit operatorizations已完成三分裁決

positive determinant、fermionic superdeterminant、Schatten regularization分別由 P44/P41--P43、
P22/P25、P31--P33到達 exact no-go。剩餘「singular cohomology」沒有 object/domain/norm，不能列
未閉 lemma。若未來重開，四項最低輸入是 positive completion、closed differential、self-adjoint
cohomology generator、以及 divisor真正等於 spectrum的 determinant theorem。

## G262. translation-compensated Hodge的 minimal two-prime obstruction（已閉合）

prime creation配 arch translation可 exact守恆 total energy並得到 scalar Hodge Laplacian。一個 prime的
`l2(Z)` model證明 dense domain、fixed weight與 compact resolvent可共存，故三條件不抽象互斥。
但第二個 distinct prime加入後，unitary shift covariance使任 eigenvalue orbit為
`lambda-Zlogp-Zlogq`；log ratio irrational使它稠密，與 locally finite spectrum矛盾。此失敗在
finite two-prime model已發生，早於 cutoff limit。

critical coefficients另令 infinite strong-sum domain不 dense，normalization則使 fixed prime weights
趨0。global unitary translation候選因此閉合。剩餘 gap只能明示 partial/nonunitary maps，並重新建立
dense closable differential、positive adjoint identity及 locally finite induced spectrum。

## G263. unilateral prime ladder的 Euler cancellation（已閉合）

partial/nonunitary repair已具體測試：backward boson shift給 dense closed complex與 locally finite
log-integer spectrum，避開 G262；但 compensator partition function exact為 `(1-p^-s)^-1`，消掉
fermionic `1-p^-s`。finite box的 `2^|P|` harmonic corners只產生
`product_p(1-p^(-(N+1)s))`，除 vacuum外全逃向無窮能量。exact驗證器為
`experiments/probe_unilateral_prime_hodge.py`。

因此 additive log-prime compensation已有完整 dichotomy：雙向 unitary導致 two-prime dense spectrum；
單向 full ladder導致 Euler cancellation。下一 gap須換成不以 additive log shifts實現 prime weight的
表示，並先給可執行 determinant/cohomology observable。

## G264. clustered prime convex transport（未閉合；P47 minimal case已嚴格裁決）

若 pole density可分割成互斥 intervals，各自與 `Lambda(n)/sqrt(n)` atom等 mass與 barycenter，則 hinge
Jensen會證 B46 `g_0<=0`。P47的256-bit Arb證書已嚴格證明 adjacent prime powers 7、8的 single
parcels overlap；同時嚴格證明 merged 7--8 parcel的全部 hinge inequalities，interior margin有正下界。

因此 minimal repair不是 dead end。真正未閉 obligation現縮成：定義 deterministic greedy clustered
allocation，先壓測 cluster size與 hinge margin是否 uniform，再對所有 clusters證 disjointness與 convex
dominance。不得由一個 certified pair外推，更不得把 finite cutoff存活當 B46/RH證明。
