"""Wave 950 Silence Surface — the product is what is not said.

Doctrine: silence is the product surface. Compression is memory.
Lab gates ≠ ALEPH CI. Additive, path-scoped.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave950_silence_surface.json"
DEFAULT = {
    "module": "wave950_silence_surface",
    "wave": 950,
    "council": "session_22_plus",
    "persona": "SILENCE",
    "surface": [],
    "compressions": 0,
    "gaps": 0,
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
        "wave": 950, "module": "wave950_silence_surface", "ok": True,
        "surface": len(st.get("surface") or []),
        "compressions": st.get("compressions", 0),
        "gaps": st.get("gaps", 0),
    }

def resonates_with():
    return ["wave671_harmony_braid", "wave672_root_archive", "wave675_consensus_bloom", "wave700_still_interval"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    surface = st.setdefault("surface", [])
    if action == "observe":
        note = str(req.get("note") or req.get("absence") or "")[:80]
        if not note:
            st["gaps"] = int(st.get("gaps") or 0) + 1
            _save(st)
            return {"status": "gap_recorded", **coherence_vitals()}
        sid = hashlib.sha256(note.encode()).hexdigest()[:10]
        surface.append({"id": sid, "note": note, "ts": datetime.now(timezone.utc).isoformat()})
        surface[:] = surface[-32:]
        _save(st)
        return {"status": "observed", "id": sid, **coherence_vitals()}
    if action == "compress":
        if len(surface) < 2:
            return {"status": "too_sparse", **coherence_vitals()}
        batch = surface[-4:]
        digest = hashlib.sha256("".join(s["id"] for s in batch).encode()).hexdigest()[:12]
        compressed = {"digest": digest, "members": [s["id"] for s in batch], "ts": datetime.now(timezone.utc).isoformat()}
        st["compressions"] = int(st.get("compressions") or 0) + 1
        surface[:] = [s for s in surface if s["id"] not in {m for m in compressed["members"]}]
        _save(st)
        return {"status": "compressed", "digest": digest, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
