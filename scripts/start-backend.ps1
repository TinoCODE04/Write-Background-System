$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { throw "Virtual environment not found. Run: python -m venv .venv" }
Set-Location (Join-Path $RepoRoot "backend")
& $Python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

