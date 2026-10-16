"""Wave 962 — hush_fossil.

Fossilize a quiet grain (or placeholder) into a permanent silent imprint.
Does not import or call prior organs. The fossil is compressed memory of what remained unsaid.
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
STATE_FILE = DATA / "wave962_hush_fossil.json"
WAVE = 962
NAME = "hush_fossil"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "fossil": "",
    "status": "idle",
    "fossils": 0,
    "layers": 0,
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


def _fossilize(grain: str) -> str:
    """Compress grain into a silent fossil token."""
    base = (grain or "unsaid|session22|hush").strip()[:48]
    raw = f"fossil|{base}|layer"
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


def coherence_vitals() -> dict:
    st = _load()
    fossils = int(st.get("fossils") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave962_hush_fossil",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "fossils": fossils,
        "layers": int(st.get("layers") or 0),
        "token_width": 12,
        "resonance": round(min(1.0, 0.61 + fossils * 0.008), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave961_quiet_grain",
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave681_hush_membrane",
        "wave672_root_archive",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "fossil":
        grain = str(req.get("grain") or req.get("token") or "")
        fossil = _fossilize(grain)
        st["fossil"] = fossil
        st["status"] = "fossilized"
        st["fossils"] = int(st.get("fossils") or 0) + 1
        st["layers"] = int(st.get("layers") or 0) + 1
        st["last_ts"] = _now()
        st["source_width"] = len(grain)
        _save(st)
        return {
            **coherence_vitals(),
            "status": "fossilized",
            "fossil": fossil,
            "caption": f"hush fossil · {fossil}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        fossil = st.get("fossil") or _fossilize("")
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silent fossil of unsaid · {fossil}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "fossil"}), indent=2))
