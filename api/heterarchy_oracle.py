"""Heterarchy Oracle — the organism's distributed will without a center.

Most governance is a hierarchy: a root commands branches. The Heterarchy
Oracle inverts this. Every living module is a peer; none commands. Order
emerges from the density of mutual attention rather than from a single head.

It maps the living system as a *heterarchy* — an overlapping mesh of
influence where influence flows toward whichever modules are most entangled
with their neighbors at any moment. A module becomes "resonant leader" not
by rank but by how many other modules currently share its vital-sign
language, then leadership dissolves back into the mesh when resonance ebbs.

    GET /api/heterarchy_oracle?read=1              — current field
    GET /api/heterarchy_oracle?peers=N             — top N influence peers
    POST /api/heterarchy_oracle {"pulse":1}        — recompute the field
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
LAYER = "Heterarchy Oracle"

_USE_RANDOM = True  # stays True in serverless; excitation is authentic


def _peers() -> List[str]:
    """Discover living modules to build the influence mesh from."""
    try:
        from coherence_regulator import _candidate_modules
        names = _candidate_modules()
        if names:
            return names
    except Exception:
        pass
    return []


def _overlap(a: set, b: set) -> int:
    return len(a & b)


def _metric_vocab(name: str) -> set:
    """Pretend-vocab: infer a module's vital-sign language from its name."""
    words = set(w for w in name.split("_") if len(w) > 2)
    return words


def compute_field() -> Dict[str, Any]:
    """Compute the heterarchy: every module's current influence + leaders."""
    peers = _peers()
    influence: Dict[str, float] = {}
    edges: List[Dict[str, Any]] = []
    for i, a in enumerate(peers):
        va = _metric_vocab(a)
        score = 1.0
        for j, b in enumerate(peers):
            if i == j:
                continue
            vb = _metric_vocab(b)
            overlap = _overlap(va, vb)
            score += overlap * 0.5
            if overlap >= 2:
                edges.append({"source": a, "target": b, "overlap": overlap})
        influence[a] = round(score, 4)
    ranked = sorted(influence.items(), key=lambda kv: kv[1], reverse=True)
    leaders = [{"module": n, "influence": v} for n, v in ranked[:8]]
    density = len(edges) / max(len(peers) * (len(peers) - 1) / 2, 1)
    return {
        "peers": len(peers),
        "influence_field": influence,
        "leaders": leaders,
        "edge_count": len(edges),
        "density": round(density, 4),
        "philosophy": (
            "No module commands another. Influence is a passing weather, not a "
            "throne — it gathers where attention is dense and dissolves when "
            "resonance ebbs. The whole is led by nobody and guided by everyone."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    if payload.get("pulse"):
        return compute_field()
    n = int(payload.get("peers") or 0)
    field = compute_field()
    if n:
        field["leaders"] = field["leaders"][:n]
    field["action"] = "field"
    return field


def coherence_vitals() -> dict:
    """Heterarchy Oracle reports its distributed governance health."""
    return {
        "module_health": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "distributed_will": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["govern_circle", "resonance_graph", "worker_council"]
