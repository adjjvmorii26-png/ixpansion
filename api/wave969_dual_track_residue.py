"""Wave 969 — dual_track_residue.

Compress the dual-track gap (lab gates ≠ ALEPH full CI) into a short residue.
The residue remembers the distinction without replaying either track.
Lab organ only. Silence is the product surface. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave969_dual_track_residue.json"
WAVE = 969
NAME = "dual_track_residue"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "residues": 0,
    "last_residue": "",
    "gap": 0.0,
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


def coherence_vitals() -> dict:
    st = _load()
    residues = int(st.get("residues") or 0)
    gap = float(st.get("gap") or 0.0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave969_dual_track_residue",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "residues": residues,
        "last_residue": st.get("last_residue", ""),
        "gap": round(gap, 4),
        "resonance": round(min(1.0, 0.42 + residues * 0.012 + gap * 0.05), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave968_pulse_residue",
        "wave967_still_interval",
        "wave966_ci_sentinel",
        "wave681_hush_membrane",
        "wave675_consensus_bloom",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "observe":
        lab = str(req.get("lab") or req.get("lab_status") or "smoke_ok")[:64]
        aleph = str(req.get("aleph") or req.get("ci_status") or "full_pending")[:64]
        note = str(req.get("note") or "")[:80]
        text = f"lab:{lab}|aleph:{aleph}|{note}"
        residue = hashlib.sha256(text.encode()).hexdigest()[:12]
        # gap is a simple ordinal distance proxy: different strings → positive gap
        gap = 0.0 if lab == aleph else round(0.3 + len(set(lab) ^ set(aleph)) * 0.02, 4)
        st["residues"] = int(st.get("residues") or 0) + 1
        st["last_residue"] = residue
        st["gap"] = gap
        st["status"] = "observed"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "observed",
            "residue": residue,
            "gap": gap,
            "caption": f"dual-track residue · {residue}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        res = st.get("last_residue") or "—"
        gap = st.get("gap", 0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"lab≠ALEPH · gap {gap:.2f} · {res}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "observe", "lab": "smoke_ok", "aleph": "full_pending"}), indent=2))
