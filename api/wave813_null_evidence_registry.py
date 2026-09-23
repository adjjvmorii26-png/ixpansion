"""Wave 813 — null_evidence_registry.

First-class registry of null / negative results so evidence ledgers
do not only store positive hits (pairs with wave904 evidence ledger).

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave813_null_evidence_registry.json"
WAVE = 813
NAME = "null_evidence_registry"

DEFAULT = {"wave": WAVE, "name": NAME, "entries": [], "status": "idle"}


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
    entries = st.get("entries") or []
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave813_null_evidence_registry",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "nulls": len(entries),
        "resonance": round(min(1.0, 0.5 + len(entries) * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave810_question_triad",
        "wave808_discovery_cycle_engine",
        "wave805_null_choir_counter",
        "wave794_organ_debt_auditor",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {
            **coherence_vitals(),
            "entries": (st.get("entries") or [])[-8:],
            "audio": False,
            "surface": "silence",
        }

    if action == "record":
        hyp = str(req.get("hypothesis") or "")[:200]
        note = str(req.get("note") or req.get("text") or "")[:300]
        if not hyp and not note:
            return {
                **coherence_vitals(),
                "status": "empty",
                "audio": False,
                "surface": "silence",
            }
        entries = list(st.get("entries") or [])
        entries.append({"hypothesis": hyp, "note": note, "ts": _now()})
        st["entries"] = entries[-128:]
        st["status"] = "recorded"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "recorded",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = len(st.get("entries") or [])
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"null evidence · {n} entries",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "record", "hypothesis": "x", "note": "no effect"}), indent=2))
