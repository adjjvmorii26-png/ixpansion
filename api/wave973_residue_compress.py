"""Wave 973 Residue Compress — compress residual traces into a silent memory token.

Frontier organ after hush_vector (972).
Takes residual input, folds it into a short silent token. Does not replay or expand.
Silence is the product surface. Compression is memory. Lab gates ≠ ALEPH CI.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave973_residue_compress.json"
DEFAULT = {
    "module": "wave973_residue_compress",
    "wave": 973,
    "tokens": [],
    "compressions": 0,
}

def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except Exception: pass
    return dict(DEFAULT)

def _save(st):
    DATA.mkdir(parents=True, exist_ok=True)
    try:
        tmp = STATE_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(st, indent=2) + "\n")
        tmp.replace(STATE_FILE)
    except OSError:
        try: STATE_FILE.write_text(json.dumps(st, indent=2) + "\n")
        except OSError: pass

def coherence_vitals():
    st = _load()
    return {
        "wave": 973, "module": "wave973_residue_compress", "ok": True,
        "tokens": len(st.get("tokens") or []), "compressions": st.get("compressions", 0),
    }

def resonates_with():
    return ["wave972_hush_vector", "wave971_threshold_silence", "wave949_council_witness"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    tokens = st.setdefault("tokens", [])
    if action == "compress":
        residual = str(req.get("residual") or req.get("trace") or "")[:256]
        if not residual.strip():
            return {"status": "empty", "token": "", **coherence_vitals()}
        # Compress: hash + length fold into 12-char silent token
        h = hashlib.sha256(residual.encode()).hexdigest()
        token = (h[:8] + str(len(residual))[-4:]).lower()[:12]
        tokens.append({
            "token": token, "len": len(residual),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        tokens[:] = tokens[-32:]
        st["compressions"] = st.get("compressions", 0) + 1
        _save(st)
        return {"status": "compressed", "token": token, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
