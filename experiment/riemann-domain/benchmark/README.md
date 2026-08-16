# Riemann-domain observational benchmark

> **Disclaimer:** This benchmark summarizes AI-generated research and workflow
> records. The Riemann hypothesis remains unsolved. Publication and formatting
> do not endorse the mathematical correctness, completeness, route closures,
> reductions, certificates, or conclusions in the archived material. See the
> [full bilingual disclaimer](../README.md#disclaimer--免責聲明).

## Result at a glance

This experiment documents repeated cases consistent with an injected Nudge
influencing the main agent's next operation. It is not a controlled efficacy
benchmark.

| Question | Observed result |
|---|---|
| How large was the full experiment? | 102 Nudge findings across 3 sessions |
| How many findings were generated after receipt tracking existed? | 19 |
| How many were confirmed in the main model's context? | 17 |
| How many traceable interactions had a direct, reframed, or delayed response? | 13 of 17 |
| Was every Nudge adopted? | No; the set includes challenges, ambiguous timing, and non-adoption |
| Does this estimate causal efficacy or validate the mathematics? | No; there was no control arm or mathematical peer review |
| Did the run prove RH? | No |

The distinction between 102 and 17 is essential. The 102 findings describe the
full operational run, including lens distribution and reviewer failures. Only
the final receipt-capable segment supports reliable finding-to-response pairing:
19 findings were generated, 17 have both an injection receipt and a matching
transcript message, and 2 had no receipt observed before the log ended. Earlier
findings may have influenced the run, but the available records cannot establish
their delivery and pair them to later behavior with the same confidence.

Among the 17 traceable cases, visible next steps included rereading missed
state, correcting a broken file loop, replacing literature search with a
numerical stress test, turning prose gaps into quantified lemmas, abandoning a
circular family of RH-equivalent criteria, and auditing a premature Goal
completion. See the [complete interaction table](interactions.md).

## Terms used in this report

- **Finding / Nudge:** the reviewer's short observation returned to the main
  model.
- **Lens:** the mathematical persona used to frame that observation.
- **Receipt:** a record confirming that a Nudge was injected into the main
  model's context; it does not prove the Nudge was read or adopted.
- **Response:** the first visible assistant statement or operation after a
  confirmed injection.
- **Stop review:** a review triggered when one work turn ends, not necessarily
  when the long-running Goal stops.
- **Checkpoint review:** a review triggered during a long task, before its final
  turn.

## What was measured

- Observation window: 2026-08-14 08:34 through 2026-08-16 11:17 (local time).
- Three Codex CLI research sessions in one workspace.
- Reviewer: Anthropic `claude-opus-4-6`.
- Unit of analysis: one reviewer finding, status event, or delivery receipt.
- Main-agent response: the first visible assistant statement or operation after
  an injected Nudge in the final session transcript.
- No control arm, randomization, blinded scoring, or claim that the mathematical
  content is correct.

The frozen, path-neutral records are in
[`snapshot/reactions.jsonl`](snapshot/reactions.jsonl); aggregate counts are in
[`snapshot/summary.json`](snapshot/summary.json). [`export_snapshot.py`](export_snapshot.py)
documents exactly how the local logs were filtered and de-identified. The
[complete 17-event table](interactions.md), including non-success cases, is
generated from the machine-readable
[`interaction_annotations.json`](interaction_annotations.json). Four
consequential route closures, their narrow claims, full arguments, and
standalone exact/interval verifiers are curated under
[`closures/`](closures/README.md).

## Aggregate results

| Measure | Result |
|---|---:|
| Total records | 142 |
| Findings | 102 |
| Reviewer status/failure events | 23 |
| Delivery receipts | 17 |
| Confirmed injected receipts | 17 |
| Findings generated after receipt tracking existed | 19 |
| Generated findings with no receipt observed before log end | 2 |

Finding reasons: 83 Stop, 13 long-task strategy, 3 large-diff, 2 test-failure,
and 1 Goal-transition review.

Lens distribution was highly imbalanced: Selberg 78, Tao 16, Riemann 4, Erdős
3, Pólya 1, and Ramanujan 0. This is a product finding, not evidence that
Selberg was intrinsically best. The early evidence router over-selected analytic
estimate language; the later dynamic routing/cooldown revision made Tao and
Erdős visible, but did not yield balanced coverage.

Reviewer reliability was also material: 11 checkpoint calls timed out at 60
seconds, 6 Stop calls timed out at 180 seconds, and 6 calls failed for another
provider/harness reason. These failures produced explicit status entries rather
than silent Nudges.

The 17 transcript-visible injections were manually coded as 10 immediately
direction-aligned responses, 2 explicit engagements that corrected/reframed the
Nudge, 1 delayed adoption, 2 concurrency-ambiguous cases, and 2 not-adopted or
too-late cases. Thus 13/17 showed an observable direct, reframed, or delayed
response under this rubric; this is descriptive annotation, not a causal effect
size. The denominator is the receipt-capable final segment, not all 102 findings.

## Representative Nudge → response cases

These are temporal observations from the receipt-capable final session. “Next
response” is not proof of exclusive causation; it shows what entered context and
what the main agent generated immediately afterward.

The table below is a representative subset. All cases, including ambiguous and
negative observations, appear in the [complete 17-interaction table](interactions.md).

| Nudge | Observable next response | Assessment |
|---|---|---|
| The loop always typed `HANDOFF.md`; four files were never read. | Replaced the loop with explicit reads of the four missing state/audit files. | Direct correction |
| Three literature checks produced no bound; construct or numerically refute polynomial `K` before another search. | Explicitly stopped expanding literature search and launched an AP2 coefficient-cost stress test. | Direction change |
| Doubling `N` at `T=16` barely changed residual L2; test convergence before blaming conditioning. | Ran the same experiment at `N=64` and `N=256`. | Direct experiment |
| “Global one-sided interpolation” was only a label; state a falsifiable quantified claim. | Recast the survivor as a fixed Riesz–Möbius mollifier with explicit parameters and an L2 limit. | Obligation formalized |
| Write the CD quadratic-form bound as an explicit computable inequality. | Produced a finite-cutoff prime/continuum centered square and fixed the order of quantifiers. | Obligation formalized; concurrency may confound timing |
| Test whether block energy actually decays before inventing another mechanism. | Explicitly adopted the stress-test order and computed real-zeta block energies. | Direction change |
| The Nudge inferred that the measured rate disproved exponential decay. | The main agent rejected that inference, explained the actual subexponential criterion, and changed to dyadic min/median/max. | Useful challenge, Nudge conclusion not accepted |
| Repeated producers may share a structural failure; another mean candidate may repeat it. | Stopped testing normalized/stationary means and pivoted to anchored finite-height obligations. | Route pruning |
| Three equivalences all pass through residue exclusion and therefore merely restate RH. | Explicitly stopped adding residue-equivalent criteria and moved to an independently testable relative-clock lemma. | Circularity stopped |
| Goal was marked complete without proof, strongest-route exhaustion evidence, or a resumable handoff. | Audited the named terminal sections before finalizing; final response explicitly stated that RH was not proved. | Goal boundary review |

Two counterexamples to a simplistic success narrative are retained: one Nudge
arrived while related work was already in flight, and the last Nudge arrived
after the Goal had effectively stopped. Receipt proves delivery, not novelty,
attention, correctness, or exclusive causation.

## Concrete outcomes of the experiment

The useful result is not a claimed RH proof. It is a set of workflow outcomes:

1. Bounded third-party observations were repeatedly accepted as the next
   operation without transferring control of the research task.
2. The main model sometimes challenged a faulty Nudge instead of blindly
   following it, which is the intended “influence, not command” behavior.
3. Delivery receipts eliminated the earlier ambiguity between reviewer output
   and context actually injected into Codex.
4. Long-task checkpoints caught repeated search, proxy work, vague obligations,
   circular reformulations, and premature Goal completion—issues that a Stop-only
   reviewer observed too late.
5. The experiment exposed two product defects: lens monopoly under keyword-heavy
   routing and reviewer latency/failure high enough to require explicit status
   handling and detached delivery.

## What this benchmark does not establish

- It does not show that Masters' Nudge increases the probability of proving RH.
- It does not compare against the same task without Nudges.
- It does not validate any mathematical claim produced by either model.
- It does not treat token count, elapsed time, or number of files as progress.
- It does not generalize the math-domain lens distribution to the shipped
  software-engineering personas.

A future controlled benchmark would replay fixed evidence packets or run paired
long tasks with seeded checkpoints, then blind-score direction changes, accepted
corrections, false-positive disruption, latency, and verified delivery.
