@echo off
title 电脑诊断工具 v2.0

echo.
echo ================================================
echo      PC Diagnostic Tool v2.0
echo      蓝屏排查 + 硬件全面检测
echo ================================================
echo.

:: Get admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs -Wait"
    exit /b
)
echo [OK] Administrator privileges confirmed
echo.

:: Ensure we are in the USB drive directory
cd /d "%~dp0"
echo [*] Working directory: %CD%
echo.

:: Run the diagnostic
echo [*] Starting diagnostic, please wait...
echo ================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0diagnose.ps1"
set PS_EXIT=%errorlevel%

echo.
echo ================================================
if %PS_EXIT% equ 0 (
    echo [OK] Diagnostic completed!
) else (
    echo [ERROR] Diagnostic failed (exit code: %PS_EXIT%)
    echo Press any key to see error details...
    pause >nul
)

echo.
echo Press any key to exit...
pause >nul
