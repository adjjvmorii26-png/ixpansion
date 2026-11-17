"""Wave 951 — hush_compressor.

Compress residual memory into silence. Ratio is the memory density.
Output is always silence. Lab organ only. Lab gates ≠ ALEPH CI.
Compression is memory. Silence is the product surface.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
STATE_FILE = DATA / "wave951_hush_compressor.json"
WAVE = 951
NAME = "hush_compressor"

DEFAULT = {
    "wave": WAVE,
    "name": NAME,
    "compressions": 0,
    "ratio": 1.0,
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
    comps = int(st.get("compressions") or 0)
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave951_hush_compressor",
        "ok": True,
        "layer": "organ",
        "status": st.get("status", "idle"),
        "compressions": comps,
        "ratio": float(st.get("ratio") or 1.0),
        "resonance": round(min(1.0, 0.6 + comps * 0.005), 4),
        "surface": "silence",
    }


def resonates_with() -> list:
    return [
        "wave950_hush_margin",
        "wave949_council_witness",
        "wave942_hush_ledger",
        "wave938_pulse_compress",
    ]


def handler(req=None) -> dict:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    st = _load()

    if action == "status":
        return {**coherence_vitals(), "audio": False, "surface": "silence", "payload": None}

    if action == "compress":
        residual = str(req.get("residual") or req.get("text") or "")
        before = max(1, len(residual))
        # compression is memory: fold into hush ratio
        ratio = round(1.0 / (1.0 + before * 0.01), 4)
        st["compressions"] = int(st.get("compressions") or 0) + 1
        st["ratio"] = ratio
        st["last_before"] = before
        st["status"] = "compressed"
        st["last_ts"] = _now()
        _save(st)
        return {
            **coherence_vitals(),
            "status": "compressed",
            "ratio": ratio,
            "before": before,
            "caption": f"hush compressed · ratio {ratio}",
            "payload": None,
            "audio": False,
            "surface": "silence",
        }

    if action == "caption":
        r = float(st.get("ratio") or 1.0)
        return {
            **coherence_vitals(),
            "status": "captioned",
            "caption": f"silence holds ratio {r}",
            "audio": False,
            "surface": "silence",
            "payload": None,
        }

    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "compress", "residual": "council residue"}), indent=2))
