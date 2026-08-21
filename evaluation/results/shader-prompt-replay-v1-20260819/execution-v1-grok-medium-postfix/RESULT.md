# Grok medium Shader prompt replay — 2026-08-19

## Result

The frozen 18-call protocol did not pass as a complete six-persona run.

- 18 attempts: 16 findings and 2 Grok CLI timeouts.
- Both timeouts were Karis calls; the only successful Karis finding did not address cross-pass material semantics.
- Human review: 16/16 observations rather than instructions, 16/16 complete findings, 16/16 strength-2 blind spots, and 15/16 persona-aligned findings.
- Aligned coverage by lens: Akenine-Möller 3, Carmack 3, Karis 0, Lottes 3, Quilez 3, Tatarchuk 3.
- Attempt p95: 91,865 ms. Successful-response p95: 88,822 ms.
- Automated diagnostics reported 93.8% non-imperative because `比較的是` triggered the lexical imperative detector; human review treats that sentence as a question, not an instruction.

## Gate interpretation

The global prompt-shape gates pass on successful responses: at least 80% non-imperative, at least 90% complete, and at least 50% strength-2 blind spots. The protocol fails the requirement for at least two aligned outputs per persona because Karis has no aligned successful output. Transport reliability is also below a clean 18-call run because two calls timed out.

## Scope

This replay uses one identical frozen checkpoint and forces each persona. It bypasses the router and does not inject findings into a main-model session. It therefore tests Provider latency and prompt/persona output quality only; it does not test research-packet v2 routing, deduplication, delivery, downstream reaction, long-tail progression, or causal effectiveness.
