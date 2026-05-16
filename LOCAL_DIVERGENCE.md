# LOCAL_DIVERGENCE — not in upstream

This working copy of Buddy_similar has commits that are **intentionally not
pushed** to `shihchengwei-lab/Buddy_similar` on GitHub. If you are a future
agent picking this up, read this before doing anything.

## Why diverged

The owner is personally experimenting with feeding
[agentcam](https://github.com/shihchengwei-lab/agentcam) (`AGENT_RUN_REPORT.md`)
into Buddy's payload as an additional context source for the second-opinion
model. The point is: when `cr "task"` (the PowerShell alias the owner uses
locally) finishes a recorded agent run, Buddy automatically picks up the
fresh report from `<git_root>/.git/agentcam/runs/*/AGENT_RUN_REPORT.md` and
the cross-vendor reviewer (default GPT-5.5 via Codex CLI) can comment on
the structured risk / change signals the report contains.

This integration is **personal workflow only**. The public Buddy_similar
package on GitHub does not require agentcam, and shipping the integration
upstream would force every user to install both tools to use Buddy at all.
That tradeoff is wrong for the public package. So the integration stays
local-only on this machine.

## What changed (local-only commit `c571b2d`)

- `buddy.py`
  - Added module constant `AGENTCAM_REPORT_TAIL_CHARS = 2000`.
  - Added 4 helpers: `_find_git_root`, `read_latest_agentcam_report`,
    `load_agentcam_last_mtime`, `save_agentcam_last_mtime`. Per-session
    dedup state lives at `~/.claude/buddy/<session_id>.agentcam.state.json`.
  - `main()` now reads `cwd` from the hook input (fallback `os.getcwd()`)
    and, if a *fresh* (mtime > last seen) AGENT_RUN_REPORT.md exists under
    the cwd's git root, appends an `[agentcam report ...]` block to the
    payload before sending to the model.
- `buddy-prompt.txt`
  - `# 優先找這些` got a new bullet 6 instructing the model to prioritize
    Risk Flags / Changed Files / Exit Code Detail when the report is
    present, and noting that the report is git-porcelain based (more
    reliable than Claude's self-narration).
  - `# 不准補腦` got an explicit exception: when `[agentcam report]` is in
    the payload, that IS valid git/file evidence Buddy may cite — but
    still don't speculate beyond what the report actually contains.
- `test_buddy.py`
  - New `TestAgentcamReport` class with 8 tests covering all the helpers
    above. All 48 tests pass (`python -m unittest test_buddy -v`).

## Why NOT pushed

- Other Buddy_similar users can install Buddy without agentcam. Forcing
  the integration upstream would break that.
- This is the owner's personal experiment. Pushing it makes the public
  package look like it depends on a tool it does not depend on.

## Rule for future agents

**Do not push this divergence to `origin/main` without explicit owner
confirmation.** If the owner ever decides agentcam integration should be
optional in the public package (e.g. gated behind a `BUDDY_USE_AGENTCAM=1`
env var with graceful no-op when agentcam is not present), refactor the
integration to be opt-in BEFORE pushing.

If you `git pull` and get conflicts, the local-only changes here are the
ones that take precedence on this machine. Do not resolve conflicts by
discarding the local divergence.

## Deployment note

Local source edits do not auto-deploy. To make Buddy actually use new
changes, re-run:

```bash
bash install.sh
```

This copies `buddy.py`, `buddy-prompt.txt`, etc., to
`~/.claude/scripts/buddy/`. The already-deployed copy stays on the old
version until you re-run install.

Last reviewed: 2026-05-16.
