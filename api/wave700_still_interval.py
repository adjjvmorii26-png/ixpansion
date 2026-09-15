"""Wave 700 Still Interval — the duration of silence is the product surface.

After hush compresses a pulse into a token, what remains between tokens
is the interval. This organ measures that still, compresses it into a
memory grain, and refuses to shout. Lab gate ≠ ALEPH CI.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave700_still_interval.json"
DEFAULT = {
    "module": "wave700_still_interval",
    "wave": 700,
    "marks": [],
    "last": None,
    "quiet_floor_s": 1.0,
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


def _now():
    return datetime.now(timezone.utc)


def _parse_ts(raw):
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z", "+00:00"))
    except Exception:
        return None


def _grain(seconds: float) -> str:
    digest = hashlib.sha256(f"{seconds:.6f}".encode()).hexdigest()[:8]
    band = "breath" if seconds < 3 else "still" if seconds < 30 else "void"
    return f"{band}:{seconds:.3f}#{digest}"


def coherence_vitals():
    st = _load()
    marks = st.get("marks") or []
    last = st.get("last") or {}
    return {
        "wave": 700,
        "module": "wave700_still_interval",
        "ok": True,
        "marks": len(marks),
        "has_last": bool(last),
        "last_interval_s": last.get("interval_s"),
        "quiet_floor_s": float(st.get("quiet_floor_s") or 1.0),
    }


def resonates_with():
    return [
        "wave681_hush_membrane",
        "wave698_void_syntax_engine",
        "wave675_consensus_bloom",
        "wave672_root_archive",
    ]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    marks = st.setdefault("marks", [])

    if action == "mark":
        now = _now()
        last = st.get("last") or {}
        prev = _parse_ts(last.get("ts"))
        interval = 0.0 if prev is None else max(0.0, (now - prev).total_seconds())
        if req.get("interval_s") is not None:
            interval = max(0.0, float(req["interval_s"]))
        grain = _grain(interval)
        floor = float(st.get("quiet_floor_s") or 1.0)
        rec = {
            "grain": grain,
            "interval_s": round(interval, 4),
            "silent": interval >= floor,
            "note": str(req.get("note") or "")[:80],
            "ts": now.isoformat(),
        }
        marks.append(rec)
        marks[:] = marks[-64:]
        st["last"] = rec
        _save(st)
        surface = "" if rec["silent"] else grain
        return {
            "status": "marked",
            "surface": surface,
            **rec,
            **coherence_vitals(),
        }

    if action == "hold":
        # Compress the last interval further — memory, not noise.
        last = st.get("last")
        if not last:
            return {"status": "empty", **coherence_vitals()}
        compressed = last["grain"].split("#")[0]
        return {
            "status": "held",
            "memory": compressed,
            "last": last,
            **coherence_vitals(),
        }

    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}

    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
