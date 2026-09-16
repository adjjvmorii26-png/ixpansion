"""Wave 703 Proof Delta — only emit work when organism DNA fingerprint changes.

Pairs with organism_pulse_engine: stores last seen fingerprint; agents query
whether the mesh actually moved before expensive downstream DAGs run.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave703_proof_delta.json"
DEFAULT = {
    "module": "wave703_proof_delta",
    "wave": 703,
    "last_fp": None,
    "changes": 0,
    "skips": 0,
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
        "wave": 703, "module": "wave703_proof_delta", "ok": True,
        "changes": st.get("changes", 0), "skips": st.get("skips", 0),
        "last_fp": (st.get("last_fp") or "")[:16] or None,
    }

def resonates_with():
    return ["wave460_pulse_engine_bridge", "wave451_proof_tide_amplifier", "wave692_terminal_velocity"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "observe":
        fp = str(req.get("fingerprint") or req.get("fp") or "")
        if not fp:
            hex_path = DATA / "organism_fingerprint.hex"
            if hex_path.exists():
                fp = hex_path.read_text().strip()
        if not fp:
            return {"status": "no_fp", **coherence_vitals()}
        prev = st.get("last_fp")
        changed = prev is not None and prev != fp
        first = prev is None
        if changed or first:
            st["changes"] = int(st.get("changes") or 0) + (0 if first else 1)
            st["last_fp"] = fp
            st["last_ts"] = datetime.now(timezone.utc).isoformat()
            _save(st)
            return {"status": "delta", "changed": True, "first": first, **coherence_vitals()}
        st["skips"] = int(st.get("skips") or 0) + 1
        _save(st)
        return {"status": "unchanged", "changed": False, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
