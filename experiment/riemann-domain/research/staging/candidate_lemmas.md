# 候選引理與已證結果

## L1（已證）：有限 Li 正性不能排除高處離線四元組

固定整數 `N≥1` 及 `β∈(0,1)\{1/2}`。令

`Q(β,γ)={β+iγ, β-iγ, 1-β+iγ, 1-β-iγ}`

及

`q_n(β,γ)=Σ_{ρ∈Q(β,γ)} [1-(1-1/ρ)^n]`。

則存在 `Γ=Γ(N,β)`，使 `γ>Γ` 時，對每個 `1≤n≤N` 都有 `q_n(β,γ)>0`。

### 證明

由共軛配對，

`q_n=2 Re(L_n(β+iγ)+L_n(1-β+iγ))`。

對固定 n 使用有限二項式展開

`L_n(ρ)=Σ_{k=1}^n (-1)^(k+1) C(n,k) ρ^(-k)`。

若 `a` 固定且 `γ→∞`，直接由 `(a+iγ)^(-k)` 得

- `Re(1/(a+iγ))=a/γ²+O(γ^-4)`；
- `Re(1/(a+iγ)²)=-1/γ²+O(γ^-4)`；
- 對 `k≥3`，所有實部合計至多為 `O_{n,a}(γ^-4)`（奇數 k 的 `γ^-k` 主項為純虛數；偶數 k≥4 本身已是 `O(γ^-4)`）。

因此

`Re L_n(a+iγ)=[na+n(n-1)/2]/γ²+O_{n,a}(γ^-4)`。

分別代入 `a=β` 與 `a=1-β`，再乘 2，得到

`q_n(β,γ)=2n²/γ²+O_{n,β}(γ^-4)`。

對每個固定 n，主項嚴格為正，故存在 `Γ_n` 使 `γ>Γ_n` 時 `q_n>0`。取有限集合的最大值 `Γ=max_{1≤n≤N} Γ_n` 即同時成立。證畢。

### 邏輯邊界

L1 是抽象對稱零點資料的障礙結果。它沒有證明 ζ 可任意加入這種四元組，也沒有否定「所有 Li 係數非負等價於 RH」的無限判準。

## L2（暫緩）：顯式一致界

目標：找出可驗證的 `C(N,β)`，使 `γ≥1` 時

`|q_n(β,γ)-2n²/γ²| ≤ C(N,β)/γ⁴`，`1≤n≤N`。

若成立，`γ²>C(N,β)/(2)`（取對所有 n 的安全上界）即可給出顯式 Γ。L3 的精確公式已提供更直接的符號判準，因此此粗界不再是優先路徑。

## L3（已證）：精確公式與無限多次負貢獻

令

`r²=[γ²+(1-β)²]/[γ²+β²]`，`λ=log r`，

`θ=Arg(γ²-β(1-β)+iγ)`，其中 `0<θ<π`。則對所有 `n≥1`，

`q_n(β,γ)=4-4 cosh(nλ) cos(nθ)`。

若 `β≠1/2`，則 `λ≠0`，而且 `q_n<0` 對無限多個 n 成立。

### 證明

置 `w_a=1-1/(a+iγ)`。直接相乘得

`|w_β|=r`、`|w_{1-β}|=r^{-1}`，且兩者辯角同為 θ。共軛根給出共軛的 w，因此四項相加為

`[2-2r^n cos(nθ)]+[2-2r^{-n} cos(nθ)]`

`=4-4 cosh(nλ)cos(nθ)`。

若 `θ/(2π)` 為有理數 `p/q`，取所有 `n=qk`，則 `cos(nθ)=1`，故 `q_n=4-4cosh(nλ)<0`。

若 `θ/(2π)` 為無理數，Dirichlet 逼近給出無窮多個、趨於無限的 n，使 `nθ` 模 `2π` 趨近 0。因此沿此子序列 `cos(nθ)→1`，而 `sech(n|λ|)→0`。充分大時

`cos(nθ)>sech(n|λ|)`，等價於 `cosh(nλ)cos(nθ)>1`，故 `q_n<0`。證畢。

### 邏輯邊界

這只證明單一離線四元組的貢獻會無限多次為負；完整 Li 係數是全部零點的正則化總和，其他零點可能在同一 n 抵消。未證明「單一負貢獻必使完整係數為負」。

## L4（已證）：高零點的共振偵測尺度

固定 `β≠1/2`，令 `d=|1-2β|`。選整數 `k` 滿足 `πkd>1/2`，並令 `n_γ` 為最接近 `2πk/θ` 的整數。當 `γ→∞` 時，對所有充分大的 γ，

`q_{n_γ}(β,γ)<0`，且 `n_γ=2πkγ+O(1)`。

### 證明

由初等 Taylor 展開，

`θ=γ^{-1}+O(γ^{-3})`，`|λ|=d/(2γ²)+O(γ^{-4})`。

寫 `n_γ θ=2πk+ε_γ`。最近整數的定義給出

`|ε_γ|≤θ/2=1/(2γ)+O(γ^{-3})`，

且

`n_γ|λ|=πkd/γ+O(γ^{-2})`。

用 `cosh x cos y=1+(x²-y²)/2+O(x⁴+y⁴+x²y²)`，得到

`q_{n_γ}=2[ε_γ²-(n_γλ)²]+O(γ^{-4})`

`≤2[1/4-(πkd)²]γ^{-2}+O(γ^{-3})`。

因 `πkd>1/2`，主項嚴格為負，故充分大 γ 時結論成立。又 `1/θ=γ+O(γ^{-1})`，所以 `n_γ=2πkγ+O(1)`。證畢。

## L5（由經典解析基礎推出）：最大模離線零點支配

採用 `analytic_foundations.md` 從 ξ 的一階整函數性、Hadamard 分解與函數方程推導的結果：

1. Li 係數可按共軛／函數方程四元組的對稱極限寫成
   `λ_n=Σ_ρ [1-(1-1/ρ)^n]`；
2. 非平凡零點位於 `0<Re(ρ)<1`，有界區域內有限，且足夠的粗計數界為 `N(T)=O(T^(3/2))`。

在這些前提下，若存在離臨界線零點，則存在無限多個 n 使 `λ_n<0`；更精確地，沿某子序列

`λ_n=-M R^n(1+o(1))`，

其中 `R=max_ρ |1-1/ρ|>1`，M 是達到 R 的零點數（計重數）。

### 證明綱要（完整估計見 `li_dominance_proof.md`）

- 對 `ρ=β+iγ`，`|1-1/ρ|>1` 等價於 `β<1/2`。離線零點的反射軌道故提供模大於 1 的 w。
- 當 `|γ|→∞` 時 w 的模一致趨近 1；配合零點離散性，最大值 `R>1` 被有限組取得，且其餘 w 的模有共同上界 `R_2<R`。
- 對最大組的有限多個相位使用同時 Dirichlet 逼近，得到無限子序列使所有 `w_j^n/R^n→1`；最大組貢獻為 `-M R^n(1+o(1))`。
- 選 `c>0` 使 `e^(3c/2)R_2<R`，並以 `T=e^{cn}` 分割其餘零點。高度不超過 T 的部分共有 `O(T^(3/2))` 項，總和為 `O(T^(3/2)R_2^n)=o(R^n)`。
- 高度超過 T 的每個四元組由 L3 精確公式一致滿足 `|q_n|=O(n²/γ²)`。由 dyadic 計數，`Σ_{γ>T}γ^-2=O(T^-1/2)`，故高尾為 `O(n²T^-1/2)=o(R^n)`。

所以非最大部分不能抵消最大組的負指數主項，結論成立。

### 邏輯邊界

L5 完成的是 Li 判準中「若 RH 為假，則某些（事實上無限多個）Li 係數為負」的方向。它沒有提供 `λ_n≥0` 的無條件證明；因此不是 RH 證明。

### L5b（已證）：負指數逸出其實有有界間隔

`li_syndetic_excursions.md` 將相位同步由 Dirichlet 子序列強化為緊群旋轉的
syndetic return set。因 L5 的非最大殼層餘項本來就對所有大 n 一致為
`o(R^n)`，若 RH 假，存在 `c>0,L,N_0`，使每個 `[N,N+L]`（`N>=N_0`）
都有某個 n 滿足 `λ_n<=-cR^n`，且同樣適用於 `E_n`。因此只要證 D10
超指數門檻的負值集合為 density zero，或存在任意長的好 block，便足以
推出 RH；此較弱算術目標尚未閉合。

## L6（已證）：radial-score convexity 使 K0 odd block entrywise 非負

若正 even kernel Phi 的 `q(t)=-Phi'(t)/(tPhi(t))` 在 `t>0` 非遞減，則對
K0B9 的 `F` 有

```text
F(p,d)>=F(d,p),  p>=|d|.
```

證明是 K0B17 的保測度徑向換元；固定 squared-argument總和時，reflected pair
spread較大，而 `h(s)=-logPhi(sqrt s)` convex。Riemann Phi 已由 J5滿足假設，故
`K0(x,y)-K0(x,-y)>=0` 對所有 x,y≥0。

邏輯邊界：這是 entrywise positivity，不是 positive-definite kernel；不能推出 RH。

## L7（候選，未證）：positive primitive 的 common-range graph bound

令 R、U、V、L 如 K0B15。若對所有 compactly supported f 有

```text
2 Re<LV,LU> <= |U(0)|^2+||U||_2^2,
```

則 K0B15.3 立即給 `K0>=0`，再由 K0B3推出 RH。這是 uniform all-size lemma。
K0B16排除逐 theta-pair證法；K0B18排除只靠 h operator convex的 standard
Loewner lift。尚需完整 theta和的 coupled factorization，不能把此候選本身當證明。

K0B19--22 已把此候選完全精確化。`L=D-1/2` 無界，不是
contraction；但 whole-line symmetric part exact cancellation。寫 `w=LU`，則

```text
2 Re<P_+M_[1/(1/2+i·)]P_+w,P_+w>
  =|U(0)|^2+||U||^2,
P_+M_[1/(1/2+i·)]P_-=0.
```

故 L7 等價於單一符號

```text
Re<P_+M_(iXi'/Xi)P_-w,P_+w><=0,
w in Ran(T_Phi),
```

而該左邊 exact 為 `-2Q_K0`。這是比原 graph-norm 敘述更小的
target，卻仍與 RH 等價。因 `Ran(T_Phi)` 在 ordinary `L2` 稠密，任何
bounded Nehari 延伸都會把單邊符號延到所有 independent half-line data，
反號論迫使 Hankel block為零。因此成功機制必須使用 Xi zeros的
unbounded graph cancellation，普通 bounded contraction 框架已排除。

## L8（候選，未證）：shifted screw cone 的可逆子錐

Suzuki 的 shifted screw densities 定義 positivity-preserving Volterra 半群
`Psi_(omega+eta)=T_eta Psi_omega`，所以已知 `omega>=1/2` 的正性可繼續
向右傳。若能找到一個可由 theta/primes 無條件驗證、受 `T_eta`
保持，且 `T_eta^-1` 亦保正的 Xi-specific proper cone，便可降到
`Psi_0>=0` 而證 RH。現有 full positive cone 不可逆；`Psi_0>=0`本身已等價
RH。所以 L8 的實質缺口是構造此 invariant subcone，不是再證 Volterra
半群正性。

Selberg nudge 後的重要修正：`Ran(T_Phi)` 在 full `L2` 稠密，其
positive-half-line projection 亦稠密；經 Paley--Wiener 就是在相應 `H2`
稠密。因此 L7 沒有任何 ordinary Hilbert-space 餘維優勢。所謂
common-range 只能指 `||w||_G=||hat w/Xi||_2` 的 non-equivalent graph norm；
在此 norm下 flux 拉回正是 `-2K0`，故沒有降階。

L8 亦有同樣防循環條件。以
`G_omega=Ran(C_[e^(-omega·)Phi])` 定義的同-preimage transfer在 graph norms間
總是 unitary，對任意 Xi都成立；這只是 tautology。要對 output Hardy
cone 保持 causality，則需 `Xi(z+i nu)/Xi(z+i omega)` 為 all-shift Schur
multiplier，這又等價 RH。所以合格 invariant cone 必須有不使用
`1/Xi` 的 theta/prime local characterization。

Suzuki 2025（ES60）把 L8 endpoint精確化。令
`E_Xi=Xi+iXi'`、`u_Xi=E_Xi#/E_Xi`；所需條件等價
`supp F^(-1)u_Xi subset [0,infinity)`。這是 uniform all-degree support target，
但 `u_Xi` 含 quotient `1/E_Xi`，所以直接驗證仍與 RH等價。真正候選必須從
theta/primes 構造一個不先除以 `E_Xi` 的 causal convolution/resolvent，並證其
boundary quotient恰為 `u_Xi`。

## L9（候選，未證）：prime Euler--Volterra common energy

K0B29 將 Markov/theta prekernel exact寫成

```text
Phi_W=2C product_p (I-p^(-3/2)T_(2log p))^(-1)g_alpha.
```

每個 factor是不用 `1/Xi` 定義的 positive causal shift resolvent。若能構造同一個
含 Archimedean completion的 quadratic storage，使每個 prime factor contractive，
並證 infinite Euler product極限沒有 boundary defect，則可能把 base Gamma channel的
Gram正性傳到 K0。這是 uniform all-prime/all-degree lemma，不是有限證書。

目前未證且 generic版本為假：PF∞不對正加總封閉（K0B27.2），逐 theta pair PSD
亦由 K0B16否證。故 L9 只在能給 explicit common energy與 telescoping prime defect時
才算進展；pointwise cone、Euler half-plane zero-free或形式 product都不合格。

K0B30 再排除 L9 的 ordinary bounded版本：completion gauge把 prime coefficient推到
`p^-1/2`，在 `L2(e^-2sigma x dx)` 的 partial product norm含
`product_p(1-p^(-(1/2+2sigma)))^-1`，只於 `sigma>1/4`收斂。target `sigma=0`
不可由正 factor逐一取極限。故 L9 現只保留 **signed prime--gamma telescoping**；
它必須明寫 counterterms並產生 K0 Gram，否則與既有 Weil-square缺口同義。

## L10（RH 等價驗收準則，不是降階）：critical-strip uniform LP exhaustion

若存在 even real kernels `K_N`，使 `Fourier(K_N)` 全為 Laguerre--Pólya，且對某個
`R>1/2` 有

```text
int_R |K_N(t)-Phi(t)|exp(R|t|)dt ->0,
```

則 transforms在含全部可能 nonreal Xi zeros的 strip locally uniformly趨 Xi。
Hurwitz與 LP零點實性遂直接推出 RH。這是 uniform-in-degree constructive mechanism。

最新 Masters' Nudge 指出的反向量詞必須明記：若 RH 已真，則 `Xi` 本身屬
Laguerre--Pólya，直接取常值族 `K_N=Phi` 即滿足全部條件。因此「存在某個 L10
family」與 RH 等價，不能列作較弱候選引理。只有一個 **不使用 RH、由 theta／prime
局部資料顯式產生該 family 的定理** 才會是新降階機制；L10 本身只保留作驗收準則。

Shi 第一族不滿足 target條件：K0B32證它在所有 exponential weights下收斂得很好，
但收斂到 explicit `K_infinity!=Phi`。因此 L10 的難點不是估計收斂速度，而是構造
真正以 Riemann Phi為極限的 LP family，並跨越 K0B30 的 `sigma=1/4` Euler boundary。

## L11（候選，未證）：Jensen reverse-shift／all-order finite-free bridge

Holland 已無條件關閉楔形 `n^3 log^2(n+2)>=K d^5`。要由此到 RH，至少需下列
兩類之一的真正 uniform theorem：

1. **reverse shift：** 由一整條已知負實根/交錯邊界，將 `J^(d,n+1)` 的
   hyperbolicity 降到 `J^(d,n)`，並可迭代至 `n=0`；或
2. **all-order factorization：** 對每個 `d,n`，把完整 ratio sequence
   `R_j=gamma(n+j)/gamma(n)`（不是固定前五項）exact 實現為保持正根的
   finite-free factors。

防循環條件：不能把欲證的 `J^(d,n)` hyperbolicity直接包成「相容性」假設；
factorization必須由 theta/prime局部資料構造。普通 inverse Rolle為假，且 ES57
證明相異正根 polynomial 的 finite-free inverse不留在正根 cone。故 L11 目前是
精確缺口，不是已得引理。任何固定階 `R_0,...,R_m` matching只改良 asymptotic wedge，
不可能單獨到達所有 `n,d`。

## L12（natural interpolant 已由 J72 關閉）：Xi moment-ratio 的 Pick--Bernstein interpolation

以 J68 的 `varphi_n=2(2n-1)m_(n-1)/m_n` 為資料。若能證 natural Mellin
interpolant

```text
varphi_nat(z)=2(2z-1)M(2z-2)/M(2z)
```

屬 KPS 的 `B_P^1`（Bernstein、Pick、1-separated meromorphic zeros/poles），則
`Psi=z varphi_nat` 的單一 Levy exponent透過 Theorem 4.4 一次生成 normalized Xi
並證全部 zeros實，故 RH。這不是 degree-by-degree刷證書。

已完成的 uniform子引理：J5 加分部積分給
`varphi_n=2E_n[q]` 與
`Delta varphi_n=2Cov_n(q,U^2)/E_n[U^2]>0` 對全部 n。尚未完成的是所有階
complete alternation及 complex Pick property。防循環：不得以 Xi已屬 LP、Xi zeros
或 `1/Xi` 表示來證 Pick；必須直接從 `Phi`/theta 的 Mellin ratio得到 Herglotz
representation。K0B36.5 的 nonreal-zero Gaussian mixture說明單靠 `q'>0` 不足。

J69 新增 all-order正結構：normalized Xi law無條件有
`D=sqrt(I)·2cos(Theta)`，且 `I` 的 density由 `Phi'<0` 的 Abel反演顯式給正；
其 Mellin recurrence恰為 `varphi_nat`。因此 representing measure問題已關閉，
剩餘不是再驗 Hankel minors，而是證此特定 `I` 屬 complete-subordinator
perpetuity class。Hirsch--Yor 給必要條件：若 `varphi_nat` complete Bernstein，則
`log I` multiplicatively infinitely divisible；一個解析必要 target是

```text
K_I(s)=2logGamma(1+s)-logGamma(1+2s)+log M(2s)-log M(0),
K_I'' completely monotone on (0,infinity).         (L12.1)
```

此條件仍未證且只屬必要條件；數值 cumulant符號不能代替 complete monotonicity。

J70 把 L12.1 再精確化。若 `A=L^(-1)[4(log M)''(2s)]`，complete-Bernstein
必要條件是 measure sandwich

```text
x/(e^(x/2)+1)dx <= A(dx) <= x/[2sinh(x/2)]dx.      (L12.2)
```

這同時編碼 perpetuity與 remainder兩個 channel，是真正 uniform全階不等式。
候選證法應從完整 theta lattice導出 A 的正 representation；僅驗 derivatives或
cumulants到有限 order不合格。即使證成 sandwich，仍須證所得 measure是 admissible
harmonic-potential measure並閉合 KPS 1-separation。

J71 顯示 L12.2 的 pole budget完全由 `M` 的 fixed Taylor poles耗盡；但依 Selberg
nudge，J70首先只是 measure sandwich，寫成 J71逐點 density前還缺 absolute
continuity及 termwise inversion。這個量詞升格不能省略。

J72 已用 Arb balls、解析尾界及 Rouché 嚴格證出一個 nonreal `M` zero，且
`M(rho-2)!=0`。所以 `varphi_nat` 在 upper half-plane有真 pole，natural Mellin
interpolant definitively不是 Pick／complete Bernstein。L12 不再列為 live proof route。
J73 再用 Carlson uniqueness 關閉最後的抽象可能性：所有 KPS 候選的
`1/W_varphi(n+1)` 都由同一 coefficient data固定；Patie--Savov Stirling bound使
`1/W_varphi` 與 natural coefficient interpolant同屬 Carlson class，故兩者必相等。
J72 的 nonreal zero遂與 KPS全負實零點矛盾。因此 L12/KPS整條插值路線已關閉，
不是只關閉 natural ratio；不得再以另一插值或有限差分批次重開。

## L13（已證為 RH 等價判準；算術上未閉合）：Goldbach--Chebyshev 次指數正能量

令 `H(X)=sum_rho X^(rho-1/2)/[rho(rho+1)]`。SMG5 證

```text
RH iff for every epsilon>0,
        integral_0^T |H(e^t)|^2 dt = O_epsilon(exp(epsilon T)).
```

反向由 weighted L2使 Laplace transform在 `Re w>0` 解析；任何
`Re rho>1/2` 卻在 `w=rho-1/2` 留下非零 pole。prime-side等價為 centered
weighted Lambda sum的 `dX/X` energy是 `O_epsilon(X^epsilon)`。

這是合格 all-scale positive target，不是 finite certificate；但目前沒有無條件
upper bound。候選證法只能用 centered Goldbach/off-diagonal correlation，不能以
absolute PNT envelope或 `Lambda*Lambda>=0` 的未中心化 positivity代替。

## L14（候選 upper bound；kernel 已證）：centered-prime Gram energy

SMG7 已證所有 Y 的 explicit PSD kernel

```text
K_Y(m,n)=integral_max(m,n)^Y (1-m/x)(1-n/x) dx/x^2,
```

以及 `Y=infinity` closed form
`K=(3max-min)/(6max^2)`。RH等價於對每個 epsilon

```text
sum_(m,n<=Y) (Lambda(m)-1)(Lambda(n)-1) K_Y(m,n)
    = O_epsilon(Y^epsilon).
```

未證部分只有此特殊 signed vector的 uniform upper bound；matrix PSD本身不足。
可接受證法必須提供 reflected/order autocorrelation或 operator contraction，不能
改用 sum-kernel Goldbach positivity。

## L15（已證結構；arithmetic contraction 未證）：log-stationary Green factorization

令 `F(t)=e^(-t/2)C(e^t)` 與
`g(u)=1_(u>=0)(e^(-u/2)-e^(-3u/2))`。PG1--2 已證

```text
F(t)=sum_n (Lambda(n)-1)n^(-1/2) g(t-log n),
g_hat(tau)=1/[(1/2+i tau)(3/2+i tau)],
(D+3/2)(D+1/2)F=sum_n (Lambda(n)-1)n^(-1/2)delta_(log n).
```

因此 `sqrt(mn)K_infinity(m,n)` 只依 `|log(m/n)|`，且 full-tail Gram form exact為

```text
(1/2pi) integral_R |sum_(n<=Y)(Lambda(n)-1)n^(-1/2-it)|^2
                    /[(t^2+1/4)(t^2+9/4)] dt.
```

這給全部尺寸的 strictly-PD Toeplitz--Green結構。未證部分是對特殊 forcing建立
`exp(o(log Y))` upper bound。任意係數版本為假：取 block `[N,2N]` 上係數皆 1，
Gram norm為 `>>N` 而 `sum |b_n|^2/n=O(1)`。故不能再尋 generic coefficient-square
contraction；新 theorem必須使用 `Lambda-1` 的 global arithmetic cancellation。

## L16（已證 exact hierarchy）：Green energy exponent等於最右零點偏移

PG6 證

```text
limsup_(Y->infinity) log[ integral_1^Y C(X)^2/X^2 dX ] / log Y
  = 2 sup_rho(Re rho-1/2).
```

所以 `exp(o(T))`／`Y^epsilon for every epsilon` contraction本身 exact等價 RH。
較弱的 `E(Y)=O(Y^theta)` 只會給 `Re rho<=(1+theta)/2`。可接受的 Selberg升階
機制必須明確產生 strict exponent map `theta -> Phi(theta)<theta` 且可迭代到 0；
PNT型 `Y exp(-c sqrt(log Y))` 的 logarithmic exponent仍是 1，沒有 contraction。

## L17（RH等價全正核）：completed log derivative的 positive-real kernel

令 `M(z)=xi'/xi(1/2+z)`。RH iff `M` 在右半平面 holomorphic且所有 Pick matrices

```text
K_M(z,w)=[M(z)+conj(M(w))]/[z+conj(w)]
```

PSD。RH下它是 `sum_gamma 1/[(z-i gamma)(conj(w)+i gamma)]` 的全階 Gram核。
Euler--gamma公式只在 `Re z>1/2` 直接收斂；把 positivity延到 `Re z>0` 正是 RH。
functional equation的 boundary純虛／Cayley模一不足：off-axis quartet polynomial
提供具有同樣 reflection boundary而含右半平面 poles的 exact all-pass反例。

## L18（已證）：Nyman remote Cholesky vector是非平方可和的邊界泛函

令 `L_kj=<f_k,e_j>`、`a_k=(k-1)/k` 與 `A=L^-1 a`。則

```text
A_j = 2 Res_(s=0) integral_0^1 e_j(x)x^(s-1)dx
    = lim_(k->infinity) [2k/log k] L_kj,
sum_(j>=2) A_j^2 = infinity.
```

最後一式若假，`w=sum A_j e_j in L2` 會滿足 `<w,f_k>=a_k->1`；但
`0<=f_k<1` 且 pointwise趨零，故 `||f_k||_2->0`，矛盾。這精確說明
Cholesky全正所控制的是 `s=0` 的不連續 boundary functional，不是 RH所需
`E=L^-1(log k/k)` 的 `ell2` 能量。NC4更構造保留 exact右端、remote漸近、
`||f_k||->0` 與全正而仍有正交殘差的模型。

## L19（已證 no-go）：Nyman--Ehm inversion tail不能逐項絕對估計

對 `q=1,2` 的 Müntz kernel `S_q`，large integer ratio處的 Bernoulli首項非零，
故存在固定 interval `I` 與 `c_q>0` 使 `|S_q(x)|>=c_q` on I。取
`m,n asymp N`、`m<=N<n` 且 `n/m in I`，再用 square-free integers正密度，得

```text
sum_(m asymp N) |mu(m)|/m sum_(n asymp N,n>N)|mu(n)S_q(n/m)| >> N.
```

Levinson--Selberg outer weight只把它降至 `>>N/log N`。所以 `q=2` 的
large-ratio decay不能處理 `n/m=Theta(1)` moving boundary；任何先取 absolute
values的 tail bound必失敗，必須保留二維 Möbius phase／cross-term cancellation。

## L20（已證強度 no-go）：generic same-scale smooth bilinear bound已蘊含 RH

若對所有固定 smooth compactly supported `W` 均能證

```text
sum_(m,n) mu(m)mu(n)W(m/N,n/N)=o(N log N),
```

則取 `W(x,y)=eta(x)eta(y)` 得
`|sum mu(n)eta(n/N)|=o(sqrt(N log N))`。標準 smooth Mertens--Mellin
判準遂使 `1/zeta(s)` 在 `Re s>1/2` holomorphic，配合 functional equation即得 RH。
所以 Ehm moving boundary不能靠 coefficient-generic smooth-kernel theorem解；候選
引理必須利用 `S_q` 與 correction terms的特殊 exact結構。詳見 NS6。

## L21（已證量詞分界）：single `S_q` kernel 的 uniform cutoff版仍為 RH-strength

在 `S_q` 不離零的 compact ratio rectangle上，local `H1` regularity與 Wiener lemma
給 `1/S_q(y/x)` 的 `L1` Fourier separated representation。若 normalized `S_q`
bilinear form對整個 Wiener cutoff Banach algebra逐點趨零，uniform boundedness使此
收斂延伸到 projective tensor completion，因而可除掉 `S_q` 並恢復 rank-one kernel。
若包含 same-block rectangle，立即得到 smooth Mertens square-root bound與 RH。

但 natural Levinson tail只是一組 fixed cutoffs且 supports分離，沒有上述 norm-uniform
量詞。superlacunary block coefficient模型可使任一固定 ratio-window bilinear form恒為零，
同時 partial sums為線性尺度。因此 L20不能直接封掉單一 tail scalar；詳見 SK1--SK3。

## L22（已證 exact no-go）：divisor inversion保留首個同尺度 Möbius band

令 `A_m(u)=sum_(n<=u)mu(n)S_q(n/m)`。則 natural error有 exact雙 logarithmic
Cesaro式 SK4.2，且

```text
A_m(u)-R_q(1/m)=sum_(j>u)d_u(j)R_q(j/m),
d_u(j)=sum_(d|j,d<=u)mu(d).
```

對 `u<j<=2u`，所有 proper divisors均 `<=u`，故
`d_u(j)=-mu(j)`。所以 identity-factory/divisor change在主要 moving band逐字留下
`-sum_(u<j<=2u)mu(j)R_q(j/m)`；沒有變成 positive primes或 far ratio。

## L23（RH等價正判準；degree判讀由 L24 強化）：critical local Möbius Orlicz bound

令 `P_N=N^-1/2 sum_(n<=N)mu(n)e(nt)`。Verjovsky的一次 local moment inequality給
fixed `q` 的 exponent loss `1/[2(q+1)]`，source以 unbounded `q` 將 loss壓到零；
L24進一步證同一 fixed `q` 可 bootstrap，故高 degree並非必要。仍等價的
單一 all-degree target是：每個 `eta>0` 均有

```text
N/(2c) int_(-c/N)^(c/N)
 exp(|P_N(t)|^2/[C_eta N^(2eta)])dt <= C_eta.
```

RH由 critical-arc supremum推出此式，反向由全部 moments及 Mertens criterion推出 RH。
未證部分是 deterministic Möbius local subgaussian bound；較小的 q=2 target見 L24。

## L24（已證升階定理）：任一 fixed critical local `L^q` subpower bound已等價 RH

令 `F_N(u)=N^-1/2 sum_(n<=N)mu(n)e(nu/N)`，`|u|<=c`。若已有
`M(x)=O(x^(1/2+delta+epsilon))`，兩次 partial summation給
`||F_N'||_infinity=O(N^(delta+epsilon))`。fixed `q` 的 local spike inequality

```text
|F_N(0)| <= max{2||F_N||_q,
 [2^(q+1)c ||F_N'||_infinity ||F_N||_q^q]^(1/(q+1))}
```

遂將 Mertens偏移 `delta` 送到 `delta/(q+1)`。從 trivial `delta_0=1/2`
有限次迭代，任一 fixed `q>=1` 的 `||F_N||_q=N^o(1)` 即給 RH。特別是 `q=2`
的單一 sinc Toeplitz PSD quadratic form已充足。完整證明見 VA2--VA4。

## L25（已證對偶 no-go）：SK5.2不能直接生成 Orlicz upper-bound certificate

Gibbs變分把 local Orlicz bound等價成對每個 probability density `w` 的 entropy不等式；
其 quadratic kernel為 additive Toeplitz `what((n-m)/N)`。SK5.2則是 multiplicative
ratio kernel `R_q(j/m)` 的 signed coefficient。由 `d_u=-mu` 可造
`w=|sum d_u(j)e(jt)|^2/Z`，但單一 feasible `w`只給 Gibbs supremum的 lower witness，
而 upper bound需要控制所有 `w`，且此選擇升成四階 correlation。故幾何與量詞皆不合。

## L26（已證量詞引理）：fixed-q exponent bootstrap不需對 delta 一致

令 `P(delta)` 表示 `M(x)=O_alpha(x^(1/2+delta+alpha))` 對每個 `alpha>0`。
fixed local `L^q` subpower bound配合 derivative/spike estimate給

```text
P(delta) => P(delta/(q+1)).
```

對每個目標 epsilon只迭代有限次；每步可另選正 loss，常數雖退化也無妨。因此不存在
`k->infinity` 與 `N->infinity` 的交換，Masters nudge所擔心的 uniform-in-delta
條件不是必要條件。完整量詞見 LQ1。

## L27（已證 exact structure）：sinc quadratic有 all-rank positive分解

Legendre Parseval精確給

```text
Q_c(N)=N^-1 sum_(k>=0)(2k+1)
 |sum_(n<=N)mu(n)j_k(2 pi c n/N)|^2.
```

等價的 discrete-prolate分解為
`Q=(2c)^-1 sum lambda_j|<mu,v_j>|^2`。prolate spectral decay可使
`J~log N/loglog N` 後的純譜尾為 subpower，但低模態是平滑 Mertens sums；正性
阻止高模態抵消它們。故這是全正結構，不是證明 producer。

## L28（已證 exact no-contraction）：`mu log` multiscale只在 RH-strength envelope下收縮

logarithmic remainder滿足

```text
R_N(u)=1/log N int_(1/N)^1 sqrt(y)F_(Ny)(yu)dy/y,
||F_x(y dot)||_[−c,c]^2=Q_(cy)(x).
```

若控制所有 `c'<=c` 的 normalized arc energy則得到 `2/log N` 收縮，但
`c'->0` 已包含 `M(x)^2/x`。只用 fixed-c inclusion給 `Q_(cy)<=Q_c/y`，係數恰回到 1。

## L29（已證 exact transfer/no-go）：Lambert all-scale operator的 symbol是 zeta

由 `sum mu(n)z^n/(1-z^n)=z`，normalized Laplace sums滿足

```text
G_N+sum_(k>=2)k^-1/2 G_(N/k)=N^-1/2 z_N.
```

係數在 `ell1`、`ell2` 都臨界發散；尺度 mode `x^s` 的 symbol為
`zeta(s+1/2)`。所以 generic coercive inversion就是控制 `1/zeta`，不能當作獨立
RH證明。live可能性只剩 special-forcing/functional-equation 的非 generic transfer。

## L30（已證強度定理）：第一個 sinc-smoothed正模態已等價 RH

取 `c=1/(2pi)` 與 `w(x)=sin(x)/x`。其 Mellin transform

```text
W(s)=sum_(r>=0)(-1)^r/[(2r+1)!(s+2r)]
```

在 `Re s>0` 無零，因
`|sW(s)-1|<=sum_(r>=1)1/(2r+1)!=sinh(1)-1<1`。故

```text
sum_(n<=N)mu(n)w(n/N)=N^(1/2+o(1)) iff RH.
```

證明用 `int_1^infinity A_w(X)X^(-s-1)dX=W(s)/zeta(s)`。此 scalar正是
L27分解的 `k=0` mode；所以 low-mode gap不是尚需聯合多模態，第一模態已 RH-strength。

## L31（已證 exact no-go）：Lambert special forcing沒有 zero cancellation

對 `G(x)=x^-1/2 Phi(e^-1/x)`，尺度 Mellin transform精確為

```text
M[G](r)=Gamma(r+1/2)/zeta(r+1/2).
```

RHS forcing的 transform是 `Gamma(r+1/2)`，而 Gamma無零。故 special forcing不消
任何 zeta pole；Gamma只給 vertical damping，functional equation只反射 poles。
Lambert線若無新的 pole-location theorem，仍是 explicit-formula reformulation。

## L32（已證 uniform升階機制）：local mean加 positive Volterra inversion一步推出 RH

取 `c=1/(2pi)`、`w(x)=sin x/x`、`A_w(X)=sum_(n<=X)mu(n)w(n/X)`。
因 `w`遞減且 `w(1)=sin1>1/2`，Abel summation及 supremum給

```text
T(X)<=S(X)<=T(X)/(2sin1-1),
T=sup_(t<=X)|A_w(t)|,  S=sup_(t<=X)|M(t)|.
```

又 `A_w(N)/sqrtN` 正是 `F_N` 在 critical arc的 normalized mean，故被任一 fixed
local `L^q` norm（`q>=1`）控制。這一步直接證 fixed-q criterion，不需 derivative
bootstrap或 uniform-in-delta constants；它是明確的 all-q/scale升階定理。

## L33（已證 exact identity）：sinc integer-sampling energy等於 Mertens歷史平方

令 `A_N(t)=sum_(n<=N)mu(n)sinc(tn/N)`。其 Fourier support在
`[-1/(2pi),1/(2pi)]`，整數 sampling無 alias，且

```text
sum_(k in Z)|A_N(k)|^2
=pi N[M(N)^2/N+sum_(n<N)M(n)^2/(n(n+1))].
```

這是 all-frequency PSD結構，但 RHS正是 weak-Mertens型能量，沒有提供無條件 upper bound。

## L34（已證 exact no-go）：compact sinc的 Möbius--Müntz source就是 target

對 `f=sinc(x)1_(x<=1)`，dilation inverse

```text
b(x)=sum_k mu(k)f(kx),  sum_m b(mx)=f(x)
```

逐點有限，且 `b(1/N)=A_1(N)`、`bhat=W/zeta`。因 `W`在 `Re s>0`無零，
尋找 source的 square-root bound沒有降低 RH強度。

## L35（已證 global positivity/no-go）：`-Pf>=0`，但 positive cone closure不可能

compact sinc正遞減，故 Müntz transform `Pf` 是 right-Riemann-sum error並處處非正。
然而 `h=-Pf` 對 `x>1` 恰為 `I/x`。任意非負 dilation組合的 tail係數
`C=sum c_k/k` 若趨零，則組合在每個 `[epsilon,1]` 也趨零，不能逼近 positive target
`f`。所以 closure必須用 signed coefficients；global sign不消 Möbius parity。

## L36（已證 exact reduction）：signed sinc closure是 weighted Nyman mollifier

若 `C(s)=sum c_k k^-s`，則

```text
||f-sum c_k h(k dot)||_2^2
=1/(2pi)int |W(s)|^2|1+zeta(s)C(s)|^2dt,
```

且 common tail強迫 `C(1)=sum c_k/k->0`。zero-free `W`只作 outer smoothing，
沒有移除 reciprocal-zeta obstacle。

## L37（已證 norm no-go）：任何成功 signed closure的 synthesis norm必發散

令 `K(c)=sum|c_k|/sqrt(k)`。critical line上 `|C(s)|<=K(c)`；在任一已知 zeta零點
附近，若 K有界則 `|1+zeta C|`在固定 interval離零，closure不可能。若零點 multiplicity
為 m，更有 error square `>>K(c)^(-1/m)`。所以不存在 bounded-norm projector。

## L38（已證 exact recursion/no-contraction）：dilation samples是同一 target的小尺度值

indicator時 `B_N(k)=M(floor N/k)`；compact sinc時 `B_N(k)=A_w(N/k)`，且

```text
sum_(k<=N)A_w(N/k)=f(1/N).
```

除以 `sqrtN` 後 dilation weights為 `k^-1/2`，兩種絕對 summability皆失敗。
隔離 k=1是 critical recursion，不是 scale contraction。

## L39（已證 uniform block basis lemma）：Laguerre difference family只多項式退化

令 `phi_n=e^(-t/2)L_n`、`Q_n=e^(-t)(L_n-L_(n-1))`。在
`L2(e^t dt)` 中，`Q_N,...,Q_(N+H)` 的 Gram matrix為對角 2、鄰對角 -1，故
eigenvalues精確為 `2-2cos(j*pi/(H+2))`。upper Riesz bound小於 4，lower bound
為 `asymp H^-2`，完全不依賴 degree endpoint N。ordinary-Laguerre路線的
uniform-in-degree basis/condition-number斷層因此已關閉；尚缺的是 centered prime
functional在這些移動 subspaces上的次指數 dual norm，不是更多 finite degrees。

## L40（已證 controlled-projector reduction）：局部存在免費，缺的是次平方根 norm

對每個 fixed T，滿足 `C(1)=0` 的 finite Dirichlet polynomials在 `L2(-T,T)`
稠密；證明用 Paley--Wiener transform在 `log k` 的 exponential zero density排除非零
annihilator。乘以 critical-line zeta後 range仍稠密，故 local weighted error可任意小。
另一方面 `W(t)=O(1/t)` 與經典 zeta 二次矩
`int_0^X|zeta(1/2+it)|^2dt<<XlogX` 給 uniform tail
`O(T^-1+K(C)^2logT/T)`。因此擴張窗口 local error趨零且
`K^2logT/T->0`（例如 `K=o(T^alpha),alpha<1/2`）足以形成 global closure；RH下可對
既有 approximants後選 T，故此亦為存在性等價格式。bounded norm已不再是 target；
最小缺口是定量 local controllability cost。

## L41（已證 support-envelope reduction）：fixed-window係數可逐項壓小

Andersson--Pechersky density theorem取
`Phi(n)=n^(1/loglog n)`，轉成 critical normalization後允許
`|c_n|<=n^(-1/2+1/loglog n)` 仍在每個 fixed window稠密。故截至 support N，
`K=sum|c_n|/sqrt n=N^o(1)`。exact `C(1)=0` 用 atoms
`c_n[n^(-1/2+it)-n^-1]`；其新增 constant parts絕對可和，故不破壞 Pechersky
directional divergence，c1亦一致 bounded。這不給 RH，因 theorem
沒有 N對 window T及 error delta的有效上界。controlled-projector缺口可改寫成：證此
construction的 support complexity足以令 `K(N(T,delta))^2logT/T->0`。

## L42（已證 quadratic no-go）：support-free ell2 synthesis bound不存在

取 `d_n=1/M` 於任意遠端 consecutive block `(N,N+M]`，並以
`d_1=-sum d_n/sqrt n` 消 `C(1)`。當 `N>>TM`，所有 `n^-it` 在 `[T,2T]` 幾乎同相，
所以 `|C|>=1/2`，但 `sum|d_n|^2=1/M+o(1)`。故任意只以 coefficient ell2 norm控制
固定 frequency shell的 theorem均為假；必須加入 support length或 log-cluster mass。
這排除以 GCD/twisted moment的 generic quadratic norm取代 L40的 K，未排除特殊 target
coefficients的 signed cluster cancellation。

## L43（已證 cluster-tail lemma）：K平方可換成 K乘解析度 cluster norm

令 `B_T^2=sum_j(sum_(j/T<=logn<(j+1)/T)|c_n|/sqrt n)^2`。Gaussian majorant與
Ingham zeta四次矩給
`tail<<T^-1+K B_T log^2T/T`。故 local error趨零加
`K B_T log^2T/T->0` 足以推出 global closure/RH。對 L41 envelope，
`B_T^2<<1+T^-1 sum_(T<n<=N)n^(-1+2/loglog n)`；這是真正利用 log-frequency
分散的 uniform estimate，但仍需 N(T,delta)或直接 cluster-mass rate。

## L44（已證 all-order kernel lemma）：任意固定 polynomial cost皆可吸收

`f_m=x(1-x)^m1_(0,1)` 的 Mellin transform為
`m!/prod_(r=1)^(m+1)(s+r)`，在 Re s>0無零且作 `|t|^(-m-1)` 衰減。其 Müntz
generator仍有 exact common tail；tail-exact signed error滿足
`tail<<_m T^(-2m-1)+K^2logT/T^(2m+1)`，cluster版則以 `K B_Tlog^2T`取代
`K^2logT`。故任何已證的 finite-degree polynomial local cost都可由先選 fixed m吸收；
若 cost先對 m0證得，`W_m/W_m0` 在 critical line對每個 m>=m0一致 bounded，所以同一
coefficients可升到 `m>max(m0,A)`，量詞不循環。尚缺的是證 cost確為某個 polynomial，
而非只知 finite。

## L45（已證 conditional lifting；前件未證）：同一殘差允許合法升階

對同一 C，`Ehat_(m,C)=W_m(1+zeta C)`，故

```text
Ehat_(m,C)=(W_m/W_(m_0))Ehat_(m_0,C),
sup_(Re s=1/2)|W_m/W_(m_0)|<infinity  (m>=m_0).
```

因此更換 `f_m,h_m` 時的 local approximation由共同 residual精確轉移；`C(1)=0`也保留。
若某 fixed `m_0` 存在 `delta(T)->0`、finite A及 `C_T(1)=0`，使 local error
`<=delta(T)`且 `K(C_T)<=T^A`，則固定 `m>max(m_0,A)`後由 L44形成 global closure並推出
RH；`K B_T<=T^A`亦同。結論已證，但 polynomial-cost前件未證，不能稱為 RH證明。

## 2026-08-16 階段候選分類

- 已證可用：L36--L44及 L45的 conditional implication。
- 已反證/淘汰：bounded-K synthesis、support-free ell2 shell control、dilation contraction、
  由 PNT搬運 critical-line reciprocal regularity。
- 存活未證：對某 fixed beta kernel取得任意 finite polynomial K cost，或 polynomial
  `K B_T` cost；Pechersky effective support rate是目前最具體子候選。
- ordinary-Laguerre只保留 prime-centered signed quadrature未證 lemma；一般
  block/frame/uniform-asymptotic候選已完成稽核，不再擴張。
- 下一輪第一步：從 Andersson--Pechersky proof抽出明示 partial-support stopping rate，
  直接對照 L45前件。RH未證；停止續攻。

## L46（已證方法論 no-go 與 exact dual）：Pechersky pointwise divergence不能給 uniform stopping rate

詳見 `andersson_pechersky_rate_audit.md`。任意 finite atom prefix在 infinite-dimensional
`L2` 中都有共同正交 unit direction，故
`inf_(||f||=1)sum_(n<=N)|<f,x_n>|=0`。source量詞是
`forall f exists N(f,R)`，不能換成 window-uniform `exists N forall f`。其 classical proof
另先取 `delta_H=1/(8eH)`、`epsilon(x)=(log(x+1))^(-1-eta)`，後續仍由 qualitative
Pechersky收尾。因此現有 proof不產生 polynomial `N(T,delta)`；這不反證 polynomial-cost
approximants本身。

正確 target-specific形式：令 `y_m=W_m(s)`、
`a_(m,n)=W_m(s)zeta(s)(n^-s-n^-1)`。消去 `C(1)`後
`q=sum_(n>=2)|c_n|/sqrt n` 與 `K(C)` 相差至多 factor 2。Hahn--Banach嚴格給

```text
exists q(c)<=K, ||y_m+sum c_n a_(m,n)||<=delta
iff
|<y_m,f>|<=delta||f||+K max_n sqrt(n)|<a_(m,n),f>|  for every f.
```

下一候選 L46.1 只證此 target-specific inequality以 `K<=T^A`、finite A及
`delta(T)->0`；不得再尋求已被 finite-prefix orthogonality否決的 all-direction coercivity。

## L47（已證 one-sided Hardy no-go）：一般 smooth target不能 polynomial-cost轉成 Dirichlet frequencies

若 `F(z)=sum d_j exp(-i lambda_j z)`、`lambda_j>=0`、`sum|d_j|<=K`，則 F在下半平面
為 H-infinity且 norm至多 K。對 target `exp(i omega t)`，取
`y=log(2K)/omega`、`mu=(2/pi)arctan(T/y)`；Poisson--Jensen applied to
`1-exp(-i omega z)F(z)` 嚴格給

```text
||F-exp(i omega t)||_L2(-T,T)
 >=sqrt(pi*y*mu) 2^(-1/mu)(1+K)^(-(1-mu)/mu).
```

所以任意 fixed A的 `K<=T^A` 都不能使 absolute error趨零。Dirichlet polynomial以
`d_n=c_n/sqrt n,lambda_n=logn`正落在此類。故「regularized reciprocal有 polynomial
real Sobolev norm」不足以產生 Handoff-2；two-sided Fourier近似轉 one-sided frequencies
會有真正 norm障礙。此反例不針對 special zeta target；下一步只能找其 lower-half-plane
arithmetic/Hardy factorization。

## L48（已證 zero-distance lower bound）：首零點局部障礙只強迫 polynomial cost

若 `rho=1/2+i gamma` multiplicity為 r，局部有 `|zeta|<=M|t-gamma|^r`、
`|W_m|>=w`。視窗端點 `T=gamma-d`，且 `|C|<=K` 時，令
`R=(2MK)^(-1/r)`；若 R>d，則長度 R-d的區間上 `|1+zeta C|>=1/2`。故
error<=delta 嚴格推出

```text
K >= [2M(d+4delta^2/w^2)^r]^-1.
```

simple zero時是 `(d+delta^2)^-1` 級。這回答 AP2數值壓測的極端參數：局部 zero
obstruction為 polynomial，不足以判 AP2.5 super-polynomial；額外爆炸若為真必來自全域
one-sided interpolation。因而不以 ridge曲線淘汰 AP2.5。

## L49（live explicit obligation MB1）：fixed Riesz--Möbius polynomial-cost closure

固定 `k>=1,B>0`，令

```text
M_X(s)=sum_(n<=X)mu(n)(1-logn/logX)^k n^-s,
a_X=M_X(1),  C_X=a_X-M_X.
```

則 `C_X(1)=0` exact，且無條件 `K(C_X)<<sqrtX+logX`。L49要求找 fixed `m,k,B`、
`2m+1>B`及 `T_j->infinity`，使 `X=T_j^B` 時

```text
integral_(|t|<=T_j)|W_m(1/2+it)|^2
 |1+zeta(1/2+it)C_X(1/2+it)|^2dt ->0.                (MB1)
```

SC16 tail立即把 MB1升成 global closure/RH。這是帶完整量詞的下一 producer；PNT只控近
Re s=1、high-shell mollifier lower經 beta weight衰減、L48 local zero lower亦與
`K=O(T^(B/2))`相容，故三者都未裁決 MB1。

## L50（已證 MB1 exact bulk identity）：k=1化為 centered prime-square energy

令 `q_X(r)=1_(r=1)+a_X-sum_(d|r,d<=X)mu(d)w_X(d)`，並設
`S_X(y)=sum_(r<=y)q_X(r)r(1-r/y)^m`。Mellin--Plancherel精確給

```text
(2pi)^-1 integral_R |W_m(1/2+it)(1+zeta C_X)|^2dt
=integral_1^infinity |S_X(y)|^2dy/y^4.
```

對 `k=1,y<=X`，divisor identities `mu*1=epsilon`、`(mu log)*1=-Lambda` 給

```text
S_X(y)=(a_X-1/logX)A_m(y)-[P_m(y)-A_m(y)]/logX,
A_m=sum n(1-n/y)^m,
P_m=sum nLambda(n)(1-n/y)^m.
```

所以 MB1 bulk正是 Abel boundary與 centered prime discrepancy放在同一 square的能量。
PNT逐點 error乘長度 X不夠，分開 triangle亦丟掉唯一可能消去。k=0則 bulk exact為
`a_X A_m(y)`，會強迫 `sqrtX|sum_(n<=X)mu(n)/n|->0`，故至少一次 log Riesz smoothing
確為必要結構。下一步只展開 `y>X` tail並核對是否同一 discrepancy控制。

## L51（已證 MB1 tail reduction）：fixed Riesz order仍留下 same-scale Möbius block

對 `y>X`，exact omitted-divisor term為

```text
H_(X,k,m)(y)=sum_(X<d<=y)mu(d)(1-logd/logX)^k d A_m(y/d).
```

在 `X<y<2X`，它縮成
`sum mu(d)(1-logd/logX)^k d(1-d/y)^m`。Riesz weight只有
`O((logX)^-k)`；以 PNT zero-free-region的 Mertens bound作 partial summation，再平方積分，
上界仍為 `X exp(-2c(logX)^alpha)/(logX)^(2k)`，不趨零。任意 fixed k皆不能補所缺
power 1/2；k隨X增長則違反 MB1量詞。

這不證 H本身大，因它可與 L50 prime/boundary terms joint cancel；但證 MB1沒有脫離
既有 moving same-scale signed Möbius gap。triangle/absolute envelope不合格，必須證整個
AP7.2的近平方根 joint cancellation。

## L52（已證 route comparison 與 fixed block criterion）：Laguerre不是 AP7 的 linear same-block換座標

`K(z)=log[(s-1)zeta(s)]=sum a_nz^n`，而 reciprocal route滿足
`1/zeta(s)=z(1-z)^(-1)exp[-K(z)]`。exp/log係數是 triangular Bell polynomials：degree n
混入全部 `1,...,n`，故不存在由此 identity產生的 bounded same-block linear map。AP7的
same-scale Möbius no-go不能直接封閉 prime-linear Laguerre block。

另可把 AL5量詞固定為 `H_N=ceil(log(N+2))`：RH iff 對每個 epsilon有 arbitrarily large N
使 `sum_(n=N)^(N+H_N)|a_n|^2<=exp(epsilon N)`。RH false時 fixed syndetic gap L終會被
H_N捕捉；RH true時 ell2 tail直接給結論。其 exact dual即 `laguerre_vs_mobius_block_audit.md`
的 LB9.1。下一步只攻此 logarithmic-width prime-centered signed embedding。

## L53（已證 LB9 producer no-go）：positivity加 PNT envelope不推出 quiet blocks

取 `1/2<theta<1`、model centered error `g_theta(t)=exp(theta t)`。它滿足
`g_theta<=exp(t-ct^alpha)` 的 PNT允許 envelope，且可加到 Li形成正 increasing measure。
但 ordinary-Laguerre coefficient精確為
`(-theta)^n/(1-theta)^(n+1)`，所以任何 `H_N=ceil(logN)` block皆有 fixed-base
exponential energy，違反 LB9.1。

故 cumulative discrepancy、uncentered positivity與只讀這兩項的 generic signed-Carleson
theorem均被排除。LB9.1若存活，必須實際使用 prime-power離散 nodes/weights或其特殊
correlation。

## L54（已證 explicit CD form）：LB9.1等價可計算的 prime--continuum平方

令 `P_n=L_n-L_(n-1)`、`H=ceil(log(N+2))`、
`K^Delta_(N,H)(t,u)=sum_(n=N)^(N+H)P_n(t)P_n(u)`，並設

```text
V_(n,Y)=sum_(p^j<=e^Y)P_n(jlogp)/(j p^j)-int_0^Y P_n(t)dt/t.
```

則 `a_n=lim_(Y->infinity)V_(n,Y)`，且 `sum|V|^2` exact展成 LM6.3 的
prime-prime、prime-continuum、continuum-continuum三項。LB9.2要求其完整 centered square
在 arbitrarily large N上 `<=exp(epsilon N)`。

量詞是先 N後 Y趨無限；fixed-N PNT convergence不能換成 uniform-in-N constant。三項分開
triangle會刪掉唯一 centering，因此 diagonal-only或 positive sampling bound均不合格。

## L55（已證 finite moment matrix）：LB9.2是 associated-Laguerre binomial joint norm

由 `L_n-L_(n-1)=-(t/n)L_(n-1)^1`，定義

```text
R_j(Y)=sum_(r<=e^Y)Lambda(r)(logr)^j/r-Y^(j+1)/(j+1),
U_n(Y)=sum_(j<n)(-1)^j binom(n,j+1)R_j(Y)/j!.
```

則 exact `nV_(n,Y)=-U_n(Y)`，LB cutoff energy為
`sum_(n=N)^(N+H)|U_n(Y)|^2/n^2`。因此 prime theorem可直接對有限 moment vector驗收。
逐 j套 PNT再 triangle會被 binomial matrix的 fixed-base absolute condition放大，不能給
`exp(o(N))`；必須控制整個 Laguerre metric中的 joint cancellation。

## L56（已證 Selberg producer no-go）：additive convolution二次核必為 Hankel，LB核不是

令 `nu=sum Lambda(r)r^-1 delta_(logr)`、`lambda=dt`、`eta=nu-lambda`。Selberg identity
exact成為 `nu_2-2t lambda=t eta+2lambda*eta+eta*eta`，其中二次項永遠是
`doubleint phi(t+u)deta(t)deta(u)`。higher `Lambda_k` recursion也只用 additive
convolution與 output multiplication；任意二次 variation仍為 `h(t+u)`。

LB9.2 所需核
`J=sum_(n=N)^(N+H)L_(n-1)^1(t)L_(n-1)^1(u)/n^2` 不是 Hankel：最高 bidegree含
`t^(M-1)u^(M-1)`，但 `J(t,0)` degree僅 M-1；任何包含前者的 `h(t+u)`必同時含
`t^(2M-2)`，矛盾。故 Selberg/higher convolution不能 exact產生 LB PSD square；需另加
reflected two-variable inequality。

## L57（數值壓測，非證明）：真實 zeta 的 LB quiet blocks 在 N<=1000 存活

兩個 Cauchy半徑的 FFT係數在 checkpoints相符；4096 samples、50 dps 的 winding為0，虛部
leakage約 `1.6e-13`。六個 dyadic區間的 block-energy minima由 `2.65e-3`降到
`1.41e-7`，maxima整體由 `8.44e-3`降到 `7.70e-4`，但高度振盪。LB只需
subexponential good blocks，不需 fixed-rate exponential decay；高 off-line zero的 rate可小至
order `(beta-1/2)/gamma^2`，有限 N無法排除。

## L58（已定量詞與 local no-go）：正 producer需 block/cutoff uniform coercivity

任何正 form `P_(N,Y)(c)` 必須對所有 block向量 c及所有 eventual `Y>=Y_0(N,epsilon)`滿足
`kappa_N|<c,V>|^2<=P(c)+r||c||^2`，其中 `log kappa_N^-1=o(N)`，P的 operator upper與
remainder亦為 `exp(o(N))`。常數可依 epsilon,N，不能依 c或 Y-subsequence；不要求 all N。

fixed-prime generating identity
`sum_n v_(p,n)z^n=-log(1-p^(-1/(1-z)))` exact使用 `Lambda(p^j)=logp`，但 per-prime
PSD只給 `sum||v_p||^2`，漏掉 LM6.3 的全部 p≠q及 prime--continuum terms。triangle/Cauchy
損失隨 cutoff prime數發散，故 local single-channel law本身不符合上述 uniformity。尚需 global
cross-prime reflected/telescoping identity。

## L59（已證 geometry no-go）：pure ratio/reflection kernel也不等於 LB projector

log-scale reflected convolution只產生 `h(t-u)`。與 L56相同的最高 bidegree論證證
associated-Laguerre J也不是此 Toeplitz form。故把 `t+u`改稱 multiplicative-ratio
autocorrelation並未閉合；合格 theorem必須保留完整 nontranslation-invariant CD projector，
或給符合 L58 uniformity的比較不等式。

## L60（已證 topology no-go）：normalized Euler--Bohr mean看不見單一離線因子

取 `R(s)=(s-rho)/(s-a)`，其中 `Re rho>1/2>Re a`。每條 `sigma>1` 上
`logR(sigma+it)=O(1/t)`且局部 log singularity為 L2，故 normalized vertical B2 seminorm
為0；但 disk座標含 interior singularity `z_rho=1-1/rho`，Taylor coefficient有
`-z_rho^-n/n` fixed exponential。故只靠 long-time prime orthogonality／Bohr H2 的
producer不可能有 L58 coercivity；尚需 non-averaged analytic/winding transport。

## L61（已證 structural no-go）：所有 normalized stationary mean 候選一併排除

任意由 invariant normalized L2 mean支配的 seminorm都 annihilate `L2(R)`；L60的 log
rational factor屬 L2卻有 exponential LB blocks。連同 L56/L59 的 `t+u`/`t-u` kernel
obstruction，證明共同失敗機制是 stationary quotienting。下一 producer必須 anchored於絕對
log origin並保留 finite-height boundary與 winding/residues，不能再是另一個 mean theorem。

## L62（已證 exact anchored bridge）：LB Cauchy residues就是 W13--W14 obstruction

對 `D=K'` 與任意避開 zeros的 `|z|=r`，

```text
(2pi i)^-1 int D(z)z^-n dz
=n a_n+sum_(|z_w|<r)ord_F(w)z_w^-n.
```

取 `r_N=1-N^-1/2`，boundary factor僅 `exp(O(sqrtN))`；其 s-contour最低實部
`1/2+1/(4sqrtN)+O(N^-1)`、高度 `sqrtN/2+O(1)`。所以合格 anchored theorem需在這些
參數上有 `exp(oN)` uniform bound並保留全部 residues。任何固定 off-line zero給
`z_rho^-n` fixed exponential；略去 residue即假設 RH。故 nonmean LB producer與既有
W13/W14 sharp prime--archimedean residue obligation合流，不是獨立攻面。

## L63（已證 quantifier bridge）：LB good blocks與 W12 all-test只經 residue-empty等價

令 A為「每 epsilon有 unbounded logarithmic good blocks」、B為「無 `|z_rho|<1`」、C為
W12.4 all-test。則 `A<=>B<=>C`：A=>B由 nearest residue shell的 syndetic exponential
excursion；B=>A由 disk analyticity/Cauchy--Hadamard，且其實給 all sufficiently large N；
C=>B由 W14 orbit localization；B=>C由 critical-zero squares。

重要量詞修正：A的 failure witness是每個 remote fixed-length interval中的 coefficient；C的
failure witness是一個 orbit-localizing test。兩者沒有已證 bounded intertwiner或 LM11常數，
只透過 off-line residue集合為空合流。引用 W12.4直接控制 LB等於引用完整 RH-equivalent theorem。

## L64（已證、獨立於 RH）：nonlinear relative-clock convex barrier

對 finite window `I subset Z`、外部固定 clock、`x_j=jd+u_j` ordered，定義

```text
phi(y)=y-log(1+y),
E_d(u)=sum_(j<k)phi((u_k-u_j)/(d(k-j))).
```

則 series收斂、`grad E_d=-S`，其中 `S_j=PV sum_(k!=j)(x_j-x_k)^-1`；故 boundary-clock
zero flow `u'=2S` exact是 `u'=-2grad E_d` 且 `E_d'=-2sum S_j^2`。Hessian為 weights
`(x_j-x_k)^-2` 的正 graph Laplacian；quadratic tangent exact是 DN13 的 `Q/(2d^2)`。

若 `E_d<c_kappa=kappa-1-logkappa`，全部 gaps `>kappa d`，並有 window-uniform
`H_x<=kappa^-2L/d^2`、`||H_x||<=pi^2/(2kappa^2d^2)`。smooth-convex interpolation給
`||gradE||^2<=2Lambda E`，first-crossing bootstrap遂證

```text
E_d(t0)exp[2pi^2 tau/(kappa^2d^2)]<c_kappa
```

足以阻止整段 `[t0-tau,t0]` 的所有 collisions。checkerboard在 kappa趨1時飽和 exponent，
所以仍需 zeta height上 `exp[-(tau/2+o(1))log^2Gamma]` theta rigidity。此 lemma本身不預設
RH；下一缺口是 varying clock、buffer flux及 theta-side initial energy bound。
## L65（已證）：nonuniform clock forcing與 exact co-moving comparison

對任意最小 spacing 為 `d_-` 的 frozen reference `y`，relative Bregman energy滿足
`grad E_y=S^y-S^x` 與
`E_y'=-2||grad E_y||^2+2<grad E_y,S^y>`。若 `E_y<c_kappa`，令
`Lambda=pi^2/(2kappa^2d_-^2)`，則

```text
sqrt(E_y(t))
 <=exp(2Lambda(t0-t))[sqrt(E_y(t0))+sqrt(2Lambda)||S^y||_2(t0-t)].
```

所以 hard cutoff 的 `||S^y||_2 asymp sqrt(n)/d` 不是可忽略 boundary term。若 reference
亦解同一 log-gas flow，centroid-aligned `F=||x-y||_2^2/2` 滿足
`-4Lambda F<=F'<=0`；`F(t0)e^(4Lambda tau)<(1-kappa)^2d_-^2/4` 為 uniform-in-degree
collision barrier。剩餘 obligation 是 theta zeros 對 exact co-moving reference 的
all-particle exponential `ell^2` approximation。
## L66（已證之量詞裁決）：`x^(-ct)` rigidity不能初始化 DN barrier

Polymath Theorem 1.5 對 `x>=exp(C/t)` 給 `H_t` 高零點相對 explicit quantile 的
`O(x^(-ct))` 誤差。DN16/L65 對長度 `delta` 的 backward step要求
`d exp[-C_1 delta log^2x]`。固定比例 `delta~t` 時前者少一個 `logx` 指數；若切成
`delta=O(t/logx)`，只能重置到 theorem range端點 `t~C/logx`，此時已知誤差為 constant、
gap卻為 `1/logx`。所以現有 theorem 一步及多步皆不夠；這不聲稱真誤差有相同下界。
## L67（已證）：exact nonlinear checkerboard saturation

對 `x_j=jd+(-1)^j a(t)`，PV log-gas exact降為
`a'=-(pi/d)tan(pi a/d)`，故
`sin(pi a(t)/d)=sin(pi a(0)/d)e^(-pi^2t/d^2)`。取極限 `a(0)=d/2` 會在
`t=0` collision，但 terminal displacement只有
`(d/pi)arcsin(e^(-pi^2t0/d^2))`。所以 DN backward exponent在完整非線性系統 sharp；
任何 clock附近連續的 terminal invariant都不能以 polynomial precision計出 collision number。
## L68（已證）：shrinking-margin terminal stability bound

DN23 collision terminal state與 clock的 normalized distance為
`epsilon_d=pi^-1 arcsin(e^(-pi^2t0/d^2))`。任何 separation margin為 `m_d`、連續模數為
`omega_d` 的 terminal detector必有 `m_d<=omega_d(epsilon_d)`。Holder detector因此
`C_d>=m_d epsilon_d^-alpha`。只有當 margin沒有同速指數衰減時才推出爆炸；shrinking-signal
surrogate未被無條件排除，但必以 `o(m_d)` arithmetic error驗證。

## L69（已證）：finite backward-heat discriminant collision counter

對 monic real degree-n polynomial `P_T`，令
`P_t=e^((T-t)D^2)P_T`、`D_P(t)=Disc(P_t)`。則 `D_P` 是 degree至多
`n(n-1)/2` 的 real polynomial，且若 `P_T` simple real-rooted，
`P_s` real-rooted iff `D_P` 在 `(s,T]` 無零。Sturm chain因此給 exact finite collision
decision。ordinary entire approximation不能傳遞此 theorem：
`[z^0]e^(TD^2)z^(2m)=T^m(2m)!/m!`，故 terminal compact-small perturbation可在過去成為 O(1)。
## L70（已證）：backward-heat collision degree has one sign

若 real heat solution `h_t=-h_xx` 在 rectangle boundary滿足 `(h,h_x)!=0`，且 interior
collisions regular，則每個 collision對 `F=(h,h_x)` 的 local degree皆為
`det DF=-h_xx^2<0`。故 collision總數 exact為
`-(2pi)^-1 Delta_boundary arg(h+i h_x)`，無 orientation cancellation。以 heat-compatible
`alpha+beta x` perturbation可為 degenerate collisions定義非負 algebraic multiplicity。
## L71（已證）：positive even heat kernel不保 collision-free homotopy

`h_t=e^t cosx+c e^(4t)cos2x` 來自 positive even frequency measure且解 backward heat。
在 `t_*=(log(1/c))/3,x=pi` 有 regular collision，`h_xx=-3e^t`。正原子以窄正偶
super-exponential bumps平滑後 collision由 implicit-function theorem保留。故 DN28 homotopy必須
使用 theta arithmetic mode coupling；positivity、evenness、smoothness與 decay不夠。
## L72（已證）：degenerate heat-collision local degree

real analytic nonzero heat solution在 multiplicity `m>=2` 的碰撞點作 parabolic scaling，
`epsilon^-m h(t*+epsilon^2s,x*+epsilonz)` 在 `C^1_compact` 收斂至
`a_m e^(-sD^2)z^m`。Hermite model在 `s>0` 有 m個實根，`s<0` 只留 `m mod 2` 個，故
local Brouwer degree exact為 `-floor(m/2)`。因此 L70 winding對所有退化碰撞仍無抵消，計數
倒退後生成的共軛 root pairs。
## L73（嚴格反例證書）：Xi vertical phase velocity不定號

Arb 320-bit certificate `experiments/certify_dn30_vertical_phase_failure.py` 在 exact-enclosed
第1、35個 zeta zeros證 `J(x_1)<0<J(x_35)`，其中
`J=H'H''-HH'''`。由 DN30.2，`partial_t arg(H_t+iH_t')` 因而不可能全域固定符號。
此反例只關閉 monotone vertical producer；L70/L72 collision degree不依賴該符號。

## L74（已證）：theta Fourier graph topology傳遞 entire collision degree

固定 `tau<T` 與 compact rectangle。以 terminal measure
`dmu_T=(1/2)e^(Tu^2)Phi(u)du` 表示
`H_t=int e^(-(T-t)u^2)e^(ixu)dmu_T`。moment-tail truncation、compact區間
Riemann quadrature及 rational mass approximation給 symmetric positive finite atomic
`nu_N`，使 `(h_N,h_(N,x))->(H,H_x)` 在 rectangle上 `C^1` 收斂。證明只需
`u^j,0<=j<=3` moments；constants不依 atom數。

若 `mu_R=min_(partial R)|(H,H_x)|>0`，任何 boundary誤差 `<mu_R` 的 approximant
與 target經 straight-line homotopy同 degree。故 DN26 monomial反例只排除 polynomial/Taylor
topology；theta的 Fourier topology無條件完成 non-naive degree transfer，但不估 margin或 degree值。

## L75（已證 exact reduction）：commensurate rational quadrature的 winding可代數決定

取 atoms `u=kdelta`、`a_k in Q_+` symmetric，並令
`q=e^(-(T-tau)delta^2) in Q`、`r=e^(-(T-t)delta^2)`、`y=delta x`。則

```text
p(r,y)=sum a_k r^(k^2)e^(iky),  (h_N,h_(N,x))=(p,delta p_y).
```

horizontal sides以 `tan(y/2)` rationalize；root-of-unity vertical sides則是 real algebraic
coefficient polynomials in r。Cauchy index/Sturm--subresultant chain可 exact計 boundary winding。
compatible rectangles與此類 quadratures在 L74 graph topology中稠密。

量詞必為先 regular rectangle R、再其 margin `mu_R`、最後 cutoff；沒有 `mu_R` lower bound便
沒有 uniform-in-X cutoff。raw `tau=0` margin又暗含 critical zeros simple，強於RH；應用
`tau_n downarrow0` 的 regular slices或 DN27 perturbation。三條殘餘實作因此共用同一未證支柱：
由 actual theta/prime weights證 expanding exact algebraic degrees為0，而不偷渡 bottom winding。

## L76（已證 equivalence audit）：expanding zero-degree obligation恰等價 RH

固定已知 real-rooted時間 T，取 regular `tau_n downarrow0` 與 spatial exhaustion。若每個 rectangle
的 degree皆0，L72的同號 local degrees強迫 `(0,T)` 無 collision；故每個 `H_t,t>0` real-rooted，
其中用 L66/DN22在每個 `tau_n>0` strip提供 uniform real high-zero exterior，排除 zeros從無窮遠
進入而逃過 compact degree。再由 locally-uniform limit/Hurwitz得 `H_0` real-rooted。反向若RH成立，de Bruijn forward
preservation使所有 `H_t,t>=0` real-rooted；任何 interior collision依 L72都會在 lower-time side
產生 nonreal pair，矛盾。故 zero-degree exhaustion iff RH。

所以 L74/L75閉合的是 transfer與finite exact decidability，不是較弱的 arithmetic theorem。
DN29、DN32、DN33之後沒有存活 producer可獨立證此等價 endpoint；三路合流只消除重複技術缺口，
不得列為接近RH的縮減。

## L77（已證 quantifier equivalence）：AP2.5/SC16.8 iff RH

AP2.5=>RH已由 SC16 beta升階、unconditional mean-square tail與 SC16.2a證明。反向若RH，
strong Nyman closure給 finite global approximants `C_j(1)=0`，global errors `epsilon_j->0`，
且每個 cost `K_j<infinity`。對任意 fixed `A>0`，在選好 approximant後才取
`T_j>=K_j^(1/A)`；於 `[T_j,T_(j+1))`重用 `C_j`，則 local error至多 `epsilon_j`且
`K_j<=T^A`。AP2.4 Hahn--Banach dual因此同樣成立。

所以 remote support允許、delta只要求趨零的 polynomial-window statement沒有獨立 rate內容；
它是 RH qualitative global closure的重參數化。要避免此坍縮，必須把 support/coefficients自然綁到
同一 T（如 explicit same-scale mollifier），或指定不能在 approximant後任意延遲T的 error rate。

## L78（已證 general filter）：free-window complexity bounds可由 global closure重參數化

令 approximants C各有 finite complexity `kappa(C)`，global error `E(C)`，且 local error
`E_T(C)<=E(C)`。若 `inf_C E(C)=0`，則對任意 unbounded increasing `g(T)`，存在 stepwise
`C_T`使 `kappa(C_T)<=g(T)` 且 `E_T(C_T)->0`：先取 `E(C_j)->0`，再選 thresholds
`T_j`使 `g(T_j)>=kappa(C_j)`，於 `[T_j,T_(j+1))`重用 C_j。

故任何只含「finite remote approximant、complexity<=g(T)、local error->0」的 criterion，若
qualitative global closure iff RH，就自動仍 iff RH。要通過此 filter，至少一項必須在選 C前固定：
explicit same-scale coefficient law、不可延遲的 support/height coupling，或 prescribed error-vs-T rate。

## L79（已證 escape toy）：rate coupling嚴格逃出 L78 scheduling

在 `ell^2(N)` 取 `y=(1/n)_(n>=1)`，令 admissible approximant為前 N座標截斷，complexity
`kappa=N`。則 global error

```text
E_N^2=sum_(n>N)n^-2,
1/(N+1)<=E_N^2<=1/N.
```

所以 qualitative global closure成立，且 free-window條件 `N<=T,E_N->0`可取 `N=floor T`。
但 natural rate-coupled條件 `N<=T,E_N<=T^-1` 對大T不可能，因
`E_N>=(N+1)^(-1/2)>T^-1`。故 L78不是另一個 iff-closure assertion；它只排除沒有
error/scale coupling的 scheduling。prescribed rate或預定 same-scale formula可有嚴格新增內容。

## L80（已證 gauge index formula）：extending GL+ gauge不改 collision degree

對 boundary nonzero map F及 `A:partial R->GL^+(2,R)`，polar decomposition給
`wind(AF)=wind(F)+ind(A)`，其中 `ind(A)`是 rotation factor作用於固定向量的 winding。
若 A nonsingular延拓到 rectangle，則 `ind(A)=0`，degree不變；若 AF被拉直到 zero winding而
F degree非零，A必不可延拓，且其 obstruction exact等於未知 degree。margin另滿足
`|AF|>=sigma_min(A)|F|`，所以 singular/ill-conditioned gauge只是把 boundary gap藏起來。

## L81（已證 shear no-go）：`(H,H_x+aH)`保留 DN32 zero-sign

任意 continuous time-dependent a給 determinant-one extending shear。於 simple real zero，若
`theta_a=arg(H+i(H_x+aH))`，heat PDE exact給
`partial_t theta_a=H_xx/H_x`、`partial_x theta_a=-1`，與 a及其 derivatives無關。
因此第1與第35 Xi零點的 vertical phase反號對所有此類 gamma/log-derivative normalization仍成立。
general extending gauge只能重分配 local velocity、不能改 total winding；nonextending gauge則編碼答案。

## L82（Arb嚴格證書）：第一 theta mode有 nonreal zero

對 `H_1=int_0^infinity T_1(u)cos(zu)du`，256-bit Arb integration、incomplete-gamma tail
與 complex interval Newton證 radius `10^-12` box
`20.6253460059217...+2.69715184233952...i` 含唯一 simple zero。故 first-mode transform
不屬 Laguerre--Polya，不能當 collision-free theta homotopy base。

## L83（Arb嚴格證書）：`T_1+lambda T_2`有 regular amplitude collision

Wronskian `W=h_1h_2'-h_1'h_2` 在
`x=22.142377661076422...` 的 radius `10^-12` interval有唯一 root，且
`lambda=-h_1/h_2 in [0.916291688 +/-8.82e-10] subset(0,1)`。Arb另證
`h_2!=0`、`H_lambda''!=0`，故 `(lambda,x)` Jacobian非零。加入第二 mode時 DN39非實支
必穿越 real double-zero wall；mode-amplitude homotopy不 nonvanishing。

## L84（已證 all-finite no-go）：每個 finite theta truncation有無限 nonreal zeros

令 `K_N=sum_(n<=N)T_n`。由 full modular evenness、`T_1'(0)>0`及所有 `n>=2`的
`T_n'(0)<0`，exact有 `K_N'(0)=-sum_(n>N)T_n'(0)>0`。兩次分部積分給
`H_N(x)=-K_N'(0)x^-2+o(x^-2)`，故 real zeros有限。double-exponential tail又給 H_N entire
order至多1；若 total zeros有限，Hadamard形式 `e^(az+b)P`與 evenness及 algebraic decay矛盾。
所以每個 finite N都有無限 nonreal zeros。finite defects只能隨 N逃到無窮遠，不能提供 LP exhaustion base。

## L85（已證 finite-span no-go）：任意 nonzero finite real theta combination皆非 LP

若 `K_c=sum_(n<=N)c_nT_n` 的所有 odd derivatives在0消失，analyticity使 K_c even。
但 `u->-infinity` 展開的第k係數為 nonzero scalar乘 `sum c_n n^(2k+2)`；evenness要匹配
`u->+infinity` double-exponential decay，迫使全部 moments為0，前N個 Vandermonde equations即得
c=0。故非零 c必有首個 nonzero odd derivative `2j+1`。

Repeated integration by parts給 fixed-sign algebraic tail
`H_c(x)~(-1)^(j+1)K_c^(2j+1)(0)x^(-2j-2)`，所以 real zeros有限；order<=1 Hadamard
仍迫使 total zeros無限，故 nonreal zeros無限。有限 mode coefficient space內任何 straight或
nonmonotone path都沒有 nonzero LP endpoint；必須從起點保留 infinite modular completion。

## L86（已證 horizontal orientation no-go）：`(A,A_x)` collisions可互相抵消

對 `Xi(x+ia)=A+iB`，collision map `(A,A_x)` 在 common zero的 Jacobian為
`A_aA_xx=-B_xB_ax=-(1/2)partial_a(B_x^2)`，無固定符號。exact harmonic toy
`A=x^2-a^2+3a-2`在 `(1,0)`、`(2,0)`的 orientations分別 `+2,-2`。故 harmonic/modular
completion本身不繼承 DN27 one-sign ledger。

## L87（已證 dichotomy）：analytic one-sign map恰回 argument principle/RH

改用 `(A,B)` 時，`det D_(x,a)(A,B)=|Xi'|^2>0`，multiplicity亦全正；其 boundary degree
exact是 horizontal rectangle內 Xi zeros的 argument-principle count。對 regular
`epsilon downarrow0` exhaustion，strip zero-degree iff無 off-critical zeros iff RH。
所以 horizontal shift要麼 orientation cancellation，要麼直接 RH count，沒有第三個較弱 topological ledger。

## L88（已證 schema-equivalence）：未指定的 coupled Bezoutian identity不是 producer

在 `K_a>=0` 已知時，若只要求存在 positivity-preserving `T_a` 與 `L_a>=0` 使
`K_(a/2)=T_a[K_a]+L_a`，則此存在式 iff `K_(a/2)>=0`：正向由保正性，反向取
`T_a=0,L_a=K_(a/2)`。因此 HS5 若沒有先驗指定的 operator class、顯式 theta/prime
公式及獨立 sign proof，只是把 HB descent改名；目前不能列為 active candidate。

## L89（已證 MB1量詞縮約）：window版本 iff explicit global Riesz--Möbius norm

固定 `m,k` 並令 `G_(m,k)(X)=integral_R|W_m R_X|^2dt`。對任意
`0<B<2m+1`、`X=T^B`，AP5.4給 `0<=G-E=o(1)`。故 MB1沿 `T_j`成立 iff
`G_(m,k)(X_j)->0`沿 `X_j=T_j^B`成立；反向對任意 global sequence取
`T_j=X_j^(1/B)`即可。`B`只有截窗作用，沒有獨立 arithmetic rate。AP6.4再把 G exact化成
`2pi integral_1^infinity|S_(X,m)(y)|^2dy/y^4`。

Burnol/Nyman support lower bound又給 squared error `>=c/logX`，所以不能另加 polynomial
decay來製造 rate leverage。定向文獻只在 RH加額外 zero-separation或改用 varying power tilt時
給 explicit convergence；未證也未反證本 Abel-corrected fixed-log family。核心仍是 AP7.2 joint square。

## L90（已證 hidden-dependence no-go）：inverse-`zeta'` producer不 uniform in multiplicity

Bettin--Conrey--Farmer 的 conditional bound假設
`sum_(|Imrho|<=T)|zeta'(rho)|^-2<<T^(3/2-delta)`；此式已強迫所有 zeros simple，因重零點
滿足 `zeta'(rho)=0`。RH不蘊含 simplicity，故該 theorem不能作 MB1的 RH-only converse或
unconditional producer。把 residue改成 multiplicity-r Laurent principal part會引入至 r階導數的
uniform bounds，沒有消掉依賴。此裁決不反證 MB1，只排除隱藏 zero-separation的移植。

## L91（已證 log-Cesaro identity/no-go）：MB1需要 Möbius-specific cross-scale sign

令 `L=logX`、`P_v(s)=sum_(n<=e^v)mu(n)n^-s`。moving endpoint weight為0，故 exact有
`LC_X(s)=integral_0^L[P_v(1)-P_v(s)]dv`，從而

```text
R_X(s)=L^-1 integral_0^L {1+zeta(s)[P_v(1)-P_v(s)]}dv.
```

在 weighted L2 Hilbert space，Cesaro mean `A_L`滿足
`(||A_L||^2)'=(2/L)(Re<A_L,Q_L>-||A_L||^2)`，符號一般不定；scalar path
`1,-1,1`即可使 energy先降後升。Jensen改估 sharp residual只丟掉所需 cancellation。
所以目前沒有非文獻 producer：合格的新 lemma必須直接給 Möbius-specific cross-scale signed
correlation；只把 AP7.2寫成 double inner product是等價改名。
