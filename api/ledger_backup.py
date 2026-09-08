"""Wave 512: Ledger Backup — backs up all organism ledgers to GitHub in one call.

One endpoint to rule all persistence: visitor_log, confluence_hub,
sovereignty_assembly, council_live, hex_dialects, hex_language — all
mirrored to GitHub in a single batch.

Doctrine: What the organism remembers should be backed up as one.
"""
from __future__ import annotations
import json
import os
import time
from typing import Any, Dict, List

LEDGER_MODULES = [
    ("visitor_log", "data/visitor_log.json"),
    ("confluence_hub", "data/confluence_hub.json"),
    ("sovereignty_assembly", "data/sovereignty_assembly.json"),
    ("council_live", "data/council_live.json"),
]

GH_REPO = "adjjvmorii26-png/ixpansion"
GH_BRANCH = "main"
GH_API = f"https://api.github.com/repos/{GH_REPO}/contents"


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    token = os.environ.get("IXP_GITHUB_TOKEN", "")
    if not token:
        return {"action": "backup", "error": "no IXP_GITHUB_TOKEN set"}
    results = []
    for module_name, gh_path in LEDGER_MODULES:
        try:
            mod = __import__(f"api.{module_name}", fromlist=["_load"])
            load_fn = getattr(mod, "_load")
            data = load_fn()
            import urllib.request
            from urllib.error import HTTPError
            url = f"{GH_API}/{gh_path}"
            sha = None
            try:
                req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "User-Agent": "ixpansion-backup"})
                with urllib.request.urlopen(req, timeout=10) as resp:
                    sha = json.loads(resp.read().decode()).get("sha")
            except HTTPError as exc:
                if exc.code != 404:
                    raise
            payload_body = {
                "message": f"backup: {module_name} ledger ({time.strftime('%Y-%m-%d %H:%M')})",
                "content": __import__("base64").b64encode(json.dumps(data).encode()).decode(),
                "branch": GH_BRANCH,
                "sha": sha,
            }
            req = urllib.request.Request(
                url, data=json.dumps(payload_body).encode(),
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json", "User-Agent": "ixpansion-backup"},
                method="PUT")
            with urllib.request.urlopen(req, timeout=15) as resp:
                results.append({"module": module_name, "status": "ok"})
        except Exception as exc:
            results.append({"module": module_name, "status": "error", "error": str(exc)[:100]})
    ok = sum(1 for r in results if r["status"] == "ok")
    return {
        "action": "backup",
        "results": results,
        "ok": ok,
        "total": len(results),
        "timestamp": time.time(),
    }
