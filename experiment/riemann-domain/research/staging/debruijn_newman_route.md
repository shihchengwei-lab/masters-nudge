# de Bruijn--Newman 熱流：uniform zero-collision 路線

本文件開啟一條與 finite Jensen certificates不同的全零點路線。所有數值只
能選擇估計區間；證明責任是對全部 zero indices的一致 collision barrier。

## DN1. deformation 與 backward heat equation

以 Xi 的 even Fourier kernel `Phi(u)` 定義（無關緊要的正 normalization略）

`H_t(z)=int_0^infinity e^(tu^2)Phi(u)cos(zu)du`.  (DN1.1)

Phi 的 double-exponential decay使 DN1.1 對每個實 t定義 entire function，且

`partial_t H_t=-partial_z^2H_t`.  (DN1.2)

`H_0` 的全部 zeros實恰為 RH。熱流路線的充分目標是：從某個已知
real-zero時間 `t_0>0` 出發，證 DN1.2 的 zeros往回延拓至 0 時永不碰撞。

## DN2. simple real zeros 的 exact dynamics

在所有 zeros `x_j(t)` 實且 simple的區間，對 `H_t(x_j(t))=0` 微分，並以
log derivative的對稱極限展開，得到

`x_j'(t)=2 PV sum_(k!=j)1/(x_j-x_k)`.  (DN2.1)

這是無限維 Calogero--Moser/gradient flow；有限 polynomial approximants上
恒等式完全代數，傳到 entire limit時須保留對稱截斷。

令 `d_j=x_(j+1)-x_j>0`。把 mutual pair與其餘 zeros分開，得

`d_j'=4/d_j-2d_j A_j`,  (DN2.2)

`A_j=sum_(k<=j-1)1/[(x_(j+1)-x_k)(x_j-x_k)]`

`   +sum_(k>=j+2)1/[(x_(j+1)-x_k)(x_j-x_k)] >0`.  (DN2.3)

定義 clock defect

`kappa_j=2-d_j^2A_j`.  (DN2.4)

則 gap平方滿足最簡 exact equation

`(d_j^2)'=4kappa_j`.  (DN2.5)

## DN3. 為何 absolute gap bound不是正確 uniform量

若 zeros是 exact infinite lattice `x_j=jh`，principal-value force為 0；
直接求和亦給 `A_j=2/h^2`，所以 `kappa_j=0`、所有 gaps stationary。
因此高處 gaps即使趨 0，也不必接近 collision：neighbor crowding會精確
抵消 `4/d_j` repulsion。任何要求 `inf_j d_j(t_0)>c>0` 的下降論證必然失敗；
應控制的是相對 clock defect DN2.4。

由 DN2.5，從 `t_0` 倒推至 t 的 exact collision budget是

`d_j^2(t)=d_j^2(t_0)-4int_t^(t_0)kappa_j(s)ds`.  (DN3.1)

故一個足以推出 RH 的 uniform theorem是

`4int_0^(t_0)max(kappa_j(s),0)ds<d_j^2(t_0)` 對所有 j。  (DN3.2)

若只對每個固定 j成立但常數隨 j惡化，仍不能排除碰撞時間向 0聚集。

## DN4. heat PDE與一般 kernel性質本身不足

有限 toy

`P_t(z)=e^(-tD^2)(z^2+a)=z^2+a-2t`, `a>0`,  (DN4.1)

滿足同一 DN1.2、even/real symmetry，但 zeros只在 `t>=a/2` 為實。
所以「熱流排斥 zeros」只保證 real-rootedness向較大 t保存，不能免費反向。
positivity/log-concavity/TP2 等一般 kernel假設亦已由 `positivity_kernel.md`
的反例證明不足。

## DN5. theta-specific 最小缺口

此路線下一個合格輸出不是更多 finite zero verification，而是由 Phi 的
theta saddle一致證明下列至少一項：

1. DN3.2 的全部 j collision budget；或
2. 一個在 DN2 flow下 backward-invariant、包含 `t=t_0` Xi zeros且禁止
   `d_j=0` 的 clock-ratio cone；或
3. 可由 theta直接驗證的全階 Laguerre--Polya/PF-infinity energy，並證其
   對 DN1.2 反向延拓至 0封閉。

大 j時必須以 zero phase/saddle的 uniform second-difference估計控制
`kappa_j`；低 j才可在高端 theorem建立後用嚴格 interval enclosure補有限
base。若所用 phase estimate已假設 `H_0` zeros實或 zeta在右半臨界帶
zero-free，便是循環。

## DN6. finite-window clock lemma

DN3.2 可降成一個明確的 local rigidity門檻。對固定 j，以 `d=d_j` 定義

`L_m=(x_j-x_(j-m))/d=sum_(r=1)^m d_(j-r)/d`,

`R_m=(x_(j+1+m)-x_(j+1))/d=sum_(r=1)^m d_(j+r)/d`.

由 DN2.3，若 `f(x)=1/[x(x+1)]`，則

`d^2A_j=sum_(m>=1)[f(L_m)+f(R_m)]`.  (DN6.1)

假設某個 `M>=1`、`epsilon>=0` 滿足

`d_(j-r)<= (1+epsilon)d_j`,

`d_(j+r)<= (1+epsilon)d_j`, `1<=r<=M`.  (DN6.2)

則 `L_m,R_m<=(1+epsilon)m` (`m<=M`)。因 f decreasing且

`f((1+epsilon)m)>=1/[(1+epsilon)^2m(m+1)]`,

DN6.1 給

`d^2A_j>=2/(1+epsilon)^2 * M/(M+1)`.  (DN6.3)

所以

`kappa_j<=2[1-M/((M+1)(1+epsilon)^2)]`

`        <=4epsilon+2/(M+1)`.  (DN6.4)

這是 deterministic all-index lemma，不使用 zeros統計。若 DN6.2 在
`0<=s<=t_0` 上以參數 `M_j,epsilon_j` 一致成立，則 DN3.2 的充分條件可由

`4t_0[4epsilon_j+2/(M_j+1)]<d_j^2(t_0)`  (DN6.5)

保證。

高處典型 `d_j^2` 約為 inverse log-squared尺度，所以 DN6.5要求大致
`M_j` 嚴格大於 log-squared高度、且 `epsilon_j` 小於同一 inverse
log-squared尺度。普通平均 spacing、pair correlation或「大多數 gaps
正常」均不夠；DN6.2 必須排除每一個可能先碰撞的 anomalously small gap。
這精確指定 theta saddle若要完成此路線所需的 uniform rigidity強度。

## DN7. uniformity audit：參數不能逐 gap事後選擇

DN6.5 的 pointwise寫法不是允許 density argument。合格的 high-zero theorem
應對每個 dyadic height block `Gamma<=|x_j|<2Gamma`，預先給共同函數

`M=M(Gamma)`, `epsilon=epsilon(Gamma)`, `h_*=h_*(Gamma)>0`,  (DN7.1)

並對該 block內每個 j、整段 `0<=s<=t_0` 同時證 DN6.2，且在起始時間

`d_j(t_0)>=h_*(Gamma)`.  (DN7.2)

若

`4t_0[4epsilon(Gamma)+2/(M(Gamma)+1)]<h_*^2(Gamma)`,  (DN7.3)

則整個 block無 collision。最後還須有一個高度後統一成立，低於該高度才
可用有限 rigorous enclosure補齊。

若 `M_j,epsilon_j` 是看過個別 gap後才挑選，或 DN6.2只對 density-one
indices成立，剩餘 exceptional gaps仍可能在趨近 0 的時間碰撞；最多得到
zero-density結論。DN7.1--DN7.3 是後續 theta saddle估計的正式驗收格式。

## DN8. Vandermonde action：可取代過強 local clock rigidity 的候選

DN7 只是充分條件，不是唯一可能的 collision barrier。對有限 simple real
zeros `x_1(t),...,x_N(t)`，置

`Delta(t)=product_(j<k)(x_j(t)-x_k(t))^2`,

`S_j(t)=sum_(k!=j)1/(x_j(t)-x_k(t))`.

由 DN2 的 `x_j'=2S_j` 直接得到 exact identity

`d/dt log Delta(t)=4 sum_j S_j(t)^2 >=0`.  (DN8.1)

因此從已知全實的 `t_0>0` 往後退，首次碰撞等價於某個 gap趨零、
`log Delta->-infinity`；在該點前 action

`int_t^t0 sum_j S_j(u)^2du`  (DN8.2)

必發散。若能對 Xi zeros的每個 dyadic height block建立扣除 clock-lattice
bulk及 boundary flux後的 uniform finite action bound，便可排除碰撞，而不需
DN7 那種「每個小 gap附近所有 gaps幾乎同長」的過強假設。稀有小 gaps可由
全局 Vandermonde能量與鄰塊 flux共同處理。

無窮 zero set下 raw `log Delta` 與 DN8.2 都發散；必要的新引理必須：

1. 定義有限 height block的 renormalized discriminant，相對 local clock
   lattice扣除 bulk；
2. 精確列出 block邊界穿越的 flux，且其常數 uniform in height；
3. 從 theta heat representation直接界定整段 `0<=t<=t_0` 的 renormalized
   action，不能先假設 zeros全實於 t=0。

DN8.1 是真正的 square/Lyapunov結構，但 DN8.2 的 theta-side uniform bound
尚未取得。它與 all-degree Hermite/Bezoutian determinant方向有實質交會：
沿 heat path由已知 real-rooted區出發，只要 discriminant不為零，roots就不能
離開實軸；故此路徑可能避開逐 degree certificate，卻仍需一個 all-height
determinant下界。

## DN9. finite height block 的 exact boundary flux

對無窮 zero system取有限 index block I，寫

`S_j^I=sum_(k in I,k!=j)1/(x_j-x_k)`,

`R_j^I=PV sum_(k notin I)1/(x_j-x_k)`, `S_j=S_j^I+R_j^I`.

block discriminant `Delta_I=product_(j<k in I)(x_j-x_k)^2` 滿足

`d/dt log Delta_I=4sum_(j in I)S_j^I S_j`

`=4sum_(j in I)(S_j^I)^2+4sum_(j in I)S_j^I R_j^I`.  (DN9.1)

所以 DN8.1 只對包含全部 roots的有限系統是純平方；高度截塊必須保留第二
項。exact clock lattice中 full `S_j=0`，internal square正被 boundary flux
完全抵消，這證明忽略外部 zeros會給錯誤的正 action。

較自然的 nonnegative量是 full velocity action

`A_I(t_1,t_0)=sum_(j in I)int_(t_1)^t0 S_j(t)^2dt`

`=(1/4)sum_(j in I)int_(t_1)^t0 |x_j'(t)|^2dt`.  (DN9.2)

若 block內發生 simple pair collision，`d^2` 線性趨零而
`S_j^2+S_(j+1)^2` 具有 `1/(t-t_*)` singularity，故 DN9.2 發散。因而一個
對擴張 blocks與 `t_1 downarrow 0` 一致的 finite-action bound足以排除所有
碰撞。真正 theta-side目標可寫為直接控制 full PV velocities；若改由
`Delta_I` 推導，則必須對 DN9.1 的 external flux作 uniform bound。這是 DN8
候選的正確無窮維介面。

## DN10. action bound 的循環性與 Sobolev no-go

對完整有限 root system，DN8.1 積分後就是

`int_t^t0 sum_j S_j(u)^2du=(1/4)log[Delta(t_0)/Delta(t)]`.  (DN10.1)

因此 uniform finite action與 `Delta(t)` 的 uniform正下界是同一敘述；它
不是比「無碰撞」更容易的自動能量估計。係數座標中亦如此：令 C 是 P 的
companion matrix。若 P simple-rooted，

`V=P''(C)P'(C)^(-1)`

的 eigenvalues正是 `P''(x_j)/P'(x_j)=x_j'`，故

`sum_j |x_j'|^2=Tr(V^2)`  (DN10.2)

（real-rooted時）。但 `P'(C)^(-1)` 的分母含 discriminant；用 DN10.2
估計時若先假設它有界，就已假設所需 separation。

普通 Fourier/Plancherel Sobolev norms也不能提供缺失下界。取

`f_d(x)=(x^2-d^2)e^(-x^2)`, `0<d<=1/4`.  (DN10.3)

這是一族 real Schwartz entire functions，所有固定階 real-axis L2 derivative
norm在 `d downarrow 0` 時保持有界；但在 root `x=d`，

`f_d''(d)/f_d'(d)=(1-4d^2)/d -> infinity`.  (DN10.4)

故由 theta Fourier integral得到的無權 `||H_t^(r)||_2` bounds，無法控制
DN9.2 的 zero-sampled velocity action。任何成功的 theta estimate必須新增
zero-sensitive sampling lower bound、de Branges frame或 all-size determinant
positivity；這些正是 RH級 uniform結構。

結論：DN8--DN9 仍是合法的 global介面，也比 DN7 local rigidity更一般，
但 DN10 排除「直接套 heat-energy/Plancherel」的捷徑。沒有新的 zero-sensitive
theta identity前，此線暫停，研究轉回 centered Weil finite-cutoff form。

## DN11. nudge audit：交叉項不是同尺度平均小量；core--buffer tail可逐點小

DN9.1 的 external flux目前沒有可用的 block-average消失。exact clock lattice
已是反例：對 symmetric index block I，full `S_j=0`，故

`sum_(j in I)S_j^I R_j^I=-sum_(j in I)(S_j^I)^2`.  (DN11.1)

交叉項與 internal square同主階並精確取消；把它稱為「boundary lower-order」
是錯的。這回答 nudge：同尺寸截塊下既沒有逐點小界，也沒有足夠的塊平均
小界。

但 core--buffer分離可對真正遠尾得到逐點估計。利用 zeros的 `+/-` symmetry，
若 `|x_j|<=Gamma`、外截斷 `L>=2Gamma`，則

`R_(j,L)=sum_(x_k>L)[1/(x_j-x_k)+1/(x_j+x_k)]`,

`|R_(j,L)| <=(8/3)|x_j| sum_(x_k>L)x_k^(-2)`.  (DN11.2)

在首次 collision以前，若 uniform zero counting
`N_t(U)<=C U log(2+U)` 成立，Stieltjes partial summation給

`sum_(x_k>L)x_k^(-2)<=C'(log L+1)/L`,  (DN11.3)

故

`sup_(|x_j|<=Gamma)|R_(j,L)|`

` <=C'' Gamma(log L+1)/L`.  (DN11.4)

再由 core cardinality `O(Gamma logGamma)`，

`sum_(|x_j|<=Gamma)|R_(j,L)|^2`

` <=C''' Gamma^3 logGamma(log L+1)^2/L^2`.  (DN11.5)

取 `L=Gamma^2` 時右側 `O(log^3Gamma/Gamma)->0`。所以遠尾確可在
core上逐點、繼而 L2 控制；真正未解的是 buffer transition layer。若直接
對 outer block `|x|<=L` 使用 DN9.1，其自身邊界仍有 DN11.1 的主階 flux。
需要 tapered/renormalized discriminant identity，把 transition flux與 clock
background精確扣除；DN11.4不能單獨完成截塊到全域的極限。

## DN12. product taper exact identity 與離散 Hilbert-transform no-go

先檢查 DN11最後提出的最自然 taper。對有限 distinct real roots、固定實權重
`a_j`，定義

`E_a=sum_(j<k) a_j a_k log (x_j-x_k)^2`,

`T_j=sum_(k!=j) a_k/(x_j-x_k)`,

`H_j=T_j-a_jS_j=sum_(k!=j)(a_k-a_j)/(x_j-x_k)`.  (DN12.1)

由 `x_j'=2S_j` 逐 pair微分，exact 有

`E_a'=4sum_j a_j S_j T_j`

`    =4sum_j a_j^2 S_j^2+4sum_j a_jS_jH_j`

`    =4sum_j(a_jS_j+H_j/2)^2-sum_jH_j^2`.  (DN12.2)

所以 product taper確把 external flux集中成一個 commutator `H`，但它沒有
自動變成 boundary lower-order term。

在雙向 exact clock `x_j=jd` 上，PV `S_j=0`，而對 compactly supported
`a in ell^2(Z)`，

`H_j=d^(-1) PV sum_(m!=0) a_(j-m)/m`.  (DN12.3)

其 Fourier multiplier為

`d^(-1)sum_(m!=0)e^(-imtheta)/m=i(theta-pi)/d`, `0<theta<2pi`.  (DN12.4)

因此它是 order-zero discrete Hilbert transform，不是 taper derivative。
若 `a_j=A(j/L)`，其中 A為固定非零 compact smooth profile，Plancherel與
frequency concentration at `theta=0,2pi` 給

`||H||_2/||a||_2 -> pi/d`.  (DN12.5)

特別地 `sum H_j^2` 與 block volume `L/d^2` 同階，不是 transition width或
`o(L)`。故「取更慢的 product taper，再以 Cauchy吸收 DN12.2 cross term」
不能提供 uniform positive action；DN11.1 的 clock cancellation只是被搬進
Hilbert commutator。

DN12 不排除真正的 relative-clock energy，但規定它必須在 pair kernel內先
扣除 clock principal value，或使用能消去 DN12.4 order-zero symbol的非局部
counterterm。普通 `a_ja_k` cutoff路線至此封閉。

## DN13. clock 線性化：正能量存在，但 backward 門檻是 exp(-c log² Gamma)

令雙向 zeros在一個局部 constant-spacing clock附近寫成

`x_j=jd+u_j`.

只要 denominators不為零，對 `Delta_(j,m)=u_j-u_(j-m)` 有 exact expansion

`1/(dm+Delta)=1/(dm)-Delta/(d²m²)`

`                 +Delta²/[d²m²(dm+Delta)]`.  (DN13.1)

clock PV首項為零。定義 positive translation-invariant operator

`(Lu)_j=sum_(m!=0)(u_j-u_(j-m))/m²`.  (DN13.2)

則 zero flow線性化為

`u'=-(2/d²)Lu`,  (DN13.3)

而 DN13.1 的最後一項給顯式 quadratic nonlinear remainder。L的 Fourier
symbol在 `-pi<=theta<=pi` 為

`ell(theta)=2sum_(m>=1)(1-cos(mtheta))/m²`

`          =pi|theta|-theta²/2`,  (DN13.4)

故 `0<=L<=pi²/2`。這是離散 fractional `|D|` energy，不是 DN12 的
order-zero Hilbert commutator。置

`Q(u)=<u,Lu>`.  (DN13.5)

在線性流上

`Q'=-(4/d²)||Lu||²<=0`.  (DN13.6)

而單一 gap deviation可由 Q直接控制。Cauchy--Schwarz與 DN13.4 給

`|u_(j+1)-u_j|²<=C_0 Q(u)`,

`C_0=(1/(2pi))int_(-pi)^pi 4sin²(theta/2)/ell(theta)dtheta<=1`.  (DN13.7)

最後一個不等式只用 `4sin²(theta/2)<=theta²` 與
`ell(theta)>=pi|theta|/2`。所以 `Q<d²` 確為禁止所有 gaps閉合的 genuine
linearized barrier。

但 backward scale非常嚴苛。checkerboard mode `theta=pi` 的 amplitude在
倒退時間 `tau` 放大

`exp(pi² tau/d²)`,  (DN13.8)

而整體 energy至多放大 `exp(2pi² tau/d²)`。因此只從 `t_0` 的 Q控制推回 0，
充分門檻至少是

`Q(t_0)<d² exp[-2pi²t_0/d²]`.  (DN13.9)

高度 Gamma 的平均 spacing `d~2pi/log(Gamma/(2pi))`，使右側尺度為

`(4pi²/log²Gamma) exp[-(t_0/2)log²Gamma]`  (DN13.10)

（忽略 lower-order logs）。這比任意 Gamma負冪更小。故普通 asymptotic
clock、pair correlation、或 polynomial-error saddle均不能啟動 perturbative
backward proof。若 theta-specific t_0 zeros確有 matching
`exp[-c t_0 log²Gamma]` rigidity，DN13仍可能存活；目前文件中的 J14/J24
只控制 moment-index tails，沒有提供 zero-height energy DN13.9。

## DN14. nudge density audit：平均模式尚未產生 zero-density theorem

full RH需要 DN3.2逐 gap成立；正比例／平均模式即使可控也至多瞄準
density statement。DN13.7 在單一仍全實的時間給形式 implication：若 dyadic
block的 local energies總和為 `o(N(Gamma)d²)`，則由 Markov至多 `o(N)` 個
gaps可有 clock-scale危險 deviation。這是有意義的中間尺度，但尚不是
「density-one zeros留在 critical line」。

原因是 backward過程一旦發生第一個 collision，DN2 的全實 labeling與正
energy推導就停止；目前沒有守恆的 collision count能把固定時間 bad-gap密度
轉成最終 nonreal-zero密度。operator路線 P30 的 Pontryagin negative index
可以扮演此計數器，但又缺 cutoff spectral-projector convergence。故本專案
目前對 density版也只有明確的 conditional mechanism，尚未得到非平凡
zero-density結論；不得用平均控制暗示逐點 RH。

## DN15. nonlinear relative-clock energy is an exact convex gradient flow

This is a theorem independent of RH. Fix `d>0`, a finite `I subset Z`, put
`u_j=0` outside I, and assume `x_j=jd+u_j` is strictly increasing. For `y>-1`
set `phi(y)=y-log(1+y)` and define

```text
E_d(u)=sum_(j<k) phi((u_k-u_j)/(d(k-j))).              (DN15.1)
```

Pairs outside I vanish; the remaining tails are `O((k-j)^-2)`. Direct
differentiation and symmetric PV cancellation of the clock give

```text
partial E_d/partial u_j
 =sum_(k!=j)[1/(d(j-k))-1/(x_j-x_k)]
 =-S_j,                                                (DN15.2)
S_j=PV sum_(k!=j)1/(x_j-x_k).
```

Thus the boundary-clock log-gas flow on I,

```text
u_j'=2S_j=-2 partial E_d/partial u_j,                  (DN15.3)
E_d'=-2 sum_(j in I)S_j^2<=0.                         (DN15.4)
```

Its Hessian is the positive weighted graph Laplacian

```text
<v,H_xv>=sum_(j<k)(v_j-v_k)^2/(x_j-x_k)^2.            (DN15.5)
```

Consequently DN13 is exactly the quadratic tangent of a global convex
barrier:

```text
E_d(u)=Q(u)/(2d^2)+O(u^3),   H_(clock)=L/d^2.         (DN15.6)
```

These are finite-dimensional identities with constants independent of I; no
thermodynamic extrapolation is used.

## DN16. uniform nonlinear gap barrier and backward bootstrap

For `0<kappa<1` put

```text
c_kappa=phi(kappa-1)=kappa-1-log kappa>0.              (DN16.1)
```

If `E_d(u)<c_kappa`, every adjacent gap exceeds `kappa d`: all pair terms are
nonnegative, and a gap ratio at most kappa contributes at least c_kappa.
Therefore

```text
|x_j-x_k|>=kappa d|j-k|,
0<=H_x<=kappa^(-2)L/d^2,
||H_x||<=Lambda_kappa=pi^2/(2kappa^2d^2).             (DN16.2)
```

The form inequality is termwise and uses `max ell=pi^2/2`, so it is uniform
in the window size. The convex segment from 0 to u obeys the same gap bound;
smooth convexity gives

```text
||grad E_d(u)||^2<=2Lambda_kappa E_d(u).               (DN16.3)
```

Let an ordered solution exist on `[t_0-tau,t_0]`. A first-crossing bootstrap
using (DN15.4)--(DN16.3) proves

```text
E_d(u(t_0)) exp[2pi^2 tau/(kappa^2d^2)]<c_kappa
 => E_d(u(t))<c_kappa and every gap>kappa d
    for t_0-tau<=t<=t_0.                              (DN16.4)
```

Indeed, below the threshold `E'>=-4Lambda_kappa E`, which gives precisely the
backward factor in (DN16.4).

This matches DN13's unavoidable scale. As `kappa->1`, the exponent tends
`2pi^2 tau/d^2`, exactly the checkerboard energy amplification; only
`c_kappa~(1-kappa)^2/2` shrinks. At zeta height Gamma the sufficient input is
still `exp[-(tau/2+o(1))log^2 Gamma]`. The gain is a rigorous nonlinear
all-gap barrier with constants uniform in the number of moving points.

## DN17. pressure audit and remaining arithmetic interface

1. Translation is the only clock null mode; fixing u outside I removes it.
2. A closing adjacent gap sends one phi term to infinity, so the barrier
   cannot silently cross a collision.
3. The checkerboard attains `max ell=pi^2/2`; no uniform smoothness proof can
   improve the exponent below `2pi^2 tau/d^2`.
4. Uniformity in I is proved, but a zeta dyadic block has slowly varying
   reference spacing and buffer flux. These corrections are not in DN16.
5. No current theta theorem gives `E_d(t_0)<=exp[-c tau log^2 Gamma]` for every
   high block. Polynomial clock asymptotics, pair correlation and mean energy
   fail this quantifier.

DN15--DN16 are unconditional progress rather than another RH-equivalent
criterion. The next named obligation is a theta-side bound for this explicit
convex energy, including reference-drift and buffer corrections.

## DN18. a nonuniform frozen clock is a forced convex flow

Let `y_j` be a strictly increasing bi-infinite reference with
`y_k-y_j>=d_-(k-j)` for `k>j`, let `x_j=y_j+u_j`, and suppose `u` has finite
support `I`. Assume the symmetric principal values

```text
S^y_j=PV sum_(k!=j)1/(y_j-y_k)
```

exist. The convergent relative Bregman energy is

```text
E_y(x)=sum_(j<k) phi((u_k-u_j)/(y_k-y_j)).             (DN18.1)
```

It is the Bregman divergence of the logarithmic Vandermonde potential. On the
moving coordinates `I`, direct differentiation gives

```text
g:=grad E_y=S^y-S^x,
x'=2S^x=-2g+2S^y,
E_y'=-2||g||_2^2+2<g,S^y>.                            (DN18.2)
```

Thus a nonuniform clock is not an unforced replacement for the arithmetic
lattice: its PV residual is an explicit forcing term. If `E_y<c_kappa`, then
every actual gap is at least `kappa` times its reference gap, and

```text
||H_x||<=Lambda=pi^2/(2kappa^2 d_-^2),
||g||^2<=2Lambda E_y.                                 (DN18.3)
```

Writing `r=||S^y||_(ell^2(I))` and `q=sqrt(E_y)`, (DN18.2)--(DN18.3) imply,
as long as `E_y<c_kappa`,

```text
q'>=-2Lambda q-sqrt(2Lambda)r.                        (DN18.4)
```

Hence a first-crossing argument proves the uniform forced barrier

```text
exp(2Lambda tau)[sqrt(E_y(t_0))+sqrt(2Lambda)r tau]
  <sqrt(c_kappa)
 => E_y(t)<c_kappa on [t_0-tau,t_0].                  (DN18.5)
```

For the exact infinite arithmetic clock `S^y=0`, this is DN16. For a hard
cutoff of `n` equally spaced points,

```text
S^y_j=d^(-1)(H_j-H_(n-1-j)),
||S^y||_2 asymp sqrt(n)/d,                             (DN18.6)
```

so the buffer error is not uniform in the window size. In particular, it
cannot be hidden inside an `O(1/n)` endpoint statement.

## DN19. moving-clock drift and the exact-reference alternative

For a finite ordered reference `y(t)`, the same energy satisfies the exact
time-dependent Bregman identity

```text
dE_y(x)/dt
 =-2||g||^2+2<g,S^y>-<H_y y',x-y>.                   (DN19.1)
```

Let `R_kappa>1` be the second solution of
`phi(R_kappa-1)=c_kappa`. Below the barrier, every pair ratio lies between
`kappa` and `R_kappa`; the integral Hessian formula and Cauchy--Schwarz give

```text
|<H_y y',x-y>|
 <=R_kappa sqrt(2E_y) A_y,
A_y^2=<y',H_y y'>
     =sum_(j<k)((y'_k-y'_j)/(y_k-y_j))^2.             (DN19.2)
```

For an affine clock `y_j=a+d j` on `n` points,

```text
A_y=|d'/d| sqrt(n(n-1)/2),                            (DN19.3)
```

while pure translation has `A_y=0`. Thus slow relative spacing drift is not
uniform in degree: it costs order `n|d'/d|`, not merely `|d'/d|`.

There is one clean way to remove both defects. If `x` and `y` are solutions
of the same finite log-gas flow, put `F=||x-y||_2^2/2` after aligning their
preserved centroids. Convexity of the Vandermonde potential gives

```text
F'=-2<x-y,grad V(x)-grad V(y)><=0.                    (DN19.4)
```

If every segment configuration between `x` and `y` has gaps at least
`kappa d_-`, the same uniform Hessian bound gives

```text
F'>=-4Lambda F.                                       (DN19.5)
```

Moreover `|u_(j+1)-u_j|<=2sqrt(F)`. Consequently

```text
F(t_0)exp(4Lambda tau)<(1-kappa)^2 d_-^2/4            (DN19.6)
```

prevents every actual gap from falling below `kappa d_-` backward through
the interval. This theorem is uniform in the number of particles, but its
input is a global `ell^2` approximation to an **exact reference solution**.
Hermite-zero self-similar log gases are explicit such references; a frozen
Riemann--von Mangoldt clock or a hard-cutoff lattice is not.

## DN20. quantified outcome of the clock/buffer pressure test

At height `Gamma`, `d_-` is of order `2pi/log Gamma`, so
`2Lambda tau=(tau/(4kappa^2)+o(1))log^2 Gamma`. Therefore every term inside
the bracket in DN18.5, and the global distance in DN19.6, must already be
`exp[-c tau log^2 Gamma]` small. Polynomial spacing asymptotics do not absorb
the PV residual, buffer, reference drift, or global `ell^2` accumulation.

This rigorously rules out the naive implementation "replace the fixed clock
by the local mean spacing and discard the endpoints." It does not rule out
the DN route itself: the surviving version must compare the theta zeros with
an exact co-moving log-gas (for example a suitably scaled Hermite-zero
configuration) with exponentially small, all-particle error. That is now the
single arithmetic obligation; any claimed estimate must state its particle
range before the height limit and must include the accumulated `ell^2` error.
## DN21. Hermite exact references fail at the finite/infinite interface

Let `q_1<...<q_n` be the zeros of the probabilists' Hermite polynomial. Its
differential equation gives `sum_(k!=j)1/(q_j-q_k)=q_j/2`. Consequently
`y_j(t)=b+a(t)q_j`, `a(t)^2=a(0)^2+2t`, is an exact finite log-gas solution.

This does not give an exact comparison for `H_t`, whose zero set is infinite.
A finite block `I` obeys

```text
x'_j=2 sum_(k in I,k!=j)1/(x_j-x_k)+B_j,
B_j=2 PV sum_(k outside I)1/(x_j-x_k).                (DN21.1)
```

For an arithmetic configuration the outside field cancels the hard-cutoff
residual in DN18.6, of `ell^2(I)` size `asymp sqrt(n)/d`. A central portion of
a larger Hermite system only moves this term into a buffer. Comparing all
particles is impossible as stated: finite Hermite roots have semicircle global
density, whereas fixed positive-time `H_t` zeros have Riemann--von Mangoldt
density and asymptotically constant local spacing. The Hermite proposal thus
fails first at the system-size/buffer interface.

## DN22. the strongest known positive-time rigidity misses one logarithm

D.H.J. Polymath, arXiv:1904.12438, Theorem 1.5, supplies the exact named-gap
input. For `0<t<=1/2`, define `x_n(t)` by

```text
g(x,t)=x/(4pi)log(x/(4pi))-x/(4pi)+11/8
       +(t/16)log(x/(4pi))=n.                         (DN22.1)
```

For `x>=exp(C/t)`, every zero of `H_t` is real and uniquely satisfies
`x_zero=x_n(t)+O(x^(-ct))`; section 9 also gives velocity
`-pi/4+O(x^(-ct))`. The error is `exp[-ct log x]`. A DN16/DN19 backward
interval of length `delta`, at spacing `d asymp 4pi/log x`, instead requires

```text
d exp[-C_1 delta log^2 x].                            (DN22.2)
```

For `delta asymp t`, the cited theorem is short by one factor `log x` in the
exponent. Splitting time does not remove the endpoint obstruction: a reset
step can be at most `delta=O(t/log x)`, but the theorem only applies while
`t>=C/log x`. At that terminal scale its guaranteed error is
`O(exp(-cC))`, while the gap is `asymp 1/log x`. Taking
`t=A loglog(x)/log x` makes the error smaller than a gap, but the final interval
to zero again demands `exp[-C A log x loglog x]`, beyond a polylogarithmic
error.

Thus the best existing positive-time zero asymptotic initializes neither a
one-step nor an admissibly reset barrier. This is an insufficiency theorem for
the cited bound, not a lower bound on the true error. A surviving DN proof now
needs new super-polynomial rigidity below heat time `1/log x`, or a different
collision invariant not governed by checkerboard backward amplification.
## DN23. exact nonlinear checkerboard collision saturates the barrier

The sharpness is not merely linearized. On the bi-infinite period-two
configuration

```text
x_j(t)=jd+(-1)^j a(t),   0<a(t)<d/2,
```

symmetric PV summation gives, for an even site,

```text
S_even=sum_(m in Z)1/(2a-(2m+1)d)
      =-pi/(2d) tan(pi a/d).
```

Hence the exact log-gas equation is

```text
a'=-(pi/d)tan(pi a/d),
sin(pi a(t)/d)=sin(pi a(0)/d)e^(-pi^2 t/d^2).         (DN23.1)
```

Choose the limiting initial value `a(0)=d/2`. Then alternate gaps collide at
`t=0`, while for every `t_0>0`

```text
a(t_0)=d/pi arcsin(e^(-pi^2 t_0/d^2))
      asymp d/pi e^(-pi^2 t_0/d^2).                  (DN23.2)
```

Thus a genuine nonlinear collision can leave only an
`exp[-pi^2t_0/d^2]` terminal displacement, and energy of twice that exponent.
This exactly saturates DN13/DN16. It rules out any universal improvement based
on a terminal norm continuous at the clock, and in particular proves that the
`x^(-ct)` information of DN22 cannot distinguish a no-collision trajectory
from a collision trajectory at zeta spacing. A surviving collision counter
must be discontinuous/topological or retain the full spectral history; a
smooth terminal energy cannot do it.
## DN24. shrinking-margin stability theorem

Let `C_d` denote the DN23 terminal configuration whose backward history
collides at time zero, and let `A_d` be the arithmetic clock. In normalized
local sup distance,

```text
epsilon_d=||C_d-A_d||/d
 =pi^(-1)arcsin(exp(-pi^2 t_0/d^2)).                  (DN24.1)
```

Suppose a terminal detector `J_d` separates the two histories by a margin
`m_d>0` and has modulus of continuity `omega_d` in this topology. Then the
taut but sharp stability constraint is

```text
m_d<=omega_d(epsilon_d).                              (DN24.2)
```

In particular, for a Holder bound
`|J_d(X)-J_d(Y)|<=C_d||X-Y||^alpha`,

```text
C_d>=m_d epsilon_d^(-alpha).                          (DN24.3)
```

Thus exponential ill-conditioning follows only when
`-log m_d=o(t_0/d^2)`, or more generally when the margin exponent is smaller
than `alpha pi^2`. A Boolean collision counter has fixed margin and is forced
to be discontinuous/non-uniform. But a real-valued surrogate whose signal
itself decays as fast as `epsilon_d` is not excluded; to use it arithmetically
one must certify errors `o(m_d)`. Smoothness was never the load-bearing
assumption: the exact boundary is terminal stability relative to the claimed
margin.

## DN25. finite backward-heat discriminant theorem

Let `P_T` be a monic real polynomial of degree `n` and define, for `t<=T`,

```text
P_t(z)=exp((T-t) partial_z^2)P_T(z),
D_P(t)=Disc_z(P_t).                                   (DN25.1)
```

Then `partial_t P_t=-partial_z^2P_t`, and `D_P` is a real polynomial with

```text
deg_t D_P<=n(n-1)/2.                                  (DN25.2)
```

Indeed, the coefficient of `z^(n-k)` has time degree at most `floor(k/2)`,
while the discriminant is isobaric of coefficient weight `n(n-1)`. By the
resultant identity,

```text
D_P(t)=0  iff  P_t and partial_z P_t have a common root. (DN25.3)
```

If `P_T` has simple real roots, continuity of roots gives

```text
P_s is real-rooted
 iff D_P(t)!=0 for every s<t<=T.                       (DN25.4)
```

The forward implication also uses preservation of real-rootedness by
`exp(-h partial_z^2)`, `h>=0`; the reverse follows because the number of
nonreal conjugate pairs cannot change without (DN25.3). Hence a Sturm chain
for the single exact polynomial `D_P` decides collision-freedom on any finite
interval. At generic transverse double collisions, `ord_t D_P` counts the
number of simultaneous colliding pairs; at degenerate collisions it is an
algebraic multiplicity ledger, not automatically a geometric pair count.

This is a genuine finite-degree topological/history counter and requires no
terminal continuity margin.

## DN26. why naive polynomial resultants do not pass to H_t

The finite theorem does not yet define a discriminant for the entire function
`H_t`. Ordinary local-uniform approximation at terminal time is far too weak.
For even degree `2m`,

```text
[z^0] exp(T partial_z^2) z^(2m)=T^m(2m)!/m!.          (DN26.1)
```

Thus the terminal perturbation

```text
r_m(z)=m!/[T^m(2m)!] z^(2m)                           (DN26.2)
```

tends rapidly to zero on every fixed disk, while its backward continuation
has constant term one at time zero. Therefore locally uniform polynomial
approximants, including a bare terminal Taylor cutoff, need not converge in
the spacetime graph norm and their discriminant zero sets need not converge.

An entire-function resultant would require a canonical regularization of the
infinite product of root separations (or an actual Fredholm/Sylvester limit),
together with convergence under `exp(T partial_z^2)`. Defining the product
from the collision times themselves is circular. This is the same type of
actual determinant/projector convergence missing in P30, now reached by an
explicit high-degree counterexample rather than analogy.

The finite resultant route therefore survives as an exact theorem but fails
at its first infinite-degree transfer. A valid continuation must supply a
theta-specific weighted entire norm in which both backward heat evolution and
the resultant regularization converge; compact convergence or fixed-height
zero convergence does not qualify.
## DN27. a boundary winding counts all generic heat collisions with one sign

Let `h(t,x)` be a real `C^3` solution of

```text
partial_t h=-partial_x^2 h
```

on a rectangle `R`, and set `F=(h,partial_x h):R->R^2`. Assume `F` is nonzero
on the boundary and every interior common zero is regular. At a collision,
`h=h_x=0`, and

```text
det D_(t,x)F
 =det [[h_t,h_x],[h_xt,h_xx]]
 =-(h_xx)^2<0.                                        (DN27.1)
```

Thus every collision has the same local Brouwer degree `-1`; there is no sign
cancellation. Consequently

```text
N_coll(R)=-deg(F,R,0)
 =-(1/(2pi)) Delta_(partial R) arg(h+i h_x).           (DN27.2)
```

This is an exact topological/history counter computed only from boundary
values. Degenerate collisions can be assigned the same nonnegative algebraic
count: perturb by the heat solutions `alpha+beta x`. The map
`(t,x,alpha,beta)->(h+alpha+beta x,h_x+beta)` is transverse in the parameter
directions, so generic small `(alpha,beta)` has only regular collisions; degree
stability makes their total `-deg` independent of the perturbation while the
boundary remains nonzero.

Unlike a smooth terminal energy, DN27 uses the whole spacetime boundary and
is integer-valued. It therefore survives DN23 and also avoids constructing an
infinite discriminant.

## DN28. pressure audit of the winding counter

The topological integer has fixed output margin, but its input stability radius
is exactly controlled by

```text
mu_R=min_(partial R) sqrt(h^2+h_x^2).                 (DN28.1)
```

DN23 permits `mu_R` (for a boundary placed near the terminal clock data) to be
log-squared exponentially small. Hence numerical or asymptotic certification
still needs error `o(mu_R)`; topology does not erase conditioning.

For `h=H_t`, take `R=[0,T]x[0,X]`, with `T>=1/2` and vertical sides chosen to
avoid collisions. The top edge has only real simple zeros. Up to zeros crossing
the vertical side, (DN27.2) is the exact ledger

```text
2 N_coll(R)=N_T^real(X)-N_0^real(X)+boundary flux.     (DN28.2)
```

Thus proving zero winding for all expanding rectangles would prove RH, but a
calculation that merely rewrites the bottom-edge phase of `H_0+iH_0'` has not
reduced the problem: it is another encoding of the missing real-zero count.

The new, non-circular obligation is narrower. One must derive directly from
the theta integral a uniform boundary homotopy for
`H_t+i partial_x H_t` on the two vertical edges and the bottom, with an
explicit nonvanishing margin, and show its winding equals the known top-edge
winding. Fixed-height interval arithmetic proves only finite verification;
discarding the bottom phase or assuming `mu_R>0` uniformly presupposes the
desired collision exclusion.
## DN29. positive even heat kernels can have a generic collision

Positivity of the Fourier kernel cannot supply the DN28 homotopy. Consider

```text
h_t(x)=e^t cos x+c e^(4t) cos(2x),   0<c<1.           (DN29.1)
```

This is the Fourier transform of a positive even two-frequency measure after
multiplication by `e^(tu^2)`, and it solves `h_t=-h_xx`. After division by
`e^t`, put `r(t)=c e^(3t)`. With `y=cos x`,

```text
h_t/e^t=2r y^2+y-r.                                   (DN29.2)
```

All complex `x`-zeros are real exactly when `r>=1`; when `r<1`, the negative
`y`-root is below `-1`. At

```text
t_*=(1/3)log(1/c),  x_*=pi,
```

one has `h=h_x=0` and `h_xx=-3e^(t_*)!=0`, so this is a regular collision with
the DN27 negative orientation. Approximating the four atoms by narrow positive
even smooth bumps preserves the common zero by the implicit-function theorem,
and the bumps may be chosen super-exponentially decaying. Hence positivity,
evenness, smoothness and rapid decay, separately or together, do not imply the
boundary nonvanishing homotopy. A proof for `H_t` must use the arithmetic
coupling of all theta modes.

## DN30. phase-current identities and the exact arithmetic remainder

Away from collisions let `theta=arg(h+i h_x)`. Direct differentiation gives

```text
theta_x=(h h_xx-h_x^2)/(h^2+h_x^2),                  (DN30.1)
theta_t=(h_x h_xx-h h_xxx)/(h^2+h_x^2).              (DN30.2)
```

The current is curl-free away from `F=0`; each collision contributes the
negative `2pi` vortex of DN27. For the Riemann kernel,

```text
H_t+i H_t'
 =1/2 int_R (1-u)e^(tu^2)Phi(u)e^(ixu)du.             (DN30.3)
```

The Fourier density changes sign at `u=1`; there is no positive-measure
argument. At `t=0`, using `H_0(x)=xi((1+ix)/2)/8`,

```text
H_0+iH_0'=[2xi(s)-xi'(s)]/16,  s=(1+ix)/2.           (DN30.4)
```

Thus the remaining bottom phase contains the full logarithmic derivative of
`xi`, including the prime Dirichlet series. Replacing it by its gamma phase or
asserting a Herglotz sign discards precisely the arithmetic zero channel.

The phase identities therefore give a clean conservation law but no sign.
The live obligation is an explicit prime--theta control of the signed transform
in (DN30.3)/(DN30.4), strong enough to preserve its boundary winding on every
expanding rectangle.
## DN31. degenerate heat collisions have explicit negative multiplicity

The perturbative sentence in DN27 can be made intrinsic. Let a nonzero real
analytic heat solution have, at `(t_*,x_*)`, a spatial zero of finite
multiplicity `m>=2`. Put `tau=t-t_*`, `y=x-x_*`, and write

```text
h(t_*,x_*+y)=a_m y^m+O(y^(m+1)),  a_m!=0.
```

Analyticity and `h_t=-h_xx` give the parabolic blow-up

```text
epsilon^(-m)h(t_*+epsilon^2 s,x_*+epsilon z)
 ->a_m exp(-s partial_z^2)z^m                      (DN31.1)
```

in `C^1` on compact `(s,z)` sets. For `s>0` the model is a scaled Hermite
polynomial with `m` simple real roots. For `s<0` it has no real roots when `m`
is even and only the root zero when `m` is odd. Hence exactly `floor(m/2)`
real pairs pass through the multiple collision.

Choose a small parabolic neighborhood whose boundary contains no common zero
of the model. The `C^1` convergence and homotopy invariance of Brouwer degree
then give the intrinsic local formula

```text
deg_(t_*,x_*)(h,h_x)=-floor(m/2).                      (DN31.2)
```

In particular a triple collision has degree `-1`, a quadruple collision degree
`-2`, and simultaneous separated collisions add. A nonzero analytic heat
solution cannot carry a curve of multiple zeros: differentiating `h=h_x=0`
along such a curve and using the PDE successively forces every spatial
derivative to vanish, hence `h` identically zero. Thus the collision set in a
compact rectangle is discrete unless the solution is trivial.

DN27.2 therefore extends without a regularity assumption:

```text
-deg(F,R,0)=sum_(collisions in R) floor(m_c/2).        (DN31.3)
```

The winding counts precisely the conjugate pairs created backward, including
all degenerate events; the earlier transverse perturbation is only an
alternative definition, not a missing hypothesis.
## DN32. certified failure of fixed-sign vertical phase velocity

The simplest producer for DN28 would make the phase on every vertical edge
monotone in heat time. By DN30.2 its numerator at `t=0` is

```text
J(x)=H_0'(x)H_0''(x)-H_0(x)H_0'''(x).                (DN32.1)
```

The 320-bit Arb certificate
`experiments/certify_dn30_vertical_phase_failure.py` evaluates the xi jet at
Arb-enclosed zeta zeros and proves

```text
J(x_1)<0,
J(x_35)>0,
x_35=223.7493183539852741712241574335... .            (DN32.2)
```

At a simple zero the denominator in DN30.2 is `H_0'(x)^2>0`, so these are
rigorous opposite signs of `partial_t arg(H_t+iH_t')`. Fixed-sign vertical
phase monotonicity is false for the actual Riemann kernel, not merely for the
generic counterexample DN29.

This does not affect the collision ledger DN27/DN31: the Brouwer degree identity
uses only the heat PDE and boundary nonvanishing, not a sign for phase velocity.
It closes only the proposed easy method of evaluating that degree.

## DN33. horizontal phase monotonicity returns to the all-Laguerre obligation

DN30.1 can be written

```text
theta_x=-L_1[H]/(H^2+H_x^2),
L_1[H]=H_x^2-HH_xx.                                  (DN33.1)
```

Thus a co-moving phase foliation based on `theta_x<0` asks for the first
Laguerre inequality. But the classical first inequality is only necessary, not
sufficient, for a real entire function to be Laguerre--Polya. The known
necessary-and-sufficient criteria require the full sequence of extended
Laguerre inequalities (Cardon, arXiv:0911.1122; Csordas--Vishnyakova 2013).
For Xi this is the all-degree obligation already indexed in the Jensen/de
Branges routes.

Therefore the boundary-degree theorem is genuine new bookkeeping, but its two
natural phase producers are now closed:

1. fixed-sign vertical velocity is rigorously false by DN32;
2. horizontal monotonicity based only on `L_1` is structurally insufficient,
   while upgrading to all extended inequalities re-enters the previously
   audited RH-equivalent all-degree target.

An arbitrary non-monotone boundary homotopy remains logically possible, but no
independent theta theorem produces it; specifying its winding to match the top
edge is exactly the missing real-zero count. This is the minimal failure point
of the spacetime-winding implementation, not a failure of DN27 itself.

## DN34. theta Fourier graph topology repairs the DN26 transfer failure

DN26 is a no-go for terminal polynomial/Taylor convergence, not for every
entire-function topology. Fix `tau<T` and put

```text
dmu_T(u)=(1/2)e^(Tu^2)Phi(u)du,
H_t(x)=int_R e^(-(T-t)u^2)e^(ixu)dmu_T(u).            (DN34.1)
```

The harmless factor `1/2` only converts the cosine integral to an integral on
`R`. The double-exponential decay of `Phi` gives
`int(1+|u|^m)dmu_T<infinity` for every m. If symmetric finite measures `nu_N`
are obtained by truncating u, partitioning the remaining compact interval, and
replacing each cell by one atom, then rationalizing the positive cell masses,
one has on every fixed rectangle

```text
F_N=(h_N,partial_x h_N) -> F=(H,partial_x H)
in C^1([tau,T]x[-X,X]).                               (DN34.2)
```

Indeed the four components in this `C^1` norm are Fourier transforms with
multipliers `1,u,u^2,u^3`. After a moment-tail truncation, the family

```text
u^j e^(-(T-t)u^2)e^(ixu),  0<=j<=3,
```

is uniformly Lipschitz in u for `(t,x)` in the rectangle. Riemann quadrature
therefore converges uniformly; rationalizing finitely many masses changes the
same norm by an arbitrarily small amount. No constant here depends on the
number of atoms. Equivalently, backward evolution from the terminal Fourier
kernel multiplies by a contraction `e^(-(T-t)u^2)`; the high-degree monomial
amplification in DN26 lies outside this topology.

Let `mu_R=min_(partial R)|(H,H_x)|`. Whenever `mu_R>0`, (DN34.2) and
`||F_N-F||_(C^0(partial R))<mu_R` give the straight-line nonvanishing homotopy
on the boundary. Hence

```text
deg(F_N,R,0)=deg(F,R,0).                              (DN34.3)
```

This proves a genuine non-naive entire transfer of the collision degree. It
does not estimate `mu_R` and does not evaluate the degree.

## DN35. commensurate rational quadratures make every finite winding algebraic

The preceding approximants may be chosen with atoms at `u=k delta` and positive
rational symmetric weights `a_k`. Choose the mesh so that

```text
q=exp(-(T-tau)delta^2) in Q,  0<q<1,
r=exp(-(T-t)delta^2),  y=delta x.                    (DN35.1)
```

Then, after deleting zero weights,

```text
p(r,y)=sum_(k=-K)^K a_k r^(k^2)e^(iky),
(h_N,h_(N,x))=(p,delta p_y).                         (DN35.2)
```

Both changes `(t,x)->(r,y)` and `(p,p_y)->(p,delta p_y)` preserve orientation.
On a horizontal side `r=q` or `1`, the substitution `w=tan(y/2)` turns
`(p,p_y)` into rational functions with rational coefficients. On a vertical
side whose `e^(iy)` is a root of unity, both components are polynomials in r
over a real algebraic number field. After clearing positive denominators, the
boundary change of argument is therefore an exact Cauchy index, decidable by
Sturm/subresultant chains. Thus every regular compatible finite rectangle has
an exact algebraic collision count, not merely a floating-point one.

These compatible rectangles and quadratures are dense in the required graph
topology. Rational q may approach 1 arbitrarily closely, roots of unity are
dense on the unit circle, and the moment-tail/Riemann argument of DN34 permits
the mesh to be chosen after the rectangle. One can in particular take regular
`tau_n downarrow 0`, `X_n to infinity`, and construct a separate exact
quadrature for each rectangle. The quantifier order is essential:

```text
choose R; establish mu_R>0; then choose quadrature error o(mu_R). (DN35.3)
```

There is no resulting cutoff bound uniform in X unless an arithmetic lower
bound for `mu_R` is supplied.

This collapses the three formerly separate implementations--entire transfer,
finite collision decision, and nonmonotone boundary homotopy--onto one common
obligation:

```text
prove from the theta/prime weights that the exact algebraic degrees in a
regular expanding exhaustion vanish, without inserting the bottom real-zero
count or an assumed boundary winding.                              (DN35.4)
```

Pressure checks prevent two hidden shortcuts. First, putting `tau=0` and
assuming an unperturbed positive boundary margin excludes every multiple
critical-line zero, a simplicity assertion stronger than RH; the correct form
uses regular `tau_n>0` tending to zero (or the DN27 perturbation). Second, DN23
allows the required margin to be log-squared exponentially small, while DN29
gives positive rational finite-frequency models with nonzero collision degree.
Hence neither qualitative convergence, positivity/evenness, nor finite
algebraic decidability proves (DN35.4). The transfer problem is closed; the
surviving common pillar is the theta-specific arithmetic value of the degree.

## DN36. the common degree pillar is exactly RH, not a weaker lemma

Fix `T` in the known real-rooted regime. Choose regular times `tau_n downarrow
0` and boundary-nonzero rectangles `R_(n,m)=[tau_n,T]x[-X_m,X_m]` exhausting
each strip, with `X_m to infinity`. Then

```text
deg((H,H_x),R_(n,m),0)=0 for every n,m                 (DN36.1)
```

is equivalent to RH (with harmless boundary perturbations if needed).

For the forward implication, DN31 says every interior collision has strictly
negative local degree. A compact degree ledger alone would still permit a
zero branch to enter from spatial infinity. DN22 removes that hidden escape:
for each fixed `tau_n>0` its high-zero theorem gives a height, uniform for
`t in [tau_n,T]`, beyond which all zeros are real and follow their explicit
quantiles. Thus every loss of real-rootedness in that time strip must occur in
a finite rectangle and is counted by the exhaustion. Zero degree means that no
collision occurs in `(0,T)`. Starting from real-rooted `H_T`, all `H_t` with
`t>0` are therefore real-rooted. Since `H_t->H_0` locally uniformly as
`t downarrow0`, Hurwitz closure of the Laguerre--Polya class gives that `H_0`
has only real zeros, which is RH.

Conversely, RH makes `H_0` real-rooted, and de Bruijn's forward preservation
makes every `H_t`, `t>=0`, real-rooted. An interior collision would, by the
Hermite blow-up DN31, have nonreal zeros immediately on its lower-time side,
a contradiction. Thus every regular rectangle has degree zero.

Consequently DN34--DN35 solve representation, convergence, and finite exact
decidability, but DN35.4 does not shrink the unknown mathematical content. The
minimal failure of this three-way route is now precise: no theta-specific
producer of the RH-equivalent zero-degree assertion survived DN29, DN32, and
DN33. It must not be counted as a weaker intermediate theorem.

## DN37. orientation-preserving boundary gauges only relocate winding

Let `F:partial R->R^2\{0}` and `A:partial R->GL^+(2,R)` be continuous. Polar
decomposition contracts the positive-definite factor of A to the identity, so
A is homotopic to a rotation loop Q. If

```text
ind(A)=wind(Q e_1),
```

then the circle action gives the exact formula

```text
wind(AF)=wind(F)+ind(A).                              (DN37.1)
```

If A extends continuously to `R` through `GL^+(2,R)`, its boundary loop is
null-homotopic and `ind(A)=0`; hence `deg(AF,R,0)=deg(F,R,0)`. Conversely, a
boundary gauge which straightens a nonzero-degree F to zero winding must have
`ind(A)=-wind(F)` and cannot extend nonsingularly across R. It has merely moved
the unknown integer into the gauge obstruction.

The quantitative margin obeys

```text
|AF|>=sigma_min(A)|F|.                               (DN37.2)
```

Thus allowing `sigma_min(A)` to vanish is exactly a hidden loss of the boundary
gap; requiring a uniformly invertible extension preserves both the degree and
the conditioning up to its stated singular-value factor. This rules out a
generic gamma/theta coordinate change as an evaluator of DN27, while leaving a
genuinely arithmetic nonvanishing homotopy logically possible.

## DN38. first-order logarithmic shears cannot repair the DN32 sign failure

The most natural phase normalization is

```text
F_a=(h,h_x+a(t,x)h)=A_a(h,h_x),
A_a=[[1,0],[a,1]].                                   (DN38.1)
```

For every continuous a this shear has determinant one and extends over the
rectangle, so DN37 already gives the same collision degree. More sharply, at
any simple real zero `h=0,h_x!=0`, writing
`theta_a=arg(h+i(h_x+ah))` and using `h_t=-h_xx` gives

```text
partial_t theta_a=h_xx/h_x,
partial_x theta_a=-1.                                (DN38.2)
```

Both values are independent of a, `a_t`, and `a_x`. Therefore the certified
opposite signs at the first and 35th Xi zeros in DN32 survive every continuous,
time-dependent first-order shear. Adding a gamma logarithmic derivative to
`H_x` cannot create fixed-sign vertical phase. A more general extending gauge
may alter pointwise phase velocity, but DN37 forces its total added boundary
winding to zero; a nonextending or singular gauge encodes the missing degree.

## DN39. the first theta mode already has a certified nonreal zero

For `u>=0` put

```text
T_1(u)=2pi e^(5u/2)(2pi e^(2u)-3)e^(-pi e^(2u)),
H_1(z)=int_0^infinity T_1(u)cos(zu)du.                 (DN39.1)
```

The 256-bit Arb certificate
`experiments/certify_first_theta_mode_nonreal_zero.py` proves a unique zero in
the radius `10^-12` complex box centered at

```text
20.6253460059217176013299
 +2.69715184233951963250594 i.                        (DN39.2)
```

It integrates on `[0,4]` and bounds both omitted tails by explicit upper
incomplete-gamma expressions. The complex interval-Newton image lies strictly
inside the box, `H_1'` excludes zero, and the box is strictly above the real
axis. Hence the first-mode transform is not Laguerre--Polya and cannot be the
collision-free endpoint of a theta-mode homotopy.

## DN40. adding the second mode crosses a regular amplitude collision

Let `h_n` be the cosine transform of `T_n` and
`H_lambda=h_1+lambda h_2`. A common zero is equivalent, when `h_2!=0`, to

```text
W(x)=h_1h_2'-h_1'h_2=0,
lambda=-h_1/h_2.                                     (DN40.1)
```

The independent 256-bit Arb certificate
`experiments/certify_two_theta_mode_collision.py` applies interval Newton to W
and proves a unique root in the radius `10^-12` interval centered at

```text
x_*=22.142377661076422295967597056922402,
lambda_* in [0.916291688 +/- 8.82e-10] subset (0,1).  (DN40.2)
```

It also proves `h_2(x_*)!=0` and
`H_(lambda_*)''(x_*)!=0`. The Jacobian of
`(H_lambda,partial_x H_lambda)` in
`(lambda,x)` is therefore `h_2 H_lambda''!=0`: this is a regular collision.
The first arithmetic mode does not perturbatively preserve a nonvanishing
phase; it removes the DN39 branch by crossing the real double-zero wall.

## DN41. every finite theta-mode truncation has infinitely many nonreal zeros

The preceding phenomenon is not confined to `N=1`. Let

```text
K_N(u)=sum_(n=1)^N T_n(u),
H_N(z)=int_0^infinity K_N(u)cos(zu)du.                 (DN41.1)
```

Each `T_n'(0)=T_n(0)a_n`, where

```text
a_n=5/2+4r_n/(2r_n-3)-2r_n,  r_n=pi n^2.
```

J18 proves `a_1>0`, while `a_n<0` for every `n>=2`. The full modular kernel is
even, so absolute convergence gives `sum_(n>=1)T_n'(0)=Phi'(0)=0`. Therefore

```text
K_N'(0)=-sum_(n>N)T_n'(0)>0                           (DN41.2)
```

for every finite N. Since `K_N''` is integrable, two integrations by parts and
Riemann--Lebesgue give the exact real-axis asymptotic

```text
H_N(x)=-K_N'(0)/x^2+o(x^-2).                          (DN41.3)
```

Thus H_N is eventually negative on both real tails and has only finitely many
real zeros. On the other hand its double-exponential kernel gives

```text
max_(|z|=R)|H_N(z)|
 <=C_N int_0^infinity exp((R+9/2)u-pi e^(2u))du,
log M_N(R)=O(R log R),                                (DN41.4)
```

so H_N is an even entire function of order at most one. If it had only
finitely many total zeros, Hadamard factorization would give
`H_N=e^(az+b)P(z)`. Evenness forces `a=0` and P even, contradicting the
nonzero algebraic decay (DN41.3). Hence H_N has infinitely many zeros, only
finitely many real: infinitely many are nonreal for every finite N.

The exact shift identity

```text
T_n(u)=n^(-1/2)T_1(u+log n)                           (DN41.5)
```

identifies the load-bearing difference. Only the infinite arithmetic shift
measure cancels the cusp at zero; every finite truncation leaves nonreal
defects, which can only escape to spatial infinity as N grows. Consequently no
finite theta-mode truncation can serve as a real-rooted base for the DN27
homotopy. This does not decide the full infinite kernel or RH.

## DN42. no nonzero finite real theta-mode combination is Laguerre--Polya

DN41 extends from unit partial sums to the whole finite coefficient space. Let

```text
K_c(u)=sum_(n=1)^N c_nT_n(u),  c_n in R,
H_c(z)=int_0^infinity K_c(u)cos(zu)du,                (DN42.1)
```

with c nonzero. Suppose every odd derivative of `K_c` vanished at zero. Since
each T_n is entire in u, `K_c` would be even by analytic continuation. But as
`u->-infinity`, putting `q=e^(2u)` gives

```text
K_c(u)=2pi e^(5u/2) sum_(k>=0) b_k pi^k e^(2ku)
                 sum_(n=1)^N c_n n^(2k+2),           (DN42.2)
b_0=-3,
b_k=(-1)^(k-1)(2k+3)/k! !=0  (k>=1).
```

Evenness would identify this ordinary exponential expansion with the
double-exponential decay of `K_c(u)` as `u->+infinity`. Hence every coefficient
`sum c_n n^(2k+2)` must vanish. The first N such equations form a Vandermonde
system in `n^2`, forcing c=0, a contradiction.

Thus some odd derivative is nonzero. Let `2j+1` be the first. Repeated
integration by parts gives

```text
H_c(x)=(-1)^(j+1)K_c^(2j+1)(0)x^(-2j-2)
       +o(x^(-2j-2)).                                 (DN42.3)
```

So H_c again has only finitely many real zeros. The order-at-most-one estimate
DN41.4 holds for every fixed finite combination, and the same Hadamard argument
gives infinitely many total zeros. Therefore H_c has infinitely many nonreal
zeros for every nonzero finite real coefficient vector c.

The collision-free Laguerre--Polya cone has empty intersection with the
nonzero finite theta-mode span. Consequently no straight or nonmonotone path
inside any finite mode coefficient space can produce an LP base; exact
infinite modular completion is a load-bearing operation, not a limit that can
be postponed until after finite real-rooted approximants.
