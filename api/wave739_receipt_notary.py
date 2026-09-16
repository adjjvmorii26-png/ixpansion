"""Wave 739 Receipt Notary — minimal cross-organ trust receipts."""
from __future__ import annotations
import hashlib, hmac, json, os
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave739_receipt_notary.json"
DEFAULT = {"module": "wave739_receipt_notary", "wave": 739, "issued": 0, "receipts": []}
LAB_SALT = os.environ.get("IX_NOTARY_SECRET", "ixpansion-lab-notary-v1").encode()


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


def _sign(payload: str) -> str:
    return hmac.new(LAB_SALT, payload.encode(), hashlib.sha256).hexdigest()


def coherence_vitals():
    st = _load()
    return {"wave": 739, "module": "wave739_receipt_notary", "ok": True, "issued": st.get("issued", 0)}


def resonates_with():
    return ["wave703_proof_delta", "wave460_pulse_engine_bridge", "wave736_silent_broadcast_lattice"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "issue":
        kind = str(req.get("kind") or "generic")[:32]
        body = req.get("body") or req.get("content") or {}
        if not isinstance(body, str):
            body = json.dumps(body, sort_keys=True, default=str)
        ts = datetime.now(timezone.utc).isoformat()
        material = f"{kind}|{ts}|{body}"
        sig = _sign(material)
        rec = {"id": sig[:16], "kind": kind, "ts": ts, "sig": sig,
               "body_hash": hashlib.sha256(body.encode()).hexdigest()[:16]}
        receipts = st.setdefault("receipts", [])
        receipts.append(rec)
        st["receipts"] = receipts[-64:]
        st["issued"] = int(st.get("issued") or 0) + 1
        _save(st)
        return {"status": "issued", "receipt": rec, **coherence_vitals()}
    if action == "verify":
        kind, ts = str(req.get("kind") or ""), str(req.get("ts") or "")
        body = req.get("body") or ""
        if not isinstance(body, str):
            body = json.dumps(body, sort_keys=True, default=str)
        sig = str(req.get("sig") or "")
        expect = _sign(f"{kind}|{ts}|{body}")
        return {"status": "verify", "valid": hmac.compare_digest(expect, sig), **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "issue", "kind": "vitals", "body": {"ok": True}}), indent=2))
