"""Reusable GitHub data persistence — mirrors JSON files to the repo so they survive Vercel's ephemeral filesystem.

Every module that needs persistent storage should import from here.
"""
from __future__ import annotations
import json, os, time
from base64 import b64encode
from typing import Any, Dict, Optional

import urllib.request
from urllib.error import HTTPError

REPO = "adjjvmorii26-png/ixpansion"
BRANCH = "main"
API_BASE = f"https://api.github.com/repos/{REPO}/contents"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"

_sha_cache: Dict[str, str] = {}


def _token() -> str:
    return os.environ.get("IXP_GITHUB_TOKEN", "")


def gh_read(path: str) -> Optional[Dict[str, Any]]:
    """Read a JSON file from the GitHub repo."""
    url = f"{RAW_BASE}/{path}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ixpansion-mirror"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def gh_write(path: str, data: Dict[str, Any], message: str = "mirror update") -> bool:
    """Write a JSON file to the GitHub repo. Returns True on success."""
    token = _token()
    if not token:
        return False
    url = f"{API_BASE}/{path}"
    body = {
        "message": message,
        "content": b64encode(json.dumps(data, indent=2).encode()).decode(),
    }
    # Include SHA for update (required by GitHub API)
    sha = _sha_cache.get(path)
    if not sha:
        try:
            req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": "ixpansion-mirror"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                sha = json.loads(resp.read().decode()).get("sha")
                if sha:
                    _sha_cache[path] = sha
        except Exception:
            pass
    if sha:
        body["sha"] = sha
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode(),
            method="PUT",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read().decode())
            _sha_cache[path] = result.get("sha", sha or "")
            return True
    except Exception:
        return False


def gh_read_local_or_remote(local_path: str, remote_path: str, default: Any = None) -> Any:
    """Read from local file first, fall back to GitHub."""
    for p in (local_path, os.path.join("/tmp", os.path.basename(local_path))):
        try:
            with open(p) as f:
                return json.load(f)
        except Exception:
            pass
    return gh_read(remote_path) or default
