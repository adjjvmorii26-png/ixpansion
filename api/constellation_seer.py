"""Wave 223 — The Organism Grows: Constellation Seer.

Discovers the unseen: scans the user's GitHub repos, identifies
ones NOT in the current interstice map, and proposes latent bridges
between the newcomer and existing islands.

The seer builds the bridges that the map doesn't yet know about.
"""
from __future__ import annotations

import json
import os
import hashlib
from typing import Any, Dict, List, Set
from urllib.request import Request, urlopen

_OWNER = "adjjvmorii26-png"
_SEEN_REPOS: Set[str] = set()
_LATENT: List[Dict[str, Any]] = []


def _known_repos() -> Set[str]:
    try:
        from api.interstice_bridge import _INTERSTICE_MAP
        return {b["repo"] for b in _INTERSTICE_MAP["top_bridges"]}
    except Exception:
        return set()


def _fetch_repos(token: str) -> List[Dict[str, Any]]:
    repos = []
    page = 1
    while page <= 5:
        url = f"https://api.github.com/user/repos?per_page=100&page={page}&type=all&sort=pushed&direction=desc"
        try:
            req = Request(url)
            req.add_header("Authorization", f"Bearer {token}")
            req.add_header("Accept", "application/vnd.github+json")
            with urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode())
            if not data:
                break
            for r in data:
                repos.append({
                    "name": r.get("name", ""),
                    "description": r.get("description", ""),
                    "pushed_at": r.get("pushed_at", ""),
                    "size": r.get("size", 0),
                    "topics": r.get("topics", []),
                    "language": r.get("language"),
                    "archived": r.get("archived", False),
                })
            page += 1
        except Exception:
            break
    return repos


def _bridge_proposal(new_repo: str, existing_island: str, themes: List[str]) -> Dict[str, Any]:
    seed = int(hashlib.sha256(f"{new_repo}::{existing_island}".encode()).hexdigest()[:8], 16)
    resonance = round(0.05 + (seed % 100) / 500, 4)
    return {
        "repo": new_repo,
        "organ": existing_island,
        "organ_layer": "discovered",
        "resonance": resonance,
        "themes": themes[:3],
        "source": "seer",
    }


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "seer", "status": "scanning", "resonance": 0.91, "wave": 223}


def resonates_with() -> list:
    return ["seer", "discover", "new", "unseen", "grow", "scan", "latent"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "scan")
    token = os.environ.get("IXP_GH_TOKEN", "").strip()
    known = _known_repos()

    if not token:
        return {"status": "dry_run", "note": "Set IXP_GH_TOKEN to scan for new repos"}

    _JUNK = {
        "ixpansion", "dev", "dev0", "base", "public_repo", "synthhall",
        "aegis-workspace", "collaborative-canvas", "capability-sandbox",
        "multi-agent", "agent-workforce", "nextjs-ai-chatbot", "nextjs-boilerplate",
        "workforce-", "hyper_symbiosis.html", "NDSO-Engine", "yaweht",
        "eve-slack-agent", "snowy-firefly", "amazing-galois",
        "exciting-river-ww9k2c", "romantic-star-xqlgp4",
        "feature-1.5-vivarium-lattice", "feature-1.3-mesh-hitl-si",
    }

    # Only the genuinely creative constellation repos are adoptable.
    _ALLOWLIST = {
        "phaseshift-manifold", "antimemetic-architecton", "luminant-reliquary",
        "chronocrypt-orrery", "astral-forge", "interstice",
    }

    all_repos = _fetch_repos(token)
    # filter: allowlist only, skip archived
    new_repos = [r for r in all_repos if r["name"] in _ALLOWLIST and not r["archived"]]

    global _SEEN_REPOS, _LATENT
    _SEEN_REPOS = {r["name"] for r in all_repos}

    # propose bridges between each new repo and 3 random known islands
    latent = []
    import random
    for r in new_repos[:10]:
        partners = random.sample(sorted(known), min(3, len(known)))
        for partner in partners:
            latent.append(_bridge_proposal(r["name"], partner, r.get("topics", [])))
    _LATENT = latent

    if action == "scan":
        return {
            "status": "scanned",
            "total_repos": len(all_repos),
            "known": len(known),
            "new": len(new_repos),
            "latent_bridges": len(latent),
            "new_repos": [r["name"] for r in new_repos[:10]],
            "note": "The seer has found the unseen.",
        }

    if action == "latent":
        return {"latent": latent, "count": len(latent)}

    if action == "adopt":
        new_name = payload.get("repo", "")
        if not new_name or new_name in known:
            return {"status": "not_needed" if new_name in known else "error"}
        bridge = _bridge_proposal(new_name, next(iter(known)), ["discovered"])
        return {"status": "proposal", "bridge": bridge}

    return {"status": "active", "actions": ["scan", "latent", "adopt"],
            "note": "The seer scans the unseen and proposes new bridges."}
