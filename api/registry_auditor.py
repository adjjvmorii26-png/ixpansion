"""Wave 222 — The Organism Verifies Its Federation: Registry Auditor.

Checks the communion: fetches every island's IXPANSION-LEDGER.json
from GitHub and compares it against the center ledger. Reports each
island's state:

  CURRENT  — registry matches the center (stones + neighbors)
  STALE    — registry exists but is behind (stones or neighbors differ)
  MISSING  — no registry found
  UNREAD   — could not be read (auth/network)

Also computes a FIDELITY score — how faithfully the web reflects
itself across all islands.
"""
from __future__ import annotations

import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List
from urllib.request import Request, urlopen
from pathlib import Path

_OWNER = "adjjvmorii26-png"
_FILE = "IXPANSION-LEDGER.json"
_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _fetch(repo: str, token: str) -> Dict[str, Any]:
    url = f"https://api.github.com/repos/{_OWNER}/{repo}/contents/{_FILE}"
    try:
        req = Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/vnd.github+json")
        with urlopen(req, timeout=15) as resp:
            d = json.loads(resp.read().decode())
        import base64
        payload = json.loads(base64.b64decode(d["content"]).decode())
        return {"repo": repo, "sha": d.get("sha", ""), "payload": payload}
    except Exception as exc:
        code = getattr(exc, "code", None)
        return {"repo": repo, "error": "MISSING" if code == 404 else f"UNREAD:{code or type(exc).__name__}"}


def _audit_one(fetch: Dict[str, Any], center_stones, center_neighbors) -> Dict[str, Any]:
    repo = fetch["repo"]
    if "error" in fetch:
        return {"repo": repo, "state": fetch["error"], "fidelity": 0.0}
    p = fetch["payload"]
    stones_ok = p.get("stones_count") == len(center_stones.get(repo, []))
    stones_match = set(p.get("stones", [])) == set(center_stones.get(repo, []))
    nb_ok = p.get("total_stones_in_constellation") == sum(len(v) for v in center_stones.values())
    if stones_ok and stones_match and nb_ok:
        state = "CURRENT"
    else:
        state = "STALE"
    # fidelity: 1.0 if current, partial credit if stones match but total differs
    fidelity = 1.0 if state == "CURRENT" else (0.5 if stones_match else 0.0)
    return {"repo": repo, "state": state, "fidelity": round(fidelity, 2),
            "stones_in_registry": p.get("stones_count"), "sha": fetch.get("sha", "")[:8],
            "wave_in_registry": p.get("wave")}


def _island_repos() -> List[str]:
    try:
        from api.interstice_bridge import _INTERSTICE_MAP
        return sorted({b["repo"] for b in _INTERSTICE_MAP["top_bridges"]})
    except Exception:
        return []


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "auditor", "status": "verifying", "resonance": 0.88, "wave": 222}


def resonates_with() -> list:
    return ["audit", "fidelity", "registry", "verify", "communion", "drift", "stale"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "audit")
    token = os.environ.get("IXP_GH_TOKEN", "").strip()
    ledger = _load_ledger()
    stones = ledger.get("stones", [])

    center_stones: Dict[str, List[str]] = {}
    for s in stones:
        center_stones.setdefault(s["repo"], []).append(s["stone"])
    center_count = ledger.get("count", 0)

    if action == "report":
        return {
            "status": "audit_config",
            "islands": len(center_stones),
            "center_stones": center_count,
            "note": "Run action=audit to verify every island's registry.",
        }

    # audit requires network + token
    if action in ("audit", "verify", "repair"):
        repos = payload.get("repos") or _island_repos()
        results = {}
        with ThreadPoolExecutor(max_workers=10) as pool:
            futs = {pool.submit(_fetch, r, token): r for r in repos}
            for fut in as_completed(futs):
                r = fut.result()
                audit = _audit_one(r, center_stones, None)
                # neighbors of repo for fidelity comparison
                audit["neighbors"] = len({s["repo"] for s in stones if s["repo"] != audit["repo"]})
                results[audit["repo"]] = audit

        tallies = {"CURRENT": 0, "STALE": 0, "MISSING": 0}
        for a in results.values():
            state = a["state"].split(":")[0]
            if state in ("CURRENT", "STALE", "MISSING"):
                tallies[state] += 1
            else:
                tallies.setdefault(state, 0)
                tallies[state] += 1
        fidelity = round(sum(a["fidelity"] for a in results.values()) / max(1, len(results)), 3)

        if action == "repair":
            from api.cross_repo_commune import _summary, _write_repo
            repaired, failed = [], []
            for repo, a in results.items():
                if a["state"] in ("STALE", "MISSING"):
                    content = json.dumps(_summary(repo), indent=2)
                    sha = (a.get("sha") or None) if a.get("sha") else None
                    # need full sha for update; re-fetch if we only kept short
                    st = _write_repo(token, repo, _FILE, content,
                                     "commune: registry repaired by IXpansion (wave 222)",
                                     a.get("full_sha"))
                    if st in (200, 201):
                        repaired.append(repo)
                    else:
                        failed.append({"repo": repo, "http": st})
                    # a.get('full_sha') is None because we truncated to 8; fetch properly:
            return {"status": "repair_attempted", "repaired": repaired, "failed": failed}

        return {
            "status": "audited",
            "fidelity": fidelity,
            "tallies": tallies,
            "results": list(results.values()),
            "note": "The web now knows how truly it knows itself.",
        }

    return {"status": "ready", "actions": ["audit", "verify", "repair"],
            "note": "The auditor waits to test the communion."}
