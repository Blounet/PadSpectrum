# ============================================================
#  PadSpectrum - Installeur PowerShell
#  A executer en tant qu'Administrateur
# ============================================================

$ErrorActionPreference = "Stop"
$AppName    = "PadSpectrum"
$AppVersion = "0.0.1"

Clear-Host
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "   $AppName v$AppVersion - Installeur"                 -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""

$defaultDir = "$env:ProgramFiles\PadSpectrum"
Write-Host "Repertoire d'installation par defaut : $defaultDir"
$installDir = Read-Host "Appuyez sur Entree pour accepter ou saisissez un autre chemin"
if ([string]::IsNullOrWhiteSpace($installDir)) {
    $installDir = $defaultDir
}

Write-Host ""
Write-Host "Installation dans : $installDir" -ForegroundColor Yellow
Write-Host ""

if (-not (Test-Path $installDir)) {
    New-Item -ItemType Directory -Path $installDir -Force | Out-Null
    Write-Host "[OK] Repertoire cree." -ForegroundColor Green
} else {
    Write-Host "[OK] Repertoire existant." -ForegroundColor Green
}

Write-Host ""
Write-Host "Verification de Python..." -ForegroundColor Cyan
$pythonOk = $false
try {
    $pyVersion = python --version 2>&1
    Write-Host "[OK] $pyVersion detecte." -ForegroundColor Green
    $pythonOk = $true
} catch {
    $pythonOk = $false
}

if (-not $pythonOk) {
    Write-Host "[INFO] Python non trouve. Telechargement en cours..." -ForegroundColor Yellow
    $pyInstaller = "$env:TEMP\python_installer.exe"
    Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe" -OutFile $pyInstaller
    Start-Process -FilePath $pyInstaller -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -Wait
    Remove-Item $pyInstaller
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-Host "[OK] Python installe." -ForegroundColor Green
}

Write-Host ""
Write-Host "Installation des dependances Python..." -ForegroundColor Cyan
$deps = @("mido", "python-rtmidi", "sounddevice", "numpy", "websockets")
foreach ($dep in $deps) {
    Write-Host "  -> pip install $dep" -ForegroundColor Gray
    pip install $dep --quiet
}
Write-Host "[OK] Dependances installees." -ForegroundColor Green

Write-Host ""
Write-Host "Copie des fichiers..." -ForegroundColor Cyan

$scriptSource = Join-Path $PSScriptRoot "padspectrum.py"
$extSource    = Join-Path $PSScriptRoot "extension"
$extDest      = Join-Path $installDir "extension"

Copy-Item -Path $scriptSource -Destination $installDir -Force
Copy-Item -Path $extSource -Destination $extDest -Recurse -Force

Write-Host "[OK] Fichiers copies." -ForegroundColor Green

Write-Host ""
Write-Host "Creation du lanceur..." -ForegroundColor Cyan

$scriptPath = Join-Path $installDir "padspectrum.py"
$batContent = "@echo off`r`npython `"$scriptPath`"`r`npause"
$batPath    = Join-Path $installDir "PadSpectrum.bat"
Set-Content -Path $batPath -Value $batContent -Encoding ASCII

Write-Host "[OK] Lanceur cree : $batPath" -ForegroundColor Green

Write-Host ""
Write-Host "Creation des raccourcis..." -ForegroundColor Cyan

$WshShell = New-Object -ComObject WScript.Shell

$desktopLink = "$env:USERPROFILE\Desktop\PadSpectrum.lnk"
$shortcut = $WshShell.CreateShortcut($desktopLink)
$shortcut.TargetPath       = $batPath
$shortcut.WorkingDirectory = $installDir
$shortcut.Description      = "PadSpectrum - Visualiseur spectral + controles YouTube"
$shortcut.Save()

$startMenu = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\PadSpectrum.lnk"
$shortcut2 = $WshShell.CreateShortcut($startMenu)
$shortcut2.TargetPath       = $batPath
$shortcut2.WorkingDirectory = $installDir
$shortcut2.Description      = "PadSpectrum - Visualiseur spectral + controles YouTube"
$shortcut2.Save()

Write-Host "[OK] Raccourcis crees (bureau + menu Demarrer)." -ForegroundColor Green

Write-Host ""
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host "   Installation de l'extension Chrome"                  -ForegroundColor Cyan
Write-Host "======================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. Ouvrez Chrome"                                      -ForegroundColor White
Write-Host "  2. Allez sur : chrome://extensions"                    -ForegroundColor White
Write-Host "  3. Activez le Mode developpeur (en haut a droite)"    -ForegroundColor White
Write-Host "  4. Cliquez Charger extension non empaquetee"           -ForegroundColor White
Write-Host "  5. Selectionnez : $extDest"                            -ForegroundColor Cyan
Write-Host ""

$openChrome = Read-Host "Ouvrir Chrome et le dossier maintenant ? (O/N)"
if ($openChrome -eq "O" -or $openChrome -eq "o") {
    Start-Process "chrome" "chrome://extensions"
    Start-Sleep -Seconds 1
    Start-Process "explorer.exe" $extDest
}

Write-Host ""
Write-Host "======================================================" -ForegroundColor Green
Write-Host "   Installation terminee !"                             -ForegroundColor Green
Write-Host "======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Lancez depuis le bureau ou le menu Demarrer."           -ForegroundColor White
Write-Host ""
Read-Host "Appuyez sur Entree pour fermer"
