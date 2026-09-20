"""Wave 784 — glass_orchard_compress.

Luminant-reliquary metaphor: compress text into a short crystal digest
(hash + silhouette) for void-safe memory — keys, not payloads.

Silence is the product surface. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave784_glass_orchard_compress.json"
WAVE = 784
NAME = "glass_orchard_compress"
MAX_CRYSTALS = 48

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "crystals": [],
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


def _silhouette(text: str) -> str:
    words = re.findall(r"[a-zA-Z0-9]+", text.lower())
    if not words:
        return "·"
    return "".join(w[0] for w in words[:8])


def coherence_vitals() -> dict:
    st = _load()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave784_glass_orchard_compress",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "crystals": len(st.get("crystals") or []),
        "resonance": round(min(1.0, 0.5 + len(st.get("crystals") or []) * 0.01), 4),
        "surface": "silence",
        "policy": "digest_not_payload",
    }


def resonates_with() -> list:
    return [
        "wave769_void_index",
        "wave772_afterimage_well",
        "wave778_antimeme_caption_guard",
        "wave775_constellation_affinity",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "compress":
        text = str(req.get("text") or "")
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
        sil = _silhouette(text)
        crystal = {
            "id": f"cry-{digest[:8]}",
            "digest": digest,
            "silhouette": sil,
            "len": len(text),
            "ts": _now(),
        }
        crystals = list(st.get("crystals") or [])
        crystals.append(crystal)
        st["crystals"] = crystals[-MAX_CRYSTALS:]
        st["status"] = "compressed"
        _save(st)
        return {
            **coherence_vitals(),
            "status": "compressed",
            "crystal": crystal,
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        n = len(st.get("crystals") or [])
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"orchard crystals {n}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "compress", "text": "council green hush"}), indent=2))
