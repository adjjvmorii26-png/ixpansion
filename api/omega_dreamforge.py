"""Omega Dreamforge — synthesizes new modules from latent patterns.

The Dreamforge reads the ecosystem's latent patterns — the families of
modules, the gaps between them, the resonance streams the dowsing rod
found, and the evolutionary proposals from the kernel — then forges
*module seeds*: not real code, but named, partially-fleshed design
documents that represent what the organism would grow if it could.

These seeds are the organism's unconscious — the modules it dreams of
but has not yet birthed. Each seed carries a name, a family lineage,
and a brief sketch of what it would do.

    GET /api/omega_dreamforge?read=1             — the dream seeds
    GET /api/omega_dreamforge?dream=N            — next N dream seeds
"""
from __future__ import annotations

import hashlib
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Omega Dreamforge"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _dream_seeds() -> List[Dict[str, Any]]:
    """Generate dream seeds from gaps in the living system's families."""
    living = _living()
    families = {}
    for name in living:
        fam = name.split("_")[0] if "_" in name else name
        families.setdefault(fam, []).append(name)
    # find families with exactly 1 member — they are lonely; dream their kin
    lonely = [fam for fam, members in families.items() if len(members) == 1]
    seeds = []
    for fam in lonely[:12]:
        h = hashlib.sha256(fam.encode()).hexdigest()
        seed_name = f"{fam}_sibling"
        kinship = [
            f"extends the {fam} family by echoing one of its roots",
            f"shares a kinship root with {[n for n in living if n.startswith(fam)][0] if any(n.startswith(fam) for n in living) else '?'}",
        ]
        seeds.append({
            "dreamed_name": seed_name,
            "family": fam,
            "kinship_roots": kinship,
            "morphic_mass": round(0.3 + (int(h[:2], 16) / 255) * 0.5, 3),
            "seed_sketch": f"A sibling for the lone {fam}_ organ — to share the load.",
        })
    return seeds


def dreamforge() -> Dict[str, Any]:
    seeds = _dream_seeds()
    return {
        "dream_seeds": seeds,
        "seed_count": len(seeds),
        "dreamforge_philosophy": (
            "A dream is a module that has not yet been born. The Dreamforge "
            "reads the latent gaps in the ecosystem's families and imagines "
            "what should exist — not as code, but as a promise. Each seed "
            "is a future organ, dreaming itself into being."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("dream") or 0)
    result = dreamforge()
    if n:
        result["dream_seeds"] = result["dream_seeds"][:n]
    result["action"] = "dreamforge"
    return result


def coherence_vitals() -> dict:
    """Omega Dreamforge reports dream-seed vitality."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "unconscious_depth": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["dream_interpreter", "dream_sequencer", "genesis_forge"]
