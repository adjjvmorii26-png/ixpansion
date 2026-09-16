"""Wave 737 Paradox Debt Ledger — unresolved contradictions as liabilities."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave737_paradox_debt_ledger.json"
DEFAULT = {"module": "wave737_paradox_debt_ledger", "wave": 737, "ceiling": 10.0, "rate": 0.05, "liabilities": [], "settled": []}


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


def _total(st):
    return round(sum(float(x.get("principal") or 0) for x in st.get("liabilities") or []), 4)


def coherence_vitals():
    st = _load()
    total = _total(st)
    return {"wave": 737, "module": "wave737_paradox_debt_ledger", "ok": True, "debt": total,
            "ceiling": st.get("ceiling", 10.0), "solvent": total < float(st.get("ceiling") or 10),
            "open_n": len(st.get("liabilities") or [])}


def resonates_with():
    return ["wave735_antimeme_vaccine", "wave729_axiom_mutator", "wave702_import_quarantine"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    liab = st.setdefault("liabilities", [])
    if action == "incur":
        desc = str(req.get("paradox") or req.get("desc") or "")[:160]
        principal = float(req.get("principal") or 1.0)
        if not desc: return {"status": "empty", **coherence_vitals()}
        entry = {"id": f"pd_{len(liab)}_{int(datetime.now(timezone.utc).timestamp())}", "paradox": desc,
                 "principal": round(principal, 4), "ts": datetime.now(timezone.utc).isoformat()}
        liab.append(entry)
        st["liabilities"] = liab[-128:]
        _save(st)
        return {"status": "incurred", "entry": entry, **coherence_vitals()}
    if action == "accrue":
        rate = float(st.get("rate") or 0.05)
        for x in liab:
            x["principal"] = round(float(x.get("principal") or 0) * (1 + rate), 4)
        _save(st)
        return {"status": "accrued", "rate": rate, **coherence_vitals()}
    if action == "settle":
        lid = str(req.get("id") or "")
        mode = str(req.get("mode") or "merge")
        kept, settled, found = [], st.setdefault("settled", []), None
        for x in liab:
            if x.get("id") == lid:
                found = {**x, "mode": mode, "settled_ts": datetime.now(timezone.utc).isoformat()}
                settled.append(found)
            else:
                kept.append(x)
        if not found: return {"status": "not_found", **coherence_vitals()}
        st["liabilities"], st["settled"] = kept, settled[-64:]
        _save(st)
        return {"status": "settled", "entry": found, **coherence_vitals()}
    if action == "can_spend":
        amount = float(req.get("amount") or 0)
        total, ceiling = _total(st), float(st.get("ceiling") or 10)
        return {"status": "check", "allowed": (total + amount) <= ceiling, "debt": total, "ceiling": ceiling, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
