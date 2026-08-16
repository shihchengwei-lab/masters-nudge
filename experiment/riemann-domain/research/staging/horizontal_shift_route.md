# Xi 水平位移的 Hermite--Biehler descent 路線

本路線不是 finite-degree certificate。它從一個無條件 all-degree
real-rooted deformation出發，詢問是否存在可反覆下降 shift parameter的
Xi-specific positive-kernel theorem。

## HS1. shifted Hermite--Biehler family

採用

`Xi(z)=xi(1/2+iz)`

的 real even normalization。對 `a>0` 定義

`E_a(z)=Xi(z+ia)`, `E_a#(z)=overline(E_a(conjugate z))=Xi(z-ia)`,  (HS1.1)

以及 real entire parts

`A_a=(E_a+E_a#)/2`, `B_a=(E_a-E_a#)/(2i)`.  (HS1.2)

因此

`A_a(z)=[Xi(z+ia)+Xi(z-ia)]/2`

`      =int_0^infinity Phi(u)cosh(au)cos(zu)du`.  (HS1.3)

若 `E_a` 是 Hermite--Biehler，即在 upper half-plane滿足

`|E_a(z)|>|E_a#(z)|`,  (HS1.4)

則 de Branges theorem給 A_a、B_a全部 zeros實且互相 interlace。

## HS2. exact threshold 等於 zero strip 的半寬

令

`delta_*=sup_rho |Re rho-1/2|`,  (HS2.1)

sup取 nontrivial zeros。由

`E_a(z)=xi(1/2-a+iz)`，zero `rho=beta+i gamma` 對應

`z=gamma+i(1/2-a-beta)`.  (HS2.2)

所以 E_a在 upper half-plane無 zeros恰等價於沒有
`beta<1/2-a` 的 zero；functional equation又把這等價成沒有
`beta>1/2+a` 的 zero。

這個充分性可直接逐 zero factor證，不需假設 Hardy bounded type。把 Xi 的
canonical product按共軛 pairs `r+ib,r-ib`（再與 functional-equation反射
成 quartets）分組；`sum |rho|^-2<infinity` 使此 grouping locally uniform。
對 `z=x+iy`, `y>0`，令

`P_(X,b)(t)=[X+(t-b)^2][X+(t+b)^2]`, `X=(x-r)^2`.

則 shifted pair在 denominator/numerator的 squared-modulus差正是

`P_(X,b)(y+a)-P_(X,b)(y-a)`

`=8ay[X+y²+a²-b²]>=0`  (HS2.3)

只要 `a>=|b|`；實軸 zeros是 `b=0` 的同一公式。逐 pair相乘並取 product
極限即得 `|E_a#(z)|<=|E_a(z)|`，upper half-plane內非退化時為 strict。
反向若有 `|b|>a`，相應 shifted zero進入 upper half-plane，E_a不可能 HB。
因此

`E_a is Hermite--Biehler <=> |Re rho-1/2|<a for every rho`.  (HS2.4)

特別地 `a>delta_*` 時成立；若 `a=delta_*`，則取決於 supremum是否被zero
達到，達到時 E_a有 real zero而只剩 boundary退化版本。後續 base `a=1/2`
使用已知 strict strip `0<beta<1`。HS2.4 也警告：若直接由 unknown zeros
驗證 HB，便完全循環。

## HS3. 無條件 all-degree base：a>=1/2

standard zero-free half-planes與 functional equation給所有 nontrivial zeros
`0<beta<1`，故 `delta_*<=1/2`。由 HS2，對每個 `a>1/2`，E_a是
Hermite--Biehler；取極限亦得 `a=1/2` 的適當 boundary版本。因此

`A_a(z)=[Xi(z+ia)+Xi(z-ia)]/2`  (HS3.1)

對全部 `a>=1/2` 有全實 zeros。這是一個 genuine all-degree起點，不使用
RH，也不是逐 degree驗證。

另一方面 `A_a -> Xi` locally uniformly as `a downarrow0`。所以若能證

`E_a is HB for every a>0`,  (HS3.2)

Hurwitz立即迫使 Xi全部 zeros實，即 RH。反向由 HS2亦成立。

## HS4. harmonic deformation本身不會向下保存實根

由 HS1.3直接有

`partial_a^2 A_a=-partial_z^2 A_a`.  (HS4.1)

但 PDE、real symmetry與某個大 a的 real-rootedness不夠。toy

`F(z)=z^2+1`

給

`[F(z+ia)+F(z-ia)]/2=z^2+1-a^2`,  (HS4.2)

只在 `a>=1` real-rooted，下降穿過 1後立即產生 imaginary zeros。因此 HS3
不能靠 continuity或一般 harmonic maximum principle推到 0；必須使用 Xi 的
theta/arithmetic結構。

## HS5. single uniform target：HB half-shift descent

令標準 de Branges kernel

`K_a(z,w)=[E_a(z)overline(E_a(w))-E_a#(z)overline(E_a#(w))]`

`          /[2pi i(conjugate(w)-z)]`.  (HS5.1)

`K_a` 對所有 finite point sets positive semidefinite恰等價 E_a為 HB。故一個
足以完成 RH、且真正 uniform-in-degree的升降定理是：對每個 `a in (0,1/2]`
直接由 Phi/theta或 centered primes構造 positive-kernel identity

`K_(a/2)=T_a[K_a]+L_a`, `T_a positivity-preserving`, `L_a>=0`,  (HS5.2)

其中 T_a、L_a必須在不知道 zeros時定義。從 HS3 的 `a=1/2` 反覆套用，得到
`a=2^(-m-1)` 全部 HB，再由 local uniform limit完成 HS3.2。

HS5.2 不是允許把 K_(a/2)事後宣告正；合格 construction須給顯式 Gram／
integral operator。Fourier側從 E_a到 E_(a/2)是把 bilateral theta feature
`e^(-au)` untilt成 `e^(-au/2)`；普通正 Fourier measure或一側 contraction不
保 HB，HS4已給最小反例。真正缺口是證這個 untilting在 Xi arithmetic
feature space具有 positive defect。

## HS6. 與既有路線的關係及 density 強度

HS不是第四個獨立 positivity obligation。令 `a downarrow0` 時，HS5 kernel的
一階項正是 Xi/ Xi' 的 Laguerre--de Branges kernel；其全尺寸正性與 A20/W18
的 Stieltjes/Weil target合流。新處只在於它提供無條件 base `a=1/2` 與一個
離散 dyadic descent介面。

若只把 HB推到某個固定 `a_0>0`，HS2只給完整 zero-free substrip
`|Re rho-1/2|<=a_0`，不是 density結果。若只證 K_a在有限維子空間或平均
points正，則 generic negative squares仍可藏在其正交補；沒有 uniform
negative-index bound時甚至不能推出 density-one RH。故 HS合格的 partial
milestone必須是一次嚴格下降某個全域 shift，或一個可計數的 negative-square
density theorem，不能是 finite kernel批次。

## HS7. positive Fourier measure仍不保存 half-shift descent

HS5不能只使用 `Phi>=0`。取 positive even discrete Fourier measure，使其
cosine transform在 shift a時為

`F_a(z)=cosh(a)cos z+(2/3)cosh(2a)cos(2z)`.  (HS7.1)

寫 `x=cos z` 與

`r_a=[(2/3)cosh(2a)]/cosh(a)>0`，則除正因子外

`F_a=2r_a x²+x-r_a`.  (HS7.2)

兩個 x-roots皆落在 `[-1,1]` 恰等價 `r_a>=1`：positive root對所有 r皆
小於 1，而 negative root大於等於 -1 等價
`1+sqrt(1+8r²)<=4r`，平方後就是 `r>=1`。所以 `r_a>=1` 時 F_a全部 z-zeros
實；`r_a<1` 時 negative x-root小於 -1，產生 nonreal z-zeros。

現在取 `a=log2`。exact 有

`cosh a=5/4`, `cosh(2a)=17/8`,

故 `r_a=17/15>1`。但

`cosh(a/2)=3/(2sqrt2)`,

所以

`r_(a/2)=[(2/3)(5/4)]/[3/(2sqrt2)]=5sqrt2/9<1`.  (HS7.3)

因此 F_a全實零而 F_(a/2)已有非實零；底層 measure仍完全正。這嚴格排除
「ratio `cosh(au/2)/cosh(au)` positive definite／普通 positive convolution，
所以 real-rootedness下降保存」的捷徑。HS5若成立，必須使用 Phi 的更強
arithmetic total positivity或 centered-prime defect，不能只用正 kernel。

## HS8. untilting是正卷積，但不是 variation-diminishing

令

`r_a(u)=cosh(au/2)/cosh(au)`.  (HS8.1)

residue calculus（或 sech Fourier integral）給

`Fourier[r_a](t)`

`=(sqrt2 pi/a) cosh[pi t/(2a)]/cosh[pi t/a] >0`  (HS8.2)

（依 Fourier normalization只差整體正常化）。所以 r_a確為 positive
definite；從 A_a到 A_(a/2)可視為對 real variable作 positive convolution。

但此 convolution kernel不是 PF_infinity。若 normalized density為 mu_a，
其 bilateral Laplace transform是

`M_a(s)=r_a(-is)=cos(as/2)/cos(as)`.  (HS8.3)

Schoenberg variation-diminishing criterion要求 `1/M_a` 延拓成
Laguerre--Polya entire function；此處

`1/M_a(s)=cos(as)/cos(as/2)`  (HS8.4)

在 `cos(as/2)=0` 處有未消去 poles（numerator在該處為 -1），故不可能。
因此 positive definiteness只給 smoothing，不給 real-zero preservation；
HS7 是此非-PF_infinity性的有限頻率 witness。

若 Xi能下降，所需正性必須來自 mu_a與特定 theta kernel Phi的 coupled
composition，而不是 mu_a單獨的 variation-diminishing性。

## HS9. real/imaginary channels的 exact split；PF∞方向仍不對

HS5 必須同時追蹤 E_a的 real/imaginary parts。由 HS1.3，從 a降到 b=a/2時

`A_b = r_a(-iD) A_a`,

`B_b = q_a(-iD) B_a`,  (HS9.1)

其中

`q_a(u)=sinh(au/2)/sinh(au)=1/[2cosh(au/2)]`.  (HS9.2)

兩通道的 multiplier不同。它們又有 exact positive split

`r_a(u)-q_a(u)`

`=1/[2cosh(au/2)cosh(au)]>0`.  (HS9.3)

q_a與 sech(au)皆 positive definite，故差 HS9.3亦然。q_a的 Fourier density
是 `(pi/a)sech(pi t/a)>0`；normalized bilateral Laplace reciprocal為

`2cos(as/2)`,  (HS9.4)

這次確是 Laguerre--Polya entire，所以 q-channel convolution kernel屬
PF_infinity。

但這不是「安全的 real-root preserving common part」。PF_infinity convolution
的 variation-diminishing方向只保證 real-axis sign changes不增加，可能把
real zeros消掉並送成 complex pair。exact toy是 normalized characteristic
`sech(au/2)` 的 symmetric convolution measure，其 variance為 `a²/4`；故

`T_q[z²]=z²+a²/4`,  (HS9.5)

已從 double real zero產生 imaginary zeros。因此即使把 HS9.1寫成 common
q-smoothing加只作用於 A的 positive remainder，也不能由 E_a HB推出 E_b HB。

surviving target必須直接控制 pair `(A_b,B_b)` 的 symplectic/de Branges
Bezoutian；分別證兩個 scalar convolutions positive、PF_infinity或
variation-diminishing都不足。

## HS10. half-angle duplication會把 Xi 本身帶回；須防止隱性循環

置 `b=a/2`。由 definitions直接有

`E_b(z+ib)=E_a(z)`, `E_b(z-ib)=E_0(z)=Xi(z)`.  (HS10.1)

取 real/imaginary parts，或在 Fourier側用
`2cosh²(bu)=cosh(au)+1`、`2sinh(bu)cosh(bu)=sinh(au)`，得到

`A_b(z+ib)+A_b(z-ib)=A_a(z)+Xi(z)`,

`B_b(z+ib)+B_b(z-ib)=B_a(z)`.  (HS10.2)

所以 inverse-shift／half-angle descent不是只由已知 HB pair `(A_a,B_a)`
生成 `(A_b,B_b)`；real channel會把 endpoint target `A_0=Xi` 原封不動帶回。
Xi作為顯式 theta integral當然可使用，但若 proposed defect identity把 HS10.2
中的 Xi cross-Bezoutian直接宣告 positive，就已假設所求 real-rootedness。

HS5 的合格驗收因此再加一條：所有 A_0 terms必須保留，並由 prime/theta
integral直接完成其與 smoothed B-channel的 sign，而不能用「A_0是 limit」或
unknown-zero product給正性。若 half-shift formula只把 K_0藏入 remainder，
它是 W18 的等價改寫，不是 descent theorem。

## HS11. known-GRH toy：成功 descent來自 shift-independent unitary phase

用 `spectral_toy_route.md` 的功能域 quadratic。critical coordinate可寫成

`F_theta(z)=cos(Lz)-cos theta`, `theta real`.  (HS11.1)

其 arithmetic RH input `|a_q|<=2sqrtq` 正等價 theta為實、boundary phase
`e^(itheta)` unitary。此時有不依賴 horizontal shift的 factorization

`F_theta(z)=-2sin[(Lz+theta)/2]sin[(Lz-theta)/2]`.  (HS11.2)

所以對每個 c>0，`E_c(z)=F_theta(z+ic)` 的兩個 sine factors全部 zeros都在
lower half-plane；每個 factor是 HB，product仍為 HB。故 toy 的
`c -> c/2` descent並不依賴 HS8 smoothing，而由同一 real theta／unitary
monodromy對所有 c同時控制。

若 theta非實，HS11.2 的一族 zeros已離開 real axis，沒有 scalar convolution
能修復。這驗證 nudge要求：在已知 GRH toy上，真正可升 all-degree且可乘積
組合的機制是 shift-independent unitary Frobenius phase；自伴直和處理多因子。

Riemann情形目前沒有由 primes/theta獨立構造的 global unitary monodromy。
若由 Xi zeros的 arguments事後定義 phases便循環；若只用 local Euler
colligations，又遇 P29 的 critical infinite-product divergence。HS11因此給出
合格新輸入的 type，而未提供該輸入。

## HS12. the real-zero collision map loses the one-sign orientation

Write on real `(a,x)`

```text
Xi(x+ia)=A(a,x)+iB(a,x).
```

For the real-zero collision map `F=(A,A_x)`, at `A=A_x=0`,

```text
det D_(a,x)F=A_a A_xx
                 =-B_x B_ax
                 =-(1/2)partial_a(B_x^2).             (HS12.1)
```

Here the Cauchy--Riemann equations give `A_a=-B_x` and `B_a=A_x`.
There is no PDE-fixed sign. The single harmonic polynomial

```text
A(a,x)=x^2-a^2+3a-2
      =Re[(x+ia)^2-3i(x+ia)-2]                       (HS12.2)
```

has collisions at `(a,x)=(1,0)` and `(2,0)`, with determinants `+2` and `-2`.
Thus the horizontal-shift harmonic equation permits exact orientation
cancellation. DN27's one-sign heat ledger does not transfer to `(A,A_x)`;
proving a sign for Xi would require a new arithmetic monotonicity of `B_x^2`.

## HS13. restoring one sign gives the ordinary RH argument principle

If instead one uses the analytic map `G=(A,B)`, then at every simple Xi zero

```text
det D_(x,a)G=|Xi'(x+ia)|^2>0                         (HS13.1)
```

(and the sign is uniformly reversed in the coordinate order `(a,x)`). Higher
multiplicities contribute their usual positive analytic multiplicity. Hence
the boundary degree of G is exactly the argument-principle count of Xi zeros
in the horizontal rectangle.

Taking regular lower boundaries `a=epsilon downarrow0`, zero degree throughout
`0<a<1/2` is equivalent, by functional-equation symmetry, to absence of
off-critical zeta zeros, i.e. RH. Therefore the horizontal family has a strict
dichotomy: `(A,A_x)` is a genuine real-zero collision map but has cancelling
orientations; `(A,B)` has one sign but directly counts the unknown zeta zeros.
It supplies no intermediate topological invariant between HS5 and RH.

## HS14. the unspecified coupled-Bezoutian decomposition is only an acceptance schema

Fix `a>0` and put `b=a/2`. Suppose `K_a` is positive semidefinite. If one only
asks for the existence of a positivity-preserving map `T_a` and a positive
semidefinite kernel `L_a` such that

```text
K_b=T_a[K_a]+L_a,                                      (HS14.1)
```

then (HS14.1) is equivalent to `K_b>=0`. The forward implication is immediate;
conversely take `T_a=0` and `L_a=K_b`. Thus HS5.2, without an independently
specified operator class and an explicit theta/prime formula for `T_a,L_a`,
merely renames HB descent.

A noncircular reopening must define `T_a,L_a` before invoking positivity of
`K_b`, prove (HS14.1) algebraically, and survive HS7--HS10. No such pair is
present in the current project. HS5 is an acceptance specification, not a
live lemma.
