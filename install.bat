@echo off
title 0day installer
color 0C
cls
echo.
echo     ___  _____      __     __
echo    / _ \|  __ \   /\ \   / /
echo   ^| ^| ^| ^| ^|  ^| ^| /  \ \_/ /
echo   ^| ^| ^| ^| ^|  ^| ^|/ /\ \ \ /
echo   ^| ^|_^| ^| ^|__^| / ____ \ ^| 
echo    \___/^|_____/_/    \_\_^|
echo.
echo   Windows Installer
echo.

:: check if python is in path
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where python3 >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo [!] Python not found in PATH
        echo [!] install from https://www.python.org/downloads/
        echo [!] make sure to check "Add Python to PATH"
        echo.
        pause
        exit /b 1
    )
)

echo [*] launching PowerShell installer...
echo [*] if UAC popup appears, click Yes
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] installer had errors. try running manually:
    echo     powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
    echo.
    pause
)
