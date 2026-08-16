# Xi 偶矩與 Jensen 多項式路徑

令 `Φ(u)` 為 `positivity_kernel.md` 的正半軸 cosine 核，並定義

`M_k=∫_0^∞ Φ(u)u^(2k)du`，

`G(w)=Xi(i sqrt(w))=Σ_(k≥0) M_k w^k/(2k)!`

`    =Σ_(k≥0) γ_k w^k/k!`，其中 `γ_k=k!M_k/(2k)!>0`。

G 是實整函數；Xi 的零點 z 與 G 的零點 `w=-z²` 對應。因此 Xi 的零點全實，等價於 G 的零點全在負實軸。

## J1（已證）：全階 Jensen hyperbolicity 是充分條件

定義第 d 階 Jensen 多項式

`J_d(X)=Σ_(k=0)^d C(d,k)γ_kX^k`。

若每個 d 的 `J_d` 都只有負實零點，則 RH 成立。

證明：

`J_d(X/d)=Σ_(k=0)^d [C(d,k)/d^k]γ_kX^k`。

對固定 k，`C(d,k)/d^k→1/k!`。因 G 整函數，標準係數 majorant／截尾論證給 `J_d(X/d)→G(X)` 在每個緊集局部一致。全為負實根的實多項式之非零局部一致極限仍屬 Laguerre–Pólya 閉包；等價地，可在避開實軸的小圓盤上用 Hurwitz 定理排除非實零點。因此 G 的零點全為負實數，故 Xi 零點全實。

邏輯邊界：證明任意固定最大階只給有限條件；J1 要求所有 d。有限數值 hyperbolicity 不是極限證明。

## J2（已證）：二次 Jensen／偶矩比條件

更一般地，shifted 二次 Jensen 多項式為

`J_(2,n)(X)=γ_n+2γ_(n+1)X+γ_(n+2)X²`。

因係數正，它有兩個負實根恰等價於 Turán 不等式

`γ_(n+1)²≥γ_nγ_(n+2)`。  (J2.1)

把 γ 的階乘因子代入並令 `k=n+1`，化簡得到精確偶矩比形式

`M_k²/(M_(k-1)M_(k+1)) ≥ (2k-1)/(2k+1)`，`k≥1`。  (J2.2)

推導中的階乘比為

`[γ_k²/(γ_(k-1)γ_(k+1))]`

`=[(2k+1)/(2k-1)]·[M_k²/(M_(k-1)M_(k+1))]`。

一般正測度的 moments 由 Cauchy–Schwarz 只給相反方向
`M_k²≤M_(k-1)M_(k+1)`；它沒有提供 J2.2 所需的定量接近程度。因此不能把「Φ>0」誤當成 Turán 證明。

## J3（候選，部分完成）：由 Xi 核特殊曲率控制全部 Jensen 階

離線網格顯示 Φ 可能具有強 log-concavity，而低階 γ Jensen 多項式也通過數值 hyperbolicity 篩查。但 K2 已證 kernel log-concavity 本身不足以控制 Fourier 零點；要完成 J1，必須證明能推出全部 Jensen 行列式／hyperbolicity 的更強偶矩結構。

第一個子目標（所有 k 的 J2.2）已由 J4–J7 完成。它仍只處理二次 Jensen 多項式，不足以推出 RH；接著必須提升至任意固定 d 並取得對 d 一致的證明。

## J4（已證）：單調 score 比率推出全部二次 Turán 不等式

令一般正函數 f 定義在 `[0,∞)`，充分光滑、快速衰減、`f'(0)=0`，並置

`q(u)=-f'(u)/[u f(u)]`，`u>0`。

若 q 非遞減，則 f 的偶矩 `M_k=∫f(u)u^(2k)du` 對每個 `k≥1` 都滿足 J2.2。

證明：更一般地置 `I_p=∫u^p f(u)du`，取 `p≥2`。分部積分給

`∫u^(p+2)q(u)f(u)du=(p+1)I_p`，

`∫u^p q(u)f(u)du=(p-1)I_(p-2)`。

在機率測度 `dν=u^pf(u)du/I_p` 下，`u²` 與 q 都非遞減，故 Chebyshev 協方差不等式給

`E_ν[u²q]≥E_ν[u²]E_ν[q]`。

代入三個積分恒等式得到

`p+1 ≥ [I_(p+2)/I_p]·[(p-1)I_(p-2)/I_p]`，

亦即

`I_p²/[I_(p-2)I_(p+2)]≥(p-1)/(p+1)`。

取 `p=2k` 正是 J2.2。證畢。

## J5（已證，J6 + J7）：Xi score 全域單調

對 `f=Φ`，J4 所需條件等價於

`q'(u)=[(log Φ)'(u)-u(log Φ)''(u)]/u²≥0`。  (J5.1)

J6 解析處理 `u≥1`；J7 的有向外捨入區間證書處理 `0<u<1`。因此 `q'(u)>0` 對所有 u>0 成立，J4 遂證明 Xi 偶矩係數的全部 shifted degree-2 Jensen/Turán 不等式。這仍須處理 `d≥3`，不是 RH 證明。

## J6（已證）：Xi score 在 `u≥1` 嚴格遞增

置 `r=πe^(2u)`、`r_n=n²r`，把 Φ 的第 n 項寫成

`T_n(u)=2πn²e^(5u/2)(2r_n-3)e^(-r_n)>0`。

令 `a_n=(log T_n)'`、`b_n=a_n'`。直接微分得

`a_n=5/2+4r_n/(2r_n-3)-2r_n`，

`b_n=-4r_n-24r_n/(2r_n-3)²`。

以權重 `p_n=T_n/Φ` 取期望，log-sum-exp 微分公式給

`(log Φ)'=E_p[a_n]`，

`(log Φ)''=E_p[b_n]+Var_p(a_n)`。

因此 J5.1 的分子 S 為

`S=(log Φ)'-u(log Φ)''`

` =E_p[a_n-ub_n]-uVar_p(a_n)`。  (J6.1)

當 `u≥1` 時，每個

`a_n-ub_n=2r_n(2u-1)+5/2+4r_n/(2r_n-3)`

`             +24ur_n/(2r_n-3)² ≥2r_n≥2r`。  (J6.2)

現在控制變異項。因 `r>20`，

`T_n/T_1 < 2n⁴ exp[-(n²-1)r]`，`n≥2`，

且 `|a_n-a_1|≤3rn²`。又相鄰的
`n⁸exp[-(n²-1)r]` 比值小於 1/2，故

`Σ_(n≥2)n⁸exp[-(n²-1)r]≤512e^(-3r)`。

於是

`Var_p(a_n)≤E_p[(a_n-a_1)²]≤9216r²e^(-3r)`。

對 `u≥1` 有 `u≤r`，且 `9216r³e^(-3r)<1`（在 `r≥20` 單調下降，端點也小於 1）。結合 J6.1–J6.2，

`S≥2r-1>0`，所以 `q'(u)=S/u²>0`。證畢。

這把 J5 的未證區域縮為緊區間 `0<u<1`。網格無反例不能填補該區間；仍需解析不等式或有向外捨入的區間證明。

## J7（已證，機器輔助區間證書）：緊區間三階 log 曲率

令 `L=log Φ`、`S=L'-uL''`，所以 `q'=S/u²`。Φ 的偶性給 `L'(0)=0`，故 `S(0)=0`，而

`S'(u)=-uL'''(u)`。

因此只需證

`(log Φ)'''(u)≤0`，`0<u<1`，  (J7.1)

就有 `S(u)≥0`。`experiments/verify_xi_score_interval.py` 已給出可重跑的有向外捨入證書：

- 用 Machin 公式的交錯有理級數夾住 π，寬度 `10^-69`；
- Decimal 的 correctly-rounded exp 結果再以相鄰 representable number 向外擴張；
- 顯式驗證 `n≥5` 對 0 至 4 階導數的解析 majorant；
- 在 `[0,0.1]` 逐格證 `(log Φ)''''<0`，由偶性得 `(log Φ)'''<0`；
- 在 `[0.1,1]` 先除以第一 theta 項，再以自適應二分證 `(log Φ)'''<0`。

最弱的嚴格上界仍為負：近零四階 numerator 上界約 -32.36，正規化三階上界約 -0.01566。故 J7.1 在整個 `0<u<1` 成立。配合 J6，J5 完成。

## J8（已證）：三次 Jensen 的精確判別式

令 `a=γ_n`、`b=γ_(n+1)`、`c=γ_(n+2)`、`d=γ_(n+3)`。三次 shifted Jensen 多項式為

`a+3bX+3cX²+dX³`。

係數全正，所以它 hyperbolic 恰等價於 cubic discriminant 非負：

`Δ/27=3b²c²-4db³-4ac³-a²d²+6abcd ≥0`。  (J8.1)

定義相鄰 Turán 比率

`U=b²/(ac)`，`V=c²/(bd)`。

除以 `a²d²>0`，J8.1 等價於

`F(U,V)=3U²V²-4U²V-4UV²+6UV-1≥0`。  (J8.2)

J5 只給 `U,V≥1`，這不自動推出 J8.2。精確反例為
`(a,b,c,d)=(1,1,1,1/2)`：兩個 Turán 條件分別為等號與嚴格正，但
`(U,V)=(1,2)`、`F=-1`，三次判別式為負。因此「完成全部 degree 2 後直接歸納 degree 3」的裸推論無效。

## J9（候選，未證）：相鄰 Turán 比率的平滑控制

寫 `T=UV`，J8.2 是

`3T²+6T-1 ≥4T(U+V)`。

除了 `U,V≥1`，還需限制相鄰比率的失衡。下一個目標是從 Φ 的 score 高階單調性或多重協方差，直接證明 Xi 的 `(U_k,U_(k+1))` 落在 J8.2 區域；僅有 J4 的一階 Chebyshev 協方差不足。

## J10（已證障礙）：score 單調不推出 degree 3

對 `ε>0` 考慮

`f_ε(u)=exp(-u²-εu⁶)`，`u≥0`。

其 score 比率是

`q_ε(u)=-f_ε'(u)/[uf_ε(u)]=2+6εu⁴`，

故嚴格遞增；而且 q 的每一階導數都非負（五階以上為零）。J4 因而保證全部 degree-2 Turán 不等式。

另一方面，令 `M_k(ε)=∫u^(2k)f_ε(u)du`、
`γ_k(ε)=k!M_k(ε)/(2k)!`。用

`e^(-εu⁶)=1-εu⁶+(ε²u¹²)/2+O(ε³u¹⁸)`

與 Gaussian 偶矩

`∫_0^∞u^(2j)e^(-u²)du=√π(2j)!/[2·4^j j!]`

逐項代入 n=0 的 J8.1，得到

`[Δ_3(ε)/(27π²)]`

`=-(9/16384)ε²+(34965/32768)ε³+O(ε⁴)`。  (J10.1)

特別地，所有充分小的 `ε>0` 都有 `Δ_3(ε)<0`，所以 degree-3 Jensen 多項式有非實根。Taylor 餘項可由 `e^-x` 的積分餘項及 Gaussian 高矩支配；精確有理係數驗證器為 `experiments/verify_score_not_cubic.py`。

因此，即使把 Xi 的 J5 全域證明完成，也不可能只靠「q 遞增、凸、乃至所有導數非負」推到 degree 3。必須利用 Xi 核比一般 super-Gaussian 核更特殊的定量結構。

## J11（已證歸約；候選不等式未證）：degree 3 的協方差形式

對 `k≥1`，令 `ν_k` 是密度正比於 `u^(2k)Φ(u)` 的機率測度，並置

`C_k=Cov_(ν_k)(u²,q(u))/(2k+1)`。

J4 的等式部分給

`C_k=1-1/U_k`，其中 `U_k=γ_k²/(γ_(k-1)γ_(k+1))`。  (J11.1)

把 `U=1/(1-C_k)`、`V=1/(1-C_(k+1))` 代入 J8.2，可化為

`(C_k-C_(k+1))²`

`≤C_kC_(k+1)[2(C_k+C_(k+1))-C_kC_(k+1)]`。  (J11.2)

J5 只證 `C_k≥0`；J10 顯示非負性本身不足。J11.2 是 degree 3 的下一個精確目標：需要控制相鄰 tilted measures 下協方差的變化率。

## J12（已證）：一個足以完成 degree 3 的簡化遞推

令 `C=C_k`、`D=C_(k+1)`。若

`0<C≤1/12`，`C(1-4C)≤D≤C`，  (J12.1)

則 J11.2 成立。

證明：寫 `D=C(1-δ)`，則 `0≤δ≤4C≤1/3`。J11.2 除以 `C²` 後成為

`δ²≤C(1-δ)[4-2δ-C(1-δ)]`。

左側至多 `16C²`；右側至少 `2C(1-4C)`。而 `C≤1/12` 給
`2C(1-4C)≥16C²`。證畢。

所以若能證所有 k 都有

`0<C_k≤1/12`，

`C_k(1-4C_k)≤C_(k+1)≤C_k`，  (J12.2)

Xi 的全部 shifted degree-3 Jensen 多項式便 hyperbolic。J12.2 比精確 J11.2 強，但形式較適合由 size-bias／協方差比較攻擊。

## J13（數值與鞍點候選；未證）

對數尺度 Laplace quadrature 到 `k=200` 顯示：`C_k` 嚴格下降，J12.2 無失敗，且 J11 左右比最大值在 k=1 約 0.108，之後下降。這不是無限序列證明。

形式鞍點分析可解釋候選尺度。n=1 theta 項的 moment saddle `u_k` 約滿足

`k≈u_kπe^(2u_k)`。

若只保留 envelope 的二階主項，得到

`C_k≈(2u_k-1)/[k(2u_k+1)]`。

故 `C_k` 約為 `1/k` 級，且相對下降約 `1/k`；J12 的允許下降 `4C_k` 同階而常數較寬。要把此變成證明，必須給 moment Laplace 法對一、二、三階 k 差分的一致顯式誤差，並控制 `n≥2` theta 尾；目前尚未完成。

## J14（已證）：高 theta 項對偶矩是超多項式小擾動

把 Φ 的第 n 項記為

`T_n(u)=2πn²e^(5u/2)[2πn²e^(2u)-3]exp[-πn²e^(2u)]`。

直接代換得到精確位移恒等式

`T_n(u)=n^(-1/2)T_1(u+log n)`。  (J14.1)

令

`A_k=∫_0^∞u^(2k)T_1(u)du`，

`R_k=Σ_(n≥2)∫_0^∞u^(2k)T_n(u)du`。

對 `k≥3` 取 `V=log k`。在 J14.1 中置 `v=u+log n`。對 `2≤n≤k` 且 `v≤V`，

`(v-log n)^(2k)≤v^(2k)exp[-2klog n/V]`

`≤v^(2k)exp[-2klog2/log k]`。

又 `Σ_(n≤k)n^(-1/2)≤2√k`。其餘 `v≥V` 的部分交換 n 和積分，使用

`Σ_(n≤e^v)n^(-1/2)≤2e^(v/2)`，得到

`R_k≤2√k e^[-2klog2/log k]A_k`

` +4∫_V^∞e^(v/2)v^(2k)T_1(v)dv`。  (J14.2)

在 `v≥V`，

`e^(v/2)T_1(v)≤4π²e^(5v)exp[-πe^(2v)]`。

右側 integrand 的 log 導數至多
`2k/log k+5-2πk²≤-πk²`。因此尾積分至多

`4π k³(log k)^(2k)e^(-πk²)`。

另一方面，T₁ 在 `[1,2]` 遞減；置明確常數 `c_0=T_1(2)>0`，則
`A_k≥c_0/k`（只積 `[1,1+1/k]`）。合併得

`R_k/A_k ≤2√k e^[-2klog2/log k]`

` +(16π/c_0)k⁴(log k)^(2k)e^(-πk²)`。  (J14.3)

故 `R_k/A_k` 比任意 k 的負冪更快趨零。特別地，完整 moment 的 log 二階差分與只保留 n=1 的版本相差 `e^{-c k/log k}` 級；若能對 n=1 證 J12 有某個多項式級餘裕，高 theta 項對充分大 k 不會破壞它。

J14 尚未證 n=1 本身的 J12 遞推；它完成的是計畫中的 theta 尾降階。

## J15（已證）：第一 theta 項的唯一 saddle 與曲率界

令 `r=πe^(2u)`，並寫

`L(u)=log T_1(u)`，`H_k(u)=2klog u+L(u)`。

直接微分，置 `h(r)=4r/(2r-3)`，得

`L'=5/2+h(r)-2r`，

`L''=-4r-24r/(2r-3)²<0`。

所以 `H_k''<0`；又 `H_k'→+∞`（`u↓0`）且 `H_k'→-∞`（`u→∞`），每個 k 有唯一 saddle `α_k`。

因 `r>π>3` 時 `2<h(r)<4`，saddle 方程給出精確位置夾界

`k/α_k+9/4 < πe^(2α_k) < k/α_k+13/4`。  (J15.1)

特別地，若 `w_k` 由 `πw_ke^(2w_k)=k` 定義，則 `α_k>w_k` 且

`α_k-w_k=O(w_k/k)`；所以 `2α_k=W(2k/π)+O((log k)/k)`。

令 saddle 曲率 `λ_k=-H_k''(α_k)`。由 J15.1 及
`24r/(2r-3)²<8` 得

`2k/α_k²+4k/α_k < λ_k`

`<2k/α_k²+4k/α_k+21`。  (J15.2)

三階導數亦有精確式

`H_k'''=4k/u³-8r+48r(2r+3)/(2r-3)³`，

故在 saddle

`|H_k'''(α_k)|≤4k/α_k³+8πe^(2α_k)+48`。  (J15.3)

再微分並用 `2r-3>r`，可得粗但顯式的

`|H_k''''(α_k)|≤12k/α_k⁴+16πe^(2α_k)+736`。  (J15.4)

J15.2–J15.4 顯示標準化三、四階量隨 k 衰減，允許 Laplace 展開；但僅有 Gaussian 主項的未結構化相對誤差不足以控制 J12 的相鄰二、三階差分。

## J16（數值診斷；未證）：需要一階 Laplace 修正

只對 T₁ 計算 moments，將 J13 的主項記為

`C_k^(0)=(2α_k-1)/[k(2α_k+1)]`。

到 k=199 的離線結果顯示 `C_k^(0)<C_k`，且相對誤差

`C_k/C_k^(0)-1 ≈3/(2k)`。

加入乘子 `1+3/(2k)` 後，殘差降至約 `O(k^-2)`，但常數仍隨 α 緩慢變化。J12 的遞推餘裕本身是 `k^-2` 級，因此下一步至少要推導一階 Laplace 修正，並對其 k 差分給一致餘項；只證 `A_k=e^(H_k(α_k))sqrt(2π/λ_k)[1+O(1/k)]` 不夠。

## J17（已證歸約）：J12 的 log-moment 累積量走廊

此節先對第一 theta 項寫

`A(t)=∫_0^∞u^(2t)T_1(u)du`，`a(t)=log A(t)`，`t>-1/2`，

並令 `μ_t` 的密度為 `u^(2t)T_1(u)/A(t)`。double-exponential 尾允許在任意緊的 t 區間逐次微分，所以若 `X=log u`，則

`a'(t)=2E_t X`，`a''(t)=4Var_t(X)`，`a'''(t)=8κ_(3,t)(X)`。  (J17.1)

置

`D_k=a(k-1)-2a(k)+a(k+1)`，`p_k=(2k-1)/(2k+1)`。

由 γ 的 factorial normalization 直接約去得到

`1/U_k=p_k exp(D_k)`，`C_k=1-p_k exp(D_k)`。  (J17.2)

而二階差分有精確 B-spline 表示

`D_k=4∫_(-1)^1(1-|s|)Var_(k+s)(X)ds`，  (J17.3)

`D_(k+1)-D_k=8∫_(-1)^1∫_0^1(1-|s|)κ_(3,k+s+r)(X)dr ds`。  (J17.4)

故問題並不是籠統地估計一個 moment，而是要把傾斜後 `log u` 的方差及第三累積量壓進下列精確走廊。若置 `R_k=p_kexp(D_k)=1-C_k`，J12.2 等價於

`log[11/(12p_k)]≤D_k<-log p_k`，  (J17.5)

以及

`log(p_k/p_(k+1))≤D_(k+1)-D_k`

`≤log[(4R_k²-7R_k+4)/R_k]-log[p_(k+1)/p_k]`。  (J17.6)

J17.3–J17.6 是有限 k 區間證明與大 k saddle 展開的共同接口：前者可直接 enclosure `A(t)`，後者只須控制一個自然 exponential family 的二、三階累積量。

## J18（已否證捷徑）：log-u 變數下並非全域 log-concave

一個自然嘗試是對 `x=log u` 使用全域 Brascamp–Lieb 方差界。但令 `L(u)=log T_1(u)`，則 x 密度的 log（除線性 tilt 外）為 `x+L(e^x)`，其二階導數是

`uL'(u)+u²L''(u)`。  (J18.1)

在 `u↓0` 時，J15 的公式給

`L'(0)=5/2+4π/(2π-3)-2π`

`=(-8π²+30π-15)/[2(2π-3)]>0`。  (J18.2)

最後一個正號可由 `3<π<22/7<(15+√105)/8` 直接核對。因此 J18.1 對所有充分小的正 u 為正；任意 k 的線性 tilt 不改變二階導數。故 transformed density 並非全域 log-concave，不能直接套用全域強凸／Brascamp–Lieb 即完成 J17.5–J17.6。

這不排除切掉極小左尾後在主 saddle 區域使用局部強凸；但該作法必須另外給左尾質量與其二、三階 cumulant 的顯式界。普通的全域 log-concavity 捷徑至此封閉。

## J19（已證）：顯式左尾隔離與局部強凸

取 `δ=1/100`。先給 `b=L'(0)` 一個完全顯式的粗界。函數

`5/2+4p/(2p-3)-2p`

對 `p>3/2` 嚴格遞減；由初等 Archimedean 界 `π>157/50`，

`0<b<5/2+4(157/50)/(2(157/50)-3)-2(157/50)`

`=101/2050<1/20`。  (J19.1)

J15 又給 `L''(u)<-4πe^(2u)<-12`。所以

`L'(u)<1/20-12u`。  (J19.2)

特別地，對所有 `u≥δ`，`L'<0`，且 x 變數下的負 log-density 曲率滿足

`-[uL'(u)+u²L''(u)]`

`>24u²-u/20≥19/10000`。  (J19.3)

因此截在 `u≥δ` 的每個 tilted density 都是顯式強 log-concave；曲率不依賴 tilt 參數 t。

左尾亦可完全控制。對 `t≥1`，令 `μ_t` 如 J17。由 L 的凹性與 J19.1，當 `0<u≤δ` 時

`T_1(u)≤T_1(0)e^(u/20)≤T_1(0)e^(δ/20)`。  (J19.4)

另一方面，J19.2 證 T₁ 在 `[1,2]` 遞減，故

`A(t)≥∫_1^(1+1/t)u^(2t)T_1(u)du≥T_1(2)/t`。  (J19.5)

置 `q=2t+1`、`Y=-logδ`。對 `m=0,1,2,3`，直接以 `y=-logu` 積分得到

`E_t[1_(u≤δ)|logu|^m]`

`≤[tT_1(0)e^(δ/20)/T_1(2)] δ^q`

` ×Σ_(j=0)^m [m!Y^j/(j!q^(m-j+1))]`。  (J19.6)

這是解析不等式，不依賴數值積分。它以 `δ^(2t)` 衰減，故足以把大 t 的左尾對方差、第三 cumulant 的影響隔離；但將 raw moments 轉成 J17.5–J17.6 所需的 sharp central bounds 仍須和 saddle 鄰域估計一起完成。

`experiments/scan_t1_left_tail.py` 只負責顯示 J19.6 的量級。因 J19.5 極粗，其 t=5,10 上界大於 1；從 t=20 起 mass 上界小於 `10^-13`，t=50 時小於 `10^-133`。這些十進位值不是證明的一部分。

## J20（已證）：log-u mode、曲率與參數敏感度

在 `x=logu` 中寫

`F_t(x)=(2t+1)x+L(e^x)`，`t≥1`。

J19 的左尾粗界保證 `F_t'>0` 於 `u≤δ`；在 `u≥δ`，J19.3 給 `F_t''<0`，而 `F_t'→-∞`。所以存在唯一 mode `x_t=logβ_t`，且

`2t+1+β_tL'(β_t)=0`。  (J20.1)

利用 `2<h(r)<4`，其中 `r=πe^(2β_t)`，可得

`(2t+1)/(2β_t)+9/4<r<(2t+1)/(2β_t)+13/4`。  (J20.2)

置 mode 曲率 `Λ_t=-F_t''(x_t)`。精確地

`Λ_t=2t+1-β_t²L''(β_t)`，  (J20.3)

而 J20.2 與 `0<24r/(2r-3)²<8` 給

`(2t+1)(1+2β_t)<Λ_t`

`<(2t+1)(1+2β_t)+21β_t²`。  (J20.4)

mode 對參數的敏感度也有精確閉式。對 J20.1 隱微分，

`dx_t/dt=2/Λ_t`。  (J20.5)

若 `B_(3,t)=F_t'''(x_t)`，則再微分曲率得

`dΛ_t/dt=-2B_(3,t)/Λ_t`。  (J20.6)

這兩式解釋 J17 cumulants 的正確局部尺度，而不需要先猜 Lambert-W 展開。

## J21（候選展開；餘項未證）：第一個局部 cumulant 修正

Euler 微分算子 `(u d/du)^j` 給 mode 處

`B_3=βL'+3β²L''+β³L'''`，

`B_4=βL'+7β²L''+6β³L'''+β⁴L''''`，  (J21.1)

其中

`L'''=-8r+48r(2r+3)/(2r-3)³`，

`L''''=-16r-96r(4r²+24r+9)/(2r-3)^4`。  (J21.2)

把 `F_t(x_t+y)` 展開並對標準 Gaussian 偶矩逐項積分，形式上得到

`Var_t(X)=1/Λ+B_4/(2Λ³)+B_3²/Λ⁴+Rem_2(t)`，  (J21.3)

`κ_(3,t)(X)=B_3/Λ³+Rem_3(t)`。  (J21.4)

前三項的係數可直接核對：未中心化二階矩的修正為
`5B_4/(8Λ³)+35B_3²/(24Λ⁴)`，扣掉 normalization 修正與 mean 平方後正好成 J21.3。

若能證一致界 `Rem_2=O(t^-3 polylog(t))`，並對其 t 差分保持同階結構，則由 `D_k=a''(k)+a''''(k)/12+...` 可得

`D_k=4[1/Λ_k+B_(4,k)/(2Λ_k³)+B_(3,k)²/Λ_k⁴]`

` +O(k^-3 polylog(k))`。  (J21.5)

相應的可計算候選是

`Ĉ_k=1-p_k exp{4[1/Λ_k+B_(4,k)/(2Λ_k³)+B_(3,k)²/Λ_k⁴]}`。  (J21.6)

離線 quadrature 顯示 `Ĉ_k/C_k-1` 在 k=50,100,199 分別約為
`3.07×10^-4, 7.30×10^-5, 1.81×10^-5`；乘 k² 後為
`0.768,0.730,0.719`。這支持但不證明 J21.5 的餘項尺度。要完成大 k J12，仍須以 J19 的尾界和 Taylor 積分餘項證出顯式常數，而不是引用此擬合。

## J22（已證）：任意階 u-導數的顯式 majorant

J21 所需的高階餘項可由一個收斂展開統一控制。因

`L'=9/2+6/(2r-3)-2r`，`r=πe^(2u)`，

且 `z=3/(2r)<1/2`，對每個 `j≥2` 有精確級數

`L^(j)(u)=-2^j r`

` +(-1)^(j-1)(3·2^(j-1)/r)Σ_(m≥0)(m+1)^(j-1)z^m`。  (J22.1)

證明只需展開

`6/(2r-3)=(3/r)Σ_(m≥0)z^m`

並反覆使用 `d/du=2r d/dr`；因 z<1/2，逐項微分在每個 `u≥0` 的閉子區間一致合法。

由 `3/r<1` 得

`|L^(j)+2^j r|`

`<2^(j-1)Σ_(m≥0)(m+1)^(j-1)/2^m`。  (J22.2)

對 `j=2,...,7`，右側依序為

`8, 48, 416, 4800, 69248, 1198848`。  (J22.3)

再用 `(u d/du)^jL=Σ_(ℓ=1)^j S(j,ℓ)u^ℓL^(ℓ)`，其中 `S(j,ℓ)` 是第二類 Stirling 數，即可把任意固定階的 x-Taylor remainder 化為 β、window 寬度與 r 的顯式初等上界。J22 尚未選定最終 window 或完成積分 remainder，但移除了「高階導數無 majorant」的缺口。

## J23（已證）：主區域曲率嚴格遞增

對 `F_t(x)=(2t+1)x+L(e^x)`，線性 tilt 不影響三階導數，且

`F_t'''(x)=uL'+3u²L''+u³L'''`。  (J23.1)

若 `δ≤u≤1/4`，J19.2、`L''<-12` 及 J22 的 `L'''<48` 給

`F_t'''<u/20-48u²+48u³`

`=u(1/20-48u+48u²)<0`；括號在此區間遞減，且於 `u=δ` 已為負。

若 `u≥1/4`，則 `r>4`。此時

`(2r-3)³>6(2r+3)`，

因 r=4 時 `125>66`，且兩側之差的導數 `6(2r-3)²-12>0`。配合 J21.2 得 `L'''<0`；而 `L',L''<0`，所以 J23.1 仍嚴格為負。故

`F_t'''(x)<0  (u≥δ)`。  (J23.2)

因此主區域的負勢能曲率 `-F_t''` 隨 x 嚴格增加，且 J20.6 給 `Λ_t'>0`。這為 mode 左右兩側建立非對稱 concentration bound 提供符號結構。注意：J23.2 本身尚未證 tilted 分布的精確第三 cumulant 必為負；若使用該結論，仍須補一個積分比較引理。

## J24（已證漸近 window 引理；顯式門檻未算）：尾部可超多項式隔離

令 `x_t=logβ_t`、`Q(x)=-F_t''(x)`，並對某個 `w>0` 置

`M_3(t,w)=sup_(|x-x_t|≤w)|F_t'''(x)|`。

若 `x_t-w≥logδ` 且

`M_3(t,w)w≤Λ_t/2`，  (J24.1)

則 window 內 `Q≥Λ_t/2`。由 J23 的 Q 遞增性，右側其實有 `Q≥Λ_t`。兩次積分給

`F_t(x_t+y)-F_t(x_t)≤-Λ_ty²/2  (y≥0)`，  (J24.2)

`F_t(x_t+y)-F_t(x_t)≤-Λ_ty²/4  (-w≤y≤0)`。  (J24.3)

在 `a=x_t-w`，又有 `F_t'(a)≥Λ_tw/2`。凹函數位於任一切線下方，故主區域更遠的左尾滿足

`∫_(logδ)^(x_t-w)e^[F_t(x)-F_t(x_t)]dx`

`≤2e^(-Λ_tw²/4)/(Λ_tw)`。  (J24.4)

右尾用 Gaussian tail bound 得

`∫_(x_t+w)^∞e^[F_t(x)-F_t(x_t)]dx`

`≤e^(-Λ_tw²/2)/(Λ_tw)`。  (J24.5)

現在選

`w_t=logt/sqrt(Λ_t)`。  (J24.6)

J20.2 易給 `β_t=O(logt)`、`r(β_t)=O(t)`；J20.4 給 `Λ_t≥2t+1`。在 J24.6 的 window 中 `u/β_t=exp[O(logt/sqrt t)]`，所以 J22 對任意固定 j 給

`M_j(t,w_t)=O(t(logt)^(j-1))`。  (J24.7)

特別地，`M_3w_t/Λ_t→0`，故 J24.1 對充分大 t 成立；而 j 階標準化 Taylor 項在 window 邊界至多

`M_jw_t^j=O(t^(1-j/2)(logt)^(2j-1))`。  (J24.8)

J24.4–J24.6 的兩個 tail 因子分別成為
`exp[-(logt)²/4]` 與 `exp[-(logt)²/2]`，比任意 t 的負冪更快衰減。加上 J19 的 `u<δ` 尾，這嚴格證明可在一個局部 window 內完成任意固定階 Laplace 展開。

J24 尚未把「充分大」換成可供有限區間證書接合的數字，也尚未展開並 enclosure 六階 Gaussian 多項式的全部交叉項。這兩項是把 J21.5 從形式展開升格為定量定理的剩餘工作。

## J25（已證代數部分；解析 enclosure 未閉合）：六階 Gaussian 交叉項

在 J24 的 window 內置 `z=sqrt(Λ_t)(x-x_t)`，並記

`A_j=B_(j,t)/(j! Λ_t^(j/2))`，`3≤j≤6`。  (J25.1)

先忽略七階 Taylor 餘項，局部密度相對標準 Gaussian 的因子是

`exp(A_3z^3+A_4z^4+A_5z^5+A_6z^6)`。  (J25.2)

給 `A_j` 指派 weight `j-2`，把指數展開至總 weight 4，並以標準
Gaussian 偶矩 `E Z^(2m)=(2m-1)!!` 積分。精確結果如下：

`N/sqrt(2π)=1+(3A_4+15A_3^2/2)`

` +(15A_6+105A_4^2/2+105A_3A_5+945A_3^2A_4/2+3465A_3^4/8)+R_N`。  (J25.3)

標準化變數的 mean 為

`E Z=3A_3+(15A_5+96A_3A_4+135A_3^3)+R_1`，  (J25.4)

raw second moment 為

`E Z^2=1+(12A_4+45A_3^2)`

` +(90A_6+384A_4^2+840A_3A_5+4500A_3^2A_4+4860A_3^4)+R_2`。  (J25.5)

在 normalization division 與 mean-square subtraction 後，所有交叉項精確化簡成

`Var(Z)=1+12A_4+36A_3^2`

` +90A_6+384A_4^2+750A_3A_5+3924A_3^2A_4+4050A_3^4+R_V`。  (J25.6)

所以 `X=x_t+Z/sqrtΛ_t` 的六階局部候選 enclosure 中心是

`Var(X)=1/Λ+B_4/(2Λ^3)+B_3^2/Λ^4`

` +B_6/(8Λ^4)+(2/3)B_4^2/Λ^5+(25/24)B_3B_5/Λ^5`

` +(109/24)B_3^2B_4/Λ^6+(25/8)B_3^4/Λ^7+R_V/Λ`。  (J25.7)

這不只重得 J21.3，也指出其未顯示的下一階完整多項式。係數由
`experiments/verify_sixth_order_gaussian.py` 以 `Fraction` 多項式環獨立生成；不使用浮點或外部 CAS，並精確斷言 J21 的 weight-2 係數。

一個可直接用於 enclosure 的餘項參數如下。置 `ell=log t`，

`theta=max_(3≤j≤6)(|A_j|ell^j)^(1/(j-2))`，

`rho=M_7(t,w_t)ell^7/(7!Λ_t^(7/2))`。  (J25.8)

若 `theta≤1/2`、`rho≤1/2`，則在 `|z|≤ell` 上，J25.2 與其
weight≤4 截斷的逐點差至多

`88 theta^5+5rho`。  (J25.9)

證明：各 monomial 的絕對值以 `theta^weight` 控制；正係數生成函數
`exp(s+s^2+s^3+s^4)` 在 `s=1/2` 小於 `e`，故 weight≥5 的尾小於
`32e theta^5<88theta^5`。Taylor 七階餘項改變指數至多 rho，而
`|e^(P+R)-e^P|≤e^(|P|+rho)rho<5rho`。這已把局部解析餘項縮成
`B_3,...,B_6,M_7,Λ_t` 的有限顯式不等式；仍須加上截斷 Gaussian
多項式尾、J24 的外尾及 J19 左尾，並把粗導數常數代入以算出數字門檻。

重要層級限制：J25 即使完成 J12，也只證全部 shifted degree-3 Jensen
多項式 hyperbolic。從 degree 3 到任意 degree 尚無轉換引理；完整 RH
仍需逐階 enclosure 或一個統一的全階 Hankel/Jensen 結構定理。

## J26（已證粗門檻；尚非 J12 接合門檻）：`t≥10^24` 的局部條件

J24.1 與 J25.8 可以先用很粗但完全顯式的常數封閉。令
`T_0=10^24`。只用初等界 `2<log10<12/5`；後者例如由
`e^(12/5)>Σ_(m=0)^5(12/5)^m/m!>10`
得到。因此在 `t=T_0` 有 `48<logt<58`，且以下出現的
`(logt)^m/sqrt(t)` 或 `(logt)^m/t^(5/2)` 對 `t≥T_0` 單調下降。

先證 mode 的粗幾何。對 `t≥36`，`F_t'(log1)>2t+1-2πe^2>0`，故
`β_t>1`。J20.2 遂給 `r(β_t)<t+4`，並由
`3e^(2β_t)<r(β_t)<t+4<3t` 得 `2β_t<logt`。又

`w_t≤logt/sqrt(2t)`。  (J26.1)

在 `T_0` 右側，J26.1 給 `w_t<1/2` 及
`2(logt)^2/sqrt(2t)<1/2`。用 `e^w≤1+2w` (`0≤w≤1/2`) 可得
window 內 `u<logt`，並且

`r(u)/r(β_t)=exp[2(u-β_t)]<2`，故 `r(u)<3t`。  (J26.2)

令 J22.2 的常數對 `L',...,L^(7)` 依序取
`7,8,48,416,4800,69248,1198848`。由 Stirling 展開
`(u d/du)^jL=ΣS(j,l)u^lL^(l)` 與 J26.2，直接求和給

`M_3≤67t(logt)^3`, `M_4≤283t(logt)^4`,

`M_5≤1363t(logt)^5`, `M_6≤7291t(logt)^6`,

`M_7≤42646t(logt)^7`.  (J26.3)

例如主係數 `Σ_l S(j,l)2^l` 對 `j=3,...,7` 是
`22,94,454,2430,14214`；把 J22 誤差常數加入後，上述整數均向上取整。
利用 `Λ_t≥2t`，J26.3 導出

`theta_3≤6(logt)^6/sqrt(t)`，

`theta_j≤2(logt)^4/sqrt(t)` (`j=4,5,6`)，  (J26.4)

其中對 `j=5,6` 又用了 `logt>1`。在端點以 `logT_0<58` 代入，
`6·58^6/10^12<1/2`；其餘更小，所以 `theta<1/2`。同理

`M_3w_t/Λ_t≤34(logt)^4/sqrt(t)<1/2`,  (J26.5)

以及

`rho≤(logt)^14/t^(5/2)<1/2`.  (J26.6)

此處係數小於 1 使用了 `sqrt2>7/5`；沒有隱含十進位近似。

故 `t≥10^24` 時，J24.1、J25.8 與 J25.9 全部無條件成立。所有端點
整數不等式由 `experiments/verify_j25_crude_threshold.py` 精確核對。

這個 `T_0` 只是一個「局部 Laplace 代數合法」門檻，不是 J17 corridor
或 J12 的完成門檻。它太大，無法作為實用的有限區間證書接點；仍需
保留 mode 的精確 `r≈t/β` 尺度、以 Gaussian 加權而非 window supremum
估計餘項，才能把門檻大幅下降。

## J27（已證）：window 截斷與主區域外尾的前三矩顯式界

J25 的局部多項式是以整條 Gaussian 積分計算，故還須控制把
`|z|≤ell` 換成 `z∈R` 的誤差。令 `S_4(z)` 是 J25.2 的 weight≤4
截斷。當 `ell≥48`、`theta≤1/2` 時，對 `q=0,1,2,3` 有

`E[1_(|Z|>ell)|Z|^q |S_4(Z)|]`

`≤6 ell^(q-1)exp(-ell^2/2)`.  (J27.1)

證明：`S_4` 每個 monomial 的 degree 至多 12，且在 `|z|=ell`
的絕對係數和小於 `exp(theta+theta²+theta³+theta⁴)<3`。反覆分部積分給

`∫_ell^∞z^m e^(-z²/2)dz≤2ell^(m-1)e^(-ell²/2)`

（`m≤15`、`ell²≥4(m-1)`）；逐 monomial 相加即得 J27.1。

J24 的真密度主區域外尾也可連同前三個 mode-centered moments 控制。
以 mode 高度與 Gaussian normalization `e^(F_t(x_t))sqrt(2π/Λ_t)`
為單位，右尾 `z≥ell` 滿足

`R_q≤ell^(q-1)e^(-ell²/2)`, `0≤q≤3`.  (J27.2)

對左側 `logδ≤x≤x_t-w_t`，在切點使用斜率
`F_t'(x_t-w_t)≥sqrtΛ_t ell/2`。置 `v=sqrtΛ_t(x_t-w_t-x)`，直接積分
`(ell+v)^q exp(-ell v/2)` 得

`L_0≤ell^(-1)e^(-ell²/4)`,

`L_1≤(1+2/ell²)e^(-ell²/4)`,

`L_2≤(ell+4/ell+8/ell³)e^(-ell²/4)`,

`L_3≤(ell²+6+24/ell²+48/ell⁴)e^(-ell²/4)`.  (J27.3)

J27.1–J27.3 是解析界，不是數值擬合；在 J26 的 `ell=logt` 下皆
超多項式小。剩下 `u<δ` 的部分由 J19.6 直接控制其 `|X|^m` raw
moments。尚未完成的 bookkeeping 是把三種誤差在同一 normalization
下傳遞到 variance、third cumulant，再與 J17.5–J17.6 的 margin 比較。

## J28（已證）：共同 normalization 的 variance／第三累積量傳播引理

先只看主區域 `u≥δ`。以 mode Gaussian 為單位，令真實的未正規化
`z`-moments 為 `J_q` (`0≤q≤3`)，J25 的 weight≤4 多項式在整條
Gaussian 下的 moments 為 `P_q`。`P_q` 是 `A_3,...,A_6` 的顯式有限
多項式；`experiments/verify_sixth_order_gaussian.py` 已全部列出。

置 `E=88theta^5+5rho`，`g=(1,1,1,2)`，並以 J27 的右端分別記
Gaussian polynomial tail `G_q`、真右尾 `R_q`、真左尾 `L_q`。則

`|J_q-P_q|≤epsilon_q:=g_q E+G_q+R_q+L_q`.  (J28.1)

這只使用 triangle inequality；各項皆已有顯式公式。若
`c=P_0-epsilon_0>0`，定義

`b_q=P_q/P_0`,

`d_q=epsilon_q/c+|P_q|epsilon_0/c^2`.  (J28.2)

則真 normalized raw moments `r_q=J_q/J_0` 滿足

`|r_q-b_q|≤d_q`.  (J28.3)

證明是精確恒等式
`J_q/J_0-P_q/P_0=[(J_q-P_q)P_0-P_q(J_0-P_0)]/(J_0P_0)`。
因此主區域 variance 有可直接計算的 enclosure

`|[r_2-r_1^2]-[b_2-b_1^2]|`

`≤d_2+d_1(2|b_1|+d_1)`.  (J28.4)

第三 cumulant 亦有

`|[r_3-3r_2r_1+2r_1^3]-[b_3-3b_2b_1+2b_1^3]|`

`≤d_3+3[d_2(|b_1|+d_1)+|b_2|d_1]`

` +2d_1[(|b_1|+d_1)^2+(|b_1|+d_1)|b_1|+|b_1|^2]`.  (J28.5)

J28.4–J28.5 完成了 J27 所缺的共同 normalization bookkeeping，且
沒有從 `F'''<0` 猜測 cumulant 符號。尚餘兩步：(i) 用 J19.6 把
`u<δ` 作為極小 mixture perturbation 加回；(ii) 將所得 t-連續 bounds
在 J17 的 triangular averages 上積分並比較 corridor margin。粗
`T_0=10^24` 下所有 epsilon 超多項式小，但中心多項式本身的 corridor
符號仍須解析核對，不能只憑誤差很小宣告 J12。

## J29（已證）：J19 極左尾的 mixture cumulant 傳播

令 `h_m(t)` 表示 J19.6 對
`E_t[1_(u≤δ)|X|^m]` 的顯式右端，故左尾質量 `p≤h_0`。J28 的主區域
normalized `z`-raw moments 記為 `r_q`，並置 `B_q=|b_q|+d_q`。
因 `z=sqrtΛ_t(X-x_t)`，左尾對 full distribution 的絕對 raw
`z`-moment 貢獻至多

`H_1=sqrtΛ(h_1+|x_t|h_0)`,

`H_2=2Λ(h_2+|x_t|²h_0)`,

`H_3=4Λ^(3/2)(h_3+|x_t|³h_0)`.  (J29.1)

full distribution 是質量 `1-p` 的主區域 conditional law 與質量 p 的
左尾 conditional law 的 mixture。因此 full raw moment `s_q` 滿足

`|s_q-r_q|≤eta_q:=h_0B_q+H_q`, `q=1,2,3`.  (J29.2)

這立即給 mixture 對 variance 的額外誤差

`eta_2+eta_1(2B_1+eta_1)`,  (J29.3)

而第三 cumulant 的額外誤差至多

`eta_3+3[eta_2(B_1+eta_1)+B_2eta_1]`

` +2eta_1[(B_1+eta_1)^2+(B_1+eta_1)B_1+B_1^2]`.  (J29.4)

證明與 J28 的差平方、差立方恒等式相同。J19.6 含 `δ^(2t+1)`，而
J26 只給 Λ、`|x_t|` 多項式／對數級上界，所以 J29.3–J29.4 在
`t≥T_0` 遠小於任意負冪。

至此六階局部展開的 normalization、左右主尾、Gaussian truncation、
Taylor remainder 與極左尾都已各自傳到 variance／third cumulant 的
顯式 enclosure。尚未閉合的是中心式的 t-依賴符號：必須把 J25/J28
中心值及誤差在 J17.3–J17.4 的 triangular kernels 上界積分，證出
J17.5–J17.6；這是下一個實質而非 bookkeeping 的缺口。

## J30（已證）：`t≥10^30` 時第三累積量嚴格為負

J25 的 window-supremum remainder 對符號過粗；改以 bookkeeping 參數
`s` 寫

`g(s,z)=sA_3z³+s²A_4z⁴+s³A_5z⁵+s⁴A_6z⁶`。

對 `e^g` 在 `s=0` 作四階 Taylor。若
`H_m(z)=Σ_(j=3)^6 (j-2)_m |A_j||z|^j`，五階導數的 Bell bound 是

`e^|g|[H_1^5+10H_1³H_2+15H_1H_2²+10H_1²H_3`

`       +10H_2H_3+5H_1H_4]`.  (J30.1)

在 J26 window 內 `|g|≤15/16`，故把 J30.1 乘標準 Gaussian 後積分，
局部 weight remainder 對第 q raw moment (`0≤q≤3`) 至多

`(1/40) E[|Z|^q B_5(H_1,...,H_4)]`

` +[5M_7/(7!Λ^(7/2))]E|Z|^(q+7)`.  (J30.2)

這是固定 Gaussian moments 的有限式，移除了 J25.9 不必要的
`(logt)^30` window 損失。

現在取 `T_*=10^30`。在 `t=T_*` 有 `60<logt<72`。J26.3 與
`Λ≥2t` 給

`|A_3|≤6(logt)^3/sqrt(t)`, `|A_4|≤3(logt)^4/t`,

`|A_5|≤3(logt)^5/t^(3/2)`, `|A_6|≤2(logt)^6/t²`.  (J30.3)

另一方面 mode 恒等式與 J23 給

`B_3=βL'+3β²L''+β³L'''≤βL'=-(2t+1)`.  (J30.4)

由 J20.4、`β<(logt)/2` 可粗取 `Λ<4tlogt`，所以

`-6A_3=-B_3/Λ^(3/2)≥1/[4sqrt(t)(logt)²]`.  (J30.5)

令 `P_q` 為 J28 的四個 exact Gaussian 多項式。其 normalized 第三
cumulant 的分子是

`K=P_3P_0²-3P_2P_1P_0+2P_1³=6A_3+K_rem`.  (J30.6)

exact polynomial expansion 有 64 個非主 monomials，全部 weight 至少
3。以 J30.3 逐項取絕對值，在 `t=T_*, logt<72` 得

`|K_rem|/[1/(4sqrt(t)(logt)²)]<0.000233`.  (J30.7)

每個比率形如 `C(logt)^d/t^((w-1)/2)`；64 項所需的最大單調門檻僅
`logt>11`，所以端點核對即覆蓋所有 `t≥T_*`。J30.2、J27、J28 的
共同 normalization 誤差與主負項之比在端點小於 `1.2·10^-18`，之後
同樣單調下降。

最後，J19.6 的固定常數可粗界為 `2·10^160`：由
`T_1(0)/T_1(2)<exp[π(e^4-1)]<e^320<10^160`。因此其 `m≤3` 左尾
moments 在 `t≥T_*` 小於 `t^-100`，J29 的 cumulant mixture 誤差小於
`t^-80`，仍遠小於 J30.5。綜合得

`κ_(3,t)(logu)<0`, `t≥10^30`.  (J30.8)

所有多項式生成、Bell-Gaussian moment 上界及端點有理比較由
`experiments/verify_j30_kappa_threshold.py` 以 `Fraction` 核對；輸出
的兩個關鍵比率是 `2.32671·10^-4` 與 `1.18415·10^-18`。十進位輸出
只展示 exact inequality 的量級。

J30.8 經 J17.4 可推出 `D_(k+1)-D_k<0`（`k≥10^30+1`），但這只給
方向。J17.6 的下界還要求負量不能太大；三角核雖保存點態負號，仍
可能平滑掉所需的精確 magnitude。故不得把 J30 直接宣告為 J12。

## J31（已證）：第一 theta 項對所有 `k≥10^30+2` 滿足 J12

先把 J30 加強為雙側 magnitude bound。由 J20.2，若 `β_t≤10`，則
`t/10<r(β_t)≤4e^20<4·3^20`，與 `t≥10^30` 矛盾；故 `β_t>10`。
利用 J21.1、J22 與 mode 方程，

`|B_3|≤(2t+1)(1+6β+4β²)+63β²+74β³`.  (J31.1)

而 `Λ>(2t+1)(1+2β)`。對 `β≥10`，初等多項式比較給

`(1+6β+4β²)/(1+2β)^3≤1/20`,

`(63β²+74β³)/(1+2β)^3≤11`.  (J31.2)

J30 的 exact numerator audit 其實還給
`|κ_3-B_3/Λ³|≤10^-3|B_3|/Λ³`；其中 normalization 對主項的額外
比率小於 `3.15·10^-5`，已包含在 `10^-3`。由 J31.1–J31.2，

`|κ_(3,t)(X)|≤(1001/1000)[1/(20(2t+1)²)+11/(2t+1)³]`

`<1/(64t²)`, `t≥10^30`.  (J31.3)

variance 更容易。J30 的四個 exact raw-moment enclosures給
`E[(sqrtΛ(X-x_t))²]<21/20`；端點 Fraction audit 後所有誤差單調下降。
配合 `Λ>(2t+1)(1+2β)>42t`，

`Var_t(X)<1/(40t)`.  (J31.4)

驗證器 `experiments/verify_j31_variance_threshold.py` 核對 J31.4 的
endpoint arithmetic；輸出的 `1.0000000000000002` 是 exact rational
上界轉成 float 的展示，不是用 float 證明。

現在令 `k≥10^30+2`。J17.3、J31.4 及 triangular kernel 質量為 1 給

`0<D_k<1/[10(k-1)]`.  (J31.5)

因 `p_k>11/12` 且
`1/[10(k-1)]<2/(2k+1)≤-logp_k`，J17.5 成立。再由 J17.4、J30.8、
J31.3，

`-1/[8(k-1)²]<D_(k+1)-D_k<0`.  (J31.6)

另一方面

`log[p_(k+1)/p_k]=log[1+4/((2k-1)(2k+3))]`

`≥4/(2k+1)²≥1/[8(k-1)²]`,  (J31.7)

所以 J17.6 的下界成立。

為處理上界，J31.5 與 `e^x≤1+2x` (`0≤x≤1/2`) 給

`C_k=1-p_ke^(D_k)≥2/(2k+1)-1/[5(k-1)]≥1/(2k)`.  (J31.8)

置 `R=1-C_k`。因

`(4R²-7R+4)/R=1+4C_k²/R`

且 `C_k²/R>C_k²≥1/(4k²)>1/[(2k-1)(2k+3)]`，J17.6 的右端嚴格
為正；J31.6 的差為負，故上界亦成立。J17.5 還給 `0<C_k<1/12`。
因此第一 theta 項的全部 J12.2 條件對 `k≥10^30+2` 已證明。

J31 仍不是完整 Φ 的 degree-3 定理：J14 的 theta-tail 雖為超多項式
小，尚須把其 log-moment 二階差分擾動用顯式常數壓到 J31 corridor
margin 以下。有限 `k<10^30+2` 更完全未由區間證書覆蓋。

## J32（已證）：完整 Xi 核對所有 `k≥10^30+2` 滿足 J12

令完整偶矩為 `M_k=A_k(1+epsilon_k)`，其中 `A_k` 是第一 theta 項，
`epsilon_k=R_k/A_k≥0`。J14.3 給

`epsilon_k≤2sqrt(k)e^[-2klog2/logk]`

` +(16π/c_0)k⁴(logk)^(2k)e^(-πk²)`.  (J32.1)

在 `k≥10^30`，第一項小於 `k^-100`：使用 `log2>1/2`，只須核對
`k/logk>(201/2)logk+log2`，端點由 `logk<72` 顯然成立，之後左減右
的導數為正。對第二項，

`16π/c_0<10^164`  (J32.2)

可由 J30 對 `1/c_0` 的同一 `e^320<10^160` 粗界得到；而
`2kloglogk-πk²<-2k²`。端點核對
`2k²>164log10+104logk` 後差值遞增，所以第二項亦小於 `k^-100`。
因此

`0≤epsilon_k≤2k^-100`, `k≥10^30`.  (J32.3)

置 `b_k=log(1+epsilon_k)`。對 `k≥K:=10^30+2`，相鄰索引的
`b_j≤4k^-100`，故完整與第一項的 log-moment 差分滿足

`|D_k^full-D_k^(1)|≤16k^-100`,

`|(D_(k+1)^full-D_k^full)-(D_(k+1)^(1)-D_k^(1))|≤32k^-100`.  (J32.4)

J31 各 corridor 具有多項式 margin。具體地，size upper margin 大於
`1/(2k)`，相鄰差 lower margin 大於 `1/(2k²)`。此外 J31.8 可加強為
`C_k^(1)≥3/(4k)`；J32.4 改變 C 不超過 `32k^-100`，所以

`C_k^full≥37/(50k)`.  (J32.5)

在 upper recurrence 中，J32.5、`R<1` 與 `log(1+x)≥x/2` 給

`log(1+4C²/R)-log(1+4/[(2k-1)(2k+3)])`

`≥119/(1250k²)>1/(20k²)`.  (J32.6)

J32.4 的擾動小於所有上述 margins。因此 J17.5–J17.6、等價地 J12.2，
對完整 Xi 核的每個 `k≥10^30+2` 成立。端點有理比較由
`experiments/verify_j32_tail_transfer.py` 核對。

結論只覆蓋 degree 3 的大 shift。要完成全部 shifted cubic Jensen，
仍需對 `1≤k<10^30+2` 建立區間證書或大幅降低解析門檻；而即使 cubic
全完成，degree 4 以上仍是獨立缺口。

## J33（已證強化）：完整 Xi 核的大-shift 門檻降至 `10^10+2`

J30 的 `10^30` 主要來自 window 上的粗界 `M_j≤K_jt(logt)^j`。在 mode
保留 J20.2 的 `r≈t/β` 可省去多餘的 log 次方。令

`C_j=Σ_(l=1)^j S(j,l)2^l`，故 `C_3,...,C_7` 為
`22,94,454,2430,14214`。mode 方程及 J22 給

`|B_j|≤2C_jtβ^(j-1)`, `3≤j≤7`, `t≥10^10`.  (J33.1)

證明：把 `l=1` 項改用 `βL'=-(2t+1)`，其餘用
`|L^(l)|≤2^lr+E_l` 與
`r<(2t+1)/(2β)+13/4`。主項係數恰不超過 `C_j/2`；J22 errors 與
`13/4` 項合計相對主項小於
`250β/t<1/4`，所以常數 2 有充分餘裕。

對 J24 window，`w≤logt/sqrtΛ`。在端點將於下證 `8<β<12`、
`Λ>34t`，所以 `2(u-β)<1/100`；由此同樣推得

`M_j(t,w)≤4C_jtβ^(j-1)`.  (J33.2)

特別地 J24.1 的左端至多
`88tβ²(logt)/Λ^(3/2)<1/2`，不再需要 J26 的天文門檻。

現在取 `T=10^10`，則 `20<logT<24`。若 `β≤8`，J20.2 會給
`T<32·3^16`，矛盾；故 `β>8`，而 J26 的舊上界仍給 `β<12`。
由 J33.1、`Λ>4tβ` 及 `sqrtβ<7/2`，得到 mode standardized bounds

`|A_3|≤77/(24·10^5)`,

`|A_4|≤47·12/(96·10^10)`,

`|A_5|≤227·12·7/(1920·10^15)`,

`|A_6|≤27·12²/(256·10^20)`.  (J33.3)

它們給 `Σ|A_j|(logT)^j<0.444<1/2`。把 J33.3 代入 J30 的 exact
64-term cumulant numerator、Bell remainder、J27–J29 errors，端點證書給

`|κ_3-B_3/Λ³|≤(1/50)|B_3|/Λ³`,

`E[(sqrtΛ(X-x_t))²]<101/100`.  (J33.4)

所有誤差／主項比皆為 `C(logt)^d/t^a` 且在 `logt>20` 後下降，故端點
覆蓋整個 `t≥T`。`experiments/verify_j33_improved_threshold.py` 用 exact
Fractions 核對；實際 enclosure 比率為 `0.012128`。

對 `β≥8`，J31.2 的第一個多項式界可換成

`(1+6β+4β²)/(1+2β)^3≤1/16`。

因此 J33.4 與 J31.1 給

`|κ_(3,t)|<1/(50t²)`, `Var_t(X)<3/(100t)`, `t≥10^10`.  (J33.5)

對 `k≥10^10+2`，J17 遂給

`0<D_k<3/[25(k-1)]`,

`-4/[25(k-1)²]<D_(k+1)-D_k<0`.  (J33.6)

與 J31 相同的有理比較證 J17.5–J17.6；此時仍有較強的
`C_k≥3/(4k)`。J14 tail transfer 在新端點也成立：J32.1 的第一、二項
仍各小於 `k^-100`。更新後的
`experiments/verify_j32_tail_transfer.py` 已核對新接點的 margins。

故完整 Xi 核對所有 `k≥10^10+2` 滿足 J12。有限證書範圍由
`10^30` 降至 `10^10`，仍遠超實用規模；下一步須使用精確 mode
rational bounds、較高階 Gaussian 展開或參數區間分塊繼續降低。

## J34（已證強化）：改用 sqrt-log window，門檻降至 `10^8+2`

J24 的 `ell=logt` 是為取得超多項式尾而選，對 J12 並非必要。只要尾
小於 `t^-2` 就已遠低於 `1/t`、`1/t²` corridor margins。改取

`ell_t=sqrt(8logt)`, `w_t=ell_t/sqrtΛ_t`.  (J34.1)

則 J24 左、右尾分別為 `t^-2`、`t^-4`，而 cubic perturbation 在 window
邊界由 `A_3(logt)^3` 降為 `A_3(8logt)^(3/2)`。

取 `T=10^8`。有 `16<logT<20`、`ell_T<13`。若 `β≤6`，J20.2 導出
`T<24·3^12`，矛盾；所以 `6<β<10`，`Λ>26t`。J33.1 給新的 endpoint
bounds

`|A_3|≤44/(15·10^4)`, `|A_4|≤47·10/(96·10^8)`,

`|A_5|≤227·32/(960·10^12)`, `|A_6|≤27·10²/(256·10^16)`.  (J34.2)

J34.2 在 `ell=13` 給 `Σ|A_j|ell^j<0.646<15/16`。window 內的 improved
`M_3≤88tβ²` 又給 `M_3w/Λ<1/2`，故 J24 curvature 與 J30 Bell bound
仍合法。注意七階 Taylor 項仍以 `logt<20` 控制 derivative majorant；
驗證器沒有把 `ell<13` 錯當成 u-derivative 的 log bound。

J30–J29 全部誤差在新端點的 exact audit 給

`|κ_3-B_3/Λ³|<(1/5)|B_3|/Λ³`,

`E[(sqrtΛ(X-x_t))²]<101/100`.  (J34.3)

對 `β≥6`，
`(1+6β+4β²)/(1+2β)^3≤1/12`。因此

`|κ_(3,t)|<1/(32t²)`, `Var_t(X)<1/(25t)`, `t≥10^8`.  (J34.4)

令 `k≥10^8+2`。J17 給

`0<D_k<4/[25(k-1)]`,

`-1/[4(k-1)²]<D_(k+1)-D_k<0`.  (J34.5)

因 D 已小於 `1/100`，可用 `e^D≤1+(51/50)D`，從而

`C_k≥2/(2k+1)-102/[625(k-1)]≥4/(5k)`.  (J34.6)

J17.5–J17.6 的 lower margins 仍為正；upper margin 由 J34.6 至少給
`7/(25k²)`。J14 tail 的 `k^-100` transfer 在 `10^8` 端點依然成立。
故完整 Xi 核對所有 `k≥10^8+2` 滿足 J12。

`experiments/verify_j34_sqrtlog_window.py` 與更新後的 J32 verifier 均以
exact arithmetic 通過；cumulant error／主項的實際粗上界為 0.185718。
剩餘前段約一億個 shift，仍不能逐項暴力驗證。

## J35（已證強化）：window 內改進 `M_7`，門檻降至 `10^7+2`

J34 的七階 Taylor remainder 仍沿用舊 `42646t(logt)^7`。在同一
sqrt-log window 內可直接使用 J33.2：

`M_7≤4C_7tβ^6`, `C_7=14214`.  (J35.1)

取 `T=10^7`、`ell=sqrt(6logt)`。端點有 `14<logT<17`、`ell<11`。
若 `β≤5` 則 `T<20·3^10`，矛盾，故 `5<β<9`、`Λ>22t`。
J33.1 給

`|A_3|≤33/(12·3162)`, `|A_4|≤47·9/(96·10^7)`,

`|A_5|≤227·27/(960·3162·10^7)`,

`|A_6|≤27·9²/(256·10^14)`.  (J35.2)

此處 `3162<sqrt(10^7)`，所以所有方向均為安全外界。J35.2 在
`ell=11` 給 exponent bound `q<1.165<6/5`；由 `e^(6/5)<4`，J30.2 的
Bell prefactor 從 `1/40` 改成 `1/30`。七階項則用 J35.1 與
`Λ^(7/2)>22³·4·t³sqrt(t)`。

exact endpoint audit 得

`|κ_3-B_3/Λ³|<(1/2)|B_3|/Λ³`,

`E[(sqrtΛ(X-x_t))²]<101/100`.  (J35.3)

對 `β≥5`，J31.2 的主比率小於 `1/10`。所以可取保守界

`|κ_(3,t)|<1/(25t²)`, `Var_t(X)<1/(20t)`, `t≥10^7`.  (J35.4)

J17 因而給

`0<D_k<1/[5(k-1)]`,

`-8/[25(k-1)²]<D_(k+1)-D_k<0`.  (J35.5)

`D<1/100` 允許 `e^D≤1+(51/50)D`，並推出

`C_k≥2/(2k+1)-51/[250(k-1)]≥3/(4k)`.  (J35.6)

其餘 J17 corridor 與 J14 transfer 的 margins 由更新後 J32 verifier
核對。因此完整 Xi 核對所有 `k≥10^7+2` 滿足 J12。

`experiments/verify_j35_mode_m7.py` 的 exact cumulant error ratio 為
0.442381，已接近六階 enclosure 的可用極限。若要再降數量級，直接
放寬同一粗界可能失去符號；較合理的下一步是加入 weight 6／8 的
Gaussian 項，或對 `10^2–10^7` 作少量 logarithmic t-block interval
enclosure，而非逐一驗證一千萬個 k。

## J36（已證強化）：利用 `A_3,...,A_6<0`，門檻降至 `10^6+2`

J35 對六階 cumulant 分子的 64 個非主 monomials 全取絕對值，仍丟失
大量符號。當 `t≥10^6` 時，mode 有 `β>4`。J21.2、J22 與
`r>t/(2β)` 證 `L',...,L^(6)<0`；所以

`A_3,A_4,A_5,A_6<0`.  (J36.1)

令 J30.6 的 `K_rem` 中某 monomial 為
`c A_3^aA_4^bA_5^cA_6^d`。其符號可精確由 coefficient 與總次數決定。
所有可能為正、且不含 A3 的 monomial 必含 A5。J33.1 與
`|B_3|≥2t` 給

`|A_5/A_3|=|B_5|/(20Λ|B_3|)≤908β³/(160t)`.  (J36.2)

因此可把每個正 monomial 除以 `|6A_3|` 後，以 J36.2 和其餘 Aj 的
上界逐項相加；不再把負修正誤算成風險。

取 `T=10^6`、`ell=sqrt(6logt)`，端點 `ell<10`、`4<β<8`、`Λ>18t`。
J35 的 mode-scale M7 與 Bell bound 仍適用；此時 exponent bound小於 3，
故使用 `e^3<27`。exact signed audit 得

`(K_rem 的正部)/|6A_3|<0.000365`,

`(K_rem 的絕對值和)/|6A_3|<0.030681`.  (J36.3)

共同 normalization、local Taylor、J27–J29 tails 對 cumulant 的誤差
小於主負項的 0.423493。故符號仍嚴格為負，且總 magnitude factor
小於 1.455。對 `β≥4`，J31.1 的主比率小於 `1/8`；可安全取

`|κ_(3,t)|<1/(16t²)`, `Var_t(X)<1/(17t)`, `t≥10^6`.  (J36.4)

此處 variance 使用 standardized 上界 `101/100` 與 `Λ>18t`。
J17 給

`0<D_k<4/[17(k-1)]`,

`-1/[2(k-1)²]<D_(k+1)-D_k<0`.  (J36.5)

因 D 極小，`e^D≤1+(51/50)D`，所以

`C_k≥2/(2k+1)-102/[425(k-1)]≥3/(4k)`.  (J36.6)

J17.5–J17.6 的 lower margin仍大於 `1/(3k²)`，upper margin由
J36.6 保持正；J14 tail transfer 亦已在新端點重跑。因此完整 Xi 核
對每個 `k≥10^6+2` 滿足 J12。

證書為 `experiments/verify_j36_signed_center.py`；它還程式化檢查每個
正 monomial 必含 A3 或 A5，避免人工漏項。有限 cubic 缺口現縮至約
一百萬個 shift；仍需 block certificate，不能以普通 quadrature
逐項掃描冒充證明。

## J37（候選工作介面，未證）：logarithmic t-block certificate

J36 以下不宜再用單一端點的全域 `β∈[4,8]`。可把
`[10²,10^6]` 分成窄 multiplicative blocks `[T,(1+η)T]`，在每塊：

1. 以 J20.1 的 score 單調性及 directed Decimal exp／Machin π，夾住
   兩端 mode `β_T,β_((1+η)T)`；
2. 用 exact Stirling 公式與 J22 對 `B_3,...,B_7,Λ` 作相關 enclosure，
   不再以獨立的全域 β 上界破壞 `A_5/A_3` 比率；
3. 選 block-specific `ell=sqrt(clogt)`，同時核對 J24.1、Bell error、
   `t^(-c/4)` 左尾及 J28–J29 normalization；
4. 直接輸出該 block 的 `κ_3<0`、magnitude 與 variance bounds，再由
   J17 積分。block 必須覆蓋連續 t，不能只驗整數 k。

有限精度診斷（只選參數，不是證書）顯示真 mode 下，`c=6` 時 exponent
bound q 在 `t=10³,10⁴,10⁵,10⁶` 約為 `3.08,1.58,0.75,0.33`；六階中心
cumulant／`6A_3` 則約為 `1.0030,1.00040,1.000050,1.000006`。這說明
block enclosure 從 `10^4` 向上有合理餘裕；`10²–10⁴` 可能需更高階
展開或直接 moment intervals。這些十進位值不得用來宣告任何 block
已證。

## J38（已證）：continuous-block 證書將完整 cubic 門檻降至 `k=10002`

`experiments/verify_j37_continuous_blocks.py` 已實作 J37。它不是整數點
掃描：以 1% multiplicative blocks 覆蓋全部實參數

`10000≤t≤10^7`.  (J38.1)

每個 block 對兩端 mode 方程作 100 次 directed Decimal bisection；π
使用 Machin 有理 enclosure，Decimal `exp/log/sqrt` 均以相鄰
representable number 向外擴張。mode 隨 t 單調，故兩端夾住 block
內全部 `β_t`。

在每塊中，證書重新計算：

- exact `Λ=2t+1-β²L''` interval；
- J22/Stirling 的 `B_3,...,B_7` 相關 upper bounds；
- signed 64-term center，其中正 monomials 以 block-specific
  `|A_5/A_3|` 控制；
- `ell=sqrt(7logt)` 的 J24 curvature、Bell fifth remainder、Taylor-7
  remainder、J27 tails、J28 normalization 與 J29 extreme-left allowance。

所有 denominator lower bounds 皆向下捨入，numerator/error upper bounds
皆向上捨入。694 個 blocks 全部嚴格通過。全區間共同結果為

`κ_(3,t)(logu)<0`,

`t²|κ_(3,t)(logu)|<0.037722<1/25`,

`t Var_t(logu)<0.064472<13/200`.  (J38.2)

三個最弱值均出現在第一 block `[10000,10100]`；其中 exponent bound
`q<2.025`，local error／negative center 小於 0.219。這些十進位數只是
directed inequalities 的顯示，證書內比較使用 70 位 outward Decimal。

J35 已對 `t≥10^7` 給更強的相容 bounds，故 J38.2 對所有
`t≥10000` 成立。令 `k≥10002`，J17 得

`0<D_k<13/[50(k-1)]`,

`-8/[25(k-1)²]<D_(k+1)-D_k<0`.  (J38.3)

J17.5 隨即成立。又 `D<1/100` 與 `e^D≤1+(51/50)D` 給

`C_k≥2/(2k+1)-663/[2500(k-1)]≥73/(100k)`.  (J38.4)

J38.3 的 lower-corridor margin大於 `1/(2k²)`。J14 在新端點仍給
`epsilon_k≤2k^-100`：directed check 證 `log(10002)<47/5`，足以驗證
第一 exponential；第二 double-exponential 更小。加回 theta tail 後

`C_k^full≥729/(1000k)`.  (J38.5)

由 J38.5、`log(1+x)≥x/2`，J17.6 upper margin 大於
`31441/(500000k²)>1/(20k²)`，遠大於 tail difference error。因此完整
Xi 核對所有 `k≥10002` 滿足 J12。

degree 3 現只缺 `1≤k≤10001`。這已可考慮直接 moment interval
certificate，但仍須 enclosure 積分與 theta tail；普通 SciPy 誤差估計
不能作為證明。

## J39（已證強化）：允許 `A_6` 未知符號，門檻降至 `k=3802`

J38 在較低 block 失敗的第一個原因是 J22 的粗界不再證 `L^(6)<0`。
這不必停止整個 signed-center 方法：`A_3,A_4,A_5<0` 已足夠，而含
`A_6` 的 monomial 可一律視為可能正貢獻。第三 cumulant 的奇 bookkeeping
weight 保證每個此類 monomial仍含 A3 或 A5，故可照 J36.2 相對主項
估計；驗證器以 assertion 程式化核對，沒有假設 A6 符號。

在 `[3800,4000]` 改用 0.1% blocks，其後仍用 1% blocks；總計 836 塊
覆蓋 `[3800,10^7]`。全部通過，最弱符號 block 為 `[3800,3804]`：

`local error/negative center<0.987944`.  (J39.1)

全區間 magnitude 的最弱 block仍是 `[4000,4040]`，給

`t²|κ_3|<0.044060<1/22`,

`t Var<0.071791<3/40`.  (J39.2)

與 J35 接合後 J39.2 對所有 `t≥3800` 成立。對 `k≥3802`，

`0<D_k<3/[10(k-1)]`,

`-4/[11(k-1)²]<D_(k+1)-D_k<0`.  (J39.3)

此時 `D<10^-4`，所以可用更貼近 1 的
`e^D≤1+(5001/5000)D`，得到 unperturbed `C_k≥69/(100k)`。J14 在此
端點用 `k^-20` 而非不必要的 `k^-100`：directed check 有
`log3802<42/5`、`3802>21(42/5)²`，故兩個 theta-tail 項各小於
`k^-20`。加回後 `C_k^full≥689/(1000k)`。

為 upper corridor，注意 `C<1/k`、`R>p`，所以
`x=4C²/R<5/k²<1/100`，並可用 `log(1+x)≥100x/101`。J39 的 lower C
使 upper margin 大於 `4/(5k²)`。更新後 J32 verifier 已核對全部有理
margins。因此完整 Xi 核對所有 `k≥3802` 滿足 J12。

現有 Bell-5 六階 enclosure 在 `[3800,3804]` 只剩約 1.2% 相對負
margin；直接再向下延伸不可靠。degree-3 finite gap 現為 `1≤k≤3801`。

## J40（已證代數；解析 enclosure 待完成）：顯式 weight-5 cumulant

為越過 J39 的 Bell-5 限制，加入

`A_7=B_7/(7!Λ^(7/2))`

並把 bookkeeping expansion 延伸至 weight 5。Exact Fraction algebra
給 standardized 第三 cumulant

`κ_3(Z)=6A_3`

` +(60A_5+504A_3A_4+864A_3³)`

` +(630A_7+6840A_4A_5+6660A_3A_6+42912A_3A_4²`

`   +42120A_3²A_5+206064A_3³A_4+170100A_3⁵)+R_7`.  (J40.1)

換回 `X=x_t+Z/sqrtΛ`，weight-5 行是

`B_7/(8Λ⁵)+(19/8)B_4B_5/Λ⁶+(37/24)B_3B_6/Λ⁶`

` +(149/12)B_3B_4²/Λ⁷+(39/4)B_3²B_5/Λ⁷`

` +(159/4)B_3³B_4/Λ⁸+(175/8)B_3⁵/Λ⁹`.  (J40.2)

`experiments/verify_weight5_gaussian.py` 獨立生成 J40.1，重驗 J21 的
weight 1／3 係數，並確認 weight 5 恰有七個 monomials。下一解析步是
把 bookkeeping remainder 改為 Bell-6，並以 spatial `M_8` 控制 A7
之外的 Taylor remainder。這應把 local absolute error多降一個
standardized 小參數，但尚未完成，故不可宣告 `k<3802`。

## J41（已證）：weight-5/Bell-6 blocks 將完整門檻降至 `k=2601`

`experiments/verify_j41_weight5_blocks.py` 已完成 J40 的解析部分：

- exponent 保留 `A_3z³+...+A_7z⁷`；
- bookkeeping `e^{g(s,z)}` 展開至 weight 5，remainder 由 complete
  Bell polynomial `B_6(g',...,g^(6)) / 6!` 控制；
- spatial Taylor remainder 使用
  `M_8|z|^8/(8!Λ^4)`；
- J22 的八階 error constant
  `E_8=24214016` 由 Eulerian polynomial 的 exact geometric-moment
  恒等式在程式內以 Fraction 重建，而非浮點猜值。

在低 blocks 中只使用 `A_3,A_4,A_5<0`；A6、A7 都允許任意符號。含
它們的 center monomials 一律當成可能正項；若正 monomial 不含 A3/A5，
則必含 A7，並用

`|A_7/A_3|≤|B_7|/[840Λ²(2t+1)]`  (J41.1)

相對主項 enclosure。這個結構也由 assertion 核對。

在 `[2600,2720]` 取 `ell=sqrt(8logt)`，其後取 `sqrt(7logt)`；共 334 個
0.1% continuous blocks 嚴格覆蓋

`2600≤t≤3800`.  (J41.2)

每塊沿用 directed mode、Λ、normalization 與 tails；全部通過。共同界為

`κ_(3,t)<0`,

`t²|κ_(3,t)|<0.046443<1/21`,

`t Var_t(X)<0.075113<19/250`.  (J41.3)

最弱 block `[2600,2603]` 的 Bell-6/spatial error 對 negative center 比率
為 `0.991946`。J39、J35 在後續範圍給相容的更強界，所以 J41.3 對
全部 `t≥2600` 成立。

令 `k≥2601`。J17 給

`0<D_k<38/[125(k-1)]`,

`-8/[21(k-1)²]<D_(k+1)-D_k<0`.  (J41.4)

此端點仍有 `D<1/5000`，故 `e^D≤1+(2501/2500)D`。J14 的兩個 tail
在 `log2601<8` 下各小於 `k^-20`；更新後 J32 verifier 證 lower/upper
corridor margins 均吸收 `16k^-20,32k^-20` 擾動。因此完整 Xi 核對
所有 `k≥2601` 滿足 J12。

degree-3 finite gap 現為 `1≤k≤2600`。第一 Bell-6 block 又只剩不足 1%
margin；下一步若續 saddle hierarchy，須加入 `A_8,A_9` 與 weight-7
中心／Bell-8，或改作直接 moment interval certificate。

## J42（已證代數；解析 enclosure 未完成）：weight-7 cumulant

加入 `A_8=B_8/(8!Λ^4)`、`A_9=B_9/(9!Λ^(9/2))`，並把 bookkeeping
展開至 weight 7。`experiments/verify_weight7_gaussian.py` 的 exact
Fraction algebra 證第三 cumulant 的 weight-7 行為

`7560A_9+99000A_5A_6+98280A_4A_7+735840A_4²A_5`

` +95760A_3A_8+725400A_3A_5²+1445040A_3A_4A_6`

` +4084992A_3A_4³+706860A_3²A_7+12100320A_3²A_4A_5`

` +3965760A_3³A_6+37812096A_3³A_4²+18691560A_3⁴A_5`

` +77857200A_3⁵A_4+41990400A_3⁷`.  (J42.1)

程式同時證所有偶 weight 0、2、4、6 精確消失，並重現 J40 的七個
weight-5 monomials。J42.1 若要成為 block certificate，還須加入
complete Bell-8 bookkeeping remainder 與 spatial `M_10/(10!Λ^5)`；
J22 的所需 exact constants 為

`E_9=558935040`, `E_10=14514710528`,  (J42.2)

可由 J41 的 Eulerian recurrence同樣重建。這部分尚未實作，故不能將
J41 門檻再下推。

## J43（已證）：weight-7/Bell-8 blocks 將完整門檻降至 `k=1859`

`experiments/verify_j43_weight7_blocks.py` 已把 J42 轉成 directed
continuous certificate。程式在每一 block 內同時 enclosure 真 mode、
`Lambda`、`B_3,...,B_9`，並使用：

- J42 的全部 weight 1、3、5、7 signed center；
- complete Bell polynomial `B_8/8!` 控制 bookkeeping remainder；
- spatial remainder `M_10|z|^10/(10!Lambda^5)`；
- 由 exact Eulerian recurrence 重建
  `E_8=24214016`、`E_9=558935040`、`E_10=14514710528`；
- 對 `A_6,...,A_9` 不作符號假設，凡含它們的 monomial 一律容許為
  正抵消項，並以 `A_5/A_3`、`A_7/A_3`、`A_9/A_3` 比率封閉。

取 `ell=sqrt(7logt)`，272 個 0.1% blocks 嚴格覆蓋

`1858<=t<=2600`.  (J43.1)

所有 blocks 通過；最弱 block `[1858,1860]` 給

`local error/negative center<0.941955`,

`t^2|kappa_(3,t)|<0.049740<1/20`,

`t Var_t(X)<0.078523<79/1000`, 且 `kappa_(3,t)<0`.  (J43.2)

J41、J39、J35 在後續區間給更強相容界，故 J43.2 對所有 `t>=1858`
成立。對 `k>=1859`，J17 因而給

`0<D_k<79/[250(k-1)]`,

`-2/[5(k-1)^2]<D_(k+1)-D_k<0`.  (J43.3)

更新後 `experiments/verify_j32_tail_transfer.py` 以 exact Fraction 核對
`D<1/5000`、theta-tail 的 `16k^-20,32k^-20` 擾動，以及 full
`C_k>=683/(1000k)` 的 lower/upper corridor margins。因此完整 Xi 核對
所有 `k>=1859` 滿足 J12。

這個證書直接比較 Bell-8 與 M10 的絕對餘項，沒有假設「下一階必比
前一階小」。本階原始 Lipschitz 曲率 gate 在低端先失敗；J45 後來以
直接 `F''` interval 改善此處，所以 1859 只是 J43 當時的接點，不是
方法本身不可越過的門檻。

## J44（已證代數）：顯式 weight-9 cumulant

加入 `A_10,A_11`。`experiments/verify_weight9_gaussian.py` 以 exact
Fraction 重現 J40/J42 所有舊項、確認偶 weight 0,2,4,6,8 全消失，並
得到 30 個 weight-9 monomials：

`103950A11+1583820A6A7+1577520A5A8+4495500A5^3+1564920A4A9`

`+26887680A4A5A6+13366080A4^2A7+84844800A4^3A5+1530900A3A10`

`+13253760A3A6^2+26437320A3A5A7+26248320A3A4A8`

`+252061200A3A4A5^2+251199360A3A4^2A6+439741440A3A4^4`

`+12870900A3^2A9+248763960A3^2A5A6+247257360A3^2A4A7`

`+2614939200A3^2A4^2A5+81012960A3^3A8+864002700A3^3A5^2`

`+1721528640A3^3A4A6+6625255680A3^3A4^3+423940230A3^4A7`

`+9855545400A3^4A4A5+1947173580A3^5A6+24503964480A3^5A4^2`

`+8102922480A3^6A5+31160026080A3^7A4+12440836980A3^9`.  (J44.1)

## J45（已證）：weight-9/Bell-10 blocks 將完整門檻降至 `k=938`

J43 的 `M_3 w<=Lambda/2` 只是視窗強凹性的充分條件。新驗證器另直接
enclosure

`F_t''(x)=u l_1(u)+u^2 l_2(u)`

並逐 block 證 `F_t''<=-Lambda/2`；這移除低端的 Lipschitz 損失。
`experiments/verify_j45_weight9_blocks.py` 再使用 J44 signed center、
complete Bell-10 remainder 與 spatial M12 remainder。所需新 exact
constants 為

`E_11=418806018048`, `E_12=13292606038016`.  (J45.1)

取 `ell=sqrt(8logt)`，以 0.1%、0.5%、1% adaptive blocks 共 84 塊
嚴格覆蓋

`937<=t<=1858`.  (J45.2)

全部通過；最弱符號 block `[937,938]` 給

`local error/negative center<0.995057`.

全區間 bounds（最弱 magnitude block 為 `[950,955]`）是

`kappa_(3,t)<0`,

`t^2|kappa_(3,t)|<0.059513<3/50`,

`t Var_t(X)<0.086636<87/1000`.  (J45.3)

與 J43 以後的更強 bounds 接合，J45.3 對所有 `t>=937` 成立。故對
`k>=938`，

`0<D_k<87/[250(k-1)]`,

`-12/[25(k-1)^2]<D_(k+1)-D_k<0`.  (J45.4)

theta-tail 在此端點改用 `k^-19`。具體地 `log938<137/20`，且

`938>(39/2)(137/20)^2+137/20`,

足以由 J32.1 的第一項得到 `k^-19`；第二項更小。更新後 J32 verifier
以有理算術證 full `C_k>=650/(1000k)`，lower recurrence 尚有
`>1/(3k^2)` margin，upper recurrence 尚有 `>2/(3k^2)` margin，均吸收
`16k^-19,32k^-19`。因此完整 Xi 核對所有 `k>=938` 滿足 J12。

最低 block 只剩約 0.5% 符號 margin，所以 weight-9/Bell-10 的當前
絕對餘項證書已實際耗盡。degree-3 finite gap 現為 `1<=k<=937`。
下一候選是直接 rigorous moment intervals；若續 saddle hierarchy，
必須先證 weight-11/Bell-12/M14 的增益足以抵銷更大的 combinatorial
majorant。無論哪一條都不處理 degree 4 以上的獨立全階缺口。

## J46--J51（已證；saddle 加階路徑目前耗盡）

同一 exact engine 又依序完成：

- J46：weight-11，56 個新層 monomials，偶 weight 仍精確消失；
- J47：Bell-12/M14 的 36 blocks 覆蓋 `[800,937]`；
- J48：weight-13，101 個新層 monomials；
- J49：Bell-14/M16 的 14 blocks 覆蓋 `[744,800]`；
- J50：weight-15，176 個新層 monomials；
- J51：Bell-16/M18 的 9 blocks 覆蓋 `[726,744]`。

各 exact algebra 分別由 `verify_weight11_gaussian.py`、
`verify_weight13_gaussian.py`、`verify_weight15_gaussian.py` 重建；block
證書為 `verify_j47_weight11_blocks.py`、`verify_j49_weight13_blocks.py`、
`verify_j51_weight15_blocks.py`。J51 全段給

`kappa_(3,t)<0`,

`t^2|kappa_(3,t)|<0.064095<13/200`,

`t Var_t(X)<0.090035<91/1000`.  (J51.1)

最低 `[726,727]` 的 error/negative-center 為 `0.996630`。與後段接合，
J51.1 對 `t>=726` 成立。更新 J32 verifier 在 `K=727` 使用
`log727<33/5` 與 `k^-16` theta tail，並核對 full
`C_k>=634/(1000k)`、lower margin `>1/(3k^2)`、upper margin
`>29/(50k^2)`。所以完整 Xi 核對所有 `k>=727` 滿足 J12。

門檻改善依序為

`1859 -> 938 -> 801 -> 745 -> 727`,  (J51.2)

而新增層大小為 `30,56,101,176`，最低 block 餘裕反覆只剩約
`0.3--0.5%`。weight-15 的單 block 建構亦已需約分鐘級；其相對
weight-13 只改善 18 個 shifts。這不證明更高階永遠無效，但已明確
耗盡目前 absolute-Bell/M_(2m) 引擎的實用加階路徑；不得無限外推
「再加兩階必能到 0」。degree-3 finite gap 現為 `1<=k<=726`。

## J52（直接 moments 的證書介面；尚未實作完成）

有限精度 `scan_xi_j11.py --max-k 728` 得最小 J12 recurrence margin
約 `2.0262e-6`，library quadrature 報告的最大相對誤差約 `1.5e-11`。
這只用來選精度，絕不是證明。

可行的純 directed 方案如下。對每個 theta 項置

`F_(k,n)(u)=2k logu+log T_n(u)`。

J15 的同一計算給 `F_(k,n)''<0`，故在 cell `[a,b]` 上：

- `exp` of the endpoint chord 積分是嚴格下界；
- midpoint tangent 是嚴格上界；若 `F'(m)` 只有 interval，左半用
  derivative lower endpoint、右半用 upper endpoint仍給上界；
- `u>=U` 由凹性 tangent 給
  `integral_U^infty exp(F)<=exp(F(U))/(-F'(U))`；
- `u<=a` 可用 `max T_n * a^(2k+1)/(2k+1)`。

theta sum 在 `n<=N` 逐項 enclosure。對 `n>N`，使用

`T_n(u)<=4pi^2 n^4 exp(9u/2)exp(-pi n^2 exp(2u))`

及 `n^4` Gaussian sum 的 integral-test bound，再把共同因子
`exp[-pi N^2(exp(2u)-1)]` 取出；所得 tail 仍是 log-concave，可用同一
chord/tangent 積分。最後從 moment intervals 算

`C_k=1-(2k-1)M_(k-1)M_(k+1)/[(2k+1)M_k^2]`  (J52.1)

並以 outward ratios直接核對 J12.2。目標 moment relative width 應取
`<10^-7`，足以低於診斷 margin；實際通過前不能宣告 finite gap 關閉。

## J53（部分已證）：directed moments 已覆蓋 `50<=k<=400`

J52 的二階 cell Taylor 已實作。若整格 `F'' in[q_-,q_+]`，則 midpoint
兩側都有相應 quadratic 上下式。每個 `exp(ax+bx^2)` 積分以三階
exponential Taylor polynomial逐係數有向積分，並加顯式餘項

`h exp(eta) eta^4/4!`, `eta>=|a|h+|b|h^2`.  (J53.1)

window 外仍用凹性 tangent。採 `h=0.45/k`；浮點 mode 只選 window，
兩端 derivative 符號由 Decimal interval assertion重驗，故不進入證明。

`experiments/verify_j53_direct_moment_chunks.py` 的核心 verifier 已完成

`[50,150]`, `[151,250]`, `[251,325]`, `[326,400]`.  (J53.2)

每個 moment 先 enclosure第一 theta 項，再把 J14.3 的 directed
`epsilon_k` 乘到上端，最後由 J52.1 outward 計算 C。四批皆通過完整
Xi 的 J12.2，共同最小認證 margin 為

`2.9422029881550...e-6>0`.  (J53.3)

首批低端 `k=49` 的 J14 relative tail upper 為 `3.680325e-7`；其後
迅速消失。另 `[99,101]` 已獨立 regression 通過。目前 degree-3 未
覆蓋集合為 `1<=k<=49` 與 `401<=k<=726`。後段可續跑同一 verifier；
前 49 個 shifts 的 J14 tail 太粗或在 `k<3` 不適用，須逐 theta 項
enclosure，再以 J52 的 Gaussian-sum bound處理 `n>N`。

## J55（已證）：1-ulp 修正後，全部 shifted degree-3 已封閉

J53 初版在 cell 上先令 `width=down(b-a)`，卻也把這個縮短寬度用於
上界；形式上留下約 1 ulp 的右端缺口。即使數值量級遠低於 margin，
也不能忽略。修正版選一個 exact Decimal midpoint：

- 下界左右長度各向下取整，只積 cell 的子區間；
- 上界左右長度各向上取整；
- `F''` enclosure domain 同步向外擴張到這兩個上界長度。

因此 lower/upper 的幾何方向現在完全正確。修正後必要重驗為

`[1,34]`（J54，逐項 n=1,...,4 加 n>=5 Gaussian-sum tail），

`[35,49]`, `[50,150]`, `[151,325]`, `[326,450]`, `[451,726]`
（J53，加 J14 tail），以及 J51 的 `k>=727` 解析接合。全部通過。

J54 對 `n>=5` 使用

`sum_(n>=5)n^4 exp(-pi n^2 exp(2u))`

`<=S_5 exp[-25 pi (exp(2u)-1)]`,

並以 `exp(2u)-1>=2u` 得 moment tail

`<=4pi^2 S_5 (2k)!/(50pi-9/2)^(2k+1)`.  (J55.1)

`S_5` 由第一項加 `integral_5^infty x^4e^(-pi x^2)dx` 的三次分部積分
上界；最大 absolute tail 仍只有 `1.298e-32`。全有限段最小 J12
認證 margin 出現在高段，為

`9.936754975375...e-7>0`.  (J55.2)

故完整 Xi 偶矩序列對每個 shift 都滿足 J12.2，從而所有 shifted
degree-3 Jensen 多項式 hyperbolic。這是一個完整、獨立的 cubic
Jensen 定理；它本身不推出 RH。

## J56（策略稽核）：degree 3 與任意 degree 的斷層

### J56.1 degree 3 實際提供的結構

J55 控制每四個連續係數。等價地，它證 J8 的 cubic discriminant，或
J11/J12 的兩個相鄰 Turan ratios／協方差 `C_k,C_(k+1)` 落在指定區域。
在 tilted log-u 語言中，這只用了 variance、third cumulant 及其相鄰
平均。它沒有控制五個以上係數形成的 quartic/higher Hermite minors，
也沒有任何 uniform-in-d 常數。

### J56.2 exact 反例：重疊 cubics 不升到 quartic

取正序列

`(gamma_0,...,gamma_4)=(25,78,143,76,29)`.

兩個 shifted cubics 是

`25+234X+429X^2+76X^3`,

`78+429X+228X^2+29X^3`.

其 exact discriminants 分別為

`1622598480`, `555001200`,

皆正；係數全正排除正根，所以各有三個負實根。但 quartic

`25+312X+858X^2+304X^3+29X^4`

的 discriminant 為

`-1348512563200<0`,  (J56.1)

故有非實共軛根。`experiments/verify_degree3_not_degree4.py` 用 integer
Bareiss resultant exact 核對。這直接否證任何不使用 Xi 額外結構的
「所有 shifted cubics => quartic」升階引理。

### J56.3 正確的 uniform 目標

Jensen polynomials 有 exact identities

`J_(d+1,n)=J_(d,n)+X J_(d,n+1)`,

`(J_(d+1,n))'=(d+1)J_(d,n+1)`.  (J56.2)

因此真正可升階的充分機制必須控制 `J_(d,n)` 與
`XJ_(d,n+1)` 的共同 interlacing／compatibility，且對所有 d,n 一致。
若只有各自 hyperbolic，兩項和仍可失去實根；J56.1 正是低階警告。

等價的兩個全階表述是：

1. 對每個 d,n，binomial-weighted block
   `a_k=C(d,k)gamma_(n+k)` 的 finite Toeplitz matrix為 PF-infinity；
2. 對每個 d,n，`J_(d,n)` 的 Hermite／Bezoutian matrix為正半定，最好
   能由 Xi 核給出一個對 d 一致的 Gram integral representation。

一般 raw moment Hankel positivity不是答案：正測度自動給
`M_k^2<=M_(k-1)M_(k+1)`，方向已與 J2 的 factorial-normalized條件不同。
同樣，Phi 的平移核 TP2 已由 K2 證明不足；直接追求 translation-kernel
PF-infinity 前還必須稽核它是否反而迫使 Fourier transform zero-free，
因而不適用具有零點的 Xi。

### J56.4 新主線與停止規則

停止逐 degree 刷 finite certificates。degree 3 記為 J55 的獨立成果。
下一研究只接受能處理任意 d 的候選：

- 從 Xi integral 導出 J56.2 的 uniform common-interlacing；
- 為全部 Jensen Hermite/Bezoutian matrices 建 uniform Gram factorization；
- 或證正確的 coefficient-array total positivity，並完整核對其 closure
  與 Fourier-zero假設。

在找到其中一個具體機制前，degree 4 甚至不應成為主線的下一個有限
掃描目標。RH Goal 仍未完成；核心缺口已明確改為 uniform all-degree
structure。

## J57. uniform Pick/PF∞ 候選與有限導數反例

令 `G(w)=sum gamma_k w^k/k!`、`h=G'/G`。若能對每個 `Im z>0` 證
`Im h(z)<=0`，則 h 在任何非實零點附近的 principal part
`m/(z-zeta)` 會產生兩種虛部符號，矛盾；配合正係數，即一次推出 G 的
零點全在負實軸，從而處理所有 Jensen degree。等價 coefficient 目標是
`c_k=gamma_k/k!` 的無限 Toeplitz PF∞，不是逐 d finite certificate。

Xi integral 將缺口化成逐點雙積分
`Im[G'(z)conj G(z)]<=0`。正 mixture 自身不保此式：scale measure
`3δ_1+δ_100` 給 `h'(0)=(AC-3B²)/(12A²)>0`。而 J56 exact 反例雖在
原點滿足 `(-1)^m h^(m)(0)>0` 對 `0<=m<=5`，其 m=6 符號失敗且 quartic
discriminant為負。故有限 real-axis derivative signs 仍只是一批必要條件，
不能升階。可行的 uniform 工作必須直接證 full upper-half-plane Pick
符號、全部 PF∞ minors，或 A7 的共同交錯 cone；目前三者皆未由 degree 3
導出。

J57 的 Pick 條件亦可化成真正的 all-size determinant 問題：令
`b_m=(-1)^m h^(m)(0)/m!`，則須同時證 `(b_(i+j))` 與
`(b_(i+j+1))` 對任意尺寸 PSD；配合解析 growth bound，Stieltjes moment
representation會反向給 full anti-Pick。J56 反例即使有 `b_0,...,b_5>0`，
最初兩個 2-by-2 determinants仍精確為 `-2119/15625`、
`-610088/234375`。故這種全尺寸 Gram 結構不是 cubic 的隱含推論。

## J58. J12 corridor 本身也只屬於 cubic

為排除 J55 證出的較強 J12.2 可能暗藏升階，取無限序列

`C_1=61/1000`, `C_2=49/1000`, `C_k=6/125` (`k>=3`)，

再由 `r_(k+1)=r_k(1-C_k)`、`gamma_(k+1)=gamma_k r_(k+1)`、
`gamma_0=gamma_1=r_1=1` 定義正 gamma。此時
`C_k=1-gamma_(k-1)gamma_(k+1)/gamma_k²` 恒成立；前兩個 lower bounds
分別是 `11529/250000<C_2`、`9849/250000<C_3`，其後 C 為常數，故
完整 J12.2 對所有 k 成立。

然而前五項所成 `J_(4,0)` discriminant嚴格為負；integer Bareiss exact
檢查已加入 `experiments/verify_degree3_not_degree4.py`。因此即使保留
J12 的全 k 單調 covariance corridor，而不只保留 cubic hyperbolicity
結論，也無法升到 degree 4。J12 正式分類為 cubic-only lemma；真正全階
路徑仍只能是共同交錯 invariant、PF∞/Pick，或 A12 的 all-size Gram。

## J59. Stieltjes--Hankel Gram 不由正 mixing 自動產生

A12 最低 determinant代入 `gamma_k=k!M_k/(2k)!` 後是

`[3M_0M_1M_3+15M_1²M_2-10M_0M_2²]/(1440M_0³)`.

一般正 scale measure `(3/4)δ_0+(1/4)δ_1` 使它精確等於
`-13/92160`；以小正 scale代替 0 仍由連續性保持負號。因此 A12 的
all-size Gram若存在，必須使用 Xi 特殊 theta/score identity，不能由
`Phi>0`、raw moment Hankel PSD或直接 mixture Cauchy--Binet得到。這條
路目前有正確的 uniform 目標，尚沒有非循環的 Xi-specific factorization。

## J60. cubic 對全階 continued fraction 只初始化兩步

PF∞、anti-Pick 與 Stieltjes--Hankel 是同一全階 obligation 的等價座標，
不列為三條獨立路線。採 S-fraction座標時，`h=G'/G` 的 moment coefficients
`b_m=(-1)^m[h]_(w^m)` 需有全部非負 continued-fraction pivots。

若 `q=gamma_1/gamma_0`、`x=C_1,y=C_2`，則 exact

`b_0=q`, `b_1=q²x`,

`det H_2^(0)=q^4(1-x)[x-(1-x)y]/2`.

故 J12 確實給前兩個 pivots正性；這是 cubic 的唯一可見 Gram seed。但
J12-compatible chain `C_1=17/500,C_2=4/125,C_k=29/1000 (k>=3)`
使第三 pivot exact 為 `-17279199581/205062500000`。所以沒有 pivot
升階遞推。

## J61. J12 加 C 的 complete monotonicity 仍不足

取 `C_k=1/[4(k+2)]` 並以 ratio recurrence定義 gamma。C 是正 measure
`(t²/4)dt` 在 `[0,1]` 的 Hausdorff moments，故所有 finite differences
完全單調；又

`C_(k+1)-C_k(1-4C_k)=1/[4(k+3)(k+2)²]>0`,

所以全域 J12 亦成立。然而 exact rational Sturm chain得到
`J_(10,0)` 的 variations為 8 與 2，只含 6 個實根。驗證器為
`experiments/verify_complete_monotone_j12_not_uniform.py`。這嚴格否證
以 C 的全部有限差分符號補成 uniform theorem。

## J62. recurrence 升階 cone 的邊界

令 `F_j^(d,n)=X^jJ_(d,n+j)`，則
`F_j^(d+1,n)=F_j^(d,n)+F_(j+1)^(d,n)`。若整族 F full compatible，
此 adjacent-sum map確實保持 compatibility，形成真正升階定理；但 d=0
family已有 `1+lambda X²` 非實根，無法初始化，而 cubic individual
hyperbolicity不給整族 compatibility。

迭代恒等式
`J_(d+m,n)=sum_j C(m,j)X^jJ_(d,n+j)` 顯示：若只控制實際需要的
binomial combinations，假設就等於 higher Jensen hyperbolicity本身。
故 Pascal recurrence目前不是 missing induction step；缺的是一個由 Xi
可證、比 full compatibility弱但仍在 adjacent-sum map下封閉的新 cone。

## J63. theta shifts 的算術因子

J14.1 等價於 exact convolution

`Phi(u)=int T_1(u+a)dmu(a)`,

`mu=sum_(n>=1)n^(-1/2)delta_(log n)`.

而 `Re s>1/2` 時

`int e^(-sa)dmu(a)=zeta(s+1/2)`.

因此 first-theta 的 saddle/score只控制 envelope；all-degree compound
positivity還必須處理離散 `log n` shifts，其 transform本身就是 zeta。
A8/A14 已證正 mixture不保 Gram/Pick，故不能把 J14 的 high-moment theta
tail smallness升格為 fixed-shift、uniform-in-degree perturbation theorem。
任何合格的 theta-side all-r identity都必須顯式保留這個算術 measure。

## J64. positive raw moments 加 global J12 仍不升 quartic

取獨立 Beta variables，參數以 `(alpha,beta)` 表示 moment
`(alpha)_k/(beta)_k`：

`(alpha_1,beta_1)=(21/40,11/2)`,

`(alpha_2,beta_2)=(9/2,51/4)`，並令 `S=X_1X_2`。則 S 是 `[0,1]`
上的正 measure，`M_k=E[S^k]`。對 `gamma_k=k!M_k/(2k)!`，C_k 是
顯式 rational function；四個 J12 inequality numerators在平移
`k=m+1` 後皆為 constant正、其餘 coefficients非負的有理多項式，故
global J12 對所有 k嚴格成立。

然而清分母後 exact Bareiss resultant給 `J_(4,0)` discriminant

`-62875994304180886316211353446153845425246830592000000000000`.

`experiments/verify_beta_moment_j12_not_uniform.py` 同時重建 Beta moments、
全 k polynomial certificate與 quartic符號。故 raw moment Hankel PSD加
J12仍只是 cubic-only；Xi 若有 all-degree closure，必須實質使用 A18 的
theta arithmetic，而非一般正測度結構。

## J65. 2026 Holland uniform wedge 與精確剩餘斷層

Holland (arXiv:2608.08682) 證存在絕對 `K` 使
`n^3 log^2(n+2)>=K d^5` 時 `J_(d,n)` 有相異負實根。其機制不是有限 degree
枚舉：以 Laguerre/Jacobi/second-Jacobi finite-free model exact匹配
`R_0,...,R_4`，再由五階 multiplier stability同時控制增長中的 `d`。

這提供 genuine uniform-in-d lemma，但不源自 J12/degree 3，也不覆蓋 RH 所需的
所有 `(d,n)`。尤其 n=0 永遠不在楔形。恒等式

```text
(J_(d+1,n))'=(d+1)J_(d,n+1),
J_(d+1,n)=J_(d,n)+X J_(d,n+1)
```

只給 forward derivative/Pascal 關係，沒有 inverse-shift。finite-free 文獻的
interlacing preservation亦為 forward；相異正根因子的 convolution inverse不能仍
全正根。因此 fixed五階 model不能 deconvolve回 exact Jensen族。

可行的新問題只有：證 theta-specific reverse-shift/common-interlacing cone，或把
完整 `R_j` 全階 exact factor為正根 finite-free blocks。固定匹配更多 `R_j` 最多擴張
asymptotic wedge；在沒有 all-order theorem前，依策略稽核停止此種逐階擴張。

## J66. Laguerre moment mixture不是 finite-free正根因子

令 `b=n+1/2` 且在 tilted probability
`dP_n=Phi(u)u^(2n)du/M_n` 下令 `V=U^2`。正確 moment公式 exact給

```text
J_(d,n)(X)/gamma(n)
 = E_n sum_(j=0)^d C(d,j) (XV)^j/[4^j(b)_j].
```

故最直接的 Schur--Szego/finite-free 解讀，是以 moments
`mu_j=E_n[V^j]` coefficientwise作用在負實根 Laguerre polynomial上。其乘子
polynomial卻是

```text
M_d(Y)=sum_j C(d,j)mu_jY^j=E_n(1+VY)^d.
```

Riemann tilted density非退化，故 d=2 時
`disc M_2=4(mu_1^2-mu_2)=-4 Var_n(V)<0`。所以 raw positive moment mixing
不是正根 finite-free factor，forward preservation theorem不能套。Holland的兩層
Jacobi correction正是 asymptotically繞過此障礙；要 exact all-order factorization
必須有不同、theta-specific blocks。

## J67. generic reverse shift即使加正係數仍為假

## J68. van Dantzig--Bernstein 的單一全階 moment-ratio target

令

```text
m_n=int_0^infinity u^(2n)Phi(u)du,
a_n=m_n/[(2n)!m_0],
Xi(t)/Xi(0)=sum_(n>=0)(-1)^n a_n t^(2n).
```

Konstantopoulos--Patie--Sarkar 的 class `D_P` 使用
`J_Psi(t)=sum (-1)^n t^(2n)/prod_(k=1)^n Psi(k)`。因此 exact coefficient
matching不是逐 degree證書，而是單一 recurrence

```text
Psi(n)=a_(n-1)/a_n
      =2n(2n-1)m_(n-1)/m_n,
varphi_n:=Psi(n)/n=2(2n-1)m_(n-1)/m_n.           (J68.1)
```

若存在一個 Bernstein Pick function `varphi`，具有該文的 1-separation property，
且 `varphi(n)=varphi_n` 對全部 `n>=1`，則 Theorem 4.4 對
`Psi(z)=z varphi(z)` 一次給 `J_Psi in D_L`，故 normalized `Xi` 屬
Laguerre--Polya，直接推出 RH。這是真正 uniform-in-degree mechanism。

更重要的是 J5 已證的 radial score恰給第一個無窮條件。令
`q(u)=-Phi'(u)/(uPhi(u))`、`dnu_n=u^(2n)Phi(u)du/m_n`。分部積分得

```text
varphi_n=2 E_(nu_n)[q(U)],                         (J68.2)
varphi_(n+1)-varphi_n
 =2 Cov_(nu_n)(q(U),U^2)/E_(nu_n)[U^2] >0.        (J68.3)
```

最後嚴格號由 J5 的 `q` 嚴格增加。因此整條 sequence無條件遞增；這不是有限
degree結果，而是 Bernstein必要條件的一階部分。尚缺全部 complete-alternation
`(-1)^(r-1)Delta^r varphi_n>=0`，以及更強的 Pick／meromorphic separation。

最自然的 theta-local interpolant是 Mellin ratio

```text
M(s)=int_0^infinity u^s Phi(u)du,
varphi_nat(z)=2(2z-1)M(2z-2)/M(2z),  Re z>1/2.    (J68.4)
```

它 exact插值 (J68.1)。要完成路線須證其 meromorphic continuation把 upper
half-plane映到自身，並控制 Mellin zeros/poles的 1-separation；正實軸 positivity
與有限差分都不夠。

## J69. Abel--arcsine deconvolution：KPS mixing variable 無條件為正

令

```text
m0=int_0^infinity Phi(u)du,
f_D(x)=Phi(|x|)/(2m0),
J=2cos(Theta),  Theta uniform on (0,pi).
```

`D` 的 characteristic function是 `Xi(t)/Xi(0)`，而 `J` 有 arcsine density
`[pi sqrt(4-j^2)]^(-1)`。右側 Abel反演給唯一 mixing density `g` 使

```text
D=sqrt(I)J,
f_D(x)=int_(x^2/4)^infinity g(v)/[pi sqrt(4v-x^2)]dv,
g(x)=-(2/m0)d/dt|_(t=4x)
      int_t^infinity Phi(sqrt(y))/sqrt(y-t)dy
    =-(1/m0)int_0^infinity
      Phi'(sqrt(4x+r))/[sqrt(4x+r)sqrt(r)]dr.       (J69.1)
```

J5 的 `Phi'(u)<0` 無條件給 `g(x)>=0`；Abel inversion給 `int g=1`。這一次
構造全部 moments 的同一正 measure：

```text
E[I^n]=(n!)^2m_n/[(2n)!m0],
E[I^s]=Gamma(s+1)^2M(2s)/[Gamma(2s+1)m0],          (J69.2)
s E[I^(s-1)]/E[I^s]
 =2(2s-1)M(2s-2)/M(2s)=varphi_nat(s).             (J69.3)
```

故 L12 的缺口縮成：證 J69 的顯式正變數 `I` 是 complete-Bernstein
subordinator 的 exponential functional，並滿足 KPS meromorphic 1-separation。
單有 `g>=0` 只證 Bessel/arcsine scale mixture，不證 `varphi_nat` 是 Bernstein/Pick。

Riemann kernel的 double-exponential tail給
`E[I^n]^(1/(2n))=O(log n)`，故 Carleman sum發散，`I` moment-determinate。
若 `varphi_nat` 是 Bernstein，perpetuity moment theorem所辨識的就是同一個 `I`。

## J70. complete-Bernstein 必要的 Fermi--Bose inverse-Laplace sandwich

令 `K_I(s)=log E[I^s]`。由 J69.2，

```text
K_I''(s)=4(log M)''(2s)+2psi_1(1+s)-4psi_1(1+2s).
```

polygamma積分與一次換元 exact給

```text
2psi_1(1+s)-4psi_1(1+2s)
 =-int_0^infinity exp(-sx) x/(exp(x/2)+1) dx.       (J70.1)
```

若 `varphi_nat` 是 complete Bernstein，Hirsch--Yor 的 harmonic-potential measure
`kappa` 滿足 `0<=kappa<=dx`，且

```text
K_I''(s)=int exp(-sx) x/(exp(x)-1)[dx-kappa(dx)].   (J70.2)
```

所以若以 `A` 表示 `4(log M)''(2s)` 的 inverse-Laplace **measure**，必有測度支配

```text
x/(exp(x/2)+1) dx
 <= A(dx)
 <= x/[2sinh(x/2)] dx.                             (J70.3)
```

上界用恒等式
`x/(e^(x/2)+1)+x/(e^x-1)=x/[2sinh(x/2)]`。這是單一 all-order
Fermi--Bose sandwich：下界等價 `log I` 的負跳 Levy measure非負，上界對應
`kappa>=0`／remainder channel。它比有限 complete-alternation批次強得多。

反向仍需一個 harmonic-potential admissibility theorem：即使 J70.3成立，所得
`kappa` 必須真是某 subordinator 的 harmonic potential，並且 exponent還須滿足
KPS meromorphic 1-separation。故 J70.3目前是必要的 uniform target，不是 RH證明。

## J71. J70 的條件式 Mellin-zero 展開

`M(s)` 的預定 poles來自 `Phi` 在 0 的 even Taylor series：`p_k=-(2k+1)`。
在允許對 logarithmic derivative作 Mittag--Leffler／inverse-Laplace展開的 growth
假設，且所得 measure已證 absolute continuous後，pole contribution的 density才可寫為

```text
sum_(k>=0)x exp(p_kx/2)
 =x exp(-x/2)/(1-exp(-x))=x/[2sinh(x/2)].          (J71.1)
```

若其餘 zeros `rho_j` 全為 simple negative real，則對 `x>0`

```text
A(x)=x/[2sinh(x/2)]-x sum_j exp(rho_jx/2),         (J71.2)
0<=sum_j exp(rho_jx/2)<=1/(exp(x)-1).              (J71.3)
```

J71.3連同 zeros全負實即給 J70 sandwich。complex zeros會產生 oscillatory/complex
inverse-Laplace terms，破壞正 measure；而 natural ratio的 poles `rho_j/2` 與 zeros
`1+rho_j/2` 正好相差 1。

邏輯限制（依 Selberg nudge 修正）：J70.3只在測度層級成立；從測度支配升成
J71.2 的逐點 density公式，必須另證 absolute continuity，以及 canonical product的
逐項 inverse-Laplace合法性。這個 density upgrade本身就是主要斷層，不能由積分
量詞自動推出。

## J72. certified nonreal Mellin zero 關閉 natural Pick interpolant

以 20 次分部積分的穩定 continuation、Arb complex-ball quadrature與顯式三類尾界，
`mellin_zero_certificate.md` 證明 `M` 在下列圓盤恰有一零點：

```text
|rho-z0|<10^(-18),
z0=-16.98836451398511699622058580767254
   +5.87553413713516825665577505243170 i.          (J72.1)
```

Rouché門檻為

```text
|M'(z0)|r-|M(z0)|-(1/2)sup_disk|M''|r^2 > 7.68*10^(-19),
|M(z0-2)|>2.4058.                                  (J72.2)
```

所有有限積分皆為 outward-rounded Arb balls；遺漏的 `v<-100`、`u>4` 與
`n>=21` tails分別有解析 majorant，總誤差遠小於門檻。故這不是以數值證據代替證明。

在 `s=rho/2`，
`varphi_nat(s)=2(2s-1)M(2s-2)/M(2s)` 有上半平面的真極點，因 J72.2 排除分子消去。
所以 **natural Mellin interpolant 不可能是 Pick／complete Bernstein**，L12 的這個
具體實現關閉。J72 本身不否證 RH；它當時尚未排除同一 integer data的另一個 KPS
interpolant，但緊接的 J73 以 Carlson uniqueness把這個最後可能性也排除。

## J73. Carlson 唯一性排除全部 KPS interpolants

令 `W_varphi(z+1)=varphi(z)W_varphi(z)`、`W_varphi(1)=1`。任何通過 J68 integer
data 的 KPS 候選都滿足

```text
1/W_varphi(n+1)=n!m_n/[(2n)!m0]=F_nat(n+1),
F_nat(z)=Gamma(z)M(2z-2)/[Gamma(2z-1)M(0)].        (J73.1)
```

duplication formula 把後者寫成

```text
F_nat(z)=sqrt(pi)2^(2-2z)M(2z-2)/[Gamma(z-1/2)M(0)],
```

其中 `1/Gamma` 恰消去 `M` 在負奇整數的 Mellin poles，故 `F_nat` entire。
Patie--Savov 的 exact Bernstein-gamma Stirling formula及
`0<=A_varphi(a+ib)<=pi|b|/2` 證 `1/W_varphi` 在右半平面為 exponential type，
兩個垂直 indicators皆 `<=pi/2`。J69 的
`E[I^n]^(1/(2n))=O(log n)`、Holder與 gamma recurrence同樣證 `F_nat` 為
exponential type且兩個垂直 indicators皆 `<=pi/2`。

因此差函數平移後在所有非負整數為零，且
`h(pi/2)+h(-pi/2)<=pi<2pi`；Carlson theorem給

```text
1/W_varphi(z)=F_nat(z)                              (J73.2)
```

先在右半平面成立，再由 entire continuation全域成立。但 J72 的 nonreal `M` zero
使 `F_nat(1+rho/2)=0`；KPS 1-separation卻要求 `1/W_varphi` 的 zeros全為 simple
negative real，矛盾。故 **不存在任何** 通過全部 `varphi_n` 的 KPS
Bernstein--Pick 1-separated interpolant。這把 J72 的 natural obstruction提升成整個
KPS route的否定性 closure；不是 RH證明。完整估計見 `carlson_kps_uniqueness.md`。
取 `P=x^4+8x^3+22x^2+24x+12`。則
`P'=4(x+1)(x+2)(x+3)`，故 shift n>=1 的完整 derivative/Jensen tower實根；
但 P 在臨界點 `-1,-2,-3` 的值為 `3,4,3`，兩端亦為正，故 P無實根。
這是 exact algebraic反例，證明 L11不能只假設 positive coefficients加所有
higher-shift hyperbolicity。缺失條件必須能辨識完整 Riemann theta arithmetic。
