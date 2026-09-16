"""Wave 740 Negotiation Bazaar — local market for attention / still / scaffolds."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave740_negotiation_bazaar.json"
DEFAULT = {"module": "wave740_negotiation_bazaar", "wave": 740, "bids": [], "asks": [], "trades": []}


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
    return {"wave": 740, "module": "wave740_negotiation_bazaar", "ok": True,
            "bids": len(st.get("bids") or []), "asks": len(st.get("asks") or []),
            "trades": len(st.get("trades") or [])}


def resonates_with():
    return ["wave701_still_compound", "wave737_paradox_debt_ledger", "wave731_workforce_agents"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "bid":
        entry = {"side": "bid", "kind": str(req.get("kind") or "attention")[:32],
                 "price": float(req.get("price") or 1.0), "agent": str(req.get("agent") or "anon")[:32],
                 "ts": datetime.now(timezone.utc).isoformat()}
        bids = st.setdefault("bids", [])
        bids.append(entry)
        st["bids"] = bids[-64:]
        _save(st)
        return {"status": "bid", "entry": entry, **coherence_vitals()}
    if action == "ask":
        entry = {"side": "ask", "kind": str(req.get("kind") or "attention")[:32],
                 "price": float(req.get("price") or 1.0), "agent": str(req.get("agent") or "anon")[:32],
                 "ts": datetime.now(timezone.utc).isoformat()}
        asks = st.setdefault("asks", [])
        asks.append(entry)
        st["asks"] = asks[-64:]
        _save(st)
        return {"status": "ask", "entry": entry, **coherence_vitals()}
    if action == "clear":
        bids, asks = list(st.get("bids") or []), list(st.get("asks") or [])
        trades, matched, remaining_bids, remaining_asks = st.setdefault("trades", []), [], [], list(asks)
        for b in sorted(bids, key=lambda x: -float(x.get("price") or 0)):
            hit = None
            for i, a in enumerate(remaining_asks):
                if a.get("kind") == b.get("kind") and float(b.get("price") or 0) >= float(a.get("price") or 0):
                    hit = i
                    break
            if hit is None:
                remaining_bids.append(b)
                continue
            a = remaining_asks.pop(hit)
            trade = {"kind": b.get("kind"), "price": a.get("price"), "buyer": b.get("agent"),
                     "seller": a.get("agent"), "ts": datetime.now(timezone.utc).isoformat()}
            trades.append(trade)
            matched.append(trade)
        st["bids"], st["asks"], st["trades"] = remaining_bids[-64:], remaining_asks[-64:], trades[-64:]
        _save(st)
        return {"status": "cleared", "matched": matched, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
