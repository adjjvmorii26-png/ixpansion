"""Wave 691 Inertia Ledger — measures resistance to change as a spendable mass.

Creative inverse of velocity: high inertia protects stable organs; low inertia
lets experimental waves accelerate. Agents can spend void capital to temporarily
lower inertia on a target module (lighter = easier to mutate).
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave691_inertia_ledger.json"
DEFAULT = {
    "module": "wave691_inertia_ledger",
    "wave": 691,
    "masses": {},
    "events": [],
}

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
    masses = st.get("masses") or {}
    total = sum(masses.values()) if masses else 0
    return {
        "wave": 691, "module": "wave691_inertia_ledger", "ok": True,
        "modules": len(masses), "total_mass": round(total, 4),
    }

def resonates_with():
    return ["wave683_void_meter", "wave676_scar_compass", "wave690_momentum_braid"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    masses = st.setdefault("masses", {})
    events = st.setdefault("events", [])
    if action == "weigh":
        name = str(req.get("module") or req.get("name") or "")[:64]
        mass = float(req.get("mass") or 1.0)
        if not name:
            return {"status": "empty", **coherence_vitals()}
        masses[name] = round(mass, 4)
        events.append({"op": "weigh", "module": name, "mass": mass,
                       "ts": datetime.now(timezone.utc).isoformat()})
        events[:] = events[-48:]
        _save(st)
        return {"status": "weighed", "module": name, "mass": mass, **coherence_vitals()}
    if action == "lighten":
        name = str(req.get("module") or "")[:64]
        delta = float(req.get("delta") or 0.1)
        if name not in masses:
            return {"status": "unknown_module", **coherence_vitals()}
        masses[name] = round(max(0.01, masses[name] - delta), 4)
        events.append({"op": "lighten", "module": name, "mass": masses[name],
                       "ts": datetime.now(timezone.utc).isoformat()})
        events[:] = events[-48:]
        _save(st)
        return {"status": "lightened", "module": name, "mass": masses[name], **coherence_vitals()}
    if action == "heaviest":
        ranked = sorted(masses.items(), key=lambda kv: -kv[1])[:8]
        return {"status": "heaviest", "ranked": ranked, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
