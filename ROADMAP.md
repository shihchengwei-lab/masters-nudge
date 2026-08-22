# Roadmap

This file lists unresolved work only. Shipped behavior belongs in [CHANGELOG.md](CHANGELOG.md); retained evaluation evidence belongs in [evaluation/README.md](evaluation/README.md).

## Active items

### 1. Prerelease acceptance for `0.2.0-dev.1`

The product is plugin-only. Before treating the prerelease as ready for wider use:

- perform a fresh Claude Code marketplace install and exercise prompt, checkpoint, Stop, doctor, migration, and optional window flows;
- perform a fresh Codex marketplace install, review hook trust, and exercise prompt, tool, detached Stop, doctor, and migration flows;
- run the generated-package check and the supported Python test matrix on Windows, Linux, and macOS;
- record host versions, commands, exit status, and any unverified GUI or provider behavior.

**Manual gate:** Do not call the prerelease generally available until the two fresh installs and cross-platform checks have current evidence.

### 2. Natural-trace reaction quality and impact

Synthetic workflow calibration is closed. It did not show a positive Phase B treatment effect, and its micro-repositories were too ceiling-saturated or overconstrained to justify more prompt tuning.

The next valid experiment requires consented, anonymized natural work traces, a declared quality floor, fixed main-model and task conditions, repeated matched runs, executable outcome checks where possible, and blinded human adjudication only where no honest oracle exists.

**Manual gate:** Do not collect or publish natural traces until consent, redaction, retention, and reviewer access rules are approved. Do not claim outcome improvement without a repeatable controlled difference.

### 3. Cost-policy decision

Content-free review telemetry and the bounded shadow window remain observational. Provider token fields, cache fields, latency, and estimated cost are not normalized across CLIs.

**Manual gate:** Keep automatic skip enforcement off. Any live cost gate requires an explicit review of the completed window, adequate samples, false-skip risk, reaction-quality evidence, and user approval.

### 4. Optional reviewer quality

The loopback-only Ollama interface and signed-in Grok CLI path are compatibility features, not endorsements of a model, license, price, or review quality.

**Manual gate:** Publish model-specific recommendations only after a fixed-packet comparison with declared hardware, versions, latency, failures, and quality adjudication. Masters’ Nudge must not install, pull, or choose a local model for the user.

### 5. Shader evidence maintenance

Keep the current Shader profile, replay, candidate-cell registry, semantic progress projection, and interaction analysis. New evaluation output must use an explicit, nonexistent directory; historical result directories are immutable evidence.

**Manual gate:** Separate a new protocol version whenever prompts, fixtures, provider settings, denominators, or acceptance rules change. Do not overwrite an earlier run or describe a fixed replay as general Shader performance evidence.

## Cut list

The following are deliberately outside the active product and should not return without a new decision and evidence:

- source/manual installers, hook snippets, shell wrappers, `BUDDY_*` aliases, and legacy runtime/data fallbacks;
- stopped Phase B and lens-differentiation harnesses, raw workspaces, screenshots, and generated dashboards in the product branch;
- the full Riemann research working tree, plugin/runtime snapshots, setup skill, and broken integration snapshot;
- a generic domain marketplace, persona merge system, or domain SDK;
- automatic cost-skip enforcement, automatic provider fallback, or automatic local-model installation;
- claims that a Nudge improves coding outcomes, that observational response timing is causal, or that archived mathematical material advances the Riemann hypothesis.

Historical material removed from the product branch is preserved in the verified [evidence archive release](https://github.com/shihchengwei-lab/masters-nudge/releases/tag/evidence-archive-2026-08-22).
