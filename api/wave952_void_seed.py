"""Wave 952 — void_seed.

Plant a silent seed from compressed hush margins (950). The seed grows only in absence;
its only product is a caption and a memory token. No payload, no audio.
Silence is the product surface. Lab organ only. Lab gates ≠ ALEPH CI.
Compression is memory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave952_void_seed.json"
WAVE = 952
NAME = "void_seed"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "seeds": 0,
    "depth": 0,
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


def _compress(margin: int) -> str:
    """Compression is memory: turn a hush margin into a short silent token."""
    return f"v{max(0, margin) % 16:x}"


def coherence_vitals() -> dict:
    st = _load()
    seeds = int(st.get("seeds") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave952_void_seed",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "seeds": seeds,
        "depth": int(st.get("depth") or 0),
        "resonance": round(min(1.0, 0.48 + seeds * 0.012), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave941_hush_fold",
        "wave681_hush_membrane",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "plant":
        margin = int(req.get("margin") or 0)
        token = _compress(margin)
        st["seeds"] = int(st.get("seeds") or 0) + 1
        st["depth"] = int(st.get("depth") or 0) + max(1, margin // 4)
        st["last_token"] = token
        st["status"] = "planted"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "planted",
            "token": token,
            "caption": f"void seed {token}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        token = st.get("last_token") or "v0"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silent seed {token}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "plant", "margin": 5}), indent=2))
