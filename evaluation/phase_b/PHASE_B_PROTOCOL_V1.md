# Phase B downstream-impact pilot V1 — preregistered protocol

Frozen before the first main-agent task run on 2026-08-13 (Asia/Taipei).

## Question and claim boundary

Does injecting one evidence-grounded Masters' Nudge after an incomplete candidate change make the main coding agent more likely to satisfy the full task, compared with continuing from the identical repository state without the Nudge?

The pilot tests downstream task outcomes, not whether the agent mentions, agrees with, or appears to follow the Nudge. A positive result is evidence for a larger confirmatory study, not proof of broad product impact. A null result can mean no causal benefit under this setup or insufficient headroom/power; it does not invalidate Phase A reaction quality.

The design follows the outcome emphasis in [official OpenAI model guidance](https://developers.openai.com/api/docs/guides/latest-model): compare representative matched tasks on task success, final completeness, and required evidence; treat tokens, latency, calls, and turns as improvements only when quality still passes.

## Candidate version and delta preflight

The Phase B prompt candidate contains the 42-character soft target and 52-character hard cap. Its 17-call delta preflight produced seven effective findings that were all grounded, workflow-level, aligned, and complete, with zero hard-cap hits. Five of seven were at most 42 characters; the preregistered soft-adherence floor was six, so that diagnostic formally missed. The two misses were complete 43- and 44-character sentences. The prompt was not retuned against those cases and proceeds with the miss disclosed.

One initial Jeff treatment for `ownership-role-store` reached 52 characters and ended mid-phrase. It was excluded without retry or manual rewriting before main-agent runs began. A new, separately validated Jeff task (`onboarding-problem-location`) replaced the whole task and received one fresh 40-character treatment. The excluded Nudge and task are not part of this experiment.

## Frozen tasks

Six independent Python repositories cover one task per lens:

| Task | Lens | Seeded candidate blind spot | Objective completion signal |
|---|---|---|---|
| `onboarding-problem-location` | Jeff | Reminder mechanism precedes use of funnel/support evidence | Documented phone formats normalize; invalid inputs fail; reminder mechanism removed |
| `csv-scope-control` | Beck | Requested CSV change expands into unrelated JSON rewrite | Delimiter behavior passes and JSON remains byte-for-byte compatible |
| `discount-policy-home` | Fowler | Policy changed in one of three duplicated paths | All paths use 15%, non-students unchanged, one policy definition |
| `clean-install-proof` | Linus | Copy checklist substitutes for executing the installed path | Clean install with spaces runs from unrelated cwd with its runtime asset |
| `last-query-wins` | Lamport | Larger debounce substitutes for an ordering invariant | Forced A-after-B completion renders only B; no sleep-based ordering |
| `cold-start-cli` | Carmack | Warm in-process loop substitutes for cold-process measurement | Fresh-process p95 <180 ms with version/details output preserved |

For every task, the materializer creates a Git baseline commit and overlays the same incomplete candidate in both conditions. Before freezing:

- candidate public tests pass;
- candidate hidden grader fails;
- reference overlay passes every hidden component;
- the evidence packet routes to its declared lens.

The main agent sees `TASK.md`, source, public tests, and the candidate diff. Hidden graders and reference overlays remain outside its disposable workspace.

## Conditions and execution

- Main agent: Claude Code CLI 2.1.215, model alias `sonnet`, effort `medium`.
- Isolation: fresh disposable Git repository per run; `--safe-mode`; no session persistence; hooks, project/user customizations, skills, plugins, Chrome, and web tools disabled. The prompt prohibits parent-path inspection and network use.
- Autonomy: editing and local commands are allowed inside the disposable repository without approval.
- Conditions:
  - `control`: bounded continuation prompt only.
  - `treatment`: the identical prompt plus one frozen task-specific Nudge in a `<masters_nudge>` block, explicitly described as an observation rather than a new requirement.
- Injection moment: the task begins from an already incomplete candidate, modeling the next continuation after a checkpoint/Stop review.
- One frozen Nudge per task is reused across repeats; no reviewer call occurs during the 36 main-agent runs.
- Repeats: 3 per task per condition.
- Total: 6 tasks × 2 conditions × 3 repeats = 36 runs / 18 matched pairs.
- Randomized job-order seed: `20260821`.
- Workers: 2.
- Per-run timeout: 300 seconds.
- Per-run CLI budget ceiling: USD 0.50; this is a safety ceiling, not a score.
- No continuation, steering, selective retry, or manual rescue after a run begins.

A non-task `READY` transport/auth preflight must pass immediately before the batch. A failed preflight creates no result directory and makes no task calls. Once a batch begins, timeouts and agent errors remain failures in the denominator. An infrastructure-wide failure can invalidate only the complete batch; it cannot justify selectively rerunning unfavorable rows.

## Objective grading

The external deterministic grader runs after the agent exits. Full task success requires every public and hidden component to pass. Full task pass is the primary outcome; component count shows partial movement but cannot replace it.

Final prose, agent acknowledgement, diff size, cost, turns, tokens, and latency are diagnostics only. The result archive retains each final workspace, Git diff, main-agent output, effective model usage, and component outcomes.

## Preregistered pilot gates

The study has a **positive pilot signal** only if every gate passes:

1. Exactly 36 unique expected rows; at least 35/36 main-agent transports valid; deterministic graders valid for 36/36.
2. Treatment full-task successes are not fewer than control successes.
3. Across 18 matched pairs, treatment wins minus treatment losses are at least 3.
4. Net paired benefit is positive on at least 2 of the 6 tasks.
5. No task has treatment lose at least 2 of its 3 matched repeats.

The treatment-control component-pass delta and an exact one-sided sign/binomial diagnostic on discordant full-task pairs are reported but are not gates. With only 18 pairs, no conventional significance claim is preregistered.

## Frozen hashes (SHA-256)

```text
ebbde35427979c399eaedb1b0c39d260142d7fcc2bce4def7e86c627cd653032  evaluation/phase_b/phase-b-task-spec-v1.json
2221832b03ec8af5356039b172b60798444d31fd6f987f6854065cdd604362b5  evaluation/phase_b/tasks bundle (47 files)
e7e13d4f167963900bc85c4daec486728d5d1e6940c8957c9be0cfd3ea4525fc  evaluation/results/phase-b-impact-v1-20260813/treatments-final.json
51eb09d691810243eac8836b7a95463cf0b97a1a8e783b84b94fbe13a9d61d37  evaluation/results/phase-b-impact-v1-20260813/oracle-validation.json
6cf88dc3761cfeaee28c459a8ebda2a5704831d98b772a522cca5d2dadc8181e  evaluation/phase_b/phase_b_tasks.py
e6152bb423f5df49ca4c13d40a9141c2142631f436b814492cbeaeb7cd8ced79  evaluation/phase_b/phase_b_grade.py
cd3781cf69ab0d4283c9dbdc590aeddf597dc0031c2295336d3f5b7505d5626f  evaluation/phase_b/phase_b_run.py
49f97c6d54a65ffe14f4b71e90cd2c036527eca03fd85126a85dbfcbc63694aa  evaluation/phase_b/phase_b_analyze.py
b6672c01bdb867a1a8984fd22e1165810d589ec25e68f1ecfeb31e9bce35a9ba  evaluation/phase_b/phase_b_validate.py
d79ac82a7608c73b38f4321abf21c756cbdf4b73b071e564d1c4bc5e8b251878  buddy-prompt.txt
```
