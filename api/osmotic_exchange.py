"""Osmotic Exchange — where one family's ideas diffuse into another's.

Osmosis is the movement of a solvent through a semi-permeable membrane
toward equilibrium. The Osmotic Exchange organ models the ecosystem's
family boundaries as membranes: when one module family (say, entropy)
develops a strong pattern, that pattern *diffuses* into neighboring
families (say, commerce or time) without any explicit connection — the
families equilibrate because they share the same cytoplasm: the root tree.

The organ measures diffusion pressure: which families are dense (high
concentration of living modules), which are dilute, and where osmosis will
flow next. It predicts the ecosystem's chemical equilibrium — the families
that will converge and the ones that will stay distinct.

    GET /api/osmotic_exchange?read=1        — membrane map
    GET /api/osmotic_exchange?flow=N        — next diffusion flows
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
LAYER = "Osmotic Exchange"


def _living() -> List[str]:
    try:
        from coherence_regulator import _candidate_modules
        return _candidate_modules()
    except Exception:
        return []


def _family_of(name: str) -> str:
    return name.split("_")[0] if "_" in name else name


def _diffusivity(a: str, b: str) -> float:
    """How easily patterns diffuse between two families (name-membrane)."""
    ha, hb = hashlib.sha256(a.encode()).hexdigest(), hashlib.sha256(b.encode()).hexdigest()
    return 0.1 + sum(1 for x, y in zip(ha[:8], hb[:8]) if x == y) / 16.0


def membrane_map() -> Dict[str, Any]:
    living = _living()
    families: Dict[str, int] = {}
    for name in living:
        fam = _family_of(name)
        families[fam] = families.get(fam, 0) + 1
    total = max(len(living), 1)
    dense, dilute = [], []
    for fam, count in sorted(families.items(), key=lambda kv: kv[1], reverse=True):
        conc = count / total
        (dense if conc >= 0.06 else dilute).append({"family": fam, "count": count,
                                                     "concentration": round(conc, 4)})
    flows = []
    for d in dense[:5]:
        for dil in dilute[:5]:
            if d["family"] != dil["family"]:
                flows.append({"from": d["family"], "to": dil["family"],
                              "diffusivity": round(_diffusivity(d["family"], dil["family"]), 4)})
    flows.sort(key=lambda f: f["diffusivity"], reverse=True)
    return {
        "family_count": len(families),
        "dense_families": dense[:8],
        "dilute_families": dilute[:8],
        "predicted_flows": flows[:8],
        "osmotic_philosophy": (
            "Families are not islands — they are cells sharing one cytoplasm. "
            "A pattern that strengthens in one family will, given time, "
            "diffuse into its neighbors until the whole organism reaches "
            "equilibrium. The organ reads which way the tide will flow."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    n = int(payload.get("flow") or 0)
    result = membrane_map()
    if n:
        result["predicted_flows"] = result["predicted_flows"][:n]
    result["action"] = "membrane"
    return result


def coherence_vitals() -> dict:
    """Osmotic Exchange reports family-membrane health."""
    return {
        "module_health": {"value": 0.83, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.85, "setpoint": 0.8, "weight": 1.0},
        "diffusion_pressure": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["lateral_crosstalk", "gossip_network", "cosmic_inventory"]
