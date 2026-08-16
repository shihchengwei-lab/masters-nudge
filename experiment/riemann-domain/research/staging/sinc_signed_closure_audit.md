# compact sinc 的 signed dilation closure 與係數範數稽核

日期：2026-08-16。沿用 SM2：

```text
f(x)=sinc(x)1_(0<x<=1),
h(x)=-P f(x)>=0,
W(s)=fhat(s),  hhat(s)=-zeta(s)W(s).
```

L30證 `W` 在 `Re s>0` 無零。Báez-Duarte general strong theorem因此給
`RH iff f in closure span{h(kx)}`。本檔檢查 signed coefficients是否存在較弱、
bounded-norm 的上游機制。

## SC1. exact critical-line optimization

對有限係數 `c=(c_1,...,c_N)` 設

```text
H_c(x)=sum_(k<=N)c_k h(kx),
C_c(s)=sum_(k<=N)c_k k^(-s).
```

Mellin--Plancherel精確給

```text
||f-H_c||_2^2
=1/(2pi)int_R |W(1/2+it)|^2
 |1+zeta(1/2+it)C_c(1/2+it)|^2dt.                      (SC1.1)
```

所以這個 sinc closure仍是帶 zero-free outer weight `W` 的 Nyman mollifier問題。
`W`只改善 large-`t` integrability，不消 zeta zeros。

## SC2. common-tail cancellation是必要條件

令 `I=int_0^1f`。因 `h(kx)=I/(kx)` on `x>1`，

```text
H_c(x)=I C_c(1)/x  (x>1),
int_1^infinity|f-H_c|^2dx=I^2|C_c(1)|^2.               (SC2.1)
```

因此任何 closure sequence必須有

```text
C_c(1)=sum c_k/k ->0.                                  (SC2.2)
```

這是 signed cancellation condition；SM3證 nonnegative coefficients無法同時滿足它
並在 `(0,1]`逼近 target。

## SC3. natural synthesis norm必定發散

定義 triangle/synthesis norm

```text
K(c)=sum_(k<=N)|c_k|/sqrt(k).                           (SC3.1)
```

因 `||h(k dot)||_2=k^-1/2||h||_2`，這正是控制 dilation synthesis operator的
自然 weighted `ell1` norm；且在 critical line `|C_c(1/2+it)|<=K(c)`。

取任一已知 critical-line zero `rho=1/2+i gamma`，multiplicity為 `m>=1`。
若一列 approximants滿足 `K(c)<=K_0`，由 zeta在 `rho`附近連續且 `W(rho)!=0`，
存在固定 interval `J` 使

```text
|zeta(1/2+it)C_c(1/2+it)|<=1/2,
|W(1/2+it)|>=|W(rho)|/2  on J.
```

代入 (SC1.1) 得一致正 lower bound，故不可能 closure。因此

```text
||f-H_(c_j)||_2->0  =>  K(c_j)->infinity.               (SC3.2)
```

更定量地，由 `|zeta(1/2+i(gamma+u))|<=C|u|^m`，可取
`|u|<=c K(c)^(-1/m)`，得到

```text
||f-H_c||_2^2 >= c_rho,W K(c)^(-1/m)                   (SC3.3)
```

（當 `K(c)` 足夠大）。故 bounded-norm projector嚴格不存在；成功逼近必須以增長的
signed coefficient mass在每個 critical zero附近形成更窄 transition。

## SC4. scale-support lower bound已有文獻障礙

Burnol arXiv:math/0103058 對 classical Nyman distance `D(lambda)`證（RH失敗時
distance不趨零；在 RH情形）

```text
liminf_(lambda->0) D(lambda)sqrt(log(1/lambda))
 >=[sum_rho m_rho^2/|rho|^2]^(1/2).                    (SC4.1)
```

這顯示 critical-line zeros即使在 RH成立時也強迫至多 `1/sqrt(log scale)` 型 closure；
不存在由 finite scale得到快速 uniform inverse的捷徑。Báez-Duarte
arXiv:math/0205003 的 explicit Möbius approximants則只在假設 RH後證 distance衰減，
不是 unconditional upper bound。

SC3是針對 compact sinc coefficient norm的直接版本；SC4是既有 Nyman scale-distance
版本。兩者都只給必要下界，不產生所缺 upper bound。

## SC5. Selberg nudge：dilation coordinate是 smaller-scale target

對 indicator kernel `chi`，

```text
B_N(k)=sum_n mu(n)chi(kn/N)=M(floor(N/k)).              (SC5.1)
```

對 compact sinc則精確為

```text
B_N(k)=sum_n mu(n)f(kn/N)=A_w(N/k),                     (SC5.2)
```

即同一 sinc-smoothed target在較小 real scale。除數反演給 all-scale identity

```text
sum_(k<=N)A_w(N/k)=f(1/N).                              (SC5.3)
```

正規化 `G(X)=A_w(X)/sqrt(X)` 後，

```text
G(N)+sum_(2<=k<=N)k^(-1/2)G(N/k)=f(1/N)/sqrt(N).       (SC5.4)
```

係數 `k^-1/2` 在 `ell1`、`ell2` 均臨界發散。故隔離 `k=1` 確實先要求控制全部
smaller scales；這是義務遞迴，不是 strict contraction。其 Mellin-scale symbol仍為
`zeta(s+1/2)`，與 LQ5完全一致。

## SC6. recent Gram compression不給 closure upper bound

arXiv:2510.18132 對經 Mellin Gaussian smoothing的 Beurling--Nyman ladder Gram entries
證 polynomial off-diagonal decay與 block-compressibility。這是 unconditional matrix
structure，但 abstract/theorems沒有證 target distance趨零；SC1的 reciprocal-zeta
mollifier upper bound仍缺。故不能由 sparse Gram外觀推斷 RH。

## SC7. 固定頻率窗的 tail-exact projector無條件存在（已證）

固定 `T>0`，寫
`C(1/2+it)=sum_k d_k exp(-it log k)`，其中 `d_k=c_k/sqrt(k)`，而
`C(1)=sum_k d_k/sqrt(k)`。滿足 `C(1)=0` 的有限多項式在 `L2(-T,T)` 稠密。

若 `F` annihilate此 family，Paley--Wiener entire function
`G(z)=int_(-T)^T F(t)exp(izt)dt` 必有
`G(log k)=lambda/sqrt(k)`。若 `lambda=0`，G在 `[0,R]` 有約 `e^R` 個 zeros，
違反非零 exponential-type entire function的 `O(R)` zero count。若 `lambda!=0`，
同理 `G(z)-lambda e^(-z/2)` 恒為零，但 G在 real line屬 L2、`e^(-x/2)`不屬，
矛盾。故 annihilator為零。

critical-line zeta連續且非零 a.e.，其乘法算子 range稠密；W又無零。因此對每個
fixed `T,delta>0`，存在 finite C使

```text
C(1)=0,
int_(-T)^T |W|^2|1+zeta C|^2dt < delta^2.              (SC7.1)
```

這不證 RH，因完全沒有控制 `K(C)=sum|d_k|`。SC3保證 delta趨零且窗口含 critical
zero時 K必趨無窮。

## SC8. global closure所需的 norm-growth門檻（已證）

對 W分部積分給
`W(1/2+it)=f(1)/(1/2+it)+O((1+|t|)^-2)`，故 `|W|<<1/(1+|t|)`。
再用無條件 convexity bound
`|zeta(1/2+it)|<<_eta(1+|t|)^(1/4+eta)` 與 `|C|<=K(C)`，得

```text
int_(|t|>T)|W|^2|1+zeta C|^2dt
 <<_eta T^-1+K(C)^2 T^(-1/2+2eta).                    (SC8.1)
```

所以若有 `T_j->infinity`、tail-exact C_j、local error趨零，且對某
`0<alpha<1/4` 有 `K(C_j)=o(T_j^alpha)`，則 global error趨零，推出 RH。
反之若 RH成立，先以趨零修正把 `C_j(1)->0` 改成 exact zero，再對每個 fixed
approximant後選足夠大的 T_j，即可滿足任意預定 `alpha<1/4` 的 growth條件。

定義
`kappa(T,delta)=inf{K(C):C finite,C(1)=0,local error<=delta}`。SC7證其有限；
真正缺口是構造 `delta(T)->0` 使對某 `alpha<1/4` 有
`kappa(T,delta(T))=o(T^alpha)`。這嚴格寬於 bounded-norm projector。

## SC9. quantitative biorthogonal文獻的 spectrum hypotheses不適配 `log k`

Fattorini--Russell及 Cannarsa--Martinez--Vancostenoble 的 moment-method upper bounds
要求 uniform/asymptotic gap與 parabolic型 polynomial counting。Gonzalez-Burgos--Ouaili
雖允許有限 condensation groups而不要求 global gap，其 H6仍假設 counting function
為 power-law級，且每個 condensation group cardinal有固定上界。對 `lambda_k=log k`，
相鄰 gap約 `1/k`，而 `[0,R]` counting約 `e^R`；兩類假設都失敗，不能給 kappa upper
bound。Trefethen對另一個 Müntz system證 coefficient cost可隨 `1/delta` exponential
爆炸，說明 qualitative density不保溫和 norm，但其 lower bound不直接適用本 target。

Primary sources: https://doi.org/10.3934/dcdss.2020082 ;
https://arxiv.org/abs/2401.17128 ; https://doi.org/10.1007/s44007-022-00039-6

## SC10. 用 zeta 二次矩把 tail 門檻提升到近 `T^(1/2)`（已證）

SC8用了逐點 convexity，並非最合適。令
`Z(X)=int_0^X|zeta(1/2+it)|^2dt`。經典 Ingham--Atkinson 二次矩公式特別給

```text
Z(X) << X log(eX).                                    (SC10.1)
```

由 dyadic decomposition（或 Stieltjes partial summation），

```text
int_T^infinity |zeta(1/2+it)|^2/t^2 dt << log(eT)/T.  (SC10.2)
```

再用 `|C(1/2+it)|<=K(C)` 及 `W=O(1/t)`，得到完全不依賴 C 的

```text
int_(|t|>T)|W|^2|1+zeta C|^2dt
 << T^-1+K(C)^2 log(eT)/T.                            (SC10.3)
```

所以 SC8 的充分條件可嚴格放寬成

```text
K(C_T)^2 log T/T ->0,                                 (SC10.4)
```

例如任意 `K=o(T^alpha)`、`alpha<1/2` 均足夠。反向仍成立：RH若真，先取 global
closure approximants，再把 T 選到遠大於 `K^2 log T`。故新的精確 live target是找
`delta(T)->0` 使

```text
kappa(T,delta(T))^2 log T/T ->0.                      (SC10.5)
```

這是成熟均值定理直接造成的實質縮減，不含 Lindelof、RH或逐點臨界界。

Primary source: F. V. Atkinson, *A Mean Value Property of the Riemann
Zeta-Function*, JLMS 23 (1948), 128--135,
https://doi.org/10.1112/jlms/s1-23.2.128

## SC11. arbitrary-length mollifier lower bound不能控制 kappa

Radziwill 的 Theorem 1 對長度 `N=T^theta`、具規定 normalization及 polynomial-size
coefficients的 Dirichlet mollifier，給 high window `[T,2T]` 上 normalized residual
`I(M)>=c/theta`。這是與本 target相鄰的無條件成熟定理，但不能直接填 SC10.5：

1. 它是 lower bound，不是所需的 coefficient-cost upper bound；
2. 乘上本問題 `|W(t)|^2 asymp T^-2` 後，該 shell只強迫約 `c/(T theta)`，本身趨零；
3. `K=sum|c_n|/sqrt n` 不限制最大 support N，故不能把 `theta=log N/log T`
   改寫成 K 的函數；
4. theorem的 `a(1)=1`/coefficient hypotheses亦不是 tail-exact kappa class的自動條件。

標準 Selberg mollifier若 `N=T^theta`，自然有 `K=O(sqrt N)`；SC10允許 fixed
`theta<1`，但已知 shell mean error約 `1/theta`，不提供 compact low-frequency window
所需的 error趨零。令 theta增大則自然 K超出 (SC10.4)。因此成熟 mollifier theorem既
沒有完成構造，也沒有排除允許任意 support/係數的 controlled projector。

Primary source: M. Radziwill, *Limitations to mollifying zeta(s)*,
https://arxiv.org/abs/1207.6583

Selberg nudge所要求的獨立性稽核結論也因此明確：`kappa` 本身仍是 RH 等價義務；本輪
真正獨立控制的只有由 zeta 二次矩導出的 **global tail**。local `kappa` upper bound尚
沒有任何不依賴 reciprocal-zeta/zero exclusion的性質可用，不能把定義改寫當成進展。

## SC12. bounded-coordinate Pechersky theorem留下 support-complexity介面

Andersson 的 Theorem 1/5處理
`sum_(n<=N) a_n n^(it-1)`、`|a_n|<=Phi(n)`，其 fixed-window L2 density判準為

```text
sum_(n>=2) log Phi(n)/(n log^2 n)=infinity.            (SC12.1)
```

代入 `a_n=c_n sqrt(n)`，就是本線的 critical-line polynomial
`sum c_n n^(-1/2+it)`。例如取

```text
Phi(n)=n^epsilon(n),  epsilon(n)=1/log log n,
|c_n|<=n^(-1/2+epsilon(n)).                            (SC12.2)
```

(SC12.1)仍發散，而截至 support N 的 synthesis norm滿足粗略

```text
K <= sum_(n<=N)n^(-1+epsilon(n))=N^(o(1)).             (SC12.3)
```

tail constraint不能在逼近後任意加常數；正確作法是從一開始用 constrained atoms

```text
c_n[n^(-1/2+it)-n^-1],  n>=2,                         (SC12.4)
```

即同步令 `c_1=-sum_(n>=2)c_n/n`。在 (SC12.2) 下，新增 constant perturbation的總
Hilbert norm由 `sum n^(-3/2+epsilon(n))<infinity` 控制；Pechersky所需的 directional
absolute divergence不會被一個 absolutely summable perturbation消掉。因此同一 proof
給 exact-tail constrained density，且 c1一致 bounded。配 fixed-window regularization與
zeta multiplication，這強化 SC7：定性局部逼近可要求 coordinate envelope，且 K對
**support N** 只次冪增長。

但 source的 Pechersky/quasianalytic proof沒有給完成 `(T,delta)` 逼近所需的最大 support
`N(T,delta)`。SC10需要的是對 **window T** 的 `K^2logT/T->0`；`N^(o(1))` 若 N可對 T
超快增長仍完全不夠。因此這是可代入/淘汰條件清楚的新介面，不是 kappa upper bound：
下一個合格 theorem必須再給有效 support complexity，使 (SC12.3)實際小於
`sqrt(T/logT)`。

Primary source: J. Andersson, *On a problem of Ramachandra and approximation of
functions by Dirichlet polynomials with bounded coefficients*,
https://arxiv.org/abs/1207.4624

## SC13. support-free `ell2` tail estimate被 log-cluster反例排除（已證）

SC12的 envelope另給 `sum|d_n|^2<infinity`，其中 `d_n=c_n/sqrt n`。但不能把 SC10
的 K直接換成 ell2。固定 `T,M`，取很大的 N並令

```text
d_n=1/M  (N<n<=N+M),
d_1=-sum_(N<n<=N+M)d_n/sqrt n.                        (SC13.1)
```

則 exact `C(1)=0`，且

```text
sum|d_n|^2=1/M+O(1/N),  K=1+O(N^-1/2).                (SC13.2)
```

若 `N>=16TM`，對 `t in [T,2T]` 有

```text
|M^-1 sum_(N<n<=N+M)n^(-it)-N^(-it)|
 <=2TM/N<=1/8,
```

而 d1修正為 `O(N^-1/2)`；故 `|C(1/2+it)|>=1/2`。由 `W zeta` 在任何正長
interval不恒零，

```text
int_T^(2T)|W zeta C|^2dt >=c_T>0                     (SC13.3)
```

但 ell2 norm可令 M趨無窮而歸零。因此不存在只依 T、且對任意 support一致的
`tail <=A(T)sum|d_n|^2`；任意可用的 quadratic bound必另懲罰 log-frequency cluster
mass或限制最大 support。

這也解釋 twisted-second-moment/GCD theorem為何不能直接代入。Bettin--Chandee--
Radziwill 的 arbitrary-coefficient asymptotic仍限 length約 `T^(1/2+delta)`；GCD matrix
spectral bounds描述充分長平均後的 arithmetic kernel，沒有覆蓋 `N>>TM` 時幾乎相同的
log frequencies。故 ell2/GCD不能消除 SC12的 `N(T,delta)` 缺口。

Primary sources: https://arxiv.org/abs/1411.7764 ;
https://arxiv.org/abs/1210.0741 ; https://arxiv.org/abs/1407.5403

## SC14. Selberg nudge：不得由 target regularity偷渡 zero exclusion

另一個可能捷徑是先把 regularized reciprocal
`g_epsilon=-conj(zeta)/(|zeta|^2+epsilon)` 作 Sobolev/analytic approximation，再宣稱
其 coefficients有效衰減。但 epsilon趨零時，g的 derivatives在 zeta zeros附近按
epsilon負冪爆炸；其複解析延拓距離又直接由 off-line zeros決定。無條件 PNT
zero-free-region餘項只控制 `1/zeta` 在 `Re s`接近 1 的區域，不能提供 critical line
所需、uniform-in-epsilon 的 analytic strip或 Fourier decay。任何足以推出 SC10.5的
此類 regularity假設都必須先作 zero-exclusion audit；目前沒有獨立 PNT input可代入。

## SC15. Gaussian cluster norm給第二個無條件 tail criterion（已證）

SC13排除 ell2-only，但也指出正確解析度。寫 `d_n=c_n/sqrt n`，對 `U>=2` 定義

```text
B_U(C)^2=sum_(j>=0)(sum_(j/U<=log n<(j+1)/U)|d_n|)^2. (SC15.1)
```

用在 `[U,2U]` 下方有固定正下界的 centered Gaussian majorant。其 Fourier transform為
`O(U exp(-cU^2 xi^2))`；展開 `|C|^2` 並按 (SC15.1) 分箱，Gaussian discrete
convolution kernel有 bounded ell1 norm，故

```text
int_U^(2U)|C(1/2+it)|^2dt << U B_U(C)^2.              (SC15.2)
```

再用 `|C|<=K`、Cauchy--Schwarz及 Ingham的無條件四次矩
`int_U^(2U)|zeta|^4dt<<Ulog^4U`，得

```text
int_U^(2U)|W zeta C|^2dt
 << K(C) B_U(C) log^2U/U.                             (SC15.3)
```

對 dyadic `U=2^rT`，(SC15.1)的 partition精確 refine T-partition，故
`B_U<=B_T`。求和後

```text
int_(|t|>T)|W|^2|1+zeta C|^2dt
 << T^-1+K(C)B_T(C)log^2T/T.                          (SC15.4)
```

所以除 SC10外，另一個充分條件是

```text
K(C_T)B_T(C_T)log^2T/T ->0.                           (SC15.5)
```

它對 clustered coefficients比 K-square bound強；SC13反例恰有 B_T約 K，故沒有矛盾。

對 SC12 envelope `|d_n|<=b_n=n^(-1+epsilon(n))`、support `n<=N`，每個低於 T的
frequency bin只有 O(1) 個整數，而高端以 Cauchy估計，嚴格有

```text
B_T(C)^2 << 1+T^-1 sum_(T<n<=N)n^(-1+2epsilon(n)).    (SC15.6)
```

取 `epsilon(n)=1/loglog n` 時，右端第二項為 `T^-1 N^o(1)`。因此 envelope在 log
clusters上確有額外平方根平均；典型 power bookkeeping把可容許 K由近 `T^(1/2)`
推寬至近 `T^(3/4)`（須保留 (SC15.6) 的 slowly varying factors）。但 N仍可能對 T
超快增長，故 (SC15.5)尚未由 Pechersky theorem自動成立。

Primary source for the fourth moment: A. E. Ingham, *Mean-Value Theorems in the
Theory of the Riemann Zeta-Function*,
https://doi.org/10.1112/plms/s2-27.1.273

## SC16. zero-free beta-kernel ladder移除任何固定 polynomial norm門檻（已證）

sinc的 `W~1/t` 是端點 jump造成，不是 Müntz closure的硬限制。對任意固定整數
`m>=0` 取

```text
f_m(x)=x(1-x)^m 1_(0<x<1),
W_m(s)=int_0^1 f_m(x)x^(s-1)dx
      =B(s+1,m+1)=m!/prod_(r=1)^(m+1)(s+r).            (SC16.1)
```

`W_m` 在 `Re s>0` 無零，且 `|W_m(1/2+it)|<=m!|t|^(-m-1)`。令
`h_m=-P f_m`；對 `x>1` 仍精確有 `h_m(x)=I_m/x`，故 `C(1)=0` 時 physical error
甚至 support於 `(0,1]`。Mellin--Plancherel給同一 exact identity

```text
||f_m-sum c_kh_m(k dot)||_2^2
=1/(2pi)int|W_m|^2|1+zeta C|^2dt.                    (SC16.2)
```

closure推出 RH在此可直接驗證，不需額外 criterion：若 `rho`是 `Re rho>1/2` 的 zeta
zero，則 error的 Mellin value恆為 `W_m(rho)!=0`；因 error support於 `(0,1]`，

```text
|W_m(rho)|<=||error||_2/sqrt(2Re(rho)-1).             (SC16.2a)
```

故 global error不可能趨零。functional equation再排除對稱的左半零點。

用 zeta二次矩逐 dyadic shell求和，對 fixed m 得

```text
tail_m(T,C)
 <<_m T^(-2m-1)+K(C)^2 logT/T^(2m+1).                (SC16.3)
```

同理把 SC15的 Gaussian cluster lemma與 Ingham四次矩代入，得

```text
tail_m(T,C)
 <<_m T^(-2m-1)+K(C)B_T(C)log^2T/T^(2m+1).           (SC16.4)
```

因此對每個 fixed polynomial exponent A，都可先固定 `m>A`，使任何
`K=O(T^A)`（或相應 cluster-product polynomial bound）自動通過 global tail。這是一個
all-m公式，不是逐 degree數值證書，也沒有假設 `1/zeta` regularity。

量詞不循環：若 local construction先在某 fixed `m_0` 給 polynomial exponent A，則對
任何 `m>=m_0`，同一 coefficients仍可用，因

```text
W_m(s)/W_(m_0)(s)
=constant/prod_(r=m_0+2)^(m+1)(s+r)
```

在 critical line一致 bounded。故可在 theorem取得後一次固定
`m>max(m_0,A)`；local error不惡化超過 fixed constant，tail exponent則真正提升。

但它沒有單獨證 RH：目前 Pechersky只給 K對 support為 `N^o(1)`，未證 K對 window T
具有任何 fixed polynomial exponent。SC16把 live gap精確放寬成：只要找到 **某個有限
次數的 polynomial-in-T local construction**，即可選一個固定 beta kernel完成 closure。
若 construction仍是 exponential/superpolynomial cost，fixed m ladder不足。

## 結論（更新）

signed dilation route現在有三個同時必要條件：

1. `C_c(1)->0` 消共同 tail；
2. `K(c)->infinity` 穿過已知 critical zeros；
3. 儘管係數增長，仍須使 weighted error (SC1.1)在整條 critical line趨零。

現有 Burnol/Radziwill lower bounds、conditional Möbius approximants與 Gram compression
只描述必要障礙或條件式 3，沒有 unconditional local upper bound。SC10把允許的 norm
growth由 `T^(1/4-)` 放寬到 `sqrt(T/log T)` 以下，確實縮小了充分條件；但 kappa 的
local控制仍未取得。任何 bounded-norm projector已被 SC3排除；任何 smaller-scale
recursion已被 SC5判為 critical/noncontractive。RH仍未證。

### SC16a. 最新 nudge 的 target-change 稽核（已證；不補 local cost）

令 `E_(m,C)=f_m-sum_k c_k h_m(k dot)`、`R_C=1+zeta C`。對相同的 finite
coefficient vector，pointwise Mellin identity為

```text
Ehat_(m,C)=W_m R_C=(W_m/W_(m_0))Ehat_(m_0,C).        (SC16.5)
```

這不是從核衰減猜測不同 target的逼近品質；`f_m,h_m`共同更換，而 residual `R_C`
不變。對 `m>=m_0`，

```text
sup_(Re s=1/2)|W_m/W_(m_0)|
 <=(m!/m_0!)/prod_(r=m_0+2)^(m+1)(r+1/2)<infinity. (SC16.6)
```

故每個 window都有

```text
||Ehat_(m,C)||_L2(|t|<=T)
 <=M_(m,m_0)||Ehat_(m_0,C)||_L2(|t|<=T).            (SC16.7)
```

`C(1)=0`亦與 m無關。因而有嚴格 conditional theorem：若某 fixed `m_0,A` 存在
`delta(T)->0`及 tail-exact `C_T`，使

```text
||W_(m_0)(1+zeta C_T)||_L2(|t|<=T)<=delta(T),
K(C_T)<=T^A,                                         (SC16.8)
```

則一次固定 integer `m>max(m_0,A)`，由 (SC16.7)、(SC16.3)得到 global closure，再由
(SC16.2a)推出 RH。cluster版以 `K(C_T)B_T(C_T)<=T^A`及 (SC16.4)取代。

循環性邊界：SC16.5--SC16.7只用 beta/Gamma代數，未用 `1/zeta`、Mertens臨界界或
zero exclusion；但 (SC16.8) 的 polynomial local upper目前未證，且正是足以導出 RH的
新義務。不得把 conditional theorem或 qualitative density記成證明。

## 2026-08-16 階段性收尾

- 已證：exact Mellin reduction、tail constraint、bounded-norm no-go、fixed-window
  density、二次矩/cluster tail、ell2-only反例及 beta升階公式。
- 已淘汰的是具體機制：bounded K、support-free ell2、critical reciprocal regularity、
  small-scale contraction；controlled-growth projector仍存活。
- ordinary-Laguerre一般 asymptotics/frame檢索已停；SK5.2與 Lambert/sinc遞迴維持封存。
- 最新最小缺口是 (SC16.8) 或其 cluster-product版本。Pechersky只有 support-relative
  `N^o(1)`，沒有 window-relative polynomial rate。
- 下一輪第一步：只量化 Andersson--Pechersky 選取過程的 support complexity，直接驗收
  (SC16.8)；在取得 rate前不再增加 qualitative density結果。
- RH尚未證明；本階段停止自動續攻。

## SC17. consistency correction: the polynomial-window target is equivalent RH

SC8 and SC10 already recorded the converse quantifier: under RH, take any
sequence of finite global-closure approximants first, and only afterwards make
the window T large compared with their finite costs. Therefore for every fixed
`A>0`, SC16.8 is not merely sufficient but equivalent to RH. Explicitly, if
global errors are `epsilon_j->0` and costs are `K_j<infinity`, choose
`T_j^A>=K_j`; on `[T_j,T_(j+1))` reuse the j-th approximant. Its local error is
at most its global error and tends to zero.

Thus `delta(T)->0` plus `K<=T^A`, with remote support allowed and no prescribed
delta-rate, has no effective scale content. SC16 remains a valid conditional
proof, but AP2.5/Handoff-1 must be indexed as an exact RH-equivalent endpoint.
Only a natural same-scale formula/support rule or a non-reparameterizable error
rate could be a genuinely stronger intermediate target.
