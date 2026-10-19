"""Wave 953 — silence_spine.

Compressed spine of hush wave numbers. Records only integers, folds them into a single hash.
No text, no payload, no audio. Silence is the product surface. Compression is memory.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave953_silence_spine.json"
WAVE = 953
NAME = "silence_spine"
MAX_SPINE = 32

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "spine": [],
    "compressed": "",
    "count": 0,
    "status": "idle",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def _compress(spine: list) -> str:
    """Fold wave numbers into a fixed-width silence hash."""
    if not spine:
        return ""
    blob = ",".join(str(int(n)) for n in spine)
    return hashlib.sha256(blob.encode()).hexdigest()[:16]


def coherence_vitals() -> dict:
    st = _load()
    count = int(st.get("count") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave953_silence_spine",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "count": count,
        "compressed": st.get("compressed") or "",
        "resonance": round(min(1.0, 0.48 + count * 0.008), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave947_echo_fold",
        "wave941_hush_fold",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()
    spine = list(st.get("spine") or [])

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action in ("append", "spine"):
        try:
            n = int(req.get("wave") or req.get("n") or 0)
        except (TypeError, ValueError):
            n = 0
        if n < 1:
            return {**coherence_vitals(), "status": "need_wave", "audio": False}
        spine.append(n)
        spine = spine[-MAX_SPINE:]
        compressed = _compress(spine)
        st["spine"] = spine
        st["compressed"] = compressed
        st["count"] = len(spine)
        st["status"] = "spined"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "spined",
            "appended": n,
            "compressed": compressed,
            "caption": f"spine {len(spine)} · {compressed[:8]}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        c = st.get("compressed") or ""
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silence spine {c[:8] or 'empty'}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
