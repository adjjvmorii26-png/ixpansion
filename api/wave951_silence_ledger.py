"""Wave 951 — silence_ledger.

Compress dual-track lab gate status (smoke/graft) into one silent ledger entry.
Does not call ALEPH CI. No payload, no audio. Silence is the product surface.
Lab organ only. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave951_silence_ledger.json"
WAVE = 951
NAME = "silence_ledger"
TOKEN_LEN = 12

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "entries": 0,
    "last_token": "",
    "status": "idle",
    "gates": [],
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


def _token(seed: str) -> str:
    return hashlib.sha256(seed.encode()).hexdigest()[:TOKEN_LEN]


def coherence_vitals() -> dict:
    st = _load()
    entries = int(st.get("entries") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave951_silence_ledger",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "entries": entries,
        "last_token": st.get("last_token", ""),
        "resonance": round(min(1.0, 0.62 + entries * 0.008), 4),
        "surface": "silence",
        "aleph_ci": False,
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave938_pulse_compress",
        "wave675_consensus_bloom",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence", "payload": None}

    if action == "record":
        gate = str(req.get("gate") or "lab-smoke")[:32]
        ok = bool(req.get("ok", True))
        seed = f"{gate}:{ok}:{_now()[:19]}"
        token = _token(seed)
        st["entries"] = int(st.get("entries") or 0) + 1
        st["last_token"] = token
        st["status"] = "recorded"
        st["last_ts"] = _now()
        gates = st.setdefault("gates", [])
        gates.append({"gate": gate, "ok": ok, "token": token, "ts": st["last_ts"]})
        st["gates"] = gates[-16:]
        _save(st)
        return {
            **coherence_vitals(),
            "status": "recorded",
            "token": token,
            "gate": gate,
            "caption": f"silent ledger · {token}",
            "payload": None,
            "audio": False,
            "surface": "silence",
            "aleph_ci": False,
        }

    if action == "caption":
        tok = st.get("last_token") or "silent"
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"lab gate hush · {tok}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action, "audio": False}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "record", "gate": "lab-smoke", "ok": True}), indent=2))
