@echo off
title PC Repair Tool v1.0

echo.
echo ================================================
echo   PC Repair Tool v1.0
echo   Auto-Fix for Blue Screen / Crash Issues
echo ================================================
echo.
echo   This tool will:
echo   - Disable Fast Startup (fixes Event 41)
echo   - Set balanced power plan (cooler CPU)
echo   - Run SFC to fix system files
echo   - Check disk for errors
echo   - Configure crash dumps properly
echo   - Reset network stack
echo   - Fix stopped services
echo   - Reset Windows Update cache
echo   - Provide GPU driver installation guide
echo.
echo   NO personal data is modified or collected.
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

:: Go to USB directory
cd /d "%~dp0"

:: Run repair
echo [*] Starting repair...
echo ================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0fix.ps1"

echo.
echo ================================================
echo   Repair complete. Check Report in USB "RepairLog" folder.
echo ================================================
echo.
pause
