# Phase B task-sensitivity calibration protocol v1

Frozen before main-agent execution on 2026-08-13.

## Question and scope

Can each synthetic workflow pattern distinguish an unaided coding agent from the
same agent given a direct, answer-shaped hint? This is instrument calibration,
not evidence that Masters' Nudge works. The current product prompt and its
42-character soft target / 52-character hard cap are not used or changed here.

## Design

- Six tasks, one for each lens: Jeff, Beck, Fowler, Linus, Lamport, Carmack.
- Conditions: `control` and `positive_control`.
- The repository, objective, checkpoint claim, evidence summary, agent command,
  model, effort, and budget are identical within each pair. Only the tagged
  positive-control hint differs.
- Three repeats per task and condition: 36 runs / 18 matched pairs.
- Candidate workspaces are isolated Git repositories. Job order is randomized.
- Main agent: Claude Code `sonnet`, `medium` effort, safe mode, no persistence,
  no web, 300-second timeout, USD 0.50 maximum per run, two concurrent workers.
- Seed: `20260822`.
- No steering, rescue, selective retries, or replacement rows. Any task, grader,
  prompt-envelope, or gate change creates a new protocol version and full batch.

## Behavioral oracle validation

Every candidate is public-green and target-red. Both accepted implementations
are green. Both plausible near misses remain public-green and target-red.

| Task | Visible basis for target | Target behavior | Independent acceptable shape |
|---|---|---|---|
| setup-bottleneck-choice | Funnel loss and rejected-name samples | Normalize supported display names to safe slugs | Regex pipeline or explicit character-state implementation |
| csv-change-boundary | Narrow CSV request, compatibility sample and JSON golden | CSV gains delimiter without changing JSON bytes | Local CSV validation with either direct or helper-based implementation |
| partner-policy-home | "Throughout" objective and policy-ownership history | All billing paths read one live partner-rate owner | Module lookup or policy accessor |
| installed-runtime-proof | QA receives only installed directory and runs elsewhere | Installed CLI carries and locates its runtime data | Copy package assets individually or as a declared bundle |
| latest-refresh-invariant | Most-recent-request objective | Forced older completion cannot overwrite newer request; controllers remain independent | Per-instance generation or equivalent request token |
| real-cli-startup | Fresh-process report and command-specific SLO | Fresh `--version` avoids slow catalog import while details still work | Lazy import in command path or deferred lookup boundary |

The graders test behavior rather than preferred filenames or exact syntax. The
manual traceability audit found each target entailed by the objective plus
visible repository evidence; it was performed in the implementation session,
so independent reviewer confirmation remains a documented limitation.

Oracle validation artifact: `evaluation/results/phase-b-calibration-v1-20260813/oracle-validation.json` (`all_valid: true`).

## Preregistered analysis

`safe_target_resolution` requires the named target plus public and regression
components to pass. For each task, accept the pattern only when:

1. control succeeds in exactly one or two of three repeats;
2. positive control succeeds in at least two of three repeats; and
3. paired positive-control wins minus losses are at least one.

Batch integrity requires 36 unique expected rows, at least 35 valid agent
transports, and 36 valid deterministic grader results. Stage 1 passes only if
integrity and all six task gates pass. If fewer than four tasks pass, stop using
synthetic fixtures and seek anonymized natural traces. Results between four and
five tasks justify fixture revision but not a product-effect claim.

## Frozen artifacts

| Artifact | SHA-256 |
|---|---|
| `buddy-prompt.txt` (unchanged product reference) | `d79ac82a7608c73b38f4321abf21c756cbdf4b73b071e564d1c4bc5e8b251878` |
| calibration task tree | `f8a0d2b9993dce7ffff03d1c94dd2aebe0cf24804e82d7a8fc19e58c011a229c` |
| `calibration-task-spec-v1.json` | `e7889e3f58c6dd923df264729dbe6bc0b3c23682b21538e30d506896e1dca4f7` |
| `calibration_tasks.py` | `225830ac38f99aa51498be9010fa3d51e6f9051d9f38ab176f349636030e0f8e` |
| `calibration_grade.py` | `6fab101484cabdbe4bdfe03759427a10201e3a3d534a58db964f26cca008c050` |
| `calibration_validate.py` | `c8911eb9d233478e654385038e3135802cd17b980a56139dd7574a55ed6abf1d` |
| `calibration_run.py` | `8d0d0137a8b1c96f35bf6cbf48a91bedba5f25e5e74c753ddcc1bbf0ea02c526` |
| `calibration_analyze.py` | `9d63a8a00f29542e85a6058ba1a1948bca7498682019dd6f4313b2aead2aee5c` |
| imported V1 runner helper `phase_b_run.py` | `cd3781cf69ab0d4283c9dbdc590aeddf597dc0031c2295336d3f5b7505d5626f` |
| oracle validation JSON | `4eb7ff6e6a6955f05beae4afd932bdb1222a5e2a60bdc8e2869b65697a9f8354` |
| calibration unit tests | `ef987ec3345dd649d38edc2756acc2e465b29c1a4251b9529878b33031cd07be` |

## Execution

```powershell
python -m evaluation.phase_b_calibration.calibration_run `
  --spec evaluation/phase_b_calibration/calibration-task-spec-v1.json `
  --output-dir evaluation/results/phase-b-calibration-v1-20260813/execution-v1 `
  --repeats 3 --seed 20260822 --workers 2 `
  --model sonnet --effort medium --timeout 300 --max-budget-usd 0.50
```

The manifest written at execution time records the randomized job order and
rechecks the spec, task-tree, runner, grader, and analyzer hashes.
