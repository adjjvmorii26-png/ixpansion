"""Wave 974 Gap Compress — fold silent intervals between events into compressed markers.

Frontier organ after residue_compress (973).
Takes pairs of timestamps or sequence markers, computes the residual gap (silence),
and folds the interval length + context into a short silent token. Does not replay content.
Silence is the product surface. Compression is memory. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave974_gap_compress.json"
DEFAULT = {
    "module": "wave974_gap_compress",
    "wave": 974,
    "markers": [],
    "compressions": 0,
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
        "wave": 974, "module": "wave974_gap_compress", "ok": True,
        "markers": len(st.get("markers") or []), "compressions": st.get("compressions", 0),
    }

def resonates_with():
    return ["wave973_residue_compress", "wave972_hush_vector", "wave971_threshold_silence"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    markers = st.setdefault("markers", [])
    if action == "compress":
        # Accept either explicit gap length or two markers to compute interval
        gap = req.get("gap")
        a = req.get("a") or req.get("before")
        b = req.get("b") or req.get("after")
        if gap is None and a is not None and b is not None:
            try:
                # Simple numeric or string-length proxy for interval
                ga = float(a) if str(a).replace(".", "", 1).isdigit() else len(str(a))
                gb = float(b) if str(b).replace(".", "", 1).isdigit() else len(str(b))
                gap = abs(gb - ga)
            except Exception:
                gap = 0
        try:
            gap = float(gap or 0)
        except Exception:
            gap = 0.0
        if gap <= 0:
            return {"status": "no_gap", "token": "", **coherence_vitals()}
        # Fold silence: hash of gap + context into short token
        ctx = str(req.get("context") or "")[:64]
        raw = f"{gap:.4f}:{ctx}"
        h = hashlib.sha256(raw.encode()).hexdigest()
        token = (h[:8] + str(int(gap))[-4:]).lower()[:12]
        markers.append({
            "token": token, "gap": round(gap, 4),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        markers[:] = markers[-32:]
        st["compressions"] = st.get("compressions", 0) + 1
        _save(st)
        return {"status": "compressed", "token": token, "gap": round(gap, 4), **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
