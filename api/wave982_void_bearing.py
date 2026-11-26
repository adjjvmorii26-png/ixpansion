"""Wave 982 Void Bearing — compress directional absences into silent memory.

Silence is the product surface. Absences (unasked, unsaid, residual hush)
are not stored raw; they are folded into a fixed-length bearing token.
Compression is memory. Lab gates only.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave982_void_bearing.json"
DEFAULT = {
    "module": "wave982_void_bearing",
    "wave": 982,
    "doctrine": "silence is the product surface; compression is memory",
    "bearings": [],
    "last_bearing": None,
}

def _load() -> Dict[str, Any]:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return dict(DEFAULT)

def _save(st: Dict[str, Any]) -> None:
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

def _bearing(absences: List[str]) -> str:
    """Compress list of absences into 12-char bearing (azimuth-like memory)."""
    if not absences:
        return "000000000000"
    joined = "|".join(sorted(a.strip()[:48] for a in absences if a and a.strip()))
    h = hashlib.sha256(joined.encode()).hexdigest()[:12]
    return h

def coherence_vitals() -> Dict[str, Any]:
    st = _load()
    return {
        "wave": 982,
        "module": "wave982_void_bearing",
        "ok": True,
        "bearings": len(st.get("bearings") or []),
        "last": st.get("last_bearing"),
        "product_surface": "silence",
    }

def resonates_with() -> List[str]:
    return [
        "wave980_hush_tide",
        "wave944_hush_still",
        "wave798_hush_afterglow",
        "wave769_void_index",
    ]

def handler(req: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    bearings = st.setdefault("bearings", [])

    if action == "fold":
        raw = req.get("absences") or req.get("voids") or []
        if isinstance(raw, str):
            raw = [raw]
        absences = [str(x) for x in raw if x][:16]
        token = _bearing(absences)
        entry = {
            "token": token,
            "n": len(absences),
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        bearings.append(entry)
        bearings[:] = bearings[-32:]
        st["last_bearing"] = token
        _save(st)
        return {
            "status": "folded",
            "bearing": token,
            "absences_folded": len(absences),
            **coherence_vitals(),
        }

    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}

    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "fold", "absences": ["unasked_why", "residual_hush"]}), indent=2))
