"""Wave 690 Momentum Braid — couples growth velocity across dual-track strands.

Like velocity, but braids lab-rail speed with ALEPH merge cadence into one
momentum vector. When strands diverge, torque rises; when aligned, momentum
compounds without extra gas.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave690_momentum_braid.json"
DEFAULT = {
    "module": "wave690_momentum_braid",
    "wave": 690,
    "lab_v": 0.0,
    "aleph_v": 0.0,
    "momentum": 0.0,
    "torque": 0.0,
    "samples": [],
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
        "wave": 690, "module": "wave690_momentum_braid", "ok": True,
        "momentum": st.get("momentum", 0), "torque": st.get("torque", 0),
        "lab_v": st.get("lab_v", 0), "aleph_v": st.get("aleph_v", 0),
    }

def resonates_with():
    return ["wave680_dual_track_sentinel", "wave671_harmony_braid", "wave674_dawn_ledger"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    samples = st.setdefault("samples", [])
    if action == "tick":
        lab = float(req.get("lab_v") or st.get("lab_v") or 0)
        aleph = float(req.get("aleph_v") or st.get("aleph_v") or 0)
        st["lab_v"] = lab
        st["aleph_v"] = aleph
        align = 1.0 - min(1.0, abs(lab - aleph) / max(lab + aleph, 0.01))
        momentum = (lab + aleph) * 0.5 * (0.5 + 0.5 * align)
        torque = abs(lab - aleph)
        st["momentum"] = round(momentum, 4)
        st["torque"] = round(torque, 4)
        samples.append({
            "lab_v": lab, "aleph_v": aleph, "momentum": st["momentum"],
            "torque": st["torque"], "ts": datetime.now(timezone.utc).isoformat(),
        })
        samples[:] = samples[-32:]
        _save(st)
        return {"status": "ticked", **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
