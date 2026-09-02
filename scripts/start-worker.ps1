$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { throw "Virtual environment not found. Run: python -m venv .venv" }
Set-Location (Join-Path $RepoRoot "backend")
& $Python -m app.workers.image_worker

