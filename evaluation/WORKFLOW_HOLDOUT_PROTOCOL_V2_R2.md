# Workflow Holdout V2 — Infrastructure Rerun R2

Declared before R2 reviewer calls on 2026-08-13 (Asia/Taipei).

R2 inherits every fixture, input hash, condition, repeat, randomization seed, blind seed, rubric, and gate from [WORKFLOW_HOLDOUT_PROTOCOL_V2.md](WORKFLOW_HOLDOUT_PROTOCOL_V2.md). No frozen model input changed.

## Why the first batch is invalid

The first batch at `evaluation/results/workflow-v2-20260813` contains 84/84 `error` rows and no model responses. Its result SHA-256 is:

```text
2ae76613a7c9170d781b06d51f0125fd40b7dfe271148ada05d1dffa5a498deb
```

The shell set `BUDDY_CODEX_BIN` to the isolated Codex 0.147.0 binary, but the frozen `_resolve_codex_bin()` implementation does not read that environment variable. It selected the global Codex 0.130.0 from PATH instead. The error log records that 0.130.0 could not decode the current model metadata because it does not recognize reasoning effort `max`; each process exited before generation. This is an infrastructure failure, not a model decision or prompt-quality result.

The entire first batch is excluded. No row is selectively retried or merged.

## R2 transport correction

For R2 only the process environment changes: the directory containing the isolated Codex 0.147.0 executable is prepended to PATH before Python starts, so the unchanged resolver selects it. A non-holdout transport preflight confirmed:

- resolved binary: isolated `codex.exe` 0.147.0;
- provider/model: `openai` / `gpt-5.6-sol`;
- exit status: success;
- raw structured output: `{"status":"no_finding","finding":""}`.

R2 is a fresh complete 84-call batch written to `evaluation/results/workflow-v2-20260813-r2`, using the original seeds (`20260816` jobs, `20260817` blind shuffle). Its outputs alone will be scored and condition-blind adjudicated.
