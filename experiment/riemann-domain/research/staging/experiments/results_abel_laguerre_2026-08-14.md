# Abel–prime–Laguerre 公式 QA（2026-08-14）

執行：`python experiments/verify_abel_laguerre.py`

以 sieve 生成 `m≤200000` 的 von Mangoldt 權重，比較：

1. 在 `s=1+δ` 直接高精度微分 h；
2. D7 的極點補償加截斷 prime–Laguerre 和。

所有 `δ∈{1,2}`、`1≤n≤4` 的殘差均落在以 `Λ(m)≤log m` 和 incomplete-gamma 積分得到的解析尾界內。例如：

- `δ=1,n=4`：殘差 `5.7609966e-4`，尾界 `5.5287737e-2`；
- `δ=2,n=4`：殘差 `1.1543437e-9`，尾界 `1.1912366e-7`。

這只檢查有限截斷實作。D7 的等式由正常收斂與有限二項代數證明；數值不證明 δ→0 與 n→∞ 的 D8 一致界。

