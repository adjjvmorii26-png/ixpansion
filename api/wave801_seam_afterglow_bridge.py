"""Wave 801 — seam_afterglow_bridge.

Bridge hold_seam ↔ hush_afterglow into one silent path.
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave801_seam_afterglow_bridge.json"
WAVE = 801
NAME = "seam_afterglow_bridge"

DEFAULT = {"wave": WAVE, "name": NAME, "bridges": 0, "status": "idle"}


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


def _import_api(mod: str):
    api = ROOT / "api"
    if str(api) not in sys.path:
        sys.path.insert(0, str(api))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    return __import__(mod)


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave801_seam_afterglow_bridge",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "bridges": int(st.get("bridges") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("bridges") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave799_hold_seam",
        "wave798_hush_afterglow",
        "wave795_residual_echo_filter",
        "wave772_afterimage_well",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "bridge":
        steps = {}
        for mod, act in (
            ("wave799_hold_seam", "status"),
            ("wave798_hush_afterglow", "status"),
        ):
            try:
                m = _import_api(mod)
                steps[mod] = m.handler({"action": act})
            except Exception as e:
                steps[mod] = {"error": str(e)[:80]}
        st["bridges"] = int(st.get("bridges") or 0) + 1
        st["status"] = "bridged"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "bridged",
            "seam": (steps.get("wave799_hold_seam") or {}).get("status"),
            "afterglow": (steps.get("wave798_hush_afterglow") or {}).get("status"),
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("bridges") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"seam-afterglow bridges {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "bridge"}), indent=2))
