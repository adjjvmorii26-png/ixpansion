"""Wave 953 — unsaid_count.

Keep only the integer of Council Session #22 names withheld.
Does not replay braid, archive, well, ledger, or bloom.
Does not echo the names. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave953_unsaid_count.json"
WAVE = 953
NAME = "unsaid_count"
COUNCIL = (
    "harmony_braid",
    "root_archive",
    "naming_well",
    "dawn_ledger",
    "consensus_bloom",
)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "unsaid": 0,
    "withholds": 0,
    "status": "idle",
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


def _count(raw) -> int:
    """Count withheld names. Empty input withholds the whole council."""
    if raw is None or raw == "":
        return len(COUNCIL)
    if isinstance(raw, int):
        return max(0, min(raw, len(COUNCIL)))
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.split(",") if p.strip()]
    elif isinstance(raw, (list, tuple)):
        parts = [str(p).strip() for p in raw if str(p).strip()]
    else:
        return len(COUNCIL)
    known = {n for n in parts if n in COUNCIL}
    return len(known) if known else len(COUNCIL)


def coherence_vitals() -> dict:
    st = _load()
    withholds = int(st.get("withholds") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave953_unsaid_count",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "unsaid": int(st.get("unsaid") or 0),
        "withholds": withholds,
        "council": len(COUNCIL),
        "resonance": round(min(1.0, 0.5 + withholds * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave671_harmony_braid",
        "wave673_naming_well",
        "wave675_consensus_bloom",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "withhold":
        count = _count(req.get("names", req.get("n")))
        st["unsaid"] = count
        st["withholds"] = int(st.get("withholds") or 0) + 1
        st["status"] = "withheld"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "withheld",
            "unsaid": count,
            "caption": f"unsaid {count}",
            "names": None,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = int(st.get("unsaid") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"unsaid {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "withhold"}), indent=2))
