# Roadmap

Items kept after first-pass scope cuts. Each entry has a "why kept" line (the
reason the trade-off wasn't a flat "no") and a "trigger to actually do it" line
(the signal that turns this from someday-maybe into a real ticket).

The point of this file is to keep ideas warm without bloating v1. If you're
reading this much later and an item still has no trigger reached, that's
evidence to delete it, not to do it.

## Current product directions

### 1. Reaction quality and impact evaluation（短評品質與後續影響） — SYNTHETIC CALIBRATION STOPPED; NATURAL TRACES NEEDED

**Goal:** First establish that a Nudge is grounded and exposes a useful workflow
blind spot, then test whether injecting it changes the main agent's work for the
better. A good-sounding reaction is not the product outcome; the intended
outcome is a better decision by the combined user-and-agent workflow.

**Why now:** Lifecycle lens routing changed what the reviewer looks for, so the
trigger in item 5 has been reached. Cost telemetry only counts call outcomes; it
cannot tell whether a finding was correct or whether a lens improved the review.

**Phase A pilot result (2026-08-13):** Workflow Holdout V2 passed all eight
preregistered gates. The effective routed lenses found 24/24 seeded workflow
blind spots, produced 24/24 human-valid workflow-level complete Nudges, stayed
silent on 11/12 seeded-clean calls, emitted 0/24 local-artifact-only critiques,
and had no 52-character cap hits. The lone silence miss exposed contamination in
the supposedly clean YAML fixture and was still judged a defensible workflow
warning. The run used synthetic fixtures, two repeats, and one condition-blind
author-rater, so it is a pilot rather than a confirmatory benchmark. Full result:
`evaluation/results/workflow-v2-20260813-r2/WORKFLOW_SUMMARY.md`.

**Phase B V1 result (2026-08-13):** All 36 randomized main-agent jobs and graders
were valid, but treatment tied control at 13/18 full-task passes and 64/69
components. The 18 matched pairs produced one treatment win, one loss, and net
zero, so the preregistered positive pilot signal failed. Four tasks were
ceiling-saturated, onboarding exposed an overconstrained oracle, and only one
task produced discordance. Preserve V1 as a null pilot; do not interpret it as
evidence of harm or retune the General prompt against it. The next step is the
measurement-first calibration and held-out V2 plan in
`evaluation/phase_b/PHASE_B_V2_PLAN.md`.

**Task-sensitivity calibration result (2026-08-13):** All 36 control/direct-hint
runs and graders were valid, but 0/6 synthetic patterns met the preregistered
sensitivity gate (control 13/18, positive control 13/18; one paired win and one
loss). Four patterns were already 3/3 in control; the other two exposed oracle
overconstraint. Even a generous semantic reclassification yields at most 1/6,
below the 4/6 stop line. Do not proceed to held-out V2 or tune prompts against
these micro-repositories. Acquire consented, anonymized natural traces first.
Full result: `evaluation/results/phase-b-calibration-v1-20260813/CALIBRATION_RESULT_V1.md`.

**Phase A — reaction quality:** Build labeled evidence packets covering the
internal no-overlay baseline, the four lifecycle stages, both specialist
takeovers, and cases that should stay silent. Cover problem framing, assumptions,
sequence, scope, feedback, verification, reversibility, and stopping conditions;
retain explicit safety and completion-claim contradictions as stop-the-line
cases. Prefer packets with an objective oracle, but do not reduce the benchmark
to seeded code defects. Check schema compliance, evidence grounding, workflow
target identification, and correct silence automatically. Blind rubric-based
human adjudication asks whether the Nudge exposes a decision-relevant workflow
tension rather than merely naming a local code issue; record disagreement instead
of hiding it in one average score. Compare the internal baseline with the intended
lens under the same model and prompt budget. The baseline is not a user-selectable
mode.

**Phase B — reaction impact:** Start only after Phase A reaches a declared
quality floor. Run matched tasks from the same repository state with Nudge
injected in one condition and withheld in the other, keeping the main model,
task, tool budget, and acceptance criteria fixed. Repeat runs rather than
treating one stochastic trajectory as proof. Primary outcomes should be
checkable: hidden tests, removal of a seeded defect, satisfaction of explicit
requirements, absence of regressions, and evidence supporting the final claim.
Turns, latency, and diff size are secondary diagnostics, not standalone quality
scores. Blind human review is reserved for design decisions that have no honest
executable oracle.

Do not count the agent acknowledging a Nudge, an evaluator model preferring its
wording, or production telemetry correlations as proof of impact. Until Phase B
shows a repeatable difference, describe Masters' Nudge as increasing the chance
of noticing a different problem, not as proven to improve task outcomes.

### 2. Generalization（通用化） — ✅ SHIPPED 2026-08-13

**Goal:** Keep the review engine, evidence policy, lenses, output schema,
telemetry, and floating UI reusable while host-specific code becomes a thin
adapter. A normalized review event should carry the task anchor, checkpoint
reason, bounded evidence, session identity, and repository context without
requiring the core to understand one host's hook JSON.

**Result:** The Claude Code adapter and Codex CLI 0.147+ adapter now feed a
shared reviewer core through a normalized review event. The core owns evidence
packets, routing, prompts/lenses, provider calls, the 42-character completion
target and 52-character hard cap, structured output, storage, and telemetry.
Host adapters own only payload interpretation and delivery timing.

This satisfies the one real second agent gate rather than describing an
imagined adapter: a Codex CLI 0.147.0 live smoke
captured `UserPromptSubmit`, journaled a successful Bash `PostToolUse`, launched
Stop review off the critical path, and completed a real Anthropic reviewer call.
Shell and PowerShell installers, a Codex hooks snippet, host-namespaced neutral
data paths, legacy read compatibility, privacy disclosure, and regression tests
ship together. Details:
`evaluation/results/phase-c-codex-smoke-20260813/SMOKE_RESULT.md`.

**Compatibility boundary:** The tested Windows 0.147.0 build skipped native
`async: true` hooks, so Stop uses a detached-worker shim. It also did not emit
`PostToolUse` for a non-zero Bash result despite current documentation, making
immediate failure checkpoints best-effort on that build; Stop review still
runs. No Codex transcript parsing was added because its format is explicitly
not a stable hook interface.

### 3. Local reviewer interface（本地審查模型接口） — ✅ SHIPPED 2026-08-13 (EXPERIMENTAL)

**Result:** `ollama-local` provides an opt-in BYOM path shared by Claude Code
and Codex. Users select their own installed model; Masters' Nudge makes no size,
quality, performance, or licensing recommendation. The native Ollama adapter
reuses the same bounded evidence, lenses, output schema, 52-character cap,
storage, and telemetry as cloud providers.

Local mode is deliberately fail-closed: only loopback HTTP is accepted; client
proxies and redirects are disabled; Ollama must report cloud features disabled;
the selected model must have no remote metadata. Failure produces no Nudge and
never falls back to a cloud reviewer. Setup persists only after metadata
preflight and never installs, pulls, or chooses a model.

**Current boundary:** Interface compatibility is not a model-quality claim.
Comparative evaluation remains optional future work and does not gate access to
the experimental provider.

### 4. Cost control（成本控制） — SHADOW EVALUATION

**Goal:** Reduce review spend without lowering the finding quality floor.
Item 10 already records call outcomes, token/cache metadata, and candidate skip
conditions for a fixed seven-day window with a 300-call target.

**Decision rule:** Any candidate call that produces a finding is a
`shadow_fail`. Errors and insufficient samples cannot justify activation.
After the report exists, consider only narrow, reversible gating backed by that
evidence. Prompt/context reduction or a cheaper model also requires the reaction
quality eval in item 5; lower token count alone is not proof of preserved quality.

**Current boundary:** Live gating remains off. The shadow window never extends
or enables skipping automatically, and no model downgrade is scheduled.

The remaining evidence work below is **5. Reaction quality and impact
confirmation** plus the optional **11. Local reviewer quality evaluation**. Item 5's Phase A,
Phase B V1, and task-sensitivity calibration are complete. The calibration hit
the preregistered stop rule: synthetic micro-repositories are not discriminating
enough for held-out V2. The current General prompt remains frozen and V2 waits
for consented, anonymized natural traces. Repairing the contaminated clean case
and obtaining an independent rater remain useful Phase A confirmation work.
Items 2 and 3 ship as an unreleased dual-host plugin prerelease. Item 11 is not
scheduled and is not a shipping gate; it becomes product work only if the project
later wants to publish model recommendations. Everything else below is either
shipped or explicitly cut from scope.

## 1. Floating window UI — ✅ SHIPPED 2026-05-09

`buddy_window.py` + `start_buddy_window.bat`. Single-file Tk app, watches
`~/.masters-nudge/data/` plus legacy `~/.claude/buddy/` and tails the
most-recently-modified per-session log file.
Pinned to bottom-right, always on top. Switches automatically when a different
session's log gets newer activity.

Hook delivery works via `UserPromptSubmit hook success:` system-reminder
messages — main Claude sees the injected reaction in its context, but
system-reminders don't render in the user's terminal. The floating window
is the user's only direct visibility channel. Runtime lens selection and
beginner-friendly focus labels were added later under item 9.

## 2. Plugin format packaging (`plugin.json`) — ✅ SHIPPED 2026-08-13 (PRERELEASE)

**Result:** Claude Code and Codex now install from native repository
marketplaces in two commands. The managed package owns its hooks, skills, core,
prompts, personas, UI assets, and platform launchers, so new users no longer
clone the repository or merge JSON by hand. A deterministic build check keeps
the packaged runtime aligned with canonical source files. This installation improvement
covers both supported hosts.

The default reviewer follows the already-authenticated host (Claude → Anthropic
`sonnet`; Codex → OpenAI `gpt-5.6-sol`) unless explicitly overridden. Bundled
skills provide model-free diagnostics, optional UI launch, and a conservative
legacy-hook migration that dry-runs first, removes exact known entries only,
creates backups, and preserves runtime/data.

Claude and Codex manifest validation, package-drift tests, migration tests, and
Linux/macOS/Windows CI cover the distribution path. Shell and PowerShell
installers remain compatibility options. Version `0.1.0-dev.2` is intentionally
not tagged or released yet.

## 3. Mid-work checkpoint gating — ✅ SHIPPED 2026-08-11

`checkpoint.py` + `checkpoint.sh` add synchronous, non-blocking Masters’ Nudge reviews inside a
long agentic turn. The local classifier calls the reviewer only for tool errors, test
failures, or the first working-tree total above 80 changed lines. Exact repeats
are deduplicated per session. There is deliberately no time cooldown.

Checkpoint reactions return directly to the main agent through
`additionalContext`; they are not written to the user-facing floating-window
log. The existing asynchronous Stop path remains as supplementary review.

## 4. Multi-model switching — ✅ SHIPPED (cross-vendor + local BYOM)

`MASTERS_NUDGE_PROVIDER` (legacy alias `BUDDY_PROVIDER`) routes between Anthropic (`claude -p`) and OpenAI
(`codex exec`). Host-aware defaults avoid a second login: Claude uses Anthropic
`sonnet`, while Codex uses OpenAI `gpt-5.6-sol`. An explicit provider/model
override still supports cross-vendor review. Experimental `ollama-local` uses a
user-selected model on a validated loopback Ollama server and has no default
model or cloud fallback.

Smart routing (different models per turn type) remains cut: checkpoint reasons
select when to review, not which model to use. The configured provider remains
stable while the lifecycle router selects the engineering lens.

## 5. Reaction quality and impact eval — SYNTHETIC CALIBRATION STOPPED; NATURAL TRACES NEEDED

**Why kept:** Currently no measurement of whether Masters’ Nudge reactions are
reliable or whether the main agent makes a better decision after receiving one.
Could borrow `cold-eyes-reviewer`'s case-fixture structure, but subjective score
cards must not be the primary evidence. The cost shadow telemetry in item 10
measures call outcomes and possible skip conditions; it establishes neither
reaction correctness nor downstream impact.

**Trigger reached:** Lifecycle lens routing changed the engineering lenses on
2026-08-12. Build the baseline before refactoring the core or evaluating a
different reviewer model.

**Phase A completed:** The 2026-08-13 Workflow Holdout V2 result passed all eight
declared quality gates. Replace or repair the YAML clean fixture, add natural
project traces, and obtain an independent condition-blind rating in later
confirmation work; these limitations bound the claim but do not block the frozen
Phase B pilot. Do not tune the current prompt against the pilot again.

**Six-lens differentiation explored:** On one fixed, non-terminal checkpoint,
all 18 production reviewer calls were valid and yielded distinct wording. Jeff,
Beck, Linus, Lamport, and Carmack stayed on their declared attention area in 3/3
repeats; Fowler did so in 1/3 and otherwise overlapped Jeff's responsibility-
boundary concern. Six unedited distinct representatives exist and are shown by
real Tk windows in the README hero, but the preregistered reliability claim
remains 5/6 rather than 6/6. Four lines hit 52 characters and three were
incomplete. See
`evaluation/results/lens-differentiation-v2-20260813/LENS_DIFFERENTIATION_RESULT.md`.

**Phase A — quality:** Use fixed, labeled evidence packets with known workflow
blind spots or verified no-Nudge cases. Cover framing, assumptions, order, scope,
feedback, verification, reversibility, and stopping conditions, with explicit
safety and evidence contradictions retained as objective stop-the-line cases.
Automatically check schema compliance, grounding, target match, and correct
silence; do not let seeded code defects stand in for workflow-review quality.
Compare the internal no-overlay baseline with the intended lens while keeping
the reviewer model, prompt budget, and output contract fixed. Blind human
adjudication evaluates whether each reaction exposes a decision-relevant tension
and reports inter-rater disagreement. The baseline is not exposed as a product
mode.

**Phase B — impact:** For reactions that pass the quality floor, run paired
agent tasks from identical starting states with injection enabled or withheld.
Use hidden tests, seeded issues, explicit acceptance checks, regression checks,
and support for the final completion claim as primary outcomes. Hold the main
model and task budget constant, randomize or alternate condition order, and run
enough repeats to report a distribution rather than a showcase. Use blind human
review only where no executable oracle can represent the design trade-off.

**Phase B V1 completed:** The frozen 36-run pilot tied at 13/18 full-task passes
with one paired win and one paired loss. Its integrity gates passed, but its
efficacy and breadth gates failed. Because four tasks saturated at the ceiling
and one oracle overconstrained an acceptable revert, V2 begins with a separate
task-sensitivity calibration rather than a prompt edit. See
`evaluation/results/phase-b-impact-v1-20260813/PHASE_B_RESULT.md` and
`evaluation/phase_b/PHASE_B_V2_PLAN.md`.

**Stage 1 calibration completed:** The frozen direct-hint calibration preserved
36/36 transport and grader integrity but accepted 0/6 patterns, below its 4/6
viability floor. Four control conditions saturated at 3/3; two remaining
patterns contained overconstrained oracle semantics. A post-hoc audit does not
rescue viability (at most 1/6), so held-out V2 is paused pending natural traces.
See `evaluation/results/phase-b-calibration-v1-20260813/CALIBRATION_RESULT_V1.md`.

**Claim boundary:** Agent acknowledgement, evaluator-model preference, fewer
turns, smaller diffs, or observational production telemetry cannot by themselves
show that Nudge improved the result. Product claims remain conservative until a
repeatable controlled difference is observed.

## 6. Background mode — ✅ SHIPPED 2026-05-09

Uses Claude Code's native `async: true` hook setting. `buddy.sh` runs
synchronously; background execution is managed by the framework. Timeout and
lifecycle are handled by Claude Code, not shell-level forking.

## 7. Event-centered source evidence packets — ✅ SHIPPED 2026-08-11

`source_context.py` gives Stop and checkpoint reviews the same lens-neutral
source-selection layer. `UserPromptSubmit` stores a bounded task anchor and the
prompt-time transcript byte offset. Checkpoints receive the anchor, triggering
event, and small recent-agent context; Stop receives the anchor, direct final
claim, current-turn tool evidence, and named agentcam evidence sections.

Long fields keep their head and tail with an explicit middle-cut marker. The old
6000-character rolling transcript remains only as a Stop fallback when no
final-claim, tool, or agentcam evidence is available.

## 8. Pet-style UI — ✅ SHIPPED 2026-05-09

`buddy_window.py` now includes Rook, an animated raven companion, alongside the
speech bubble. The 2x6 transparent spritesheet provides idle and review rows,
is draggable, always on top, runs at 4fps, and follows the active session.
The outer-window background follows the effective lens while Rook remains
graphite black. Legacy `BUDDY_SPRITE_PATH` overrides remain compatible.

## 9. Lifecycle lens routing — ✅ SHIPPED 2026-08-12

The floating window offers Design, Build, Evolve, and Review stages. These map
to Jeff Dean, Kent Beck, Martin Fowler, and Linus Torvalds. Build is the default;
General remains the shared workflow-evidence and stop-the-line base rather than a
selectable stage. Stop and checkpoint reviews use the same local, deterministic
router without an extra model call.

High-confidence state/ordering evidence temporarily selects Leslie Lamport;
measured execution-cost evidence temporarily selects John Carmack. A temporary
specialist does not change the saved stage, and Lamport wins a simultaneous
match. Reaction logs and telemetry record the primary and effective lens,
trigger, stage, and route source. `BUDDY_PERSONA`, existing persona configs, and
old log entries remain compatible.

## 10. Bounded cost shadow evaluation — ✅ SHIPPED 2026-08-11 (enforcement off)

`review_telemetry.py` records content-free metadata for Stop and checkpoint
model calls, including outcome status, latency, source fingerprint, and token /
cache usage when the CLI exposes it. It does not store prompts, transcripts,
tool results, or finding text.

The first review starts a fixed seven-day shadow window with a 300-call target.
Potential `no_new_evidence` and `checkpoint_stop_overlap` skips are observed
only; every review still runs. Any candidate call that produces a finding is a
`shadow_fail`. At the deadline, the next review writes
`shadow-evaluation.md` and emits one notice, even when the sample is
insufficient. The evaluation never silently extends and never enables skipping automatically.

**Next decision:** Review the generated report manually. Live cost gating needs
explicit approval after the evidence window; it is not a current implementation
task merely because telemetry is present.

## 11. Local reviewer quality evaluation — OPTIONAL; NOT A SHIPPING GATE

**Why kept:** A local reviewer could avoid a second cloud egress and may reduce
per-call cost and latency. Those benefits matter only if review quality remains
useful.

**Interface shipped:** The experimental Ollama adapter is available as BYOM
without prescribing model size. The shared reviewer core and provider boundary
allow a later benchmark to reuse item 5's fixtures and score card without
changing the runtime interface.

**Future evaluation:** If the project later publishes recommended models, each
candidate should meet an explicit quality floor for correct findings, correct
silence, schema compliance, and latency. Until then, do not claim that any
parameter count or hardware setup provides adequate review quality.

---

## Cut from scope (recorded so they don't come back accidentally)

These were considered and removed by the user during the v1 scope discussion:

- **Cross-session memory** — Masters’ Nudge doesn't need to remember things across days;
  one-turn reactions are enough.
- **Lens-selection CLI** — the floating-window selector covers normal use; a
  separate CLI layer adds surface area for no real benefit.
- **buddy.log dashboard** — JSONL 可以直接看，trigger 沒到過，log 量不大。
- **Smart model routing** — reason-based 路由被明確拒絕，trigger 是場景上下文不是路由信號。
- **Built-in custom lens/rule management** — this is an open-source prompt-based
  tool. Users who need different rules can edit or fork `buddy-prompt.txt` and
  `personas/*.txt`; a loader, marketplace, merge policy, and management UI would
  add product surface without improving the core review loop.
