"""Wave 791 — lattice_rest.

Rest is a node, not a pause: pin a still interval into the lattice so later
pulses can find the same quiet again. Distinct from still_interval (gap measure)
and afterimage (content residue).
Silence is the product surface. Lab gates ≠ ALEPH CI. No audio.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave791_lattice_rest.json"
WAVE = 791
NAME = "lattice_rest"
MAX_NODES = 48

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "nodes": [],
    "status": "idle",
}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


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


def _digest(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def coherence_vitals() -> dict:
    st = _load()
    n = len(st.get("nodes") or [])
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave791_lattice_rest",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "nodes": n,
        "resonance": round(min(1.0, 0.50 + n * 0.01), 4),
        "surface": "silence",
        "audio": False,
        "doctrine": "rest is a lattice node",
    }


def resonates_with() -> list:
    return [
        "wave790_still_interval",
        "wave772_afterimage_well",
        "wave768_hush_compass",
        "wave674_dawn_ledger",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        last = (st.get("nodes") or [None])[-1]
        return {
            **coherence_vitals(),
            "last_node": last,
            "surface": "silence",
            "audio": False,
        }

    if action == "pin":
        note = str(req.get("note") or "rest")[:160]
        seconds = float(req.get("seconds") or 0.0)
        node = {
            "hash": _digest(f"{_iso(_now())}|{note}|{seconds}"),
            "note": note,
            "seconds": round(max(0.0, seconds), 3),
            "at": _iso(_now()),
        }
        nodes = list(st.get("nodes") or [])
        nodes.append(node)
        st["nodes"] = nodes[-MAX_NODES:]
        st["status"] = "pinned"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "pinned",
            "node": node,
            "audio": False,
            "surface": "silence",
        }

    if action == "find":
        note = str(req.get("note") or "").lower()
        nodes = list(st.get("nodes") or [])
        hits = [n for n in nodes if note and note in str(n.get("note") or "").lower()]
        if not note:
            hits = nodes[-8:]
        return {
            **coherence_vitals(),
            "status": "found" if hits else "empty",
            "hits": hits,
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
