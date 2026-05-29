[CmdletBinding()]
param(
    [string]$PythonVersion = "3.13",
    [switch]$Recreate
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$VenvPath = Join-Path $ProjectRoot ".venv"
$PythonPath = Join-Path $VenvPath "Scripts\python.exe"
$RequirementsPath = Join-Path $ProjectRoot "requirements.txt"
$VerifyPath = Join-Path $PSScriptRoot "verify_environment.py"

Set-Location $ProjectRoot

if ($Recreate -and (Test-Path -LiteralPath $VenvPath)) {
    Write-Host "Removing existing virtual environment at $VenvPath"
    Remove-Item -LiteralPath $VenvPath -Recurse -Force
}

if (-not (Test-Path -LiteralPath $PythonPath)) {
    Write-Host "Creating .venv with Python $PythonVersion"
    & py "-$PythonVersion" -m venv $VenvPath
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to create .venv with Python $PythonVersion. Install that Python version or pass -PythonVersion with an installed version."
    }
}

Write-Host "Using $(& $PythonPath --version)"
& $PythonPath -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Unable to update pip." }

& $PythonPath -m pip install -r $RequirementsPath
if ($LASTEXITCODE -ne 0) { throw "Unable to install project dependencies." }

# On Windows dlib-bin exposes the dlib module, but face-recognition's package
# metadata only recognizes a distribution named dlib.
& $PythonPath -m pip install --no-deps "face-recognition==1.3.0"
if ($LASTEXITCODE -ne 0) { throw "Unable to install face-recognition." }

& $PythonPath $VerifyPath
if ($LASTEXITCODE -ne 0) { throw "Environment verification failed." }

Write-Host ""
Write-Host "Environment setup complete."
Write-Host "Activate it: .\.venv\Scripts\Activate.ps1"
Write-Host "Run the app: streamlit run app.py"
