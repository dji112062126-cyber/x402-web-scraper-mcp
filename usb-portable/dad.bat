@echo off
title PC Diagnostic v2.1

echo.
echo ================================================
echo   PC Diagnostic Tool v2.1
echo   BSOD Analysis + Full Hardware Check
echo ================================================
echo.

:: Admin check
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Requesting admin privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs -Wait"
    exit /b
)
echo [OK] Running as Administrator
echo.

:: Go to USB drive
cd /d "%~dp0"
echo [*] Working dir: %CD%
echo.

:: Run diagnostic
echo [*] Starting diagnostic scan...
echo [*] This takes 1-2 minutes. Please wait...
echo ================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0diagnose.ps1"

echo.
echo ================================================
echo   Done. Check the HTML report in "Report" folder.
echo ================================================
echo.
pause
