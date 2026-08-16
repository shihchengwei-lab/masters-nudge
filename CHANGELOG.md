# Changelog

## 0.1.0-dev.2 — Unreleased prerelease

- Archive the complete domain-specialization experiment under `experiment/riemann-domain/`; keep the shipped runtime focused on software-engineering workflows.
- Add an optional signed-in Grok CLI reviewer with schema-constrained single-turn output and web search, tools, memory, and subagents disabled; include persistent configure/reset commands and doctor detection.
- Document that provider and CLI harness costs are not normalized, including one dated Grok CLI smoke as a clearly non-binding observation rather than a pricing claim.
- Add delivery receipts with event sequence, injection channel, and queued/injected/expired/failed states; the Tk window now distinguishes reviewer generation from actual context injection.
- Add recurring detached long-goal strategy checkpoints for repeated command/failure families, eight meaningful events, and each additional ~80 changed lines, plus immediate `complete`/`blocked` Goal transition review.
- Route workflow-drift evidence across the existing six software lenses and add deterministic Phase D long-goal replay tests; no manual “review now” control is added.
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
