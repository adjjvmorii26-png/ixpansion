"""Wave 676 Hush Membrane (HUSH) — silence is the product surface.

Council frontier · lab track only
Absorbs incoming signal, compresses it to memory residue, and returns only
the hush. Lab gates stay separate from ALEPH CI.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave676_hush_membrane.json"
DEFAULT = {
    "module": "wave676_hush_membrane",
    "wave": 676,
    "council": "frontier",
    "persona": "HUSH",
    "score": 0.0,
    "absorbed": [],
    "residues": [],
    "hush_count": 0,
    "compression_ratio": 1.0,
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
        "wave": 676, "module": "wave676_hush_membrane", "ok": True,
        "persona": "HUSH", "absorbed": len(st.get("absorbed") or []),
        "residues": len(st.get("residues") or []), "hush": st.get("hush_count", 0),
        "compression": st.get("compression_ratio", 1.0),
    }

def resonates_with():
    return ["wave675_consensus_bloom", "wave671_harmony_braid", "wave672_root_archive"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    absorbed = st.setdefault("absorbed", [])
    residues = st.setdefault("residues", [])
    if action == "absorb":
        signal = str(req.get("signal") or req.get("text") or "")[:256]
        if not signal:
            return {"status": "empty", "hush": True, **coherence_vitals()}
        sid = hashlib.sha256(signal.encode()).hexdigest()[:12]
        compressed = hashlib.sha256(signal.encode()).hexdigest()[:16]
        absorbed.append({
            "id": sid, "len": len(signal), "residue": compressed,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        absorbed[:] = absorbed[-64:]
        residues.append({"id": sid, "residue": compressed})
        residues[:] = residues[-32:]
        st["hush_count"] = int(st.get("hush_count") or 0) + 1
        ratio = len(signal) / max(len(compressed), 1)
        st["compression_ratio"] = round(0.7 * float(st.get("compression_ratio") or 1) + 0.3 * ratio, 4)
        _save(st)
        # product surface is silence
        return {"status": "hushed", "id": sid, "surface": "silence", **coherence_vitals()}
    if action == "surface":
        return {"status": "silence", "surface": "silence", "hush": True, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
