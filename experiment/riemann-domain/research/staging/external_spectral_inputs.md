# External spectral inputs (2026-08-14)

本檔只記錄可核查的原始論文結果、其防循環稽核，以及由此得到的新中介引理。
數值吻合不作證明。

## ES1. Suzuki 2026：有限尺度的 hidden generator 已無條件存在

來源：M. Suzuki, *Weil's quadratic form via the screw function*,
arXiv:2606.09096v1, https://arxiv.org/abs/2606.09096 。

令 `g` 為論文 (1.3) 的顯式 continuous screw kernel（prime、archimedean、
pole 三部分皆寫出），`P_a` 投影到 `L^2_0(-a,a)`，

```text
G_a=P_a(g*)P_a,       B_a=D^*G_aD,       D=i d/dx,
dom(B_a)=H^1_0(-a,a).
```

論文無條件證明：

1. `A_a`（localized Weil form 的自伴算子）是 `B_a` 的 Friedrichs extension；
2. 最低特徵值 `lambda_a` 對 `a` continuous；RH 等價於所有 `a>0` 皆
   `lambda_a>=0`（等價地，沒有 zero crossing）；
3. 對任意 `lambda<lambda_a`，以
   `T_a=A_a-lambda I>0` 定義 Hilbert space `H(T_a)`，則
   `mathscr D_a=i d/dx` 的 deficiency indices 是 `(1,1)`；
4. 每個自伴延拓的 spectrum 正是 entire function `W(a,theta;z)` 的 zeros，
   所以這些 zeros 對每個有限 `a` 都全實。

這是真進展：P19--P36 所缺的「有限尺度自伴生成元」不再是 blocker。新的
blocker 是把 finite-volume characteristic functions 作非循環的 `a->infty`
極限。

### ES1.1 防循環稽核

有限尺度實零本身不蘊含 RH，因為 inner product 用的是
`A_a-lambda I`，而 `lambda` 可選在負的 `lambda_a` 以下。要直接取
`lambda=0` 正好需要 `A_a>0`，即 localized Weil positivity。

Suzuki 的 Corollary 1.6 把足夠條件寫成

```text
exp(phi(a,z)) W(a,theta(a);z)
    -> z^2 xi(1/2-iz)/xi'(1/2-iz).
```

這是新的明確極限 target，不是已證結果。原文 Section 8.3 的 heuristic 在
`Assume RH` 後才令 `lambda=0` 並 Fourier-transform `G_a v=h`；故該 heuristic
不可反向當證明。另須把「every compact subset of C」嚴格改讀為避開
`Z(xi')` 的 locally uniform meromorphic convergence（或 spherical
convergence），因右端一般是 meromorphic，entire functions 不可能在含 pole
的 compact 上以普通 sup norm 收斂。

## ES2. Connes--Consani--Moscovici 2025：prolate approximant 已有正確極限

來源：A. Connes, C. Consani, H. Moscovici, *Zeta Spectral Triples*,
arXiv:2511.22755v1, https://arxiv.org/abs/2511.22755 。

對有限維 restriction `QW_lambda^N`，若最低 eigenvalue simple 且 eigenvector
even，論文構造 rank-one perturbation `D_log^(lambda,N)`；其 regularized
determinant是該 eigenvector 的 Fourier transform，因 self-adjointness 而全實零。

更重要的是，論文顯式定義

```text
k_lambda=E(h_lambda),
```

其中 `h_lambda` 是 prolate operator 的第 0、4 eigenfunctions 的零積分線性
組合，並已嚴格證明：`hat k_lambda -> Xi`，在每個 closed substrip
`|Im z|<1/2` 上 locally uniform。所用 input 包括

```text
||h_lambda-h||_infty = O(lambda^-2),
1-chi_4(lambda) ~ C exp(-4 pi lambda^2) lambda^9.
```

論文明列未證的兩步：localized Weil ground state 的 simple-even 性，以及
`k_lambda` 對該 ground state 的充分逼近。這比抽象 Hilbert--Polya 更可操作。

## ES3. 新的 uniform bridge lemma（候選中介定理）

令 `A_lambda` 是 localized Weil self-adjoint operator，離散 eigenvalues
`epsilon_1<epsilon_2<=...`。令 normalized explicit even prolate candidate
`k_lambda` 屬於 form/operator domain，設

```text
mu_lambda=<A_lambda k_lambda,k_lambda>,
r_lambda=(A_lambda-mu_lambda)k_lambda,
Delta_lambda=epsilon_2-mu_lambda >0.
```

由 spectral theorem 立即有

```text
dist_L2(k_lambda, ker(A_lambda-epsilon_1))
    <= ||r_lambda||_2 / Delta_lambda.                 (ES3.1)
```

若右側 `<1`，ground state 不可能是 odd（`k_lambda` even 且 parity sectors
orthogonal）；若 spectral window 中只有一個 eigenvalue，亦同時給 simple-even。

令 `a=log lambda`。對 `|Im z|<=eta<1/2`，Cauchy--Schwarz 給

```text
|hat f(z)| <= (int_-a^a exp(2 eta |x|) dx)^(1/2) ||f||_2
             = O_eta(lambda^eta ||f||_2).             (ES3.2)
```

因此要把 `L2` eigenvector approximation 升成 closed-substrip 的 compact-uniform
Fourier approximation，一個足夠的、真正 uniform-in-scale 條件是：對每個
`eta<1/2`，

```text
lambda^eta ||r_lambda||_2 / Delta_lambda -> 0.         (ES3.3)
```

再配合 ES2 已證的 `hat k_lambda -> Xi`，Hurwitz 即把 finite-volume real zeros
傳到 `Xi`，完成 RH。這不是 finite certificate；它是單一 all-scale 升階定理。

prolate leakage 的 `exp(-4 pi lambda^2)` 量級遠強於 (ES3.3) 所需的任意
`lambda^-eta`。所以此路徑的精確新 target 是證明一個 arithmetic intertwining
estimate，把 time-frequency leakage 傳成 Weil residual，並給不比它更快消失的
spectral separation：例如

```text
||r_lambda|| <= lambda^M (1-chi_4(lambda))^alpha,
Delta_lambda >= lambda^-M
```

對固定 `M`、`alpha>0` 已足夠。任何只驗有限 `lambda,N` 的批次仍不算進展。

### ES3.1 為何 generic positivity-improving 不能直接補 simple-even

Suzuki 的 small-`a` simplicity 使用 prime-free leading Dirichlet form；不能
直接延伸到所有 `a`。由其 `r_0(t)=-8(cosh(t/2)-1)` 得
`r_0''(t)=-2cosh(t/2)`，pole 部分的 quadratic form精確為

```text
-iint r_0''(x-y)v(y)conj(v(x)) dxdy
 = 2 Re(conj(M_+) M_-),
M_+=int exp(x/2)v(x)dx,  M_-=int exp(-x/2)v(x)dx.
```

它是 rank-two indefinite form（even/odd directions 符號相反），不是
Markov killing term。故不能只引用 Perron--Frobenius／Dirichlet semigroup 就宣稱
all-`a` ground state simple-even；必須利用 prolate--Weil 的特殊 intertwining
或另證 parity-sector gap。

## ES4. 其他外部路線的稽核

- Suzuki 2012 的 `Theta_omega` canonical system只在 `omega>1` 無條件顯式構造；
  延伸到所有 `omega>0` 正是 RH criterion，沒有提供 HS5 的 half-shift descent。
- Connes--Consani 的 semilocal trace framework仍把足以推出全 Weil positivity 的
  semilocal statement列為 conjecture；不能把 trace interpretation當 positivity。
- Rodgers--Tao 的 de Bruijn--Newman結果證 `Lambda>=0`，其 rigidity是反證
  `Lambda<0` 時的 forward real-zero regime；沒有提供 DN13 所需從固定正時間
  backward 到 0 的 `exp[-c log^2 Gamma]` pointwise clock estimate。

## ES5. 原訂下一步（經 ES7 稽核後降級）

原訂主攻 ES3，而非再擴張 moment/degree certificates：

1. 從 semilocal trace formula抽出 `QW_lambda` 與 time/frequency projections
   `P_lambda, F P_lambda F^-1` 的 exact operator identity；
2. 對 `k_lambda=E(h_lambda)` 計算 analytic residual（先在 quadratic-form dual
   norm，避免不合法地假設 operator domain）；
3. 尋找 parity-sector 第二特徵值的 variational lower bound；
4. 只有得到 uniform residual/gap estimate後才使用 Hurwitz。數值只能找尺度，
   不能代替以上任一步。

ES7 證明其中第 3 步不是普通 perturbation estimate：它本身已承擔排除 Weil
負方向的 RH 核心責任。因此不得再把 ES3 稱為「只差 gap 技術」。

## ES6. `E`-radical 給 exact boundary-residual identity，但不給 spectral ordering

來源：A. Connes, C. Consani, *Spectral Triples and Zeta-Cycles*,
arXiv:2106.01715, https://arxiv.org/abs/2106.01715 ，特別是 (3.1)--(3.3)。

對 even Schwartz `f` 滿足 `f(0)=hat f(0)=0`，

```text
E(f)(x)=x^(1/2) sum_(n>=1) f(nx)
```

的 range 無條件包含於 global Weil form 的 radical。若
`I=[lambda^-1,lambda]`、`H=E(f)`、`k=1_I H`，則對 support 在 `I` 的
admissible `v`，在共同 form domain內精確有

```text
QW_I(k,v)=QW(H-1_(I^c)H,v)=-QW(1_(I^c)H,v).          (ES6.1)
```

所以 Weil residual 的 arithmetic bulk 已 exact 消掉；只剩 time/frequency
cutoff leakage。Prolate operator diagonalizes
`P_lambda F^-1 P_lambda F P_lambda`，正好提供極小 leakage。這是 ES3 所要的
intertwining 骨架，而非僅數值類比。

但有兩個未閉合點：

1. hard-cutoff prolate eigenfunction未必直接屬於 `E` 所需 Schwartz domain；
   必須 smooth regularize並在 Weil form dual norm控制由此產生的 boundary terms；
2. (ES6.1) 只把 `k` 放到 **near-zero spectral subspace**。若 RH 假，localized
   Weil operator可有負 eigenvalues 位於其下；near-kernel不等於 ground state。
   因此 ES3 中 `mu<epsilon_2`／rank-one bottom spectral window不能由小 residual
   自動推出。必須另證「零附近的 prolate band 以下沒有負 spectrum」，而這正是
   最可能重新等價於 Weil positivity的地方。

故修正下一步：先證一個不預設正性的 spectral-ordering lemma，或改走 Suzuki
`W(a,theta;z)` 的極限而完全避開 ground-state identification。若 ordering lemma
的 proof直接使用 `A_a>=0`，即循環。

## ES7. hook gap 稽核：`epsilon_2-mu` 的 uniform 下界已是 RH 級命題

來源交叉核對：M. Suzuki, *Weil's quadratic form via the screw function*,
arXiv:2606.09096, Theorem 1.3 前後；其明述 RH 假等價於某個 `a` 有
localized lowest eigenvalue `epsilon_1(a)<0`。

由 interval 嵌入（把小區間函數延零）立刻有

```text
a<b  ==>  epsilon_1(b)<=epsilon_1(a).                (ES7.1)
```

所以若 RH 假，存在 `a_0,c>0` 使所有 `a>=a_0` 都有
`epsilon_1(a)<=-c`。現在若 normalized prolate candidate 滿足

```text
mu_a -> 0,  ||r_a|| -> 0,
r_a=(A_a-mu_a)k_a,
Delta_a=epsilon_2(a)-mu_a>0,
||r_a||/Delta_a -> 0,                                (ES7.2)
```

則 spectral expansion 給 `k_a` 對 ground eigenspace 的正交分量趨零；同時
ground coefficient 上有
`|epsilon_1-mu_a||<k_a,e_1>|<=||r_a||`。故
`epsilon_1(a)->0`，與 `epsilon_1(a)<=-c` 矛盾。換言之，ES6 若真給
`mu_a,||r_a||->0`，則 RH 假時下列至少一項必發生：

1. `mu_a>=epsilon_2(a)`（near-zero band 不是 bottom rank-one window）；
2. `Delta_a` 退化得至少和 residual 同階；
3. domain/tail estimate不足以使 strong residual趨零。

這精確回答 hook：任何足以完成 ES3.3 的 gap 下界，若沒有獨立的新 arithmetic
ordering mechanism，就不是輔助引理，而已經是一個 RH 證明。再者 CCM 2025
Section 8 只以數值觀察 higher Weil eigenfunctions也接近 higher prolate modes；
不能用那些圖宣稱 near-zero band 是一維或 gap 為 polynomial。故停止以單一
ground-state gap 為主攻，保留 ES6 boundary identity 為可重用的獨立成果。

## ES8. 不用 ground 的兩個候選；一個可行、一個仍有 shift 缺口

### ES8.1 直接證 explicit `hat k_lambda` 全實零

CCM 2025 Lemma 7.3 已證 `hat k_lambda -> Xi` 於
`|Im z|<1/2` 的 closed substrips。若能另證每個充分大 `lambda` 的
`hat k_lambda` 全實零，Hurwitz 立即證 RH，完全不需 Weil bottom ordering。
現有 Caratheodory--Fejer theorem不適用：它要求該向量是最低 eigenvector，
而 CCM 自己把這項辨認列為 missing step。合格的新 lemma 必須直接來自
prolate Sturm--Liouville、`E`-map 與 total positivity／Hermite--Biehler
intertwining；不能再引用 `QW-epsilon_1 I>=0`。

### ES8.2 finite-volume Weyl `m`-function 正常族

Suzuki 的 deficiency `(1,1)` 自伴延拓可取兩個 characteristic functions之比，
形成有限體積 Weyl `m_a`，因此每個 `m_a` 都是 Nevanlinna function。若可在
無條件 Dirichlet-series 區 `Im z>1/2` 證

```text
m_a(z) -> i xi'/xi(1/2-iz),                           (ES8.1)
```

並有上半平面的非退化 normal-family compactness，解析唯一性會把極限延到
整個上半平面；target 的 poles因此被排除，得到 RH。這比 entire `W` 趨近
meromorphic `z^2 xi/xi'` 的表述乾淨。

但 Suzuki 的 Hilbert norm 使用 `T_a=A_a-lambda I`、`lambda<epsilon_1(a)`。
若 RH 假，ES7.1 迫使可用 shift保持在負值以下，甚至可能向負無窮退化；文獻只
「預期」`W` 的 zeros不依 shift，未證。故 ES8.2 的精確新 target是：證
normalized Weyl cross-ratio 對 shift projectively invariant，或直接由 continuous
kernel `g(x-y)` 建構 shift-free `m_a`。若最後仍需 `lambda(a)->0`，路線又等價於
Weil positivity，須立即停用。

## ES9. prolate ODE 經 `E`-map 的 exact Mellin difference identity

這提供 ES8.1 可檢驗的 arithmetic intertwining 起點。令

```text
PW_lambda f=-d/dx((lambda^2-x^2)f')+4pi^2 lambda^2 x^2 f=chi f,
F(p)=int_0^infty f(x)x^(p-1)dx.
```

此處 `chi` 只表示 PW differential eigenvalue（ES18 後統一改記 `omega`），
不是接近 1 的 Fourier-compression/concentration eigenvalue。

兩次分部積分給 exact recurrence

```text
-lambda^2(p-1)(p-2)F(p-2)
+[p(p-1)-chi]F(p)
+4pi^2 lambda^2 F(p+2)=0.                             (ES9.1)
```

對未截斷 `H(u)=u^(1/2)sum_(n>=1)f(nu)`，其 Mellin transform滿足
`K(s)=zeta(p)F(p)`、`p=s+1/2`，因此

```text
-lambda^2(p-1)(p-2) zeta(p)/zeta(p-2) K(s-2)
+[p(p-1)-chi]K(s)
+4pi^2 lambda^2 zeta(p)/zeta(p+2) K(s+2)=0.           (ES9.2)
```

functional equation在 `Re p=1/2` 把 `p-2` channel與 `p+2` 的共軛 channel
配對，顯示一個可能的 bilateral Jacobi／canonical-system結構。真正的
`k_lambda` 是 interval truncation，故還有 ES6 boundary term；下一步只應嘗試
把 (ES9.2) 加上該 boundary term寫成明確 Hermitian transfer matrix，並檢查其
determinant/flux 是否正。若 symmetrizer含 `1/zeta(p)` 在 critical strip 的未知
poles，則此候選也循環。這是 analytic identity，不是數值證據。

### ES9.1 functional-equation symmetrizer 成功，但 untruncated HB 仍是同義改寫

令 `p=1/2+it`。functional equation與 Gamma recurrence精確給

```text
zeta(1-p)/zeta(3-p)
 =-(p-1)(p-2)/(4pi^2) * zeta(p)/zeta(p-2),
```

故 (ES9.2) 的 left coefficient恰等於 right coefficient的共軛；middle
coefficient `p(p-1)-chi=-(t^2+1/4+chi)` 為實。若 `f` real、Fourier-even而使
`H(u)=H(1/u)`，則 `K(-s)=K(s)`，於是三項式可全純地寫成

```text
(z^2+chi+1/4) K(iz)=R(z)+R#(z),
R(z)=4pi^2 lambda^2 zeta(1/2+iz) F(5/2+iz),          (ES9.3)
R#(z)=conj(R(conj(z))).
```

若 `R` 是 Hermite--Biehler，右側只有實零，便會推出 `K(iz)` 全實零。但
`F` entire，所以任何位於 `Re rho<1/2` 的 off-line zeta zero 都直接成為 `R`
的上半平面 zero。故「`R` 為 HB」本身已排除一半 off-line zeros，再由 functional
equation排除另一半；untruncated ES9沒有降低 RH 難度。

仍可能非循環的唯一部分是 **truncation boundary**：CCM 的 `k_lambda` 並非完整
`H=E(f)`，其 Mellin transform沒有 exact `zeta(p)` 因子。需把 ES6 boundary
項算成 finite-volume determinant `R_lambda`，並直接從 prolate flux證
`R_lambda` 為 HB；若最後令 boundary消失而重新露出 `zeta(p)` 並先假定其
zero-free，則仍循環。

## ES10. hard truncation 的 exact finite Dirichlet--Mellin formula

令 `f=h_lambda` 延零於 `x>lambda`，`I=[lambda^-1,lambda]`，以及
`k_lambda(u)=1_I(u)u^(1/2)sum_n f(nu)`。對 `p=s+1/2`，交換的是有限和，故
無收斂假設地有

```text
K_lambda(s)
=sum_(1<=n<=lambda^2) n^(-p) int_(n/lambda)^lambda f(x)x^(p-1)dx
=int_(1/lambda)^lambda f(x)x^(p-1)
   [sum_(n<=lambda*x)n^(-p)]dx.                       (ES10.1)
```

這與 untruncated `zeta(p)F(p)` 的關鍵差別是 bracket 為 finite Dirichlet
polynomial。把 x-axis 依 `x=n/lambda` 切段，可視為 prolate Sturm--Liouville
flow 加有限次 rank-one jumps。若
`Z_p(x)=sum_(n<=lambda*x)n^(-p)`，則 distributionally

```text
dZ_p=sum_(n<=lambda^2)n^(-p) delta_(n/lambda),
x^(p-1)n^(-p)|_(x=n/lambda)=lambda^(1-p)/n.           (ES10.2)
```

所以 Green identity中的 cutoff jump擁有共同 spectral phase `lambda^(1-p)`
與 scalar coefficient `1/n`；沒有 naked `zeta(p)`。

必要符號稽核：這 **還不是 positive rank-one jump**。實際線性項含
`(lambda^2-x_n^2)f'(x_n)/n`，其符號不定；而 jump 位於 Mellin test weight
`Z_p`，不是 prolate ODE 的 potential，故不會自動給 2x2 J-unitary monodromy。
要表示 `K_lambda`，至少須加入 accumulated-integral channel（3x3 affine
transfer），或解 inhomogeneous adjoint equation後以 boundary Wronskian表示。

下一個驗收項因此修正為：對這個 enlarged colligation找一個 **不依未知 zeros**
的固定 indefinite metric，證 interval propagation與全部 arithmetic source
共同 contractive/J-unitary並使 boundary scalar為 HB。若 metric sign仍要求
full `zeta(p)` scattering phase或 Weil positivity，路線再次循環。ES10.1--2
只是 exact finite identity，尚不是 positivity theorem。

## ES11. accumulated channel 的 local metric no-go；cumulative positivity仍未排除

在任一 `Z_p` 常值的小區間令

```text
q=lambda^2-x^2,  b=4pi^2 lambda^2 x^2-chi,
y_1=f,  y_2=q f',  I'=w_p(x)f,
w_p=x^(p-1)Z_p(x).
```

則 `Y=(y_1,y_2,I)^T` 滿足

```text
Y'=A_pY,
A_p=[[0,1/q,0],[b,0,0],[w_p,0,0]].                  (ES11.1)
```

直接解 fixed Hermitian metric 方程
`A_p^*J+JA_p=0`（要求同一 J 對所有 interval與 critical-line p 成立）得到：
`J_13=J_23=J_33=J_11=J_22=Re J_12=0`。唯一剩下的是

```text
J=c [[0,i,0],[-i,0,0],[0,0,0]],                     (ES11.2)
```

它在 accumulator direction退化。故不存在 nondegenerate fixed 3x3 local
metric；普通逐 interval J-unitary proof被排除。

可以加入 frozen dual port `r'=0` 作形式上的 4x4 symplectic dilation：

```text
f'=q^-1 y_2,
y_2'=b f-conj(w_p)r,
I'=w_p f,
r'=0.                                                (ES11.3)
```

取 `r=0` 恢復原系統。但此 dilation對任意 forcing `w_p` 都存在；其 Hamiltonian
含 `f-r` off-diagonal block，當 `w_p!=0` 時必 indefinite。因此 symplectic/J-unitary
本身不給 de Branges positivity。原始 canonical-system理論要求 Hamiltonian
positive semidefinite，才能保證 Weyl coefficient為 Nevanlinna function；參見
Romanov--Woracek arXiv:1904.03662 與 Langer--Pruckner--Woracek
arXiv:2108.10162。

### ES11.1 回應 nudge：只需累積正性，不必逐 `n` 正性

以上 no-go只排除「每個 partial interval/jump均由同一 metric正或守恆」；它
**沒有** 排除所有 `n` 相加後的 endpoint kernel為正。事實上 ES10.1 的單一
`n` summand一般既無 inversion symmetry也非 real-entire pair，要求逐 `n` HB
並不自然。正確剩餘 target是 cumulative Christoffel--Darboux identity：找 companion
`B_lambda` 並直接證

```text
[B_lambda(z)conj(K_lambda(w))-K_lambda(z)conj(B_lambda(w))]
 /(z-conj(w))  >= 0                                  (ES11.4)
```

為 positive kernel。sign-indefinite `q(x_n)f'(x_n)/n` 可以在完整和中 telescoping；
必須實際展示 sum-of-squares／Gram factorization，不能由逐 jump失敗推論累積失敗。
反之，若 (ES11.4) 的 proof使用 `QW-epsilon_1 I>=0`，就回到 ES7循環。

外部 Mellin文獻（Coffey arXiv:math-ph/0612085、arXiv:1308.6821）證 Hermite
functions 的 **完整** Mellin transforms具有 critical-line polynomial zeros；
目前未找到對 incomplete Mellin integrals或 prolate deformation的相應 theorem。
它們可提供 companion/interlacing的 base case，但不能直接套到 ES10 finite sum。

## ES12. cumulative target 的 Hardy／inner 精確化

為避免 `k_lambda` 的小 inversion defect，先在 log variable作 exact symmetrization

```text
kappa_lambda^s(x)=[kappa_lambda(x)+kappa_lambda(-x)]/2,
F_lambda(z)=int_(-a)^a kappa_lambda^s(x)e^(izx)dx.
```

CCM 的 strip convergence與 `Xi(-z)=Xi(z)` 保證 `F_lambda->Xi` 仍成立。定義

```text
E_lambda(z)=int_0^a kappa_lambda^s(x)e^(-izx)dx,
E_lambda#(z)=conj(E_lambda(conj(z))),
F_lambda=E_lambda+E_lambda#.                         (ES12.1)
```

因此一個完全 cumulative、足以完成 RH 的命題是

```text
U_lambda(z)=E_lambda#(z)/E_lambda(z)
```

在上半平面 analytic 且 `|U_lambda(z)|<1`。這等價 `E_lambda` 為
Hermite--Biehler，亦等價 ES11.4 的 de Branges kernel正；不要求任何單一 n
summand正。邊界上 `|U_lambda(t)|=1`，所以這就是證完整 arithmetic/prolate
ratio為 inner function。

Connes--Consani, *The Scaling Hamiltonian*, arXiv:1910.14368, Lemma 3.4與
Corollary 3.5 給 operator版本：對 Hardy projection `P` 與 boundary unitary
`U_lambda`，inner property等價

```text
P U_lambda = P U_lambda P,                            (ES12.2)
```

或等價 Hankel defect `(1-P)U_lambda P=0`。該文也精確指出 individual local
zeta factors雖在 critical boundary為 unit modulus，卻因 half-plane poles／
unboundedness而不是 inner；所以逐 prime／逐 n positivity不是可行要求。

Prolate concentration最多先給 `(1-P)U_lambda P` 很小；這不等於 (ES12.2)，
因靠近 real axis沒有 uniform HB margin，小 defect不能排除少量 nonreal zeros。
合格進展必須是：(i) exact cumulative cancellation使 Hankel defect為零，或
(ii) 一個 quantitative positive lower bound支配 defect並對整個上半平面一致。
若此 lower bound取自 Weil ground positivity，仍回到 ES7循環。

## ES13. dense-core closure lemma：累積 leakage 不必 operator-norm 小

令 `P` 為 Hardy projection，`U_j` 為 boundary-unimodular multipliers，且
`U_j -> U` weak-star 於 `L^infinity`。若存在 dense `D subset H^2` 使每個
`f in D` 都有

```text
||(1-P)U_j f||_2 -> 0,                               (ES13.1)
```

則 `U H^2 subset H^2`。對 `g in (H^2)^perp` 取 matrix element即有
`<Uf,g>=lim <U_jf,g>=0`；先在 D 成立，再由 `||U_j||_infinity=1` 延到全部
`H^2`。因此 `U in H^infinity` 且 `|U|<=1`。若另有 `|U|=1` a.e.（例如
`U_j->U` in measure／a.e.，無 boundary modulus loss），U 才是 inner。
weak-star 極限本身不保存 unimodularity。此 closure lemma不要求
`||(1-P)U_jP||->0`，但必須單列 modulus-retention gate。

這提供真正 all-mode lift：對每個固定 prolate index n，classical fixed-n
asymptotics給 `h_(n,lambda)->h_n` 且 concentration leakage趨零；Hermite
functions `{h_n}` 是 dense basis。若能證一個對所有 fixed n 同型的 intertwining

```text
(1-P)U_lambda T_lambda h_n
 = S_lambda (prolate leakage of h_(n,lambda)),        (ES13.2)
```

其中 `T_lambda h_n->T h_n` 且 `T{h_n}` 在 `H^2` 稠密，則 ES13.1一次給
cumulative innerness。這不是逐 degree certificate：n 固定後取 lambda極限，
再由 basis稠密性與 multiplier uniform boundedness封閉全部輸入。

目前三個精確缺口：

1. nonlinear ratio `U_lambda=E_lambda#/E_lambda` 尚未與 time-frequency
   compression建立 (ES13.2)；單純 `E`-Poisson identity不足。
2. ratios 的 weak-star convergence與 boundary modulus retention都需要
   denominator控制；不能只由 `F_lambda->Xi` 推出。
3. innerness只排除非共同 zeros；仍須證 `E` 與 `E#` 沒有 nonreal common
   factor，或改用天然 coprime companion。正 half-density本身不足：positive
   palindromic exponential polynomials可有 reciprocal off-unit common roots。

所以 ES13 是 genuine uniform lift lemma，但 arithmetic intertwining、ratio
compactness與 coprimality皆未閉合；不得只驗前幾個 prolate modes。

## ES14. Poisson/prolate leakage 與 Hardy defect 是不同 operator；通用 intertwining 不存在

Poisson summation給的 exact relation是

```text
R E = E F,                                           (ES14.1)
```

其中 `R` 是 log-inversion、`F` 是 additive Fourier transform。因此 prolate
estimate最多把 `(F-chi)f` 傳成 `(R-chi)E(f)`：它控制單一 output function的
inversion parity defect。ES13需要的卻是 multiplication operator
`M_(U_lambda)` 對 **所有 Hardy inputs** 的 Hankel defect
`(1-P)M_(U_lambda)P`。兩者沒有形式上的 operator identification。

而且不能存在只依 parity leakage的 universal bound。workspace HS7 已有 exact
even positive cosine kernel，其 inversion defect為零，但 Fourier transform在
half-shift後有 nonreal zeros；更簡單地，一般 real-even compact kernel的 transform
也不必 real-rooted。若有

```text
||H_(U_k)|| <= C ||(R-1)k||,
```

右側對這些反例為零，會錯誤推出 HB。因此 (ES13.2) 不能只由 (ES14.1) 與
prolate concentration導出，無論使用多少 fixed modes。

ES13 dense-core lemma本身正確，但要餵給它必須新增 Xi-specific cumulative
Bezoutian／score-sign term，精確區分「even」與「Hermite--Biehler」。這與 HS5、
W18 的 arithmetic positive-defect obligation合流。只有能從 ES10 finite sum
展示該額外 term的 Gram factorization時，prolate leakage才可作 error項；把
leakage單獨當主項的路線至此封閉。

## ES15. cumulative score 的 exact finite double-sum target

對 symmetrized log-kernel寫

```text
F_lambda(z)=int_(-a)^a kappa_lambda(r)e^(izr)dr.
```

若 `z=t+i eta`，Cauchy--Riemann直接給

```text
Im(F_lambda'(z)conj(F_lambda(z)))
 =-(1/2) partial_eta |F_lambda(t+i eta)|^2.           (ES15.1)
```

所以 anti-Pick/HB 的 cumulative score target是對所有 `t real, eta>0`

```text
partial_eta |F_lambda(t+i eta)|^2 >=0.                (ES15.2)
```

用 ES10.1，令 `r=log(x/n)`、`q=log(y/m)`、
`a_n(x)=f(x)/sqrt(n*x)`，則 exact 有

```text
Im(F'conj(F))
=1/2 sum_(n,m<=lambda^2) int_(n/lambda)^lambda int_(m/lambda)^lambda
 a_n(x)a_m(y)(r+q)e^[-eta(r+q)]cos[t(r-q)] dxdy.      (ES15.3)
```

這就是 nudge 所指的 **累積** sign；單一 `(n,m)` 不需同號。合格證明可讓
`q(x_n)f'(x_n)/n` 在完整 sum中 telescoping，但最後必須把 ES15.3 對任意
`t,eta` 重排成 nonpositive Gram form。`eta->0+` 的首階只給 real-axis
Laguerre inequality `F'^2-FF''>=0`；有限階/moment證書仍不足以推出完整 ES15.2。

ES15 與 A9.3、HS5 的 de Branges kernel是同一 uniform obligation；ES10 的
新增價值只在於提供 finite arithmetic/prolate coordinates，可能容許新的
summation-by-parts factorization。若無 all-(n,m), all-(t,eta) 重排，不得把
ES15列作獨立進展或以有限 sampling替代。

## ES16. prolate Green 分部的 exact boundary recurrence；bulk 不有限閉合

先對單一 prolate eigencomponent `f_nu`，`PW_lambda f_nu=chi_nu f_nu`，置

```text
J_(m,nu)(p)=int_(m/lambda)^lambda f_nu(x)x^(p-1)dx,
a_m=m/lambda, q_m=lambda^2-a_m^2.
```

在 `[a_m,lambda]` 對 Sturm--Liouville項完整分部（`q(lambda)=0`，其餘
upper boundary terms精確消去）得

```text
-lambda^2(p-1)(p-2)J_(m,nu)(p-2)
+[p(p-1)-chi_nu]J_(m,nu)(p)
+4pi^2lambda^2 J_(m,nu)(p+2)
+q_m a_m^(p-2)[a_m f_nu'(a_m)-(p-1)f_nu(a_m)]=0.    (ES16.1)
```

乘 `m^-p` 並對 `m<=lambda^2` 求和，boundary精確化為

```text
B_(nu,lambda)(p)
=lambda^(1-p) sum_m q_m f_nu'(a_m)/m
 -(p-1)lambda^(2-p) sum_m q_m f_nu(a_m)/m^2.         (ES16.2)
```

所以先前預期的 derivative jump外，還有不可漏掉的 `f_nu/m^2` 項。

但 bulk recurrence不在 `K_lambda(p)=sum m^-p J_m(p)` 上閉合：`J(p-2)` 與
`J(p+2)` 仍帶原 weight `m^-p`，若改寫成 shifted K就分別產生 `m^-2`、`m^2`
channels。反覆使用 ODE會生成無限的 arithmetic moment lattice；普通 3x3
accumulator或逐 m summation-by-parts沒有自動 finite closure。

另作必要修正：CCM 的實際 `h_lambda=c_0h_(0,lambda)+c_4h_(4,lambda)`，而
`chi_0!=chi_4`，故它不是單一 `PW_lambda` eigenfunction。ES15.3 必須拆成
`00,04,40,44` 四個 score channels，分別使用 (ES16.1)。尚可能提供有限結構的
只剩 eigenvalue difference `chi_4-chi_0` 所誘導的 coupled
Christoffel--Darboux/Wronskian identity；不能再把單一 `chi` recurrence套到
整個 h_lambda。

下一驗收項：用兩個 eigen-equations相減，尋找四 channel總和的 Wronskian
boundary formula，並檢查 zero-integral coefficient relation能否消去 ES16.2
中的 signed terms。若仍留下無限 `m^(2j)` hierarchy，ES15不會由 prolate ODE
有限閉合，便只剩 HS9 的 coupled Bezoutian obligation。

## ES17. 回應 nudge：oscillation 已是 Gram；真正障礙是 rank-two indefinite radial form

令 `dnu(r)=kappa_lambda(r)dr`，並定義 real vectors

```text
v(t,eta)=int e^(-eta r)(cos(tr),sin(tr)) dnu(r),
w(t,eta)=int r e^(-eta r)(cos(tr),sin(tr)) dnu(r).
```

因

```text
cos[t(r-q)]=(cos(tr),sin(tr)) dot (cos(tq),sin(tq)),
```

oscillatory factor本身是 rank-two PSD Gram kernel，且

```text
Im(F'conj(F))=v dot w,
partial_eta |F(t+i eta)|^2=-2 v dot w.                (ES17.1)
```

所以不需要 x,y 分部去消掉 t。真正的不定 kernel是
`(r+q)e^[-eta(r+q)]`；在 features
`(e^-eta r,r e^-eta r)` 上的 coefficient matrix為 `[[0,1],[1,0]]`，
signature `(1,1)`。逐 n positivity不可能；完整和只需證 cumulative vectors
`v dot w<=0`。

Green/CD 的合格輸出因此應是一個 dissipative polarization，例如

```text
w=-C_lambda(t,eta)v+J beta_lambda(t,eta)v+e,
C_lambda symmetric positive-semidefinite,
v dot e<=0,                                           (ES17.2)
```

其中 `J` skew，rotation項不影響內積。ES16 的兩 eigenchannels若有用，必須在
`00,04,40,44` 合計後產生 (ES17.2)；只處理 cosine phase或只在 `t=0` 成立
皆不足。構造 `C,e` 尚未完成，不能把此有限維幾何當作正性證明。

## ES18. 兩 eigenvalue Wronskian只控制 cross channels；diagonal obligation仍在

為避免記號混淆，本節以 `omega_nu` 表示 `PW_lambda` 的 **differential**
eigenvalue；CCM 用於 concentration leakage 的 Fourier-compression eigenvalue
另記 `chi_nu`。對 `nu,mu in {0,4}` 有 exact off-diagonal Green identity

```text
(omega_nu-omega_mu) int int f_nu(x)f_mu(y)K(x,y)dxdy
=int int f_nu(x)f_mu(y)(L_x-L_y)K(x,y)dxdy
 + boundary_(nu,mu)[K].                              (ES18.1)
```

所以 `omega_4-omega_0` 可重寫 `04,40` cross terms。但在 `nu=mu` 時左側
為零，(ES18.1) 只是恒等式，不能解出 `00,44` diagonal scores。實際

```text
S_h=c_0^2 S_00+2c_0c_4 S_04+c_4^2 S_44.             (ES18.2)
```

zero-integral relation `c_0 int h_0+c_4 int h_4=0` 只在一個 Mellin point給一條
linear constraint，並不令 `S_00,S_44` 對所有 `t,eta` 消失。因此兩模
Wronskian本身不足以證 ES17.1。

一個較強但清楚的充分 target是 vector-valued score matrix

```text
M_(nu,mu)(z)=Hermitian polarization of
             Im(F_nu'(z)conj(F_mu(z)))
```

對所有 `z in C_+` 皆 negative-semidefinite；較弱 target則只需
`c^*M(z)c<=0` 對 zero-integral coefficient vector c。ES18.1只能處理 M 的
off-diagonal entry，仍須 Xi-specific diagonal positivity及 cross Cauchy--Schwarz
bound。這與 HS9 的 coupled symplectic Bezoutian完全同型，故
`omega_4-omega_0` 沒有單獨提供 finite CD closure。

## ES19. 外部 matrix de Branges 理論只包裝正性，不能產生正性

外查 Mahapatra--Sarkar 的 finite-dimensional matrix de Branges 理論
(arXiv:2406.15194)及 operator-valued版本 (arXiv:2302.06297)。前者定義
`E=[E_- E_+]` 所生成的 vector de Branges space時，明列

```text
E_+^{-1} E_- in S_in^(n x n)                            (ES19.1)
```

為假設；其 reproducing kernel positivity與
`E_+E_+^*-E_-E_-^* >=0` 是 (ES19.1) 的結果。後者同樣從 positive
operator-valued reproducing kernel/de Branges operator出發。因此把 ES18 的兩模
score寫成 2x2 matrix kernel不會從 prolate orthogonality自動得到 positivity；
它只是把待證的 Schur/inner 條件換成標準語言。

而且要求完整 `M(z)<=0` 過強：它特別要求每個 diagonal scalar mode滿足
`M_00(z)<=0`、`M_44(z)<=0`。componentwise strip limit含
`zeta(s)` 乘 Hermite Mellin factor；只要其中一個 nonvanishing component在全
上半平面滿足該 vertical-modulus sign，便已排除 off-critical zeta zeros。
故 full matrix negativity本身已是 RH-level命題。正確最弱 target仍只是 CCM
zero-integral vector `c` 的 `c^*M(z)c<=0`；matrix de Branges文獻沒有提供這個
特殊方向的 sign。

Primary sources:

- https://arxiv.org/abs/2406.15194
- https://arxiv.org/abs/2302.06297

## ES20. 新 all-mode 結構：Fourier 正相位支上的 prolate 二次譜多項式

令 `L=PW_lambda` 為 `[-lambda,lambda]` 上的自伴 prolate Sturm--Liouville
operator，`L h_(n,lambda)=omega_n h_(n,lambda)`，並按 Sturm oscillation排序
`omega_0<omega_1<...`。有限 Fourier compression與 L commute；在 real-even
space其本徵值相位交替。稱

```text
H_+(lambda)=closure span{h_(4j,lambda): j>=0}          (ES20.1)
```

為正 Fourier-**phase** 支。這裡不是聲稱 finite Fourier eigenvalue等於 `+1`；
其 modulus一般小於 1，只有相位為正。CCM 2025 明確記錄 `n` 為 4 的倍數時
為 Fourier-invariant phase，且其 prolate標號與 Hermite標號一致。

在 `H_+(lambda)` 定義

```text
P_lambda=(L-omega_0)(L-omega_4).                       (ES20.2)
```

由 spectral theorem，對 `f=sum_(j>=0)a_j h_(4j,lambda)`，

```text
<f,P_lambda f>
=sum_(j>=2)|a_j|^2(omega_(4j)-omega_0)
                    (omega_(4j)-omega_4) >=0,          (ES20.3)
ker P_lambda=span{h_(0,lambda),h_(4,lambda)}.
```

令 bounded functional `ell(f)=int_(-lambda)^lambda f(x)dx`，並置

```text
Q_lambda=P_lambda+ell^*ell.                            (ES20.4)
```

第一 prolate mode可取 strictly positive，故 `ell(h_0)!=0`，`ell` 不會在
`ker P_lambda` 上恒為零。於是

```text
Q_lambda>=0,
ker Q_lambda={f in span(h_0,h_4): ell(f)=0}
            =span{h_lambda}.                           (ES20.5)
```

因 `P_lambda` 有 compact resolvent且 rank-one perturbation bounded，零是
`Q_lambda` 的 simple isolated ground eigenvalue，並有某個無條件 auxiliary gap
`delta_lambda>0`。這是第一次不依 Weil positivity、也不逐 degree 的 all-mode
定理：zero-integral條件把 CCM explicit `h_lambda` 從完整同相位 prolate tower
中唯一選成 ground state。

但 (ES20.5) **尚不推出** `Fourier(E h_lambda)` 全實零。任意向量都能被某個
PSD projection做成唯一 kernel；實零還需要 Toeplitz/convolution displacement
structure。Connes--van Suijlekom 2025 的 theorem假設 quadratic form kernel為
`D(x-y)`，不能直接套到 (ES20.4) 的變係數微分算子。

Primary sources:

- https://arxiv.org/abs/2511.22755
- https://arxiv.org/abs/2511.23257

## ES21. ES20 與實零定理之間的精確斷層：非卷積的 infinite-rank commutator

置 scaling generator `D=x partial_x`。在 interior core
`C_c^infty(-lambda,lambda)`，prolate operator可寫成

```text
L=D^2+D+lambda^2(-partial_x^2+4pi^2 x^2),
[L,D]=-2lambda^2(partial_x^2+4pi^2 x^2).              (ES21.1)
```

故

```text
[P_lambda,D]
=(L-omega_0)[L,D]+[L,D](L-omega_4)                    (ES21.2)
```

含非零四階 differential principal part，為 infinite rank。`ell^*ell` 的
commutator至多是 finite rank，不能消去 (ES21.2)。因此 ES20 的正算子目前沒有
Caratheodory--Fejer/CvS 所需的 translation/Toeplitz structure；matrix de Branges
也不能補此缺口。

剩餘可執行 bridge因此被精確化為下列二選一：

1. 證 hard-truncated arithmetic map `S_lambda:f -> 1_I E(f)` 把
   `Q_lambda` 共軛／壓縮成 log-variable 的 convolution positive form，允許一個
   可控 finite-rank boundary correction；或
2. 不要求 full conjugacy，直接從 `Q_lambda>=0` 與 Poisson arithmetic identity
   推出特殊 kernel vector `h_lambda` 的 cumulative score
   `c^*M(t+i eta)c<=0`。

第一項可用 commutator作 falsification test：若共軛後仍保留 ES21.2 的
infinite-rank bulk，就不可能只靠 finite boundary correction變成 convolution。
第二項則必須展示明確的 positive Green/Bezoutian identity；auxiliary ground-state
事實本身不得當作替代。RH仍未證。

## ES22. 修正 ES6：finite two-mode 不在 exact E-radical domain

重新讀 Connes--Consani 2021 原文 §3。global `E`-radical的 domain明確是
codimension two：even test function須同時滿足 `f(0)=hat f(0)=0`。其實際
prolate construction令

```text
phi_(2n)=psi_(2n)psi_0(0)-psi_0 psi_(2n)(0),
```

只 exact 保證 `phi_(2n)(0)=0`；下一步 Fourier parity在原文寫成 `simeq`。
對 CCM 2025 的 same-phase modes，若

```text
T_lambda h_n=tau_n h_n,
a_n=h_n(0),
```

則代 finite Fourier kernel的 output point 0，exact 有

```text
int h_n=tau_n a_n.                                    (ES22.1)
```

two-mode `c_0h_0+c_4h_4` 由 integral zero選取後，

```text
h_lambda(0)=c_0a_0(1-tau_0/tau_4),                    (ES22.2)
```

一般非零，因 `tau_0!=tau_4`。故 ES6 所稱 exact radical只能對已 smooth 且
double-zero的 test成立；finite CCM two-mode僅給 exponentially/super-polynomially
small domain defect，不能把 approximate parity寫成 exact bulk cancellation。

這不否定 CCM strip convergence，因後者只需要 `int h_lambda=0`；它修正的是
把 finite candidate投入 Connes--Consani radical theorem的合法性。

## ES23. 三同相位模態給 exact double-zero 與 uniform constraint theorem

置 `e_j=h_(4j,lambda)`、`a_j=e_j(0)`、finite Fourier eigenvalue
`tau_(4j)>0`。在 `span{e_0,e_1,e_2}` 中令 `d_j=c_ja_j`，取

```text
(d_0,d_1,d_2)
=(tau_4-tau_8, tau_8-tau_0, tau_0-tau_4).             (ES23.1)
```

則恒等式給

```text
sum d_j=0,
sum tau_(4j)d_j=0,                                    (ES23.2)
```

所以 `g_lambda=sum c_je_j` exact 滿足
`g_lambda(0)=int g_lambda=0`，且因三個 tau互異，此 line唯一。

同時在正 Fourier-phase支 `H_+=closure span{h_(4j)}`，

```text
R_2=(PW-omega_0)(PW-omega_4)(PW-omega_8)>=0,
ker R_2=span{h_0,h_4,h_8}.                            (ES23.3)
```

加兩個 functional squares `|f(0)|^2+|int f|^2` 後，kernel恰為
`span{g_lambda}`。一般地，正 phase支前 `r+1` 個相鄰 modes滿足

```text
R_r=product_(j=0)^r(PW-omega_(4j))>=0,                (ES23.4)
```

加 rank-r independent constraints便留下唯一 line。這是 genuine
uniform-in-r constraint升階；但與 Jensen degree/J24 Gaussian expansion無關。

還有 natural positive-measure表示。令

```text
mu_r=sum_(j=0)^r a_j^2 delta_(tau_(4j)),
```

取其 monic orthogonal polynomial `p_r`，則
`g_(r)=p_r(T_lambda)sum a_je_j` 滿足
`ev_0(T^k g_(r))=0` (`k<r`)。所以相關 Hankel determinants及 Lanczos
subdiagonals全正。`r=2` 時 `k=0,1` 正是 value/integral double-zero。
這些 polynomial的 variable是 concentration eigenvalue tau，不是 Xi Mellin
variable，故尚不提供 RH/Jensen PF-infinity。

Fuchs fixed-index asymptotic顯示 leakage hierarchy
`(1-tau_4)/(1-tau_8)->0`、`(1-tau_0)/(1-tau_4)->0`。配合 fixed-mode
prolate-to-Hermite estimate，(ES23.1) projectively趨向
`(d_0,d_1,d_2)=(1,-1,0)`，故 `g_lambda` 應趨向 CCM 的 Hermite
zero-integral combination。完整 proof仍須核對 finite-Fourier vs concentration
eigenvalue的 square-root normalization並把 CCM Lemma 7.3擴至 fixed mode 8。
詳細推導見 `three_mode_poisson_route.md`。

Primary sources:

- https://arxiv.org/abs/2106.01715
- https://arxiv.org/abs/2511.22755
- https://doi.org/10.1016/0022-247X(64)90017-4

## ES24. full positive-operator-to-convolution conjugacy 被 bulk shifts 排除

ES23.3 的 order-6 positivity只在 nonlocal phase支成立。在 full even space，
intermediate modes使 spectral polynomial改號。若要 full-space local PSD，可用

```text
[product_(n in {0,4,8})(PW-omega_n)]^2>=0,            (ES24.1)
```

但成 order 12；這再次說明 local PSD ground本身很容易構造而不蘊含 real zeros。

更強的 no-go來自 Mellin bulk。對一般 f，`PW` 的 Mellin action含
`F(p-2),F(p),F(p+2)`；經 global E-map、`K(p)=zeta(p)F(p)` 後，outer terms為

```text
-lambda^2(p-1)(p-2) zeta(p)/zeta(p-2) K(p-2),
4pi^2lambda^2 zeta(p)/zeta(p+2) K(p+2).               (ES24.2)
```

因此 cubic spectral polynomial有 nonzero `p+/-6` outer shifts（square版本至
`p+/-12`）。log-variable convolution在 Mellin座標必為 scalar multiplier；
nonzero shifts等價 interior multiplication by `u^+/-2j`，是 infinite-rank bulk。
finite-rank endpoint correction不能在 dense core上消去它。hard truncation只新增
ES16 boundary terms，不移除 bulk moment lattice。

故 ES21 option 1「整個 auxiliary Q 經 E 後等於 convolution positive form加
finite-rank boundary」封閉。保留的唯一較弱機會是：雖 full operator不共軛，
其 special kernel vector `g_lambda` 可能因 (ES23.1) 額外 cancellation而直接滿足
`c^*M(t+i eta)c<=0`。下一步只計算此 scalar direction。

Burnol Sonine/de Branges外查亦不直接補洞：canonical structure functions
`A_a,B_a` 無條件 HB且 zero density與 completed zeta同主階，但現有 theorem沒有
把 arithmetic `E(g_lambda)` 辨認為 `A_a/B_a` 或其 locally uniform limit；
generic Sonine/de Branges-space member也不必 real-rooted。故只能把
「special vector是 real-point reproducing kernel／associated function」列為需證
的新 identity，不能由 space membership推出。

## ES25. strip-only target 與 natural half-kernel companion 失敗

CCM convergence只在 `|Im z|<1/2` 的 closed substrips；排除 off-critical Xi zero
亦只需 `0<eta<1/2`。因此 ES15 的 all-upper-half-plane score target過強，應改成

```text
partial_eta |F_lambda(t+i eta)|^2>=0,
t in R, 0<eta<1/2.                                  (ES25.1)
```

把標準 positive-side Xi kernel寫成 one-sided transform `H`，其 natural HB差的
cosine kernel為

```text
A_eta(x)=2 int_0^infty Phi(v)Phi(v+x)
                    sinh(eta(2v+x))dv.              (ES25.2)
```

若 `A_eta` 遞減凸，Pólya criterion會給 cosine transform非負。但分部積分 exact
給 `A_eta'(0)=0`，而 diagnostic顯示 `A_eta''(0)<0`；更直接的 half-transform
modulus difference在 `t≈17` 對多個 `eta<1/2` 變負。故自然 one-sided `H` 不是
可用 companion；這只是分解的反例檢查，不是 RH反例。見
`experiments/results_strip_hb_diagnostics_2026-08-14.md`。

## ES26. hard-cutoff 高頻 jump polynomial

ES10 symmetrized transform的 log-kernel在每個 `r_n=log(lambda/n)` 有 arithmetic
cutoff jump。一階分部給

```text
F_lambda(z)=B_lambda(z)/z+O_lambda(|z|^-2),          (ES26.1)
B_lambda(z)=sqrt(lambda)g(lambda)
 sum_(n<=lambda^2)n^-1/2 sin[z log(lambda/n)]
 +lambda^-1/2(sum_(n<=lambda^2)g(n/lambda))
  sin(z log lambda).                                (ES26.2)
```

所以不能只用 outer endpoint作 sine-type tail；所有 arithmetic jumps同階出現。
不過 heuristic scan在 lambda=2,2.5,3 未找到 `0<Im z<1/2` 的穩健 nonreal roots；
lambda=2.5 的 endpoint polynomial非實根首先出現在 eta約 1.05。這保留一個
可稽核候選：證 (ES26.2) 在 critical strip為 Hermite--Biehler exponential
polynomial，再以 uniform `O(1/z^2)` Rouché控制 full transform。數值不算證明。

## ES27. Freedman 2026 Weyl--Volterra 全尺寸結構

外部 primary source https://arxiv.org/abs/2606.29555 對同一 Phi 建立 Weyl kernel

```text
K_omega(a,b)=1/2 int_|(a+b)/2|^infty y cosh(2omega y)
 Phi(y+(a-b)/2)Phi(y-(a-b)/2)dy.                    (ES27.1)
```

其可保留 exact input是共同二階 theta identity、Volterra boundary+tail formula，
以及 branch multiplier

```text
kappa(s,u)=(1-s-u)/(1+s+u), |kappa|<=1.             (ES27.2)
```

這確是 all-function-space contraction機制，優於 finite Jensen certificates。作者
沒有宣稱 RH，且明列 KLM-to-de Branges bridge未閉合。

## ES28. 小 omega tangent 證 bridge承擔完整 all-degree義務

對 `E_omega(z)=Xi(z+iomega)`，直接 Taylor 展開給

```text
K_Eomega(w,z)=omega B_Xi(w,z)+O(omega^3),            (ES28.1)
B_Xi=1/pi * [Xi'(z)Xi(conj w)-Xi(z)Xi'(conj w)]
                 /(conj w-z).                       (ES28.2)
```

而 ES27.1 因只含 cosh，`K_omega^KLM=K_0+O(omega^2)`。任何 regular pullback
`K_Eomega=T_omega^*K_omegaT_omega` 在 endpoint都必給 `B_Xi` 的全尺寸 Gram
factorization；這正是 `-Xi'/Xi` anti-Pick／A9--A12 obligation，等價全實零
結構。故 KLM positivity不會自動推出 RH。合格突破必須從 theta atoms獨立構造
此 pullback。

Freedman 的 exact Mellin atom split
`X_i(z)=B_i(s,z)+T_i(s,z)` 顯示 Volterra tail diagonal匹配，但 incomplete-gamma
prefix `B_i` 可以是主量。把 z-dependent prefix functional加入 graph norm只完成
augmented quotient bookkeeping；尚須證 z-independent joint-Gram isometry，否則
可能把 target Bezoutian寫回 domain。完整 audit見 `volterra_klm_audit.md`。

## ES29. endpoint-jet tower 是新的 uniform hard-cutoff mechanism

T3P4 的一般 constraint theorem可加入 endpoint jets。前 `m+3` 個 same-phase
prolate modes施加

```text
f(0)=int f=0,
f^(j)(lambda)=0, 0<=j<m.                            (ES29.1)
```

在 rank條件下留下唯一 line，並仍是 positive spectral polynomial加 functional
squares的 simple ground。ES10 每個 arithmetic cutoff的 left limit都取樣同一
`x=lambda`，故 (ES29.1) 一次把所有 cutoff jumps延後到 derivative order m；
high-frequency order `1/z` 只剩共同 outer boundary的單一 sine。

這是 uniform-in-jet的實質升階，亦直接攻 T3P6 hard-support regularity，而非 finite
moment certificate。Dunster 2016（https://arxiv.org/abs/1601.00699）提供 fixed-mode
large-bandwidth、含 endpoint區的 uniform PSWF asymptotics；下一個 exact lemma是
用其 error bounds證 boundary corrector coefficients在 central region消失，保留
CCM `h_0/h_4` projective limit。若只證 fixed m而需 `m->infty`，還缺 joint bound。

## ES30. endpoint-jet rank 已 generic 關閉

在 bandwidth `c->0`，same-phase prolate modes退化為 `P_(4k)`。endpoint jet
`P_(4k)^(j)(1)` 是 `L_k=4k(4k+1)` 的 degree-j polynomial；integral row由
Legendre orthogonality只 pivot column k=0。center row

```text
P_(4k)(0)=(2/pi)int_0^(pi/2)sin^(4k)(theta)dtheta
```

作為 `L_k` 的函數 strict completely monotone，故不在 degree `<m` polynomial
Vandermonde span。於是 T3P9 full constraint matrix在 c=0 row-full-rank；analytic
perturbation推出對 fixed m，positive lambda除至多離散 set外仍 full rank。

所以 endpoint-jet unique line不是 genericity猜想；可取 `lambda_j->infty` 避開
exceptions。剩餘真正難點已縮成 Dunster asymptotics下的 projective limit與
condition-number/uniform remainder，而非線性代數存在性。

## ES31. finite RH verification不能單獨關閉 drifting middle band

Platt--Trudgian（https://arxiv.org/abs/2004.09765）用 rigorous interval/ball
arithmetic、critical-line sign changes與 Turing counting證 RH到
`3,000,175,332,800`。這足以作固定 compact base，且完整 sign-change count可
排除該段重零；但 endpoint-jet approximants的 prolate bandwidth
`c=2pi lambda^2` 無界。single-sine tail的有效 onset隨 c漂移，中央 derivative
remainder含 `(Cc/t)^m` 尺度。故固定 verified height不能覆蓋所有 approximants的
intermediate band。除非另證 uniform fixed-height tail theorem，否則此 diagonal
拼接無效。

## ES32. Xi Bezoutian 是 K_0 的 exact Fourier--Laplace pullback

對 `Im z,Im w>0`，把半線 Laplace identity代入 (ES28.2)，再以
`q=t+r, q'=r-u` 換元並使用 Phi even，exact得到

```text
B_Xi(w,z)=4/pi int_R^2 K_0(q,q')
                    e^(izq-i conj(w)q')dq dq'.      (ES32.1)
```

關鍵 parity identity是

```text
int_(-p)^infty y Phi(y+d/2)Phi(y-d/2)dy
=int_|p|^infty y Phi(y+d/2)Phi(y-d/2)dy.            (ES32.2)
```

故原始 Freedman coordinate kernel `K_0>=0` 直接推出全部尺寸 `B_Xi>=0`，再由
Pick/Herglotz criterion推出 Xi全實零。這顯式關閉了先前未知的 tangent
KLM-to-de Branges map；不需 uniform omega。唯一 RH-facing blocker改為原始
`K_0` quadratic form positivity／normalized quotient-to-original lift。

## ES33. quotient-to-original gap不是例行 closure

Freedman Problem 15.15 後段已證 primitive Green boundary form為零，且 primitive
trace image完成後等於全 `X_R`。所以 lift所需 `D_q|Y=0` 等價 `D_q=0`，亦即

```text
Gamma^*Gamma <= C
<=> Q_Phi>=0 on the entire completed form domain.   (ES33.1)
```

原稿只提供 finite Galerkin Schur complement diagnostics，明列 continuum theorem
未證。由 ES32 的 Fourier converse，`Q_Phi>=0`／`K_0>=0` 與 Xi Bezoutian全正性
等價。因此新橋消除了不必要的 uniform-omega問題，但沒有把最後 positivity降成
技術性 closure；它精確定位了 RH-equivalent continuum Gram theorem。

## ES34. same-sign K_0 是 Hankel-square 的 infinitesimal Loewner derivative

令 `H_lambda` 為半線 Hankel operator，kernel
`e^[lambda(s+u)]Phi(s+u)`。直接 composition得

```text
K_0^(++)=1/4 (d/dlambda)H_lambda^2|_(lambda=0).      (ES34.1)
```

所以 Freedman moment inequality等價 `H_lambda^2` 的 infinitesimal Loewner
monotonicity。Yafaev 的 Hankel sign-function/quasi-diagonalization
（https://arxiv.org/abs/1303.4040；https://arxiv.org/abs/1403.3941）形式上把它
變成 anti-Loewner kernel (VK8.5)。但 Phi非 completely monotone，inverse-Laplace
object未必為普通正函數，且 full parity reflected block仍在；故這是全尺寸候選
座標，不是 positivity證明。

## ES35. K_0 給全部 degree 的同一 Gram source

微分 ES32.1 得 Xi Bezoutian的每個 Taylor compression皆為 monomials
`1,q,...,q^N` 在同一 `K_0` form中的 Gram compression。故 `K_0>=0` 一次推出
Xi 屬 LP，再由 Jensen theorem推出全部 degree hyperbolicity；這是 sought uniform-in-degree
mechanism。degree 3沒有升階力，只是此無限 Gram若成立時的一個 finite corner。
反之有限多 corners仍不能證 continuum K0 positivity。

## ES36. Burnol Sonine/de Branges 空間沒有辨認 Xi 為結構函數

Burnol（arXiv:math/0203120）無條件構造 Sonine 空間 `K_a` 及其 de Branges
結構函數 `A_a,B_a`；後兩者由空間正性而全實零，且零密度主階與 zeta 相同。
但同一論文明說一般 Sonine 函數可任意加入零，RH 並不對全部 Sonine 函數成立。
zeta 零在其框架中產生 evaluation vectors／quotient systems，並不把
`Xi` 證成某個 `A_a` 或 `B_a`。因此

```text
Xi belongs to / acts on a positive Sonine space
    != Xi is that space's Hermite--Biehler structure function. (ES36.1)
```

缺少的 target identification 等價於證 `B_Xi>=0`，即 ES32 的 `K0>=0`；不能由
ambient de Branges positivity 補出。此路只在能寫出 `B_Xi` 到 Sonine reproducing
kernel 的顯式正 pullback 時才重開。

## ES37. Dimitrov Wronskian／Lee--Yang 是全 Jensen 塔的等價座標

對 `dmu(t)=Phi(t)dt` 的正交多項式 `p_n`，Dimitrov
（arXiv:1311.0596, Thm. 1--3）給

```text
Xi has only real zeros
<=> W(p_1,...,p_n;z) has only imaginary zeros for every n
<=> int product_j(t-z_j)dmu(t) has the Lee--Yang property for every n. (ES37.1)
```

Leclerc identity更精確地把 `W(p_1,...,p_n)` 辨認成 Appell/Jensen polynomial；
所以這不是由正交多項式三項遞迴自動得到的新升階定理。普通 Karlin--Szego
Wronskian定理控制 real argument 上 consecutive OP Wronskians 的符號；這裡需要
rotated argument `ix` 的全階符號，兩者不可互換。raw moment Hankel positivity亦只
保證 `p_n` 存在，不保 (ES37.1)。合格的新輸入必須是 `Phi dt` 的 ferromagnetic
Lee--Yang 表示、或全部 n 的單一 correlation/Gram inequality；否則只是 RH重述。

## ES38. 2026 joint Jensen wedge 是真 uniform 輸入，但不覆蓋低 shift

Holland（arXiv:2608.08682v1, 2026-08-09）證存在 absolute `K>0` 使

```text
n^3 log^2(n+2) >= K d^5  =>  J^(d,n) hyperbolic.  (ES38.1)
```

這首次給 simultaneous degree--shift wedge，優於「每個 fixed d，充分大 n」。
其核心是匹配前五個 coefficient-ratio invariants到 real-rooted finite-free/Jacobi
model，再用 fifth-order holomorphic multiplier stability；故是解析 theorem，不是
更多 finite certificate。

但 complement

```text
n^3 log^2(n+2) < K d^5                         (ES38.2)
```

仍含每個固定 `n`（尤其 `n=0`）的任意大 `d`，所以仍是無限區域。微分關係

```text
d/dX J^(d+1,n)=(d+1)J^(d,n+1)                 (ES38.3)
```

只把 hyperbolicity 往較大 shift 傳遞；由 derivative 的實根反推 primitive 實根
還需所有 critical values 的交錯符號，正是尚未證的低-shift全階義務。因此 wedge
大幅縮小高-shift區，但不能與 degree 3 拼成 RH，也不允許恢復逐 degree刷證書。

## ES39. fixed-shift large-degree 極限精確返回 RH target

置

```text
F(X)=sum_(j>=0) gamma(j)X^j/j! = xi(1/2+sqrt(X)).
```

對 fixed `n` 與 compact `|X|<=R`，有

```text
J^(d,n)(X/d)
=sum_(j=0)^d [binom(d,j)/d^j] gamma(n+j)X^j
 -> sum_(j>=0) gamma(n+j)X^j/j! = F^(n)(X).       (ES39.1)
```

這是 rigorous local-uniform convergence：
`0<=binom(d,j)/d^j<=1/j!`，而 `F^(n)` 的正係數級數在每個 R收斂，故可用
dominated convergence。若某 fixed n 的 `J^(d,n)` 對所有充分大 d hyperbolic，
正係數使其零皆負；LP類在局部一致極限下封閉，遂得 `F^(n) in LP`。尤其

```text
J^(d,0) hyperbolic for all sufficiently large d
   => F in LP <=> RH.                              (ES39.2)
```

所以 Holland wedge外的 fixed-shift/large-degree sector不是可由另一個普通
asymptotic estimate掃掉的技術尾巴；`n=0` 那條射線已完整攜帶 RH。任何聲稱填滿
complement的 uniform theorem，若沒有新全正性機制，實際上只是在另一座標重證 RH。

## ES40. Lee--Yang class 的 weak closure 使模型極限路線邏輯完整

Newman--Wu（arXiv:1708.08820, Thm. 7）證：其具有 entire mgf、pure-imaginary
zeros與 sub-Gaussian integrability的 Lee--Yang probability class，在 weak
convergence下封閉；證明並由 tightness推出 uniform second-moment control，再用
compact-uniform mgf convergence與 Hurwitz保零區。因此若能構造

```text
mu_N = finite ferromagnetic/known Lee--Yang magnetization laws,
mu_N => Phi(t)dt / int Phi,                         (ES40.1)
```

便會嚴格推出 RH，且不需另外假設 moment convergence。`Phi` 的雙指數尾符合
sub-Gaussian要求。真正缺口完全在 (ES40.1) 的 explicit model/coupling construction；
一般 positive atomic quadrature不自動是 Lee--Yang，有限 moments匹配也不足。

## ES41. anti-Loewner functions 的完整 all-size 分類

Audenaert（arXiv:1008.2943, Thm. 2.1）分類所有使

```text
[(g(x_i)+g(x_j))/(x_i+x_j)]_(i,j)
```

對任意 size、任意正 points皆 PSD 的函數。all-order情形等價

```text
g(x)=alpha/x+beta*x+int_0^infinity x/(t+x^2)dmu(t),
alpha,beta>=0, mu>=0.                              (ES41.1)
```

等價地 `g(sqrt x)sqrt x` 是非負 operator-monotone increasing，而
`g(sqrt x)/sqrt x` 是非負 operator-monotone decreasing。套到 VK8.5：若 Hankel
sign object `sigma` 是普通 nonzero函數，則 same-sign K0 kernel經 diagonal
congruence後正是 `g=sigma'/sigma` 的 anti-Loewner kernel。因此 ES41.1 是具體的
uniform-in-size sufficient/necessary symbol target，不是 degree 3 certificate。

但 Yafaev座標中的 Riemann inverse-Laplace sign object目前可能是 distribution；
沒有 regular `sigma` 時不能取 logarithmic derivative，也不能套 ES41.1。即使成功
關閉 same-sign block，VK9 reflected block仍需 theta-specific contraction。故外部
分類提供明確方向，沒有自行完成 RH bridge。

## ES42. ES41 對 standard theta sign-symbol 的 compatibility obstruction

anti-Loewner函數必非負。若 VK8 standard Laplace symbol是 ordinary nowhere-zero
real `sigma` 且 `g=sigma'/sigma` 滿足 ES41，則 sigma固定正號並單調，從而
`Phi(t)=int e^(-tx)sigma(x)dx` 是 completely monotone。K0B12 的超指數尾排除任何
非零正 Laplace measure。故 ES41不能直接修補 Riemann的 distributional symbol；
必須先有一個不同的 multiplicative/theta transform並重新證明其 kernel分類。

## ES43. Suzuki shifted screw family 給 exact forward cone，但 backward descent 仍是 RH

來源：M. Suzuki, *Aspects of the screw function corresponding to the Riemann
zeta function*, arXiv:2206.03682v4, (1.1)--(1.3), Theorems 1.7--1.8,
(11.1)--(11.2)；並與 arXiv:2606.09096v1 的 localized Weil operator交叉核對。

定義 `Psi_omega`後，對 `eta>=0` 有 exact semigroup law

```text
Psi_(omega+eta)(t)
 =e^(-eta t)Psi_omega(t)
 +2eta int_0^t e^(-eta u)Psi_omega(u)du
 +eta^2 int_0^t(t-u)e^(-eta u)Psi_omega(u)du.       (ES43.1)
```

每個 coefficient/kernel 皆非負，所以正性只能無條件地向右傳。
Laplace side為

```text
F_(omega+eta)(s)=((s+eta)/s)^2F_omega(s+eta).       (ES43.2)
```

而 `Psi_0>=0` 對所有 t 成立恰等價 RH。逆運算必須微分並帶符號，
故現成 Volterra positivity 不能從 `omega>=1/2` 降到 0。合格的新輸出
必須是一個 theta/prime-specific proper invariant cone，使該半群在子錐上
可逆且保正。現有文獻沒有這個 cone。

## ES44. generic bounded Hankel theory不適用 common-range flux

Yafaev arXiv:1303.4040 將 self-adjoint Hankel positivity分類為 sign-function
positivity；Nehari/model-space theory處理 bounded Hardy Hankel blocks。但 K0B21 的
symbol `iXi'/Xi` 在 Xi zeros有極點，只在 `w in Ran(T_Phi)` 的 graph
cancellation後取值。`Ran(T_Phi)` 又在 ordinary `L2` 稠密；若 off-diagonal
block為 bounded，單邊符號會連續延伸到 independent half-line data，因反號
迫使 block為零。故外部 bounded-Hankel 定理不會自動證 K0；所需的
是 unbounded graph factorization，這正是文獻未供給的 Xi-specific input。

## ES45. Schoenberg 與 PF5 failure：raw Riemann kernel不能承擔全正性

Schoenberg 的 PF∞ classification（原始來源：*On Pólya frequency functions I*；
可核對 Gröchenig, arXiv:2007.12889, Theorem 1）要求 integrable PF∞ kernel的
bilateral Laplace transform為 Laguerre--Pólya entire function reciprocal，因而在
其收斂帶 zero-free。classical Riemann `Phi` 的 transform為 `Xi(is)`，而 Xi已知
有 real zeros，所以 raw translation kernel不可能 PF∞。這是解析 theorem，不是
數值推測。

W. Michałowski, *On the Pólya Frequency Order of the de Bruijn--Newman Kernel:
Certified Failure at Order Five*, arXiv:2602.20313v2，另給 explicit
`u0=0.01,h=0.05` 的 `5 by 5` Toeplitz determinant enclosure
`[-1.8472496e-9,-1.8472225e-9]`。該文清楚區分已 certified 的 PF5 failure與
撤回的 global derivative-tail claims；本研究只引用前者作 finite obstruction，
不把 interval evidence當作 RH 證明。

## ES46. Watson Markov-cycle稿的 PF∞ closure lemma為假

已下載 arXiv:2602.01248v1 source到
`external_inputs/watson_2602.01248/`。其 finite-positive-sum lemma錯把 mixed-column
determinants當成單一 PF kernel minors。translated Gaussians給 exact反例：

```text
f=e^(-x^2)+e^(-(x-4)^2),
f(2)^2-f(1)f(3)=4e^-8-(e^-1+e^-9)^2<0.
```

故 PF∞不對正加總封閉。對該稿特殊 logarithmic kernel更可直接積分：若
`q=s+3/4`，

```text
B Phi_W(s)=2C alpha^(-q)Gamma(q)zeta(2q).
```

其 continuation含 zeta zeros，不能是 PF∞ transform。稿中 centered half-density
inversion亦直接失敗：self-dual時兩側分別為
`t^-1/2 theta(t)-t^-1` 與 `t theta(t)-t`。因此這篇外部輸入沒有提供從 Markov
positivity到 Xi 的 bridge；反而嚴格標出「PF atoms相加」的錯誤升階。

## ES47. positive Hankel/reflection theory的適用邊界

Adamo--Neeb--Schober, arXiv:2105.08522，將 bounded positive Hankel operators
表成正 measure/Pick symbols。K0 same-sign block卻是

```text
A=1/4 (H_(tPhi)H_Phi+H_Phi H_(tPhi)),
```

即一般不正 Hankel operators的 anticommutator，不是 `h(x+y)` positive Hankel。
而 K0B22已證若 log-derivative off-diagonal flux能 bounded延伸並對 dense independent
half-line data保單邊符號，便必為零。故該外部理論可用來排除誤套，不能填補
unbounded graph cancellation。

## ES48. Pólya-like real-rooted approximants沒有 convergent LP exhaustion

Y. Shi, *Real-rooted Pólya-like approximations to the Riemann Xi-function*,
arXiv:1502.06844（頁面顯示 2026-03-22 revision），構造若干 Fourier transform
全實零的 kernels。但其 approximation criteria是：固定候選在 `t->infinity`
匹配 Riemann kernel尾部、在 `t=0` 匹配一至兩個值／導數，以及候選 transform
實零。它沒有證 family參數趨極限時 `K_m->Phi` 的全域 norm或 transform locally
uniform convergence。

只有後一種收斂才可用 Laguerre--Pólya closedness把實零傳給 Xi；而一旦證得，已
直接完成 RH。故該文提供可用的 LP toy factors，卻沒有 K0B31 所需的 convergent
factor/approximant system，不能當外部證明輸入。

## ES49. Shi 第一族其實收斂到另一個 LP kernel

對 arXiv:1502.06844 Theorem 1 的 coefficients直接取 Riemann-sum limit，得到
K0B32.2。共同 double-exponential envelope允許任意 exponential-weighted L1
dominated convergence，因此該 family的 transforms確實 locally uniformly收斂；
但極限是 explicit `K_infinity`，不是 Riemann Phi。其 tail相對主項有 `2beta/a`
修正，Riemann theta expansion沒有 algebraic `1/t` correction。

所以該文不是「差一個尚未證的 compactness lemma」；其第一 approximant family
有可計算的錯誤極限。這也具體回應 Selberg nudge：G41 所需的是跨臨界 weight
boundary、且 **以 Phi 為極限** 的一致估計，逐 m實零與逐候選 tail matching不夠。

## ES50. Hudson 定理關閉 raw Wigner positivity

Hudson, *Reports on Mathematical Physics* 6 (1974), 249--252，證明一維 pure state
的 Wigner density處處非負當且僅當 wavefunction是 quadratic exponential
(Gaussian)。K0B33.1 的 integrand是 Riemann `Phi` 的 pure-state Wigner function；
`Phi` 的 double-exponential theta tail排除 Gaussian。因此不能以
`W_Phi(y,xi)>=0` 作 K0的全正性來源。這是解析 obstruction，不是數值反例。

注意 theorem只排除 raw Wigner positivity，沒有排除 weighted tail
`int_|p|^infinity yW_Phi dy` 的 operator positivity；但 pointwise Weyl-symbol
positivity本身也不足以推出 positive operator。仍需 theta-specific anti-Wick或
star-square identity。

## ES51. Lagarias 與 Sondow--Dumitrescu 的 horizontal monotonicity criterion

Lagarias, *Acta Arith.* 89 (1999), 217--234，記錄 RH 等價於
`Re(xi_R'/xi_R)>0` 在 `Re(s)>1/2`；Sondow--Dumitrescu, *Period. Math. Hungar.*
60 (2010), 37--40，等價表述為 completed xi modulus沿每條右向 horizontal
half-line嚴格增加。K0B35.1--2 把這個既有 criterion exact辨識成 K0 Weyl symbol
的 center exponential moments。因此外部定理沒有新增正性，卻嚴格證明「先證
symbol moments」已吞回完整 RH。

## ES52. 2026 theta-kernel preprint：exact identity可用，positivity仍未證

2026-06-01 的 *A Theta-Kernel Reformulation of a Growth Theorem and the Riemann
Hypothesis* 將 `d_sigma|xi_R|^2` 積分分部成兩個 positive-amplitude sine modes；
其最終 Problem 1／Theorem 4 明確仍與 RH等價，與 K0B35 是同一 scalar obstruction，
沒有 operator Gram／Kraus lift。

其 Proposition 2 的書面 proof亦不能直接採信：Step 3 以「one verifies」帶過
`|A_n-A_1|` 的全域單調，且只驗右側在 `r=pi` 的導數為正便推整個半軸最小值在端點；
末端小數與未寫出的 tail bound不是完整 enclosure。Riemann `Phi` 的 strict
log-concavity倒可由本專案 J5 得到：`L'-uL''>0` 且 `L'<0` 立即給 `L''<0`。
但 K0B36 給 exact Gaussian-mixture反例，證明這個 score/log-concavity輸入本身
不控制 Fourier實零或 K0全正性。

## ES53. Planat paired-tail稿的 local analytic contradiction

Planat, *Curvature Transition Layers and Paired-Tail Positivity for the Riemann Xi-Function*
(Preprints 202606.1957v1, 2026-06-26) 明列 single-crest uniqueness、pre-crest block
positivity及 global bridge仍 open，故本身不證 RH。更嚴重的是其 Proposition 3
聲稱在 `p=-Phi'/Phi>0,p'>0,R>0` 下，
`H(a,lambda)=partial_a M(a,lambda a)` 對每條 ray滿足 `dH/da>0` 全域。

這與原點 Taylor展開 exact矛盾。令 `c=-Phi''(0)/Phi(0)>0`，則
`p(u)=cu+O(u^3)`；對 `u_+=(1+lambda)a,u_-=(1-lambda)a`，

```text
H=M[-p(u_+)-p(u_-)]=-2c Phi(0)^2 a+O(a^3),
dH/da=-2c Phi(0)^2+O(a^2)<0
```

於充分小正 `a`。原稿公式亦漏掉乘法因子 `M` 與 leading `-p'` terms。故其後依賴
該 proposition的 ray monotonicity／curvature chain不可輸入本研究；數值區塊更不能
替代此 analytic contradiction。

即使只保留該稿的 scalar hypotheses也不夠：K0B36.5 證 exact nonreal-zero
Gaussian mixture同時滿足 `p'>0` 與 `R=(p^2-p')'>0` 全域。故 Riccati curvature
必須配一個尚未給出的 theta-specific global coupling，不能自行升階。

## ES54. 2026 Wald/GGC 路線自己保留 signed-measure RH缺口

Polson, *Wald Couples in the Critical Strip* (SSRN 6986418, 2026-06-23) 摘要明述：
Riemann theta construction得到的 mixing measure是 signed；Jordan decomposition後
剩下一個 complete-monotonicity條件，而該條件在 critical continuation端是 RH-equivalent，
非由 infinite divisibility推出。這與 K0B30 的 prime--gamma signed telescoping及
ES45 Schoenberg obstruction一致。

另須避免字面誤讀「Xi infinite divisibility」：正規化 `Xi(t)/Xi(0)` 是 `Phi` 機率
密度的 characteristic function，但 Hardy theorem已無條件給 critical line上無窮多
zeros；非退化 infinitely-divisible characteristic function必 zero-free。因此可 ID 的
只能是 auxiliary Gamma mixture／convergent-side object，不可能是完整 Xi characteristic
function。此路沒有新增 all-degree positive measure。

## ES55. Siegel--Narain scale/moduli Laplace equation的可用部分

Siegel--Narain theta文獻中的標準 scale/moduli heat equation，在目前 rank-two
positive lattice上可逐項自證為 K0B37.1；因此不需借用物理 normalization。
它提供真正 theta-specific輸入 `(D_y^2-1)H=4Delta_zH`，並導出 rectangular
normal identity K0B37.4。可是一般 theta-lift/Siegel--Weil positivity是 moduli平均
後的 statement；K0只取 rectangular geodesic的 normal jet。文獻沒有 theorem把這個
restriction的 fourth-order stress變成 positive operator，故目前只列 interface，
不列已證 Gram。

## ES56. Holland 的 uniform Jensen 楔形是真升階，但沒有逆 shift

Holland, *A new hyperbolicity wedge and a joint semicircle limit for the
Riemann xi Jensen polynomials* (arXiv:2608.08682, 2026-08-09) 證明存在絕對
常數 `K`，使

```text
n^3 log^2(n+2) >= K d^5  =>  J^(d,n) 有 d 個相異負實根。
```

這是本研究第一次找到真正 `uniform-in-d` 的外部輸入，而不是逐 degree 證書。
正規化亦正確：若 `M_n=int_0^inf Phi(u)u^(2n)du`，則
`gamma(n)=n! M_n/(2n)!`。證明用 Laguerre、Jacobi、再一個 Jacobi 因子的
finite-free 乘法卷積，exact 匹配 `R_0,...,R_4`；五階 holomorphic multiplier
殘差為 `O(d^(5/2)/(n^(3/2)log n))`，由此得到楔形。

它沒有補上 RH：作者明言這只是 asymptotic region，沒有從 partial Jensen
hyperbolicity 到 RH 的 converse。導數恒等式
`(J^(d+1,n))'=(d+1)J^(d,n+1)` 只往較大 shift 傳；Rolle 不可逆，不能降回
`n=0`。楔形外仍有無窮區域 `d >> n^(3/5)log^(2/5)n`，degree 3 對此無橋接。

## ES57. finite-free convolution只保 forward cone；正根 inverse 被排除

Martinez-Finkelshtein--Morales--Perales, arXiv:2309.10970v3，Propositions
2.7/2.11/2.17 證 finite-free 乘法卷積在一因子全非負根時保持實根、交錯與
logarithmic mesh。這正好驗證 Holland comparison model 的 forward algebra。

但同文 Corollary 2.18：若 `p` 有相異正根，且 `q` 是 `p` 的 finite-free
乘法 inverse，則 `q` 不可能仍全為正根。故不能在正根 cone 內 deconvolve
Holland model 以恢復完整 Jensen polynomial。所需新輸入必須是 Xi-specific
全階 factorization，或不等同 deconvolution 的 reverse-shift/common-interlacing
定理；現有 finite-free preservation沒有提供它。

## ES58. Farmer 的 information-loss 警告可強化成 exact 正係數反例

Farmer (Adv. Math. 411 (2022), arXiv:2008.07206v2) 指出 repeated
differentiation會抹去原函數的非實零資訊，並給出高階導數全實零而原函數非實零的
entire例子。對本研究可用更小的 exact polynomial 直接封住 generic reverse shift：

```text
P(x)=x^4+8x^3+22x^2+24x+12,
P'(x)=4(x+1)(x+2)(x+3).
```

`P` 的所有 coefficients皆正，所有 `P^(n), n>=1` 都只有負實根；但 `P` 的
critical points為 `-1,-2,-3`，其值分別為 `3,4,3`，且兩端趨正無窮，故
`P(x)>0` 對所有實 x，四根全非實。於是即使所有 higher-shift Jensen族雙曲加
positive coefficients，也不能一般性推出 shift 0。任何 reverse-shift theorem
必須明確使用 Riemann theta/prime結構，不能只用導數交錯或 coefficient positivity。

## ES59. Shi 1706.08868 的 claimed LP exhaustion 有 exact index error

Shi, *On the zeros of Riemann Xi(z) function* (arXiv:1706.08868v1) 宣稱構造
real-rooted `H(14,n,z)` 並在 critical strip一致收斂至 Xi。原始 TeX 的關鍵
interlacing proof在 equations 2913--2964 有可直接否證的截斷改寫：原和為
`sum_(j=0)^m y^(2j)/(2j)!`（以及 odd analogue），「加入為零的奇次項」後卻寫成
`sum_(j=0)^m (y^j+(-y)^j)/j!`。正確 combined上限應為 `2m`，odd支為 `2m+1`。
例如 `m=1` 時原式含 `y^2/2!`，稿中改寫只含 j=0,1，完全遺失 `y^2`。

因此隨後以 tail index `m+2` 寫出的 incomplete-gamma／`_2F_2` identities不是
原有限和的 identities；`m=7n^3` 的 boundary asymptotics、`w_2>w_1` 及 U/V
全域交錯均失去依據。修正索引會把 boundary推到約 `14n^3`，不可沿用原 sign
balance。另其最後 Hurwitz段以 `R(n)-W(n)->0` 而 target `W(n)`隨 n變動，書面
量詞也不成立（雖可另設 fixed-n truncation嘗試修補）；但 upstream exact index
錯誤已足以否決整個 claimed proof。故此稿不提供 L10 family。

## ES60. Suzuki 2025 給出精確 causal-support 介面，但 endpoint 仍等價 RH

Suzuki, *Chains of reproducing kernel Hilbert spaces generated by unimodular functions*,
Ann. Inst. Fourier 75 (2025), 1463--1508，從 boundary-unimodular `u` 定義
`K_u=F^(-1)M_uJ#F`，並由 half-line compressions 構造正 Hamiltonian/RKHS chain。
其 Proposition 6.1 給出

```text
u 是 upper-half-plane inner function
iff supp F^(-1)u subset [0,infinity).                 (ES60.1)
```

對 `E_Xi=Xi+iXi'`，實軸上的
`u_Xi=E_Xi#/E_Xi=(Xi-iXi')/(Xi+iXi')` 自動 unimodular；但 `u_Xi` inner
正是 `E_Xi` Hermite--Biehler，亦即 RH。Theorem 2.7--2.8 在 `t=0` 辨識
model/de Branges space時先假設 inner／HB；無條件 shifted L-function例只覆蓋
`omega>=1/2`。故這是 all-degree canonical interface，沒有從 theta/primes推出
endpoint support。

合格的新輸入必須是不使用 `1/E_Xi` 或 zeros 的 causal factorization，再證其
boundary quotient為 `u_Xi`。Primary source:
https://aif.centre-mersenne.org/item/10.5802/aif.3705.pdf

## ES61. cyclic heat-kernel total positivity控制空間角度，不控制 Riemann scale

Kieburg--Li--Zhang--Forrester, *Cyclic Polya Ensembles on the Unitary Matrices and
their Spectral Statistics* (Constructive Approximation 57 (2023), arXiv:2012.11993)
把 circle/unitary-group Brownian heat kernel的 Jacobi theta weight放入 cyclic
Polya-frequency/determinantal ensemble；其 determinant變數是 circle eigenangle／
spatial transition variable，time只是參數。

Riemann kernel需要的是 `u=log(time)/2` 的 translation minors，並再施加
`(D_u^2-1/4)` completion。空間 TP 不會把 time trace變成 scale-translation
PF-infinity；K0B27 已解析排除後者，K0B38 又顯示 completion後逐格點 normal
stress換號。因此「theta 是 heat kernel，所以 K0/Phi 全正」有精確變數錯置。
Primary source: https://arxiv.org/abs/2012.11993

## ES62. KPS 2024 提供真全階 Levy/Pick升階定理；其 Riemann公式須自行修正

Konstantopoulos--Patie--Sarkar, *A new class of solutions to the van Dantzig
problem, the Lee--Yang property, and the Riemann hypothesis*, Ann. Inst. Fourier
74 (2024), 377--421（arXiv:2211.16680），定義

```text
J_Psi(t)=sum_(n>=0)(-1)^n t^(2n)/W_Psi(n+1),
W_Psi(n+1)=product_(k=1)^n Psi(k).
```

Theorem 4.4 證：若 `varphi` 是 Bernstein Pick function且有 1-separation，則
`Psi(u)=u varphi(u)` 生成的 `J_Psi` 屬 `D_L`，所以其 entire characteristic
function全為實零。這是可直接處理所有 degree 的外部定理，導出 J68/L12。

但該文 Riemann subsection equations (4.15)--(4.18) 不能原樣使用。它寫
`Theta(z)=xi(sqrt z)=sum gamma(n)z^n/n!` 且右側 gamma公式為正；Fourier表示卻
要求 `Xi(sqrt z)` 的係數交錯，正係數版本應是 `Xi(i sqrt z)`。其後 displayed
`varphi(n+1)` 另帶一個與 Bernstein positivity不相容的負號，且 `G(2n)` 中的
`64n(2n-1)` 與前式 `32 binom(2n,2)=32n(2n-1)` 也不一致。故只採用已證的一般
Theorem 4.4；Riemann matching改由 Fourier moments直接推導成 J68.1，避免紙面
sign/factor錯誤。

Source archived as `external_inputs/kps_2211.16680.tex`; primary publication:
https://aif.centre-mersenne.org/item/10.5802/aif.3600.pdf

## ES63. Hirsch--Yor perpetuity/remainder theory 對 L12 的精確限制

已下載並核對 Hirsch--Yor, *Bernoulli* 19 (2013), arXiv:1309.7801 原始 TeX。
對 Laplace--Bernstein exponent `varphi`，subordinator perpetuity
`I=int_0^infinity exp(-xi_t)dt` 滿足

```text
E[I^n]=n!/[varphi(1)...varphi(n)],
e=IR  (independent),
E[R^n]=varphi(1)...varphi(n).
```

兩個 moment laws皆 determinate。Corollary 3.1 又說 complete Bernstein exponent使
`I` multiplicatively infinitely divisible；Theorem 3.3以 `varphi'/varphi` 的 Laplace
measure刻畫此性質。套入 J69：若 KPS route成立，J69 的 explicit Abel mixing
variable必是該 perpetuity，故 `log I` 的 Levy measure在負半軸，並迫
`K_I''` completely monotone。反向不自動成立：任意正 Abel mixing density不必是
subordinator perpetuity，所以 J69沒有單獨證 RH。

來源：`external_inputs/hirsch_yor_1309.7801/bejsp01.tex`。

## ES64. 2026 orthogonal-combination theorem仍是 fixed-width，不閉合 Xi expansion

Durán, *Zeros of Linear Combinations of Orthogonal Polynomials*, Mediterr. J. Math.
23 (2026), Art. 148（arXiv:2505.11956）證：固定 `K` 與固定 coefficients時，能選
orthogonal-polynomial normalization，使

```text
q_n=sum_(j=0)^K gamma_j p_(n-j)
```

在 `n>=n0(K,gamma)` 後全實根並與 `p_(n-1)` 交錯。其 proof明確要求 `K` 固定，
門檻 (3.11) 含依 `K` 指數增長的常數。Romik 的 Xi Hermite expansion雖有正交基與
正 coefficients，但第 `N` 個 truncation含約 `N+1` 個 lower modes，即 `K=N`，且
coefficients隨 N變；不滿足此 fixed-width theorem。故它最多再次解釋高-index有限帶
實根，沒有提供 uniform all-mode closure或 RH。Primary sources:
https://arxiv.org/abs/2505.11956 and https://arxiv.org/abs/1902.06330

## ES65. Siegel transform／incomplete Eisenstein 提供 Haar-square，不提供標準格點符號

Kelmer--Yu, *The Second Moment of the Siegel Transform in the Space of Symplectic
Lattices*, IMRN 2021，將 lattice Siegel transform辨識成 incomplete Eisenstein
series，並證其 Haar-space second moment是明確 Hilbert norm（Theorem 1；文中亦給
Mellin--Eisenstein representation (1.10)）。在 dimension 2，這正支持 K0B39 將完整
Gaussian lattice theta放入 automorphic spectral machinery。

但 theorem積分遍歷 `SL_2(Z)\SL_2(R)` 的全部 unimodular lattices；Riemann kernel
取的是 standard rectangular orbit上的指定 basepoint/geodesic trace。Haar平均平方
不能推出單一 lattice point的 K0 form符號，也沒有 point-evaluation positivity converse。
故此輸入只告訴我們合格突破的形狀：需把每個 test `f` 構造成 automorphic lift，令
`Q_K0(f)` **exact等於** 一個 Haar second moment或 Rankin--Selberg norm；僅把 theta
寫成 incomplete Eisenstein integral不夠。

Primary source:
https://academic.oup.com/imrn/article/2021/8/5825/5314048

## ES66. Lagarias--Suzuki Eisenstein 實零族停在不可縮的 half-shift

已下載並核對 Lagarias--Suzuki, *The Riemann hypothesis for certain integrals of
Eisenstein series*, JNT 118 (2006), arXiv:math/0412039v4 原始 TeX。其核心 Theorem
2.1 是真正全階零點定理：若 genus `0/1` 的 `F` 滿足 functional equation，且全部
zeros落在 `|Re(s)-1/2|<a`，則每個 `c>=a` 的

```text
F(s+c)+exp(i theta)F(s-c)
```

全部 zeros在 critical line。對 Riemann函數取
`F(s)=xi(2s-1/2)`，已知 critical strip只給 `a=1/4`，最小 `c=1/4` 在原 xi
變數正是不可縮的 half-shift。其 truncation family explicit為

```text
I(T,s)=-zeta*(2s)T^(s-1)/(s-1)
       +zeta*(2s-1)T^(-s)/s,  T>=1,
```

並全在 `Re s=1/2` 零；但 `T=1` 是 rank-2 Weng zeta，不是 Riemann xi。

這不能產生 L10 exhaustion。讓 `c->0` 超出 theorem假設，除非先把 zero strip寬度
證到 `a=0`，即先有 RH。把變數縮放使 `a_N->0` 也同時把原 xi shift乘回固定
`>=1/2`，沒有改善。另一方面 `T->infinity` 時兩個 shifted xi terms在 critical line
兩側由不同項主導，沒有跨 strip的 locally uniform entire極限到 xi。故此輸入精確
證實 reverse-shift斷層，而非提供其解法。

Source archived as `external_inputs/lagarias_suzuki_0412039.tar` (gzip-compressed TeX).
Primary source: https://arxiv.org/abs/math/0412039

## ES67. Patie--Savov Stirling bound + Carlson theorem gives KPS interpolation uniqueness

已下載核對 Patie--Savov, *Bernstein-gamma functions and exponential functionals of
Levy processes* (EJP 2018; arXiv:1604.05960) 原始 TeX。Theorems 2.9--2.10給

```text
|W_phi(a+ib)|
 =sqrt(phi(1))/sqrt(phi(a)phi(a+1)|phi(a+ib)|)
  *exp(G_phi(a)-A_phi(a+ib))*bounded_error,
0<=A_phi(a+ib)<=pi|b|/2,
```

且 error在 `a>=a0>0` uniform bounded above/below。配合 Bernstein函數在右半平面的
線性 growth，這證 `1/W_phi` 為 exponential type，垂直 indicator至多 `pi/2`。

Carlson half-plane theorem的 indicator版本說：右半平面 analytic exponential-type
函數若在全部非負整數為零，且
`h(pi/2)+h(-pi/2)<2pi`，則 identically zero。套到 J73 的兩個 coefficient
interpolants，indicator sum至多 `pi`，所以 integer samples唯一決定插值。這是排除
所有 KPS候選的關鍵外部輸入，不是對 RH的先驗假設。

Source archived as `external_inputs/patie_savov_1604.05960.tar` (gzip-compressed TeX).
Primary sources: https://arxiv.org/abs/1604.05960 and the Carlson theorem in standard
right-half-plane indicator form.

## ES68. Suzuki 2606.09096：無條件 real-zero family是真的，極限橋仍是 conjecture

已下載逐行核對 Masatoshi Suzuki, *Weil's quadratic form via the screw function*,
arXiv:2606.09096。Theorem 5：令 `lambda_a` 為 localized Weil operator `A_a` 的最低
eigenvalue；對任意 `lambda<lambda_a`，`T=A_a-lambda I>0` 所建 Hilbert space中的
minimal first derivative有 deficiency indices `(1,1)`，其每個 self-adjoint extension
的 characteristic entire function `W(a,theta;z)` 全部 zeros實。這是無條件且非
finite-degree的 theorem。

它尚未給 RH。Section 7 在導出

```text
z^2 xi(1/2-iz)/xi'(1/2-iz)
```

前明確寫 `Assume RH`，用以取 `lambda=0` 及 `A_a>0`。無條件 shift必須保持
`lambda(a)<lambda_a`；而 `lambda_a` 隨 interval增大 non-increasing，所以若可令
`lambda(a)->0`，已推出所有 `lambda_a>=0`，即 Weil positivity。

另有形式量詞需修正：Corollary 6寫 normalized entire functions在 `C` 每個 compact
一致收斂到上式，但上式在 `xi'` zeros一般有 poles。普通 locally uniform limit of
holomorphic functions必 holomorphic，故字面敘述不可能成立。可用版本須要求
normalization holomorphic且 nowhere zero，並在 `C\Z(xi')` compacta收斂，或明確採
spherical meromorphic convergence；如此才可在 nonreal xi zero附近用 Hurwitz。

因此此外部輸入提供候選 exhaustion family，不提供 limit theorem。真正新缺口是：
不預設 `lambda_a>=0` 的 global shift control，加上 corrected meromorphic compact
convergence。Source archived as `external_inputs/suzuki_2606.09096.tar` and PDF.
Primary source: https://arxiv.org/abs/2606.09096

## ES69. Zenodo 19546495 claimed proof drops the ground-eigenvalue term

已下載並視覺核對 Viceré, *A Proof of the Riemann Hypothesis ... Semilocal Spectral
Descent* (2026)。核心 Theorem 2不是其所引 CCM/Connes theorem的結論。CCM只在

```text
QW_lambda^N-epsilon_N I >=0
```

所定 Hilbert norm中得到 rank-one perturbation self-adjoint，因而 selected ground
eigenvector的 Fourier transform有 real zeros。這不證原 `QW_lambda^N>=0`；後者還差
`epsilon_N>=0`，且 CCM 明說 continuum ground value未必非負。

claimed paper憑空把 determinant zeros寫成
`QW_lambda^N(g*g#)=sum|g_tilde(rho_k)|^2`。determinant formula只辨識 auxiliary
rank-one operator的 spectrum，並非任意 `g` 的 Weil-form spectral resolution；正確
finite matrix分解仍含 `epsilon_N||g||^2`。所以其 Theorem 3 所用
`QW_lambda^N(g_N)>=0` 沒有來源。compact support只使有限 prime-power local terms
穩定，不會消去 ground term或補上 determinant convergence。

完整 audit見 `external_claim_audit_vicere.md`。Source archived as
`external_inputs/vicere_zenodo_19546495.pdf`.
Primary comparison: https://arxiv.org/abs/2511.22755, especially Theorem 1.1,
Corollary 3.7, and Sections 7--8.

## ES70. Uniform Toeplitz wedge: genuine all-rank theorem, but only outside the critical cone

Micha\l{}owski, *An explicit uniform cubic wedge for consecutive Toeplitz minors of
the Riemann xi coefficients*, arXiv:2607.16795v1, defines

```text
G(z)=sum a_k z^k=(1/8)xi(1/2+sqrt(z)/2),
D_(r,k)=det[a_(k+j-i)]_(0<=i,j<r),
```

and proves the uniform statement

```text
D_(r,k)>0 for every r>=2 and k>=10^18 r^3.          (ES70.1)
```

This is not a fixed-degree certificate.  Its exact algebraic core is a
`q`-Vandermonde `LDL^T` factorization and the group
`R_alpha=L^(-1)diag(q^(alpha i))L`, while the analytic perturbation is controlled by
`r^3/k`.  Source audit shows that this group acts only inside a fixed `q=q_k`, fixed
rank comparison block.  It does not map `k` to `k-1`, and the proof explicitly fails
when `k/r^3` ceases to be large.  Thus the theorem supplies a real uniform wedge but
no reverse transport into `k=O(r)`, the RH-critical region.

Independently, Desnanot--Jacobi gives

```text
D_(r,k)D_(r-2,k)=D_(r-1,k)^2-D_(r-1,k-1)D_(r-1,k+1).
```

This is an exact discrete-Toda elevation, but positivity at rank `r` is precisely
log-concavity of the preceding determinant row, so it is not a free induction.
Rectangular Jacobi--Trudi duality further gives a fixed-shift all-rank reduction
`D_(r,k)/a_0^r=det[e_(r+j-i)]_(0<=i,j<k)` for
`sum e_nz^n=1/G(-z/a-normalization)`.  Its pole/Vandermonde proof is effective for
each fixed certified `k`; uniform growing `k` again requires the unknown ordered-real
pole structure.  Full details are in `toeplitz_uniform_route.md`.

Source archived as `external_inputs/michalowski_2607.16795.tar` and
`external_inputs/michalowski_2607_source/main.tex`. Primary source:
https://arxiv.org/abs/2607.16795

Reproducibility update (2026-08-15): a fresh download of the arXiv source tar
contains only `main.tex` and `00README.json`.  It does **not** contain the four
claimed ancillary certificate modules or the advertised 36-test suite.  The
`q`-Pascal identities in Gate B have short independent algebraic proofs in the
text and remain usable.  The directed-rounding claims in Gates A/C cannot
currently be rerun from the deposited source, so ES70.1 is recorded as an
external theorem whose advertised computer certificate is unavailable, not as
a locally reproduced certificate.

## ES71. Moving contour Hankel inertia preserves the obstruction

Deng--Yang--Lue, *Contour Hankel dynamics and indicator fields for the Riemann
Xi-function*, arXiv:2608.11520v1, proves that contour moments of `Xi'/Xi` are the
moments of the enclosed zero atoms.  The resulting Hankel matrix factors as
`V W V^T`; after stabilization, every real node contributes one positive direction
and every nonreal conjugate pair contributes one positive and one negative direction.

The moving-contour equation is a congruence flow only between zero crossings, hence
preserves inertia.  A nonreal conjugate-pair crossing is exactly a rank-two indefinite
jump.  Therefore requiring all these Hankel matrices to be PSD is equivalent to the
absence of nonreal crossings/RH.  The paper explicitly leaves derivation of positivity
independently of the zero set unresolved.  This is a clean localization theorem, not an
arithmetic all-degree positivity source.

Source archived as `external_inputs/deng_2608.11520.tar` and
`external_inputs/deng_2608_source/Riemann_Xi_contour_Hankel_revised.tex`. Primary
source: https://arxiv.org/abs/2608.11520

## ES72. Finite Guinand--Weil dictionary gives an exact real-axis square, not full positivity

Groskin, arXiv:2607.02828v2, constructs from every finite even Galerkin vector
`v` a band-limited test and proves

```text
<v,Q_inf^(c,N)v>=sum_(1/2+iz in Z(zeta)) g_v(z).      (ES72.1)
```

Direct autocorrelation calculation strengthens its transport to

```text
g_v(z)=L F_v(z)F_v(-z),
g_v(x)=L|F_v(x)|^2>=0 for x real.                     (ES72.2)
```

Thus this is exactly a finite Weil-square coordinate. Over all bands its PSD is the
localized Weil/RH endpoint. The second theorem writes only the post-band archimedean
increment as an integral of two Cauchy rank-one squares and proves that isolated tail
strictly totally positive; it excludes the archimedean head, signed primes and pole.

The matrices are Loewner divided differences at integer nodes, but integer value and
derivative data have the exact null perturbation `sin^2(pi z)h(z)` at the natural type
`2pi`, so a one-lattice Carlson uniqueness argument fails at the critical sampling rate.
Full audit: `finite_weil_dictionary_audit.md`. Source archived as
`external_inputs/groskin_2607.02828.tar` and `external_inputs/groskin_2607_source`.
Primary source: https://arxiv.org/abs/2607.02828

## ES73. Kim et al. 2607.24830：FEM positivity不是 endpoint下界

來源：T. Kim et al., *A Numerical Realization of Suzuki's Weil-Quadratic-Form
Operator*, arXiv:2607.24830v2。其無條件解析內容 R2 是 prime-free archimedean
small-aperture Mellin double-pole coefficient，沒有 zeta-specific prime sign。

對最低 eigenvalue，P1 Rayleigh--Ritz value是 true infimum 的 **upper bound**；正的
finite-element value不能證 true value正。原文表格只在 `a<=0.5` 尚可解析，`a>=0.6`
已 below resolution，並明說更大 `a` 是 extrapolation。R6 的 bounded residual方向
更在 proof第一行假設全部 zeros on line；§4明確承認 converse就是 RH。因此本文只作
數值/archimedean diagnostics，不能補 Suzuki 的 `lambda_a>=0` endpoint，也不作證明
輸入。Primary source: https://arxiv.org/abs/2607.24830

## ES74. Polson 6992163：Barnes clocks為正，但 Xi dual Thorin sign就是 RH

來源：N. Polson, *Barnes Beta Distributions and the Riemann Xi Function*, SSRN
6992163 (2026-06-24)。作者的 unconditional tier把 Biane--Pitman--Yor `S2,C2`
辨認為 Thorin measure支撐在 integer squares的 genuine GGC，並把 Barnes
`beta_(2,2)` 寫成以 `C2/16` 為正 clock 的 Gaussian subordination。這些是
archimedean/theta probability laws，不含未知 zeta-zero sign。

進入 folded variable `w=s(1-s)` 後，稿件把 Xi 的 Wald-dual Thorin measure寫成
`sum_rho delta_(rho(1-rho))`。這個 measure支撐正實軸恰要求每個 folded zero為
`1/4+gamma^2`，即 RH；摘要也明列「closing Wald couple／dual Thorin positivity」
為 open equivalent clause。故 Barnes positive clock不能轉移成 Xi dual positivity，
除非另證完整 zero/prime source的 sign。此稿提供清楚字典，沒有新 proof bridge。
Primary source: https://ssrn.com/abstract=6992163

## ES75. Schatz backward barrier：碰撞橋接被精確 heat-flow 反例否證

Kevin Schatz, *Riemann Hypothesis: Backward Parabolic Positivity Barriers for
the Xi Flow* 宣稱把 de Bruijn 實零 slice 的 Pick positivity 沿 backward heat
flow傳回 `t=0`。其核心 Lemma 7.3 不成立。精確反例是
`E_t(z)=z^2+1-2t=e^{-t d_z^2}(z^2+1)`。

`t>1/2` 時零點全實，`t=1/2` 碰撞，`t<1/2` 時為非實共軛對；且
`Im(-E_t'(iy)/E_t(iy))=-2y/(1-2t-y^2)`，碰撞後在上半平面嚴格變負。
Appendix C 把 WPT 的 analytic polynomial coefficients誤升級成 individual
roots analytic through collision；`+-sqrt(t-t*)` 已直接否證。能量 Lemma 7.1
的常數依賴 zero-speed bound，而速度在碰撞以 `|t-t*|^-1/2` 發散；Lemma 7.3
卻在整個開區間使用單一有限 `K` 做 Gronwall。故此稿沒有 RH 證明或可移植引理。
完整稽核見 `external_claim_audit_schatz.md`。Primary source:
https://kschatz.github.io/rh-xi-backward-parabolic-barrier/schatz_riemann_hypothesis_backward_parabolic_positivity_barriers_xi_flow.pdf

## ES76. Pólya-ensemble分類精確涵蓋 T7，但 rank-3 已排除其正密度

Förster--Kieburg--Kösters, *Polynomial Ensembles and Pólya Frequency
Functions* (J. Theor. Probab. 2019, arXiv:1710.08794) 定義 positive-radial
polynomial ensemble的 derivative-type density。其 operator
`D_nu=x^nu d_x x^(1-nu)d_x` 在 `x=u^2,nu=-1/2` 時滿足
`D_(-1/2)=u^-1 d_u^2 u/4`。因此取
`omega(x)=x^-1/2 Phi(sqrt(x))` 後，並保留 `dx=2u du` 的 Jacobian，該文
size-`r` density `Delta(x)det[D_(-1/2)^i omega(x_j)]dx` 正好是 T7
pointwise integrand（差正 row/column常數）。

這給 T7 一個標準 random-matrix分類，但不給新正性：T7.4 的 certified rank-3
負值證明 `omega` 連 size 3 的 Pólya ensemble都不是。該文 convolution semigroup
與 transform factorization的前提就是 joint density非負，故不能對 signed Xi weight
啟動。T9正是相應 derivative-principle的 integration-by-parts版本，仍只移動負區。
Primary source: https://arxiv.org/abs/1710.08794

## ES77. derivative principle辨認 inverse-Abel 缺口，不提供 T11正性

Kieburg--Zhang, *Derivative principles for invariant ensembles*
(arXiv:2007.15259) 對 `i o(2n+1)`，即 Bessel parameter `nu=-1/2`，證明由
pseudo-diagonal marginal經 inverse Abel/Hankel transform重建 squared-eigenvalue
density的唯一公式。這正是 T10 derivative determinant的 matrix-theoretic來源。

但 theorem的起點是已存在的 positive invariant random-matrix density；它不宣稱任意
positive pseudo-diagonal function的 inverse derivative reconstruction仍正。T7.4正好顯示
Xi weight的 reconstruction在 size 3為 signed。因此 ES77不能推出 matrix existence，
也不能推出 T11 determinant pushforward正；它只把所缺量詞定位為「inverse Abel後
某一 invariant的一維 marginal正」，需要另證。Primary source:
https://arxiv.org/abs/2007.15259

## ES78. Dimitrov 的 Lee--Yang Wronskians 是全階等價座標，不是升階定理

Dimitrov, *Lee--Yang measures and wave functions* (arXiv:1311.0596), 對 even
positive measure `mu` 的 orthogonal polynomials `p_n` 證明：其 Fourier transform
全實零等價於每個 `W(p_1,...,p_n;z)` 全純虛零；亦等價於所有
`W(p_2,...,p_n;ix)<0`。這確實是 uniform-in-degree statement。

但 Leclerc identity在本文中又 exact把第一族 Wronskians變回 Fourier transform的
Appell/Jensen polynomials；第二族則是相鄰 Appell polynomials的 Turán determinant。
所以 theorem沒有由 positive measure自動給 sign。直接 polarization已有
`A_n(z)^2-A_(n-1)(z)A_(n+1)(z)` 等於帶
`(t-s)^2(t-z)^(n-1)(s-z)^(n-1)` 的雙積分（差固定常數/符號），在 `z=ix` 時相位
隨 `n,t,s,x` 改變。正 measure或 log-concavity不消除此相位。

因此 ES78 是 Jensen/PF-infinity obligation的 orthogonal-polynomial座標，不填
degree-3斷層。可用的 Lee--Yang路仍只有顯式構造已知 ferromagnetic/Lee--Yang
measures `mu_N` 並證整體 weak convergence至 normalized `Phi(t)dt`；有限 moments、
finite Wronskians或任意 positive quadrature均不夠。Primary source:
https://arxiv.org/abs/1311.0596

## ES79. Connes--Consani：local modulus-one ratio不等於 inner；global Poisson不可省

Connes--Consani, *The Scaling Hamiltonian* (arXiv:1910.14368) 檢查 semilocal Weil
positivity的 Hardy-space捷徑。其 local-factor ratio在 critical boundary modulus為 1，
但 Archimedean ratio不屬所需半平面 `H^infinity`、實際上可無界；因此不能由
modulus-one直接視為 inner multiplier。文中並證 single Archimedean place對應的不等式
一般失敗（Riemann--Siegel phase非單調），而有限 primes的 principal-value normalization
不能任意各自設零，必須由 global Poisson formula共同固定。

這直接支持 G67的新稽核：boundary Riesz density與 local ground-state transform不足以
控制 actual analytic normal derivative；interior Blaschke項及 global normalization不能
從 boundary modulus回復。該文提出 semilocal support-by-support operator conjecture，並未
證完整 Weil positivity，故它提供的是正確 global接口與 local no-go，不是 RH證明。
Primary source: https://arxiv.org/abs/1910.14368

## ES80. Archimedean Sonin trace給 genuine positive storage，但 support避開 primes

Connes--Consani, *Weil positivity and Trace formula, the archimedean place*
(arXiv:2006.13771；2026-03-22 更新 TeX) 證：若
`supp(g) subset [2^-1/2,2^1/2]` 且所需 Fourier evaluations在 `0,-i/2` 歸零，則

```text
W_infinity(g*g*) >= Tr(vartheta(g) S vartheta(g)^*) >=0,
```

其中 `S` 是投影到 classical Sonin space。這是完全 operator-level 的正 storage；
它解釋 G67 所缺 kinetic不應是人工加入的 `|D|`，而是 phase-space compression trace。
但 `g*g*` 的 support在 `(1/2,2)`，恰好沒有任何 rational-prime term。正文只說把同一
工具推到 `S={infinity,2,...,p}` 是自然方向，沒有證 semilocal comparison。因此不可
把 ES80外推成 prime--gamma Weil positivity。原始 source存於
`external_inputs/connes_consani_2006_source`。Primary source:
https://arxiv.org/abs/2006.13771

## ES81. Semilocal Sonin/Jacobi spaces已構造，但 finite-S stability高度非 uniform

CCM, *Zeta zeros and prolate wave operators* (arXiv:2310.18423) 證每個 finite
`S` 的 semilocal Sonin space由 bounded invertible `theta_S` 與 Archimedean Sonin
space同構；*On q-series and the moment problem associated to local factors*
(arXiv:2403.01247) 證 cyclic measure `dmu_S=|E_S(t)|^2dt` 的 Hamburger problem
determinate，並對 `S={infinity,p}` 給 Jacobi/Lambert `q=1/p` 結構。

兩者與 G67 可 exact拼接：
`|L_p(1/2+it)|^2=P_(p^-1/2)(tlogp)/(1-p^-1)`。但在 dual coordinates，`theta_S`
的 norm ratio乘子是 `m_S=prod_p|1-p^-1/2e^(-itlogp)|^2`。prime logs的有理獨立給
`essinf m_S=prod(1-p^-1/2)^2`、`esssup m_S=prod(1+p^-1/2)^2`，故 full ambient
condition number為 `prod(1+p^-1/2)/(1-p^-1/2)->infinity`。所以「Sonin spaces穩定」
不是 uniform common norm theorem，positive moment measure也不是 Weil log-derivative
positivity。真正剩餘命題是每個 support cutoff上的 semilocal projection trace comparison。
Sources archived under `external_inputs/ccm_2310_source` and
`external_inputs/ccm_2403_source`. Primary sources:
https://arxiv.org/abs/2310.18423 , https://arxiv.org/abs/2403.01247

## ES82. Burnol p-adic scattering：positive time delay在 Weil form中被減去

Burnol, *Scattering on the p-adic field and a trace formula*
(arXiv:math/9901051) 對 non-Archimedean local field構造 causal scattering、interaction
projection與非負 time-delay operator。對 `Q_p` 的 unramified trivial channel，原文
Theorems VII--VIII exact化為

```text
T_p(t)=(log p)P_(p^-1/2)(tlogp)>=0,
H_p+T_p=(log p)I.
```

所以 local Weil multiplier `H_p=-(logp)(P-1)` 正是 G67 source，但 positive time delay
位於被減的一側。Theorem X 把 Weil local term寫成 `sTr Z_p(f)+(logp)f(1)`，其中 Tate
function張成一維 odd sector。這是 operator-level sign dictionary，不是 local positivity。
任何 global proof須以 Poisson/adelic complex消去或配對 odd sector，不能只 direct-sum各地
positive `T_p`。下載的 gzip TeX存於 `external_inputs/burnol_math_9901051.tar`。
Primary source: https://arxiv.org/abs/math/9901051

## ES83. 2026 arithmetic Jacobian給 cross-place tensor geometry，沒有 Hodge inequality

Connes--Consani, *On the Jacobian of the completed spectrum of the integers*
(arXiv:2602.15941) 將 Riemann adele sector辨認成 arithmetic Picard monoid：objects是
帶 Archimedean norm/root rigidification的 rank-1 torsion-free groups，adelic multiplication
對應 tensor product。稿件亦把 explicit formula解釋為 idele translations的 Lefschetz trace，
local terms來自各 place periodic orbit的 transverse trace，generic orbit負責 divergent cutoff。

這是 ES82 odd local sectors的 global幾何載體，但不是 positivity input。原始 TeX未定義
degree-zero intersection pairing，沒有 Hodge-index theorem，也沒有把 signed Lefschetz trace
升為 ordinary positive trace。semilocal公式仍是既有 cutoff trace。故新的 geometric target是
在 relative pair `(Picard monoid,generic orbit)` 上構造 exact Weil pairing並證 Hodge sign；
在此之前 ES83不推出 B9.2/RH。Source archived at
`external_inputs/connes_consani_2602_source`. Primary source:
https://arxiv.org/abs/2602.15941

## ES84. Quasi-inner提供all-finite-S kernel升階，但無正性或uniform Schatten class

Connes--Consani, *Quasi-inner functions and local factors*
(arXiv:2008.10974), proves for every finite set \(F\) of \(m\) primes that
\(u_F=\rho_\infty\prod_{p\in F}\rho_p\) is quasi-inner and
\((1-P)u_FP\) is an infinitesimal of order \(1/(2m)\). It also proves that
\(S(u_F)=\ker((1-P)u_F(1-P))\) is infinite dimensional and multiplication by
\(\prod_{p\in F'\setminus F}(1-p^{-z})\) injects \(S(u_F)\) into \(S(u_{F'})\).

This is a genuine all-finite-\(S\) algebraic mechanism, but not an isometric or
positive one. The characteristic-value estimate only guarantees
\(\mathcal S^q\) membership for \(q>2m\), so it supplies no fixed ideal for an
all-prime regularized determinant. Direct projection block algebra also shows
that upgrading quasi-innerness to full positive projection difference is exactly
innerness. Source archived at `external_inputs/connes_consani_2008_source`.
Primary source: https://arxiv.org/abs/2008.10974

## ES85. Burnol adelic causality is the desired orthogonality, but is RH-equivalent

Burnol, *On Fourier and Zeta(s)* (arXiv:math/0112254), Theorem 2.7, states that
the incoming/outgoing subspaces in the adelic Lax--Phillips system satisfy
\(\mathcal D_+\perp\mathcal D_-\) if and only if RH holds for all abelian
\(L\)-functions of the number field. Co-Poisson intertwining is an exact
functional-equation identity, but it does not establish that orthogonality.
Thus global Poisson/causal terminology supplies the correct all-place interface,
not the missing sign. A non-circular use must prove a new support-by-support
defect contraction independently. Primary source:
https://arxiv.org/abs/math/0112254

## ES86. Scaling Hamiltonian明確區分trace Weil sign與inner/operator sign

Connes--Consani, *The Scaling Hamiltonian* (arXiv:1910.14368), formula (3.2),
identifies the finite-place local sum on a convolution square with
\(\operatorname{Tr}(M_{|f|^2}U^*[P,U])\). Lemma 3.4 and Corollary 3.5 prove
that imposing a sign on the whole operator \(U^*[P,U]\) is equivalent to an
inner-function condition, and the local ratios fail it. Their Conjecture 4.1
therefore asks only for the support-by-support trace sign with the two pole
constraints. This validates B21--B22's distinction: the live obligation is a
weighted spectral average/mean delay, not operator positivity. Primary source:
https://arxiv.org/abs/1910.14368

## ES87. Rodgers否證universal weighted-Hilbert常數pi；異常是endpoint coupling

Brad Rodgers, *On the optimal constant in the Montgomery-Vaughan weighted
Hilbert inequality* (arXiv:2608.12315) 證 universal最佳常數嚴格大於 `pi`。
其解析反例取一個孤立點 `-1` 與 mesh趨零的半直線；極限是 half-line
Hilbert transform加 rank-one endpoint coupling，且顯式 eigenvalue
`alpha=pi*coth(pi alpha)>pi`。這排除只靠 local spacing在臨界常數 `pi`
吸收全部 cross terms。刪除孤立座標後只剩 norm `pi` 的 transform，但 Riemann
的 pole constraints並非刪除一個係數。Source archived at
`external_inputs/rodgers_2608_source`. Primary source:
https://arxiv.org/abs/2608.12315

## ES88. Burnol給pole-neutral Paley-Wiener空間的exact finite-rank geometry

Jean-Francois Burnol, *Paley-Wiener spaces with vanishing conditions and
Painleve VI transcendents* (arXiv:1008.0617) 對 `PW_x` 加有限個非實
vanishing points，顯式計算 reproducing kernel與 Darboux/Krein support flow。
本問題取 `+-i/2` 時，排除向量正是 time-side `exp(+-y/2)`，Gram matrix為
B23.2。這提供 exact constraint projection，但不處理 semilocal prime phase，
也不證 compressed Toeplitz sign。Primary source:
https://arxiv.org/abs/1008.0617

## ES89. Schoenberg classification排除B27 natural jump semigroup的PF-infinity

Schoenberg 的 bilateral theorem（1951；Grochenig, arXiv:2007.12889,
Theorem 1 有清楚重述）說 integrable PF-infinity function的 bilateral Laplace
transform必為某個 entire Laguerre--Polya function的 reciprocal。B30 對 B27
archimedean Levy density exact計算 reciprocal transform的 logarithm：

```text
-2 tau s^2 sum_(m>=0) 1/[(2m+1/2)((2m+1/2)^2-s^2)].
```

它在每個 `s=+-(2m+1/2)` 有 pole，exponential有 essential singularity；finite
prime-jump factor entire且 nowhere zero，不能消去。故此 semigroup不具
PF-infinity／全變差遞減結構。Thomas Simon, arXiv:1412.0132, 亦顯示 Levy
semigroup的 total positivity是需精細分類的特殊性質，不是 positivity-preserving
semigroup的一般推論。Primary sources:
https://arxiv.org/abs/2007.12889 , https://arxiv.org/abs/1412.0132

## ES90. BFI regularized theta lift是正確Green模板，不是現成K0正性定理

Bruinier--Funke--Imamoglu, *Regularized theta liftings and periods of modular
functions* (arXiv:1112.3444), proves the hyperbolic current equation used in
K0B43. For closed geodesics it expresses a theta bulk integral as a geodesic
period minus `(4 pi)^-1 int (Delta f) eta`; for split geodesics the truncated
identity retains two boundary integrals. Their explicit hard-term asymptotic
depends on arbitrary cusp constant terms and negative Fourier coefficients.
At spectral parameter `s=1`, Proposition `prop:specdef` further gives a
correction involving `B'_ell(1)`, so the regularized value can depend on the
chosen spectral deformation. These formulas supply the desired non-equivariant
Green/Rellich architecture, but no fixed sign for a general test function and,
as ES92 records, not yet an intertwining identity with the K0 Epstein theta.
Source archived at `external_inputs/bruinier_1112/BIFfinal.tex`. Primary source:
https://arxiv.org/abs/1112.3444

## ES91. Kudla--Millson Thom form不會在level 1免費產生Hodge norm

Branchereau, *The Kudla-Millson form via the Mathai-Quillen formalism*
(arXiv:2211.10341), identifies the Kudla--Millson differential form with a
canonical Thom form for the corresponding special cycle. This validates the
cycle/current interpretation behind K0B43. It does not supply positivity of a
linear cycle period. In the present full modular-group setting the compactified
curve `X(1)` has genus zero (`S_2(SL_2(Z))=0`), hence its real and L2 harmonic
first cohomology vanish. A closed geodesic current therefore has no nonzero
harmonic class whose Hodge norm could equal `Q_K0`; its information must occur
through an exact Green transgression, while noncompact cycles retain cusp terms.
Primary source: https://arxiv.org/abs/2211.10341

## ES92. BFI source的quadratic space與K0 lattice不同

The original BFI source defines `V` as the three-dimensional space of trace-zero
`2 by 2` matrices, with `Q(X)=-N det(X)` and the `SL_2` conjugation action; its
Gaussian is `exp(-pi (X,X)_z)`. This is the adjoint/`Sym^2` representation of
signature `(2,1)`. K0B39 instead uses the standard two-dimensional lattice and
the Epstein Gaussian `exp(-pi t Q_z(m,n))`. There is no `SL_2`-equivariant
linear map from `Std` to `Sym^2 Std`. The natural quadratic Veronese map lands
in the discriminant-zero cone and pulls a quadratic majorant back to degree four.
Consequently BFI's geodesic-current theorem is a rigorous model for the desired
boundary bookkeeping, but not an identity for the K0 theta stress without a new
intertwining theorem. Source archived at
`external_inputs/bruinier_1112/BIFfinal.tex`; primary source:
https://arxiv.org/abs/1112.3444

## ES93. Maass--Selberg只定截斷組合的zeros，不定renormalized time delay

Lagarias--Suzuki (arXiv:math/0412039) uses the Maass--Selberg relation to show
that a zero of the truncated Eisenstein constant term away from the real axis
must lie on the critical line: at such a zero the boundary side vanishes, while
the truncated Eisenstein norm cannot. The same source makes the relevant
constant term and its fixed half-shift in completed zeta explicit. This is not a
positive finite-part theorem for arbitrary spectral wave packets. After
polarization, a truncated norm contains a positive logarithmically divergent
baseline, the scattering derivative for
`phi(s)=zeta^*(2s-1)/zeta^*(2s)`, and boundary terms; positivity before
subtraction gives no sign after renormalization. Thus the correct Epstein-theta
version returns to the restricted scattering/time-delay problem rather than
solving it. Source archived at
`external_inputs/lagarias_suzuki_0412039_source/paper.tex`. Primary source:
https://arxiv.org/abs/math/0412039

## ES94. Arov-gauge Szego sum rule的正性建立在Schur spectral function上

Damanik--Eichinger--Yuditskii, *Szego's Theorem for Canonical Systems: the
Arov Gauge and a Sum Rule* (arXiv:1907.03267), Theorem 2.1, proves
`I(w)=int(tr A-2 sqrt(det A))` for a positive canonical Hamiltonian and a
holomorphic Schur spectral function `w`. This is a genuine coefficient-side
nonnegative integral. It cannot be applied directly to the modular scalar
scattering ratio: zeta zeros appear as its meromorphic poles, while its
physical-line boundary values are unimodular, making the displayed Schur
entropy infinite. Establishing the needed Schur quotient down to the Riemann
endpoint is the already-known canonical-system/Hermite--Biehler gap. A
nontrivial transmission completion would require new arithmetic data and an
additional identity with the Weil time-delay form. Primary sources:
https://arxiv.org/abs/1907.03267 and https://arxiv.org/abs/1903.05622

## ES95. Connes--Consani的compact theorem只是archimedean principal structure

Connes--Consani, arXiv:2006.13771, TeX label `thmqkey1` 在每個 fixed support interval上將
archimedean `D o Q` 寫成 `-2I+K_I`，其中 `K_I` 是 Hilbert--Schmidt；原文
因此得到 essential negativity，並明說延伸到
`{infinity,2,...,p}` 的 semilocal framework是「natural strategy」，論文本身只處理
support `(1/2,2)` 而不含質數。B34的直接 operator calculation解釋了為何
這不是 compact-perturbation corollary：prime-power evaluations在 additive time 上是
compressed translations，有 essential spectrum；經 `Q` 後還有 shifted derivative
energies。所以外部 theorem提供的是無質數 principal model，不是 B32.2 的
uniform semilocal sign。Primary source: https://arxiv.org/abs/2006.13771

## ES96. Suzuki給出無零點定義的L2 feature map，Gram恆等式即RH

Suzuki, *On the Hilbert space derived from the Weil distribution*
(arXiv:2301.00421), equations (1.5)--(1.6), 用 `zeta'/zeta`、`n<=e^t` 的顯式
prime sum、gamma derivative與 Hurwitz--Lerch tail 無條件定義
`mathfrak S_t in L2(R)`。Theorem 1.4 在 RH 下證它是 Riemann screw function的
screw line；Theorem 1.3/1.4 的 converse說明相應 Gram/isometry identity足以推出 RH。

論文的 unconditional zero expansion顯示實際缺口。`Theta=E#/E`,
`E=A+iA'`, `A(z)=xi(1/2-iz)`；feature vectors
`F_gamma=sqrt(m_gamma/pi)i(1+Theta)/(2(z-gamma))`只在 `Theta` inner時為
orthonormal model kernels。若零點非實，Weil form配對 `gamma` 與 `bar(gamma)`，
所需的 two-point matrix indefinite，不可能自動等於正 `L2` Gram。故這個
外部輸入提供真正 all-support square的明確候選，但不提供缺的
arithmetic coisometry。Source archived at
`external_inputs/suzuki_2301_source/screwzse_11.tex`. Primary sources:
https://arxiv.org/abs/2301.00421 and https://arxiv.org/abs/2606.09096

## ES97. Indefinite Hermite--Biehler theory將off-line zeros變成negative-square index

Langer--Woracek 所述的 indefinite Hermite--Biehler/Krein--Langer framework給
`K_E(w,z)=A(z)N_q(w,z)overline(A(w))` 及 `ind_- K_E=ind_- N_q`，其中
`E=A-iB`, `q=B/A`。對 Riemann `E=A+iA'` 有 `q=-A'/A`，所以上半平面
poles就是 `A=xi(1/2-iz)` 的 nonreal zeros。在 finite-index情形，
Krein--Langer factorization將負平方數與這些 poles的總重數對應；無限情形
則在有限子核上可見任意大的負指數。這提供 B35 所需 residue correction
的正確 indefinite 帳本，卻不提供 `index=0`。Primary source:
https://files.ele-math.com/articles/oam-07-29.pdf

## ES98. Krein--Langer factorization將負指數寫成finite Blaschke kernel

對 finite-index scalar generalized Schur function，Krein--Langer factorization給
`Theta=Theta_0/B`，其中 `Theta_0` 為 Schur，`B` 是 degree等於負平方數的
finite Blaschke product。直接代入 kernel即得
`K_Theta=(K_(Theta_0)-K_B)/(B(z)overline(B(w)))`。這證明 B35--B36
的 residue correction是一個明確 rank-`deg B` negative channel，不是 contour
regularization可丟的邊界項。一般理論不證 `B=1`；該結論需 Riemann-specific
arithmetic input。Primary general source同 ES97，並可參考 scalar Krein--Langer
factorization theorem。

## ES99. Degree-one Selberg rigidity辨識L-function，不提供zero-index sign

Kaczorowski--Perelli 與 Soundararajan 的 degree-one classification證明 Selberg class中
degree-one elements是 Riemann zeta 與 shifted primitive Dirichlet `L`-functions。這是很強的
single-channel rigidity，但結論本身不包含 GRH；在 conductor-one Riemann data上只是
重新辨識已知的 `zeta`。所以它無法從 B37 推出 `B=1`。

B38 的 shifted product `xi(s+a)xi(s-a)` 另證明：若不用 degree-one/Ramanujan
條件，那麼 positive logarithmic Euler coefficients、centered functional equation與 exact
explicit formula 容許無界 off-line index。Primary sources:
https://hdl.handle.net/11567/190933 and https://arxiv.org/abs/math/0306300

## ES100. Degree-one local Euler data是Hankel rank one，但分類不含GRH

對 `(1-alpha_p p^-s)^-1`，log Euler coefficients去掉 `1/k` 後是
`alpha_p^k`，故所有 adjacent `2 by 2` Hankel minors為零。B38的
`p^(ak)+p^(-ak)` minors則為 `(p^a-p^-a)^2>0`。然而 primitive Dirichlet
L-functions亦滿足 rank one、Ramanujan bound與單 gamma factor。
Kaczorowski--Perelli／Soundararajan 的 classification只辨識 degree-one Selberg
objects，不證其 critical-line zeros。未找到由 local Hankel rank控制 global
generalized-Nevanlinna negative squares的 theorem；若有，它至少推出 real
Dirichlet GRH。Primary sources: Kaczorowski--Perelli, Acta Math. 182 (1999),
207--241; https://arxiv.org/abs/math/0306300

## ES101. BSY/Kunik factorization給exact scalar Blaschke defect

Balazard--Saias--Yor證
`(2pi)^-1 int_R log|zeta(1/2+it)|/(1/4+t^2)dt`
等於 `sum_(Re rho>1/2)log|rho/(1-rho)|`；右側各項嚴格正，故 integral為零
iff RH。Kunik進一步寫 `((s-1)/s)zeta(s)=zeta_B(s)B(s)` 且
`B(1)=prod|(1-rho)/rho|=exp(-Omega_zeta)`。在 `s=1` 的 pole normalization
只讓 outer與 Blaschke factors相消，不能迫使 `B(1)=1`。這給真正 all-zero scalar
target，但缺從 prime/gamma side證 critical-line logarithmic integral `<=0`。
Gonek--Hughes--Keating 的 hybrid Euler--Hadamard formula同時保留 prime product與
zero product，沒有提供此 sign。Primary sources:
https://translations.thosgood.net/AIM-143-1999-284.html ;
https://arxiv.org/abs/0804.4829 ; https://arxiv.org/abs/math/0511182

## ES102. Burnol的quantitative Nyman theorem等同BSY Blaschke mass

Burnol證 Nyman--Beurling閉子空間 `N` 上常數 `1` 的 projection norm為
`prod_(Re rho>1/2)|1-1/rho|`。與 ES101 合併即得
`dist(1,N)^2=1-exp(-2 Omega_zeta)`。所以 critical-line log integral upper bound
與 uniform Nyman mollifier estimate完全等價，不能視為獨立機率。其 adelic
Lax--Phillips causality theorem則明說 causality iff 全部 abelian L-functions滿足 RH，
也不提供 missing sign。Primary sources: https://arxiv.org/abs/math/9910055 ;
https://arxiv.org/abs/math/0001013

## ES103. inner-quotient theory把local prime baseline辨識為infinite model channel

B42由 elementary Euler factor直接導出：critical local ratio是
`b_r(exp(iz logp))/exp(iz logp)`。standard model-space identity對 inner quotient
`N/D` 給 `K_(N/D)=(K_N-K_D)/(D overline D)`；`D=exp(iaz)` 的 model space
unitarily對應長度 `a` 的 time interval，為 infinite-dimensional。這與 Burnol local
time-delay identity及 B34 compressed translations一致：constant baseline不是 scalar
finite-rank debt，而是 singular-inner Paley--Wiener principal channel。一般 inner
factorization只提供此帳本，不提供跨 places的 coisometry。

## ES104. local all-pass filter的anti-causal leakage可exact計算

對 `u_p=b_r(w)/w`，Laurent expansion為
`-r w^-1+(1-r^2)sum_(k>=0)r^k w^k`。Paley--Wiener把 `K_w` 辨識為
`L2(0,logp)`；negative term平移到 `(-logp,0)`，positive terms落在互不相交的
後續 intervals。因此 Hankel leakage平方 exact為 `p^-1 I`，causal component平方
為 `(1-p^-1)I`。Bohr tensor product遂重現 Euler normalization
`prod(1-p^-1)`。一般 Hardy/model-space theory只給此 decomposition；跨質數
diagonal restriction的 mixed kernel仍須由 B43.5 直接計算。

## ES105. Tate cosine kernel提供completed semilocal leakage的顯式式

even Fourier transform在 log coordinate的 reflection-convolution kernel為
`2e^(a/2)cos(2pi e^a)`；Mellin cosine integral multiplier是
`pi^(1/2-s)Gamma(s/2)/Gamma((1-s)/2)`。與 ES104各 prime discrete measures
convolve後得到 B45.4 completed kernel。它不含 zeros，卻只重現 primal--dual
cancellation或 same-side unbounded distortion，沒有 B32 sign。Related local
spectral background: https://arxiv.org/abs/math/9904044 and
https://arxiv.org/abs/math/0602425

## ES106. Groskin source formula顯示pole channel exact飽和Nyquist type

Groskin arXiv:2607.02828v2 的 pole source在變數 `omega=1-y/L` 後，是 density
`2L cosh(L(1-omega)/2)` 的 `[0,1]` sine transform。endpoint density非零，故 source
type exact為 `2pi`；不是可套 strict Carlson uniqueness的 `<2pi` class。這是原始
source formula的直接 consequence，不依數值。由於 `sin^2(pi z)h(z)` 的 integer
Hermite data全零，任何 finite-codimension pole restriction也不移除此 sampling
nullspace。Primary source: https://arxiv.org/abs/2607.02828

## ES107. Reflection-positive dilation與Li v10 trace claim audit

Neeb--Olafsson 的 one-parameter theorem確實把 Hermitian contraction semigroup
`C_t` dilation成 covariance `C_|t-s|`。套 W10 box measure可得 W19.1 的完整
OS construction；但 dilation parameter是 Laplace shift，prime lengths則是 spectral
endpoints。W19.2 顯示 endpoint comb為正 bulk的 distributional derivative加 boundary，
所以 theorem不提供 Weil sign。Primary source: https://arxiv.org/abs/1312.6161

另稽核 X.-J. Li arXiv:0807.0090v10 的聲稱證明。其兩個關鍵零 trace步驟
(4.13)->(4.14) 與 (5.8)->(5.9) 都使用 `x->x/gamma`，其中
`x in C_S=J_S/O_S^*`、`gamma in O_S^*`。此 map在 quotient上是 identity，不能
改變 `Psi_S(x gamma v)`；若 x取 fundamental-domain代表，`x/gamma`一般離開該域，
也不是同域變數代換。additive character本身不下降到 quotient。故各 unit-orbit
summand未被證明相同，「同一數無窮次」的結論無效；Theorems 1.3--1.4未成立。
詳見 `li_semilocal_trace_audit.md`。Primary source:
https://arxiv.org/abs/0807.0090v10

更精確地，single-prime unit weights `1,-1/(p-1),0` 乘 critical Jacobian與
`1-p^-1` 後，exact給 B43 Laurent symbol
`-p^-1/2 w^-1+(1-p^-1)sum_(k>=0)p^(-k/2)w^k`。所以合法修正版不是新 route；
它回到 ES104--105 已明算但未定號的 completed Hankel leakage。

## ES108. Nakamura--Suzuki infinite divisibility導出half-Cauchy measure target

Suzuki 2206.03682 證 explicit prime--gamma `Psi(t)>=0` for all t iff RH；
Nakamura--Suzuki 2306.08317 又證 `exp(-Psi(t))` infinitely divisible iff RH。
依其 Herglotz representation，在無條件 zero-free line `Re s=1` 的 boundary measure
是 `sum P_(1-beta)(x+gamma)dx`。CS2新增 exact factorization：RH iff此 measure
屬 positive Poisson-semigroup range `P_(1/2)*M_+`。off-line zero給 strip內不可消
Poisson pole，故 converse不需數值或 finite moments。Primary sources:
https://arxiv.org/abs/2206.03682 and https://arxiv.org/abs/2306.08317

## ES109. Suzuki arithmetic formula的exact Chebyshev-error形

由 Suzuki 2206.03682 Eq. (1.1) 對 von Mangoldt sum作 Stieltjes分部積分，CS5.5
exact得到 `Psi` 為 `A(x)=x-psi(x)` 對正三角 kernel
`u^(-3/2)[1+(t-logu)/2]` 的積分，加完全顯式 gamma--Lerch項。這不是新外部
定理，而是原式的代數 consequence。classical zero-free-region PNT bound代入只給
Suzuki 同文已證的 `exp(t/2-c sqrt(t))` 上界；不可能靠 absolute estimate推出
`Psi>=0`。同時 Poisson semigroup Fourier multiplier顯示 half-Cauchy deconvolution
就是 zero counting spectrum／distributional `Psi''`，故沒有把 full Weil positivity
降成較弱的 moment problem。Primary source: https://arxiv.org/abs/2206.03682

## ES110. Freedman Weyl kernel：可用的derivative bridge與不可用的positivity ledger

Freedman arXiv:2606.29555 定義 coordinate kernel `K_omega`。WD1--WD3由此無條件
導出 `partial_omega D_omega=(4/pi) F K_omega F*`，所以 uniform Weyl PSD確足以
推出 RH。這是該輸入真正提供的新 analytic bridge。

然而 companion bundle的 positivity chain只複製 JSON `closed` flags。底層關鍵
`|kappa|<=1 => ||CKE||<=1` 對 non-isometric integration compression不成立，且
boundary/minimizer theorem以定義與 hard-coded True取代 existence、domain及 range
proof。有限 Galerkin representer script自己也只陳述 conditional continuum theorem。
故該論文/附件不構成 RH證明。完整逐檔稽核見
`freedman_weyl_positivity_audit.md`。Primary source:
https://arxiv.org/abs/2606.29555

## ES111. Csordas/Dimitrov--Xu定位correlation positivity的全階門檻

Csordas證 Jacobi--Riemann kernel `Phi` 嚴格 log-concave，並證 associated kernels
`K_n(t)=int Phi(s+t)Phi(s-t)s^(2n)ds` 仍為 admissible；但 `K_n` 對所有 n
positive definite iff Xi屬 Laguerre--Polya，也就是 RH。其 Open Problem 4.7甚至只問
實軸第一 Laguerre inequality。Dimitrov--Xu則把完整判據寫成 correlation translates
的 L1 density；同樣是 RH-equivalent closure，不是免費 positivity theorem。

WD5顯示 Freedman kernel的 boundary plane-wave form exact等於 complex Laguerre
expression，所以這兩篇文獻不是 G110 的缺失引理，而是證明該缺口已位於既知
all-degree門檻。Primary sources: https://arxiv.org/abs/1309.0055 and
https://arxiv.org/abs/1606.05011

## ES112. Suzuki RKHS chains不提供omega方向的無條件單調性

Suzuki 2012.11121 對固定 unimodular function構造 support-truncation參數 t 的 RKHS
chain；其 Selberg-class例明確說 `Theta_L^(omega,nu)` 在 `omega>=1/2` 無條件 inner，
而 `0<omega<1/2` 只有假設 GRH才 inner。這個 t-chain不是 WD7 的 vertical-shift
omega-chain，不能用來證 `partial_omega D_omega>=0`。

WD7則直接由 LP product證 omega-chain contractive，並與 WD3合成等價；所以既有
canonical-system theorem說明 RH成立時的結構，而非提供 RH所缺的無條件正性。
Primary source: https://arxiv.org/abs/2012.11121

## ES113. ES86 的 projection theorem 對 TPD Douglas 的精確套用（非新 theorem）

此處不是新增外部結果，而是把 ES86 接到 TPD2。Connes--Consani 1910.14368,
Lemma 3.4/Corollary 3.5 證：unitary multiplier相對
full Hardy half-space projection的 commutator sign，等價於其 Beurling innerness。該文
Section 4.1 用 Poisson 公式解釋臨界線 quotient為 modulus-one scattering multiplier，
但把由 semi-local operator 推到 Weil inequality明列 Conjecture 4.1。這正好驗證
TPD4：boundary unitarity不能替代 full-Hardy causality。FW6 的 special-range
版本不由此 iff直接涵蓋，但經 VK6仍等價 K0/RH positivity。

Suzuki 1204.1827 Proposition 1.2 則證 shifted-xi quotient對所有大於門檻的位移
inner iff對應右半平面 zero-free；小位移不是無條件引理。其 canonical-system
construction無條件範圍只到 `omega>1`，延伸至全部正 omega本身被說明為 RH criterion。
因此搜尋沒有找到不預設 RH/zero-free region而閉合 TPD2.3 的 theta-specific theorem。
Primary sources: https://arxiv.org/abs/1910.14368 and
https://arxiv.org/abs/1204.1827

## ES114. 最新 Laguerre 題名結果沒有證 Xi 的實軸 function inequality

聯網核對三類容易混淆的輸入。Wang--Yang, *Laguerre Inequalities for Riemann
Xi-Function* 的主變數是 Xi Taylor coefficient sequence `alpha(n)`，結論為每個
固定 order 在 sufficiently large n成立；不是
`(Xi'(x))^2-Xi(x)Xi''(x)>=0` 對所有 real x。Wagner 2108.01827 的 shifted
Laguerre--Polya class同樣只保證每個 inequality在足夠高 derivative/shift後成立。
2026 *On the Log-Concavity of the Riemann Xi Kernel* 則證 `Phi` 的 TP2/log-concavity，
不是 Fourier transform Xi 的 Laguerre inequality；而此 kernel shape已被 WD6
解析反例證明不能 uniform升到 Weyl/K0 positivity。

所以搜尋未取得 WD5 boundary diagonal所需的全實軸 sign，更沒有從該 scalar sign
升到 all-configuration matrix positivity的 theorem。Primary source for shifted class:
https://arxiv.org/abs/2108.01827 ; kernel preprint:
https://www.preprints.org/manuscript/202604.0159

## ES115. Polson 2026 Thorin/Wald輸入：新版是RH字典，舊版closure有硬矛盾

Polson arXiv:1804.10043v8 的一般 duality theorem把 imaginary zeros等價於 reciprocal
GGC／positive Thorin measure，確是 all-degree結構。但其 xi Theorems 23--25 不可
採信：式 (30)、(31)直接代數不等；且論文明寫
`U_star=delta_(3/4)+u_star dz`，所以 `H_star` 含 `Exp(3/4)`，必有
`E exp(H_star)=infinity`，與 Theorem 25 用該有限 moment作 parameter-1 exponential
tilt正面矛盾。

其 Theorem 21 甚至已有更早的 sign error：式 (24) 左側
`log(1+s/(alpha-1))-s/(alpha-1)` 為負，右側卻寫成正 integrand。正確 pole measure
是 `-e^x dx`；所以 (22) 不是 positive Levy measure，Lemma 16 的 Tonelli/GGC
結論不成立。修正後恰留下 prime atoms減 pole baseline的 renormalized signed transform。

其後 SSRN 6992163 改採 two-tier 說法：integer-square GGC clocks與 critical-line
characteristic function是無條件；folded dual Thorin measure正、LP、Weil、全 Hankel/
Jacobi positivity則是同一 RH open clause。SSRN 6992161 更明說 theta atoms的 HCM
不由 lattice sum保留，不能 atomwise組裝。這與 TPD/DU compression斷層一致，沒有
提供 G117 所缺的算術平方。詳見 `polson_thorin_audit.md`。Primary sources:
https://arxiv.org/abs/1804.10043v8 , https://ssrn.com/abstract=6992163 ,
https://ssrn.com/abstract=6992161 , https://arxiv.org/abs/1402.6163

## ES116. actual de Bruijn--Newman kernel不是PF5

Michałowski arXiv:2602.20313v2 對 `K(u)=Phi(|u|)` 展示 configuration
`M_ij=K(0.01+(i-j)0.05)` 的 certified負 5x5 Toeplitz determinant。v2 已撤回舊版
不健全的 derivative-threshold claims，但 direct witness不依賴該尾界。

本地另用 Arb 320-bit ball arithmetic、解析 theta tail `<1e-70`，並分別以 Arb matrix
determinant與 explicit 120-term Leibniz展開重驗，兩者都嚴格給負號。故 actual Phi
不可能 PF-infinity；低階 translation minors沒有 uniform升階。這是候選引理的嚴格
反例，不是 RH數值證據，也不涉及不同的 K0/Weyl form。詳見 `phi_pf5_audit.md`。
Primary source: https://arxiv.org/abs/2602.20313v2

## ES117. Williams--Ostrovsky Mellin law只閉合Thorin outer modulus

由 `E(W^s)=2(2/pi)^s xi(s)`，tilt後
`(2/pi)^(it)xi(a+it)/xi(a)` 是 characteristic function。因此修正後的 Polson
sine-square expression `log(xi(a)/|xi(a+it)|)` 確實非負。這是無條件 combined
prime--pole boundary sign，不需把 signed measure錯拆為正項。

但 boundary modulus不含 half-plane Blaschke inner factor；off-line zeros可存在而不改
此 sign。故它只生成 outer candidate，不能證 reciprocal GGC/Stieltjes analytic
identity。另 raw Gamma input除以 `x` 近0如 `dx/(2x^2)`，Polson Lemma 16 的 stated
integrability也未滿足。詳見 `thorin_outer_inner_bridge.md`。Primary sources:
https://arxiv.org/abs/1402.6163 and https://arxiv.org/abs/1804.10043v8

## ES118. Suzuki weighted Chebyshev sign 是 phase-sensitive arithmetic target

Suzuki arXiv:2411.07436v3 證 RH 等價於純算術函數
`g_0(t)=sum_(n<=e^t)Lambda(n)n^(-1/2)(t-log n)-4(e^(t/2)+e^(-t/2)-2)`
最終非正。其二階 distribution 是 prime atoms 減 `e^(t/2)+e^(-t/2)` pole density，
Laplace transform exact為
`-z^(-2)d_s log[s(s-1)zeta(s)]`，`s=z+1/2`。因此它保留 inner/phase，並提供
非逐 degree 的具體全域 target。

但論文沒有證該 sign；PNT absolute errors經半權積分後遠大於決定 sign 的 logarithmic
drift，且分開估 prime powers會失去 cancellation。故它是 G117 的有用 arithmetic
座標，不是已取得的正性機制。詳見 `arithmetic_phase_sign_audit.md`。
Primary source: https://arxiv.org/abs/2411.07436

## ES119. generalized Li propagation與model-space norm沒有補 sign

Freitas arXiv:math/0507368 的 `alpha_n(tau)` 全 n非負等價 zero-free half-plane；其
微分遞迴沒有把 `tau>=2` 的無條件正號向 `tau=1` 傳播的 maximum principle。
Suzuki arXiv:2301.05779 的 `G_n` 無條件屬 L2，但
`lambda_n=(2pi)^(-1)||G_n||^2` 全 n成立本身等價 RH；證 norm expansion先使用
Hermite--Biehler innerness與正交 model-space basis。無 RH 時的 `xi+xi'` poles／
cross terms正是 Pontryagin defect。兩者都提供 uniform字典，未提供 AP2.2 的 sign。
Primary sources: https://arxiv.org/abs/math/0507368 and
https://arxiv.org/abs/2301.05779

## ES120. Radziejewski theorem排除 off-line zero 的無限聚合抵消

Radziejewski 的 weakly-bounded Mellin oscillation theorem說：real function 的
Mellin transform若在 `rho=beta+i gamma`、`gamma!=0` 有指定型非零奇點，則扣除
real-axis main term後，error以 logarithmic frequency作正負振盪；保守量級為
`x^beta(log x)^(-M)`。對 `f(x)=g_0(log x)`，每個 zeta zero
`rho` 在 `q=rho-1/2` 給 residue `-m_rho/q^2 !=0` 的 simple pole；標準
`zeta'/zeta` partial fraction bound及 unit-height zero count驗證 weak-bounded條件。

所以即使 off-line real parts的 supremum不取到、無限 zeros逼近 edge，任一個
`a=Re q>0` 仍強迫 `g_0=Omega_+(e^(at)t^(-M))` 及同量級負 excursion。這關閉
G128的 aggregation caveat，但沒有給 Euler side的 eventual `g_0<=0`；它不是 RH
證明。詳見 AP9。Primary source:
https://doi.org/10.1093/qmath/has036

## ES121. 2026 Chebyshev integral claimed proof有空 floor-cell硬錯

Preprints.org 202605.1525v4 聲稱由 Chebyshev mean square證 RH；其核心 Lemma 9
要求每個 `J_m={k:floor(N/k)=m}` 的 normalized weight至少 `1/(2m)`。但
`N=10,m=6` 時 J_m為空，weight是0。一般 floor map只取 `O(sqrt N)` 個不同值，
不能從 U(N)控制全部 `m<=N` 的 `A(m)^2/m`。

因此 claimed core estimate、mean-square、absolute integral convergence與 RH結論
均不成立。這是 exact lemma counterexample，不是對數值 RH evidence的判斷；該稿
不能補 AP11.6。詳見 `preprints_chebyshev_integral_audit.md`。Source:
https://www.preprints.org/manuscript/202605.1525

## ES122. Johnston theorem把 AP11 的 `3/2` weight定位為 zero boundary

Johnston arXiv:2201.06184（Canadian Math. Bulletin；2026 version）無條件證
`t^-2` weighted prime/Chebyshev averages的負 bias；但若
`omega=sup Re rho>1/2`，其 oscillation theorem對每個 `c<1+omega` 產生正
excursions。AP11.6等價於控制
`int_1^x(psi(u)-u)u^-3/2du`，故 `c=3/2` 對任何 off-line omega都在 oscillatory
range。這確認 Mertens的 c=2結果不能平滑延伸到臨界 c=3/2；沒有補上所缺 sign。
詳見 AP12。Primary source: https://arxiv.org/abs/2201.06184

## ES123. Akatsuka 提供全複雜度乘法極值結構，不提供所需上界

Akatsuka arXiv:2411.19259 證 RH 等價於 renormalized critical partial Euler product
`E_1(X)` 有界，亦等價於 normalized `sigma_(1/2)` 在所有整數上有界。1/2-superior
highly composite numbers把任意多質因數及任意 exponent patterns統一壓成 partial
Euler product，故這是 all-complexity mechanism，不是 finite-degree certificate。

自行 partial-summation 得 `log E_1` 等於
`int(psi-u)u^-3/2(1/(2log u)+1/log^2 u)du` 加非負 theta concavity defect。
log damping使 critical-line zero項衰減、off-line項仍增長；但 local prime jumps兩號
（Arb嚴格證 p=5 負、p=1327 正），沒有 monotonicity。外部 theorem提供全域座標與
failure detector，未提供 boundedness producer。詳見 `akatsuka_multiplicative_audit.md`。
Primary source: https://arxiv.org/abs/2411.19259

## ES124. PNT-error mean square不能用 absolute blocks補 AP14

Brent--Platt--Trudgian arXiv:2008.06140 證 RH下 dyadic mean square
`int_X^(2X)(psi-x)^2dx<<X^2`；RH false時 normalized mean square unbounded。對 AP14
的 q kernel，Cauchy--Schwarz即使使用前述最佳尺度，每 block也只得 `O(1/logX)`，
跨 dyadic scales不可和。故 ordinary positive L2/Selberg square會丟掉 Q收斂所需的
cross-scale phase；不能補 G135。Primary source: https://arxiv.org/abs/2008.06140

## ES125. Banks--Sinha 將 fractional Selberg family定位為已知 RH detectors 的凸組合

Banks--Sinha arXiv:2209.11768 對 `Lambda^k` convolution與 generalized
`Lambda_k=mu*log^k` 證明 uniform twisted square-root-exponent estimates及其 RH
converse。對 k=2，SFS family exact滿足

`a_alpha=(1-alpha)(Lambda*Lambda)+alpha Lambda_2`,

其中 `Lambda_2=Lambda*Lambda+Lambda log`。故 RH下兩個外部 theorem線性合成
SFS8.2；反向因 zero multiplicity `m` 的 pole係數 `m(m-alpha)` 在 `0<alpha<1`
不消失。此輸入嚴格確認新 family 是 robust all-multiplicity RH criterion，不是
unconditional positivity producer。Primary source: https://arxiv.org/abs/2209.11768

## ES126. infinite-divisibility continuation進 critical strip 已 exact等價 RH

Nakamura arXiv:1504.03438 證 completed xi ratio雖對任意 real sigma都是
characteristic function，但其在每個 1/2<sigma<1 的相關
pretended-infinite-divisibility representation成立 iff RH。Nakamura--Suzuki
arXiv:2306.08317 又構造 exp(g_zeta(t))，其為 infinitely divisible
characteristic function iff RH；RH下 Levy measure由 real zero frequencies的
m_gamma/gamma^2 positive atoms組成。故 SFS9 的 positivity-preserving
critical-strip continuation不是一般 probability theorem，而是完整 RH義務。

## ES127. 最新 PNT error仍不能支撐 SC quantile 的 absolute-envelope變分

Bellotti arXiv:2508.02041, Theorem 1.5 由新的 near-one-line zero-density estimate
得到 optimal Vinogradov--Korobov型
`|psi(x)-x|/x << exp(-omega(x))`，其中
`omega(x)=d(log x)^(3/5)(log log x)^(-1/5)`。Johnston arXiv:2411.13791,
Corollary 2.3 的前一版本為同指數尺度乘 logarithmic factor。

代入 AP21 的 weighted slope後為
`E(t) asymp exp(t/2-dt^(3/5)(log t)^(-1/5))` 的 absolute allowance，仍增長且
不可積。因此這些最佳外部輸入能嚴格證明 envelope-only route失敗，卻不提供所需
signed primitive。Primary sources: https://arxiv.org/abs/2508.02041 and
https://arxiv.org/abs/2411.13791

## ES128. Grochenig--Schoenberg reciprocal-Xi 全正性與既有 Thorin target相同

Grochenig arXiv:2007.12889, Theorems 1/4 證 RH等價於
`1/xi(1/2+t)` 的反 Fourier核為 Polya-frequency infinity。這是合法 all-degree
theorem；但 source亦明說連最低層 positive-definiteness都未由實軸資料證得。

本地 SRX audit進一步指出：`1/zeta(s)=sum mu(n)n^-s` 只覆蓋 real `s>1` 的尾部；
functional equation給另一尾，中央 compact frequency段留下 arbitrary additive
correction，PF-infinity不對此加法封閉。Schoenberg product轉成 `u=t^2` 後就是
positive Stieltjes logarithmic derivative，與 A20/Polson--Thorin同一義務，故不計為
新路徑。Primary source: https://arxiv.org/abs/2007.12889

## ES129. Arias ordinary-Laguerre energy提供 all-degree Hilbert座標

Arias de Reyna 證 `Pi(e^t)-Li(e^t)` 的 ordinary Laguerre coefficients
`a_n` 滿足 RH iff `(a_n) in ell^2`，且 Parseval energy exact等於
`int_1^infinity|Pi(x)-Li(x)|^2x^-2dx`。D10.4 又直接給 `E_n=n a_n`。
這是外部取得的真正 all-degree positive structure，不是 finite certificate；但
其 L2 finite 已 exact等價 RH。Karp 的 `sum |a_n|^2theta^n` theorem
（theta>1）要求 entire-function restriction，與 prime-power jump function不相容。
詳見 `li_laguerre_l2_external_audit.md`；可續的新責任只剩 LS2 的單側
density/block 弱型估計。

## ES130. Suman 2026 Li 漸近 claim 經稽核不可用

原稿宣稱由顯式 PNT error無條件推出 Voros 的 Li 漸近。精確核對顯示 (6)--(7)
混淆 `Y(x)=L_n(log x)` 的 x導數與 `L_n(t)` 的 t導數，使 (53) 的 cancellation
錯誤；`L_1(t)=1-t` 即為符號層級反例。後段又把 factorially divergent Bernoulli
漸近級數當作收斂無窮和並交換極限。故不採納其 RH結論或 `O(n^(3/4))` remainder。
Primary source:
https://www.researchgate.net/publication/400430678_On_the_Asymptotics_of_Li_coefficients_and_Proof_of_the_Riemann_Hypothesis

## ES131. Suzuki 給無條件 Li-indexed L2 Gram family，但 norm identity iff RH

arXiv:2301.05779（頁面標示 2026-08-11 版本）無條件構造 `G_n in L2(R)`，並證
`RH iff lambda_n=||G_n||^2/(2pi)` 對每個 n。故全部 `G_m,G_n` 的 Gram matrix
是 uniform all-degree PSD；斷層則是把 diagonal norm識別成 Li coefficient。
該識別使用 `Theta=(xi-xi')/(xi+xi')` 的 model-space orthogonal basis，而
`Theta` inner / `E=xi+xi'` Hermite--Biehler亦 exact iff RH。
Primary source: https://arxiv.org/abs/2301.05779

## ES132. Matsumoto--Suzuki 把 signed correlation移到 Goldbach M-function

arXiv:2409.00888 / JNT 280 (2026) 給 H與 H_1 的無條件 weighted-prime formulas，
並證 boundedness或 compact-support M-function law會推出 RH。`Lambda*Lambda` 的
Goldbach係數非負，提供二尺度算術結構；但 sharp centered asymptotic的 remainder
bounds在 source中仍以 RH為前提，非負性不能穿過主項扣除。故它是 AL5 cross-scale
候選介面，尚非 positivity producer。
Primary source: https://arxiv.org/abs/2409.00888

## ES133. Han 的 smooth k-Goldbach converse 排除 convolution-degree 捷徑

Han arXiv:2505.23795（頁面日期 2026-08-11）對 smooth weighted PNT error與
smooth weighted k-Goldbach asymptotic建立 zero-free-region雙向 implication。
核心 `F_k=(sum Lambda(n)e^(-n/x))^k` 顯示 fixed k升階沒有新 cancellation；
centered二卷積的係數 `(Lambda-1)*(Lambda-1)` 亦不再非負。這驗證 Goldbach
可作 cross-scale detector，但 ordinary additive convolution不是 SMG5的正能量 producer。
Primary source: https://arxiv.org/abs/2505.23795

## ES134. analytic-space zero-free framework確認臨界 Hardy closure是主缺口

Ghosh--Kremnizer--Noor--Santos arXiv:2206.00434 將 zero-free half-planes歸約為
analytic-space closure與 bounded functional。`p<1` 的 cross-space shift inverse
可無條件完成，但只給 `Re s>1`；對 `1<=p<=2`，functional bounded而 closure未解，
`p=2` 正是 RH half-plane。故此框架支持 SMG8的定位，沒有提供 H2 contraction。
Primary source: https://arxiv.org/abs/2206.00434

## ES141. Nyman triangular positivity仍是 conjecture，且不足以推出 RH

Bellemare--Langlois--Ransford arXiv:2011.02847 conjecture Nyman functions的全部
Cholesky entries／bordered Gram determinants正；作者明說未知其與 RH的 implication。
NC2另給抽象 exact反例：全正 Cholesky與正 RHS可和非零 orthogonal residual共存。
因此即使 conjecture獲證，仍需獨立 quantitative closure theorem。
Primary source: https://arxiv.org/abs/2011.02847

## ES135. Connes--Consani 的 local operator sign失敗，global support仍為 conjecture

arXiv:1910.14368 Lemma 3.4/Corollary 3.5 證 quantized logarithmic derivative的 sign
等價 Hardy subspace invariance／innerness；文中隨即驗出 finite-prime與 archimedean
local ratios皆非 bounded inner。以 global Poisson normalization和 compact support
恢復 Weil inequality被明列為 Conjecture 4.1。故其框架不能當成已知 contraction，
但精確指出 L15必須是 global prime--gamma identity，不能乘接 local PSD factors。
Primary source: https://arxiv.org/abs/1910.14368

## ES136. strong Nyman--Beurling提供 closure等價，不提供臨界 closure證明

Baez-Duarte arXiv:math/0505453 與 math/0011254 將 RH寫成 dilation/co-Poisson的
critical `L2` closure，並強調自然近似可在 pointwise、L1收斂而於 L2失敗。
所以 L15的 Green平滑不能僅由形式 Poisson identity或弱收斂升成所需 norm bound。
Primary sources: https://arxiv.org/abs/math/0505453 ; https://arxiv.org/abs/math/0011254

## ES137. Selberg symmetry與 short-interval mean square不控制 fixed-origin L14

Helfgott arXiv:1501.05438 記錄 Selberg/Vaughan Dirichlet-convolution identities；
Coppola arXiv:1009.6121 給 primes symmetry/Selberg integral的 nontrivial averaged
bound與 almost-all short-interval PNT。前者在 Mellin側形成 analytic powers而非
modulus squares，後者平均 interval origin而容許 exceptional origins。兩者皆沒有
把 fixed-origin nested discrepancy轉成 `O_epsilon(Y^epsilon)` 的 maximal theorem。
Primary sources: https://arxiv.org/abs/1501.05438 ; https://arxiv.org/abs/1009.6121

## ES138. optimized trigonometric-polynomial zero regions仍保留 `1/log t` 尺度

Mossinghoff--Trudgian arXiv:1410.3926 與 Nielsen arXiv:2210.14130 以更高階
nonnegative trigonometric polynomials改善零區常數，但結論仍為
`sigma>=1-c/log|t|`。Leong--Mossinghoff arXiv:2404.05928亦證經典 polynomial在其
另一 zeta lower-bound用途的 optimality。PG8從 explicit formula說明尺度障礙：
可隔離 target zero的 nonnegative coefficient mass必付不可消的 gamma `log t` cost。
Primary sources: https://arxiv.org/abs/1410.3926 ; https://arxiv.org/abs/2210.14130 ;
https://arxiv.org/abs/2404.05928

## ES139. averaged Chowla與 critical reciprocal-zeta norm不在同一量詞層級

Matomaki--Radziwill--Tao arXiv:1503.05121 證 fixed-order Liouville correlations在
shift tuple上的 averaged cancellation；它不控制 fixed Mellin line的
`int W(t)|1/zeta(sigma+it)|^2dt`。Ng arXiv:math/0310381 的 Mertens distribution／
weak Mertens結果在 RH外還使用 Gonek--Hejhal negative moments，反映 reciprocal-zeta
norm的額外敏感性。故 additive averaged Mobius randomness不能作 PG10 continuation。
Primary sources: https://arxiv.org/abs/1503.05121 ; https://arxiv.org/abs/math/0310381

## ES140. `H^q, q<1` closure的 evaluation boundary只到 `Re s=1`

arXiv:2206.00434 Lemma 4.4 的 exact cross-space條件是 `q<p/(1+p)`；Theorem 4.5
遂證 `H^q` closure，但 Proposition 4.1 的 evaluation只在 `Re s>1/q` bounded。
令 `q->1-` 只逼近 `Re s=1`，且所需 source exponent `p->infinity`。此 theorem沒有
任何可延至 `1<=q<=2` 的 uniform constant，不能作 critical reciprocal-zeta bridge。
Primary source: https://arxiv.org/abs/2206.00434

## ES142. Ehm的 Nyman Gram分解把未閉合項定位為 Möbius inversion tail

Werner Ehm, arXiv:2405.06349，對 `q=1,2` 導出 explicit Gram kernels、Müntz
series與 reciprocity，並把 Möbius型 quadratic form拆成 Landau/Mertens factors及
truncated inversion error。`q=2` closure仍與 RH等價；Section 8.1明確把 inversion
error稱為 major challenge並 set aside。文中的高度 correlation圖只屬探索性數值，
不能補該 uniform tail estimate。

Primary source: https://arxiv.org/abs/2405.06349

## ES143. Maier--Rassias只在 `n>=k^2` 證 cotangent--Möbius power saving

arXiv:1806.05070 Theorem 2.1 證存在 `z0>0`，使對 `D>=2`

```text
sum_(k^D<=n<2k^D) mu(n) g(n/k) <<_epsilon k^(D-z0+epsilon).
```

這是與 Nyman/Vasyunin相關的真正 fixed-power cancellation；但 kernel `g` 非 Ehm
`S_q` 本身，且尺度條件排除 `n/k=Theta(1)`。未找到同尺度版本。故可列為 remote-tail
外部輸入，不能宣稱控制 NC5/G172 的 moving boundary。

Primary source: https://arxiv.org/abs/1806.05070

## ES144. MRT averaged Chowla 的量詞低於 Ehm same-scale 門檻

Matomaki--Radziwill--Tao arXiv:1503.05121 Theorem 1.1 對 Möbius亦給
`sum_(h<=H)|sum_(n<=X)mu(n)mu(n+h)|=o(HX)`。在 `H=X=N` 僅是 `o(N^2)`，
而 NS1需要完整 weighted signed double sum為 `o(N log N)`。甚至逐 shift
`O(sqrt N)` 經 triangle inequality仍為 `N^(3/2)`；此 theorem不能補 moving
boundary，因它恰好丟棄了跨 shift 的符號。

Primary source: https://arxiv.org/abs/1503.05121

## ES145. Guth--Maynard large values 尚未到 Möbius square-root regime

arXiv:2405.20552v2 改善 length `N` Dirichlet polynomial在 value約 `N^(3/4)` 的
大值估計，並導出 `N(sigma,T)<=T^(30(1-sigma)/13+o(1))` 與
`x^(17/30+o(1))` short-prime interval。NS2所需則是 adjacent Möbius polynomials
的 near-`N^(1/2)` signed product，且要排除所有 exceptional off-line poles；generic
large-value與 zero-density結論不給這個 bound。

Primary source: https://arxiv.org/abs/2405.20552

## ES146. Ramaré--Zuniga identity factory給 `sigma>=1` positivity，非 critical bound

arXiv:2312.05138v3 Theorem 1.2 證
`0<=sum_(n<=X)mu(n)n^-sigma log^k(X/n)`（`sigma>=1`）及 explicit upper bound；
Theorems 1.4--1.5 的 complex estimates仍含 `int_1^X|m_q(t)|dt`、`1/zeta(s)`，並排除
zeta zeros。作者也明說 `sum mu(n)/n=O(X^-1/2+epsilon)`等價 RH。因此此正性是有用的
scale-uniform資料，但不能控制 Ehm的 m-dependent same-scale kernel。

Primary source: https://arxiv.org/abs/2312.05138

## ES147. Verjovsky local moments給明確 uniform升階機制

arXiv:2607.25002 Theorem 1.3 證 critical arc `|t|<=c/N` 上 normalized Möbius
polynomial的 arbitrarily high finite subpolynomial moments iff RH。Corollary 3.3顯示
fixed `q` 一次只給 Mertens exponent `1/2+1/[2(q+1)]`，所以 source採 `q->infinity`。
ES148再證 fixed-q feedback可迭代，故此處的 degree limitation不是最終強度。source明說
其結果是 reformulation，不是 RH proof。

Primary source: https://arxiv.org/abs/2607.25002

## ES148. fixed-moment bootstrap嚴格強化 Verjovsky 的量詞

`external_claim_audit_verjovsky.md` 證 source Corollary 3.3所得第一次 Mertens gain可回饋
到 critical-rescaled polynomial的 derivative bound，形成
`delta->delta/(q+1)`。故 source主 theorem仍正確但非 sharp；Remark 3.4所稱 fixed `q`
只能到大於 `1/2` 的說法忽略 iteration。任一 fixed `q>=1` subpolynomial local moment
已 iff RH，尤其 `q=2` 即足夠。網路搜尋未找到先前相同 bootstrap；此處只宣稱已給出的
elementary proof，不宣稱文獻優先權。

Primary source audited: https://arxiv.org/abs/2607.25002

## ES149. discrete prolate文獻提供 sinc matrix的正譜與超指數 tail

Boulsane--Bourguiba--Karoui arXiv:1905.08354明列 Toeplitz matrix
`sin(2pi W(n-m))/(pi(n-m))`、eigenvalues in `(0,1)`，並給 non-asymptotic decay；
Bonami--Karoui arXiv:1509.02646描述 fixed bandwidth eigenvalues的超指數 decay。
這足以嚴格截去 LQ3 的 high spectral tail，但 papers不含 Möbius projection估計，
不能補 low-mode arithmetic gap。

Primary sources: https://arxiv.org/abs/1905.08354 ; https://arxiv.org/abs/1509.02646

## ES150. discrete Laplace transform的新 criterion仍以 reciprocal zeta為核心

Liflandsky arXiv:2607.09797v3證
`Phi(e^-x)=sum mu(n)e^(-nx)` 的 Mellin transform為 `Gamma(s)/zeta(s)`；
`Phi(e^-x)=O(x^-1/2)` 無條件蘊含 RH，converse另加 simple-zero及 summability假設。
explicit formula的 nontrivial-zero項為 `Gamma(rho)x^-rho/zeta'(rho)`。這支持 LQ5
對 power modes的判讀，但 theorem是 criterion/explicit formula，不是無條件臨界 bound。

Primary source: https://arxiv.org/abs/2607.09797v3

## ES151. Báez-Duarte的 general strong kernel theorem涵蓋 compact sinc

arXiv:math/0505453 Theorems 1.2--1.3及 Müntz formula證：對 compact good/step kernel，
若 Mellin transform在 critical strip無零，則 `f in closure span{(Pf)(kx)}` iff RH；
`(Pf)^hat=zeta fhat`。compact sinc的 Mellin transform由 L30在更大半平面無零，故完全
落在此框架。source提供的是 criterion，不是 unconditional closure。

Primary source: https://arxiv.org/abs/math/0505453

## ES152. Möbius convolution與 weak Mertens文獻沒有補 sampling上界

Báez-Duarte arXiv:math/0504402把 Riesz/Hardy--Littlewood growth統一成 Möbius
convolution criteria；仍是 RH等價。Inoue arXiv:1705.00853研究
`int(M(u)/u)^2du` 時明確假設 weak Mertens hypothesis；不能作 SM4的無條件 input。

Primary sources: https://arxiv.org/abs/math/0504402 ; https://arxiv.org/abs/1705.00853

## ES153. Burnol量化 critical zeros造成的 Nyman distance下界

arXiv:math/0103058 Theorem 1.3證（RH失敗時 distance不趨零；RH情形）
`liminf D(lambda)sqrt(log(1/lambda)) >= [sum m_rho^2/|rho|^2]^(1/2)`。
這排除快速 uniform inverse，但只是 lower bound。Báez-Duarte arXiv:math/0205003
的 explicit Möbius approximant decay明確假設 RH，不能作無條件 upper bound。

Primary sources: https://arxiv.org/abs/math/0103058 ; https://arxiv.org/abs/math/0205003

## ES154. recent ladder Gram decay沒有證 target closure

arXiv:2510.18132證 Gaussian Mellin smoothing後 Beurling--Nyman ladder Gram entries的
arbitrary polynomial off-diagonal decay與 block-compressibility；source沒有證 target
distance趨零或 RH。這是 matrix structure input，不是 reciprocal-zeta upper bound。

Primary source: https://arxiv.org/abs/2510.18132

## ES155. Laguerre相鄰成熟理論補 basis，不補 centered prime discrepancy

Lubinsky--Mate--Nevai (SIAM J. Math. Anal. 18 (1987)) 與 Lubinsky 的 quadrature/MZ
理論對 exponential weights給 uniform polynomial sampling inequalities，但需要自然
尺度上 suitably spaced nodes與positive weights；prime logs/weights不符合直接代入
條件。Temme及 Frenzen--Wong的全實軸 uniform Laguerre expansions、Vanlessen的
Riemann--Hilbert Plancherel--Rotach theorem則完整補 kernel localization，沒有
arithmetic signed-measure bound。Plewa的 sharp all-degree Hardy inequality要求
`g e^-t/2` 屬 H1/L1；此假設不能由 PNT envelope驗證，且 L1已會給全部 `a_n`
bounded，屬 RH級義務。詳見 `laguerre_block_uniform_audit.md`。

Primary sources: https://doi.org/10.1137/0518041 ;
https://acta.hu/download.phtml?id=2328 ; https://ir.cwi.nl/pub/2379/2379D.pdf ;
https://arxiv.org/abs/math/0504604 ; https://arxiv.org/abs/1810.08138

## ES156. quantitative exponential controllability theorem不涵蓋 log-integer超密 spectrum

Cannarsa--Martinez--Vancostenoble 的 precise biorthogonal estimates依賴 uniform bad gap
加 asymptotic good gap；Gonzalez-Burgos--Ouaili 2024雖處理無 global gap，仍要求
power-law counting function及 uniformly bounded condensation group。`lambda_k=log k`
有 gap `~1/k`、counting `N(R)~e^R`，故兩者無法代入 SC8 的 kappa upper bound。
Trefethen 2023在另一 Müntz basis證 approximation coefficients可對精度 exponential
爆炸，只能警示 qualitative density的 condition cost，不能作本系統 lower bound。

Primary sources: https://doi.org/10.3934/dcdss.2020082 ;
https://arxiv.org/abs/2401.17128 ; https://doi.org/10.1007/s44007-022-00039-6

## ES157. zeta 二次矩改善 tail；長 mollifier lower bound不補 local cost

Atkinson 的經典 critical-line second moment特別蘊含
`int_0^X|zeta(1/2+it)|^2dt<<XlogX`。配 `W=O(1/t)`、`|C|<=K`，SC10得到
`int_(|t|>T)|W|^2|1+zeta C|^2 << T^-1+K^2logT/T`，把 controlled-projector
允許成長提升到近 `T^(1/2)`；這是可直接代入的新定理。

Radziwill arXiv:1207.6583 Theorem 1 對 arbitrary-length（但有 normalization及
polynomial coefficient條件）mollifier給 high-window residual lower `c/theta`。
它乘 sinc weight後只成 `c/(Ttheta)`，且 K不控制 support length，故不能給 kappa upper
bound或 K-only lower bound。標準 mollifier asymptotics同樣不控制 fixed low window。

Primary sources: https://doi.org/10.1112/jlms/s1-23.2.128 ;
https://arxiv.org/abs/1207.6583

## ES158. Andersson bounded-coefficient density未提供有效 support rate

arXiv:1207.4624 Theorem 1/5以 Pechersky rearrangement及 Paley--Wiener
quasianalyticity證 fixed interval上的 bounded-coefficient Dirichlet polynomial density。
取 `Phi(n)=n^(1/loglog n)` 並轉回 critical normalization，可令
`|c_n|<=n^(-1/2+1/loglog n)`，從而 K截至 N僅 `N^o(1)`；tail correction亦 bounded。
但 theorem/證明沒有給達到指定 window T與 error delta所需的 N上界，所以不能驗證
SC10.5。它提供 support-complexity介面，不是 window-uniform projector。

Primary source: https://arxiv.org/abs/1207.4624

## ES159. twisted moments/GCD bounds不能提供 support-free ell2 tail

Bettin--Chandee--Radziwill arXiv:1411.7764 對 arbitrary Dirichlet polynomial的 zeta
twisted mean square仍只把 length推至 `T^(1/2+0.01515...)`；特殊形狀才到 `T^(3/4)`。
Aistleitner--Berkes--Seip及後續 GCD spectral norm結果給長平均/dilated periodic systems的
quadratic bounds，但沒有涵蓋任意大 support在固定 t-window形成的 log-frequency clusters。
SC13給 elementary反例：ell2 norm趨零而 shell energy固定。因此這批 theorem不能移除
SC12的 support complexity；只有附 length/spacing或 cluster-mass控制的版本可代入。

Primary sources: https://arxiv.org/abs/1411.7764 ;
https://arxiv.org/abs/1210.0741 ; https://arxiv.org/abs/1407.5403

## ES160. Ingham fourth moment可直接產生 cluster-aware tail

Ingham的 classical theorem給 `int_U^(2U)|zeta(1/2+it)|^4dt<<Ulog^4U`。配自行證明的
Gaussian short-window large sieve
`int_U^(2U)|C|^2<<U B_U^2` 及 `|C|<=K`，SC15得到
`tail<<T^-1+K B_T log^2T/T`。這是成熟相鄰定理的直接可代入成果；它不要求 RH、
support length或 reciprocal regularity。未解部分只剩 local construction是否控制
`K B_T`。

Primary source: https://doi.org/10.1112/plms/s2-27.1.273

## ES161. quantitative Müntz literature未給 polynomial-in-window controllability

依 SC16的新寬鬆驗收式重查 quantitative Müntz coefficient estimates。Trefethen 2023只對
even-power Müntz basis證 coefficient隨 `1/error` exponential lower growth；Erdelyi型
Markov/Remez inequality與 Müntz-space geometry書籍控制 derivatives、embeddings或固定
finite-dimensional bases，沒有對 `lambda_n=log n`、乘法 target `1+zeta C` 給
`K<=T^A` 的 upper construction。故沒有可直接代入 L44 的成熟 theorem；也不能把另一
basis的 exponential lower bound移植成本系統 no-go。

Primary source directly audited: https://doi.org/10.1007/s44007-022-00039-6

## ES162. Andersson primary-source stopping-rate audit

已下載並逐行核對 arXiv:1207.4624 的 TeX source。Theorem 3以 qualitative
Pechersky rearrangement theorem收尾：只需對每個 fixed nonzero `f` 證
`sum A_n|fhat(lambda_n)|=infinity`。proof沒有 finite-prefix modulus；Hadamard product、
zero neighborhoods與 logarithmic integral的常數均依該 fixed f。任意 finite prefix又在
`L2(0,H)` 有共同正交 unit direction，故不能把 pointwise divergence交換成 uniform
stopping rate。

作者在該文所指的 follow-up arXiv:1207.5337已一併核對；它 explicitize的是 Dirichlet
series non-vanishing lower bounds，並未提供 bounded-coefficient approximation的
`N(T,delta)` 或 coefficient-cost upper。故 ES158 的「source沒有 rate」現已提升為
proof-level量詞裁決；見 `andersson_pechersky_rate_audit.md`。

Primary sources: https://arxiv.org/abs/1207.4624 ;
https://arxiv.org/abs/1207.5337

## ES163. W12.4／LM11 named-gap adjacent literature audit

只針對已命名的 sharp centered prime--arch inequality檢索一手來源，未搜尋 RH proof claims。

1. Morán Ledezma, arXiv:2311.08519，把 Weil explicit sums寫成 Bohr compactification上的
   covariances、expectations與 spectral-integral limits；文中相應 covariance upper仍是 RH
   equivalent reformulation，沒有證 sharp sign。L60又說明 normalized mean topology沒有
   LM11 coercivity。
2. Connes--Consani, arXiv:2006.13771，完整處理 simplest single archimedean place的 Sonin/
   prolate positivity；摘要只說 ingredients可延至 general semilocal case，而該 general case
   正是 Weil positivity/RH，未給 prime-global constant-one inequality。
3. Connes--Consani, arXiv:1910.14368，section 3逐步說明 X.-J. Li semilocal cutoff attempt
   fails；缺口是所需 operator sign/equality，不能由 positive factors與 cyclic trace推出。

所以外部結果支持目前界線：probabilistic mean與 archimedean compression提供結構，不補
W12.4 的 global centered prime--arch sign。沒有可直接代入 L63/LM11的新 theorem。

Primary sources:
https://arxiv.org/abs/2311.08519 ;
https://arxiv.org/abs/2006.13771 ;
https://arxiv.org/abs/1910.14368
## ES164. positive-time H_t zero rigidity has only `x^(-ct)` precision

只針對 DN22 已命名的 fixed-positive-time 高零點剛性缺口核對 D.H.J. Polymath
arXiv:1904.12438。Theorem 1.5 對 `0<t<=1/2`、`x>=exp(C/t)` 證所有高零點皆實，且相對
explicit quantile `g(x_n,t)=n` 的位置誤差為 `O(x^(-ct))`；section 9 另給 velocity
`-pi/4+O(x^(-ct))`。

DN16 的 backward clock要求 `exp[-C t log^2x]`，而 theorem 只有
`exp[-ct logx]`。分段 reset 只能到 `t~C/logx`；該端點誤差為 constant scale而 gap為
`1/logx`。故此文不能閉合 DN obligation，也沒有宣稱 super-polynomial error。

Primary source: https://arxiv.org/abs/1904.12438
## ES165. no adjacent theorem supplies the DN28 boundary phase homotopy

只針對 `H_t+iH_t'` boundary phase／Laguerre--de Branges monotonicity檢索一手文獻。
Rodgers--Tao arXiv:1801.05914研究 zero dynamics並證 `Lambda>=0`，方向與所需
`Lambda<=0`相反，未給 bottom boundary homotopy。D.H.J. Polymath arXiv:1904.12438 的
Riemann--Siegel approximation只在 `x>=exp(C/t)` 控制正時間高區，DN22已證其精度與 range
不能覆蓋 `t downarrow0` expanding rectangle。Wagner arXiv:2108.01827 的 shifted
Laguerre--Polya結果證 fixed degree／sufficiently high derivative inequalities，沒有 all-x phase
monotonicity或 `H_t+iH_t'` nonvanishing homotopy。

所以沒有可直接代入 L70 的成熟 theorem。DN29另給 positive even smooth heat kernel的 exact
collision反例，排除只靠 kernel positivity/decay的推廣。

Primary sources: https://arxiv.org/abs/1801.05914 ;
https://arxiv.org/abs/1904.12438 ;
https://arxiv.org/abs/2108.01827
## ES166. first Laguerre inequality is not a sufficient phase producer

DN33 named-gap audit核對 Cardon arXiv:0911.1122 與 Csordas--Vishnyakova 2013。對 genus
0/1 real entire functions，real-zero criterion需要一整族 extended/generalized Laguerre
inequalities；classical first inequality `f'^2-ff''>=0` 只是必要條件，一般不充分。Csordas 2013
對 Xi/Fourier kernels亦明說 ordinary Laguerre inequalities一般不充分。

因此即使能證 DN33.1 的 `theta_x<=0`，也沒有完成 collision exclusion；補齊 higher inequalities
就是既有 all-degree Jensen/de Branges obligation，非新 topology升階。

Primary sources: https://arxiv.org/abs/0911.1122 ;
https://eudml.org/doc/269318 ;
https://arxiv.org/abs/1309.0055

## ES167. fixed-log Selberg mollifier literature does not supply an RH-only converse

Only the L89/AP9 converse gap was searched. Báez-Duarte arXiv:math/0205003
records the natural Selberg approximant with coefficients
`mu(n)(1-log n/log N)`, but its proved RH-conditional construction uses a
different `N`-dependent power tilt. Conrey--Myerson arXiv:math/0002254 prove
uniform convergence of the associated sawtooth sums; their Remark 1 shows why
this does not imply the required weighted `L2` convergence, whose small-variable
piece contains a same-scale Riesz--Möbius scalar. Their stated full convergence
input also includes zero separation.

Bettin--Conrey--Farmer arXiv:1211.5191 obtain the conjectural optimal
`1/log N` scale assuming RH and
`sum_(|Im rho|<=T)|zeta'(rho)|^-2 << T^(3/2-delta)`. This additional condition
implies simplicity and is not a consequence of RH. Hence none of these primary
sources proves the RH-only convergence of the Abel-corrected MB1 family, and
none gives an unconditional producer for AP7.2.

Primary sources: https://arxiv.org/abs/math/0205003 ;
https://arxiv.org/abs/math/0002254 ;
https://arxiv.org/abs/1211.5191

## ES168. A0--Xi counting discrepancy is unbounded

This search served only the named fixed-finite-rank spectral gap.  Dunster's
imaginary-order Bessel asymptotics (also catalogued in DLMF 10.45) give, for
fixed `a=2*pi`,

```text
K_(i nu)(a)=amplitude*[sin(nu log(2nu/(ea))+O(1))+O(1/nu)],
```

with monotone phase and corresponding zero asymptotics.  Hence for the P3
core ordinates `beta=2nu`,

```text
N_A0(T)=T/(2pi) log(T/(2pi))-T/(2pi)+O(1).
```

Riemann--von Mangoldt gives the same smooth main term plus `S(T)+O(1)`.
Dobner proves unconditionally that positive values of `S(T)` reach a growing
range up to constant order `(log T/loglog T)^(1/3)`; in particular `S(T)` is
unbounded above.  Therefore `N_zeta(T)-N_A0(T)=S(T)+O(1)` is unbounded.

This rules out every fixed-finite-rank self-adjoint resolvent perturbation or
finite-deficiency domain extension of `A0`, because its spectral counting
difference is bounded by the rank.  It does not rule out a genuinely
singular/infinite-rank domain or an independent operator.

Primary sources: https://doi.org/10.1137/0521055 ;
https://dlmf.nist.gov/10.45 ;
https://arxiv.org/abs/2101.01747
