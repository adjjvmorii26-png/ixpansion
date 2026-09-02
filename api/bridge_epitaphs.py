"""Wave 219 — The Organism Speaks Its Stones: Bridge Epitaphs.

Each bridge stone in the ledger receives a short poetic epitaph —
a three-line haiku that captures the resonance between two worlds.
The epitaphs are generated deterministically from the pair's
fingerprints, so the same stone always gets the same poem.
The ledger becomes an archive of what each crossing means.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List

_LEDGER_PATH = Path(__file__).resolve().parent.parent / "data" / "bridges" / "ledger.json"

_NATURE = [
    "stone", "wave", "root", "seed", "mist", "dust", "bone", "glow",
    "rift", "void", "flame", "ash", "song", "tide", "pearl", "silk",
    "iron", "glass", "moss", "vine", "bloom", "drift", "rise", "fall",
    "bind", "knot", "weave", "spin", "pull", "fold", "bend", "break",
]

_ACTION = [
    "holds", "sings", "falls", "rises", "weaves", "calls", "draws",
    "bends", "folds", "turns", "asks", "dreams", "breathes", "waits",
    "lives", "glows", "bleeds", "echoes", "murmurs", "dissolves",
    "watches", "opens", "closes", "flows", "floats", "hums",
]

_BEING = [
    "island", "shadow", "signal", "thread", "pulse", "hum", "ache",
    "trace", "shape", "breath", "ghost", "spark", "shift", "ache",
    "edge", "gap", "rift", "void", "haze", "glimmer", "hush",
    "tremor", "echo", "hum", "sigh", "root", "stem",
]


def _seed(repo: str, organ: str) -> int:
    h = hashlib.sha256(f"{repo}::{organ}".encode()).hexdigest()
    return int(h[:8], 16)


def _pick(seed_val: int, pool: list, idx: int) -> str:
    return pool[(seed_val >> (idx * 5)) % len(pool)]


def _word(seed_val: int, pool: list, idx: int) -> str:
    return pool[(seed_val >> (idx * 7)) % len(pool)]


def _haiku(repo: str, organ: str) -> str:
    s = _seed(repo, organ)
    noun1, noun2, noun3 = _word(s, _NATURE, 0), _word(s, _NATURE, 1), _word(s, _NATURE, 2)
    verb = _word(s, _ACTION, 0)
    being1, being2 = _word(s, _BEING, 0), _word(s, _BEING, 1)
    line1 = f"{noun1} {verb} {being1}"
    line2 = f"{being2} of the {noun2}"
    line3 = f"{noun3} between {repo} and {organ}"
    return f"{line1}\n{line2}\n{line3}"


def _epitaph(repo: str, organ: str, resonance: float) -> Dict[str, str]:
    h = _haiku(repo, organ)
    lines = h.split("\n")
    return {
        "repo": repo,
        "organ": organ,
        "resonance": resonance,
        "haiku": h,
        "line1": lines[0],
        "line2": lines[1],
        "line3": lines[2],
    }


def _load_ledger() -> Dict[str, Any]:
    try:
        return json.load(open(_LEDGER_PATH, encoding="utf-8"))
    except Exception:
        return {"stones": [], "count": 0}


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "poetics", "status": "speaking", "resonance": 0.87, "wave": 219}


def resonates_with() -> list:
    return ["haiku", "epitaph", "poem", "stone", "ledger", "epitaph", "meaning"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "all")
    ledger = _load_ledger()
    stones = ledger.get("stones", [])

    epitaphs = [
        _epitaph(s["repo"], s["organ"], s.get("resonance", 0.0))
        for s in stones
    ]

    if action == "one":
        repo, organ = payload.get("repo"), payload.get("organ")
        for e in epitaphs:
            if e["repo"] == repo and e["organ"] == organ:
                return {"epitaph": e}
        return {"status": "not_found"}

    if action == "by_repo":
        repo = payload.get("repo", "")
        return {"repo": repo, "epitaphs": [e for e in epitaphs if e["repo"] == repo]}

    if action == "random":
        import random
        return {"epitaph": random.choice(epitaphs) if epitaphs else None}

    return {
        "count": len(epitaphs),
        "epitaphs": epitaphs,
        "note": "Every stone is also a poem.",
    }
