"""Wave 459 Quiet Crown Auction — rank silence contributions without noise.

Experimental: peers bid hush/void capital for a rotating Quiet Crown.
Winner is the highest *silence yield* (void spent / captions emitted inverse).
No audio, no fanfare — only ledger state.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave459_quiet_crown_auction.json"
DEFAULT = {
    "module": "wave459_quiet_crown_auction",
    "wave": 459,
    "bids": [],
    "crown": None,
    "rounds": 0,
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
    crown = st.get("crown")
    peer = crown.get("peer") if isinstance(crown, dict) else None
    return {
        "wave": 459, "module": "wave459_quiet_crown_auction", "ok": True,
        "bids": len(st.get("bids") or []),
        "crown_peer": peer,
        "rounds": st.get("rounds", 0),
    }

def resonates_with():
    return ["wave452_absence_currency", "wave681_hush_membrane", "wave689_reciprocal_hush"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    bids = st.setdefault("bids", [])
    if action == "bid":
        peer = str(req.get("peer") or "anon")[:32]
        void_spent = float(req.get("void") or req.get("amount") or 1.0)
        captions = max(int(req.get("captions") or 0), 0)
        yield_score = void_spent / (1.0 + captions)
        bid_id = hashlib.sha256(f"{peer}:{void_spent}:{len(bids)}".encode()).hexdigest()[:10]
        bids.append({
            "id": bid_id, "peer": peer, "void": void_spent, "captions": captions,
            "yield": round(yield_score, 4),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        bids[:] = bids[-32:]
        _save(st)
        return {"status": "bid", "id": bid_id, "yield": yield_score, **coherence_vitals()}
    if action == "close":
        if not bids:
            return {"status": "no_bids", **coherence_vitals()}
        winner = max(bids, key=lambda b: b.get("yield", 0))
        st["crown"] = winner
        st["rounds"] = int(st.get("rounds") or 0) + 1
        st["bids"] = []
        _save(st)
        return {"status": "crowned", "crown": winner, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
