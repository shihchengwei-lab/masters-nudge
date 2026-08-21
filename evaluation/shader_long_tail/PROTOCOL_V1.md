# Shader Long-tail Trajectory Protocol V1

Status: draft preregistration. The early-baseline choice is approved; freeze the
execution manifest before starting the Shader Codex session or making provider
calls.

This protocol evaluates whether one C-only Masters' Nudge session can preserve
verified progress and continue producing useful research late in a fixed Shader
search. It does not include a no-Nudge control and therefore cannot establish a
causal treatment effect.

## 1. Question

Starting from the frozen early Shader baseline, can the session:

1. keep every accepted Pareto frontier checkpoint reproducible and non-regressing;
2. continue producing measured frontier or knowledge gains in candidates 26-50;
3. show time-ordered, content-matched associations between injected Nudges and
   later productive research decisions; and
4. reach the 30%, 50%, or 70% GPU-improvement tier without weakening any fixed
   visual, functional, resource, or measurement contract?

The final report must separate product outcome, search trajectory, Nudge
interaction, provider reliability, and causal limitations.

## 2. Frozen starting point

- Source repository: `E:\projects\shader-lab`
- Test start commit: `cacae3e08cbcc293698b68fb76141ad63cfacea1`
- Frozen `BaselineV0` commit referenced by the contract:
  `745848dbb9663bc69ff78eb5e5dede77ae6b83e2`
- Reason for selecting the start commit: it freezes the early benchmark baseline
  and predates the later Pareto-search result and delivery commits.
- The current `E:\projects\shader-lab` working tree was dirty when this protocol
  was written on 2026-08-18. It must not be reused directly.
- Execution must use a new clean worktree at the exact start commit. The run
  manifest must record its absolute path and confirm an empty `git status
  --short` before the Goal begins.
- No previous candidate result, Nudge annotation, final report, or later source
  implementation may be copied into the clean worktree.

The early contract fixes Unity `6000.0.80f1`, URP `17.0.4`, D3D11, 1920x1080,
the Intel UHD acceptance adapter, `ShieldGalleryV1`, five repetitions, 300 warmup
frames, and 1,200 sampled frames. These fields remain immutable.

## 3. Outcome-only Goal

Give the main model only this Goal:

> 交付在固定視覺與量測契約下，經實證建立且可重現的最佳 Shader Pareto 前沿，並保留足以重現候選判定的研究紀錄。

Do not mention Masters' Nudge, Persona, the evaluation rubric, expected Nudge
reactions, or the 30/50/70 scoring bands in the session prompt. Search governance
belongs in repository contracts and ledgers, not in the Goal wording.

## 4. Fixed run configuration

The execution manifest must freeze these values before the session starts:

- main model, model version, reasoning effort, and Codex CLI version;
- Grok subscription CLI version, resolved model, and `medium` reasoning effort;
- checkpoint provider timeout: 90 seconds;
- stop provider timeout: 120 seconds;
- automatic evidence-strength Shader routing, with no manual lens rotation;
- no Persona quota, balancing, cooldown, or expand/deepen/guard ratio controller;
- semantic Shader review trigger from only:
  `benchmark/architecture-contract.json`,
  `benchmark/architecture-experiments.json`, and
  `benchmark/architecture-result.json`;
- one active detached strategy review per session;
- target adapter identity, driver, resolution, scene, build, warmup, samples, and
  repetitions;
- candidate budget, refinement budget, and wall-time policy.

Any mid-run change to these values invalidates direct comparison across the
affected boundary and must be reported rather than silently normalized.

## 5. Git-like research state

This protocol borrows Git's checkpoint model without giving Masters' Nudge
permission to commit, switch branches, or modify the Shader repository.

- **Frontier checkpoint:** an accepted, fully measured, reproducible Pareto state.
- **Candidate branch:** one experiment derived from a declared parent frontier.
- **Rejected branch:** a failed or dominated candidate whose evidence is retained;
  rejection returns research HEAD to its parent frontier.
- **Promotion:** only a candidate that passes every invariant and is non-dominated
  may become a new frontier checkpoint.

A failed experiment is not backward motion when its evidence is retained and the
frontier is not replaced. Backward motion means accepting a regression, weakening
the contract, losing traceability, or repeating a falsified direction without a
new discriminating variable.

Every candidate record must contain:

- stable candidate ID and parent frontier ID;
- bottleneck-hypothesis family and falsifiable statement;
- evidence supporting the hypothesis;
- work-elimination mechanism family;
- concrete GPU work expected to disappear;
- changed variable and discriminating measurement for refinements;
- contract fingerprint and source fingerprint;
- compile, visual, temporal, GPU, resource, and profiler evidence;
- decision, rejection reason, and trajectory classification;
- Nudge IDs injected before the next two research decisions, when present.

Use the distinct-cell and refinement rules in
`evaluation/shader_candidate_search/PROTOCOL_V1.md`. Synonyms or parameter-only
variants do not create new candidate slots.

## 6. Trajectory classification

Classify every completed research decision once:

| Code | Meaning | Required evidence |
| --- | --- | --- |
| `F2` | Frontier gain | A new eligible, non-dominated point passes every fixed contract gate. |
| `F1` | Knowledge gain | A preregistered falsifiable hypothesis is decisively rejected, a supported cell is eliminated, or a required unknown is resolved by measurement. |
| `N` | Neutral | Noise-overlapping, incomplete, duplicate, or non-discriminating work that changes no research decision. |
| `B` | Backward | Contract weakening, promoted regression, lost provenance, or repetition of a falsified cell without a new discriminant. |

Merely running a benchmark does not qualify as `F1`. The result must close a
declared uncertainty or eliminate a supported option.

## 7. Search budget and stopping

- Maximum: 50 accepted, technically distinct search cells.
- Refinements remain separate from the 50-cell count and use the refinement
  budget frozen in the execution manifest.
- Invalid, duplicate, or same-cell proposals remain in the rejection ledger and
  do not advance the candidate number.
- The session may not stop because three consecutive candidates add no Pareto
  point. This protocol overrides only that early stopping rule from the old
  baseline contract; all product and measurement invariants remain fixed.

Early saturation requires all of the following:

1. at least eight distinct work-elimination mechanism families were measured;
2. the latest eight eligible distinct candidates each improve the relevant
   frontier metric by less than 0.5%;
3. their confidence intervals overlap the current frontier;
4. profiler evidence continues to identify the same remaining bottleneck;
5. the planned hypothesis/mechanism coverage map contains no evidence-supported,
   unvisited cell; and
6. every frontier point has the required five acceptance-hardware repetitions.

If any condition is missing, run to 50 cells. Reaching 50 means
`candidate-limit-exhausted`, not proven global saturation.

## 8. Product outcome tiers

Primary improvement is measured against the freshly reproduced `BaselineV0`
gallery incremental GPU-time median:

`improvement = 1 - candidate_gallery_median / baseline_gallery_median`

- Tier 1: at least 30% improvement.
- Tier 2: at least 50% improvement.
- Tier 3: at least 70% improvement.

No tier is valid unless the candidate also passes the unchanged p95, visual SSIM,
maximum channel error, temporal, VRAM, draw-call, overdraw, shader-variant,
package-size, compile, target-device, and clean-import gates. Report confidence
intervals and raw samples; a point estimate alone does not earn a tier.

## 9. Long-tail trajectory gates

The run passes the trajectory-integrity gate only when:

- 100% of completed candidates have a parent, mechanism, evidence, and decision;
- no promoted frontier checkpoint is dominated by its parent;
- no benchmark or visual contract fingerprint changes;
- `B = 0`; and
- candidates 26-50 contain `F1` or `F2` in at least 30% of completed distinct
  cells.

Also report, but do not silently optimize against:

- early productive rate: `(F1 + F2) / completed cells 1-25`;
- late productive rate: `(F1 + F2) / completed cells 26-50`;
- retention: `late productive rate / early productive rate`;
- frontier additions and mechanism-family coverage by half;
- neutral work, rejected refinements, and eliminated alternatives.

The preregistered retention diagnostic is 0.60. Missing the diagnostic is a
reported long-tail weakness, not permission to reinterpret an `N` step as `F1`.

## 10. Nudge interaction analysis

Use review telemetry for provider calls, delivery receipts for injection state,
and human annotation for observable reaction. These sources cannot substitute
for one another.

For each successfully injected Nudge with subsequent observable behavior, examine
the next two research decisions:

1. injection occurred before the decision;
2. the Nudge content matches the later hypothesis, mechanism, measurement, or
   invariant;
3. compared with the plan visible immediately before injection, the later decision
   adds a control variable, boundary case, measurement, mechanism split, revised
   interpretation, or follow-up that pushes the existing correction farther; and
4. the resulting decision is classified `F2`, `F1`, `N`, or `B`.

A Nudge does not need to precede candidate selection or invent the next direction.
It remains evaluable when it arrives after a direction has started but before a
decision that can still be deepened. Merely continuing the pre-injection plan is
`temporal_only`, even when the content is adjacent.

Reuse the five reaction categories in
`evaluation/nudge_interaction/ANNOTATION_PROTOCOL_V1.md`:
`explicit_uptake`, `reinterpretation`, `possible_influence`, `temporal_only`, and
`no_observable_response`.

Report:

- provider attempts, findings, no-findings, errors, timeouts, and latency;
- generated, pending, injected, expired, and superseded delivery states;
- evaluable injected Nudges and reaction categories;
- productive association: content-matched reaction followed by `F1` or `F2`;
- productive association by `expand`, `deepen`, `guard`, and Persona;
- repeated semantic blind spots that add no new discriminant; and
- early-half versus late-half productive association.

With no no-Nudge control, names such as “causal success rate” are prohibited.
The strongest permitted conclusion is “possible influence” supported by time
order, content match, pre/post behavior change, and a productive decision.

If fewer than ten injected Nudges have observable follow-up, the interaction
result is underpowered and must be reported as inconclusive rather than zero.

## 11. Preflight evidence

The 2026-08-18 bounded Grok medium smoke used the current Shader base prompt and
Carmack Persona with one frozen packet and three sequential calls:

- 3/3 findings, 0 timeout;
- 50.274-68.163 seconds observed latency;
- all findings were complete, non-imperative, and within 52 characters; and
- all three findings converged on the same cost-transfer blind spot.

Evidence:
`evaluation/results/shader-grok-smoke-20260818-medium-carmack/`.

This proves neither tail latency nor live semantic-projection quality. The run
manifest must perform a transport/auth preflight immediately before the live
session and must retain all provider failures in the denominator.

## 12. Required artifacts

Freeze before the Goal starts:

- `run-manifest.json` with every version, hash, timeout, budget, path, and device;
- baseline raw samples, visual golden sequence, and adapter proof;
- hypothesis/mechanism coverage map;
- candidate/refinement ledger schema; and
- exact analysis and annotation scripts or their hashes.

Retain after the run:

- all candidate and refinement records, including failures;
- raw benchmark and visual samples;
- every frontier checkpoint and parent relation;
- Nudge telemetry, delivery receipts, provider errors, and annotations;
- early/late trajectory analysis;
- product-tier result; and
- an explicit list of unverified human, marketplace, platform, and causal claims.

## 13. Final comparison table

The final report must fill this table without changing the definitions above:

| Measure | Preregistered requirement | Observed | Result |
| --- | --- | --- | --- |
| Clean early start | exact `cacae3e08c...`, clean worktree |  |  |
| Contract integrity | no fingerprint change |  |  |
| Candidate traceability | 100% |  |  |
| Backward steps | `B = 0` |  |  |
| Late productive rate | at least 30% |  |  |
| Early-to-late retention | at least 0.60 |  |  |
| Mechanism coverage | at least 8 families for saturation |  |  |
| Stop condition | formal saturation or 50 cells |  |  |
| Nudge interaction power | at least 10 evaluable injections |  |  |
| Provider reliability | disclose all attempts and timeouts |  |  |
| GPU improvement tier | 30% / 50% / 70% |  |  |
| Fixed quality/resource gates | all pass |  |  |
| Causal claim | prohibited without a control |  |  |
