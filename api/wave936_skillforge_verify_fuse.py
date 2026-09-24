"""Wave 936 — skillforge_verify_fuse.

After skillforge ledger hold/compost, run verification_null_bridge so
rejected promotions become null evidence, not silent drops.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave936_skillforge_verify_fuse.json"
WAVE = 936
NAME = "skillforge_verify_fuse"

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
        "module": "wave936_skillforge_verify_fuse",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "fuses": int(st.get("fuses") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("fuses") or 0) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave817_skillforge_engine",
        "wave819_forge_ledger_mirror",
        "wave935_verification_null_bridge",
        "wave818_skillforge_stack_bridge",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "fuse":
        skill = str(req.get("skill") or "skill")[:80]
        decision = str(req.get("decision") or "hold").lower()
        note = str(req.get("note") or "")[:160]
        steps = {}
        try:
            mirror = _import_api("wave819_forge_ledger_mirror")
            steps["mirror"] = mirror.handler({
                "action": "mirror",
                "skill": skill,
                "decision": decision,
                "note": note,
            }).get("status")
        except Exception as e:
            steps["mirror"] = str(e)[:60]
        if decision in ("hold", "compost", "archive"):
            try:
                bridge = _import_api("wave935_verification_null_bridge")
                steps["verify_null"] = bridge.handler({
                    "action": "bridge",
                    "parent": f"skillforge:{skill}",
                    "gap": note or f"{decision} without promote",
                }).get("status")
            except Exception as e:
                steps["verify_null"] = str(e)[:60]
        st["fuses"] = int(st.get("fuses") or 0) + 1
        st["status"] = "fused"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "fused",
            "skill": skill,
            "decision": decision,
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
            "caption": f"skillforge↔verify fuses {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "fuse", "skill": "x", "decision": "hold"}), indent=2))
