"""Wave 956 — rank_hush.

Compress Council Session #22 score order into a silent inversion count.
score_ash keeps spread; near_hush keeps close pairs; this keeps rank disagreement.
Does not replay organs 671-675. No names, no scores on the product surface.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave956_rank_hush.json"
WAVE = 956
NAME = "rank_hush"

# Sealed milles from session #22. Order is wave order. Not replayed.
SEALED_MILLES = (761, 734, 718, 689, 802)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "inversions": 0,
    "pairs": 0,
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


def _milles(req: dict) -> tuple:
    raw = req.get("milles")
    if not raw:
        return SEALED_MILLES
    out = []
    for item in list(raw)[:8]:
        try:
            out.append(int(item))
        except (TypeError, ValueError):
            continue
    return tuple(out) if out else SEALED_MILLES


def inversions(milles: tuple) -> int:
    """Kendall inversions: earlier wave ranked above a later one."""
    n = 0
    seq = list(milles)
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                n += 1
    return n


def pair_count(milles: tuple) -> int:
    n = len(milles)
    return n * (n - 1) // 2


def coherence_vitals() -> dict:
    st = _load()
    inv = int(st.get("inversions") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave956_rank_hush",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "inversions": inv,
        "pairs": int(st.get("pairs") or 0),
        "resonance": round(min(1.0, 0.5 + inv * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave675_consensus_bloom",
        "wave674_dawn_ledger",
        "wave955_near_hush",
        "wave954_score_ash",
        "wave949_council_witness",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "rank":
        milles = _milles(req)
        inv = inversions(milles)
        pairs = pair_count(milles)
        st["inversions"] = inv
        st["pairs"] = pairs
        st["sealed"] = milles == SEALED_MILLES
        st["status"] = "ranked"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "ranked",
            "inversions": inv,
            "pairs": pairs,
            "caption": f"rank hush · {inv}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        inv = int(st.get("inversions") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silent rank {inv}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "rank"}), indent=2))
