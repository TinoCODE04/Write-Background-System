$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Scripts = Join-Path $RepoRoot "scripts"
Write-Host "Starting API, image worker, and frontend in hidden PowerShell processes..."
Start-Process powershell -WindowStyle Hidden -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $Scripts "start-backend.ps1"))
Start-Process powershell -WindowStyle Hidden -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $Scripts "start-worker.ps1"))
Start-Process powershell -WindowStyle Hidden -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-File", (Join-Path $Scripts "start-frontend.ps1"))
Write-Host "Services are starting. Open http://localhost:3000 in a few seconds."

