"""Wave 673 Heuristic Garden — cultivates Sentient Heuristic weights as plants.

Each heuristic is a plant; outcomes water or drought it; top plants form the
organism's adaptive policy canopy.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave673_heuristic_garden.json"
DEFAULT = {"module": "wave673_heuristic_garden", "wave": 673, "plants": {}, "seasons": 0}

def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except Exception: pass
    return dict(DEFAULT)

def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try: STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError: pass

def coherence_vitals():
    st = _load()
    return {"wave": 673, "module": "wave673_heuristic_garden", "ok": True,
            "plants": len(st.get("plants") or {}), "seasons": st.get("seasons", 0)}

def resonates_with():
    return ["wave670_sentient_heuristic", "wave641_fractal_garden", "wave650_auto_optimizer"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    plants = st.setdefault("plants", {})
    if action == "plant":
        name = str(req.get("name") or f"h_{len(plants)}")[:48]
        plants[name] = {"weight": float(req.get("weight") or 0.5), "yields": 0, "droughts": 0}
        _save(st)
        return {"status": "planted", "name": name, **coherence_vitals()}
    if action == "water":
        name = str(req.get("name") or "")
        success = bool(req.get("success", True))
        if name not in plants:
            return {"status": "unknown_plant", **coherence_vitals()}
        p = plants[name]
        if success:
            p["weight"] = min(1.0, float(p["weight"]) + 0.05)
            p["yields"] = int(p.get("yields") or 0) + 1
        else:
            p["weight"] = max(0.05, float(p["weight"]) - 0.08)
            p["droughts"] = int(p.get("droughts") or 0) + 1
        st["seasons"] = int(st.get("seasons") or 0) + 1
        _save(st)
        return {"status": "watered", "name": name, "weight": p["weight"], **coherence_vitals()}
    if action == "canopy":
        ranked = sorted(plants.items(), key=lambda kv: -kv[1].get("weight", 0))[:8]
        return {"status": "canopy", "top": [{"name": n, **m} for n, m in ranked], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
