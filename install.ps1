# auto-mouse-mover installer for Windows
#
# Usage (paste into PowerShell):
#   irm https://raw.githubusercontent.com/Diana-Lee0912/auto-mouse-mover/main/install.ps1 | iex
#
# What it does:
#   1. Downloads auto_mouse_mover.py into %USERPROFILE%\auto-mouse-mover
#   2. Adds two files there that you can double-click:
#        "Start auto-mouse-mover.bat"  starts the program
#        "Change settings.bat"         asks for your work hours again
#   3. Asks for your work hours, then starts the program
#
# Running it again updates the program and keeps your saved settings.

$ErrorActionPreference = "Stop"
[Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12

$RawUrl = "https://raw.githubusercontent.com/Diana-Lee0912/auto-mouse-mover/main"
$InstallDir = Join-Path $HOME "auto-mouse-mover"

Write-Host "=== auto-mouse-mover installer ==="
Write-Host ""

# Find a working Python 3. "python" can be a Microsoft Store shortcut that
# doesn't actually run Python, so check that it really works.
$Python = $null
foreach ($cmd in @("python", "py")) {
    try {
        $out = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0 -and "$out" -match "Python 3") { $Python = $cmd; break }
    } catch { }
}
if (-not $Python) {
    Write-Host "Python 3 isn't installed (or isn't on PATH)."
    Write-Host "1. Install it from https://www.python.org/downloads/"
    Write-Host "   and tick 'Add python.exe to PATH' at the bottom of the installer."
    Write-Host "2. Open a NEW PowerShell window and paste the install command again."
    return
}

New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
Write-Host "Downloading to $InstallDir ..."
Invoke-WebRequest -UseBasicParsing -Uri "$RawUrl/auto_mouse_mover.py" -OutFile (Join-Path $InstallDir "auto_mouse_mover.py")

Set-Content -Encoding ASCII -Path (Join-Path $InstallDir "Start auto-mouse-mover.bat") -Value @(
    "@echo off",
    'cd /d "%~dp0"',
    "$Python auto_mouse_mover.py",
    "pause"
)
Set-Content -Encoding ASCII -Path (Join-Path $InstallDir "Change settings.bat") -Value @(
    "@echo off",
    'cd /d "%~dp0"',
    "$Python auto_mouse_mover.py --setup",
    "pause"
)

Write-Host ""
Write-Host "Installed!"
Write-Host "  Next time, open $InstallDir"
Write-Host "  and double-click 'Start auto-mouse-mover'."
Write-Host ""

# Show the folder so the double-click files are easy to find
Start-Process explorer.exe $InstallDir

& $Python (Join-Path $InstallDir "auto_mouse_mover.py") --setup
