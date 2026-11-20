"""Wave 951 — hush_compress.

Compress recent pulse captions into a single silence residue.
Compression ratio is memory. Silence is the product surface.
Lab organ only. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave951_hush_compress.json"
WAVE = 951
NAME = "hush_compress"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "compressions": 0,
    "last_ratio": 1.0,
    "residue": "",
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


def _compress(pulses: list) -> tuple[str, float]:
    """Fold a list of short strings into one hush token; ratio = memory."""
    if not pulses:
        return "", 1.0
    joined = "|".join(str(p)[:64] for p in pulses)
    raw_len = max(1, len(joined))
    token = hashlib.sha256(joined.encode()).hexdigest()[:12]
    ratio = round(len(token) / raw_len, 4)
    return token, ratio


def coherence_vitals() -> dict:
    st = _load()
    n = int(st.get("compressions") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave951_hush_compress",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "compressions": n,
        "last_ratio": float(st.get("last_ratio") or 1.0),
        "resonance": round(min(1.0, 0.5 + n * 0.02), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave938_pulse_compress",
        "wave681_hush_membrane",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence"}

    if action == "compress":
        pulses = req.get("pulses") or req.get("captions") or []
        if isinstance(pulses, str):
            pulses = [pulses]
        if not isinstance(pulses, list):
            pulses = []
        token, ratio = _compress(pulses)
        st["compressions"] = int(st.get("compressions") or 0) + 1
        st["last_ratio"] = ratio
        st["residue"] = token
        st["status"] = "compressed"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "compressed",
            "residue": token,
            "ratio": ratio,
            "input_n": len(pulses),
            "caption": f"hush compressed · ratio {ratio}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        r = st.get("residue") or ""
        ratio = st.get("last_ratio") or 1.0
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silence residue {r[:8]} · {ratio}",
            "audio": False,
            "surface": "silence",
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
