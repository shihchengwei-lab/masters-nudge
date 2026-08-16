# Xi 的 archimedean 譜核心與 prime-relative determinant 路線

本文件接續 `spectral_toy_route.md`。目標是把「存在某個 Hilbert--Pólya
算子」縮成有固定 archimedean core、可由 primes 稽核的 relative spectral
problem。所有結論均離線推導；沒有把數值或未知零點位置當輸入。

## P1. 任意正自伴 determinant 的存在本身等價 RH

令

`G(w)=Xi(i sqrt(w))`, `mathcalG(w)=G(w)/G(0)`.

若存在正自伴 compact-resolvent A、`A^(-1)` trace class，且

`mathcalG(w)=det(I+wA^(-1))`,  (P1.1)

則 determinant 的 zeros全是 A eigenvalues的負值，故 Xi zeros全實，RH
成立。

反之，若 RH 成立，將 Xi 的正 ordinates（含 multiplicity）記為 `gamma_j`。
G 的 zeros便是 `-gamma_j^2`。Xi 是 order-one entire，故
`sum_j gamma_j^(-2)<infinity`；而 G 作為 w-entire function的 order為 1/2，
沒有額外 `exp(aw)` genus factor。於是在 `ell^2` 上取 diagonal

`Ae_j=gamma_j^2 e_j`

便有 P1.1。

所以「某個 A 存在」沒有降低難度。非循環路線必須先由 theta/primes
獨立定義 A 的 domain/action，再證 P1.1；不得用未知 zeros反造 spectrum。

## P2. regular finite-interval Sturm--Liouville 被增長率排除

令 `x=sqrt(w)>0`。功能方程給

`G(w)=xi(1/2-x)=xi(1/2+x)`.

由

`xi(s)=(1/2)s(s-1)pi^(-s/2)Gamma(s/2)zeta(s)`,

`zeta(s)=1+o(1)` (`s->+infinity`) 與 Stirling formula，

`log G(w)=(x/2)log[x/(2pi)]-x/2+O(log x)`  (P2.1)

`        =(1/4)sqrt(w)log w+O(sqrt(w))`.

若 A 是 regular finite-interval second-order Sturm--Liouville operator，
其 eigenvalues滿足 `lambda_n>=c n^2`（除去有限多項）。因此

`log det(I+wA^(-1))`

` <=sum_n log(1+Cw/n^2)=O(sqrt(w))`.  (P2.2)

P2.2 無法產生 P2.1 的 `sqrt(w)log w`。故任何匹配 Xi 的 differential
operator都不能是普通有限長區間模型；它必須有 logarithmically growing
phase volume，例如 singular/infinite geometry、exponential wall、quantum
graph growth或 nonlocal structure。

## P3. 一個精確匹配 archimedean 增長的自伴 core

在 `L^2(0,infinity)` 上取 Dirichlet boundary `f(0)=0`，並令

`A_0=-4d^2/dx^2+16pi^2 exp(2x)`.  (P3.1)

A_0 正自伴且 potential趨無限，故 compact resolvent。對 spectral parameter
`-w`，置 `y=2pi exp(x)`；decaying solution是

`f_w(x)=K_(sqrt(w)/2)(2pi exp(x))`,  (P3.2)

因 modified-Bessel equation直接給 `(A_0+w)f_w=0`。所以 normalized
boundary characteristic function為

`D_0(w)=K_(sqrt(w)/2)(2pi)/K_0(2pi)`.  (P3.3)

`K_nu` 對 nu為偶 entire，故 D_0 是 w-entire。Dirichlet eigenvalues對應
P3.3 的負實 zeros；`A_0^(-1)` trace class，且 normalized genus-zero product
給

`D_0(w)=det(I+wA_0^(-1))`.  (P3.4)

固定 argument 的 large-order asymptotic

`K_nu(2pi)=(1/2)Gamma(nu)pi^(-nu)[1+O(1/nu)]`

配合 Stirling，在 `nu=x/2` 給

`log D_0(w)=(x/2)log[x/(2pi)]-x/2+O(log x)`.  (P3.5)

P3.5 與 Xi 的 P2.1 精確匹配到 `O(log x)`。這不是 RH 證明，但它把
archimedean growth放進一個完全顯式、非循環的正自伴 operator。

同一匹配也可由 classical phase integral看出。P3.1 在 energy lambda 的
turning point前給

`N_0(lambda)=(sqrt(lambda)/(4pi))`

` *[log lambda-2log(2pi)-2]+o(sqrt(lambda))`,  (P3.6)

與 Riemann zero-counting的兩個主項同型。P3.5 已足以排除「只是偶然匹配
leading order」的疑慮；P3.6 用於解釋常數 `16pi^2` 的選擇。

## P4. Xi 與 core 的 relative factor只剩 polynomial growth

定義

`R(w)=mathcalG(w)/D_0(w)`.  (P4.1)

由 P3 的 Bessel asymptotic可更精確寫成（`x=sqrt(w)`）

`R(w)=C (x^2-1/4) pi^(-1/4)`

` *[Gamma(x/2+1/4)/Gamma(x/2)] zeta(x+1/2)[1+O(1/x)]`

`    =C' x^(9/4)[1+o(1)]`, `x->+infinity`,  (P4.2)

其中 C、C' 為正常數。也就是 A_0 已吸收整個 exponential/archimedean
growth；剩餘 arithmetic relative factor在正軸只有 polynomial growth。

合格的新目標是從 primes 構造另一個正自伴 A，使 resolvent difference
trace class且

`R(w)=det(I+wA^(-1))/det(I+wA_0^(-1))`.  (P4.3)

則

`R'(w)/R(w)=Tr[(A+w)^(-1)-(A_0+w)^(-1)]`.  (P4.4)

P4.3 會立即證 RH，因 numerator determinant只能有負實 zeros。它比任意
Hilbert--Pólya A 更具體：A_0 已固定，尚缺的是 arithmetic self-adjoint
perturbation／extension及 relative determinant identity。

## P5. prime Euler series給 relative trace 的候選長度資料

當 `x>1/2`（即 `s=x+1/2>1`）時，Euler product絕對收斂並給

`log zeta(1/2+x)`

` =sum_(p,m>=1) p^(-m/2) exp[-xm log p]/m`.  (P5.1)

所以 prime powers提供正的 length data

`length_(p,m)=m log p`, `weight_(p,m)=p^(-m/2)/m`.  (P5.2)

對 w 微分後，其 contribution 是

`-(1/(2x))sum_(p,m)(log p)p^(-m/2)exp[-xm log p]`.  (P5.3)

P5.1 很像 relative/scattering determinant 的 periodic-orbit expansion，
而 P5.3 很像 resolvent-trace difference。然而這只在 `x>1/2` 合法；把它
延伸至 central region而不預設 zeta zero-free，正是 arithmetic難點。

此外逐 prime local factor仍不能各自量子化：其 central-coordinate poles
位於 `Im z=1/2`，且 amplitude `p^(-1/2)` 是 contraction而非 unit-modulus
self-adjoint scattering phase。任何 operator realization都必須把所有 primes
與 archimedean channel全域耦合；disjoint loops/direct sums不合格。

## P6. 當前最小非循環 obligation

下一步只接受下列形式的實質進展：

1. 以 P3.1 為 core，從 prime-length measure P5.2 獨立定義一個 symmetric
   perturbation、boundary coupling、canonical system或 unitary dilation；
2. 證其 closure/self-adjointness與 resolvent difference trace class；
3. 先在 `x>1/2` 由絕對收斂 Euler series證 P4.4，再以 operator analyticity
   延拓 P4.3，而不是先使用 zeta 的未知 zero-free region；
4. 核對 determinant normalization、gamma shift `1/4`、polynomial
   `s(s-1)` 與所有 boundary terms。

若 construction只把 Xi zeros作 spectral data輸入，依 P1 淘汰；若只重現
P5.1 的非自伴 transfer determinant而沒有 self-adjoint/unitary dilation，
亦不足以推出 RH。

## P7. theta summands 是 exact Morse ground states

令

`y_n(u)=pi n^2 exp(2u)`

並把既有 theta summand寫成

`T_n(u)=2pi n^2 exp(5u/2)(2y_n-3)exp(-y_n)`.

定義

`phi_n(u)=T_n(u)/(2exp(u/2))`

`        =y_n(2y_n-3)exp(-y_n)`.  (P7.1)

直接使用 `y_n'=2y_n` 兩次微分，得到 exact identity

`phi_n''=(4y_n^2-20y_n+4)phi_n`.  (P7.2)

所以

`H_n=-d^2/du^2+4pi^2n^4exp(4u)-20pi n^2exp(2u)+4`  (P7.3)

滿足 `H_n phi_n=0`。在 `u>=0`，`y_n>=pi>3/2`，故 phi_n嚴格正且衰減。
若在 0 取由 phi_n logarithmic derivative指定的 Robin condition，則

`H_n=Q_n^*Q_n>=0`, `Q_n=d/du-phi_n'/phi_n`,  (P7.4)

且 phi_n是 zero ground state。這是完整解析 factorization，不是數值
觀察。

同一式可辨認為 Whittaker/Morse channel。置 `z=2y_n`，則

`phi_n` 正比於 `z^(-1/2)W_(5/2,1)(z)`,  (P7.5)

因 `W_(5/2,1)(z)=exp(-z/2)z^(3/2)(z-3)`。更一般地，

`f_(n,w)(u)=z^(-1/2)W_(5/2,sqrt(1+w/4))(z)`  (P7.6)

滿足 `(H_n+w)f_(n,w)=0` 且在 infinity衰減。故每個 channel 的 Weyl
function與 Dirichlet determinant可由 P7.6 顯式寫出。

此外 `H_n` 只是同一 Morse expression的 shift：`y_n(u)=y_1(u+log n)`。
這與 J14/A18 的 exact theta shift完全一致。於是完整 theta kernel有

`Phi(u)=2exp(u/2)sum_(n>=1)phi_n(u)`.  (P7.7)

P7.7 首次把 theta arithmetic表示成一族獨立定義的正自伴 Morse channels
之 ground states。它仍只是 state-sum，不是 spectral determinant；不得
由 P7.4 直接宣告 Xi zeros全實。

P7.2 的純整數 polynomial audit 為
`experiments/verify_theta_morse_identity.py`；它重建
`D=2y(d/dy)` 對 `exp(-y)P(y)` 的作用，不使用浮點或特殊函數 library。

## P8. 合法的和式 operator closure：star boundary coupling

雖然 determinants 的正和不封閉，自伴 boundary coupling能合法產生 Weyl
functions 的和。對有限個 half-line channels，令 `m_n(w)` 是 P7.6 的
boundary logarithmic derivative。要求各 channel boundary values為
`f_n(0)=c_n a`，並取 real Kirchhoff condition

`sum_n c_n f_n'(0)=alpha a`, `alpha real`.  (P8.1)

這是自伴 star coupling；其非-Dirichlet eigenvalues滿足

`sum_n c_n^2 m_n(w)=alpha`.  (P8.2)

每個 m_n 是 Weyl--Nevanlinna function，故正權和仍是同類；P8.2 的 zeros
受自伴性保護。有限-channel secular determinant是各 Dirichlet determinants
的乘積再乘 P8.2 的左側差。

因此 S8 的「theta 是和」並未排除所有 operator機制：正確的 sum closure
不是平均 characteristic functions，而是先把 shifted Morse channels作
共同自伴 boundary coupling，再對 Weyl functions求和。

目前尚未證 P8.2 等於 Xi 的 G、h 或 relative factor。countable channels
還須證 boundary map summability與必要 renormalization。P7.1 的 boundary
values有 `exp(-pi n^2)` 衰減，顯示至少自然的 square-summable couplings
存在；但選擇 c_n、alpha 必須由 P7.7/P5 推出，不能事後配合未知 zeros。

下一個具體計算是把 P7.6 的 exact `m_n(w)` 代入候選 P8.2，檢查其在
`sqrt(w)>1/2` 的 expansion能否逐項重現 P5.3 或 Xi logarithmic derivative。
若 analytic forms不匹配，star route即可解析淘汰；若匹配，再處理無限
channel self-adjointness與 determinant normalization。

## P9. naive Morse-star 作為完整 spectrum 被 Weyl density 排除

上述比較的第一關已可不用特殊函數細節完成。對固定 n，P7.3 是 half-line
exponential-wall operator；其 high-energy counting與 P3 同階：

`N_n(lambda)=(sqrt(lambda)/(4pi))log lambda+O_n(sqrt(lambda))`.  (P9.1)

因此有限 N 個 channels 的任一 energy-independent self-adjoint boundary
coupling，其 counting主項為

`N_total(lambda)=(N sqrt(lambda)/(4pi))log lambda+O(sqrt(lambda))`.  (P9.2)

理由是不同 self-adjoint boundary conditions只給 finite-rank resolvent
difference，不改 Weyl主項。Xi/G只需要 P3.6 的一份主項，所以 P9.2 除
`N=1` 外不可能是 Xi spectrum。

把全部 theta channels作 direct sum更糟。P7.3 的 boundary potential尺度
為 `n^4`，energy lambda只允許約 `n<=C lambda^(1/4)` 的 channels進入
classically allowed region。第 n channel的有效長度為

`(1/4)log lambda-log n+O(1)`.

故 Stirling summation給

`sum_(n<=C lambda^(1/4)) sqrt(lambda)`

` *[(1/4)log lambda-log n+O(1)] =Theta(lambda^(3/4))`.  (P9.3)

這與 Xi 的 `Theta(sqrt(lambda)log lambda)` 不相容。若每個 channel取 P7.4
的 ground-state Robin condition，未耦合 direct sum甚至先有 infinite
zero-mode multiplicity；改成共同 star boundary雖可移除該簡單退化，仍不
改 P9.3 的 high-energy phase volume。

Weyl function本身也顯示尺度問題。對 `w=x^2->+infinity`，Riccati equation
`m_n'+m_n^2=x^2+V_n` 給固定 n 的 expansion

`m_n(x^2)=-x-V_n(0)/(2x)-V_n'(0)/(4x^2)+O_n(x^-3)`.  (P9.4)

所以有限正權 sum只有 algebraic `1/x` expansion；Euler arithmetic tail則

`(1/(2x))zeta'(x+1/2)/zeta(x+1/2)`

` =-(log 2)/(2sqrt(2)x) 2^(-x)+O(3^(-x)/x)`.  (P9.5)

若不先減去 P9.4 的無限串 counterterms，兩者連 asymptotic scale都不符。
固定有限 star coupling因此不能精確重現 prime relative trace。

結論：P7 的 exact Morse structure是真實的新 identity，但 raw finite或
countable star assembly不是 Xi operator。它最多可作單一 A_0 的 auxiliary
boundary/relative construction；任何續作都必須保持只有一份 archimedean
phase volume，並讓 primes進入 trace-class relative perturbation，而非新增
一個 channel spectrum。P8 的 naive 版本至此封閉。

## P10. infinite Weyl sum 的收斂與 poles 不能正權消去

P9 的 infinite-channel判定還須處理 `sum m_n` 是否真正定義。P7.6 在
fixed compact w-set、`z_n=2pi n^2->infinity` 時使用 Whittaker large-z
expansion

`W_(kappa,mu)(z)=exp(-z/2)z^kappa[1+O_K(1/z)]`

（此處 `kappa=5/2`, `mu=sqrt(1+w/4)`），給 boundary logarithmic derivative

`m_n(w)=-2pi n^2+4+O_K(n^-2)`.  (P10.1)

所以未正則化正權和 `sum c_n^2m_n(w)` 在例如
`sum c_n^2n^2<infinity` 時 locally normally convergent；P7.1 的自然
`exp(-pi n^2)` boundary尺度遠強於此。也可減去 real constants

`m_n_tilde(w)=m_n(w)+2pi n^2-4`,  (P10.2)

再作較弱 summability。減去 real constants不破壞 Nevanlinna符號，故這是
合法的 boundary renormalization，而不是形式發散。

但 P10.2 不能修正 spectral density。每個 m_n 的 real poles是 H_n 的
Dirichlet eigenvalues，residues在統一 Weyl convention下同號。star weights
必為 `c_n^2>=0`，所以不同 channels即使 poles重合也只能增加 residue，不能
消去。由 P9.3，union pole counting是 `Theta(lambda^(3/4))`。meromorphic
Nevanlinna function的任一 real level `sum c_n^2m_n_tilde=alpha` 在 successive
poles間交錯，故其 zeros亦有同一主階（差至多 lower-order endpoint項）。

因此 convergence本身可以嚴格建立，但一旦保留正權／self-adjoint star
結構，poles恰好把過大的 channel density傳給 coupled spectrum。要消去
poles必須使用 signed/complex weights或 energy-dependent counterterms，前者
失去 Hilbert-space boundary norm `c_n^2`，後者不再是固定 self-adjoint
extension。故 P8 的全部標準 infinite-star版本均被排除；尚未排除的仍只有
單一 A_0 上的 trace-class global perturbation。

## P11. prime Hamiltonian 精確存在，但屬 semigroup／resonance 類型

prime lengths其實有一個完全非循環的自伴 operator。令

`H_P e_p=(log p)e_p` on `ell^2(primes)`.  (P11.1)

H_P 正自伴。當 `Re s>1` 時 `exp(-sH_P)` trace class，Fredholm product給

`det(I-exp(-sH_P))^(-1)`

` =product_p(1-p^(-s))^(-1)=zeta(s)`.  (P11.2)

等價地，zeta是 bosonic Fock Hamiltonian `dGamma(H_P)` 的 partition trace。
所以「primes無法放進任何自伴 Hilbert space」並非障礙；真正障礙是 P11.2
屬 heat/semigroup determinant，而 P1/P4需要 spectral resolvent determinant。

置 `s=1/2+x`、`x=sqrt(w)>1/2`。每個 local contraction是

`p^(-1/2)exp(-x log p)`.  (P11.3)

此外 subordination identity

`exp(-a sqrt(w))=(a/(2sqrt(pi)))`

` *int_0^infinity t^(-3/2)exp[-a^2/(4t)]exp(-wt)dt`  (P11.4)

將 P5.1 變成 w 上的正 Laplace transform。這解釋 Euler half-plane內的
complete-monotone sign，但不能合法越過 `x=1/2` 的 trace-class boundary；
該延拓正承擔 zeta poles/zeros。

P11.3 也有 self-adjoint open-graph interpretation。對
`r=p^(-1/2)<1`，可把 scalar reflection amplitude r 嵌入一個 unitary vertex
scattering matrix，以額外 channel補足 `sqrt(1-r^2)` transmission。長度
`log p` 的 loop repetitions遂產生 `r^m exp(-xm log p)`。但 amplitude小於
1 正表示能量洩漏到 auxiliary channel；local Euler poles是 open-system
resonances，不是 self-adjoint point spectrum。self-adjointness只保 real
energy scattering unitarity，並不迫使 resonances位於 RH line。

若把 auxiliary channels關閉以取得 compact spectrum，return paths會產生
額外 mixed periodic orbits；它們不在 Euler log的純 prime-power列表中。
故逐 prime unitary dilation雖可精確重現 local factors，仍不能直接給 P4.3。
合格的新機制必須全域耦合且證額外 orbits恰好重組成 archimedean/functional-
equation terms；目前沒有此 identity。

## P12. 分布跡公式測試：sign-definite trace-class perturbation 不可能

G16/P11 的 pointwise Euler identity與 P9 的 Weyl density之間，還可插入
一個可證偽的 heat-trace distribution。令 `x=sqrt(w)`。prime contribution
到 `d/dw log zeta(1/2+x)` 是

`q_P(w)=-(1/(2x))sum_(n>=2)Lambda(n)n^(-1/2)exp(-x log n)`.  (P12.1)

由 elementary subordination

`exp(-a sqrt(w))/(2sqrt(w))`

` =int_0^infinity exp(-wt)[exp(-a^2/(4t))/(2sqrt(pi t))]dt`,

得到 exact inverse-Laplace distribution

`Theta_P(t)=-(1/(2sqrt(pi t)))`

` *sum_(n>=2)Lambda(n)n^(-1/2)exp[-(log n)^2/(4t)]`.  (P12.2)

對每個 t>0，P12.2 在 small-t regime絕對收斂，且第一項為

`-(log 2)/(2sqrt(2pi t))exp[-(log 2)^2/(4t)]`.  (P12.3)

完整 relative heat trace還須加入 gamma、polynomial與 A_0 terms；P12.2
是 prime orbit部分，不可單獨當作正譜 heat trace。

現在測試最自然的 additive model `A=A_0+V`。若 V 是 bounded trace-class
self-adjoint，則

`Delta_V(w)=det(I+V(A_0+w)^(-1))`

滿足 `log Delta_V(w)=O(1/w)`，故 `Delta_V(w)->1`。但 P4.2 的 Xi/core
ratio為 `Cw^(9/8)`，所以原始 R 不可能來自這類 perturbation。archimedean
power必須先由 boundary/singular core modification吸收。

即使形式上先除去該 power，prime factor有

`log zeta(1/2+sqrt(w))=O(2^(-sqrt(w)))`,  (P12.4)

比任意 `w^-N` 更小。若再要求 `V>=0` 或 `V<=0` 且 trace class，Fredholm
expansion與 trace-norm dominated convergence給更精確的

`lim_(w->infinity) w log Delta_V(w)=Tr V`.  (P12.5)

P12.4 的左側乘 w仍趨 0，所以必須 `Tr V=0`；sign-definiteness隨即迫使
`V=0`。故非平凡 primes不能由 sign-definite trace-class additive potential
編碼。這一步不需要假設所有 higher trace moments存在。

這是 distribution-level falsification，而不只是 density mismatch。尚未
排除的是：

- 改變 domain的 singular/boundary perturbation；
- sign-indefinite relative perturbation，容許 spectral-shift cancellation；
- open scattering system的 resonance trace；
- 或一個先精確吸收 gamma/polynomial後、由全域 arithmetic coupling產生的
  non-additive determinant。

模曲面 MS1 已提供第三類的 exact realization。其 Birman--Krein/phase
distribution可重現 explicit formula，但 spectral-shift density是 signed
continuous/resonant object，不是正離散 heat trace；這正是從 scattering
到 RH point spectrum仍缺的一步。

## P13. explicit prime--gamma heat trace 與 complete-monotonicity criterion

W18 令

`h(w)=G'(w)/G(w)=xi'/xi(1/2+sqrt(w))/(2sqrt(w))`.  (P13.1)

在 `w>1/4` 的 Euler half-plane可逐項 inverse Laplace。置 x=`sqrt(w)`；
`1/s+1/(s-1)` 的 pair除以 `2x` 正好是 `1/(w-1/4)`。再用

`psi(z)=int_0^infinity[e^(-u)/u-e^(-zu)/(1-e^(-u))]du`

及

`L_w^(-1)[e^(-a sqrt(w))/sqrt(w)](t)`

`=exp[-a^2/(4t)]/sqrt(pi t)`,  (P13.2)

得到 exact arithmetic heat trace `h(w)=int_0^infinity e^(-wt)Theta(t)dt`，
其中

`Theta(t)=e^(t/4)`

` +(1/(4sqrt(pi t))){int_0^infinity[`

` e^(-u)/u-e^(-u/4-u^2/(16t))/(1-e^(-u))]du-log pi}`

` -(1/(2sqrt(pi t)))sum_(n>=2)Lambda(n)n^(-1/2)`

` *exp[-(log n)^2/(4t)]`.  (P13.3)

integral在 u=0 的兩個 singularities相消；對每個 t>0，prime sum亦由
Gaussian log-weight絕對收斂。P12.2 正是 P13.3 最後一行。

若 RH成立，G 的 genus-zero product給

`Theta(t)=sum_(gamma>0)m_gamma e^(-gamma^2t)`,  (P13.4)

故 Theta completely monotone。反之，若能直接由 P13.3 證

`(-1)^k Theta^(k)(t)>=0` 對所有 `k>=0,t>0`,  (P13.5)

Bernstein representation給 `Theta(t)=int_0^infinity e^(-ut)dmu(u)`、
`mu>=0`。Tonelli再給

`h(w)=int_0^infinity dmu(u)/(w+u)`,  (P13.6)

即 W18/A20 所需 Stieltjes representation，從而 G 的 zeros全在負實軸並
推出 RH（配合既有解析 growth/uniqueness）。所以 P13.5 是完整而非有限階
criterion。

這仍不是證明：prime line在 P13.3 中為負，gamma/pole line為 signed
compensation；目前沒有把全部 k 的 derivatives重排成 squares。下一個合格
工作只接受 P13.3 的 single positive-measure factorization、semigroup trace
或 all-k recursion；逐 k 數值驗證不算進展。

## P14. Theta 非負或有限階導數符號都不夠

P13.5 不能弱化成 `Theta(t)>=0`。抽象反例取

`Theta_epsilon(t)=e^(-t)+2epsilon e^(-Rt)cos(Bt)`,  (P14.1)

其中 `R>=1`, `0<epsilon<1/2`, `B!=0`。則對所有 t>0，

`Theta_epsilon(t)>=(1-2epsilon)e^(-t)>0`,

但其 Laplace transform有 poles `-R+/-iB`，不是 Stieltjes function。對任意
預先固定 K，再把 epsilon取得足夠小，同樣可令
`(-1)^kTheta_epsilon^(k)>=0` 對 `0<=k<=K`，而 off-axis poles仍存在。

所以只有 all-k theorem或 single positive-measure identity合格。P14 是一般
解析反例，不聲稱 P13 的 arithmetic Theta具有這些假 poles；它只證有限
Gaussian/derivative certificates無法取代 uniform factorization。

## P15. Stieltjes boundary measure 已正；真正障礙是 off-cut poles

取 `w=-r^2` 的 cut boundary。由 functional equation，regular real r處

`G(-r^2)=Xi(r)` 為實數，`h(-r^2)=G'/G(-r^2)` 亦為實，故沒有 continuous
imaginary jump。若 `Xi(gamma)=0` 且 multiplicity為 m，則

`h(w)=m/(w+gamma^2)+holomorphic`,  (P15.1)

所以 Stieltjes inversion在 `u=gamma^2` 給正 atom m。也就是說，所有已在
critical line上的 zeros無條件地形成 positive boundary measure。

若有 off-line zero `rho=1/2+lambda`，其 G-zero是

`omega=lambda^2 notin (-infinity,0]`;  (P15.2)

它在 h 中產生 cut之外的孤立 pole，而不改 P15.1 的 boundary atom signs。
因此「critical boundary density/residues非負」、scattering time delay正或
P13 的 formal Stieltjes inversion measure正，均不能排除 P15.2。

完整 P13 factorization必須同時證兩件事：positive boundary measure，以及
`h` 在 `C\(-infinity,0]` 無其他 poles。前者已自動成立；後者正是 RH。
所以若 proposed semigroup只從 boundary phase構造 Hilbert space，卻未從
Euler/theta side證 cut-plane analyticity，它仍是 MS11 型循環。真正可能的
新輸出必須是 arithmetic resolvent identity，其 analyticity先於 zero
decomposition成立。

## P16. Hankel-kernel／contraction semigroup 的 single-factor target

P13.5 可避免逐 derivative表述。對每個 `tau>0` 定義

`K_tau(s,t)=Theta(2tau+s+t)`, `s,t>=0`.  (P16.1)

若 P13.6 成立，則在 `L2(mu)` 中取
`v_(tau+s)(u)=e^(-(tau+s)u)`，便有

`K_tau(s,t)=<v_(tau+s),v_(tau+t)>`,  (P16.2)

且 shift `v_r -> v_(r+a)` 是 contraction semigroup `e^(-aA)`、`A>=0`。
反之，若能直接由 P13.3 構造 compatible Gram factorizations P16.2，並證
shifts為 strongly continuous symmetric contractions，spectral theorem給
positive measure mu並回復 P13.6。使用 `tau>0` 是必要的，因 zero density
使 `Theta(t)` 在 `t downarrow 0` 發散，未必有 finite-norm `v_0`。

等價的 pure-kernel驗收條件是對所有 finite `(c_i,t_i)` 及 `a>=0`，

`sum_(i,j)c_i conjugate(c_j)Theta(2tau+t_i+t_j)>=0`,  (P16.3)

`sum_(i,j)c_i conjugate(c_j)[Theta(2tau+t_i+t_j)`

` -Theta(2tau+2a+t_i+t_j)]>=0`.  (P16.4)

P16.3 給 Gram，P16.4 令 shift contractive；它們是 all-size identity，不是
有限 k certificate。

P13.3 的 local prime heat kernel

`k_t(a)=(4pi t)^(-1/2)e^(-a^2/(4t))`

只有 convolution cross identity

`k_(s+t)(a)=int_R k_s(x)k_t(a-x)dx`.  (P16.5)

當 `a!=0` 時右側是不同 translated features的 pairing，不是單一 norm；
prime coefficient在 Theta中又帶負號。故逐 prime/local-length Gram不能給
P16.3。存活 construction必須把全部 prime lengths與 gamma continuum放進
同一 global feature map，以 sharp optical/reflection identity完成平方。

## P17. nudge audit：k 趨無窮時沒有可犧牲的 derivative margin

先在 RH成立時量出 target的必要尺度。由 Riemann--von Mangoldt counting與
Laplace method，對 fixed `t>0`，

`M_k(t):=(-1)^kTheta^(k)(t)`

`=sum_(gamma>0)m_gamma gamma^(2k)e^(-t gamma^2)`

`~[Gamma(k+1/2)/(8pi t^(k+1/2))]`

` *log[k/(4pi^2t)]`.  (P17.1)

error比 leading少一個 log；saddle位於 `gamma~sqrt(k/t)`。這是任何正
factorization必須 exact重現的 moment growth。

prime Gaussian可精確微分。若 `z_n=(log n)^2/(4t)`，則

`(-1)^k d^k/dt^k[t^(-1/2)e^(-z_n)]`

`=k! t^(-k-1/2)e^(-z_n)L_k^(-1/2)(z_n)`.  (P17.2)

所以 P13 prime line的第 k 階是

`-[k!/(2sqrt(pi)t^(k+1/2))]`

` *sum_n Lambda(n)n^(-1/2)e^(-z_n)L_k^(-1/2)(z_n)`.  (P17.3)

對每個 fixed `z>0`，Plancherel--Rotach asymptotic給

`e^(-z)L_k^(-1/2)(z)`

`=pi^(-1/2)e^(-z/2)k^(-1/2)`

` *[cos(2sqrt(kz))+O_z(k^(-1/2))]`.  (P17.4)

故單一 fixed prime的 oscillatory envelope已是
`k! k^(-1/2)t^(-k-1/2)`，與 P17.1 相同 factorial/exponential base，只少
aggregate zero density產生的 `log k`。gamma、pole與 growing prime range
必須逐 k sharp cancellation後才留下 P17.1。

結論：任何估計若引入 `C^k` (`C>1`)、階數依賴 Cauchy loss，或先對
P17.3 取 absolute Laguerre sum，都無法由 target的單一 `log k` margin吸收。
P16 的 Gram/semigroup若存在，必須是逐階 zero-loss的 exact identity；這是
最新 nudge要求的 uniform-in-k 門檻。

## P18. arch block 已有 explicit Stieltjes measure；regular densities精確相消

令

`h_A(w)=A_4(sqrt(w))/(4sqrt(w))`.

`A_4(z)=psi(17/4+z/2)-logpi` 在 right half-plane analytic，且其 boundary
real part是 `b_4(r)>0`。Poisson formula給 exact

`A_4(x)=(2x/pi)int_0^infinity b_4(r)/(x^2+r^2)dr`, `x>0`,

所以

`h_A(w)=int_0^infinity [b_4(r)/(2pi)]dr/(w+r^2)`.  (P18.1)

這是無條件 positive Stieltjes representation。以 `u=r^2` 表示，其 measure
density為 `b_4(sqrtu)/(4pi sqrtu)`；P16 的 free Gram feature因此已顯式：

`v_t^A(r)=sqrt[b_4(r)/(2pi)]e^(-tr^2)`.  (P18.2)

W18 又給

`h(w)=h_A(w)-h_F(w)`,

`h_F(w)=F_4(sqrt(w))/(2sqrt(w))`.  (P18.3)

在 regular cut point `w=-r^2+i0`，W13.4 的
`2ReF_4(ir)=b_4(r)` 推出

`-(1/pi)Im h_F(-r^2+i0)=b_4(r)/(4pi r)`.  (P18.4)

這與 h_A 的 u-density逐點完全相同。因此 h=h_A-h_F 的 regular cut
boundary density精確為零；在 RH情形，因另知沒有 off-cut poles，才可升格為
完整 spectral-measure敘述並說剩下的只有 critical-zero正 atoms。
若有 off-line zero，則另留下 P15 的 off-cut poles。

P18 排除簡單 positive-measure domination／subtraction：兩個 continuous
measures不是一大一小，而是 regular部分完全相等；離散 atoms必須由 boundary
condition變更或 scattering spectral flow產生。合格的 P16 construction應以
P18.2 為 free channel，並由 arithmetic unitary/self-adjoint extension把
continuous density轉成 zero atoms，同時證不產生 off-cut resonances。只把
h_F視為 h_A 的 positive submeasure不可能完成。

## P19. standard self-adjoint boundary perturbation保留 a.c. spectrum，仍不夠

P18.1 的 free measure在每個 `u>0` 有 strictly positive absolutely-continuous
density。RH下 P13.6 的 target measure則是

`mu=sum_(gamma>0)m_gamma delta_(gamma^2)`,  (P19.1)

純離散。兩者不能由 ordinary unitary equivalence互換，因 spectral type受
unitary保留。

標準 finite-deficiency boundary extension也無法完成。rank-one Weyl change
具有 Möbius form（依 convention）

`m_alpha(z)=m_0(z)/(1+alpha m_0(z))`,

其 regular boundary density為

`Im m_alpha(u+i0)=Im m_0(u+i0)/|1+alpha m_0(u+i0)|^2`.  (P19.2)

只要 free density正，new a.c. density仍正，不會整片消失。更一般地，
finite-rank／trace-class self-adjoint perturbations由 a.c.-spectrum invariance
得到同一障礙；這也與 P12 的 trace-tail no-go一致。

所以 P18 所需的「spectral flow」不能是 ordinary unitary scattering或標準
finite-rank boundary condition。尚未排除的只剩：

- singular、non-trace-class domain change，能改變 spectral type；
- 從 continuum ambient space取一個 arithmetic cohomology/model quotient，
  但須先驗證 quotient norm正且不循環；
- 或完全獨立地構造 target positive operator，而非 perturb h_A。

這些機制仍須重現 P18 的 exact regular-density cancellation及 P17 zero-loss
moments。把 generic self-adjoint extension當作完成步驟已由 P19排除。

## P20. singular model quotient可離散化 continuum，但 generic positivity仍不足

P19 留下 cohomology/model quotient；最自然的 Hardy model仍有 exact反例。
對 upper-half-plane任意 `a`（`Im a>0`），Blaschke factor

`B_a(z)=(z-a)/(z-conjugate(a))`  (P20.1)

是 inner。model space `K_(B_a)=H2 minus B_a H2` 為 positive one-dimensional
Hilbert space，compressed shift含 eigenvalue a；其 Clark self-adjoint
extensions又有 real pure-point measures。也就是說，positive quotient確能
把 ambient boundary continuum轉成 atoms，但完全容許任意 off-boundary zero a。

因此 P19 的 quotient候選只有在另證以下額外結構時才有 RH內容：centered
scaling generator在 quotient上 self-adjoint，或 forward/backward shifts在同一
norm中皆 contractive。P20.1 對 generic inner functions不滿足這個 two-sided
條件。這正回到 MS8/MS11，而不是新的免費離散化機制。

結論：普通 Clark/model-space positivity已封閉。尚存的 quotient必須有
arithmetic Hodge star／polarization，先驗迫使 generator normal且 spectrum在
target line；證這個 polarization仍是 W12/P13核心。

## P21. exact determinant quotient：arch resolvent對 prime semigroup defect

P18 的 logarithmic derivatives可直接積分。置 `s=1/2+x`，normalize constants
使 value at x=0為 1。因

`d/dx log[pi^(-x/2)Gamma(17/4+x/2)]=A_4(x)/2`,

可取

`D_A(x)=pi^(-x/2)Gamma(17/4+x/2)/Gamma(17/4)`.  (P21.1)

又因 `d log D_F/dx=F_4(x)`，W18及 gamma recurrence給 exact

`D_F(x)=C_F (s+2)(s+4)(s+6)/[(s-1)zeta(s)]`,  (P21.2)

常數 `C_F` 只負責 normalization。直接相除即

`G(x^2)/G(0)=D_A(x)/D_F(x)`.  (P21.3)

P21.2 的 arithmetic factor不是形式 product。在 `Re s>1`，令

`H_P e_p=(logp)e_p` on `ell^2(primes)`；則 `e^(-sH_P)` trace class，且

`det(I-e^(-sH_P))=product_p(1-p^(-s))=1/zeta(s)`.  (P21.4)

所以 D_F 在 Euler half-plane確是 rational boundary channels乘一個由 primes
先驗構造的 Fredholm determinant。這比「假設存在 operator」更具體。

但 P21.4 是 semigroup defect determinant，不是 positive resolvent determinant。
local factor `1-p^(-1/2)e^(-xlogp)` 的 complex x-zeros是 open-channel
resonances；逐 prime unitary dilation會加入 leakage channels。P19 又排除以
trace-class self-adjoint perturbation把 D_A/D_F直接改成 pure-point target。

因此 arithmetic Hodge polarization的最小精確任務是：從 P21.4 的 fermionic/
defect complex構造一個 singular cohomology reduction，使

1. leakage/continuous states與 P18 free density逐點配對並 exact消去；
2. induced generator在 cohomology上 positive self-adjoint；
3. determinant quotient仍為 P21.3，且不新增 mixed periodic orbits。

若能完成，P13/P16即給 RH；目前沒有此 reduction。只把 Euler product稱為
spectral determinant不合格，因 determinant type與 positivity正是缺口。

## P22. unique factorization 阻止 prime exterior Fock 的 ordinary Hodge differential

P21.4 亦可寫成 exact fermionic supertrace。令

`F_P=Lambda^* ell^2(primes)`, `H_F=dGamma(H_P)`；則

`Str_(F_P)e^(-sH_F)=det(I-e^(-sH_P))=1/zeta(s)`.  (P22.1)

exterior basis state `e_S` 由 finite prime subset S標記，

`H_F e_S=(sum_(p in S)logp)e_S=log(n_S)e_S`,

其 parity為 `|S| mod 2`.  (P22.2)

unique factorization給 `log n_S=log n_T => S=T`。因此若 Q 是 odd operator、
在 basis span上與 H_F 對易，matrix element `<e_T,Qe_S>` 非零必要求同能量，
遂要求 T=S；但 odd Q不能保 parity，所以

`[Q,H_F]=0 and Q odd => Q=0`.  (P22.3)

這嚴格排除 prime exterior Fock內部的 ordinary energy-preserving supersymmetric
pairing：沒有 opposite-parity degeneracy可形成 acyclic pairs。把一份 parity-
reversed duplicate加進來雖可逐能量完全配對，卻只會消去整個 Euler determinant，
不會留下 P21.3 的 Xi spectrum。

若用 P18 arch continuum提供 opposite states，又遇到 TR12：atomic log-n
eigenspaces與 nonatomic continuum不存在 nonzero bounded exact spectral
intertwiner。故任何 Hodge differential若成功，必須是 singular／rigged、只在
analytic continuation後形成 resonant cohomology；但此時仍須獨立證 induced
inner product正，不能從 supertrace自動推出。P22 把「arithmetic Hodge star」
的缺口縮成一個非標準 singular differential，而非普通 Hilbert complex。

## P23. nudge correction：P17 moments滿足 Carleman；P18只聲稱 regular density

P17.1 的 growth不是 moment-indeterminacy障礙。對 fixed t，

`M_k~C_t Gamma(k+1/2)t^(-k)log k`

給

`M_k^(-1/(2k))~sqrt(e t/k)`,  (P23.1)

故 Stieltjes--Carleman sum `sum_k M_k^(-1/(2k))` 發散。若用 Hamburger形式，
`M_(2k)^(-1/(2k))~et/(2k)` 亦為 harmonic divergence。因此一旦 P16/P13
建立 positive representing measure，它由 moments唯一決定；「factorial
growth違反 Carleman」在此 indexing下不成立。

P18 的 density equality也有 independent algebraic proof，但必須精確限定。
由 W18.1

`F_4(ir)=A_4(ir)/2-xi'/xi(1/2+ir)`.

在非 zero ordinate，functional equation與 conjugation使
`xi'/xi(1/2+ir)` purely imaginary，故

`Re F_4(ir)=Re A_4(ir)/2=b_4(r)/2`.  (P23.2)

代入 branch `sqrt(-r^2+i0)=ir` 即得 P18.4，不用 RH或 contour shift。
但這只證 regular cut boundary densities相消；若 h_F有 off-cut poles，它
不是 Stieltjes transform，不能把 P18.4稱為完整 measure equality。P15/P18
的 analyticity缺口因此仍然存在，現已修正措辭。

## P24. determinant scattering ratio完全消去 G；boundary phase不含 RH資訊

P21.3 對 x 與 -x 都成立，而 `G(x^2)` 為 even。相除立即得到 meromorphic
identity

`D_F(-x)/D_F(x)=D_A(-x)/D_A(x)`

`=pi^x Gamma(17/4-x/2)/Gamma(17/4+x/2)`.  (P24.1)

在 physical boundary `x=ir`，P24.1 modulus為 1；其 phase完全由 arch gamma
factor決定。所有 nontrivial G zeros在 quotient兩側因 evenness成 paired
poles/zeros並消去。這是 functional equation的 determinant版本。

因此從 D_F只抽取 scattering matrix

`S_F(x)=D_F(-x)/D_F(x)`  (P24.2)

會丟掉全部 RH資訊。boundary unitarity、phase derivative、time delay、inner/
outer factor的 boundary modulus，即使 exact計算，也只能重現 P24.1。off-line
resonance pairs可存在而不改 S_F。

這排除 P21後最自然的 Lax--Phillips shortcut。合格 singular construction不能
只依賴 scattering ratio；它必須保留 absolute Jost determinant D_F 的
cut-plane pole divisor，並另證該 divisor只落在 imaginary x-axis。後一敘述
正是 RH，所以若 construction的 positivity只來自 P24.2 unitary boundary，
仍屬循環。

## P25. unbounded/rigged differential audit：closability與 spectral intertwining衝突

P22 不只排除 bounded Q。設 Q 為 densely defined closed odd operator，domain
含 finite-support prime states，並 strong-intertwine spectral projections：

`Q E_(H_F)(B) subset E_(H_F)(B)Q`.  (P25.1)

對 singleton `B={log n_S}`，P22 的 eigenspace為 rank one且只在單一 parity。
P25.1 迫使 `Qe_S` 同時留在該 eigenspace又改 parity，故為 0。finite-support
core上 Q=0；closedness/density遂不產生非平凡 ordinary Hodge differential。

atomic-to-continuum情形亦然。若 Q intertwines H_F 與 P18 multiplication
operator A，則

`Q E_(H_F)({log n})=E_A({log n})Q=0`,  (P25.2)

因 A 的 a.c. measure對 singleton projection為 0。反向 intertwiner對 Q*套
同一論證也為零。

唯一逃法是 distributional map，例如在 continuum fiber作 point evaluation。
但 point evaluation在 L2不 closable：可取 norm趨零、在指定點值固定的窄
spikes；其 images不趨零，graph無法閉合。於是 Q*Q不能由 standard Hilbert
operator theory定義成 positive self-adjoint Hodge Laplacian。

所以「改用 rigged space」本身不是解法。必須另造一個更強 topology，使
evaluation continuous，同時證 completion後的 norm positive、scaling action
self-adjoint且 determinant仍為 P21.3。這三項若未獨立完成，rigging只把
W12 positivity藏進 domain choice。P25 排除 fixed free Hilbert space上的所有
closable exact-intertwining versions。

## P26. nudge refinement：拓撲無法繞過 fiberwise Euler characteristic

P22.3 的核心確為純代數。對 squarefree n，energy fiber `log n` 的 chain
superdimension是

`sdim C_(log n)=(-1)^omega(n)=mu(n)`.  (P26.1)

任何 odd differential若保持 energy，無論 Hilbert、Fréchet或 distributional
topology，fiberwise Euler--Poincare identity仍給

`sdim H_(log n)(Q)=sdim C_(log n)=mu(n)`.  (P26.2)

加入 acyclic opposite-parity pairs不改 P26.2。因此當 `mu(n)=-1` 時，
cohomology不可能變成只含正 even multiplicity的 Hilbert spectrum。

若為每個 n重新指定 grading使 surviving state皆 even，supertrace coefficient
會從 `mu(n)` 變成 `|mu(n)|`，Euler determinant不再是 `1/zeta(s)`。若令 Q
連接不同 energies以配掉負 parity，則 `[Q,H_F]!=0`，heat supertrace不再由
cohomology invariant，P21.4 determinant identity失去保證。

所以僅放寬 topology確實不夠。要繞過 P26，必須同時改變 grading與 generator，
並另證新的 graded determinant仍精確等於 D_F；這已不是 prime exterior
complex的 Hodge theorem，而是一個全新的 arithmetic construction。P25 的
「新 topology」必要但遠非充分，現以 P26補正。

## P27. hidden-mode formulation：需要 full conservative realization，不是 scattering data

P24.1 表示 D_F 的 nontrivial divisor在 numerator/denominator間完全 cancellation。
在 system language中，G zeros是 scattering transfer function看不見的 hidden
modes。任一 realization都可分成

`minimal observable arch system direct-sum hidden block`.  (P27.1)

boundary unitarity只限制第一塊；可任意附加帶 off-axis eigenvalues的 hidden
finite-dimensional block而不改 P24 scattering ratio。這給一個抽象 exact
countermodel，說明 phase data永遠不夠。

然而若能從 P21 prime colligations先驗構造一個 full conservative realization，
並證 positive total energy同時 nondegenerate地限制到 hidden invariant subspace，
則 hidden generator Z_h滿足

`Z_h^*=-Z_h`  （centered x-coordinate）.  (P27.2)

其 spectrum遂在 imaginary axis；由 determinant identity P21.3即推出 RH。

所以目前最精確的 Hilbert--Polya sufficient theorem是：

1. absolute D_F（非只 ratio）是某個 arithmetic conservative colligation的
   perturbation/Jost determinant；
2. realization minimality分解後的 hidden subspace仍承受 positive conserved
   metric，而非 Krein或degenerate metric；
3. hidden determinant恰為 G，沒有額外 modes。

local prime unitary dilations只證 observable open system passivity；它們的
internal contractions產生 resonances，且 global closure新增 mixed returns，
尚未滿足 1--3。P27 並未證明 positive hidden metric；它把 P24遺失的 RH資訊
精確定位在 full-state energy completeness。

## P28. single-prime Euler factor 的 exact conservative colligation

令 `r_p=p^(-1/2)`、`ell_p=logp`。在一維 state與一維 channel上取

`U_p=[[r_p,sqrt(1-r_p^2)],[sqrt(1-r_p^2),-r_p]]`.  (P28.1)

直接乘法給 `U_p^*=U_p`、`U_p^2=I`。其 discrete-time transfer function是

`S_p(z)=-r_p+z(1-r_p^2)/(1-r_p z)`

`      =(z-r_p)/(1-r_p z)`,  (P28.2)

故對 `|z|=1` unitary。置 `z=e^(-x ell_p)` 並令

`d_p(x)=1-r_p e^(-x ell_p)=1-p^(-(1/2+x))`;  (P28.3)

則 exact

`S_p(e^(-x ell_p))=e^(-x ell_p)d_p(-x)/d_p(x)`.  (P28.4)

因此 Euler local denominator確是 positive conservative colligation的 state
determinant；numerator是 reflected denominator乘 trivial delay。這不是 heuristic
quantum graph。

對 finite prime set P，把 scalar colligations作 conservative cascade。transfer
functions相乘，令

`D_P(x)=product_(p in P)d_p(x)`, `L_P=sum_(p in P)ell_p`,

便有

`S_P(x)=e^(-xL_P)D_P(-x)/D_P(x)`.  (P28.5)

所以有限 cascade在 determinant層不新增 mixed-prime factors；P27先前把
mixed returns視為所有 globalization的必然障礙過強，現修正為：cascade可
避免它們。可是 `D_P` zeros只有

`x=-1/2+2pi i k/logp`,  (P28.6)

沒有 global zeta zeros。nontrivial divisor只能在 infinite renormalized limit
中出現。

## P29. critical infinite cascade不在 determinant/Hilbert--Schmidt topology收斂

在 Euler half-plane `Re x>1/2`，

`sum_p |r_p e^(-xell_p)|=sum_p p^(-(1/2+Re x))<infinity`,

故 P28 denominators在 trace-class determinant topology收斂到 P21.4。到
critical boundary `Re x=0`，即使先移除 trivial delays，local normalized
scattering deviation仍為 `O(r_p)`，而

`sum_p r_p^2=sum_p 1/p=infinity`.  (P29.1)

因此它們連 standard Hilbert--Schmidt infinite-product criterion都不滿足；
更不可能由 trace-class Fredholm determinant直接取 limit。finite conservative
cascades的 positivity沒有一個可用 operator topology自動延伸到 critical line。

functional equation可把 divergent ratio renormalize成 P24 的 gamma phase，
但該 renormalization同時消去 G divisor。absolute product D_F的 meromorphic
continuation則會產生新的 global poles，卻不是 P28 finite state determinants的
locally uniform limit於 target domain。

所以 P27 的 full conservative realization若存在，必須提供一個非標準
renormalized infinite cascade，並同時證：

1. positive energy forms在 cutoff極限 closable且 nondegenerate；
2. absolute Jost determinants收斂到 D_F，而非只收斂 P24 ratio；
3. limit hidden determinant正好是 G。

P29.1 顯示普通 von Neumann/Hilbert--Schmidt product無法做到。任何 counterterm
若只在 scalar determinant層指定 analytic continuation，沒有 operator-energy
極限，仍不能推出 hidden generator skew-adjoint。

## P30. nudge audit：density-one hidden positivity是有效中間層，但 cutoff尚未對應 zeros

假設已有 P27 型 hidden spectral realization與 orbit-local nondegenerate pairing。
令 `K_T` 為 `|Im rho|<=T` 的 generalized hidden eigenspaces，`kappa_-(T)` 為
metric負指標。MS13 的 exact two-point block顯示，每個 off-line reflection
orbit至少貢獻一個 negative direction。因此（按 multiplicity並容許固定
endpoint誤差）

`N_off(T)<=C kappa_-(T)`.  (P30.1)

故

`kappa_-(T)=o(N(T)) => N_off(T)=o(N(T))`,  (P30.2)

確實會給 density-one RH；而 full positivity `kappa_-(T)=0` 對所有 T 才給
完整 RH。這區分了可推進的 averaged mechanism與單純等價改寫。

但 P28 finite cascades的 state poles是 P28.6 local resonances，並非 truncated
zeta zeros；P29 又沒有 critical operator convergence。因此目前沒有 canonical
map把 cutoff positive metrics送到 K_T，連 P30.2 的 `kappa_-` estimate都尚未
從 primes定義出來。只在 scalar explicit formula上證 averaged positivity，
最多是 zero-density statement，不構成 hidden-energy construction。

一條合格的 staged program必須依序證：

1. renormalized cutoff state measures／spectral projectors收斂到 hidden G divisor；
2. normalized negative index `kappa_-(T)/N(T)->0`；
3. 再以 W14 型 orbit localization或 uniform coercivity把 `o(N)` 升到 0。

目前第一步即缺。故 density-one可作中間驗收，但不能以 finite-cascade positivity
自動宣稱，也不能替代最終 all-mode正能量。

## P31. positive infinite direct sum存在，但 meromorphic determinant不再是 spectral determinant

P29.1 不表示 unitary Hilbert space本身不存在：block direct sum

`U=direct-sum_p U_p`  (P31.1)

是良定 unitary operator。問題是其 scalar scattering determinant／cascade
product不在 critical boundary的 determinant class。

可以形式上把 Euler determinant作 meromorphic continuation，得到 P21.2；
但 continuation後 ζ zeros所產生的 D_F poles並不是 P31.1 的 state eigenvalues。
P31.1 的 local state parameters仍只有 `r_p=p^-1/2`，finite denominators的
resonances仍是 P28.6。analytic regularization能產生 collective divisor，卻
沒有提供相應 spectral projections或 positive hidden subspace。

因此必須區分：

`regularized scalar determinant identity`  (P31.2)

與

`operator determinant in a domain where zeros/poles equal spectrum`.  (P31.3)

只有 P31.3 可從 self-adjointness推 zero location。若 renormalization只證
P31.2，prime Hamiltonian早已 self-adjoint仍不能推出 RH；這正是反例。

P30 的第一步所以不能只是 finite Euler products在 distribution或 scalar
analytic-continuation sense趨近。它必須構造 actual limit resolvent與 spectral
projectors，並證其 perturbation determinant為 G/D_F。這比普通 zeta-
regularized determinant嚴格得多。

## P32. Schatten regularization可達 critical line，但 hard divisor全在 scalar cumulants

令 `K_s=diag(p^(-s))` on `ell^2(primes)`。對整數 `q>=2`，

`K_s in S_q <=> sum_p p^(-q Re s)<infinity`,

所以在 `Re s>1/q` 可定義 regularized determinant

`det_q(I-K_s)=product_p(1-p^(-s))`

` *exp[sum_(j=1)^(q-1)p^(-js)/j]`.  (P32.1)

因 `|p^(-s)|<1`，P32.1 在此 domain analytic且 nonzero。於 `Re s>1`，令
`P_1(z)=sum_p p^(-z)`，便有 exact

`1/zeta(s)=det_q(I-K_s)`

` *exp[-sum_(j=1)^(q-1)P_1(js)/j]`.  (P32.2)

在 critical line `Re s=1/2`，K_s 不屬 S_2（`sum_p1/p` 發散），但屬每個
`S_q,q>2`；特別是 `det_3(I-K_s)` 在整個 `Re s>1/3` operator-theoretically
良定且無零。這個 domain已跨過 critical line附近的右側區域。

因此 ζ 的 nontrivial divisor不可能來自 regularized operator determinant本身；
它全部藏在被 subtract的 scalar cumulants

`P_1(s)+(1/2)P_1(2s)`  （q=3）.  (P32.3)

若 P32.3 在某 domain是 single-valued analytic，exponential不會產生 poles；
實際上 prime-zeta continuation的 logarithmic singularities正編碼 ζ zeros與
pole。也就是說，Schatten renormalization雖保住 positive prime operator，卻
把 RH資訊移到沒有 operator positivity的 scalar counterterm。

更高 q只增加有限個 cumulants並把 determinant domain向左推，不解此問題。
P31所需的 spectral determinant不能由 `det_q` 加形式 scalar subtraction取得；
必須把 cumulants本身納入一個 positive arch/arithmetic operator identity。
P18/W16 正是該未解的 sharp cancellation。

## P33. Schatten decomposition 的 exact circularity：det_q只含 easy high-power tail

在 `Re s>1/q`，P32.1 可直接取 log並絕對重排：

`log det_q(I-K_s)`

`=-sum_(m=q)^infinity P_1(ms)/m`.  (P33.1)

右側之所以收斂，正因 `m Re s>1`。另一方面 Euler log identity是

`log zeta(s)=sum_(m=1)^infinity P_1(ms)/m`,  (P33.2)

所以 missing cumulants exact滿足

`sum_(m=1)^(q-1)P_1(ms)/m`

`=log zeta(s)-sum_(m=q)^infinity P_1(ms)/m`.  (P33.3)

以 q=3 為例，det_3只封裝在 `Re s>1/3` 已容易 analytic的 `m>=3`
prime-power tail；被 subtraction的 `P_1(s)+P_1(2s)/2` 原封不動包含
`log zeta(s)`。將 P33.3 代回 P32.2只得到 tautology。

因此不能把 det_3 的 operator positivity與 scalar cumulants分開證後再聲稱
得到 ζ：若 cumulants的 continuation是藉 P33.3 定義，就已使用 target
`log zeta`及其 divisor。合格的新 construction必須不經 P33.3，直接把 low
prime powers與 arch channel組成 operator relative trace。standard det_q路徑
至此完全封閉。

## P34. two-orbit bookkeeping：只在 Euler 區是直接 trace identity

取 q=3，定義 absolutely convergent

`R_(>=3)(s)=sum_p sum_(m>=3)p^(-ms)/m`, `Re s>1/3`.  (P34.1)

則

`log zeta(s)=P_1(s)+(1/2)P_1(2s)+R_(>=3)(s)`.  (P34.2)

`exp[R_(>=3)]` 在該 domain analytic且 zero-free；所以 ζ 的所有 zeros/pole
divisor在 `Re s>1/3` 完全由 low-orbit functional

`L_12(s)=P_1(s)+(1/2)P_1(2s)`  (P34.3)

的 continuation承擔。高 prime powers可作已知 analytic nonvanishing factor，
不再是 hidden-spectrum obstruction。

operator座標中，若 `K_s=diag(p^(-s))`，形式上

`L_12(s)=Tr K_s+(1/2)Tr K_s^2`.  (P34.4)

它只含 one-prime orbit與同一 prime的 double traversal，沒有 distinct-prime
mixed states。兩項在 Euler區皆為 positive traces；到 critical line第一項
非 trace class，第二項有 `sum_p1/p` logarithmic divergence。

因此 P33後的最小非循環 target已縮成：把 P34.4 與 P18 arch free channel
構造成一個 sharp relative trace／conservative colligation，使其 absolute
determinant等於 P21 quotient除去已知 `det_3` tail，且 hidden metric正。
若做到，domain `Re s>1/3` 已足以排除所有右半 critical-strip off-line zeros，
再由 functional equation得到 RH。

P34 目前只能稱為 bookkeeping localization，不能稱為已完成的 divisor
reduction。不能以 P34.2 反向用 logζ定義 L_12；必須從 prime與prime-square
sums直接完成 operator renormalization。

## P35. two-orbit cutoff尺度不匹配；Möbius cancellation只在 continuation後出現

P34.4 不能把兩個 positive traces直接彼此 renormalize。於 `s=1/2`，PNT
partial summation給 finite cutoffs

`sum_(p<=X)p^(-1/2)~2sqrtX/logX`,  (P35.1)

`(1/2)sum_(p<=X)p^(-1)~(1/2)loglogX`.  (P35.2)

兩者不同主階；prime-square sector不可能以 bounded/sharp pairing吸收 prime
sector的 power divergence。必須先由 arch continuum扣除 P35.1 的全部 smooth
bulk，才可能討論 logarithmic remainder。

Möbius inversion更清楚顯示後續 cancellation：

`P_1(s)=sum_(m>=1)mu(m)logzeta(ms)/m`.  (P35.3)

在 `s=1/2` 附近，m=2項 `-logzeta(2s)/2` 才與
`P_1(2s)/2` 的 leading `+logzeta(2s)/2` 相消。這是 analytic continuation
與 parity sign的 cancellation，不存在於 raw positive cutoffs P35.1--2。

所以 P34雖把 divisor責任縮到 two orbits，卻沒有產生現成 positive block。
合格 construction仍須兩步同時 operatorize：

1. prime atoms對 arch continuum的 sharp bulk subtraction（W16/P18）；
2. centered remainder與 prime-square的 parity-sensitive log cancellation。

第一步已是 W12 core；第二步若只用 P35.3又循環。two-orbit route的真正新
希望只能是一個包含 arch cross term的 positive square，不能是 prime與square
兩個 diagonal positive traces的直接差或和。

## P36. nudge 修正：P34 的臨界帶延拓獨立地循環

`P_1(s)=sum_p p^(-s)` 的原始 prime trace只在 `Re s>1` 收斂；因此 P34.4
在該 Euler 區才是獨立定義的 trace identity。Möbius inversion

`P_1(s)=sum_(m>=1) mu(m) log zeta(ms)/m`  (P36.1)

顯示其 continuation具有由 `s=1/m` 與 `s=rho/m` 產生的 logarithmic
singularities（可能有局部抵消）。尤其 `m=1` 已直接帶入 zeta zeros。
所以在 `1/3<Re s<=1` 宣稱 P34.4 已有 continuation，若沒有另一個完全不使用
zeta divisor的 operator construction，就已預設所要控制的零點位置。

更直接地，P34.2 在該帶內只能寫成

`exp L_12(s)=zeta(s) exp[-R_(>=3)(s)]`.  (P36.2)

右側確說明「若 L_12 已獨立構造」，其 exponential會承擔同一 divisor；但若
用 P36.2 定義 L_12，這只是 tautology。無條件、非循環的成果只剩：
`R_(>=3)` 在 `Re s>1/3` 絕對收斂且 zero-free。它沒有把 RH難度縮成兩個已
存在的 trace sectors。

因此 P34 的正確狀態是：它精確標記一個候選 construction必須在 Euler 區
匹配哪些 low orbit terms，但不是 proof-complexity reduction。P35 的 cutoff
尺度不匹配又顯示，最直接的 positive renormalization甚至沒有可用起點；在
出現獨立的 low-orbit+arch operator前，此支線暫停。

## P37. Carleman不能由 regular boundary density補出缺失 moments

P23 的 determinacy值得保留，但不能倒置成 existence。令 omega遍歷 G 的
zeros，並置

`u_omega=-omega`.  (P37.1)

G在 w-variable為 genus zero；對 t>0，log-derivative的 inverse Laplace可按
G-zero orbits寫成絕對收斂的 heat expansion

`Theta(t)=sum_omega m_omega exp(-t u_omega)`.  (P37.2)

critical-line zeros恰給 `u_omega=gamma²>0`。所以由 P15 boundary atoms可無條件
定義正 measure

`mu_crit=sum_(omega: u_omega>0 real)m_omega delta_(u_omega)`,  (P37.3)

及其 moments

`C_k(t)=int u^k e^(-tu)dmu_crit(u)`.  (P37.4)

另一方面 arithmetic P13.3給

`M_k(t)=(-1)^kTheta^(k)(t)`

`      =C_k(t)+sum_(omega: u_omega notin R_+)`

`        m_omega u_omega^k e^(-t u_omega)`.  (P37.5)

off-line functional-equation orbits在 P37.5 中成 conjugate pairs，所以 defect
為實，但一般不為零。P18/P23 的 regular cut density只辨認 P37.3；off-cut
poles沒有 boundary jump，正是 P37.5 的第二行。因此目前沒有獨立理由令
`M_k=C_k`。

Carleman的正確用途是：若先證 M_k有 positive Stieltjes representing measure，
則該 measure唯一；或若直接證所有 k的 `M_k=C_k`，則 off-cut heat defect被
唯一性消去。但前者就是 P13/P16 existence，後者則要求全部 off-line damped
moments消失，仍承擔同一 pole-exclusion責任。只把 regular boundary atoms的
moments指定為 candidate，不能宣稱它們已等於 arithmetic moments。

所以「P18 density equality + P23 Carleman => RH」是無效捷徑。它漏掉的不是
moment determinacy，而是 P37.5 的 moment equality；任何 contour argument若
在證 equality時忽略 off-cut residues，仍屬循環。

## P38. exponential-wall rank-one boundary candidate fails interlacing

P3 的 `A_0` 本身提供 collision-exclusion：任兩個 energy-independent scalar
self-adjoint boundary conditions的 simple spectra依 Sturm oscillation逐 gap交錯。若 Xi 是
`A_0` 的 rank-one boundary characteristic determinant，必要有每個 consecutive Dirichlet gap
恰一個 Xi ordinate。

256-bit Arb interval Newton嚴格給

```text
beta_3=29.3699195519006641880785494146...
 < gamma_4=30.4248761258595132103118975306...
 < gamma_5=32.9350615877391896906623689641...
 < beta_4=33.3831578765848344063229671695... .
```

其中 `beta_j=2nu_j`、`K_(i nu_j)(2pi)=0`；兩個 gamma balls由 Arb zeta-zero isolation取得。
同一 `A_0` gap含兩個 Xi zeros，故此 rank-one representation嚴格排除。最小失敗點是 spectral
multiplicity/counting，不是 positivity或數值精度。尚未排除 P19 所列 singular/infinite-rank
domain change與 independent arithmetic operator；它們必須先給 explicit domain/projectors，不能只
聲稱 self-adjointness。

## P39. all fixed finite-rank A0 perturbations fail by counting omega

P38 的 low-zero certificate只殺 rank one。數值合併 Arb zeta zeros與 Bessel roots甚至顯示
`0<=N_Xi(T)-N_A0(T)<=2` 到 `T=1000`，所以 finite height會錯誤支持 rank two。

fixed-argument imaginary-order Bessel asymptotic（Dunster 1990）給 phase

```text
phi(nu)=nu log(2nu/(e*2pi))+O(1),
```

故置 `nu=T/2` 後

```text
N_A0(T)=T/(2pi)log(T/(2pi))-T/(2pi)+O(1).          (P39.1)
```

Riemann--von Mangoldt則為同一 smooth main term加 `S(T)+O(1)`。Dobner 的無條件
large-deviation theorem特別推出 `S(T)` positive unbounded，因此

```text
N_zeta(T)-N_A0(T)=S(T)+O(1)                       (P39.2)
```

無界。另一方面，若兩個 compact-resolvent self-adjoint operators的 resolvent difference
固定 rank `r`（含 finite-deficiency domain extensions），min--max/spectral-shift counting給
`|N_A-N_A0|<=r`。P39.2矛盾，故所有 fixed finite rank一次排除。

此裁決不依賴 RH：若 Xi真是該自伴 determinant，表示本身先推出其全部 divisor為 real spectrum，
再與 unconditional Riemann--von Mangoldt及 S-omega衝突。存活者必須 genuine infinite-rank/singular，
且不能由低端 `rank<=2` pattern外推。

同一證明亦排除所有 bounded additive perturbations `A=A_0+V`。min--max給
`|lambda_n(A)-lambda_n(A_0)|<=||V||`；而 Bessel individual spacing在 energy variable為
`lambda_(n+1)-lambda_n asymp T/logT ->infinity`，故 sufficiently high counting discrepancy
至多1，與 P39.2無界矛盾。特別是 additive trace-class/Hilbert--Schmidt V皆不可能；P4若存活，
必須是 unbounded but resolvent-comparable 的真正 domain change。

## P40. single-channel prime point scatterers create a forbidden mixed orbit

在 P39 後最直接的 unbounded domain候選，是於同一 `A_0` channel 的
`L_p=(1/2)logp` 放 real self-adjoint point scatterers。boundary round trip長度
`2L_p=logp`，可匹配 first Euler orbit且不增加 arch phase volume。

但兩點 relative determinant exact為

```text
(1+g_pG_pp)(1+g_qG_qq)-g_pg_qG_pq^2.             (P40.1)
```

large positive spectral parameter k 時，`G_pq~c(k)e^(-k|L_p-L_q|)` 且 `c!=0`，所以
log determinant必有 distinct-prime mixed orbit `e^(-2k|L_p-L_q|)`。取 p=2,q=3，
其 length為 `log(3/2)<log2`；Euler log只含 `m logr`，完全沒有此項。因它比所有 Euler terms
更早，不能由尾項或其他 primes抵消；令 coefficient為0又必須殺掉2或3的 reflection。

故 ordinary single-channel local scatterers嚴格排除。分離 channels雖消除 mixed paths，卻已由
P9--P10 的過大 Weyl density排除。存活 construction必須 nonlocal 地同時保留 same-prime repetitions、
消除全部 distinct-prime paths，且只有一份 arch phase volume。

## P41. positive prime defect space has an immovable `-1/2` drift

令 `ell=logp`,`r=e^(-ell/2)`，在 `L2([0,ell],e^t dt)` 取 `A_pf=f'` 與 boundary
`f(ell)=rf(0)`。integration by parts exact給

```text
K_p=A_p+1/2 skew-adjoint,
spec(A_p)=-1/2+(2pi i/ell)Z.                      (P41.1)
```

後者正是 local Euler defect `1-p^(-1/2-x)` 的 zero line。故 positive weighted norm確實存在，
但它只證 generator是 fixed dissipative drift加 skew-adjoint，不是 critical-axis self-adjoint model。

任 finite prime direct sum與任何 reducing positive subspace仍滿足 `Re A=-I/2`；若 Hilbert
cohomology differential intertwines A且 adjoint structure可下降，同一 identity亦下降。把 A平移
`+1/2` 雖恢復 conservative generator，卻把 factor改成 `1-p^(-x)`，丟掉 exact critical weight。

所以 G256 後所需的「nonlocal projector」若只在 prime defect space內取 positive reducing quotient，
已被一個 prime嚴格排除且 uniform in cutoff。P28 unitary dilation仍可存在，但 P31已證 Euler zeros
在其中只是 compression resonances、不是 dilation spectrum。唯一邏輯逃生是另與 arch channel作
singular coupling，建立不繼承 P41.1 的新 positive norm；P22/P25又排除 ordinary Hilbert Hodge
differential與 bounded atomic--continuum intertwiner。

## P42. finite positive drift pairing survives, infinite prime limit accumulates at zero

P41 的 opposite-drift coupling不是空條件。對 `a=1/2`，finite block

```text
L=[[-a,q],[-q,a]],  G=[[1,-a/q],[-a/q,1]]
```

在 `q>a` 時 exact有 `G>0`、`L^T G+GL=0`，eigenvalues為
`+/-i sqrt(q^2-a^2)`。所以 finite cutoff確可用新 positive metric把 drift搬到 imaginary axis。

但 p-th defect circle frequencies是 `2pi k/logp`。若 coupling可依 p變成任意 `q_p>a`，paired
frequencies只是平移為

```text
2pi k/logp +/- c_p,  c_p=sqrt(q_p^2-a^2).         (P42.1)
```

對每個 p取最接近 `-c_p logp/(2pi)` 的整數 k，即有某 eigenfrequency絕對值
`<=pi/logp->0`。因此 infinite prime sum在0有無限 spectral accumulation，與 q_p大小無關；
resolvent不 compact，ordinary Fredholm spectral determinant不存在。

這是典型 cutoff量詞陷阱：每個 finite prime set都有正 metric與離散譜，但沒有 locally finite
infinite spectrum。要逃生必須在 limit前 nonlocally混合不同 prime lattices；然而 P40又要求不得
產生 distinct-prime orbit lengths。現在沒有同時滿足兩條的 explicit coupling。

## P43. positive cross-prime mixing is forbidden by the second determinant cumulant

把 P42 所需 mixing寫成 prime-graded semigroup form：

```text
K(s)_(p,q)=e^(-s(logp+logq)/2)B_(p,q),
B_(q,p)=B_(p,q)^* .                               (P43.1)
```

在 Euler half-plane若 K(s) trace class，`logdet(I-K)=-sum TrK^m/m`。對 p不等於q，
second cumulant在 length `log(pq)` 的係數為

```text
Tr(B_(p,q)B_(q,p))=||B_(p,q)||_HS^2>=0.           (P43.2)
```

Euler log只有 `m log r`；distinct product pq的係數為0。unique factorization保證 higher cycle
不能有同一 total length取消 P43.2。因此 exact Euler determinant強迫所有 off-diagonal
`B_(p,q)=0`。

這與 P42 形成嚴格 dichotomy：block diagonal pairing在0無限累積；cross-prime positive mixing
則加入 Euler不存在的 mixed cumulant。故 ordinary trace-class、orthogonal prime grading、natural
length covariance三條同時成立的 nonlocal operator整族排除。若只改 scalar zeta regularization，
P31--P33已證 divisor落在無 spectral projectors的 counterterms。

## P44. exact Euler determinant classifies every positive prime realization as diagonal

P43 不需先假設 orthogonal grading。設

```text
K(s)=sum_p p^(-s)A_p,  A_p>=0 trace class,         (P44.1)
det(I-K(s))=product_p(1-p^(-s)).
```

在 absolute convergence half-plane比較 log-det Dirichlet coefficients。integer p給
`TrA_p=1`；p平方給 `TrA_p^2=1`。positive eigenvalues的 sum與 square-sum同為1，故 A_p必為
rank-one orthogonal projection。distinct pq係數再給

```text
Tr(A_pA_q)=Tr(A_p^(1/2)A_qA_p^(1/2))=0,
```

所以不同 prime ranges正交。任何 positive nonorthogonal realization因此自動 unitary-equivalent
於 obvious diagonal prime operator。

結合 P41--P43：exact positive determinant沒有 hidden mixing自由；唯一模型帶 fixed `-1/2` drift，
modewise arch pairing在0累積，而 cross mixing違反 Euler coefficients。signed/super determinant則回
P22 energy-degeneracy no-go；regularized determinant回 P31--P33 scalar counterterms。

## P45. translation compensation: exact algebra, sharp two-prime no-go

在 `exterior l2(primes) tensor A` 令 creation `a_p^*` 同時作用 unitary `U_p`，且
`MU_p=U_pM-(logp)U_p`。對 `H=H_F+M`，energy shifts抵消，CAR給

```text
Q_sigma=sum_p p^(-sigma)a_p^* tensor U_p,
Q_sigma^2=0, [H,Q_sigma]=0,
{Q_sigma,Q_sigma^*}=(sum_p p^(-2sigma))I.           (P45.1)
```

此表示確實繞過 P22。一個 prime可在 `l2(Z)` 同時保 dense domain、exact weight與 compact
resolvent；但兩個 distinct primes時，任 eigenvalue生成
`lambda-m logp-n logq`。因 `logp/logq` irrational，此 orbit稠密，違反 locally finite spectrum。
所以 global unitary translation機制在兩 primes即不是 discrete spectral realization。

另在 infinite critical `sigma=1/2`，cutoff vacuum image norm平方為
`(sum_(p<=X)1/p)||f||^2`，故自然 strong-sum domain的 vacuum component必為0，domain不 dense。
`sigma>1/2` 雖 bounded，complex由 `Q^*/C_sigma` contracting為 acyclic；cutoff normalization又把
每個 fixed prime coefficient送到0。完整推導見 `translation_compensated_hodge_audit.md`。

## P46. unilateral compensation cancels the Euler factor exactly

以 bosonic backward shift `L_p` 取代 global unitary translation，可保
`Q^2=0,[H,Q]=0` 且使 spectrum locally finite；所以 P45 two-sided dense orbit確可避開。
但每個 compensating ladder貢獻 trace `(1-p^-s)^-1`，與 fermionic supertrace
`1-p^-s` exact相消。finite ladder `0<=n_p<=N` 的 full及 harmonic supertrace同為

```text
product_p(1-p^(-(N+1)s)) -> 1,                    (P46.1)
```

非 vacuum cohomology全在 moving top boundary。`probe_unilateral_prime_hodge.py` 已以 exact rational
arithmetic 對1、2、3 primes驗證 nilpotence、commutator、Hodge kernel與 P46.1。故 naive partial-shift
repair保住 domain/離散譜，卻結構性消掉 target Euler data。

## P47. single-atom transport fails rigorously; merged 7--8 parcel survives

對 Suzuki B46 的 pole density `b(u)=e^(u/2)+e^(-u/2)`，替每個 prime power `n=p^k` 解唯一 local
interval，使其 b-mass為 `logp/sqrt(n)` 且 b-barycenter為 `logn`。若 intervals互不相交，對 convex
hinge `(t-u)_+` 逐段 Jensen會直接推出 `g_0(t)<=0`。

70-digit executable screen至 `n<=10^5` 的第一 overlap在7與8：

```text
I_7=[1.8224337343384,2.0656910856717],
I_8=[2.0407406498706,2.1177580015083],
overlap=0.0249504358010953773.                       (P47.1)
```

`certify_prime_convex_transport_7_8.py` 以256-bit Arb/Krawczyk嚴格包住兩個 moment roots，並證

```text
r_7-l_8 in 0.02495043580109537726196 +/- 6.16e-24 >0.  (P47.2)
```

所以 single-atom disjoint-parcel ansatz嚴格排除。最小修復把7、8合併；同一證書包住 merged parcel、
middle stationary point，並得全部 hinge的唯一 interior minimum

```text
0.0045857897154596318447348191 +/- 6.46e-29 >0.      (P47.3)
```

outer intervals由 derivative monotonicity接到零端點，故 merged pair對所有 t嚴格存活。P47至此完成：
它決定 minimal local ansatz與 minimal repair；未決者另為 uniform clustered transport，不能由一個 pair
外推。
