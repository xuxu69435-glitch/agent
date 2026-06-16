$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
Set-Location $Root
$env:PYTHONNOUSERSITE = "1"

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment .venv ..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create .venv."
    }
}

$VenvConfig = Get-Content ".venv\pyvenv.cfg" -Raw
if ($VenvConfig -match "include-system-site-packages\s*=\s*true") {
    throw ".venv is configured to use system site-packages. Remove it and rerun setup.ps1."
}

$env:PIP_REQUIRE_VIRTUALENV = "1"
Write-Host "Installing dependencies ..."
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    throw "Failed to upgrade pip."
}

& ".\.venv\Scripts\python.exe" -m pip install -e ".[dev]"
if ($LASTEXITCODE -ne 0) {
    throw "Failed to install project dependencies."
}

Write-Host ""
Write-Host "Environment is isolated in: $Root\.venv"
Write-Host ""
Write-Host "Recommended startup command:"
Write-Host "  .\run.ps1"
Write-Host ""
Write-Host "Or activate the local environment manually:"
Write-Host "  .\.venv\Scripts\Activate.ps1"
Write-Host "  python main.py"
