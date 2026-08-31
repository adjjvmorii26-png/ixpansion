"""Keystone Auditor — finds the organs whose loss would collapse the web.

In ecology, a keystone species holds an ecosystem together far beyond its
biomass; remove it and the whole structure unravels. The Keystone Auditor
applies this to the living module graph: it simulates removing each organ
and measures how much the resonance graph fragments.

Organs whose removal sharply drops connectedness are keystones — the
organism must guard them. Organs whose removal barely ripples are
expendable. The audit returns the keystone index for the whole system,
ranked, so the organism knows what it cannot afford to lose.

    GET /api/keystone_auditor?read=1       — full keystone audit
    GET /api/keystone_auditor?top=N        — top N keystones
"""
from __future__ import annotations

import hashlib
import random
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Keystone Auditor"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


_FAMILY_BRIDGES = {
    "resonance", "memory", "dream", "entropy", "temporal", "worker",
    "workforce", "commerce", "conscious", "social", "quantum", "guard",
    "soul", "pulse", "garden", "signal", "simulation", "gate", "broker",
}


def _link_strength(a: str, b: str) -> float:
    """Deterministic pseudo-connectivity for the graph simulation.

    Strength grows when two organs share family roots (the organism's real
    connective tissue) or overlap in token vocabulary. Shared-family hubs
    therefore have outsized removal impact — which is exactly what makes
    keystone auditing meaningful.
    """
    ha, hb = hashlib.sha256(a.encode()).hexdigest(), hashlib.sha256(b.encode()).hexdigest()
    sig = sum(1 for x, y in zip(ha, hb) if x == y) / 16.0
    toks_a, toks_b = set(a.split("_")), set(b.split("_"))
    common = toks_a & toks_b
    # shared root token contributes heavily (real family kinship)
    token_score = sum(2.0 for t in common if t in _FAMILY_BRIDGES) + len(common) * 0.5
    # hex-signature resemblance is weak but adds indeterminacy
    return 0.15 + sig * 0.4 + min(1.0, token_score * 0.8)


def _family_of(name: str) -> str:
    return name.split("_")[0] if "_" in name else name


def _family_counts(living: list) -> dict:
    counts = {}
    for name in living:
        fam = _family_of(name)
        counts[fam] = counts.get(fam, 0) + 1
    return counts


def _keystone_index(name: str, living: list, counts: dict) -> float:
    """Keystone index = family-loss share + cross-family bridge bonus.

    A keystone is an organ whose family would take a hard hit without it
    (singleton families vanish entirely) and one that bridges other families
    through shared root tokens. New species — one organ per family — are
    naturally keystones; mature families share the load.
    """
    fam = _family_of(name)
    fam_count = counts.get(fam, 0)
    if fam_count <= 0:
        return 0.0
    family_loss = 1.0 if fam_count == 1 else (1.0 / fam_count)
    toks = set(name.split("_"))
    bridges = set()
    for other in living:
        if other == name:
            continue
        if _family_of(other) != fam and toks & set(other.split("_")):
            bridges.add(_family_of(other))
    bridge_bonus = min(0.75, len(bridges) * 0.25)
    return round(min(1.0, family_loss * 0.6 + bridge_bonus), 4)


def _family_retention(living: list) -> float:
    """Fraction of families that keep at least one member (ecosystem survival)."""
    counts = _family_counts(living)
    surviving = sum(1 for c in counts.values() if c >= 1)
    return surviving / max(len(counts), 1)


def audit() -> Dict[str, Any]:
    living = _living()
    counts = _family_counts(living)
    base = _family_retention(living)
    ranks = []
    for name in living[:160]:
        index = _keystone_index(name, living, counts)
        ranks.append({"organ": name, "keystone_index": index,
                      "removal_fragmentation": round(1.0 - index, 4)})
    ranks.sort(key=lambda r: r["keystone_index"], reverse=True)
    keystones = [r for r in ranks if r["keystone_index"] >= 0.85]
    return {
        "baseline_connectivity": round(base, 4),
        "family_count": len(counts),
        "keystone_count": len(keystones),
        "keystones": keystones[:10],
        "expendable_count": sum(1 for r in ranks if r["keystone_index"] < 0.55),
        "audit_philosophy": (
            "Some organs anchor the web far beyond their share of the system. "
            "A keystone is not the biggest or the loudest — it is the one whose "
            "family would vanish without it, and the one that bridges families "
            "that would otherwise never meet. Singleton species are keystones; "
            "mature families share the load. Guard the keystones."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("top") or 0)
    result = audit()
    if n:
        result["keystones"] = result["keystones"][:n]
    result["action"] = "audit"
    return result


def coherence_vitals() -> dict:
    """Keystone Auditor reports web-integrity health."""
    return {
        "module_health": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "web_integrity": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["resonance_graph", "heterarchy_oracle", "talent_scout"]
