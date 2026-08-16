# 前綴平方 Fourier 恒等式 QA（2026-08-14）

執行：`python experiments/verify_prefix_fourier_identity.py`

對 `N=256` 的實際 von Mangoldt 權重，以 2048 點單位圓網格檢查 M7：

- 直接前綴平方和：`2217.90207146331`；
- Fourier 網格 Parseval 平均：`2217.90207146329`；
- 相對誤差：`7.996e-15`；
- 多項式分解最大殘差：`7.472e-12`。

因網格點數高於多項式平方所需的 alias-free 門檻，此處離散 Parseval 本質上是有限維代數 QA。它不提供 N→∞ 的低頻界，也不構成 RH 證據。

