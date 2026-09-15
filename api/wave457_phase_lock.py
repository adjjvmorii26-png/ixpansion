"""Wave 457 Phase Lock — synchronizes organ tick phases into a shared beat.

Experimental: agents declare phase offsets; lock strength rises when phases
align within ε. Drives dawn_ledger-style circadian coherence without a clock.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave457_phase_lock.json"
DEFAULT = {
    "module": "wave457_phase_lock",
    "wave": 457,
    "phases": {},
    "lock": 0.0,
    "epsilon": 0.15,
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
    return {
        "wave": 457, "module": "wave457_phase_lock", "ok": True,
        "lock": st.get("lock", 0), "nodes": len(st.get("phases") or {}),
    }

def resonates_with():
    return ["wave455_swarm_heartbeat_mesh", "wave674_dawn_ledger", "wave690_momentum_braid"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    phases = st.setdefault("phases", {})
    if action == "set":
        node = str(req.get("node") or req.get("name") or "")[:48]
        phase = float(req.get("phase") or 0.0) % 1.0
        if not node:
            return {"status": "empty", **coherence_vitals()}
        phases[node] = phase
        vals = list(phases.values())
        if len(vals) < 2:
            st["lock"] = 1.0
        else:
            dists = []
            for i in range(len(vals)):
                for j in range(i + 1, len(vals)):
                    d = abs(vals[i] - vals[j])
                    d = min(d, 1.0 - d)
                    dists.append(d)
            mean_d = sum(dists) / len(dists)
            eps = float(st.get("epsilon") or 0.15)
            st["lock"] = round(min(1.0, max(0.0, 1.0 - mean_d / max(eps, 1e-6))), 4)
        _save(st)
        return {"status": "set", "node": node, "phase": phase, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
