#!/usr/bin/env python3
"""
桌面番茄钟 — Pomodoro Timer
25 分钟专注 + 5 分钟短休息，每 4 轮后长休息 15 分钟。
纯 Python + tkinter，无需额外依赖。
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
import math
import os
import sys

# ── 常量 ──────────────────────────────────────────────
WORK_MINUTES   = 25
SHORT_BREAK    = 5
LONG_BREAK     = 15
POMODOROS_BEFORE_LONG = 4

# 颜色主题
COLORS = {
    "work":        "#E65C4B",   # 番茄红
    "short_break": "#4CAF50",   # 绿
    "long_break":  "#2196F3",   # 蓝
    "bg":          "#1E1E2E",   # 深色背景
    "surface":     "#2A2A3C",   # 卡片背景
    "text":        "#E0E0E0",
    "text_dim":    "#999999",
    "accent":      "#E65C4B",
    "ring_bg":     "#2A2A3C",
    "ring_fg":     "#E65C4B",
    "btn_start":   "#E65C4B",
    "btn_pause":   "#FF9800",
    "btn_reset":   "#666666",
    "btn_hover":   "#FF7B6B",
}

# ── 工具函数 ──────────────────────────────────────────
def resource_path(relative_path):
    """获取资源绝对路径（兼容 PyInstaller 打包）"""
    if getattr(sys, '_MEIPASS', None):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# ── 音效 ──────────────────────────────────────────────
def play_beep():
    """使用 winsound 或 print \a 播放提示音"""
    try:
        import winsound
        # 播放 3 声短促的滴
        for _ in range(3):
            winsound.Beep(880, 150)
            time.sleep(0.08)
    except ImportError:
        print("\a")  # 终端响铃 fallback

# ── 主应用 ────────────────────────────────────────────
class PomodoroTimer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🍅 番茄钟")
        self.root.geometry("420x620")
        self.root.minsize(360, 540)
        self.root.configure(bg=COLORS["bg"])
        self.root.resizable(True, True)

        # 窗口图标
        try:
            self.root.iconbitmap(default="tomato.ico")
        except Exception:
            pass

        # ── 状态变量 ──────────────────────────────────
        self.mode = "work"           # work | short_break | long_break
        self.remaining = WORK_MINUTES * 60
        self.total = WORK_MINUTES * 60
        self.running = False
        self.paused = False
        self.pomodoro_count = 0      # 已完成的番茄数
        self.always_on_top = tk.BooleanVar(value=True)
        self.timer_id = None

        # ── 构建界面 ──────────────────────────────────
        self._build_ui()
        self._update_display()

        # 置顶
        self.root.attributes("-topmost", True)

        # 关闭窗口时停止计时器
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── 界面构建 ──────────────────────────────────────
    def _build_ui(self):
        # --- 标题栏 ---
        title_bar = tk.Frame(self.root, bg=COLORS["bg"])
        title_bar.pack(fill=tk.X, padx=20, pady=(20, 0))

        self.title_label = tk.Label(
            title_bar, text="🍅 番茄钟",
            font=("Segoe UI", 18, "bold"),
            fg=COLORS["text"], bg=COLORS["bg"]
        )
        self.title_label.pack(side=tk.LEFT)

        # 置顶切换
        top_cb = tk.Checkbutton(
            title_bar, text="置顶", variable=self.always_on_top,
            command=self._toggle_top,
            font=("Segoe UI", 10),
            fg=COLORS["text_dim"], bg=COLORS["bg"],
            selectcolor=COLORS["surface"],
            activebackground=COLORS["bg"],
            activeforeground=COLORS["text"]
        )
        top_cb.pack(side=tk.RIGHT)

        # --- 环形进度区 ---
        self.canvas_size = 280
        self.canvas = tk.Canvas(
            self.root,
            width=self.canvas_size, height=self.canvas_size,
            bg=COLORS["bg"], highlightthickness=0
        )
        self.canvas.pack(pady=(20, 0))

        self._draw_ring()

        # --- 模式标签 ---
        self.mode_label = tk.Label(
            self.root, text="专注工作",
            font=("Segoe UI", 14, "bold"),
            fg=COLORS["accent"], bg=COLORS["bg"]
        )
        self.mode_label.pack(pady=(8, 0))

        # --- 控制按钮 ---
        btn_frame = tk.Frame(self.root, bg=COLORS["bg"])
        btn_frame.pack(pady=(12, 8))

        self.btn_start = self._make_btn(btn_frame, "▶  开始", COLORS["btn_start"], self._start)
        self.btn_start.pack(side=tk.LEFT, padx=5)

        self.btn_pause = self._make_btn(btn_frame, "⏸  暂停", COLORS["btn_pause"], self._pause)
        self.btn_pause.pack(side=tk.LEFT, padx=5)
        self.btn_pause.configure(state=tk.DISABLED)

        self.btn_reset = self._make_btn(btn_frame, "↺  重置", COLORS["btn_reset"], self._reset)
        self.btn_reset.pack(side=tk.LEFT, padx=5)

        # --- 跳过按钮 ---
        self.btn_skip = self._make_btn(
            self.root, "⏭  跳过当前阶段", COLORS["btn_reset"], self._skip
        )
        self.btn_skip.pack(pady=(0, 8))

        # --- 进度条 (session 内) ---
        self.progress = ttk.Progressbar(
            self.root, orient=tk.HORIZONTAL, length=340, mode="determinate"
        )
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TProgressbar", thickness=6, background=COLORS["accent"],
                        troughcolor=COLORS["surface"], borderwidth=0)
        self.progress.pack(pady=(0, 12))

        # --- 番茄计数 ---
        count_frame = tk.Frame(self.root, bg=COLORS["bg"])
        count_frame.pack(pady=(0, 8))

        tk.Label(
            count_frame, text="已完成:",
            font=("Segoe UI", 11),
            fg=COLORS["text_dim"], bg=COLORS["bg"]
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.count_label = tk.Label(
            count_frame, text="0 🍅",
            font=("Segoe UI", 11, "bold"),
            fg=COLORS["text"], bg=COLORS["bg"]
        )
        self.count_label.pack(side=tk.LEFT)

        # --- 设置面板 ---
        settings_frame = tk.Frame(self.root, bg=COLORS["surface"])
        settings_frame.pack(fill=tk.X, padx=20, pady=(12, 20), ipadx=10, ipady=10)

        tk.Label(
            settings_frame, text="⏱ 时长设置（分钟）",
            font=("Segoe UI", 11, "bold"),
            fg=COLORS["text"], bg=COLORS["surface"]
        ).pack(anchor=tk.W, padx=10, pady=(8, 6))

        row = tk.Frame(settings_frame, bg=COLORS["surface"])
        row.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.work_var   = tk.IntVar(value=WORK_MINUTES)
        self.short_var  = tk.IntVar(value=SHORT_BREAK)
        self.long_var   = tk.IntVar(value=LONG_BREAK)

        self._spin_row(row, "工作", self.work_var,  1, 60)
        self._spin_row(row, "短休", self.short_var, 1, 30)
        self._spin_row(row, "长休", self.long_var,  1, 60)

    # ── 自定义微调器行 ────────────────────────────────
    def _spin_row(self, parent, label, var, vmin, vmax):
        f = tk.Frame(parent, bg=COLORS["surface"])
        f.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=4)

        tk.Label(
            f, text=label,
            font=("Segoe UI", 10),
            fg=COLORS["text_dim"], bg=COLORS["surface"]
        ).pack()

        row = tk.Frame(f, bg=COLORS["surface"])
        row.pack()

        btn_sub = tk.Button(
            row, text="−", font=("Segoe UI", 12, "bold"),
            width=2, relief=tk.FLAT,
            bg=COLORS["ring_bg"], fg=COLORS["text"],
            activebackground=COLORS["ring_fg"],
            activeforeground="white",
            cursor="hand2",
            command=lambda: self._spin(var, -1, vmin, vmax)
        )
        btn_sub.pack(side=tk.LEFT)

        val_lbl = tk.Label(
            row, textvariable=var, width=3,
            font=("Segoe UI", 13, "bold"),
            fg=COLORS["text"], bg=COLORS["surface"]
        )
        val_lbl.pack(side=tk.LEFT, padx=6)

        btn_add = tk.Button(
            row, text="+", font=("Segoe UI", 12, "bold"),
            width=2, relief=tk.FLAT,
            bg=COLORS["ring_bg"], fg=COLORS["text"],
            activebackground=COLORS["ring_fg"],
            activeforeground="white",
            cursor="hand2",
            command=lambda: self._spin(var, 1, vmin, vmax)
        )
        btn_add.pack(side=tk.LEFT)

    def _spin(self, var, delta, vmin, vmax):
        v = var.get() + delta
        if vmin <= v <= vmax:
            var.set(v)
            # 如果当前没在运行，更新剩余时间
            if not self.running and not self.paused:
                self._load_duration()
                self._update_display()

    def _load_duration(self):
        """根据 mode 从设置变量加载时长"""
        mapping = {
            "work":        self.work_var,
            "short_break": self.short_var,
            "long_break":  self.long_var,
        }
        minutes = mapping.get(self.mode, self.work_var).get()
        self.total = minutes * 60
        self.remaining = minutes * 60

    # ── 按钮工厂 ──────────────────────────────────────
    def _make_btn(self, parent, text, color, command):
        btn = tk.Button(
            parent, text=text,
            font=("Segoe UI", 12, "bold"),
            relief=tk.FLAT,
            bg=color, fg="white",
            activebackground=COLORS["btn_hover"],
            activeforeground="white",
            cursor="hand2",
            padx=18, pady=6,
            borderwidth=0,
            command=command
        )
        # 悬停效果
        btn.bind("<Enter>", lambda e, b=btn, c=color: b.configure(bg=self._lighten(c)))
        btn.bind("<Leave>", lambda e, b=btn, c=color: b.configure(bg=c))
        return btn

    @staticmethod
    def _lighten(hex_color, factor=0.2):
        c = hex_color.lstrip("#")
        r, g, b = int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)
        r = min(255, int(r + (255 - r) * factor))
        g = min(255, int(g + (255 - g) * factor))
        b = min(255, int(b + (255 - b) * factor))
        return f"#{r:02X}{g:02X}{b:02X}"

    # ── 环形进度条 ────────────────────────────────────
    def _draw_ring(self):
        self.canvas.delete("ring")
        cw = self.canvas_size
        cx, cy = cw // 2, cw // 2
        r = 115
        width = 18

        # 背景环
        self.canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=COLORS["ring_bg"], width=width,
            tags="ring"
        )

        # 进度弧
        angle = (self.remaining / self.total) * 360 if self.total > 0 else 0
        if angle > 0:
            self.canvas.create_arc(
                cx - r, cy - r, cx + r, cy + r,
                start=90, extent=-angle,
                outline=COLORS["ring_fg"], width=width,
                style="arc", tags="ring"
            )

        # 中央时间文本
        mins, secs = divmod(self.remaining, 60)
        time_str = f"{mins:02d}:{secs:02d}"
        self.canvas.create_text(
            cx, cy - 6, text=time_str,
            font=("Consolas", 42, "bold"),
            fill=COLORS["text"], tags="ring"
        )
        # 子标签
        mode_text = {"work": "专注", "short_break": "短休息", "long_break": "长休息"}
        self.canvas.create_text(
            cx, cy + 34, text=mode_text.get(self.mode, ""),
            font=("Segoe UI", 11),
            fill=COLORS["text_dim"], tags="ring"
        )

    def _update_display(self):
        self._draw_ring()

        # 模式标签
        mode_map = {
            "work":        ("专注工作", COLORS["work"]),
            "short_break": ("短休息",   COLORS["short_break"]),
            "long_break":  ("长休息",   COLORS["long_break"]),
        }
        text, color = mode_map.get(self.mode, ("", COLORS["accent"]))
        self.mode_label.configure(text=text, fg=color)

        # 进度条
        pct = 100 - (self.remaining / self.total) * 100 if self.total > 0 else 0
        self.progress["value"] = pct

        # 环形颜色
        COLORS["ring_fg"] = color
        COLORS["accent"] = color
        style = ttk.Style()
        style.configure("TProgressbar", background=color)

        # 更新窗口标题
        mins, secs = divmod(self.remaining, 60)
        self.root.title(f"🍅 {mins:02d}:{secs:02d} — {text}")

    # ── 控制逻辑 ──────────────────────────────────────
    def _start(self):
        if self.running:
            return
        if self.paused:
            self.paused = False
        else:
            self._load_duration()

        self.running = True
        self.btn_start.configure(state=tk.DISABLED, text="▶  运行中")
        self.btn_pause.configure(state=tk.NORMAL)
        self._tick()

    def _pause(self):
        self.paused = True
        self.running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.btn_start.configure(state=tk.NORMAL, text="▶  继续")
        self.btn_pause.configure(state=tk.DISABLED)

    def _reset(self):
        self.running = False
        self.paused = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self._load_duration()
        self.btn_start.configure(state=tk.NORMAL, text="▶  开始")
        self.btn_pause.configure(state=tk.DISABLED)
        self._update_display()

    def _skip(self):
        """跳过当前阶段"""
        self.running = False
        self.paused = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
        self.remaining = 0
        self._on_complete()

    def _tick(self):
        if not self.running:
            return
        if self.remaining > 0:
            self.remaining -= 1
            self._update_display()
            self.timer_id = self.root.after(1000, self._tick)
        else:
            self.running = False
            self._on_complete()

    def _on_complete(self):
        """当前阶段结束，切换模式"""
        # 播放提示音（异步避免阻塞 UI）
        threading.Thread(target=play_beep, daemon=True).start()

        if self.mode == "work":
            self.pomodoro_count += 1
            self.count_label.configure(text=f"{self.pomodoro_count} 🍅")
            if self.pomodoro_count % POMODOROS_BEFORE_LONG == 0:
                self.mode = "long_break"
            else:
                self.mode = "short_break"
        else:
            self.mode = "work"

        self._load_duration()
        self.btn_start.configure(state=tk.NORMAL, text="▶  开始")
        self.btn_pause.configure(state=tk.DISABLED)
        self._update_display()

        # 弹窗提醒
        mode_map = {
            "work":        ("专注时间到！", "开始新的番茄钟吧 🍅"),
            "short_break": ("休息结束！",   "该开始专注了 💪"),
            "long_break":  ("长休息结束！",  "精力充沛，开始吧 ⚡"),
        }
        title, msg = mode_map.get(self.mode, ("", ""))
        self._flash_window()
        self._show_toast(title, msg)

    def _flash_window(self):
        """闪烁任务栏图标"""
        try:
            self.root.attributes("-topmost", True)
            self.root.update()
            self.root.attributes("-topmost", self.always_on_top.get())
        except Exception:
            pass

    def _show_toast(self, title, message):
        """简单的弹窗提示（3 秒后自动消失）"""
        toast = tk.Toplevel(self.root)
        toast.title("")
        toast.geometry("300x90")
        toast.configure(bg=COLORS["surface"])
        toast.overrideredirect(True)  # 无边框
        toast.attributes("-topmost", True)

        # 居中于主窗口
        self.root.update_idletasks()
        rx, ry = self.root.winfo_rootx(), self.root.winfo_rooty()
        rw, rh = self.root.winfo_width(), self.root.winfo_height()
        x = rx + (rw - 300) // 2
        y = ry + (rh - 90) // 2
        toast.geometry(f"+{x}+{y}")

        tk.Label(
            toast, text=title,
            font=("Segoe UI", 13, "bold"),
            fg=COLORS["text"], bg=COLORS["surface"]
        ).pack(pady=(14, 0))

        tk.Label(
            toast, text=message,
            font=("Segoe UI", 11),
            fg=COLORS["text_dim"], bg=COLORS["surface"]
        ).pack()

        # 淡出 + 销毁
        def fade_out(alpha=1.0):
            if alpha <= 0:
                toast.destroy()
                return
            try:
                toast.attributes("-alpha", alpha)
                toast.after(50, lambda: fade_out(alpha - 0.05))
            except Exception:
                toast.destroy()

        toast.after(2500, lambda: fade_out())

    def _toggle_top(self):
        self.root.attributes("-topmost", self.always_on_top.get())

    def _on_close(self):
        self.running = False
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.root.destroy()

    # ── 启动 ──────────────────────────────────────────
    def run(self):
        self.root.mainloop()


# ── 入口 ──────────────────────────────────────────────
if __name__ == "__main__":
    app = PomodoroTimer()
    app.run()
