"""Wave 953 — memory_compress.

Treats compression itself as durable memory. Stores only the residue
of prior silence seeds; never expands. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI. Compression is memory.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave953_memory_compress.json"
WAVE = 953
NAME = "memory_compress"
RESIDUE_WIDTH = 12

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "residues": [],
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


def _compress(seed: str, prior: str = "") -> str:
    """Compress a silence seed into a fixed-width residue. No expansion."""
    raw = f"{seed}:{prior or 'mem'}"
    return hashlib.sha256(raw.encode()).hexdigest()[:RESIDUE_WIDTH]


def coherence_vitals() -> dict:
    st = _load()
    n = int(st.get("compressions") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave953_memory_compress",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "compressions": n,
        "residues": len(st.get("residues") or []),
        "width": RESIDUE_WIDTH,
        "resonance": round(min(1.0, 0.58 + n * 0.006), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave952_silence_seed",
        "wave950_hush_margin",
        "wave681_hush_membrane",
        "wave674_dawn_ledger",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "compress":
        seed = str(req.get("seed") or "hush")[:32]
        prior = ""
        residues = st.setdefault("residues", [])
        if residues:
            prior = residues[-1].get("residue", "")
        residue = _compress(seed, prior)
        entry = {
            "residue": residue,
            "seed": seed,
            "ts": _now(),
        }
        residues.append(entry)
        residues[:] = residues[-32:]
        st["compressions"] = int(st.get("compressions") or 0) + 1
        st["status"] = "compressed"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "compressed",
            "residue": residue,
            "caption": f"memory compress · {residue}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        residues = st.get("residues") or []
        last = residues[-1]["residue"] if residues else _compress("idle")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"compressed memory · {last}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "compress", "seed": "test"}), indent=2))
