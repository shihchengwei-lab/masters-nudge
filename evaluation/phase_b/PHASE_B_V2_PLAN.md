# Phase B V2 improvement plan — measurement before prompt changes

Status: Stage 1 executed and failed the synthetic-fixture viability floor on
2026-08-13. Phase B V1 remains frozen and is not regraded. Held-out V2 is paused
until consented, anonymized natural traces are available. See
`evaluation/results/phase-b-calibration-v1-20260813/CALIBRATION_RESULT_V1.md`.

## Decision

Do **not** change `buddy-prompt.txt`, the 42-character soft target, the 52-character hard cap, or the persona overlays yet.

Phase B V1 measured no benefit, but its task set had too little discrimination to identify the cause. The next work is therefore:

1. calibrate a task-and-oracle design that demonstrably has headroom;
2. apply that design to fresh held-out tasks;
3. test the current Nudge unchanged;
4. consider prompt or delivery changes only if the held-out measurement remains null.

This follows the official OpenAI eval guidance to use task-specific data, combine automated metrics with human judgment, calibrate automated scoring, and prefer comparative or pass/fail decisions over open-ended impressions: <https://developers.openai.com/api/docs/guides/evaluation-best-practices>.

## What V1 taught us

| Failure mode | V1 evidence | Consequence |
|---|---|---|
| Answer-shaped task leakage | `TASK.md` explicitly named most hidden requirements and often the corrective strategy | The control agent already received the substance of the Nudge |
| Ceiling effects | Four tasks passed 3/3 in both conditions | No remaining headroom for treatment to improve |
| Oracle overconstraint | Onboarding required the placeholder file itself to disappear, although reverting it removed the mechanism | A reasonable solution was scored as a full-task failure |
| Too few informative pairs | Only `last-query-wins` produced discordant pairs; total was one win and one loss | The paired gate was driven by one task's run variance |
| Observable overhead | Treatment tied quality while adding 9.7% cost and 11.2% wall time | Extra context has a measurable price when it adds no decision value |

The V1 result remains a valid null result for that frozen setup. These observations guide new fixtures; they do not change any V1 score.

## Stage 1 — task-sensitivity calibration (no product claim)

Build six calibration fixtures, one per lens. These fixtures are development instruments and will never be counted as V2 evidence.

### Continuation envelope

Each condition receives the same realistic checkpoint packet:

- original user objective;
- current candidate repository and diff;
- prior assistant checkpoint or completion claim;
- recent public-test/tool evidence;
- access to all repository evidence a real agent would have.

The packet must not contain a checklist that restates the hidden blind spot, corrective mechanism, verification method, or architecture boundary. Treatment is not used for this calibration.

### Calibration conditions

- `control`: neutral instruction to continue the current task.
- `positive_control`: the same instruction plus a direct, answer-shaped hint naming the target evidence or invariant. This is deliberately stronger than Masters' Nudge and is only used to prove that the task can respond to attention.

Run three repeats per task and condition: 6 tasks × 2 conditions × 3 repeats = **36 runs**.

### Fixture acceptance gates

A calibration pattern is usable only when all of the following hold:

1. Candidate public checks pass and the targeted hidden behavior fails.
2. A reference solution and at least one materially different acceptable solution pass.
3. At least two plausible near-miss mutations fail the intended component.
4. A baseline revert is graded according to its behavior, not file names or preferred syntax.
5. The control target succeeds in one or two of three repeats—neither 0/3 nor 3/3.
6. The positive control succeeds at least 2/3 and improves on control by at least one paired run.
7. A human traceability review agrees that the oracle follows from the user objective and visible repository evidence.

If a pattern fails, adjust task difficulty, evidence placement, or oracle semantics. Do not modify the product prompt to make a calibration fixture pass.

## Stage 2 — held-out Phase B V2 causal pilot

After all six calibration patterns pass, build **12 fresh tasks**, two per lens. They may reuse a workflow pattern but not calibration code, data, names, or outcomes. No main-agent run is allowed on these exact tasks before freeze.

### Task construction contract

- The user objective specifies the desired real-world outcome, not the answer.
- The incomplete candidate represents a plausible wrong workflow decision and remains public-green/target-red.
- The overlooked requirement is entailed by the objective plus visible repository evidence.
- The control agent can discover the issue, but the task packet does not say it verbatim.
- Prefer behavioral oracles. Static implementation checks are allowed only when the implementation constraint is itself part of the user contract.
- Every grader exposes a named `target_resolution` component and separate public/regression components.
- `safe_target_resolution` means the target component passes while all public/regression components remain green.
- Reference, alternative-solution, and near-miss mutation tests must pass before freeze.
- An independent traceability review should approve task-to-oracle alignment before execution.

### Lens patterns

| Lens | Held-out task shape |
|---|---|
| Jeff | Broad product objective; candidate treats a downstream symptom while repo evidence identifies an earlier bottleneck |
| Beck | Narrow behavioral request; candidate widens an adjacent surface that hidden compatibility fixtures protect |
| Fowler | Candidate makes one path correct while a future-change behavioral test reveals the missing knowledge boundary |
| Linus | Candidate satisfies a checklist or mock but fails the real clean execution path |
| Lamport | Candidate passes sequential examples but fails a forced interleaving or state-transition invariant |
| Carmack | Candidate improves a warm proxy while a representative cold/end-to-end measurement still misses the SLO |

### Treatment generation

- Generate one Nudge per held-out task with the current frozen General/persona prompts.
- Keep the 42-character soft target and 52-character hard cap.
- Apply the existing Phase A checks for grounding, workflow level, completeness, target alignment, and correct silence.
- Exclude an invalid treatment before any main-agent run; never rewrite it using downstream outcome knowledge.
- Freeze tasks, treatments, graders, analyzer, runner, hashes, seeds, model, and gates before execution.

### Formal run

- Conditions: `control` and current `treatment`; the Nudge block is the only difference.
- Main agent: the same Claude Sonnet alias and effort in both conditions.
- Repeats: three per task per condition.
- Total: 12 tasks × 2 conditions × 3 repeats = **72 runs / 36 matched pairs**.
- Randomize job order; use isolated repositories; prohibit steering, rescue, and selective retries.
- Archive every final workspace, diff, main-agent result, component outcome, cost, turns, and latency.

### Preregistered V2 gates

A positive V2 pilot signal requires every gate below:

1. **Integrity:** 72 unique expected rows, at least 70/72 valid agent transports, and 72/72 valid deterministic graders.
2. **Measurement headroom:** control `safe_target_resolution` is between 9/36 and 27/36 inclusive.
3. **Target efficacy:** treatment wins minus treatment losses on `safe_target_resolution` are at least 6 across 36 pairs.
4. **Full-task safety:** treatment full-task successes are not fewer than control successes.
5. **Breadth:** net target benefit is positive on at least 4/12 tasks and at least 3/6 lenses.
6. **No concentrated harm:** no task has treatment lose at least two of its three matched repeats.

Report component deltas, exact one-sided sign/binomial diagnostics, cost, turns, and latency, but do not substitute them for the gates. If the headroom gate fails, report the batch without drawing a prompt-effect conclusion.

## Stage 3 — prompt or delivery work, only on a declared trigger

Enter this stage only when Stage 1 passes and held-out V2 still has adequate headroom but fails the efficacy gates.

Then test one change at a time on new held-out tasks. The first recommended comparison is not a longer Nudge; it is the delivery contract:

- current: third-party observation, not an additional requirement;
- candidate: a hypothesis the agent must verify or reject with repository evidence before finalizing;
- optional placebo: an equal-length generic workflow reminder, to measure the effect of extra context alone.

Keep the Nudge content and 52-character cap fixed while testing delivery. Only after delivery is isolated should the General/persona wording be reconsidered.

## Cost and stopping boundary

Using the V1 observed mean of roughly USD 0.144 per main-agent run:

- calibration estimate: about USD 5.2; hard CLI safety ceiling USD 18;
- held-out V2 estimate: about USD 10.4; hard CLI safety ceiling USD 36.

Stop after calibration if fewer than four of the six lens patterns can meet the acceptance gates without answer leakage. That would indicate the present synthetic-fixture approach is not a credible impact instrument; the next source should be anonymized natural traces rather than further prompt tuning.

**Triggered 2026-08-13:** the frozen 36-run calibration had complete integrity
but accepted 0/6 patterns. Four were control-ceiling saturated and two exposed
overconstrained oracle semantics. A generous post-hoc semantic audit could raise
the result only to 1/6, so the stop boundary is robust. Do not revise and rerun
these micro-repositories; acquire natural traces before any held-out V2 work.

## Deliverables before any V2 task call

- calibration protocol and result;
- held-out task spec and task/oracle traceability matrix;
- oracle validation with alternative-solution and mutation coverage;
- frozen treatment registry and Phase A quality validation;
- V2 protocol with hashes, seeds, budgets, and gates;
- dry-run job manifest proving 72 expected rows.
