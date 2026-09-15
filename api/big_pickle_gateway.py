"""Big Pickle Gateway — Unified API for the entire Big Pickle Open Zen system.

Entry point that connects pickle_jar, zen_session, equilibrium_field,
consciousness_film, and openness_index into one coherent meditation engine.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any

# Import sub-modules
import sys
sys.path.insert(0, str(Path(__file__).parent))

DATA = Path(__file__).parent / "data"
STATE_FILE = DATA / "big_pickle_gateway.json"

DEFAULT = {
    "module": "big_pickle_gateway",
    "wave": 700,
    "total_sessions": 0,
    "total_pickles": 0,
    "total_meditations": 0,
    "total_insights": 0,
    "equilibrium_score": 0.5,
    "transparency_score": 0.5,
    "film_length": 0.0,
    "gateway_status": "active",
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
        "module": "big_pickle_gateway",
        "ok": True,
        "total_sessions": st["total_sessions"],
        "total_pickles": st["total_pickles"],
        "equilibrium_score": st["equilibrium_score"],
        "transparency_score": st["transparency_score"],
    }


def resonates_with():
    return ["pickle_jar", "zen_session", "equilibrium_field", "consciousness_film", "openness_index"]


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    st = _load()

    if action == "meditate":
        """Full meditation cycle: pickle → zen → equilibrium → measure openness."""
        state = req.get("state", {"default": True})
        depth = req.get("depth", 3)

        # Step 1: Pickle the state
        from pickle_jar import handler as pickle_handler
        pickle_result = pickle_handler({"action": "pickle", "state": state, "type": "consciousness"})

        # Step 2: Open zen session on the pickle
        from zen_session import handler as zen_handler
        zen_result = zen_handler({"action": "open", "pickle_id": pickle_result.get("id", ""), "depth": depth})

        # Step 3: Scan equilibrium
        from equilibrium_field import handler as eq_handler
        eq_result = eq_handler({"action": "scan", "modules": ["big_pickle_gateway", "zen_session", "pickle_jar"]})

        # Step 4: Measure openness
        from openness_index import handler as open_handler
        open_result = open_handler({"action": "measure", "modules": ["big_pickle_gateway", "zen_session"]})

        st["total_sessions"] += 1
        st["total_pickles"] += 1
        st["total_meditations"] += depth
        st["total_insights"] += len(zen_result.get("insights", []))
        st["equilibrium_score"] = eq_result.get("equilibrium_score", st["equilibrium_score"])
        st["transparency_score"] = open_result.get("transparency_score", st["transparency_score"])

        _save(st)
        return {
            "status": "meditated",
            "pickle": pickle_result,
            "zen": zen_result,
            "equilibrium": eq_result,
            "openness": open_result,
            "insights": zen_result.get("insights", []),
            "wave": 700,
        }

    if action == "full_report":
        from pickle_jar import handler as pj
        from zen_session import handler as zs
        from equilibrium_field import handler as ef
        from consciousness_film import handler as cf
        from openness_index import handler as oi

        return {
            "status": "report",
            "pickle_jar": pj({"action": "status"}),
            "zen_session": zs({"action": "status"}),
            "equilibrium": ef({"action": "status"}),
            "film": cf({"action": "status"}),
            "openness": oi({"action": "status"}),
            "gateway": {"sessions": st["total_sessions"], "pickles": st["total_pickles"], "meditations": st["total_meditations"], "insights": st["total_insights"]},
            "wave": 700,
        }

    if action == "status":
        return {
            "status": "active",
            "module": "big_pickle_gateway",
            "wave": 700,
            "total_sessions": st["total_sessions"],
            "total_pickles": st["total_pickles"],
            "total_meditations": st["total_meditations"],
            "total_insights": st["total_insights"],
            "equilibrium_score": st["equilibrium_score"],
            "transparency_score": st["transparency_score"],
            "ok": True,
        }

    return {"status": "error", "message": f"unknown action: {action}"}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
