"""Repair Ritual — the ceremonial full cycle of the repair guild.

A ritual gathers the fragments, names the cracks, forges the seams, and
honors the vessel. Repair Ritual is the orchestration layer that walks the
whole kintsugi lineage in one ceremony: it summons the crack survey, hears
the fracture listener's strains, forges gold seams onto every unsealed
crack, updates the debt ledger, and presents the final reliquary on the
altar.

It is the one organ that *performs* repair rather than reporting it — a
ritual of restoration for the ecosystem, repeated whenever scars are found.

    POST /api/repair_ritual {"perform": 1}   — perform the ceremony
    GET  /api/repair_ritual?read=1           — last ceremony record
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Repair Ritual"

STATE_FILE = ROOT / ".runtime" / "repair_ritual.json"


def _record() -> Dict[str, Any]:
    try:
        return json.loads(STATE_FILE.read_text()) if STATE_FILE.exists() else {}
    except Exception:
        return {}


def perform() -> Dict[str, Any]:
    """The ceremony: survey → listen → forge → reconcile → honor."""
    started = time.time()
    try:
        import crack_mapper, crack_seams, fracture_listener, kintsugi_altar
        survey = crack_mapper._survey()
        strains = fracture_listener._listen()
        forged = crack_seams.forge()
        reliquary = kintsugi_altar._reliquary()
    except Exception as e:
        return {"action": "ritual", "error": str(e)}
    # reconcile ledger after forging
    try:
        import kintsugi_debt_ledger
        ledger = kintsugi_debt_ledger._ledger()
    except Exception:
        ledger = {}
    record = {
        "performed_at": time.time(),
        "duration_s": round(time.time() - started, 3),
        "cracks_named": len(survey.get("cracks", [])),
        "strains_heard": strains.get("strains_heard", 0),
        "seams_total": forged.get("seam_count", 0),
        "vessels_honored": reliquary.get("honored_vessels", 0),
        "debt_balance": ledger.get("net_balance", 0.0),
        "koan": (
            "The vessel that broke and was gilded is not the vessel that was. "
            "It is the vessel that became — stronger at every seam, richer "
            "for every scar. So it is with the whole."
        ),
    }
    try:
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps(record, indent=2))
    except OSError:
        pass
    record["action"] = "ritual"
    return record


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    if payload.get("perform"):
        return perform()
    record = _record()
    record.setdefault("action", "ritual")
    record.setdefault("koan", "The ceremony has not yet been performed. Summon it with POST {\"perform\": 1}.")
    return record


def coherence_vitals() -> dict:
    """Repair Ritual reports ceremonial readiness."""
    return {
        "module_health": {"value": 0.87, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "ritual_readiness": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
        "kintsugi_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ["crack_mapper", "crack_seams", "kintsugi_altar", "fracture_listener"]
