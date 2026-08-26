# Roadmap

This file lists unfinished work and exclusion decisions that remain in force. Shipped behavior belongs in [CHANGELOG.md](CHANGELOG.md); retained evaluation evidence belongs in [evaluation/README.md](evaluation/README.md).

## Active items

### 1. Ongoing host compatibility

The product is plugin-only. Before claiming compatibility with a later Claude Code or Codex host version:

- perform a fresh Claude Code marketplace install and exercise prompt, checkpoint, Stop, doctor, migration, and optional window flows;
- perform a fresh Codex marketplace install, review hook trust, and exercise prompt, tool, synchronous Stop continuation, doctor, and migration flows;
- run the generated-package check and the supported Python test matrix on Windows, Linux, and macOS;
- record host versions, commands, exit status, and any unverified GUI or provider behavior.

**Compatibility boundary:** A tagged release and its CI evidence do not automatically cover later host versions. Re-run the applicable checks before making a new compatibility claim.

### 2. Natural-trace reaction quality and impact

This is future research, not a release acceptance gate. Design any experiment around consented, anonymized natural work traces, a declared quality floor, fixed main-model and task conditions, repeated matched runs, executable outcome checks where possible, and blinded human adjudication only where no honest oracle exists. The historical prerelease benchmark remains in [the evidence index](evaluation/README.md) and does not establish an effect.

**Research boundary:** Do not collect or publish natural traces until consent, redaction, retention, and reviewer access rules are approved. Do not claim outcome improvement without a repeatable controlled difference.

### 3. Optional reviewer quality

This is future research, not a release acceptance gate.

**Research boundary:** Publish model-specific recommendations only after a fixed-packet comparison with declared hardware, versions, latency, failures, and quality adjudication. Masters’ Nudge must not install, pull, or choose a local model for the user.

## Cut list

The following are deliberately outside the active product and should not return without a new decision and evidence:

- source/manual installers, hook snippets, legacy source wrappers, `BUDDY_*` aliases, and legacy runtime/data fallbacks; the packaged `hooks/run_python.cmd` and `hooks/run_python.sh` launchers remain required host entry points;
- stopped Phase B and lens-differentiation harnesses, raw workspaces, screenshots, and generated dashboards in the product branch;
- retired domain-specialization runtimes, protocols, fixtures, and research artifacts;
- a generic domain marketplace, named-reviewer prompt merge system, or domain SDK;
- automatic cost-skip enforcement, automatic provider fallback, or automatic local-model installation;
- claims that a Nudge improves coding outcomes or that observational response timing is causal.
