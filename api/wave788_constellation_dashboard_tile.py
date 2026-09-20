"""Wave 788 — constellation_dashboard_tile.

Compact tile payload for local_control / dashboard: affinity snapshot.
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave788_constellation_dashboard_tile.json"
WAVE = 788
NAME = "constellation_dashboard_tile"

NEIGHBORS = [
    {"id": "ixpansion", "affinity": 1.0, "role": "hub"},
    {"id": "phaseshift", "affinity": 0.82, "role": "route"},
    {"id": "pentaxis", "affinity": 0.78, "role": "project"},
    {"id": "echotide", "affinity": 0.74, "role": "pace"},
    {"id": "luminant", "affinity": 0.71, "role": "crystal"},
    {"id": "chronocrypt", "affinity": 0.69, "role": "scar"},
    {"id": "oracle", "affinity": 0.65, "role": "dream"},
    {"id": "hitl", "affinity": 0.63, "role": "gate"},
]

DEFAULT = {"wave": WAVE, "name": NAME, "renders": 0, "status": "idle"}


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
        "module": "wave788_constellation_dashboard_tile",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "renders": int(st.get("renders") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("renders") or 0) * 0.01), 4),
        "surface": "silence",
        "neighbors": len(NEIGHBORS),
    }


def resonates_with() -> list:
    return [
        "wave775_constellation_affinity",
        "wave780_pentaxis_projection",
        "wave770_copilot_council_pulse",
        "wave785_silent_publish_orchestrator",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "tile":
        top = sorted(NEIGHBORS, key=lambda x: -x["affinity"])[: int(req.get("limit") or 6)]
        tile = {
            "title": "constellation",
            "hub": "ixpansion",
            "nodes": top,
            "ts": _now(),
            "style": "void-cyan",
        }
        st["renders"] = int(st.get("renders") or 0) + 1
        st["status"] = "tiled"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "tiled",
            "tile": tile,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("renders") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"constellation tiles {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "tile"}), indent=2))
