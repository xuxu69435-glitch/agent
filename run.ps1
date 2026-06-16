$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root
$env:PYTHONNOUSERSITE = "1"

$Python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $Python)) {
    Write-Host "Local virtual environment not found. Initializing..."
    powershell -NoProfile -ExecutionPolicy Bypass -File (Join-Path $Root "setup.ps1")
    if ($LASTEXITCODE -ne 0) {
        throw "Environment initialization failed."
    }
}

& $Python main.py @args
exit $LASTEXITCODE
