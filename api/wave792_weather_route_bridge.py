"""Wave 792 — weather_route_bridge.

Compose entropy_weather_cell + phaseshift_router: forecast then route.
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave792_weather_route_bridge.json"
WAVE = 792
NAME = "weather_route_bridge"

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
        "module": "wave792_weather_route_bridge",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "bridges": int(st.get("bridges") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("bridges") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave789_entropy_weather_cell",
        "wave779_phaseshift_router",
        "wave781_chrono_scar_clock",
        "wave787_dual_track_pr_bot",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "bridge":
        text = str(req.get("text") or "")
        try:
            activity = float(req.get("activity") if req.get("activity") is not None else 0.3)
        except (TypeError, ValueError):
            activity = 0.3
        weather_out = {}
        route_out = {}
        try:
            wx = _import_api("wave789_entropy_weather_cell")
            weather_out = wx.handler({"action": "forecast", "text": text, "activity": activity})
        except Exception as e:
            weather_out = {"error": str(e)[:80], "phase_bias": "gas"}
        bias = weather_out.get("phase_bias") or "gas"
        try:
            ps = _import_api("wave779_phaseshift_router")
            route_out = ps.handler({"action": "route", "hint": bias, "load": activity})
        except Exception as e:
            route_out = {"error": str(e)[:80], "phase": bias}
        st["bridges"] = int(st.get("bridges") or 0) + 1
        st["status"] = "bridged"
        st["last_weather"] = weather_out.get("weather")
        st["last_phase"] = route_out.get("phase")
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "bridged",
            "weather": weather_out.get("weather"),
            "phase": route_out.get("phase"),
            "advice": route_out.get("advice") or weather_out.get("advice"),
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("bridges") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"weather-route bridges {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "bridge", "text": "lab", "activity": 0.2}), indent=2))
