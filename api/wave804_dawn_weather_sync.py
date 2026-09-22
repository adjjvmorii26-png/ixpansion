"""Wave 804 — dawn_weather_sync.

Sync circadian phase with entropy weather for a single daily bias vector.
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave804_dawn_weather_sync.json"
WAVE = 804
NAME = "dawn_weather_sync"

DEFAULT = {"wave": WAVE, "name": NAME, "syncs": 0, "status": "idle"}


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
        "module": "wave804_dawn_weather_sync",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "syncs": int(st.get("syncs") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("syncs") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave796_circadian_dawn_pulse",
        "wave789_entropy_weather_cell",
        "wave792_weather_route_bridge",
        "wave779_phaseshift_router",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "sync":
        phase = None
        weather = None
        try:
            dawn = _import_api("wave796_circadian_dawn_pulse")
            d = dawn.handler({"action": "pulse", "hour": req.get("hour")})
            phase = d.get("phase")
        except Exception as e:
            phase = "day"
            derr = str(e)[:60]
        else:
            derr = None
        try:
            wx = _import_api("wave789_entropy_weather_cell")
            w = wx.handler({
                "action": "forecast",
                "text": str(req.get("text") or phase or ""),
                "activity": float(req.get("activity") or 0.3),
            })
            weather = w.get("weather")
            bias = w.get("phase_bias")
        except Exception as e:
            weather = "fog"
            bias = "gas"
            werr = str(e)[:60]
        else:
            werr = None
        vector = f"{phase}+{weather}"
        st["syncs"] = int(st.get("syncs") or 0) + 1
        st["status"] = "synced"
        st["last_vector"] = vector
        st["last_ts"] = _now()
        _save(st)
        out = {
            **coherence_vitals(),
            "status": "synced",
            "phase": phase,
            "weather": weather,
            "phase_bias": bias,
            "vector": vector,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }
        if derr:
            out["dawn_error"] = derr
        if werr:
            out["weather_error"] = werr
        return out

    if action == "caption":
        n = int(st.get("syncs") or 0)
        v = st.get("last_vector") or "-"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"dawn-weather syncs {n} · {v}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "sync", "hour": 6}), indent=2))
