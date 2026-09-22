"""Wave 797 — antimeme_scar_fuse.

Fuse antimeme scan with chrono scar budget; silence if risk stays hot.
Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave797_antimeme_scar_fuse.json"
WAVE = 797
NAME = "antimeme_scar_fuse"

DEFAULT = {"wave": WAVE, "name": NAME, "fuses": 0, "status": "idle"}


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
        "module": "wave797_antimeme_scar_fuse",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "fuses": int(st.get("fuses") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("fuses") or 0) * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave778_antimeme_caption_guard",
        "wave781_chrono_scar_clock",
        "wave783_hitl_publish_gate",
        "wave785_silent_publish_orchestrator",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "fuse":
        text = str(req.get("text") or "")
        steps = {}
        risk = 0.0
        try:
            guard = _import_api("wave778_antimeme_caption_guard")
            scan = guard.handler({"action": "scan", "text": text})
            steps["antimeme"] = {"verdict": scan.get("verdict"), "score": scan.get("score")}
            risk = float(scan.get("score") or 0)
        except Exception as e:
            steps["antimeme"] = {"error": str(e)[:80]}
        if risk >= 0.35:
            try:
                clock = _import_api("wave781_chrono_scar_clock")
                budget = int(800 + risk * 4000)
                o = clock.handler({"action": "open", "label": "antimeme", "budget_ms": budget})
                scar = o.get("scar")
                steps["scar"] = {"id": scar.get("id") if scar else None, "budget_ms": budget}
                if scar:
                    clock.handler({"action": "close", "id": scar.get("id")})
            except Exception as e:
                steps["scar"] = {"error": str(e)[:80]}
        silent = risk >= 0.45 or (steps.get("antimeme") or {}).get("verdict") == "block"
        st["fuses"] = int(st.get("fuses") or 0) + 1
        st["status"] = "silenced" if silent else "cleared"
        st["last_risk"] = risk
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "silenced" if silent else "cleared",
            "risk": risk,
            "silent": silent,
            "steps": steps,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("fuses") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"antimeme-scar fuses {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "fuse", "text": "hush"}), indent=2))
