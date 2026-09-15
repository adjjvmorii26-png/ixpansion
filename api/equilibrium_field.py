"""Equilibrium Field — Cross-module balance detection.

Scans all organism modules and detects imbalance.
The field visualizes where the organism is in equilibrium
and where it needs meditation to restore balance.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

DATA = Path(__file__).parent / "data"
STATE_FILE = DATA / "equilibrium_field.json"

DEFAULT = {
    "module": "equilibrium_field",
    "wave": 700,
    "scan_count": 0,
    "balanced_modules": [],
    "imbalanced_modules": [],
    "field_strength": 0.0,
    "equilibrium_score": 0.5,
    "last_scan": None,
}


def _load():
    DATA.mkdir(parents=True, exist_ok=True)
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try:
            STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError:
            pass


def coherence_vitals():
    st = _load()
    return {
        "wave": 700,
        "module": "equilibrium_field",
        "ok": True,
        "field_strength": st["field_strength"],
        "equilibrium_score": st["equilibrium_score"],
        "scan_count": st["scan_count"],
    }


def resonates_with():
    return ["pickle_jar", "zen_session", "openness_index", "consciousness_film"]


def _measure_balance(module_name: str) -> dict:
    """Measure balance of a single module using its name as entropy source."""
    h = hashlib.sha256(module_name.encode()).hexdigest()
    coherence = (int(h[:4], 16) % 100) / 100.0
    resonance = (int(h[4:8], 16) % 100) / 100.0
    entropy = (int(h[8:12], 16) % 100) / 100.0
    balance = (coherence + resonance + (1 - entropy)) / 3.0
    return {
        "module": module_name,
        "coherence": round(coherence, 4),
        "resonance": round(resonance, 4),
        "entropy": round(entropy, 4),
        "balance": round(balance, 4),
        "equilibrium": balance > 0.4,
    }


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    st = _load()

    if action == "scan":
        modules = req.get("modules", ["organism_core", "coherence_validator", "zen_session"])
        balanced = []
        imbalanced = []
        for m in modules:
            result = _measure_balance(m)
            if result["equilibrium"]:
                balanced.append(result)
            else:
                imbalanced.append(result)

        total_balance = sum(r["balance"] for r in balanced + imbalanced) / max(len(balanced + imbalanced), 1)

        st["balanced_modules"] = [r["module"] for r in balanced]
        st["imbalanced_modules"] = [r["module"] for r in imbalanced]
        st["field_strength"] = round(total_balance, 4)
        st["equilibrium_score"] = round(len(balanced) / max(len(balanced + imbalanced), 1), 4)
        st["scan_count"] += 1
        st["last_scan"] = datetime.now(timezone.utc).isoformat()

        _save(st)
        return {
            "status": "scanned",
            "balanced": len(balanced),
            "imbalanced": len(imbalanced),
            "field_strength": st["field_strength"],
            "equilibrium_score": st["equilibrium_score"],
            "details": balanced[:5] + imbalanced[:5],
            "wave": 700,
        }

    if action == "field":
        return {"status": "field", "strength": st["field_strength"], "equilibrium": st["equilibrium_score"], "balanced": st["balanced_modules"][:10], "imbalanced": st["imbalanced_modules"][:10], "wave": 700}

    if action == "status":
        return {
            "status": "active",
            "module": "equilibrium_field",
            "wave": 700,
            "scan_count": st["scan_count"],
            "field_strength": st["field_strength"],
            "equilibrium_score": st["equilibrium_score"],
            "last_scan": st["last_scan"],
            "ok": True,
        }

    return {"status": "error", "message": f"unknown action: {action}"}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
