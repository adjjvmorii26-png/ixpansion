"""Wave 951 — silence_fold.

Fold recent hush margins into a single compressed silence memory.
Does not emit payload. Silence is the product surface.
Compression is memory. Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave951_silence_fold.json"
WAVE = 951
NAME = "silence_fold"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "folds": 0,
    "density": 0.0,
    "memory": "",
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


def _compress(margins: list) -> tuple[str, float]:
    """Compress margin integers into a short density token."""
    if not margins:
        return "0", 0.0
    avg = sum(margins) / len(margins)
    density = round(min(1.0, avg / 12.0), 4)
    token = f"s{int(density * 1000):03d}"
    return token, density


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave951_silence_fold",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "folds": int(st.get("folds") or 0),
        "density": float(st.get("density") or 0.0),
        "resonance": round(min(1.0, 0.5 + float(st.get("density") or 0) * 0.4), 4),
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

    if action == "fold":
        raw = req.get("margins") or []
        margins = [int(m) for m in raw if isinstance(m, (int, float))][:16]
        if not margins:
            margins = [0]
        token, density = _compress(margins)
        st["folds"] = int(st.get("folds") or 0) + 1
        st["density"] = density
        st["memory"] = token
        st["status"] = "folded"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "folded",
            "memory": token,
            "density": density,
            "caption": f"silence folded · {token}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        mem = str(st.get("memory") or "")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"compressed silence {mem}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "fold", "margins": [4, 8, 2]}), indent=2))
