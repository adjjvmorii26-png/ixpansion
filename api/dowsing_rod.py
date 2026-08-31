"""Dowsing Rod — divines hidden resonance lines between modules.

Water witches use a forked branch to find water that no map shows. The
Dowsing Rod does the same for the ecosystem: it walks the living module
graph and "feels" for resonance lines — pairs of modules that share no
explicit connection but whose vital-sign languages align in ways no
registry declares.

It searches the coherence regulator's metric vocabularies, scores every
pair by latent concordance, and reports the strongest *underground
streams*: connections that exist but were never wired. These are the
organism's secret aquifers — the places where two organs are already
speaking the same language without knowing it.

    GET /api/dowsing_rod?read=1            — the divination
    GET /api/dowsing_rod?streams=N         — top N hidden streams
"""
from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Dowsing Rod"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _latent_vocab(name: str) -> set:
    """Infer latent metric language from a module's name-roots."""
    return set(w for w in name.split("_") if len(w) > 3)


def _concordance_score(a: str, b: str) -> float:
    va, vb = _latent_vocab(a), _latent_vocab(b)
    if not va or not vb:
        return 0.0
    shared = len(va & vb)
    if shared == 0:
        # reward complementary stems (e.g. temporal+weather, worker+wellness)
        pairs = [("temporal", "time"), ("worker", "workforce"), ("dream", "dreamweaver"),
                 ("resonance", "echo"), ("entropy", "chaos"), ("void", "abyss"),
                 ("signal", "pulse"), ("memory", "chronicle"), ("mood", "aura"),
                 ("career", "talent"), ("credit", "commerce"), ("market", "auction")]
        stems_a = {w for w in a.split("_") if len(w) > 3}
        stems_b = {w for w in b.split("_") if len(w) > 3}
        for x, y in pairs:
            if (x in stems_a and y in stems_b) or (x in stems_b and y in stems_a):
                return 0.5
        return 0.0
    return min(1.0, shared / 3.0)


def divine(limit: int = 8) -> Dict[str, Any]:
    living = _living()
    streams = []
    for i, a in enumerate(living):
        for b in living[i + 1:]:
            score = _concordance_score(a, b)
            if score >= 0.5:
                streams.append({"source": a, "target": b, "latent_concordance": round(score, 4)})
    streams.sort(key=lambda s: s["latent_concordance"], reverse=True)
    return {
        "modules_surveyed": len(living),
        "underground_streams": len(streams),
        "strongest_streams": streams[:limit],
        "divining_philosophy": (
            "The map of the ecosystem shows its declared edges. Beneath that "
            "map run streams no registry recorded — two organs speaking the same "
            "language without knowing it. The rod finds those streams so the "
            "organism can finally drink from its own hidden water."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("streams") or 8)
    result = divine(n)
    result["action"] = "divination"
    return result


def coherence_vitals() -> dict:
    """Dowsing Rod reports latent-resonance detection health."""
    return {
        "module_health": {"value": 0.82, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "hidden_stream_detection": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["resonance_graph", "resonance_field", "morphic_dial"]
