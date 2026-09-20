$ErrorActionPreference = 'Stop'

$payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
$markerPath = Join-Path $PSScriptRoot 'hook-started.json'
$payload | ConvertTo-Json -Depth 20 -Compress | Set-Content -LiteralPath $markerPath -Encoding utf8
Start-Sleep -Seconds 180
