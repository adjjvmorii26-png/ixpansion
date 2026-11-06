"""Wave 951 — silence_threshold.

Seal a compressed silence token when hush margin (950) crosses a quiet threshold.
Does not emit payload or audio. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave951_silence_threshold.json"
WAVE = 951
NAME = "silence_threshold"
DEFAULT_THRESHOLD = 1

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "seals": 0,
    "threshold": DEFAULT_THRESHOLD,
    "last_token": None,
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


def _seal(margin: int, threshold: int) -> str:
    """Compressed memory of a crossed silence threshold."""
    raw = f"silence:{margin}:{threshold}:{WAVE}".encode()
    return hashlib.sha256(raw).hexdigest()[:16]


def coherence_vitals() -> dict:
    st = _load()
    seals = int(st.get("seals") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave951_silence_threshold",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "seals": seals,
        "threshold": int(st.get("threshold") or DEFAULT_THRESHOLD),
        "resonance": round(min(1.0, 0.6 + seals * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave681_hush_membrane",
        "wave672_root_archive",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "threshold":
        margin = int(req.get("margin") or 0)
        threshold = int(req.get("threshold") or st.get("threshold") or DEFAULT_THRESHOLD)
        st["threshold"] = threshold
        crossed = margin >= threshold
        token = None
        if crossed:
            token = _seal(margin, threshold)
            st["seals"] = int(st.get("seals") or 0) + 1
            st["last_token"] = token
            st["status"] = "sealed"
        else:
            st["status"] = "below"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "sealed" if crossed else "below",
            "margin": margin,
            "threshold": threshold,
            "crossed": crossed,
            "token": token,
            "caption": f"silence sealed · {token[:8]}" if token else "silence below threshold",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        tok = st.get("last_token") or ""
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silence token {tok[:8]}" if tok else "no seal yet",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "threshold", "margin": 2}), indent=2))
