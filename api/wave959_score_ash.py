"""Wave 959 — score_ash.

Council Session #22 sealed five scores. The organs keep the numbers.
This organ burns them to a single ash token: sorted scores, compressed once.
Does not call 671–675. Ash is the memory the scores leave behind.

Silence is the product surface. Compression is memory.
Lab gate only — not ALEPH CI.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave959_score_ash.json"
WAVE = 959
NAME = "score_ash"

# Sealed Session #22 scores. Do not replay handlers.
SEALED = (
    {"wave": 671, "name": "harmony_braid", "persona": "AXIOME", "score": 0.761},
    {"wave": 672, "name": "root_archive", "persona": "CYTHARA", "score": 0.734},
    {"wave": 673, "name": "naming_well", "persona": "LUMINA", "score": 0.718},
    {"wave": 674, "name": "dawn_ledger", "persona": "NOOS", "score": 0.689},
    {"wave": 675, "name": "consensus_bloom", "persona": "ALEPH", "score": 0.802},
)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "burns": 0,
    "ash": "",
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


def sorted_scores() -> list:
    """Milli-scores sorted ascending. No organ calls."""
    return sorted(int(round(row["score"] * 1000)) for row in SEALED)


def ash_token(millis=None) -> str:
    millis = millis if millis is not None else sorted_scores()
    blob = "|".join(str(m) for m in millis)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


def coherence_vitals() -> dict:
    st = _load()
    n = int(st.get("burns") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave959_score_ash",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "burns": n,
        "sealed": 5,
        "resonance": round(min(1.0, 0.48 + n * 0.008), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave671_harmony_braid",
        "wave672_root_archive",
        "wave673_naming_well",
        "wave674_dawn_ledger",
        "wave675_consensus_bloom",
        "wave958_gap_hush",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "burn":
        millis = sorted_scores()
        ash = ash_token(millis)
        st["burns"] = int(st.get("burns") or 0) + 1
        st["ash"] = ash
        st["status"] = "ashed"
        st["last_ts"] = _now()
        st["span"] = millis[-1] - millis[0]
        _save(st)
        return {
            **coherence_vitals(),
            "status": "ashed",
            "ash": ash,
            "millis": millis,
            "span": st["span"],
            "caption": f"score ash · {ash}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        ash = st.get("ash") or ash_token()
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"session 22 ash {ash}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "burn"}), indent=2))
