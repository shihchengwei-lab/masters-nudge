# Shader Long-tail V1 Runbook

This is the short operational checklist for
`evaluation/shader_long_tail/PROTOCOL_V1.md`. The protocol owns definitions and
gates; this file records execution order.

## Current state

- [x] Protocol written.
- [x] Isolated worktree created at `E:\projects\shader-long-tail-v1`.
- [x] Branch created at `codex/shader-long-tail-v1`.
- [x] Start commit verified as `cacae3e08cbcc293698b68fb76141ad63cfacea1`.
- [x] Worktree verified clean after Unity preflight.
- [x] Fifteen Python contract tests passed.
- [x] Unity `6000.0.80f1` first import and script compilation exited with code 0.
- [x] Masters' Nudge workspace profile saved as Shader / explore / Grok medium /
  automatic routing.
- [x] Codex CLI `0.147.0` and Grok CLI `1.0.4` recorded.
- [x] User accepted the proposed main model and refinement budget.
- [x] Project-local Codex memory use and generation disabled; model-visible
  prompt checked for historical Shader result leakage.
- [x] Execution manifest frozen; detached SHA-256 recorded.
- [x] Clean research-source overlay committed as `137d2efa6c09220db9d7bb1d33c8f4bb4bedd9a5`.
- [x] Fresh `BaselineV0` evidence committed as `ab1027d0f1980d792539e4e1b1e06ebdf1d6365d`:
  18,000 valid GPU samples, Intel UHD / D3D11 proof, and matching repeat-golden hashes.
- [x] The first started session (`01a01552-a991-7bc0-870f-7746207f3167`) was
  stopped and excluded because `benchmark/experiments.json` seeded a historical
  candidate. No Nudge was delivered in that session.
- [x] The legacy candidate registry was removed and guarded by a contract test;
  the new clean ready commit is `10839d137e6b49e2f22d48d9d71946a37462da8f`.
- [x] Masters' Nudge V1 projection parsing was corrected and reinstalled as
  `0.1.0-dev.2+codex.20260818145636`; 357 tests passed, 2 were skipped, and the
  installed projection smoke read `BaselineV0`, 0 resolved, and 50 unresolved.
- [ ] User opens Codex CLI in the isolated worktree and starts the outcome-only
  Goal.
- [ ] Masters' Nudge window and monitoring start after the Codex session exists.
- [ ] Final trajectory, Nudge interaction, and 30/50/70 outcome comparison run.

## Frozen values

- Main model: `gpt-5.6-sol`
- Main-model reasoning effort: `high`
- Refinement limit: 2 per distinct search cell
- Candidate limit: 50 distinct cells
- Wall-time policy: no short wall-time stop; stop only on formal saturation,
  50 cells, or a genuine blocked condition

## User actions

1. Open Codex CLI in `E:\projects\shader-long-tail-v1`.
2. Start this exact Goal:

   > 交付在固定視覺與量測契約下，經實證建立且可重現的最佳 Shader Pareto 前沿，並保留足以重現候選判定的研究紀錄。

3. Tell the monitoring task that the CLI session has started. Do not manually
   rotate Persona, inject evaluation instructions, or copy old candidate results
   into the workspace.

## Remaining agent actions

1. Verify the workspace profile and open the Masters' Nudge window after the user
   starts Codex CLI.
2. Monitor without modifying the Shader work, injecting manual Nudges, or
   calling extra paid providers.
