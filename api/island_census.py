"""Wave 220 — The Organism Takes a Census: Island Census.

The first organ that senses the OUTSIDE: queries the GitHub API for
every constellation island and learns whether it is LIVELY, QUIET,
or DORMANT — how recently it was pushed, how large it is, how many
eyes watch it. The archipelago finally reads its own islands, not
just its own ledger.

Concurrent queries (ThreadPoolExecutor) keep the census fast; a short
in-memory cache prevents hammering the API on every request.
"""
from __future__ import annotations

import json
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List
from urllib.request import Request, urlopen

_OWNER = "adjjvmorii26-png"
_CACHE_TTL = 900  # 15 minutes
_cache: Dict[str, Any] = {"ts": 0, "data": None}


def _repo_url(repo: str) -> str:
    return f"https://api.github.com/repos/{_OWNER}/{repo}"


def _fetch(repo: str, token: str) -> Dict[str, Any]:
    try:
        req = Request(_repo_url(repo))
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        with urlopen(req, timeout=15) as resp:
            d = json.loads(resp.read().decode())
        return {
            "repo": repo,
            "pushed_at": d.get("pushed_at", ""),
            "created_at": d.get("created_at", ""),
            "size_kb": d.get("size", 0),
            "stars": d.get("stargazers_count", 0),
            "watchers": d.get("subscribers_count", 0),
            "open_issues": d.get("open_issues_count", 0),
            "forks": d.get("forks_count", 0),
            "default_branch": d.get("default_branch", "main"),
            "archived": d.get("archived", False),
        }
    except Exception as exc:
        return {"repo": repo, "error": str(getattr(exc, "code", None)) or type(exc).__name__}


def _classify(d: Dict[str, Any], now_ts: float) -> str:
    try:
        pushed = time.mktime(time.strptime(d.get("pushed_at", "")[:19], "%Y-%m-%dT%H:%M:%S"))
    except Exception:
        return "UNKNOWN"
    days = (now_ts - pushed) / 86400
    if days < 30:
        return "LIVELY"
    if days < 120:
        return "QUIET"
    return "DORMANT"


def _island_repos() -> List[str]:
    try:
        from api.interstice_bridge import _INTERSTICE_MAP
        return sorted({b["repo"] for b in _INTERSTICE_MAP["top_bridges"]})
    except Exception:
        return []


def _token() -> str:
    return os.environ.get("IXP_GH_TOKEN", "").strip()


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "census", "status": "sensing", "resonance": 0.92, "wave": 220}


def resonates_with() -> list:
    return ["census", "island", "lively", "dormant", "quiet", "github", "outside", "sensing"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "census")
    force = payload.get("force") == "1" or action == "refresh"
    token = _token()

    now = time.time()
    if not force and _cache["data"] and (now - _cache["ts"]) < _CACHE_TTL:
        data = _cache["data"]
        fresh = False
    else:
        repos = _island_repos()
        results: Dict[str, Any] = {}
        with ThreadPoolExecutor(max_workers=10) as pool:
            futs = {pool.submit(_fetch, r, token): r for r in repos}
            for fut in as_completed(futs):
                r = fut.result()
                results[r["repo"]] = r
        now_ts = time.time()
        for r in results.values():
            if "error" not in r:
                r["class"] = _classify(r, now_ts)
        data = {"repos": results, "as_of": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)), "token": bool(token)}
        _cache.update({"ts": now, "data": data})
        fresh = True

    if action in ("refresh", "census"):
        repos = data["repos"]
        tallies = {"LIVELY": 0, "QUIET": 0, "DORMANT": 0, "UNKNOWN": 0}
        for r in repos.values():
            tallies[r.get("class", "UNKNOWN")] = tallies.get(r.get("class", "UNKNOWN"), 0) + 1
        dormants = [r["repo"] for r in repos.values() if r.get("class") == "DORMANT"]
        return {
            "status": "census_taken" if fresh else "cached",
            "islands": len(repos),
            "classes": tallies,
            "dormant": dormants,
            "as_of": data["as_of"],
            "token": data["token"],
            "note": "The archipelago reads its own islands.",
        }

    if action == "island":
        repo = payload.get("repo", "")
        r = data["repos"].get(repo)
        if not r:
            return {"status": "not_found"}
        return {"island": r}

    if action == "dormant":
        return {"dormant": [r for r in data["repos"].values() if r.get("class") == "DORMANT"]}

    return {"status": "census", "repos": list(data["repos"].values())}
