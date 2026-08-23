# Evaluation evidence index

Historical protocols, raw rows, workspaces, screenshots, and dated reports are
preserved in the verified
[`evidence-archive-2026-08-22`](https://github.com/shihchengwei-lab/masters-nudge/releases/tag/evidence-archive-2026-08-22)
release. They are not active product code.

## Retained conclusions

- Workflow Holdout V2 R2 used 18 synthetic packets and two repeats: 36 baseline,
  36 routed, and 12 specialist-primary calls (84 total). The routed condition
  passed its eight pilot gates, but the evidence used one author-rater and does
  not establish field reliability or downstream task impact. The first 84-row
  batch was excluded in full because the harness selected an incompatible Codex
  CLI and exited before generation.
- The lens-differentiation run transported 18/18 calls. Five of six lenses were
  stable in 3/3 repeats; the alternate lens was stable in 1/3. A later 18-call observation
  run reached 18/18 aligned, complete delivered findings, still without an
  independent holdout reliability claim.
- Phase B sensitivity calibration had 18 control and 18 positive-control runs;
  all 36 transports and graders were valid, but 0/6 task patterns met the
  preregistered sensitivity gate. The instrument was therefore stopped.
- The Phase B impact pilot had 18 matched pairs and 36/36 valid rows. Treatment
  and control both passed 13/18 tasks; one treatment win and one loss produced
  net zero. This is a null pilot, not evidence that injection improves outcomes.
- An earlier six-call treatment-generation batch was infrastructure-invalid:
  generation completed, but a wrong field name prevented result serialization.
  No output from that batch was inspected, selected, or reused.
- The dated Codex Phase C smoke was one Windows/Codex 0.147.0 observation. Its
  host behavior is not a guarantee for later versions.

## Claim boundaries

- Synthetic fixtures test fixed inputs; they do not establish field reliability.
- Human adjudication was limited and was not independent multi-rater validation.
- A generated finding, an injection receipt, and a later response are different
  events. Temporal association is not a causal effect size.
- Provider-reported usage and latency describe only the archived harness and
  versions; they are not normalized cost or future-performance estimates.
