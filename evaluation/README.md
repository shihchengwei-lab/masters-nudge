# Evaluation evidence index

This is the only index for evidence retained in the product repository. It separates result summaries from executable protocols and from raw historical artifacts.

Raw rows, screenshots, generated dashboards, zipped workspaces, and stopped harnesses are preserved in the verified [evidence archive release](https://github.com/shihchengwei-lab/masters-nudge/releases/tag/evidence-archive-2026-08-22). The complete Riemann tree is preserved at the release's fixed [tagged source tree](https://github.com/shihchengwei-lab/masters-nudge/tree/evidence-archive-2026-08-22/experiment/riemann-domain).

## Retained workflow summaries

- [Workflow Holdout V2 R2](results/workflow-v2-20260813-r2/WORKFLOW_SUMMARY.md) — fixed synthetic packets and one author-rater; useful for bounded schema/grounding checks, not a general reliability estimate.
- [Six-lens differentiation V2](results/lens-differentiation-v2-20260813/LENS_DIFFERENTIATION_RESULT.md) — fixed-packet lens separation.
- [Observation scenes round 4](results/lens-observation-scenes-20260813/ROUND_4_RESULT.md) — follow-up fixed scenes and local output closure.
- [Phase B sensitivity calibration](results/phase-b-calibration-v1-20260813/CALIBRATION_RESULT_V1.md) — synthetic task patterns did not meet the preregistered sensitivity gate.
- [Phase B impact result](results/phase-b-impact-v1-20260813/PHASE_B_RESULT.md) and [invalid first treatment batch](results/phase-b-impact-v1-20260813/TREATMENT_GENERATION_R1_INVALID.md) — null pilot plus excluded infrastructure evidence.
- [Phase B delta preflight](results/phase-b-delta-preflight-20260813/RESULT.md) — bounded setup evidence.
- [Codex Phase C smoke](results/phase-c-codex-smoke-20260813/SMOKE_RESULT.md) — one dated Windows host observation.

## Retained Shader summaries

- [Material routing](results/shader-router-material-v1-20260819/RESULT.md)
- [Prompt replay V1](results/shader-prompt-replay-v1-20260817/RESULT.md)
- [Grok medium six-lens replay](results/shader-prompt-replay-v1-20260817/execution-v6-grok-medium-all/RESULT.md)
- [Focused post-fix replay](results/shader-prompt-replay-v1-20260819/execution-v2-grok-medium-karis-postfix/RESULT.md)
- [Nudge interaction analysis](results/shader-nudge-interaction-v1-20260818/RESULT.md), with retained [metrics](results/shader-nudge-interaction-v1-20260818/metrics.json) and [annotations](results/shader-nudge-interaction-v1-20260818/annotations.json)

The current executable Shader protocols and tools live under `shader_prompt_replay/`, `shader_candidate_search/`, `shader_long_tail/`, and `nudge_interaction/`. Unity／URP Protocol V1 remains frozen. [Three.js／WebGPU Protocol V2](shader_long_tail/PROTOCOL_V2.md) is a separate draft whose domain fit remains unconfirmed until a baseline profiler identifies the dominant bottleneck. No production adapter is added unless an unchanged-domain smoke exposes a reproducible gap. New runs must use a new explicit output directory and must not overwrite a retained result.

## Separate observational archive

The Riemann run is history only in the fixed [tagged source tree](https://github.com/shihchengwei-lab/masters-nudge/tree/evidence-archive-2026-08-22/experiment/riemann-domain). It is a pre-question-contract observational pilot with incomplete delivery receipts: the current open-question output rule was added later, and only the final receipt-capable segment can distinguish generation from confirmed injection. It is not an active benchmark or current product validation.

## Claim boundaries

- Synthetic fixtures test behavior under fixed inputs; they do not establish field reliability.
- Phase B did not show a positive treatment effect. Its calibration and impact harnesses are closed.
- Human adjudication in retained pilots is limited and is not independent multi-rater validation unless a summary explicitly says otherwise.
- A generated finding, an injection receipt, and a later response are different events. Temporal association is not a causal effect size.
- Provider-reported usage and latency are descriptive for the recorded harness and version, not normalized price or future performance.
- Shader replay results do not establish Unity Asset Store readiness, cross-platform GPU performance, or visual equivalence outside their stated contract.
- Three.js／WebGPU source vocabulary does not itself prove that a workload belongs in the Shader domain. The frozen profiler gate owns that decision, and an adapter requires a separate observed runtime failure.
