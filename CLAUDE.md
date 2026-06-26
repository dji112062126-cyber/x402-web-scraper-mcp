# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Run the app

```powershell
& "C:\Program Files\Python312\python.exe" pomodoro.py
```

## Architecture

Single-file tkinter desktop app (`pomodoro.py`). Zero external dependencies — only Python stdlib.

- `PomodoroTimer` class owns all state: `mode` (`work|short_break|long_break`), `remaining` seconds, `running`/`paused` booleans, `pomodoro_count`.
- `COLORS` dict is the theme — mutated at runtime (`COLORS["ring_fg"]` and `COLORS["accent"]` change per mode for color-coded feedback).
- Timer loop uses `tk.after(1000, …)` rather than `time.sleep` to keep the UI responsive. Phase transitions fire in `_on_complete()` which switches mode, plays beep via background thread, and shows a fade-out toast.
- `_draw_ring()` redraws the entire canvas on each tick — creates a background oval and a foreground arc whose extent decreases from 360° to 0°.
- Duration settings (`work_var`, `short_var`, `long_var`) are `tk.IntVar` values bound to custom ± spin buttons; `_load_duration()` re-reads them when a timer phase starts.

## Python

Python 3.12.9 installed at `C:\Program Files\Python312\python.exe`. tkinter is included (no separate install). The scripts use Unix line endings (LF) but the repo is on Windows — `git` warns about CRLF conversion.

## 机场订阅 (sakuracat)

可用订阅链接获取代理节点：

```
https://c7a91e3b-84d2-4c6f-9b71-2e8d4a6f3c11.com/sabusuku?token=d32bd54b907dd08e95148f7f5a5f986d
```

调用方式：
- 获取节点列表：`curl -s "订阅链接" | base64 -d`（Clash 格式）或直接导入 Clash/V2Ray 客户端
- 需要使用代理访问外部资源时，可从此订阅获取可用节点

## Git remote

```
origin  git@github.com:dji112062126-cyber/first-cc.git (main)
```
