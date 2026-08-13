param(
    [ValidateSet("all", "claude", "codex")]
    [string]$HostName = "all",
    [string]$RuntimeDir = $(
        if ($env:MASTERS_NUDGE_RUNTIME_DIR) { $env:MASTERS_NUDGE_RUNTIME_DIR }
        else { Join-Path $env:USERPROFILE ".masters-nudge\runtime" }
    ),
    [string]$ClaudeTargetDir = $(
        if ($env:BUDDY_TARGET_DIR) { $env:BUDDY_TARGET_DIR }
        else { Join-Path $env:USERPROFILE ".claude\scripts\buddy" }
    )
)

$ErrorActionPreference = "Stop"
$SourceDir = $PSScriptRoot

Write-Host "Masters’ Nudge — install"
Write-Host "Source:  $SourceDir"
Write-Host "Runtime: $RuntimeDir"

New-Item -ItemType Directory -Force -Path $RuntimeDir | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $RuntimeDir "masters_nudge") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $RuntimeDir "personas") | Out-Null

$SharedFiles = @(
    "hook_entry.py", "source_context.py", "persona_config.py", "lens_router.py",
    "review_telemetry.py", "buddy-prompt.txt", "reaction-schema.json",
    "codex-hooks-snippet.json"
)
foreach ($File in $SharedFiles) {
    Copy-Item -LiteralPath (Join-Path $SourceDir $File) -Destination $RuntimeDir -Force
}
Copy-Item -Path (Join-Path $SourceDir "masters_nudge\*.py") -Destination (Join-Path $RuntimeDir "masters_nudge") -Force
Copy-Item -Path (Join-Path $SourceDir "personas\*.txt") -Destination (Join-Path $RuntimeDir "personas") -Force

if ($HostName -in @("all", "claude")) {
    New-Item -ItemType Directory -Force -Path $ClaudeTargetDir | Out-Null
    $ClaudeFiles = @(
        "buddy.sh", "buddy.py", "checkpoint.sh", "checkpoint.py", "inject.sh",
        "inject.py", "source_context.py", "persona_config.py", "lens_router.py",
        "review_telemetry.py", "buddy-prompt.txt", "reaction-schema.json",
        "buddy_window.py", "start_buddy_window.bat", "spritesheet.webp"
    )
    foreach ($File in $ClaudeFiles) {
        Copy-Item -LiteralPath (Join-Path $SourceDir $File) -Destination $ClaudeTargetDir -Force
    }
    Copy-Item -LiteralPath (Join-Path $SourceDir "personas") -Destination $ClaudeTargetDir -Recurse -Force
    Copy-Item -LiteralPath (Join-Path $SourceDir "masters_nudge") -Destination $ClaudeTargetDir -Recurse -Force
}

Write-Host "Installed shared runtime."
if ($HostName -in @("all", "claude")) {
    Write-Host "Claude Code: merge settings-snippet.json into ~/.claude/settings.json."
}
if ($HostName -in @("all", "codex")) {
    Write-Host "Codex CLI: merge $RuntimeDir\codex-hooks-snippet.json into ~/.codex/hooks.json, then trust it in /hooks."
}
Write-Host "Local data defaults to ~/.masters-nudge/data."
