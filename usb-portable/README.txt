============================================================
  Claude Code + CC-Switch — USB Portable
  Insert → Work → Eject. Zero traces on host.
============================================================

REQUIREMENTS
------------
- Windows 11 (target machine)
- USB drive (32GB recommended, ~400MB actually used)
- Internet connection (for Claude Code API calls)
- The USB drive itself (obviously)

HOW TO SET UP (do this ONCE on your main PC)
---------------------------------------------
1. Copy this entire folder to your USB drive root
2. Double-click setup.bat on the USB drive
3. Enter your USB drive letter when prompted
4. Wait for setup to complete (downloads Node.js, installs Claude Code)
5. Eject USB safely

WHAT SETUP DOES
---------------
- Downloads Node.js v24.16.0 (portable zip) → USB\tools\node\
- Copies CC-Switch.exe from your PC → USB\tools\cc-switch\
- Copies .claude config (API tokens, settings) → USB\home\.claude\
- Copies CC-Switch app preferences → USB\home\AppData\
- Installs @anthropic-ai/claude-code → USB\tools\claude-code\

HOW TO USE (on any Windows 11 machine)
---------------------------------------
1. Insert USB
2. Double-click launch.bat
3. CC-Switch starts automatically (manage API keys)
4. In the command window, type: claude
5. When done:
   a. Close CC-Switch window
   b. Type 'exit' in the command window
   c. Eject USB safely

USB DRIVE STRUCTURE
-------------------
USB:\
  +-- launch.bat              <-- Double-click to start
  +-- setup.bat               <-- First-time setup only
  +-- tools\
  |     +-- node\             Portable Node.js
  |     +-- cc-switch\        CC-Switch API manager
  |     +-- claude-code\      Claude Code CLI (npm)
  +-- home\
        +-- .claude\          Claude config & credentials
        +-- AppData\          CC-Switch app data
        +-- .npm\             npm cache

HOW IT WORKS
------------
All environment variables (HOME, APPDATA, LOCALAPPDATA, etc.)
are redirected to USB before launching any tool. This means:

  - Claude Code reads/writes config ONLY on USB
  - CC-Switch stores ALL data on USB
  - Nothing is written to C:\Users\ on the host
  - When you close the window, all redirections vanish
  - After USB eject: zero files, zero registry keys, zero traces

TROUBLESHOOTING
---------------
Q: "Node.js not found on USB" error?
A: Run setup.bat again, or manually download:
   https://nodejs.org/dist/v24.16.0/node-v24.16.0-win-x64.zip
   Extract to USB\tools\node\ (node.exe should be at the root)

Q: "Claude Code not found" error?
A: Open a cmd as Admin, navigate to USB, run:
   tools\node\npm install --prefix tools\claude-code @anthropic-ai/claude-code

Q: Claude Code asks me to login?
A: Your API keys weren't copied. Check USB\home\.claude\settings.json
   It should have ANTHROPIC_AUTH_TOKEN and ANTHROPIC_BASE_URL in env.

Q: CC-Switch doesn't start?
A: It might need WebView2 runtime. Windows 11 has it preinstalled.
   If missing, download from: https://developer.microsoft.com/microsoft-edge/webview2/

Q: Can I use this on a Mac or Linux?
A: No, this setup is Windows-only. But the same principle works —
   use shell scripts instead of .bat, and download Node.js for the target OS.

UPDATING CLAUDE CODE
--------------------
To update Claude Code on the USB:
  USB\tools\node\npm install --prefix USB\tools\claude-code @anthropic-ai/claude-code@latest

SECURITY NOTE
-------------
Your API tokens are stored in USB\home\.claude\settings.json.
Keep your USB drive secure! If lost, rotate your API keys immediately.
