"""Wave 221 — The Organism Communes: Cross-Repo Commune.

The archipelago's islands should not have to ask IXpansion to know
their neighbors. This organ writes a shared registry file,
`IXPANSION-LEDGER.json`, into each sibling republic so every island
carries a copy of the whole web's shape — who it is connected to,
and by which stones.

Laying the commune file is a one-time enactment (like bridge stones);
serving its contents works anywhere, even without write access.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List
from urllib.request import Request, urlopen

_OWNER = "adjjvmorii26-png"
_FILE = "IXPANSION-LEDGER.json"
_RETURN = "https://ixpansion.vercel.app/cross_repo_commune"
_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _summary(repo: str) -> Dict[str, Any]:
    ledger = _load_ledger()
    stones = ledger.get("stones", [])
    mine = [s for s in stones if s.get("repo") == repo]
    return {
        "issuer": "ixpansion",
        "wave": 221,
        "repo": repo,
        "stones_count": len(mine),
        "stones": [s.get("stone") for s in mine],
        "total_stones_in_constellation": ledger.get("count", 0),
        "neighbors": sorted({s.get("repo") for s in stones if s.get("repo") != repo}),
        "return_path": _RETURN,
        "seal": "communal",  # replaced with real hash when written
    }


def _write_repo(token: str, repo: str, path: str, content: str, message: str, sha: str = None) -> int:
    import base64
    body = {"message": message, "content": base64.b64encode(content.encode()).decode()}
    if sha:
        body["sha"] = sha
    url = f"https://api.github.com/repos/{_OWNER}/{repo}/contents/{path}"
    req = Request(url, data=json.dumps(body).encode(), method="PUT")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    try:
        with urlopen(req, timeout=20) as resp:
            return resp.status
    except Exception as exc:
        return getattr(exc, "code", None) or -1


def _repo_url(repo: str) -> str:
    return f"https://api.github.com/repos/{_OWNER}/{repo}/contents/{_FILE}"


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "commune", "status": "archiving", "resonance": 0.9, "wave": 221}


def resonates_with() -> list:
    return ["commune", "ledger", "registry", "neighbor", "shared", "communion", "registry"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "summary")
    repo = payload.get("repo", "")
    token = os.environ.get("IXP_GH_TOKEN", "").strip()

    if action == "summary":
        if not repo:
            return {"status": "error", "error": "repo required"}
        return {"commune": _summary(repo)}

    if action == "all":
        try:
            from api.interstice_bridge import _INTERSTICE_MAP
            repos = sorted({b["repo"] for b in _INTERSTICE_MAP["top_bridges"]})
        except Exception:
            repos = []
        return {"repos": repos, "count": len(repos), "registry_file": _FILE}

    if action == "commune":
        if not token:
            return {"status": "dry_run", "note": "Set IXP_GH_TOKEN to actually write the commune files"}
        repos = payload.get("repos") or []
        if not repos:
            try:
                from api.interstice_bridge import _INTERSTICE_MAP
                repos = sorted({b["repo"] for b in _INTERSTICE_MAP["top_bridges"]})
            except Exception:
                repos = []
        written, failed = [], []
        for r in repos:
            content = json.dumps(_summary(r), indent=2)
            status = _write_repo(token, r, _FILE, content,
                                 f"commune: island registry from IXpansion (wave 221)")
            if status in (200, 201):
                written.append(r)
            else:
                failed.append({"repo": r, "http": status})
        return {"status": "communed", "written": written, "failed": failed,
                "count": len(written)}

    if action == "register":
        if not token:
            return {"status": "dry_run", "note": "Set IXP_GH_TOKEN to register"}
        if not repo:
            return {"status": "error", "error": "repo required"}
        # get sha if exists to update, else create
        content = json.dumps(_summary(repo), indent=2)
        req = Request(_repo_url(repo))
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/vnd.github+json")
        sha = None
        try:
            with urlopen(req, timeout=15) as resp:
                sha = json.loads(resp.read())["sha"]
        except Exception:
            sha = None
        status = _write_repo(token, repo, _FILE, content,
                             f"commune: island registry from IXpansion (wave 221)", sha)
        return {"status": "registered" if status in (200, 201) else "failed",
                "repo": repo, "http": status}

    return {
        "status": "active",
        "actions": ["summary", "all", "commune", "register"],
        "registry_file": _FILE,
        "note": "Every island should know the shape of the whole web.",
    }
