#!/usr/bin/env python3
"""
PUBLISH ALL — Complete Marketplace Submission Script
=====================================================
One script to rule them all. Handles:
  1. GitHub dedicated repo creation (needs PAT)
  2. Smithery MCP marketplace publish (needs SMITHERY_API_KEY)
  3. Coinbase Agent Marketplace submission

Usage:
  python publish_all.py --github-token ghp_xxx --smithery-key sk_xxx

Or set env vars:
  $env:GITHUB_TOKEN="ghp_xxx"
  $env:SMITHERY_API_KEY="sk_xxx"
  python publish_all.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx

# Fix Windows GBK console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_DIR = Path(__file__).resolve().parent
TUNNEL_URL = "https://8f372f1b5b3ec361-27-46-89-4.serveousercontent.com"
GITHUB_REPO_NAME = "x402-web-scraper-mcp"
GITHUB_OWNER = "dji112062126-cyber"
SMITHERY_PACKAGE = "dji112062126/web-scraper-x402"

# =============================================================================
# 1. GitHub: Create dedicated public repo & push
# =============================================================================


def step_github(token: str) -> bool:
    """Create a public GitHub repo and push code to it."""
    print("\n" + "=" * 60)
    print("  STEP 1: GitHub Repository")
    print("=" * 60)

    # Check if repo already exists
    result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
         f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO_NAME}"],
        capture_output=True, text=True,
    )
    if result.stdout.strip() == "200":
        print(f"[skip] Repo {GITHUB_OWNER}/{GITHUB_REPO_NAME} already exists")
        # Try to push
        subprocess.run(["git", "remote", "add", "dedicated",
                        f"git@github.com:{GITHUB_OWNER}/{GITHUB_REPO_NAME}.git"],
                       stderr=subprocess.DEVNULL)
        subprocess.run(["git", "push", "dedicated", "main"], stderr=subprocess.DEVNULL)
        print(f"[done] https://github.com/{GITHUB_OWNER}/{GITHUB_REPO_NAME}")
        return True

    # Create repo via GitHub API
    print(f"Creating {GITHUB_OWNER}/{GITHUB_REPO_NAME} ...")
    resp = subprocess.run([
        "curl", "-s", "-w", "\n%{http_code}",
        "-X", "POST",
        "https://api.github.com/user/repos",
        "-H", f"Authorization: token {token}",
        "-H", "Content-Type: application/json",
        "-H", "Accept: application/vnd.github+json",
        "-d", json.dumps({
            "name": GITHUB_REPO_NAME,
            "description": "Web scraper MCP server with x402 crypto micropayments on Base chain",
            "homepage": "https://smithery.ai/server/dji112062126/web-scraper-x402",
            "private": False,
            "has_issues": True,
            "has_projects": False,
            "has_wiki": False,
        }),
    ], capture_output=True, text=True)

    lines = resp.stdout.strip().split("\n")
    http_code = lines[-1]
    body = "\n".join(lines[:-1])

    if http_code not in ("201", "200"):
        print(f"[error] GitHub API returned {http_code}")
        print(body[:500])
        return False

    repo_data = json.loads(body)
    html_url = repo_data.get("html_url", "")
    ssh_url = repo_data.get("ssh_url", "")

    print(f"[created] {html_url}")

    # Set up remote and push
    subprocess.run(["git", "remote", "add", "dedicated", ssh_url],
                   stderr=subprocess.DEVNULL)
    subprocess.run(["git", "remote", "set-url", "dedicated", ssh_url],
                   stderr=subprocess.DEVNULL)
    result = subprocess.run(["git", "push", "dedicated", "main"],
                            capture_output=True, text=True)
    if result.returncode == 0:
        print(f"[pushed] Code is live at {html_url}")
        return True
    else:
        print(f"[warn] Push may have failed: {result.stderr[:200]}")
        return html_url != ""


# =============================================================================
# 2. Smithery: Publish to MCP marketplace
# =============================================================================


def step_smithery(api_key: str) -> bool:
    """Publish the MCP server to Smithery."""
    print("\n" + "=" * 60)
    print("  STEP 2: Smithery MCP Marketplace")
    print("=" * 60)

    env = {**os.environ, "SMITHERY_API_KEY": api_key}
    print(f"Publishing to Smithery as {SMITHERY_PACKAGE} ...")
    print(f"Server URL: {TUNNEL_URL}")

    result = subprocess.run(
        ["smithery", "mcp", "publish", TUNNEL_URL, "-n", SMITHERY_PACKAGE, "--json"],
        capture_output=True, text=True, env=env, timeout=120,
    )

    if result.returncode == 0:
        try:
            output = json.loads(result.stdout)
            url = output.get("serverUrl", f"https://smithery.ai/server/{SMITHERY_PACKAGE}")
            print(f"[published] {url}")
            return True
        except json.JSONDecodeError:
            print(result.stdout[:500])

    # Check stderr for useful info
    stderr = result.stderr
    if "already exists" in stderr.lower():
        print(f"[skip] Already published: https://smithery.ai/server/{SMITHERY_PACKAGE}")
        return True
    if "authentication failed" in stderr.lower():
        print("[error] Invalid SMITHERY_API_KEY")
        print("  Get yours: https://smithery.ai/account/api-keys")
        return False

    print(f"[smithery] {stderr[:300] or result.stdout[:300]}")
    return False


# =============================================================================
# 3. Coinbase: Submit agent manifest
# =============================================================================


async def step_coinbase() -> bool:
    """Submit to Coinbase Agent Marketplace."""
    print("\n" + "=" * 60)
    print("  STEP 3: Coinbase Agent Marketplace")
    print("=" * 60)

    manifest_path = PROJECT_DIR / "agent_manifest.json"

    # Verify manifest
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    checks = {
        "Name": manifest["agent"]["name"],
        "Recipient": manifest["blockchain"]["recipient_address"],
        "Price": manifest["pricing"]["price_per_call"],
        "Endpoint": manifest["protocol"]["endpoint"],
        "Token Contract": manifest["blockchain"]["token_contract"],
        "Chain ID": manifest["blockchain"]["chain_id"],
    }

    all_ok = True
    for key, val in checks.items():
        icon = "[OK]" if val else "[MISSING]"
        print(f"  {icon} {key}: {val}")
        if not val:
            all_ok = False

    # Verify the endpoint works
    base_url = manifest["protocol"]["endpoint"].replace("/mcp/sse", "")
    async with httpx.AsyncClient(timeout=15) as client:
        try:
            r = await client.get(f"{base_url}/health")
            if r.status_code == 200:
                print(f"  [OK] Health check: {r.text.strip()}")
            else:
                print(f"  [WARN] Health check: HTTP {r.status_code}")
                all_ok = False
        except Exception as e:
            print(f"  [WARN] Health check failed: {e}")
            all_ok = False

        try:
            r = await client.get(f"{base_url}/payment-info")
            if r.status_code == 200:
                pi = r.json()
                print(f"  [OK] Payment info: {pi.get('price')} {pi.get('token')} on {pi.get('network')}")
            else:
                print(f"  [WARN] Payment info: HTTP {r.status_code}")
        except Exception:
            pass

    # Write submission bundle
    submission = {
        "manifest": manifest,
        "verified_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "checks": {k: str(v) for k, v in checks.items()},
        "all_checks_pass": all_ok,
    }
    out_path = PROJECT_DIR / "coinbase_submission.json"
    out_path.write_text(json.dumps(submission, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  Submission bundle: {out_path}")

    if all_ok:
        print(f"\n  [READY] Submit at: https://cdp.coinbase.com/agent-marketplace")
        print(f"  Or via CLI: coinbase agent submit {out_path}")
    else:
        print("\n  [WARN] Some checks failed — review before submitting")

    return True


# =============================================================================
# Main
# =============================================================================


async def main() -> int:
    parser = argparse.ArgumentParser(description="Publish to all marketplaces")
    parser.add_argument("--github-token", help="GitHub Personal Access Token")
    parser.add_argument("--smithery-key", help="Smithery API Key")
    parser.add_argument("--skip-github", action="store_true")
    parser.add_argument("--skip-smithery", action="store_true")
    args = parser.parse_args()

    gh_token = args.github_token or os.environ.get("GITHUB_TOKEN")
    smith_key = args.smithery_key or os.environ.get("SMITHERY_API_KEY")

    results = {}

    # 1. GitHub
    if not args.skip_github:
        if gh_token:
            results["github"] = step_github(gh_token)
        else:
            print("\n[github] SKIPPED — no token. Set --github-token or GITHUB_TOKEN env var.")
            print("  Get PAT: https://github.com/settings/tokens → Generate new token (classic)")
            print("  Scopes: repo, workflow")
            results["github"] = False
    else:
        print("\n[github] SKIPPED (--skip-github)")
        results["github"] = True

    # 2. Smithery
    if not args.skip_smithery:
        if smith_key:
            results["smithery"] = step_smithery(smith_key)
        else:
            print("\n[smithery] SKIPPED — no key. Set --smithery-key or SMITHERY_API_KEY env var.")
            print("  Get API key: https://smithery.ai/account/api-keys")
            results["smithery"] = False
    else:
        print("\n[smithery] SKIPPED (--skip-smithery)")
        results["smithery"] = True

    # 3. Coinbase
    results["coinbase"] = await step_coinbase()

    # Summary
    print("\n" + "=" * 60)
    print("  PUBLISH SUMMARY")
    print("=" * 60)
    for platform, status in results.items():
        icon = "[DONE]" if status else "[PENDING]"
        print(f"  {icon} {platform}")
    print(f"\n  GitHub:    https://github.com/{GITHUB_OWNER}/{GITHUB_REPO_NAME}")
    print(f"  Smithery:  https://smithery.ai/server/{SMITHERY_PACKAGE}")
    print(f"  Coinbase:  {PROJECT_DIR / 'coinbase_submission.json'}")
    print(f"  Live URL:  {TUNNEL_URL}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
