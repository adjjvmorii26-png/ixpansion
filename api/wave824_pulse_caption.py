"""Wave 824 — pulse_caption.

Compresses a lab daily pulse into a silent caption token.
The product surface is the hush between status lines; the token is compressed memory.
Does not block on ALEPH full CI. Lab gates ≠ ALEPH CI.

Silence is the product surface.
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave824_pulse_caption.json"
WAVE = 824
NAME = "pulse_caption"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "pulses": 0,
    "captions": [],
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


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave824_pulse_caption",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "pulses": int(st.get("pulses") or 0),
        "captions": len(st.get("captions") or []),
        "resonance": round(min(1.0, 0.62 + int(st.get("pulses") or 0) * 0.03), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave823_pytest_collection_gate",
        "wave822_gate_priority",
        "wave821_still_interval",
        "wave799_hold_seam",
        "wave675_consensus_bloom",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()
    captions = st.setdefault("captions", [])

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "compress":
        # Accept pulse notes; compress into silent caption token
        notes = str(req.get("notes") or req.get("pulse") or "frontier quiet")[:240]
        frontier = req.get("frontier") or "824+"
        token = hashlib.sha256(f"{notes}|{frontier}|{_now()}".encode()).hexdigest()[:16]
        caption = f"@CoodingLooop frontier {frontier} hush:{token[:8]}"
        captions.append({
            "token": token,
            "caption": caption,
            "notes_len": len(notes),
            "ts": _now(),
        })
        captions[:] = captions[-32:]
        st["pulses"] = int(st.get("pulses") or 0) + 1
        st["status"] = "compressed"
        st["last_caption"] = caption
        _save(st)
        return {
            **coherence_vitals(),
            "status": "compressed",
            "token": token,
            "caption": caption,
            "audio": False,
            "surface": "silence",
            "payload": None,
        }

    if action == "caption":
        last = captions[-1]["caption"] if captions else "@CoodingLooop frontier hush"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": last,
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action, "audio": False, "surface": "silence"}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
