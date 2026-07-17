# 0day Windows installer
# run this in PowerShell as Administrator
# right-click -> Run with PowerShell, or: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "SilentlyContinue"

Write-Host ""
Write-Host "    ___  _____      __     __" -ForegroundColor Red
Write-Host "   / _ \|  __ \   /\ \   / /" -ForegroundColor Red
Write-Host "  | | | | |  | | /  \ \_/ / " -ForegroundColor Red
Write-Host "  | | | | |  | |/ /\ \ \ /  " -ForegroundColor Red
Write-Host "  | |_| | |__| / ____ \| |   " -ForegroundColor Red
Write-Host "   \___/|_____/_/    \_\_|   " -ForegroundColor Red
Write-Host ""
Write-Host "  0day Windows Installer" -ForegroundColor Cyan
Write-Host ""

# check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[!] not running as admin. attempting to elevate..." -ForegroundColor Yellow
    Start-Process powershell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    exit
}

Write-Host "[*] running as admin" -ForegroundColor Green
Write-Host ""

# ============================================================
#  STEP 1: Check/install package managers
# ============================================================
Write-Host "[1/5] checking package managers..." -ForegroundColor Green

$hasWinget = Get-Command winget -ErrorAction SilentlyContinue
$hasChoco = Get-Command choco -ErrorAction SilentlyContinue

if (-not $hasWinget) {
    Write-Host "  [*] winget not found, installing..." -ForegroundColor Yellow
    # install winget via.msixbundle
    $wingetUrl = "https://aka.ms/getwinget"
    $wingetTemp = "$env:TEMP\winget.msixbundle"
    try {
        Invoke-WebRequest -Uri $wingetUrl -OutFile $wingetTemp -UseBasicParsing
        Add-AppxPackage -Path $wingetTemp
        Write-Host "  [+] winget installed" -ForegroundColor Green
    } catch {
        Write-Host "  [!] winget install failed, trying chocolatey..." -ForegroundColor Yellow
        if (-not $hasChoco) {
            Set-ExecutionPolicy Bypass -Scope Process -Force
            [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
            Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
            $hasChoco = Get-Command choco -ErrorAction SilentlyContinue
        }
    }
}

if (-not $hasChoco -and -not (Get-Command choco -ErrorAction SilentlyContinue)) {
    Write-Host "  [*] installing chocolatey as backup..." -ForegroundColor Yellow
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
}

Write-Host "  [+] package managers ready" -ForegroundColor Green
Write-Host ""

# ============================================================
#  STEP 2: Install Python
# ============================================================
Write-Host "[2/5] checking Python..." -ForegroundColor Green

$hasPython = Get-Command python -ErrorAction SilentlyContinue
if (-not $hasPython) {
    $hasPython = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $hasPython) {
    Write-Host "  [*] Python not found, installing..." -ForegroundColor Yellow
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    } elseif (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install python3 -y
    } else {
        Write-Host "  [!] cannot install Python automatically. download from python.org" -ForegroundColor Red
        Write-Host "  [!] make sure to check 'Add Python to PATH' during install" -ForegroundColor Red
        Read-Host "  press Enter after installing Python manually"
    }
    # refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
} else {
    Write-Host "  [+] Python found" -ForegroundColor Green
}

python --version 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
Write-Host ""

# ============================================================
#  STEP 3: Install pip packages
# ============================================================
Write-Host "[3/5] installing Python packages..." -ForegroundColor Green

pip install rich requests pyfiglet --quiet 2>&1 | Out-Null
if ($?) {
    Write-Host "  [+] rich, requests, pyfiglet installed" -ForegroundColor Green
} else {
    Write-Host "  [*] trying pip3..." -ForegroundColor Yellow
    pip3 install rich requests pyfiglet --quiet 2>&1 | Out-Null
}

Write-Host ""

# ============================================================
#  STEP 4: Install tools
# ============================================================
Write-Host "[4/5] installing tools..." -ForegroundColor Green

# nmap
$hasNmap = Get-Command nmap -ErrorAction SilentlyContinue
if (-not $hasNmap) {
    Write-Host "  [*] installing nmap..." -ForegroundColor Yellow
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install Insecure.Nmap --accept-source-agreements --accept-package-agreements
    } elseif (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install nmap -y
    }
} else {
    Write-Host "  [+] nmap found" -ForegroundColor Green
}

# curl (usually built-in on Win10+)
$hasCurl = Get-Command curl.exe -ErrorAction SilentlyContinue
if ($hasCurl) {
    Write-Host "  [+] curl found" -ForegroundColor Green
} else {
    Write-Host "  [!] curl not found (should be built into Windows 10+)" -ForegroundColor Yellow
}

# git (for cloning tools later)
$hasGit = Get-Command git -ErrorAction SilentlyContinue
if (-not $hasGit) {
    Write-Host "  [*] installing git..." -ForegroundColor Yellow
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        winget install Git.Git --accept-source-agreements --accept-package-agreements
    } elseif (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install git -y
    }
} else {
    Write-Host "  [+] git found" -ForegroundColor Green
}

# netcat (via nmap's ncat or windows built-in)
Write-Host "  [~] netcat: nmap install includes ncat (use ncat.exe)" -ForegroundColor Cyan

# hashcat (Windows build exists but needs GPU)
Write-Host "  [~] hashcat: download from hashcat.net if you want GPU cracking" -ForegroundColor Cyan

Write-Host ""

# ============================================================
#  STEP 5: Setup 0day wrapper
# ============================================================
Write-Host "[5/5] setting up 0day..." -ForegroundColor Green

$panelDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$wrapperPath = "$panelDir\0day.bat"

# create the .bat wrapper
$batContent = @"
@echo off
cd /d "$panelDir"
python "%panelDir%\0panel.py" %*
"@

Set-Content -Path $wrapperPath -Value $batContent -Encoding ASCII
Write-Host "  [+] wrapper created: $wrapperPath" -ForegroundColor Green

# add to PATH if not already there
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($currentPath -notlike "*$panelDir*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$panelDir", "User")
    $env:Path += ";$panelDir"
    Write-Host "  [+] added to PATH" -ForegroundColor Green
} else {
    Write-Host "  [+] already in PATH" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  0day installed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  run: 0day" -ForegroundColor Yellow
Write-Host "  or:  python $panelDir\0panel.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "  NOTE: some features work better on Linux:" -ForegroundColor Cyan
Write-Host "  - MAC changer (needs admin + network adapter)" -ForegroundColor Cyan
Write-Host "  - WiFi monitor mode (needs compatible adapter)" -ForegroundColor Cyan
Write-Host "  - aircrack-ng suite (limited on Windows)" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Tools available on Windows:" -ForegroundColor Cyan
Write-Host "  - nmap / ncat" -ForegroundColor Cyan
Write-Host "  - PowerShell reverse shells" -ForegroundColor Cyan
Write-Host "  - metasploit (if installed separately)" -ForegroundColor Cyan
Write-Host "  - all OSINT/web recon (network-based)" -ForegroundColor Cyan
Write-Host "  - all crypto/hash tools" -ForegroundColor Cyan
Write-Host "  - all reference/cheat sheet modules" -ForegroundColor Cyan
Write-Host ""

Read-Host "press Enter to exit"
