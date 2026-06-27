#!/usr/bin/env python3
"""
Personal Project Workstation Dashboard
=======================================
A live dashboard showing project health, wallet balance,
access logs, and platform status — all in one place.

Inspired by Homepage / Glance / Homarr design patterns.

Usage: python dashboard.py
Then open: http://localhost:8888
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler

PROJECT_DIR = Path(__file__).resolve().parent
ACCESS_LOG = PROJECT_DIR / "access.log"
WALLET = "0xcf15b97a41022427f50d4bb284c108eb0a716c2b"
USDC_CONTRACT = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
RPC_URL = "https://mainnet.base.org"
TUNNEL_URL = (PROJECT_DIR / ".tunnel_url").read_text().strip() if (PROJECT_DIR / ".tunnel_url").exists() else "未检测到"
SERVER_URL = "http://localhost:8000"
DASHBOARD_PORT = 8888
REFRESH_SECONDS = 15

# =============================================================================
# Style — dark terminal-inspired, clean, responsive
# =============================================================================

CSS = """
:root {
    --bg: #0d1117;
    --card: #161b22;
    --border: #30363d;
    --text: #c9d1d9;
    --dim: #8b949e;
    --accent: #58a6ff;
    --green: #3fb950;
    --red: #f85149;
    --yellow: #d2991d;
    --purple: #a371f7;
    --radius: 12px;
    --gap: 16px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.5;
    min-height: 100vh;
    padding: 20px;
}

.header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: var(--gap);
    margin-bottom: 24px;
}
.header h1 {
    font-size: clamp(20px, 4vw, 28px);
    font-weight: 700;
    background: linear-gradient(135deg, var(--accent), var(--purple));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.header .time { color: var(--dim); font-size: 13px; }
.header .refreshing { color: var(--dim); font-size: 12px; }

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: var(--gap);
}

.card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    position: relative;
}
.card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    font-weight: 600;
}
.card-header .icon {
    font-size: 18px;
    width: 32px; height: 32px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 8px;
}
.icon-green  { background: rgba(63,185,80,0.15); color: var(--green); }
.icon-blue   { background: rgba(88,166,255,0.15); color: var(--accent); }
.icon-purple { background: rgba(163,113,247,0.15); color: var(--purple); }
.icon-yellow { background: rgba(210,153,29,0.15); color: var(--yellow); }
.icon-red    { background: rgba(248,81,73,0.15); color: var(--red); }

.badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 3px 10px; border-radius: 20px;
    font-size: 12px; font-weight: 600;
}
.badge-on  { background: rgba(63,185,80,0.15); color: var(--green); }
.badge-off { background: rgba(248,81,73,0.15); color: var(--red); }

.stat-row {
    display: flex; justify-content: space-between;
    padding: 6px 0; border-bottom: 1px solid rgba(48,54,61,0.5);
    font-size: 13px;
}
.stat-row:last-child { border-bottom: none; }
.stat-label { color: var(--dim); }
.stat-value { font-weight: 500; font-family: 'Cascadia Code', 'Fira Code', monospace; }

.big-number {
    font-size: 36px; font-weight: 800; font-family: 'Cascadia Code', monospace;
    background: linear-gradient(135deg, var(--green), var(--accent));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 8px 0;
}
.big-number.zero {
    background: linear-gradient(135deg, var(--dim), var(--dim));
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
}

.log-line {
    font-family: 'Cascadia Code', 'Fira Code', monospace;
    font-size: 11px; padding: 3px 0;
    color: var(--dim); border-bottom: 1px solid rgba(48,54,61,0.3);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.log-line .time  { color: var(--yellow); }
.log-line .path  { color: var(--accent); }
.log-line .ip    { color: var(--purple); }
.log-line .paid  { color: var(--green); }

.flow-chart {
    display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
    font-size: 11px; padding: 10px 0;
}
.flow-node {
    background: var(--card); border: 1px solid var(--border);
    border-radius: 6px; padding: 4px 10px;
    font-family: monospace;
}
.flow-arrow { color: var(--dim); font-size: 14px; }

.url-box {
    background: #0d1117; border: 1px solid var(--border);
    border-radius: 6px; padding: 8px 12px;
    font-family: monospace; font-size: 12px; word-break: break-all;
    margin: 6px 0;
}

@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.5} }
.pulse { animation: pulse 2s infinite; }

@media (max-width: 600px) {
    .grid { grid-template-columns: 1fr; }
    .header { flex-direction: column; align-items: flex-start; }
}
"""

# =============================================================================
# Data fetchers
# =============================================================================


def rpc(method: str, params: list) -> dict:
    try:
        req = urllib.request.Request(
            RPC_URL,
            data=json.dumps({"jsonrpc": "2.0", "method": method, "params": params, "id": 1}).encode(),
            headers={"Content-Type": "application/json"},
        )
        return json.loads(urllib.request.urlopen(req, timeout=10).read())
    except Exception:
        return {}


def get_wallet():
    eth = rpc("eth_getBalance", [WALLET, "latest"])
    eth_val = int(eth.get("result", "0x0"), 16) / 1e18 if eth.get("result") else 0

    ud = "0x70a08231" + "0" * 24 + WALLET[2:].lower().zfill(64)
    usdc_r = rpc("eth_call", [{"to": USDC_CONTRACT, "data": ud}, "latest"])
    usdc_raw = int(usdc_r.get("result", "0x0"), 16) if usdc_r.get("result") else 0
    usdc_val = usdc_raw / 1e6

    return eth_val, usdc_val, usdc_raw


def get_health():
    try:
        r = urllib.request.urlopen(f"{SERVER_URL}/health", timeout=5)
        return r.status == 200
    except Exception:
        return False


def get_tunnel_health():
    if TUNNEL_URL and TUNNEL_URL != "未检测到":
        try:
            r = urllib.request.urlopen(f"{TUNNEL_URL}/health", timeout=5)
            return r.status == 200
        except Exception:
            return False
    return None  # unknown


def get_platform_status():
    results = {}
    for name, url in [
        ("GitHub", "https://github.com/dji112062126-cyber/x402-web-scraper-mcp"),
        ("Smithery", "https://smithery.ai/server/dji112062126/web-scraper-x402"),
    ]:
        try:
            req = urllib.request.Request(url, method="HEAD")
            req.add_header("User-Agent", "Mozilla/5.0")
            r = urllib.request.urlopen(req, timeout=8)
            results[name] = r.status in (200, 301, 302, 308)
        except Exception:
            results[name] = False
    return results


def get_logs(n=20):
    if not ACCESS_LOG.exists():
        return []
    lines = ACCESS_LOG.read_text(encoding="utf-8").strip().split("\n")
    return lines[-n:]


def get_system_info():
    import platform
    try:
        uptime = subprocess.check_output(
            "powershell -Command \"(get-date) - (gcim Win32_OperatingSystem).LastBootUpTime\"",
            shell=True, text=True
        ).strip()
    except Exception:
        uptime = "unknown"
    return {
        "python": sys.version.split()[0],
        "os": platform.platform(),
        "hostname": platform.node(),
        "uptime": uptime[:30] if uptime else "unknown",
    }


def get_git_status():
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%h %s (%cr)"],
                          cwd=PROJECT_DIR, capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else "unknown"
    except Exception:
        return "unknown"


# =============================================================================
# HTML builder
# =============================================================================


def build_card(header: str, icon_class: str, body: str, col_span: str = "1") -> str:
    style = f"grid-column: span {col_span};" if col_span != "1" else ""
    return f"""
    <div class="card" style="{style}">
        <div class="card-header"><span class="icon {icon_class}">{'🔍' if 'blue' in icon_class else '💰' if 'green' in icon_class else '📊' if 'purple' in icon_class else '⚡' if 'yellow' in icon_class else '❌'}
        </span> {header}</div>
        {body}
    </div>"""


def build_page() -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    eth, usdc, usdc_raw = get_wallet()
    local_ok = get_health()
    tunnel_ok = get_tunnel_health()
    platforms = get_platform_status()
    logs = get_logs(15)
    sys_info = get_system_info()
    last_commit = get_git_status()

    # ---- Service Status Card ----
    service_body = f"""
    <div style="margin-bottom:10px">
        <span class="badge {'badge-on' if local_ok else 'badge-off'}">{'● 在线' if local_ok else '○ 离线'}</span>
        <span style="margin-left:6px;font-size:12px;color:var(--dim)">本地 :8000</span>
    </div>
    <div style="margin-bottom:10px">
        <span class="badge {'badge-on' if tunnel_ok is True else 'badge-off'}">{'● 在线' if tunnel_ok is True else '○ 离线' if tunnel_ok is False else '○ 未知'}</span>
        <span style="margin-left:6px;font-size:12px;color:var(--dim)">外网隧道</span>
    </div>
    <div class="url-box" style="font-size:11px;max-height:40px;overflow:hidden;text-overflow:ellipsis">{TUNNEL_URL}</div>
    <div class="stat-row"><span class="stat-label">本地服务</span><span class="stat-value" style="color:{'var(--green)' if local_ok else 'var(--red)'}">{'在线' if local_ok else '离线'}</span></div>
    <div class="stat-row"><span class="stat-label">最后提交</span><span class="stat-value" style="font-size:11px;max-width:180px;overflow:hidden;text-overflow:ellipsis">{last_commit}</span></div>
    """

    # ---- Wallet Card ----
    if usdc > 0:
        wallet_body = f"""<div class="big-number">{usdc:.4f}</div><div style="color:var(--dim);font-size:12px;margin-bottom:10px">USDC 余额</div>"""
    else:
        wallet_body = f"""<div class="big-number zero">0.0000</div><div style="color:var(--dim);font-size:12px;margin-bottom:10px">USDC 余额 — 尚无入账</div>"""
    wallet_body += f"""
    <div class="stat-row"><span class="stat-label">ETH</span><span class="stat-value">{eth:.6f} ETH</span></div>
    <div class="stat-row"><span class="stat-label">USDC (raw)</span><span class="stat-value">{usdc_raw} 单位</span></div>
    <div class="stat-row"><span class="stat-label">收款地址</span><span class="stat-value" style="font-size:10px;max-width:180px;overflow:hidden;text-overflow:ellipsis">{WALLET[:12]}...</span></div>
    <div class="stat-row"><span class="stat-label">链</span><span class="stat-value">Base (ID 8453)</span></div>
    """

    # ---- Payment Flow Card ----
    flow_body = """
    <div class="flow-chart">
        <span class="flow-node">Agent 调用</span><span class="flow-arrow">→</span>
        <span class="flow-node">402 付款</span><span class="flow-arrow">→</span>
        <span class="flow-node">0.001 USDC</span><span class="flow-arrow">→</span>
        <span class="flow-node">链上验证</span><span class="flow-arrow">→</span>
        <span class="flow-node">返回结果</span>
    </div>
    <div class="stat-row"><span class="stat-label">单价</span><span class="stat-value">0.001 USDC</span></div>
    <div class="stat-row"><span class="stat-label">代币</span><span class="stat-value">USDC (Base)</span></div>
    <div class="stat-row"><span class="stat-label">合约</span><span class="stat-value" style="font-size:10px">{USDC_CONTRACT[:16]}...</span></div>
    """

    # ---- Platforms Card ----
    plat_body = ""
    for name, ok in platforms.items():
        plat_body += f"""<div class="stat-row"><span class="stat-label">{name}</span><span class="stat-value" style="color:{'var(--green)' if ok else 'var(--red)'}">{'● 可达' if ok else '○ 离线'}</span></div>"""
    plat_body += """
    <div style="margin-top:10px;display:flex;flex-wrap:wrap;gap:8px">
        <a href="https://github.com/dji112062126-cyber/x402-web-scraper-mcp" target="_blank" style="color:var(--accent);font-size:12px;text-decoration:none">GitHub →</a>
        <a href="https://smithery.ai/server/dji112062126/web-scraper-x402" target="_blank" style="color:var(--accent);font-size:12px;text-decoration:none">Smithery →</a>
    </div>
    """

    # ---- Access Log Card (spans 2 cols) ----
    log_body = ""
    for line in logs:
        log_body += f'<div class="log-line">{line.strip()}</div>'
    if not log_body:
        log_body = '<div style="color:var(--dim);font-size:12px;padding:10px">暂无访问记录</div>'

    # ---- System Card ----
    sys_body = ""
    for key, val in sys_info.items():
        sys_body += f"""<div class="stat-row"><span class="stat-label">{key}</span><span class="stat-value" style="font-size:11px">{val[:50]}</span></div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>X402 MCP — 个人工作站</title>
<style>{CSS}</style>
</head>
<body>
<div class="header">
    <div>
        <h1>X402 Web Scraper MCP 工作站</h1>
        <div style="color:var(--dim);font-size:12px;margin-top:4px">个人项目管理面板 · 实时监控 · 收款追踪</div>
    </div>
    <div>
        <div class="time">{now}</div>
        <div class="refreshing pulse">每 {REFRESH_SECONDS}s 自动刷新</div>
    </div>
</div>

<div class="grid">
    {build_card('服务状态', 'icon-blue', service_body)}
    {build_card('钱包余额', 'icon-green', wallet_body)}
    {build_card('收款流程', 'icon-purple', flow_body)}
    {build_card('平台链接', 'icon-yellow', plat_body)}
    {build_card('系统信息', 'icon-blue', sys_body)}
</div>

<div class="grid" style="margin-top:var(--gap)">
    {build_card('访问日志 · Access Log', 'icon-purple', log_body, '2')}
</div>

<div style="text-align:center;color:var(--dim);font-size:11px;padding:30px 0 10px">
    X402 Web Scraper MCP · <span style="color:var(--purple)">0.001 USDC / call</span> · Base Chain ·
    <a href="https://github.com/dji112062126-cyber/x402-web-scraper-mcp" style="color:var(--accent);text-decoration:none">GitHub</a> ·
    <a href="https://smithery.ai/server/dji112062126/web-scraper-x402" style="color:var(--accent);text-decoration:none">Smithery</a>
</div>

<script>
setTimeout(() => location.reload(), {REFRESH_SECONDS * 1000});
</script>
</body>
</html>"""

    return html


# =============================================================================
# HTTP Server
# =============================================================================


class DashboardHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # silence access logs

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = build_page().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/health":
            ok = get_health()
            data = json.dumps({"ok": ok, "time": datetime.now().isoformat()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)
            self.end_headers()


def main():
    print("=" * 55)
    print("  X402 Web Scraper MCP — 个人工作站")
    print("=" * 55)
    print(f"  仪表盘:    http://localhost:{DASHBOARD_PORT}")
    print(f"  刷新间隔:  {REFRESH_SECONDS}s")
    print(f"  钱包:      {WALLET}")
    print(f"  隧道:      {TUNNEL_URL}")
    print("=" * 55)
    print(f"  Press Ctrl+C to stop")
    print()

    server = HTTPServer(("0.0.0.0", DASHBOARD_PORT), DashboardHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()
