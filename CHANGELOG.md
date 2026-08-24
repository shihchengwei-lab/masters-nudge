# Changelog

## Unreleased

Target package version: `0.2.0-dev.1`.

- Deliver each finding only in the eligible event that produced it; record a successful flush as `emitted`, a wire failure as terminal `failed`, and require a later host event before confirming `injected`.
- Use one canonical review-attempt identity across both hosts and every review kind; terminal `finding`, `no_finding`, and `error` attempts do not trigger automatic Provider retries.
- Run eligible Claude and Codex checkpoint, strategy, goal-transition, and Stop reviews synchronously; a Stop finding continues the same turn instead of waiting for a later prompt or detached worker.
- Cap Provider work at 90 seconds inside a 120-second host-hook timeout, while retaining lower explicit timeout settings.
- Run Anthropic reviews at explicit medium effort without session persistence, retain bounded timeout diagnostics, and stop treating a single edit-to-validation cycle as a strategy checkpoint.
- Present earlier failures as bounded history without repeating the current failed event, and remove the duplicate goal objective from strategy evidence.
- Make `ReviewCore` the sole routing owner, keep the lifecycle filter when unrelated specialist evidence is absent, and avoid rotating filters merely because the primary is cooling down.
- Present engineering stages and practical focus in public configuration and the floating window; keep person names only inside provider prompts as private attention cues.
- Keep only Claude's current-turn final-claim fallback parser, share one checkpoint/Stop JSON emitter, and remove the dead transcript renderer and duplicate delivery seams.
- Make native plugin marketplaces the only supported installation path; remove manual installers, hook snippets, legacy source wrappers, legacy `BUDDY_*` configuration aliases, and legacy runtime/data fallbacks while retaining the packaged host launchers.
- Retire the former Shader, Three.js／WebGPU black-hole, and Riemann specializations from the product branch; their historical artifacts remain in the verified [`evidence-archive-2026-08-22`](https://github.com/shihchengwei-lab/masters-nudge/releases/tag/evidence-archive-2026-08-22) release and fixed tag.
- Replace stopped evaluation harnesses, fixtures, dated reports, screenshots, and an unused spritesheet builder with a single `evaluation/README.md` index that retains denominators, exclusions, null results, and explicit claim boundaries.
- Consolidate Claude hook entry points, checkpoint classification, turn state, Agentcam discovery, logging, and runtime inventory around one owner for each behavior; remove detached review launchers.
- Derive package membership and doctor dependencies from one manifest, Claude session identity from one adapter helper, and public stage views from one `StageSpec` registry.
- Align README claims with prompt-level question guidance and Codex-only response observations; remove test-only Claude session fallbacks and unused forwarding surfaces.
- Shorten the public documentation to installation, use, migration, configuration, privacy, evidence limits, and current manual gates.
- Record the first observable tool action or Stop claim after each emitted question, then confirm its receipt as injected; this is temporal evidence only and does not attribute the action or result to the Nudge.
- Align software reviews around one evidence-grounded second opinion, semantic result evidence without tool-operation details, the latest three injected findings for duplicate avoidance, semantic evidence-cycle triggers, same-event delivery, local/trajectory scope, and separate route, provider, and delivery records.
- Keep review telemetry as content-free append-only diagnostics and remove the inactive shadow cost-evaluation state, reports, notices, and automatic candidate machinery.
- Terminate the full Claude, Codex, and Grok reviewer process tree after a deadline, normalize provider failure categories, and avoid storing raw provider output.
- Pass structured routing concerns instead of parsing classifier-generated marker text, and limit Claude Stop fallback evidence to the current turn.
- Refuse legacy-config migration when its source changes after preflight, and derive doctor readiness from the code-owned package manifest instead of an installed self-report.
- Rename the architecture document to describe its lasting responsibility rather than an old project phase.
- Keep collision-resistant reaction identifiers and session-scoped write locking while removing cross-event freshness selection and automatic `superseded` receipts.
- Expand mid-turn checkpoint input from one triggering event into a bounded current-state packet containing the task anchor, recurring workflow evidence, validation state, and open target/evidence tension; keep Stop input unchanged.
- Keep timeout status entries visible in Tk without incorrectly labeling them as pending delivery.
- Pass the caller's workspace explicitly through the window launcher so workspace filtering no longer depends on the plugin script's working directory.
- Reviewer provider CLIs now run without opening transient console windows on Windows.

## 0.1.0-dev.2 — Unreleased prerelease

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
