"""Wave 704 Lab Epoch Seal — names and seals a lab growth epoch.

Lightweight ceremony organ: bind a label + wave range + fingerprint into a
sealed epoch record. Supports lineage without full council machinery.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave704_lab_epoch_seal.json"
DEFAULT = {
    "module": "wave704_lab_epoch_seal",
    "wave": 704,
    "epochs": [],
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
        "wave": 704, "module": "wave704_lab_epoch_seal", "ok": True,
        "epochs": len(st.get("epochs") or []),
    }

def resonates_with():
    return ["wave673_naming_well", "wave672_root_archive", "wave703_proof_delta"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    epochs = st.setdefault("epochs", [])
    if action == "seal":
        label = str(req.get("label") or req.get("name") or "")[:64]
        lo = int(req.get("lo") or 0)
        hi = int(req.get("hi") or 0)
        fp = str(req.get("fingerprint") or "")[:64]
        if not label:
            return {"status": "empty", **coherence_vitals()}
        eid = hashlib.sha256(f"{label}:{lo}:{hi}:{fp}".encode()).hexdigest()[:12]
        rec = {
            "id": eid, "label": label, "lo": lo, "hi": hi, "fingerprint": fp,
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        epochs.append(rec)
        epochs[:] = epochs[-48:]
        _save(st)
        return {"status": "sealed", "epoch": rec, **coherence_vitals()}
    if action == "list":
        return {"status": "list", "epochs": epochs[-10:], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
