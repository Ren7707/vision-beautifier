$ErrorActionPreference = "Stop"

function Run($File, $Arguments) {
    & $File @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$File failed with exit code $LASTEXITCODE"
    }
}

$venv = ".venv"
$runtimePython = "C:\Users\jin'ri\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$basePython = if ($env:PYTHON -and (Test-Path $env:PYTHON)) {
    $env:PYTHON
} elseif (Test-Path $runtimePython) {
    $runtimePython
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    "py"
} else {
    "python"
}
if (-not (Test-Path ".\$venv\Scripts\python.exe")) {
    Run $basePython @("-m", "venv", $venv)
}
$py = ".\$venv\Scripts\python.exe"
Run $py @("-m", "pip", "install", "--upgrade", "pip")
Run $py @("-m", "pip", "uninstall", "-y", "opencv-python")
Run $py @("-m", "pip", "install", "-r", "requirements.txt")
Run $py @("-m", "PyInstaller", "--noconfirm", "VisionBeautifier.spec")
Write-Host "EXE: dist\VisionBeautifier.exe"
