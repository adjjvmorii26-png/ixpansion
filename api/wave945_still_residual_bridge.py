"""Wave 945 — still_residual_bridge.

Bridge hush_still (944) residue into residual_chain_cap (940) caption path.
Read-only observe; no payload. Silence is the product surface. Lab organ only.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave945_still_residual_bridge.json"
WAVE = 945
NAME = "still_residual_bridge"

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
        "module": "wave945_still_residual_bridge",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "bridges": int(st.get("bridges") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("bridges") or 0) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave944_hush_still",
        "wave940_residual_chain_cap",
        "wave939_residual_bind",
        "wave938_pulse_compress",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "bridge":
        steps = {}
        still_hash = ""
        try:
            still = _import_api("wave944_hush_still")
            s = still.handler({"action": "status"})
            still_hash = str(s.get("hash") or s.get("seal") or s.get("residue") or "")[:64]
            steps["still"] = s.get("status")
        except Exception as e:
            steps["still"] = str(e)[:60]
        try:
            cap = _import_api("wave940_residual_chain_cap")
            steps["cap"] = cap.handler({"action": "cap"}).get("status")
        except Exception as e:
            steps["cap"] = str(e)[:60]
        st["bridges"] = int(st.get("bridges") or 0) + 1
        st["status"] = "bridged"
        st["last_hash"] = still_hash
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "bridged",
            "still_hash": still_hash,
            "steps": steps,
            "caption": f"still→residual · {still_hash[:12] or 'empty'}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("bridges") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"still residual bridges {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "bridge"}), indent=2))
