"""Wave 972 Hush Vector — orients by residual silence between organs.

Silence is the product surface. Compression is memory.
Records quiet directional residues; the product is the hush vector itself.
Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave972_hush_vector.json"
DEFAULT = {
    "module": "wave972_hush_vector",
    "wave": 972,
    "vectors": [],
    "quietest": None,
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
        "wave": 972, "module": "wave972_hush_vector", "ok": True,
        "vectors": len(st.get("vectors") or []),
        "quietest": st.get("quietest"),
    }

def resonates_with():
    return ["wave971_threshold_silence", "wave949_council_witness", "wave672_root_archive"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    vectors = st.setdefault("vectors", [])
    if action == "record":
        a = str(req.get("a") or req.get("from") or "")[:48]
        b = str(req.get("b") or req.get("to") or "")[:48]
        hush = min(1.0, max(0.0, float(req.get("hush") or req.get("silence") or 0.5)))
        if not a or not b:
            return {"status": "need_pair", **coherence_vitals()}
        vid = hashlib.sha256(f"{a}:{b}:{hush}".encode()).hexdigest()[:12]
        vec = {
            "id": vid, "a": a, "b": b, "hush": hush,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        vectors.append(vec)
        vectors[:] = vectors[-48:]
        # Quietest is the highest hush residue
        if not st.get("quietest") or hush > st["quietest"].get("hush", 0):
            st["quietest"] = vec
        _save(st)
        return {"status": "recorded", "id": vid, **coherence_vitals()}
    if action == "status":
        return {"status": "oriented", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
