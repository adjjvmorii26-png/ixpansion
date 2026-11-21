"""Wave 952 — silence_seed.

Seed a compressed silence residue from the hush margin border (950).
Does not replay session organs or expand payload. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave952_silence_seed.json"
WAVE = 952
NAME = "silence_seed"
SEED_WIDTH = 8

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "seeds": 0,
    "seed": "",
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


def _seed(margin: int, token: str = "") -> str:
    """Compress margin + optional prior token into an 8-char silent seed."""
    raw = f"{margin}:{token or 'hush'}"
    return hashlib.sha256(raw.encode()).hexdigest()[:SEED_WIDTH]


def coherence_vitals() -> dict:
    st = _load()
    seeds = int(st.get("seeds") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave952_silence_seed",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "seeds": seeds,
        "seed_width": SEED_WIDTH,
        "resonance": round(min(1.0, 0.62 + seeds * 0.008), 4),
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

    if action == "seed":
        margin = int(req.get("margin") or 1)
        token = str(req.get("token") or "")
        seed = _seed(margin, token)
        st["seed"] = seed
        st["seeds"] = int(st.get("seeds") or 0) + 1
        st["margin"] = margin
        st["status"] = "seeded"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "seeded",
            "seed": seed,
            "margin": margin,
            "caption": f"silence seed · {seed}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        seed = st.get("seed") or _seed(1)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"seeded hush · {seed}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "seed"}), indent=2))
