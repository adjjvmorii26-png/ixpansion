"""Wave 954 — score_ash.

Compress a score spread into one integer of milles.
Default spread is the sealed Council Session #22 scores, but names are not stored.
Does not replay braid, archive, well, ledger, or bloom.
Silence is the product surface. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave954_score_ash.json"
WAVE = 954
NAME = "score_ash"
# Sealed session milles, order-only. Names stay outside the organ.
SEALED_MILLES = (761, 734, 718, 689, 802)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "ash": 0,
    "compressions": 0,
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


def _milles(raw) -> list:
    if raw is None or raw == "" or raw == []:
        return list(SEALED_MILLES)
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return [int(round(float(raw) * (1000 if float(raw) <= 1 else 1)))]
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.replace(";", ",").split(",") if p.strip()]
    elif isinstance(raw, (list, tuple)):
        parts = list(raw)
    else:
        return list(SEALED_MILLES)
    out = []
    for p in parts[:8]:
        try:
            v = float(p)
        except (TypeError, ValueError):
            continue
        if 0 < v <= 1:
            v = v * 1000
        out.append(int(round(max(0, min(v, 1000)))))
    return out or list(SEALED_MILLES)


def _ash(milles: list) -> int:
    """Memory is the spread, not the scores."""
    if len(milles) < 2:
        return 0
    return max(milles) - min(milles)


def coherence_vitals() -> dict:
    st = _load()
    n = int(st.get("compressions") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave954_score_ash",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "ash": int(st.get("ash") or 0),
        "compressions": n,
        "resonance": round(min(1.0, 0.52 + n * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave953_unsaid_count",
        "wave671_harmony_braid",
        "wave674_dawn_ledger",
        "wave675_consensus_bloom",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "compress":
        milles = _milles(req.get("scores", req.get("milles")))
        ash = _ash(milles)
        st["ash"] = ash
        st["compressions"] = int(st.get("compressions") or 0) + 1
        st["width"] = len(milles)
        st["status"] = "ashed"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "ashed",
            "ash": ash,
            "width": len(milles),
            "caption": f"ash {ash}",
            "scores": None,
            "names": None,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        ash = int(st.get("ash") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"ash {ash}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "compress"}), indent=2))
