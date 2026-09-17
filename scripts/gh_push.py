"""Push the working tree to GitHub via the REST Git Database API.

Used when the git smart-HTTP transport is blocked. Reads GH_TOKEN env only.
Usage: GH_TOKEN=<token> python scripts/gh_push.py [--branch main] [--message "..."]
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import urllib.request

API = "https://api.github.com"
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}
SKIP_FILES = {".env"}


def api(token: str, method: str, path: str, payload: dict | None = None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        API + path, data=data, method=method,
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json",
                 "Content-Type": "application/json",
                 "User-Agent": "live-odds-bot-gh-push/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read().decode()
        return json.loads(body) if body else {}


def tracked_files() -> list[str]:
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True,
                         check=True, cwd=os.path.dirname(os.path.dirname(
                             os.path.abspath(__file__))))
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = []
    for line in out.stdout.splitlines():
        line = line.strip()
        if not line or os.path.basename(line) in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in line.split("/")):
            continue
        full = os.path.join(root, line)
        if os.path.isfile(full):
            files.append(line)
    return files


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch", default="main")
    ap.add_argument("--message", default="feat: live odds Telegram bot")
    ap.add_argument("--repo", required=True, help="owner/repo")
    args = ap.parse_args()
    token = os.environ.get("GH_TOKEN", "")
    if not token:
        sys.exit("GH_TOKEN is not set.")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    files = tracked_files()
    print(f"pushing {len(files)} files to {args.repo}@{args.branch}")
    blobs = []
    for i, rel in enumerate(files, 1):
        with open(os.path.join(root, rel), "rb") as fh:
            content = base64.b64encode(fh.read()).decode()
        b = api(token, "POST", f"/repos/{args.repo}/git/blobs",
                {"content": content, "encoding": "base64"})
        blobs.append({"path": rel, "mode": "100644", "type": "blob",
                      "sha": b["sha"]})
        if i % 20 == 0:
            print(f"  blobs {i}/{len(files)}")
    tree = api(token, "POST", f"/repos/{args.repo}/git/trees",
               {"tree": blobs})
    print("tree:", tree["sha"][:8])
    ref_path = f"/repos/{args.repo}/git/refs/heads/{args.branch}"
    try:
        existing = api(token, "GET", ref_path)
        parents = [existing["object"]["sha"]]
        print("parent:", parents[0][:8])
    except Exception:
        existing, parents = None, []
    commit = api(token, "POST", f"/repos/{args.repo}/git/commits",
                 {"message": args.message, "tree": tree["sha"],
                  "parents": parents})
    print("commit:", commit["sha"][:8])
    if existing:
        api(token, "PATCH", ref_path, {"sha": commit["sha"], "force": False})
        print(f"updated ref heads/{args.branch}")
    else:
        api(token, "POST", f"/repos/{args.repo}/git/refs",
            {"ref": f"refs/heads/{args.branch}", "sha": commit["sha"]})
        print(f"created ref heads/{args.branch}")
    print("DONE", commit["sha"])


if __name__ == "__main__":
    main()
