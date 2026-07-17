# 0day Windows installer
# right-click install.bat -> Run with PowerShell
# or: powershell -ExecutionPolicy Bypass -File install.ps1

$ErrorActionPreference = "Continue"
$panelDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "    ___  _____      __     __" -ForegroundColor Red
Write-Host "   / _ \|  __ \   /\ \   / /" -ForegroundColor Red
Write-Host "  | | | | |  | | /  \ \_/ / " -ForegroundColor Red
Write-Host "  | | | | |  | |/ /\ \ \ /  " -ForegroundColor Red
Write-Host "  | |_| | |__| / ____ \| |   " -ForegroundColor Red
Write-Host "   \___/|_____/_/    \_\_|   " -ForegroundColor Red
Write-Host ""
Write-Host "  Windows Installer" -ForegroundColor Cyan
Write-Host "  $panelDir" -ForegroundColor DarkGray
Write-Host ""

# ============================================================
#  check admin
# ============================================================
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "[*] requesting admin rights..." -ForegroundColor Yellow
    try {
        Start-Process powershell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
        exit
    } catch {
        Write-Host "[!] could not get admin. continuing without it (some installs may fail)" -ForegroundColor Yellow
    }
}

# ============================================================
#  STEP 1: make sure python exists
# ============================================================
Write-Host "[1/5] checking Python..." -ForegroundColor Green

$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    $found = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($found) {
        $ver = & $cmd --version 2>&1
        if ($ver -match "Python 3") {
            $pythonCmd = $cmd
            Write-Host "  [+] found: $ver ($cmd)" -ForegroundColor Green
            break
        }
    }
}

if (-not $pythonCmd) {
    Write-Host "  [!] Python 3 not found" -ForegroundColor Red
    Write-Host "  [*] trying to install Python..." -ForegroundColor Yellow
    
    $installed = $false
    
    # try winget
    $wg = Get-Command winget -ErrorAction SilentlyContinue
    if ($wg) {
        Write-Host "  [*] installing via winget..." -ForegroundColor Yellow
        winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements --silent 2>&1 | Out-Null
        if ($?) { $installed = $true }
    }
    
    # try choco
    if (-not $installed) {
        $choco = Get-Command choco -ErrorAction SilentlyContinue
        if ($choco) {
            Write-Host "  [*] installing via chocolatey..." -ForegroundColor Yellow
            choco install python3 -y --no-progress 2>&1 | Out-Null
            if ($?) { $installed = $true }
        }
    }
    
    # try scoop
    if (-not $installed) {
        $scoop = Get-Command scoop -ErrorAction SilentlyContinue
        if ($scoop) {
            Write-Host "  [*] installing via scoop..." -ForegroundColor Yellow
            scoop install python 2>&1 | Out-Null
            if ($?) { $installed = $true }
        }
    }
    
    if ($installed) {
        # refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        foreach ($cmd in @("python", "python3", "py")) {
            $found = Get-Command $cmd -ErrorAction SilentlyContinue
            if ($found) {
                $ver = & $cmd --version 2>&1
                if ($ver -match "Python 3") {
                    $pythonCmd = $cmd
                    Write-Host "  [+] Python installed: $ver" -ForegroundColor Green
                    break
                }
            }
        }
    }
    
    if (-not $pythonCmd) {
        Write-Host ""
        Write-Host "  [!] FAILED to install Python automatically" -ForegroundColor Red
        Write-Host "  [!] download manually from: https://www.python.org/downloads/" -ForegroundColor Red
        Write-Host "  [!] IMPORTANT: check 'Add Python to PATH' during install!" -ForegroundColor Red
        Write-Host ""
        Write-Host "  after installing, run this script again" -ForegroundColor Yellow
        Read-Host "  press Enter to exit"
        exit 1
    }
} else {
    Write-Host "  [+] Python ready" -ForegroundColor Green
}

# ============================================================
#  STEP 2: pip packages
# ============================================================
Write-Host "[2/5] installing Python packages..." -ForegroundColor Green

$pipCmd = "$pythonCmd -m pip"
$pkgs = @("rich", "requests")

foreach ($pkg in $pkgs) {
    $check = & $pythonCmd -c "import $pkg" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [+] $pkg already installed" -ForegroundColor Green
    } else {
        Write-Host "  [*] installing $pkg..." -ForegroundColor Yellow
        & $pythonCmd -m pip install $pkg --quiet --disable-pip-version-check 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  [+] $pkg installed" -ForegroundColor Green
        } else {
            # try with --user flag
            & $pythonCmd -m pip install $pkg --quiet --user --disable-pip-version-check 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [+] $pkg installed (user)" -ForegroundColor Green
            } else {
                Write-Host "  [!] failed to install $pkg" -ForegroundColor Red
            }
        }
    }
}

# ============================================================
#  STEP 3: nmap
# ============================================================
Write-Host "[3/5] checking nmap..." -ForegroundColor Green

$hasNmap = Get-Command nmap -ErrorAction SilentlyContinue
if ($hasNmap) {
    Write-Host "  [+] nmap found" -ForegroundColor Green
} else {
    Write-Host "  [*] installing nmap..." -ForegroundColor Yellow
    $installed = $false
    
    $wg = Get-Command winget -ErrorAction SilentlyContinue
    if ($wg) {
        winget install Insecure.Nmap --accept-source-agreements --accept-package-agreements --silent 2>&1 | Out-Null
        if ($?) { $installed = $true }
    }
    
    if (-not $installed) {
        $choco = Get-Command choco -ErrorAction SilentlyContinue
        if ($choco) {
            choco install nmap -y --no-progress 2>&1 | Out-Null
            if ($?) { $installed = $true }
        }
    }
    
    if (-not $installed) {
        $scoop = Get-Command scoop -ErrorAction SilentlyContinue
        if ($scoop) {
            scoop install nmap 2>&1 | Out-Null
        }
    }
    
    # refresh PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    
    if (Get-Command nmap -ErrorAction SilentlyContinue) {
        Write-Host "  [+] nmap installed" -ForegroundColor Green
    } else {
        Write-Host "  [!] nmap install failed. download from https://nmap.org/download.html" -ForegroundColor Yellow
    }
}

# ============================================================
#  STEP 4: git
# ============================================================
Write-Host "[4/5] checking git..." -ForegroundColor Green

$hasGit = Get-Command git -ErrorAction SilentlyContinue
if ($hasGit) {
    Write-Host "  [+] git found" -ForegroundColor Green
} else {
    Write-Host "  [*] installing git..." -ForegroundColor Yellow
    $wg = Get-Command winget -ErrorAction SilentlyContinue
    if ($wg) {
        winget install Git.Git --accept-source-agreements --accept-package-agreements --silent 2>&1 | Out-Null
    } else {
        $choco = Get-Command choco -ErrorAction SilentlyContinue
        if ($choco) { choco install git -y --no-progress 2>&1 | Out-Null }
    }
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    if (Get-Command git -ErrorAction SilentlyContinue) {
        Write-Host "  [+] git installed" -ForegroundColor Green
    } else {
        Write-Host "  [!] git install failed" -ForegroundColor Yellow
    }
}

# ============================================================
#  STEP 5: create wrapper + PATH
# ============================================================
Write-Host "[5/5] setting up 0day..." -ForegroundColor Green

# fix any forward slashes to backslashes for Windows
$panelDirWin = $panelDir.Replace('/', '\')

# create 0day.bat wrapper
$batPath = Join-Path $panelDirWin "0day.bat"
$batContent = "@echo off`r`ncd /d `"$panelDirWin`"`r`n`"$pythonCmd`" `"$panelDirWin\0panel.py`" %*`r`n"
[System.IO.File]::WriteAllText($batPath, $batContent, [System.Text.Encoding]::ASCII)
Write-Host "  [+] created $batPath" -ForegroundColor Green

# create 0day.ps1 wrapper (for PowerShell users)
$ps1Path = Join-Path $panelDirWin "0day.ps1"
$ps1Content = "Set-Location `"$panelDirWin`"`r`n& $pythonCmd `"$panelDirWin\0panel.py`" @args"
[System.IO.File]::WriteAllText($ps1Path, $ps1Content, [System.Text.Encoding]::UTF8)
Write-Host "  [+] created $ps1Path" -ForegroundColor Green

# add to user PATH
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if ($userPath -notlike "*$panelDirWin*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$panelDirWin", "User")
    $env:Path += ";$panelDirWin"
    Write-Host "  [+] added to PATH" -ForegroundColor Green
} else {
    Write-Host "  [+] already in PATH" -ForegroundColor Green
}

# ============================================================
#  done
# ============================================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  0day installed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  open a NEW terminal and run:" -ForegroundColor Yellow
Write-Host "    0day" -ForegroundColor White
Write-Host ""
Write-Host "  or from this directory:" -ForegroundColor Yellow
Write-Host "    .\0day.bat" -ForegroundColor White
Write-Host "    .\0day.ps1" -ForegroundColor White
Write-Host "    $pythonCmd 0panel.py" -ForegroundColor White
Write-Host ""

# quick test
Write-Host "[*] testing..." -ForegroundColor Cyan
$testResult = & $pythonCmd -c "import rich; import requests; print('ok')" 2>&1
if ($testResult -eq "ok") {
    Write-Host "[+] test passed! 0day is ready" -ForegroundColor Green
} else {
    Write-Host "[!] test failed: $testResult" -ForegroundColor Red
    Write-Host "[!] try running: $pythonCmd -m pip install rich requests" -ForegroundColor Yellow
}

Write-Host ""
Read-Host "press Enter to exit"
