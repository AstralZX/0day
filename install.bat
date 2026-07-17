@echo off
title 0day installer
color 0C
echo.
echo     ___  _____      __     __
echo    / _ \|  __ \   /\ \   / /
echo   ^| ^| ^| ^| ^|  ^| ^| /  \ \_/ /
echo   ^| ^| ^| ^| ^|  ^| ^|/ /\ \ \ /
echo   ^| ^|_^| ^| ^|__^| / ____ \ ^| 
echo    \___/^|_____/_/    \_\_^|
echo.
echo   0day Windows Installer
echo.
echo [*] launching PowerShell installer...
echo [*] if UAC pops up, click Yes
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0install.ps1"
