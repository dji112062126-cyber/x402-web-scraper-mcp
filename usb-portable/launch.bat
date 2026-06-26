@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

:: ============================================================
::  Claude Code + CC-Switch — USB Portable Launcher
::  Insert USB → double-click launch.bat → work → eject USB
::  Zero traces on host machine after USB removal.
:: ============================================================

:: Use script directory as base (works from any folder, not just USB root)
set "USB_BASE=%~dp0"

:: --- Environment redirection: everything lives on USB ---
set "PATH=%USB_BASE%tools\node;%USB_BASE%tools\claude-code\node_modules\.bin;%PATH%"
set "HOME=%USB_BASE%home"
set "USERPROFILE=%USB_BASE%home"
set "APPDATA=%USB_BASE%home\AppData\Roaming"
set "LOCALAPPDATA=%USB_BASE%home\AppData\Local"
set "NPM_CONFIG_CACHE=%USB_BASE%home\.npm"
set "NPM_CONFIG_PREFIX=%USB_BASE%tools\claude-code"
set "CLAUDE_CONFIG_DIR=%USB_BASE%home\.claude"

:: --- Verify USB tools exist ---
if not exist "%USB_BASE%tools\node\node.exe" (
    echo [ERROR] Node.js not found. Run setup.bat first.
    pause
    exit /b 1
)

if not exist "%USB_BASE%tools\claude-code\node_modules\.bin\claude.cmd" (
    echo [ERROR] Claude Code not found. Run setup.bat first.
    pause
    exit /b 1
)

:: ============================================================
echo.
echo   ╔══════════════════════════════════════════╗
echo   ║  Claude Code USB Portable v1.0          ║
echo   ║  Base: %USB_BASE%║
echo   ╚══════════════════════════════════════════╝
echo.
echo   All data stored on USB. Zero traces on host.
echo.

:: --- Optional: Launch CC-Switch ---
if exist "%USB_BASE%\tools\cc-switch\cc-switch.exe" (
    echo   [*] Starting CC-Switch ^(API switcher^)...
    start "" "%USB_BASE%\tools\cc-switch\cc-switch.exe"
)

:: --- Launch interactive shell ---
echo   [*] Starting Claude Code shell...
echo   ─────────────────────────────────────────
echo.
echo   Type 'claude' to start, 'exit' to close.
echo   IMPORTANT: Close CC-Switch before ejecting USB!
echo.
echo   ─────────────────────────────────────────
echo.

:: Start shell with all env vars set
cmd /k "cd /d %USB_BASE% && title Claude Code USB [%USB_BASE%]"
