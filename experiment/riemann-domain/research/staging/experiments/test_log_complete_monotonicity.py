#!/usr/bin/env python3
"""Offline finite stress test for complete monotonicity of g'/g.

No finite pass establishes complete monotonicity or RH.
"""

from __future__ import annotations

import mpmath as mp


def h(s: mp.mpf) -> mp.mpf:
    return 1 / (s - 1) + mp.diff(mp.zeta, s) / mp.zeta(s)


def main() -> None:
    mp.mp.dps = 40
    points = [mp.mpf(x) for x in ("1.1", "1.5", "2", "3", "5")]
    failures: list[tuple[str, int, str]] = []
    minimum = None
    for s in points:
        coefficients = mp.taylor(h, s, 3)
        for k, coefficient in enumerate(coefficients):
            value = (-1) ** k * mp.factorial(k) * coefficient
            if minimum is None or value < minimum[0]:
                minimum = (value, s, k)
            if value < 0:
                failures.append((mp.nstr(s, 8), k, mp.nstr(value, 18)))
    print("DIAGNOSTIC ONLY: finite derivative samples cannot prove complete monotonicity")
    assert minimum is not None
    print(
        "smallest signed derivative: "
        f"{mp.nstr(minimum[0],18)} at s={mp.nstr(minimum[1],8)}, k={minimum[2]}"
    )
    print(f"negative samples: {len(failures)}")
    for row in failures[:20]:
        print(",".join(map(str, row)))


if __name__ == "__main__":
    main()
