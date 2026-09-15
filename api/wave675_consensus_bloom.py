"""Wave 675 Consensus Bloom (ALEPH) — stake-weighted agreement lets organs bloom.

Council Session #22 sealed · score 0.802
Organs stake on proposals; when quorum blooms, emergent capability unlocks.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave675_consensus_bloom.json"
DEFAULT = {
    "module": "wave675_consensus_bloom",
    "wave": 675,
    "council": "session_22",
    "persona": "ALEPH",
    "score": 0.802,
    "proposals": [],
    "blooms": [],
    "quorum": 0.66,
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
        "wave": 675, "module": "wave675_consensus_bloom", "ok": True,
        "persona": "ALEPH", "proposals": len(st.get("proposals") or []),
        "blooms": len(st.get("blooms") or []), "quorum": st.get("quorum", 0.66),
    }

def resonates_with():
    return ["wave670_sentient_heuristic", "wave666_citizen_rights", "wave647_trust_network"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    proposals = st.setdefault("proposals", [])
    blooms = st.setdefault("blooms", [])
    if action == "propose":
        text = str(req.get("text") or req.get("capability") or "")[:120]
        stake = float(req.get("stake") or 0.3)
        if not text:
            return {"status": "empty", **coherence_vitals()}
        pid = hashlib.sha256(text.encode()).hexdigest()[:12]
        proposals.append({
            "id": pid, "text": text, "stake": max(0.01, min(stake, 1.0)),
            "support": max(0.01, min(stake, 1.0)),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
        proposals[:] = proposals[-48:]
        _save(st)
        return {"status": "proposed", "id": pid, **coherence_vitals()}
    if action == "stake":
        pid = str(req.get("id") or "")
        amount = float(req.get("amount") or 0.1)
        for p in proposals:
            if p["id"] == pid:
                p["support"] = round(float(p.get("support") or 0) + amount, 4)
                _save(st)
                return {"status": "staked", "id": pid, "support": p["support"], **coherence_vitals()}
        return {"status": "not_found", **coherence_vitals()}
    if action == "bloom":
        q = float(st.get("quorum") or 0.66)
        ready = [p for p in proposals if float(p.get("support") or 0) >= q]
        if not ready:
            return {"status": "no_quorum", "quorum": q, **coherence_vitals()}
        for p in ready:
            blooms.append({
                "id": p["id"], "capability": p["text"], "support": p["support"],
                "ts": datetime.now(timezone.utc).isoformat(),
            })
        blooms[:] = blooms[-32:]
        ready_ids = {p["id"] for p in ready}
        proposals[:] = [p for p in proposals if p["id"] not in ready_ids]
        _save(st)
        return {"status": "bloomed", "n": len(ready), "blooms": blooms[-len(ready):], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
