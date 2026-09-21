"""Wave 790 — still_interval.

The product is the gap: record the quiet interval between pulses as compressed memory.
Distinct from afterimage (content residue) and caption_pace (frame offsets).
Silence is the product surface. Lab gates ≠ ALEPH CI. No audio.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave790_still_interval.json"
WAVE = 790
NAME = "still_interval"
MAX_GAPS = 48

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "last_mark": None,
    "gaps": [],
    "status": "idle",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            raw = json.loads(STATE_FILE.read_text())
            if isinstance(raw, dict):
                return raw
        except Exception:
            pass
    return dict(DEFAULT)


def _save(st: dict) -> None:
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


def _digest(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def coherence_vitals() -> dict:
    st = _load()
    n = len(st.get("gaps") or [])
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave790_still_interval",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "gaps": n,
        "resonance": round(min(1.0, 0.50 + n * 0.01), 4),
        "surface": "silence",
        "audio": False,
        "doctrine": "compression is memory",
    }


def resonates_with() -> list:
    return [
        "wave772_afterimage_well",
        "wave786_echotide_caption_pace",
        "wave768_hush_compass",
        "wave674_dawn_ledger",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        last = (st.get("gaps") or [None])[-1]
        return {
            **coherence_vitals(),
            "last_mark": st.get("last_mark"),
            "last_gap": last,
            "surface": "silence",
            "audio": False,
        }

    if action == "mark":
        now = _now()
        note = str(req.get("note") or "pulse")[:160]
        prev = st.get("last_mark")
        seconds = 0.0
        if prev:
            try:
                then = datetime.fromisoformat(str(prev).replace("Z", "+00:00"))
                seconds = max(0.0, (now - then).total_seconds())
            except Exception:
                seconds = 0.0
        gap = {
            "hash": _digest(f"{prev}|{_iso(now)}|{note}"),
            "seconds": round(seconds, 3),
            "note": note,
            "from": prev,
            "to": _iso(now),
        }
        gaps = list(st.get("gaps") or [])
        gaps.append(gap)
        st["gaps"] = gaps[-MAX_GAPS:]
        st["last_mark"] = _iso(now)
        st["status"] = "marked"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "marked",
            "gap": gap,
            "audio": False,
            "surface": "silence",
        }

    if action == "still":
        gaps = list(st.get("gaps") or [])
        if not gaps:
            return {
                **coherence_vitals(),
                "status": "empty",
                "median_seconds": 0.0,
                "audio": False,
                "surface": "silence",
            }
        secs = sorted(float(g.get("seconds") or 0) for g in gaps)
        mid = secs[len(secs) // 2]
        return {
            **coherence_vitals(),
            "status": "still",
            "median_seconds": mid,
            "count": len(secs),
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
