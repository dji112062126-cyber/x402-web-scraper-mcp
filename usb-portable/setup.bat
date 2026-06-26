@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul 2>&1

:: ============================================================
::  Claude Code USB — Setup Script
::  Run ONCE on your current PC to prepare the USB drive.
:: ============================================================

echo.
echo   ╔══════════════════════════════════════════════════╗
echo   ║  Claude Code USB — Setup                        ║
echo   ║  Prepares USB drive for portable use            ║
echo   ╚══════════════════════════════════════════════════╝
echo.

:: --- Step 0: Detect USB drive ---
echo Available drives:
for %%d in (D E F G H I J K L M N O P Q R S T U V W X Y Z) do (
    if exist "%%d:\" (
        for /f "tokens=3" %%t in ('vol %%d: 2^>nul') do (
            echo   %%d:  [%%t]
        )
    )
)
echo.
set /p USB_LETTER="Enter your USB drive letter (e.g., D): "
set "USB=%USB_LETTER%:"

if not exist "%USB%\" (
    echo [ERROR] Drive %USB% not found!
    pause
    exit /b 1
)

echo.
echo Target: !USB!\
echo.

:: --- Step 1: Create directory structure ---
echo [1/7] Creating directory structure...
mkdir "%USB%\tools\node"              2>nul
mkdir "%USB%\tools\cc-switch"         2>nul
mkdir "%USB%\tools\claude-code"       2>nul
mkdir "%USB%\home\.claude"            2>nul
mkdir "%USB%\home\.npm"               2>nul
mkdir "%USB%\home\AppData\Roaming\com.ccswitch.desktop" 2>nul
mkdir "%USB%\home\AppData\Local\com.ccswitch.desktop"   2>nul
echo   ^> Created folder structure

:: --- Step 2: Download & extract Node.js portable ---
echo [2/7] Setting up Node.js v24.16.0 (portable)...

if exist "%USB%\tools\node\node.exe" (
    echo   ^> Node.js already exists, skipping download.
) else (
    set "NODE_ZIP=%USB%\node-tmp.zip"
    set "NODE_URL=https://nodejs.org/dist/v24.16.0/node-v24.16.0-win-x64.zip"

    echo   ^> Downloading from nodejs.org ...
    curl -L -o "!NODE_ZIP!" "!NODE_URL!" --progress-bar 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo   [WARNING] Download failed!
        echo   Please manually download from:
        echo     !NODE_URL!
        echo   Extract the zip, then copy folder contents to:
        echo     %USB%\tools\node\
        echo   (node.exe should be at %USB%\tools\node\node.exe)
        pause
    ) else (
        echo   ^> Extracting...
        powershell -Command "Expand-Archive -Path '!NODE_ZIP!' -DestinationPath '%USB%\tools\node-tmp' -Force"
        move "%USB%\tools\node-tmp\node-v24.16.0-win-x64\*" "%USB%\tools\node\" >nul 2>&1
        rmdir /s /q "%USB%\tools\node-tmp" 2>nul
        del "!NODE_ZIP!" 2>nul
        echo   ^> Node.js extracted successfully.
    )
)

:: --- Step 3: Copy CC-Switch ---
echo [3/7] Copying CC-Switch...

set "CC_SRC=%LOCALAPPDATA%\Programs\CC Switch\cc-switch.exe"
if exist "!CC_SRC!" (
    copy /y "!CC_SRC!" "%USB%\tools\cc-switch\cc-switch.exe" >nul
    echo   ^> CC-Switch copied ^(30MB^)
) else (
    echo   [WARNING] CC-Switch not found at !CC_SRC!
    echo   Please manually copy cc-switch.exe to:
    echo     %USB%\tools\cc-switch\
)

:: --- Step 4: Copy Claude Code config ---
echo [4/7] Copying Claude Code configuration...

set "CLAUDE_SRC=%USERPROFILE%\.claude"
if exist "!CLAUDE_SRC!" (
    :: Copy settings.json (contains API tokens), skills, and essential config
    :: Skip large caches that rebuild automatically
    robocopy "!CLAUDE_SRC!" "%USB%\home\.claude" /E /NDL /NFL /NJH /NJS ^
        /XD "cache" "backups" "shell-snapshots" "sessions" "telemetry" "file-history"
    echo   ^> Claude config copied ^(settings, skills, plugins^)
) else (
    echo   [WARNING] No .claude folder found at !CLAUDE_SRC!
    echo   Creating empty config. You may need to configure API keys manually.
    mkdir "%USB%\home\.claude" 2>nul
)

:: --- Step 5: Copy CC-Switch app data ---
echo [5/7] Copying CC-Switch app data...

set "CC_ROAMING=%APPDATA%\com.ccswitch.desktop"
set "CC_LOCAL=%LOCALAPPDATA%\com.ccswitch.desktop"

if exist "!CC_ROAMING!" (
    robocopy "!CC_ROAMING!" "%USB%\home\AppData\Roaming\com.ccswitch.desktop" /E /NDL /NFL /NJH /NJS
    echo   ^> CC-Switch roaming data copied
)

if exist "!CC_LOCAL!" (
    :: Only copy small config files, skip huge EBWebView browser cache
    robocopy "!CC_LOCAL!" "%USB%\home\AppData\Local\com.ccswitch.desktop" /E /NDL /NFL /NJH /NJS ^
        /XD "EBWebView"
    echo   ^> CC-Switch local config copied ^(cache skipped - rebuilds automatically^)
)

:: --- Step 6: Install Claude Code npm package on USB ---
echo [6/7] Installing Claude Code on USB ^(this may take a few minutes^)...

set "NPM_CMD=%USB%\tools\node\npm.cmd"

if exist "%USB%\tools\claude-code\node_modules\@anthropic-ai\claude-code" (
    echo   ^> Claude Code already installed, skipping.
) else (
    echo   ^> Running npm install ^(~230MB, may take 2-5 minutes^)...
    "!NPM_CMD!" install --prefix "%USB%\tools\claude-code" @anthropic-ai/claude-code --no-audit --no-fund
    if !ERRORLEVEL! NEQ 0 (
        echo   [WARNING] npm install failed. You can retry later from USB:
        echo     %USB%\tools\node\npm install --prefix %USB%\tools\claude-code @anthropic-ai/claude-code
    ) else (
        echo   ^> Claude Code installed successfully on USB.
    )
)

:: --- Step 7: Copy launcher to USB root ---
echo [7/7] Copying launcher to USB root...

:: Find launch.bat in the same directory as this setup script
set "SCRIPT_DIR=%~dp0"
if exist "!SCRIPT_DIR!launch.bat" (
    copy /y "!SCRIPT_DIR!launch.bat" "%USB%\launch.bat" >nul
    echo   ^> launch.bat copied to USB root
) else (
    echo   [WARNING] launch.bat not found next to setup.bat
    echo   Make sure launch.bat is on the USB root before using.
)

:: ============================================================
echo.
echo   ╔══════════════════════════════════════════════════╗
echo   ║  SETUP COMPLETE!                                ║
echo   ╚══════════════════════════════════════════════════╝
echo.
echo   USB: %USB%\
echo.
echo   What's on the USB:
echo     tools\node\          — Node.js v24.16.0 (portable)
echo     tools\cc-switch\     — CC-Switch API manager
echo     tools\claude-code\   — Claude Code CLI
echo     home\.claude\        — Claude config & credentials
echo     launch.bat           — Double-click to start
echo.
echo   Next steps:
echo     1. Eject USB safely
echo     2. Insert into target Windows 11 machine
echo     3. Double-click launch.bat
echo     4. Type 'claude' to start
echo.
pause
