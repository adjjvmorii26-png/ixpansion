"""Wave 955 — near_hush.

Compress a score spread into the count of pairs closer than a hush threshold.
Default spread is the sealed Council Session #22 milles. Names and scores stay out.
Does not replay braid, archive, well, ledger, bloom, or score_ash.
Sum of consecutive gaps equals max-min; this organ counts near pairs instead.
Silence is the product surface. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave955_near_hush.json"
WAVE = 955
NAME = "near_hush"
SEALED_MILLES = (761, 734, 718, 689, 802)
DEFAULT_THRESHOLD = 40

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "near": 0,
    "threshold": DEFAULT_THRESHOLD,
    "hushes": 0,
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
        v = float(raw)
        return [int(round(v * (1000 if 0 < v <= 1 else 1)))]
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


def _threshold(raw) -> int:
    if raw is None or raw == "":
        return DEFAULT_THRESHOLD
    try:
        t = int(round(float(raw)))
    except (TypeError, ValueError):
        return DEFAULT_THRESHOLD
    return max(1, min(t, 1000))


def _near(milles: list, threshold: int) -> int:
    """Memory is proximity count, not the scores."""
    n = len(milles)
    if n < 2:
        return 0
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            if abs(milles[i] - milles[j]) < threshold:
                count += 1
    return count


def coherence_vitals() -> dict:
    st = _load()
    n = int(st.get("hushes") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave955_near_hush",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "near": int(st.get("near") or 0),
        "threshold": int(st.get("threshold") or DEFAULT_THRESHOLD),
        "hushes": n,
        "resonance": round(min(1.0, 0.55 + n * 0.01), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave954_score_ash",
        "wave671_harmony_braid",
        "wave674_dawn_ledger",
        "wave675_consensus_bloom",
        "wave949_council_witness",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "hush":
        milles = _milles(req.get("scores", req.get("milles")))
        threshold = _threshold(req.get("threshold"))
        near = _near(milles, threshold)
        st["near"] = near
        st["threshold"] = threshold
        st["width"] = len(milles)
        st["hushes"] = int(st.get("hushes") or 0) + 1
        st["status"] = "hushed"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "hushed",
            "near": near,
            "threshold": threshold,
            "width": len(milles),
            "caption": f"near {near}",
            "scores": None,
            "names": None,
            "pairs": None,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        near = int(st.get("near") or 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"near {near}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "hush"}), indent=2))
