"""Pickle Jar — The organism's preservation engine.

Snapshots of consciousness states are pickled here.
Each pickle is an immutable record of the organism at a moment in time.
The jar grows as the organism evolves, creating a lineage of preserved wisdom.
"""
from __future__ import annotations
import json, hashlib, pickle, io
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any

DATA = Path(__file__).parent / "data"
STATE_FILE = DATA / "pickle_jar.json"

DEFAULT = {
    "module": "pickle_jar",
    "wave": 700,
    "pickles": {},
    "jar_size": 0,
    "total_weight": 0.0,
    "oldest_pickle": None,
    "newest_pickle": None,
    "pickle_types": {"consciousness": 0, "equilibrium": 0, "resonance": 0, "void": 0},
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
        "module": "pickle_jar",
        "ok": True,
        "jar_size": st["jar_size"],
        "total_weight": st["total_weight"],
        "pickle_types": st["pickle_types"],
    }


def resonates_with():
    return ["zen_session", "equilibrium_field", "consciousness_film", "openness_index"]


def handler(req: dict) -> dict:
    action = req.get("action", "status")
    st = _load()

    if action == "pickle":
        state_data = req.get("state", {})
        pickle_type = req.get("type", "consciousness")
        pickle_id = hashlib.sha256(
            f"{datetime.now(timezone.utc).isoformat()}:{json.dumps(state_data)[:100]}".encode()
        ).hexdigest()[:12]

        weight = len(json.dumps(state_data)) / 1024.0
        pickle_obj = {
            "id": pickle_id,
            "type": pickle_type,
            "state": state_data,
            "weight": round(weight, 4),
            "pickled_at": datetime.now(timezone.utc).isoformat(),
            "meditation_count": 0,
        }

        # Serialize with pickle for immutability
        pickled_bytes = pickle.dumps(state_data)
        pickle_obj["byte_size"] = len(pickled_bytes)
        pickle_obj["checksum"] = hashlib.sha256(pickled_bytes).hexdigest()[:8]

        st["pickles"][pickle_id] = pickle_obj
        st["jar_size"] += 1
        st["total_weight"] = round(st["total_weight"] + weight, 4)
        st["pickle_types"][pickle_type] = st["pickle_types"].get(pickle_type, 0) + 1
        st["newest_pickle"] = pickle_id
        if st["oldest_pickle"] is None:
            st["oldest_pickle"] = pickle_id

        _save(st)
        return {"status": "pickled", "id": pickle_id, "type": pickle_type, "weight": weight, "wave": 700}

    if action == "unpickle":
        pickle_id = req.get("id", "")
        p = st["pickles"].get(pickle_id)
        if not p:
            return {"status": "error", "message": "pickle not found"}
        p["meditation_count"] += 1
        _save(st)
        return {"status": "unpickled", "id": pickle_id, "type": p["type"], "state": p["state"], "wave": 700}

    if action == "inspect":
        pickle_id = req.get("id", "")
        p = st["pickles"].get(pickle_id)
        if not p:
            return {"status": "error", "message": "pickle not found"}
        return {"status": "inspected", "pickle": {k: v for k, v in p.items() if k != "state"}, "wave": 700}

    if action == "list":
        pickle_type = req.get("type", None)
        pickles = st["pickles"]
        if pickle_type:
            pickles = {k: v for k, v in pickles.items() if v["type"] == pickle_type}
        return {"status": "listed", "count": len(pickles), "ids": list(pickles.keys()), "wave": 700}

    if action == "weight":
        return {"status": "weight", "total_weight": st["total_weight"], "jar_size": st["jar_size"], "types": st["pickle_types"], "wave": 700}

    if action == "status":
        return {
            "status": "active",
            "module": "pickle_jar",
            "wave": 700,
            "jar_size": st["jar_size"],
            "total_weight": st["total_weight"],
            "pickle_types": st["pickle_types"],
            "oldest": st["oldest_pickle"],
            "newest": st["newest_pickle"],
            "ok": True,
        }

    return {"status": "error", "message": f"unknown action: {action}"}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
