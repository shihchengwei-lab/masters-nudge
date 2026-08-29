# Changelog

## Unreleased — 2026-08-29

### Changed

- Reduced the active engineering Filters to Simplicity, Reliability, and Performance; retired selections now resolve to Automatic.
- Made the Provider an independent second opinion over only the bounded task-and-evidence packet. Router reasoning and prior Nudges no longer enter Generator input.
- Replaced semantic output policing with structural validation and exact post-generation duplicate suppression.
- Moved Claude checkpoints to native `PostToolBatch`; Codex remains on synchronous `PostToolUse` and is documented as an approximate control point.
- Made Stop observation-only on both Hosts and added the actual hook event to diagnostic telemetry.

### Removed

- Jeff, Beck, and Fowler Filter prompts and package entries.
- Strategy-cycle scheduling, repeated-failure routing, semantic regex gates, and repository benchmark artifacts.

## 0.3.0 — 2026-08-26

### Added

- Native marketplace plugins for Claude Code and Codex, with synchronous second opinions at eligible checkpoints and Stop boundaries.
- Six software-engineering lenses, Automatic lifecycle selection, and an optional local history window.
- Anthropic, OpenAI, signed-in Grok CLI, and privacy-constrained loopback Ollama reviewer paths.
- Model-free diagnostics, explicit local-reviewer setup, and fail-closed migration of exact known legacy hooks with adjacent backups.

### Changed

- Reviewer findings are limited to one evidence-grounded, task-bound, immediately testable direction within the 52-character contract; invalid output is rejected rather than rewritten.
- Mid-turn review eligibility follows semantic change-to-verification cycles or repeated same-surface failures instead of diff size, tool choice, or ordinary successful work.
- Reviewer packets retain the task contract, explicitly named local sources, bounded semantic results, and up to three prior findings for duplicate avoidance while excluding tool operations, running commentary, and full transcripts.
- Each eligible event makes at most one canonical Provider attempt. Reviews do not silently retry, switch providers, or outlive the 90-second Provider budget inside the host hook timeout.
- Delivery state distinguishes a finding written to the host from a later observed injection. The observation establishes sequence only, not causation.
- Package membership, diagnostics, stage metadata, checkpoint policy, and host identity now have one code-owned source each; generated plugin contents are validated across supported platforms.
- Windows Provider processes run without transient console windows, and timed-out Provider process trees are cleaned up.

### Removed

- Manual installers, public hook snippets, legacy source wrappers, `BUDDY_*` aliases, detached review workers, and legacy runtime/data fallbacks.
- Retired Shader, Three.js/WebGPU black-hole, and Riemann specializations from the product branch. Their historical artifacts remain in [`evidence-archive-2026-08-22`](https://github.com/shihchengwei-lab/masters-nudge/releases/tag/evidence-archive-2026-08-22).
- Inactive shadow cost evaluation, automatic candidate machinery, automatic Provider fallback, and automatic local-model installation.
