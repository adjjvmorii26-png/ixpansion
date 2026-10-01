"""Wave 949 — council_witness.

Compress Council Session #22 organs (671–675) into one silent witness token.
Does not replay braid, archive, well, ledger, or bloom. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave949_council_witness.json"
WAVE = 949
NAME = "council_witness"

COUNCIL = (
    (671, "harmony_braid", "AXIOME"),
    (672, "root_archive", "ROOT"),
    (673, "naming_well", "NAME"),
    (674, "dawn_ledger", "DAWN"),
    (675, "consensus_bloom", "ALEPH"),
)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "session": 22,
    "token": "",
    "status": "idle",
    "witnesses": 0,
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


def _token() -> str:
    raw = "|".join(f"{n}:{name}:{persona}" for n, name, persona in COUNCIL)
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave949_council_witness",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "session": 22,
        "organs": len(COUNCIL),
        "witnesses": int(st.get("witnesses") or 0),
        "token_width": 12,
        "resonance": 0.76,
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave671_harmony_braid",
        "wave672_root_archive",
        "wave673_naming_well",
        "wave674_dawn_ledger",
        "wave675_consensus_bloom",
        "wave948_fold_register",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "witness":
        token = _token()
        st["token"] = token
        st["status"] = "witnessed"
        st["witnesses"] = int(st.get("witnesses") or 0) + 1
        st["last_ts"] = _now()
        st["organs"] = [name for _, name, _ in COUNCIL]
        _save(st)
        return {
            **coherence_vitals(),
            "status": "witnessed",
            "token": token,
            "caption": f"council witness · {token}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        token = st.get("token") or _token()
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"session 22 hush · {token}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "witness"}), indent=2))
