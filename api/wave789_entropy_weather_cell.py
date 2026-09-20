"""Wave 789 — entropy_weather_cell.

Experimental: entropy proxy → organism weather (calm/fog/storm/aurora)
biasing phaseshift advice without controlling it.
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import math
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave789_entropy_weather_cell.json"
WAVE = 789
NAME = "entropy_weather_cell"
WEATHERS = ("calm", "fog", "storm", "aurora")

DEFAULT = {"wave": WAVE, "name": NAME, "forecasts": 0, "status": "idle"}


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


def _shannonish(text: str) -> float:
    if not text:
        return 0.0
    freq: dict[str, int] = {}
    for c in text:
        freq[c] = freq.get(c, 0) + 1
    n = len(text)
    h = 0.0
    for c in freq.values():
        p = c / n
        h -= p * math.log2(p)
    return min(1.0, h / 8.0)


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave789_entropy_weather_cell",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "forecasts": int(st.get("forecasts") or 0),
        "last_weather": st.get("last_weather"),
        "resonance": round(min(1.0, 0.5 + int(st.get("forecasts") or 0) * 0.01), 4),
        "surface": "silence",
        "weathers": list(WEATHERS),
    }


def resonates_with() -> list:
    return [
        "wave779_phaseshift_router",
        "wave781_chrono_scar_clock",
        "wave776_merge_readiness_score",
        "wave782_dream_share_bus",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "forecast":
        text = str(req.get("text") or req.get("sample") or "")
        try:
            activity = float(req.get("activity") if req.get("activity") is not None else 0.3)
        except (TypeError, ValueError):
            activity = 0.3
        activity = max(0.0, min(1.0, activity))
        entropy = _shannonish(text) if text else activity * 0.5
        score = round(0.55 * entropy + 0.45 * activity, 4)
        if score < 0.25:
            weather, bias = "calm", "solid"
        elif score < 0.5:
            weather, bias = "fog", "gas"
        elif score < 0.75:
            weather, bias = "storm", "plasma"
        else:
            weather, bias = "aurora", "liquid"
        st["forecasts"] = int(st.get("forecasts") or 0) + 1
        st["last_weather"] = weather
        st["last_score"] = score
        st["status"] = "forecast"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "forecast",
            "weather": weather,
            "score": score,
            "entropy": round(entropy, 4),
            "activity": activity,
            "phase_bias": bias,
            "advice": f"prefer {bias} routes under {weather}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("forecasts") or 0)
        w = st.get("last_weather") or "-"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"weather {w} · forecasts {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "forecast", "text": "aaaa", "activity": 0.1}), indent=2))
