# Riemann domain experiment

This directory preserves the complete local domain-specialization experiment as
it stood when the production runtime returned to a software-engineering-only
scope on 2026-08-16.

It is a fork reference, not shipped plugin code and not a claim of progress on
the Riemann hypothesis.

## Contents

- `domain/riemann/`: the domain base prompt and six mathematical personas.
- `riemann_router.py`: evidence-based specialist routing and cooldown policy.
- `runtime-snapshot/`: exact integration-point snapshots from the experimental
  runtime, including core, storage, prompting, workspace profile, CLI, and Tk UI.
- `plugin-snapshot/`: domain files and router removed from the generated plugin.
- `skill/SKILL.md`: the Codex setup skill used by the local experiment.
- `research/staging/`: working notes, candidate lemmas, experiments, and results.
- `research/output/`: the consolidated write-up and numerical verifier.
- `tests/riemann_domain_integration_snapshot.py`: the original integration test
  suite retained as executable design documentation.
- `tests/test_archive.py`: a self-contained archive integrity test.

The production runtime deliberately retains only domain-neutral long-task
checkpoints, delivery receipts, and Goal-transition review. To revive this
experiment in a fork, port the runtime snapshots as a coherent set rather than
copying only the personas; routing, workspace configuration, timeout policy,
prompt assembly, UI state, and tests were coupled.

Run the archive integrity test from the repository root:

```powershell
python -m unittest experiment/riemann-domain/tests/test_archive.py
```
