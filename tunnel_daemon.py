#!/usr/bin/env python3
"""
Tunnel Daemon — keeps the public URL alive. One-shot sync on every run.
Set as a Windows scheduled task to run on boot and hourly.
"""

import json, os, re, subprocess, sys, time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
URL_CACHE = PROJECT / ".tunnel_url"
SMITHERY_KEY = "99892dfc-957f-4365-a752-c6d8f68713cb"
SMITHERY_PKG = "dji112062126/web-scraper-x402"
PORT = 8000

def log(msg): print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def get_live_url():
    """Detect current tunnel URL from cached file or active SSH process."""
    if URL_CACHE.exists():
        return URL_CACHE.read_text().strip()
    return None

def update_configs(url):
    sse = f"{url.rstrip('/')}/mcp/sse"
    for path, key in [(PROJECT/"mcp_config.json","mcpServers"), (PROJECT/"agent_manifest.json","protocol")]:
        if not path.exists(): continue
        d = json.loads(path.read_text(encoding="utf-8"))
        if key == "mcpServers":
            for e in d.get("mcpServers",{}).values(): e["url"] = sse
        else:
            d["protocol"]["endpoint"] = sse
        path.write_text(json.dumps(d,indent=2,ensure_ascii=False),encoding="utf-8")
    log(f"Configs: {sse}")

def update_smithery(url):
    env = {**os.environ, "SMITHERY_API_KEY": SMITHERY_KEY}
    try:
        r = subprocess.run(f'smithery mcp publish {url} -n {SMITHERY_PKG} --json',
                          shell=True, capture_output=True, text=True, timeout=60, env=env)
        if r.returncode == 0:
            log(f"Smithery: https://smithery.ai/server/{SMITHERY_PKG}")
        else:
            log(f"Smithery: {r.stderr[:100] or r.stdout[:100]}")
    except Exception as e:
        log(f"Smithery err: {e}")

def verify_health(url):
    import urllib.request
    try:
        r = urllib.request.urlopen(f"{url}/health", timeout=10)
        return r.status == 200
    except: return False

if __name__ == "__main__":
    url = get_live_url()
    if not url:
        log("No tunnel URL cached. Run tunnel first: ssh -R 80:localhost:8000 serveo.net")
        sys.exit(1)

    log(f"Syncing URL: {url}")

    if verify_health(url):
        log("Health check: OK")
    else:
        log("Health check: FAIL — server or tunnel may be down")

    update_configs(url)
    update_smithery(url)
    log("Sync complete.")

    # Also push to GitHub
    import datetime
    try:
        subprocess.run(["git","-C",str(PROJECT),"add","mcp_config.json","agent_manifest.json","tunnel_daemon.py",".tunnel_url"],
                      capture_output=True)
        subprocess.run(["git","-C",str(PROJECT),"commit","-m",f"sync: tunnel URL {url} {datetime.datetime.now().isoformat()}"],
                      capture_output=True)
        subprocess.run(["git","-C",str(PROJECT),"push","origin","main"], capture_output=True)
        log("GitHub: pushed latest configs")
    except: pass
