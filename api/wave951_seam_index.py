"""Wave 951 — seam_index.

Index the four silent joins between Council Session #22 organs (671–675).
Does not replay braid, archive, well, ledger, or bloom. Names only.
Silence is the product surface. Lab organ only. Lab gates ≠ ALEPH CI.
Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave951_seam_index.json"
WAVE = 951
NAME = "seam_index"

ORGANS = (
    (671, "harmony_braid"),
    (672, "root_archive"),
    (673, "naming_well"),
    (674, "dawn_ledger"),
    (675, "consensus_bloom"),
)


def _seams():
    return tuple(
        (ORGANS[i][0], ORGANS[i][1], ORGANS[i + 1][0], ORGANS[i + 1][1])
        for i in range(len(ORGANS) - 1)
    )


DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "session": 22,
    "status": "idle",
    "indexes": 0,
    "seams": 4,
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


def _digest(left: str, right: str) -> str:
    raw = f"{left}|{right}"
    return hashlib.sha256(raw.encode()).hexdigest()[:8]


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave951_seam_index",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "session": 22,
        "seams": len(_seams()),
        "indexes": int(st.get("indexes") or 0),
        "digest_width": 8,
        "resonance": 0.71,
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave671_harmony_braid",
        "wave672_root_archive",
        "wave673_naming_well",
        "wave674_dawn_ledger",
        "wave675_consensus_bloom",
        "wave949_council_witness",
        "wave950_hush_margin",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "index":
        joins = []
        for left_n, left, right_n, right in _seams():
            joins.append({
                "span": f"{left_n}-{right_n}",
                "join": f"{left}|{right}",
                "digest": _digest(left, right),
            })
        st["indexes"] = int(st.get("indexes") or 0) + 1
        st["status"] = "indexed"
        st["last_ts"] = _now()
        st["joins"] = [j["join"] for j in joins]
        _save(st)
        return {
            **coherence_vitals(),
            "status": "indexed",
            "joins": joins,
            "caption": f"seam index · {len(joins)} joins",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = len(_seams())
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"session 22 seams · {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "index"}), indent=2))
