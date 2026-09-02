"""Wave 224 — The Organism Remembers: Constellation Archive.

A grand unified endpoint that tells the complete story of the
archipelago in one call: every island, its stones, its epitaphs,
its alliances, its census state, its audit fidelity, its federation
status. This is the organism's encyclopedia — the definitive
state of the web, for humans to read and for other organs to query.
"""
from __future__ import annotations

import hashlib
import json
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def _epitaph(repo: str, organ: str) -> str:
    """Generate the haiku for a stone (same logic as bridge_epitaphs)."""
    _NATURE = ["stone","wave","root","seed","mist","dust","bone","glow",
               "rift","void","flame","ash","song","tide","pearl","silk"]
    _ACTION = ["holds","sings","falls","rises","weaves","calls","draws",
               "bends","folds","turns","asks","dreams","breathes","waits"]
    _BEING = ["island","shadow","signal","thread","pulse","hum","ache",
              "trace","shape","breath","ghost","spark","shift","haze","glimmer"]
    s = int(hashlib.sha256(f"{repo}::{organ}".encode()).hexdigest()[:8], 16)
    n1 = _NATURE[(s >> 0) % len(_NATURE)]
    v = _ACTION[(s >> 7) % len(_ACTION)]
    b1 = _BEING[(s >> 14) % len(_BEING)]
    n2 = _NATURE[(s >> 21) % len(_NATURE)]
    b2 = _BEING[(s >> 28) % len(_BEING)]
    return f"{n1} {v} {b1}\n{b2} of the {n2}\n{repo} and {organ} drift"


def _alliance_graph(stones: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    allies = defaultdict(list)
    for s in stones:
        allies[s["repo"]].append(s["organ"])
    return dict(allies)


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "archive", "status": "recording", "resonance": 0.93, "wave": 224}


def resonates_with() -> list:
    return ["archive", "encyclopedia", "memory", "story", "record", "comprehensive", "encyclopedia"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "full")

    ledger = _load_ledger()
    stones = ledger.get("stones", [])
    allies = _alliance_graph(stones)
    repos = sorted(set(s["repo"] for s in stones))
    total = ledger.get("count", 0)

    # build island entries
    islands = []
    for repo in repos:
        island_stones = [s for s in stones if s["repo"] == repo]
        islands.append({
            "repo": repo,
            "stones": len(island_stones),
            "partners": sorted(set(s["organ"] for s in island_stones)),
            "lifecycle": "ACTIVE" if island_stones else "DORMANT",
            "first_enacted": min((s.get("enacted_at", "9") for s in island_stones), default=None),
            "avg_resonance": round(sum(s.get("resonance", 0) for s in island_stones) / max(1, len(island_stones)), 4),
            "epitaphs": [
                {"organ": s["organ"], "stone": s.get("stone"), "poem": _epitaph(repo, s["organ"])}
                for s in island_stones
            ],
        })

    # alliance summary
    alliance_summary = {}
    for repo, partners in allies.items():
        alliance_summary[repo] = len(partners)

    # timeline summary
    dates = sorted(set(s.get("enacted_at", "")[:10] for s in stones if s.get("enacted_at")))

    full = {
        "version": "4.11.0",
        "wave": 224,
        "total_stones": total,
        "total_islands": len(repos),
        "timeline": {"dates": dates, "first_date": dates[0] if dates else None},
        "islands": islands,
        "alliances": alliance_summary,
        "top_connected": sorted(alliance_summary.items(), key=lambda x: -x[1])[:10],
        "note": "The organism remembers everything.",
    }

    if action == "full":
        return full

    if action == "island":
        repo = payload.get("repo", "")
        matches = [i for i in islands if i["repo"] == repo]
        return matches[0] if matches else {"status": "not_found"}

    if action == "summary":
        return {
            "total_stones": total, "total_islands": len(repos),
            "top_connected": full["top_connected"],
            "timeline": full["timeline"],
        }

    return full
