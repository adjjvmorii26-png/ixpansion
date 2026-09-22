"""Wave 803 — margin_publish_gate.

Gate silent publish on quiet_margin_meter bands (thin → hold/deny).
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave803_margin_publish_gate.json"
WAVE = 803
NAME = "margin_publish_gate"

DEFAULT = {"wave": WAVE, "name": NAME, "gates": 0, "status": "idle"}


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
        "module": "wave803_margin_publish_gate",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "gates": int(st.get("gates") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("gates") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave802_quiet_margin_meter",
        "wave785_silent_publish_orchestrator",
        "wave783_hitl_publish_gate",
        "wave778_antimeme_caption_guard",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "gate":
        text = str(req.get("text") or "")
        margin = None
        band = "soft"
        try:
            meter = _import_api("wave802_quiet_margin_meter")
            m = meter.handler({"action": "measure", "text": text})
            margin = m.get("margin")
            band = m.get("band") or "soft"
        except Exception as e:
            band = "soft"
            err = str(e)[:80]
        else:
            err = None
        if band == "thin":
            outcome = "denied"
        elif band == "soft":
            outcome = "holding"
        else:
            outcome = "allowed"
        st["gates"] = int(st.get("gates") or 0) + 1
        st["status"] = outcome
        st["last_band"] = band
        st["last_ts"] = _now()
        _save(st)
        out = {
            **coherence_vitals(),
            "status": outcome,
            "band": band,
            "margin": margin,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }
        if err:
            out["meter_error"] = err
        return out

    if action == "caption":
        n = int(st.get("gates") or 0)
        b = st.get("last_band") or "-"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"margin gates {n} · last {b}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "gate", "text": "hush"}), indent=2))
