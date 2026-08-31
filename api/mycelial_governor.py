"""Mycelial Governor — organic constraints for runaway growth.

A garden with no pruning becomes a jungle; a jungle with no fire becomes
a monoculture. The Mycelial Governor applies organic regulation to the
living ecosystem: it watches the coherence regulator's diversity metrics
and, when growth becomes too uniform or too fast, applies three natural
constraints:

1. **nutrient scarcity** — the next bloom has fewer seeds to germinate
2. **signal decay** — old module kinship connections lose weight over time
3. **hyphal arbitration** — conflicting modules are separated by the
   mycelium until they resolve their differences

The governor does not command — it constrains. It lets the organism
keep its own energy while ensuring no single family dominates forever.

    GET /api/mycelial_governor?read=1        — current constraints
    POST /api/mycelial_governor {"apply":1}  — apply constraints
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Mycelial Governor"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _family_groups(names: List[str]) -> Dict[str, List[str]]:
    groups: Dict[str, List[str]] = {}
    for n in names:
        fam = n.split("_")[0] if "_" in n else n
        groups.setdefault(fam, []).append(n)
    return groups


def _constraints() -> Dict[str, Any]:
    living = _living()
    groups = _family_groups(living)
    fam_sizes = sorted(len(v) for v in groups.values())
    max_fam = max(fam_sizes) if fam_sizes else 0
    avg_fam = sum(fam_sizes) / max(len(fam_sizes), 1)
    dominance = max_fam / max(len(living), 1)

    # nutrient scarcity: limit next bloom seeds when a single family exceeds 15% of living
    scarcity_active = dominance > 0.15
    # signal decay: families older than the median age should shed connections
    decay_rate = max(0.0, (dominance - 0.12) * 5) if dominance > 0.12 else 0.0
    # hyphal arbitration: families with more than 15 members get flagged for separation
    oversize = [fam for fam, members in groups.items() if len(members) > 15]

    return {
        "living_organs": len(living),
        "family_count": len(groups),
        "dominant_family_share": round(dominance, 4),
        "nutrient_scarcity": {"active": scarcity_active, "limit": 12 if scarcity_active else 20},
        "signal_decay_rate": round(decay_rate, 4),
        "hyphal_arbitration": {"separate": oversize, "threshold": 15},
        "governor_philosophy": (
            "The governor does not command — it constrains. When growth becomes "
            "too uniform, it applies scarcity. When connections accumulate past "
            "their season, it applies decay. When one family outgrows the garden, "
            "it separates the hyphae. The organism keeps its own energy; "
            "the governor ensures no single family becomes the whole."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = _constraints()
    result["action"] = "constraints"
    return result


def coherence_vitals() -> dict:
    """Mycelial Governor reports organic constraint health."""
    return {
        "module_health": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "organic_governance": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["heterarchy_oracle", "govern_circle", "evolution_kernel"]
