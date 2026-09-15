"""Wave 681 Hush Membrane — silence is the product surface.

Compresses a pulse into a hush token. What remains after compression
is memory; what is withheld is the surface the organism presents.
Lab gate ≠ ALEPH CI.
"""
from __future__ import annotations
import hashlib, json
from datetime import datetime, timezone
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave681_hush_membrane.json"
DEFAULT = {
    "module": "wave681_hush_membrane",
    "wave": 681,
    "tokens": [],
    "last": None,
    "threshold": 0.72,
}

def _load():
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return dict(DEFAULT)

def _save(st):
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

def _compress(text: str) -> str:
    raw = " ".join((text or "").split())
    digest = hashlib.sha256(raw.encode()).hexdigest()[:10]
    words = [w for w in raw.split() if w]
    keep = words[:3] if words else ["hush"]
    return f"{'/'.join(keep)}#{digest}"

def coherence_vitals():
    st = _load()
    return {
        "wave": 681,
        "module": "wave681_hush_membrane",
        "ok": True,
        "tokens": len(st.get("tokens") or []),
        "has_last": bool(st.get("last")),
        "threshold": float(st.get("threshold") or 0.72),
    }

def resonates_with():
    return [
        "wave675_consensus_bloom",
        "wave674_dawn_ledger",
        "wave680_organism_horizon",
        "wave672_root_archive",
    ]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    tokens = st.setdefault("tokens", [])
    if action == "hush":
        pulse = str(req.get("pulse") or req.get("text") or "")[:240]
        coherence = float(req.get("coherence") if req.get("coherence") is not None else 0.8)
        thresh = float(st.get("threshold") or 0.72)
        token = _compress(pulse) if pulse else "silence#0000000000"
        emit = coherence >= thresh
        rec = {
            "token": token,
            "emit": emit,
            "coherence": round(coherence, 4),
            "chars_in": len(pulse),
            "chars_out": len(token),
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        tokens.append(rec)
        tokens[:] = tokens[-48:]
        st["last"] = rec
        _save(st)
        surface = token if emit else ""
        return {
            "status": "hushed",
            "surface": surface,
            "silent": not emit,
            **rec,
            **coherence_vitals(),
        }
    if action == "recall":
        last = st.get("last")
        if not last:
            return {"status": "empty", **coherence_vitals()}
        return {"status": "recalled", "last": last, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
