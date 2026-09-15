"""Wave 689 Reciprocal Hush Exchange — silence tokens \u2194 void capital market.

Experimental: hush_membrane tokens and void_meter capital convert at a
living rate. Peers post offers; clearing is soft and ledgered without
blocking the dual-track. Silence becomes tradable microstructure.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave689_reciprocal_hush.json"
DEFAULT = {
    "module": "wave689_reciprocal_hush",
    "wave": 689,
    "rate_hush_per_void": 1.0,
    "offers": [],
    "clears": [],
    "volume": 0.0,
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
        "wave": 689, "module": "wave689_reciprocal_hush", "ok": True,
        "rate": st.get("rate_hush_per_void", 1.0),
        "offers": len(st.get("offers") or []),
        "volume": st.get("volume", 0),
    }

def resonates_with():
    return ["wave681_hush_membrane", "wave683_void_meter", "wave675_consensus_bloom"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    offers = st.setdefault("offers", [])
    clears = st.setdefault("clears", [])
    if action == "offer":
        side = str(req.get("side") or "sell_hush").lower()
        amount = float(req.get("amount") or 1.0)
        peer = str(req.get("peer") or "anon")[:32]
        oid = hashlib.sha256(f"{side}:{peer}:{amount}:{len(offers)}".encode()).hexdigest()[:12]
        offers.append({
            "id": oid, "side": side, "amount": amount, "peer": peer,
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        offers[:] = offers[-32:]
        _save(st)
        return {"status": "offered", "id": oid, **coherence_vitals()}
    if action == "clear":
        rate = float(st.get("rate_hush_per_void") or 1.0)
        sells_h = [o for o in offers if o.get("side") == "sell_hush"]
        sells_v = [o for o in offers if o.get("side") == "sell_void"]
        if not sells_h or not sells_v:
            return {"status": "no_match", **coherence_vitals()}
        a, b = sells_h[0], sells_v[0]
        qty = min(float(a["amount"]), float(b["amount"]) * rate)
        clears.append({
            "hush_offer": a["id"], "void_offer": b["id"], "qty": round(qty, 4),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        clears[:] = clears[-32:]
        st["volume"] = round(float(st.get("volume") or 0) + qty, 4)
        offers[:] = [o for o in offers if o.get("id") not in (a["id"], b["id"])]
        st["rate_hush_per_void"] = round(max(0.25, min(4.0, rate * (1.0 + 0.01 * (1 if qty > 1 else -1)))), 4)
        _save(st)
        return {"status": "cleared", "qty": qty, "rate": st["rate_hush_per_void"], **coherence_vitals()}
    if action == "book":
        return {"status": "book", "offers": offers, "clears": clears[-5:], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
