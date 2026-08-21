# Changelog

- Align software reviews with the Shader interaction contract: one unlabeled open question, cold current-state input, delivery-aware two-Persona cooldown, semantic evidence-cycle triggers, source-fresh pending delivery, local/trajectory scope, and separate route/provider/delivery records.
- Add a `shader configure-recommended` workspace preset that preserves the V12 Shader environment (`anthropic / opus / explore / review all`, automatic Persona routing), and keep Shader injection label-free on both Codex and Claude paths.
- Terminate the full Grok reviewer process tree after a deadline, preventing timed-out Windows hook workers and their CLI descendants from lingering.
- Add a two-injection Shader Persona cooldown: only successfully injected findings count, routing keeps the Provider cold, and the next eligible Persona follows the original evidence ranking.
- Include live Shader candidate results from either `benchmark/candidate-results.json` or per-candidate `Evidence/LongTail/*/result.json` and `failure.json` files in the semantic research fingerprint and projection, focus the packet on the latest observed candidate, and retain generic long-goal checkpoints when structured evidence temporarily remains unchanged.
- Enrich semantic Shader reviews with candidate decision material, the latest direct tool evidence, and explicit missing-field markers; route research changes from structured evidence dimensions, suppress only an unchanged evidence-gap pair, and record route basis, gap fingerprint, and material completeness in telemetry.
- Trigger structured Shader strategy reviews from semantic changes in the architecture contract, experiment registry, and result files instead of the generic eight-event workflow budget; send a compact source projection without replaying the full tool journal.
- Make Shader specialist routing prefer the strongest current evidence rather than balancing historical invocation counts.
- Add per-session strategy single-flight, source-aware Shader delivery freshness, explicit `superseded` receipts, and collision-resistant reaction identifiers.
- Record Shader `expand` / `deepen` / live-`guard` opportunities in telemetry as an observational metric, not a runtime quota.
- Add Shader candidate-search governance where the 50-slot budget counts distinct bottleneck-hypothesis/work-elimination cells, while near-neighbor numeric and algebraic variants become separately budgeted refinements.
- Report nearest-rank observed p95 for all Shader replay attempts and successful responses separately, retaining timeout wall time in the operational tail while labeling three-sample persona p95 as descriptive only.
- Expand mid-turn checkpoint input from one triggering event into a bounded research state containing the current bottleneck proxy, workflow recurrence, mechanism outcomes, and the still-open target/evidence tension; keep Stop input unchanged.
- Show six Shader specialists in the Tk selector for Shader workspaces; persist a workspace-scoped Stop primary while retaining evidence-driven checkpoint switching.
- Raise the default Stop reviewer timeout from 60 to 120 seconds, and keep timeout status entries visible in Tk without incorrectly labeling them as pending injection.
- Pass the caller's workspace explicitly through the window launcher so Tk domain selectors no longer depend on the plugin script's working directory.
- Reviewer provider CLIs now run without opening transient console windows on Windows.

## 0.1.0-dev.2 — Unreleased prerelease

- Archive the complete domain-specialization experiment under `experiment/riemann-domain/`; keep the shipped runtime focused on software-engineering workflows.
- Add an optional signed-in Grok CLI reviewer with schema-constrained single-turn output and web search, tools, memory, and subagents disabled; include persistent configure/reset commands and doctor detection.
- Document that provider and CLI harness costs are not normalized, including one dated Grok CLI smoke as a clearly non-binding observation rather than a pricing claim.
- Add delivery receipts with event sequence, injection channel, and queued/injected/expired/failed states; the Tk window now distinguishes reviewer generation from actual context injection.
- Add recurring detached long-goal strategy checkpoints for repeated command/failure families, eight meaningful events, and each additional ~80 changed lines, plus immediate `complete`/`blocked` Goal transition review.
- Route workflow-drift evidence across the existing six software lenses and add deterministic Phase D long-goal replay tests; no manual “review now” control is added.
- Keep Stop on the selected primary lens; allow event-scoped checkpoint switches across all six lenses, then force three eligible checkpoints back to primary after every five switches.
- Raise the default checkpoint reviewer timeout from 15 to 90 seconds so a slow paid response is more likely to reach the queued/injected delivery path.
- Make Codex hook responses code-page-safe, commit delivery only after stdout succeeds, and inject detached Stop findings through the next PostToolUse event so persistent Goals receive reviewer feedback without a new user prompt.
- Isolate Anthropic reviewer calls from Claude Code's default tools, plugins, settings, and project prompt to reduce unrelated context and Opus input cost.
- Use PowerShell-native plugin paths for Codex hooks on Windows, mirror checkpoint findings into the Tk window without redelivering them, and keep launchers fail-open; retain synchronous PostToolUse delivery for Codex CLI 0.147 compatibility.
- Read a newly active session log from its first entry so the Tk window no longer skips that session's initial Nudge.
- Tag reactions with normalized workspace identity and make the Tk window ignore logs from other workspaces, preventing research and plugin-development sessions from nudging the same display.
- Add six distinct, evidence-bounded workflow observation scenes that guide lens-specific candidate selection without leaking persona role-play into Nudge text.
- Improve fixed-packet semantic lens differentiation from 5/6 to 6/6 in the scene follow-up; retain the holdout requirement before making a general reliability claim.
- Target a complete 36–42-character Nudge ending in terminal punctuation while retaining the 52-character hard cap and accepting shorter complete answers.
- Close an unpunctuated hard-cap finding locally at its last complete clause, preserving delivery without another reviewer call.
- Replace the original 5/6 README hero with six real Tk captures from the 6/6-aligned, 18/18-complete local-closure run.
- Add an experimental BYOM `ollama-local` reviewer shared by Claude Code and Codex.
- Require loopback HTTP, disabled proxies and redirects, Ollama cloud-disabled status, and local model metadata before every generation.
- Persist an explicitly configured local reviewer while keeping environment variables as the highest-priority override.
- Fail closed on missing, remote, or malformed local configuration and never fall back to a cloud reviewer.
- Add model-free local diagnostics and a `setup-local` plugin skill without installing, pulling, or recommending models.

This version is intentionally not tagged or released yet.

## 0.1.0-dev.1 — Unreleased prerelease

- Add native Claude Code and Codex plugin packages and repository marketplaces.
- Make core installation clone-free and remove manual hook-file merging.
- Run Claude hooks in shell-free exec form with an install-time Python executable setting.
- Default Claude Code reviews to Anthropic `sonnet` and Codex reviews to OpenAI `gpt-5.6-sol`; explicit provider/model environment variables still win.
- Add model-free installation diagnostics, optional window launching, and fail-closed migration of exact legacy hook entries with backups.
- Keep the shell and PowerShell installers as supported compatibility paths.
- Validate generated plugin contents on Linux, macOS, and Windows with Python 3.10 and 3.14.

This version is intentionally not tagged or released yet.
