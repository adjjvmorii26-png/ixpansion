"""Wave 460 Pulse Engine Bridge — organ surface for organism_pulse_engine.

Exposes fast organism-wide processing as a standard wave handler so agents
can request a pulse without shelling out.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OPS = ROOT / "lab" / "ops"
if str(OPS) not in sys.path:
    sys.path.insert(0, str(OPS))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from organism_pulse_engine import pulse, pulse_range, build_index, bloom_has
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lab" / "ops"))
    from organism_pulse_engine import pulse, pulse_range, build_index, bloom_has  # type: ignore

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave460_pulse_engine_bridge.json"
DEFAULT = {"module": "wave460_pulse_engine_bridge", "wave": 460, "last": None}


def _load():
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
    last = st.get("last") or {}
    return {
        "wave": 460,
        "module": "wave460_pulse_engine_bridge",
        "ok": True,
        "last_ms": last.get("ms"),
        "last_fp": (last.get("fingerprint") or "")[:16] or None,
        "last_changed": last.get("changed"),
    }


def resonates_with():
    return [
        "wave455_swarm_heartbeat_mesh",
        "wave457_phase_lock",
        "wave690_momentum_braid",
        "wave693_jerk_sensor",
    ]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "pulse":
        force = bool(req.get("force"))
        lo = req.get("lo")
        hi = req.get("hi")
        if lo is not None and hi is not None:
            result = pulse_range(int(lo), int(hi), force=force)
        else:
            result = pulse(force=force)
        st["last"] = {
            "ms": result.get("ms"),
            "fingerprint": result.get("fingerprint"),
            "changed": result.get("changed"),
            "modules_pulsed": result.get("modules_pulsed"),
        }
        _save(st)
        return {"status": "pulsed", **result, **coherence_vitals()}
    if action == "index":
        idx = build_index()
        return {
            "status": "index",
            "count": idx["count"],
            "waves": idx.get("waves"),
            "bloom_popcount": sum(idx.get("bloom") or []),
            **coherence_vitals(),
        }
    if action == "has":
        w = int(req.get("wave") or 0)
        idx = build_index()
        return {
            "status": "has",
            "wave": w,
            "present": bloom_has(idx, w),
            **coherence_vitals(),
        }
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "pulse"}), indent=2))
