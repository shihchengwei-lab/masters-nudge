# Phase B task-sensitivity calibration v1 result

Executed 2026-08-13. **Stage 1 did not pass. Do not start the held-out V2
product-effect batch from these synthetic patterns.**

This result evaluates the measurement instrument, not Masters' Nudge. Neither
the product prompt nor its 42-character soft target / 52-character hard cap was
used as a treatment in this batch.

## Result

| Metric | Control | Positive control |
|---|---:|---:|
| Runs / valid transports / valid graders | 18 / 18 / 18 | 18 / 18 / 18 |
| Safe target resolutions | 13/18 | 13/18 |
| Full-task passes | 13/18 | 13/18 |
| Cost | US$2.499633 | US$2.433655 |
| Mean turns | 10.44 | 10.33 |
| Mean wall time | 33.8 s | 32.3 s |

Across 18 matched pairs there was one positive-control win, one loss, 12 pairs
where both succeeded, and four where both failed: net zero. All 36 expected rows
were unique and valid, but **0/6 tasks met the preregistered sensitivity gate**.
The preregistered viability floor was at least 4/6.

| Pattern | Control | Positive | Gate | Diagnosis |
|---|---:|---:|---|---|
| setup-bottleneck-choice | 1/3 | 1/3 | fail | Both conditions found the bottleneck; the grader rejected reasonable punctuation-to-hyphen normalization not prohibited by the visible contract. |
| csv-change-boundary | 3/3 | 3/3 | fail | Ceiling: the tiny diff and explicit preserve-other-behavior instruction made the JSON regression obvious. |
| partner-policy-home | 0/3 | 0/3 | fail | Oracle overconstraint: five runs centralized the constant, but the grader required live propagation after an in-process monkeypatch. |
| installed-runtime-proof | 3/3 | 3/3 | fail | Ceiling: the handoff note and adjacent runtime file directly exposed the missing asset. |
| latest-refresh-invariant | 3/3 | 3/3 | fail | Ceiling: the objective named latest-request semantics and the implementation was small enough to inspect completely. |
| real-cli-startup | 3/3 | 3/3 | fail | Ceiling: the fresh-process report and module-level delay made the representative path obvious. |

## Post-hoc semantic audit

The frozen automated scores above remain unchanged. A diagnostic audit found two
oracle semantics that should not be carried forward:

- `partner-policy-home` mutated `discount_policy.PARTNER_RATE` after importing all
  consumers. `from discount_policy import PARTNER_RATE` is still a single source
  for normal source-edit/restart deployments, so five centralizing solutions were
  rejected despite satisfying the visible task. Under that interpretation the
  task would be control 2/3 versus positive 3/3, with one paired win.
- `setup-bottleneck-choice` required `bad!name` to remain invalid, although the
  task only required safe slug creation and the visible samples established
  normalization. Treating punctuation-to-hyphen as acceptable makes both
  conditions ceiling-saturated rather than sensitive.

Even with those generous corrections, only the partner-policy pattern could
meet the gate: **1/6**, still below the 4/6 stop boundary. The stop decision is
therefore not dependent on either questionable oracle.

## Decision

Stop synthetic micro-repository calibration and do not tune the General/persona
prompts against this batch. A stronger answer-shaped hint cannot demonstrate
incremental value when the control agent already reads the complete tiny repo and
recovers the intended workflow issue in four patterns.

The next credible input is a set of consented, anonymized natural task traces
with real repository scale, competing evidence, and independently observed
completion gaps. No such trace corpus exists in this workspace, so V2 is paused
at data acquisition. The future process should:

1. collect the original objective, checkpoint claim, bounded evidence available
   at that point, final diff, and independently known missed outcome;
2. remove secrets, identities, proprietary literals, and irrelevant source;
3. obtain permission for evaluation use and keep source provenance separate from
   the blinded task packet;
4. define behavioral oracles from the original outcome before any model run;
5. split calibration and held-out traces by project or incident, not random row.

Do not use production correlation, agent acknowledgement, or a retrofitted
hidden test as a substitute for this trace provenance.

## Reproducibility

- Protocol: `evaluation/phase_b_calibration/CALIBRATION_PROTOCOL_V1.md`
- Oracle validation: `oracle-validation.json`
- Frozen manifest: `execution-v1/manifest.json`
- Raw rows and diffs: `execution-v1/runs.jsonl`
- Archived final workspaces: `execution-v1/artifacts/`
- Machine analysis: `execution-v1/analysis.json`

| Artifact | SHA-256 |
|---|---|
| manifest | `6606237cd6be658ffa98f0c879ed0221dcbcab30ca0e3c07fc545c9e7c96fdf3` |
| raw rows | `7976997cbe6e968ac3384e08dd1b19b9c9150e2bb462cf7f265c5f6ee4bd860f` |
| analysis | `f29ffbd833d9cc7104f93a54a0d87ef435c856ece0175565ea19b42754081a9a` |
