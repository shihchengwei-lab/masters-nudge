# Changelog

## 0.1.0-dev.1 — Unreleased prerelease

- Add native Claude Code and Codex plugin packages and repository marketplaces.
- Make core installation clone-free and remove manual hook-file merging.
- Run Claude hooks in shell-free exec form with an install-time Python executable setting.
- Default Claude Code reviews to Anthropic `sonnet` and Codex reviews to OpenAI `gpt-5.6-sol`; explicit provider/model environment variables still win.
- Add model-free installation diagnostics, optional window launching, and fail-closed migration of exact legacy hook entries with backups.
- Keep the shell and PowerShell installers as supported compatibility paths.
- Validate generated plugin contents on Linux, macOS, and Windows with Python 3.10 and 3.14.

This version is intentionally not tagged or released yet.
