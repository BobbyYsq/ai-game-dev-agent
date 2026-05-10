$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Write-Host "[bootstrap] Starting on Windows"
Write-Host "First launch requires internet access to download runtime and dependencies."
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
