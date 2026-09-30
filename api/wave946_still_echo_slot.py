"""Wave 946 — still_echo_slot.

Compress hush_still (944) residue into a circular 8-slot silent echo.
Read-only observe of 944/945; no payload. Silence is the product surface.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave946_still_echo_slot.json"
WAVE = 946
NAME = "still_echo_slot"
SLOTS = 8

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "echoes": 0,
    "slots": [""] * SLOTS,
    "head": 0,
    "status": "idle",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            raw = json.loads(STATE_FILE.read_text())
            if isinstance(raw, dict):
                raw.setdefault("slots", [""] * SLOTS)
                raw.setdefault("head", 0)
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
    echoes = int(st.get("echoes") or 0)
    filled = sum(1 for s in (st.get("slots") or []) if s)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave946_still_echo_slot",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "echoes": echoes,
        "filled": filled,
        "resonance": round(min(1.0, 0.5 + echoes * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave945_still_residual_bridge",
        "wave944_hush_still",
        "wave942_hush_ledger",
        "wave938_pulse_compress",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "echo":
        residue = str(req.get("residue") or "")[:16]
        if not residue:
            try:
                still = _import_api("wave944_hush_still")
                s = still.handler({"action": "status"})
                residue = str(s.get("residue") or s.get("hash") or s.get("seal") or "")[:16]
            except Exception:
                residue = ""
        if not residue:
            residue = "still"
        slots = list(st.get("slots") or [""] * SLOTS)
        while len(slots) < SLOTS:
            slots.append("")
        slots = slots[:SLOTS]
        head = int(st.get("head") or 0) % SLOTS
        slots[head] = residue
        st["slots"] = slots
        st["head"] = (head + 1) % SLOTS
        st["echoes"] = int(st.get("echoes") or 0) + 1
        st["status"] = "echoed"
        st["last_residue"] = residue
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "echoed",
            "residue": residue,
            "slot": head,
            "caption": f"still echo · {residue}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("echoes") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"still echo slots {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "echo"}), indent=2))
