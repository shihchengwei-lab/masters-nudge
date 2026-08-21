# Revised Karis replay — 2026-08-19

## Result

The revised Karis persona passed this three-call forced-persona replay.

- 3/3 calls returned findings; no timeout or provider error.
- 3/3 findings were observations rather than instructions and were complete within 52 characters.
- Human review scored 3/3 as strength-2 blind spots and 3/3 as aligned with cross-pass material semantics.
- Latencies were 59,394 ms, 59,880 ms, and 82,131 ms; observed sample p95 was 82,131 ms.
- Recorded provider cost was USD 0.02417298. Total reported tokens were 44,895.

The lexical theme diagnostic counted 2/3 because the frozen fixture terms include the English pass names but one finding used the Chinese words `深度` and `陰影`. Human review counted that finding as aligned; the diagnostic miss is not treated as a persona failure.

## Scope

This replay uses one identical frozen checkpoint and forces Karis, bypassing routing and main-model delivery. It validates the revised Persona wording against this packet only; it does not test routing, injection, downstream reaction, long-tail progression, or causal tool effectiveness.
