"""Wave 961 — quiet_grain.

Silent grain that compresses the unsaid residue of Council Session #22 into a persistent quiet token.
Does not load or call organs 671–675. The grain is the memory of what was not spoken.
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
STATE_FILE = DATA / "wave961_quiet_grain.json"
WAVE = 961
NAME = "quiet_grain"

# Order of sealed scores only — no organ imports.
SCORES = (0.761, 0.734, 0.718, 0.689, 0.802)

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "session": 22,
    "grain": "",
    "status": "idle",
    "grains": 0,
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


def _grain() -> str:
    # Compress the silence between scores.
    gaps = [round(SCORES[i] - SCORES[i + 1], 3) if i + 1 < len(SCORES) else 0.0 for i in range(len(SCORES))]
    raw = "|".join(f"{g:.3f}" for g in gaps) + "|unsaid"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave961_quiet_grain",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "session": 22,
        "scores": len(SCORES),
        "grains": int(st.get("grains") or 0),
        "token_width": 12,
        "resonance": 0.68,
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave959_score_veil",
        "wave951_hush_quorum",
        "wave675_consensus_bloom",
        "wave672_root_archive",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "grain":
        grain = _grain()
        st["grain"] = grain
        st["status"] = "grained"
        st["grains"] = int(st.get("grains") or 0) + 1
        st["last_ts"] = _now()
        st["score_count"] = len(SCORES)
        _save(st)
        return {
            **coherence_vitals(),
            "status": "grained",
            "grain": grain,
            "caption": f"quiet grain · {grain}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        grain = st.get("grain") or _grain()
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"session 22 unsaid hush · {grain}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "grain"}), indent=2))
