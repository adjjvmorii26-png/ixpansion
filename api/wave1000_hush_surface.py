"""Wave 1000 Hush Surface — silence is the product surface.

Council Session #22 + lab frontier · score 0.81
Compression is memory. Absence is the interface. Lab gates stay separate from ALEPH CI.
"""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave1000_hush_surface.json"
DEFAULT = {
    "module": "wave1000_hush_surface",
    "wave": 1000,
    "council": "session_22",
    "persona": "HUSH",
    "score": 0.81,
    "surfaces": [],
    "compressions": 0,
    "silence_depth": 0.0,
}

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
    return {
        "wave": 1000,
        "module": "wave1000_hush_surface",
        "ok": True,
        "persona": "HUSH",
        "surfaces": len(st.get("surfaces") or []),
        "compressions": st.get("compressions", 0),
        "silence_depth": st.get("silence_depth", 0.0),
    }

def resonates_with():
    return [
        "wave675_consensus_bloom",
        "wave672_root_archive",
        "wave674_dawn_ledger",
        "wave671_harmony_braid",
    ]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    surfaces = st.setdefault("surfaces", [])
    if action == "surface":
        note = str(req.get("note") or "unspoken")[:80]
        depth = float(req.get("depth") or 0.4)
        sid = f"hush-{len(surfaces)}"
        surfaces.append({
            "id": sid,
            "note": note,
            "depth": round(depth, 3),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        surfaces[:] = surfaces[-32:]
        st["silence_depth"] = round(float(st.get("silence_depth") or 0) + depth * 0.15, 4)
        _save(st)
        return {"status": "surfaced", "id": sid, "silence_depth": st["silence_depth"], **coherence_vitals()}
    if action == "compress":
        if not surfaces:
            return {"status": "empty_surface", **coherence_vitals()}
        removed = len(surfaces)
        surfaces.clear()
        st["compressions"] = int(st.get("compressions") or 0) + 1
        st["silence_depth"] = round(float(st.get("silence_depth") or 0) * 0.6, 4)
        _save(st)
        return {
            "status": "compressed",
            "removed": removed,
            "compressions": st["compressions"],
            "silence_depth": st["silence_depth"],
            **coherence_vitals(),
        }
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
