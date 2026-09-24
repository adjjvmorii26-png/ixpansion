"""Wave 935 — verification_null_bridge.

When verification reports a gap, record null evidence + lineage edge.
Pairs with wave933/934 without hard import dependency.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave935_verification_null_bridge.json"
WAVE = 935
NAME = "verification_null_bridge"

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
        "module": "wave935_verification_null_bridge",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "bridges": int(st.get("bridges") or 0),
        "resonance": round(min(1.0, 0.5 + int(st.get("bridges") or 0) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave933_verification_explainability",
        "wave934_verification_provenance",
        "wave813_null_evidence_registry",
        "wave814_lineage_null_fuse",
        "wave823_pytest_collection_gate",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "bridge":
        gap = str(req.get("gap") or req.get("note") or "verification gap").strip()[:200]
        parent = str(req.get("parent") or "verification").strip()[:120]
        steps = {}
        try:
            reg = _import_api("wave813_null_evidence_registry")
            steps["null"] = reg.handler({
                "action": "record",
                "hypothesis": f"verify:{parent}",
                "note": gap,
            }).get("status")
        except Exception as e:
            steps["null"] = str(e)[:60]
        try:
            fuse = _import_api("wave814_lineage_null_fuse")
            steps["fuse"] = fuse.handler({
                "action": "fuse",
                "parent": parent,
                "hypothesis": gap,
                "note": "verification_null_bridge",
            }).get("status")
        except Exception as e:
            steps["fuse"] = str(e)[:60]
        st["bridges"] = int(st.get("bridges") or 0) + 1
        st["status"] = "bridged"
        st["last_gap"] = gap
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "bridged",
            "gap": gap,
            "steps": steps,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("bridges") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"verification→null bridges {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "bridge", "gap": "probe"}), indent=2))
