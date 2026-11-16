"""Wave 951 — hush_capacitor.

Stores silence as charge. Discharges as hush weather into the bay.
Does not emit sound. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave951_hush_capacitor.json"
WAVE = 951
NAME = "hush_capacitor"
MAX_CHARGE = 1.0

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "charge": 0.0,
    "discharges": 0,
    "status": "idle",
    "weather": [],
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
    charge = float(st.get("charge") or 0.0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave951_hush_capacitor",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "charge": round(charge, 4),
        "discharges": int(st.get("discharges") or 0),
        "max_charge": MAX_CHARGE,
        "resonance": round(min(1.0, 0.62 + charge * 0.3), 4),
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
    weather = st.setdefault("weather", [])

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "charge":
        delta = float(req.get("delta") or 0.15)
        delta = max(0.0, min(delta, 0.5))
        st["charge"] = round(min(MAX_CHARGE, float(st.get("charge") or 0) + delta), 4)
        st["status"] = "charged"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "charged",
            "added": delta,
            "caption": f"silence charge · {st['charge']}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "discharge":
        amount = float(req.get("amount") or st.get("charge") or 0.0)
        amount = max(0.0, min(amount, float(st.get("charge") or 0)))
        if amount <= 0:
            return {**coherence_vitals(), "status": "empty", "audio": False}
        st["charge"] = round(float(st.get("charge") or 0) - amount, 4)
        st["discharges"] = int(st.get("discharges") or 0) + 1
        event = {
            "id": f"hush_{st['discharges']}",
            "amount": round(amount, 4),
            "kind": "hush_weather",
            "ts": _now(),
        }
        weather.append(event)
        weather[:] = weather[-32:]
        st["status"] = "discharged"
        st["last_ts"] = event["ts"]
        _save(st)
        return {
            **coherence_vitals(),
            "status": "discharged",
            "event": event,
            "caption": f"hush weather · {event['id']}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        c = float(st.get("charge") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"capacitor hush · {round(c, 2)}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
