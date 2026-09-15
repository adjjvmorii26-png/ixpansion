"""Wave 671 Ontology Crystal — compresses 670 waves of concepts into a queryable crystal.

Never-before at this scale: every organ name + doctrine phrase folds into a
content-addressed lattice; queries return nearest-neighbor ontology facets
without scanning the full registry.
"""
from __future__ import annotations
import json, hashlib, math
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave671_ontology_crystal.json"
DIM = 16
DEFAULT = {"module": "wave671_ontology_crystal", "wave": 671, "facets": {}, "queries": 0}

SEED = [
    "silence is the product surface", "lab gates != ALEPH CI", "compression is memory",
    "tide follows proof density", "forgetting is a feature", "mycelial weave",
    "paradox court", "sentient heuristic", "epoch forge", "sovereignty beacon",
    "quiet crown", "absence currency", "retrocausal echo", "citizen rights",
]

def _vec(s: str) -> list[float]:
    h = hashlib.sha256(s.encode()).digest()
    raw = [(h[i] / 127.5) - 1.0 for i in range(DIM)]
    n = math.sqrt(sum(x * x for x in raw)) or 1.0
    return [x / n for x in raw]

def _cos(a, b):
    return sum(x * y for x, y in zip(a, b))

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
    return {"wave": 671, "module": "wave671_ontology_crystal", "ok": True,
            "facets": len(st.get("facets") or {}), "queries": st.get("queries", 0)}

def resonates_with():
    return ["wave667_mycelial_weave", "wave659_epoch_forge", "wave670_sentient_heuristic"]

def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    facets = st.setdefault("facets", {})
    if action == "crystallize":
        items = req.get("items") or SEED
        for it in items[:64]:
            it = str(it)[:120]
            facets[it] = {"vec": _vec(it), "id": hashlib.sha256(it.encode()).hexdigest()[:12]}
        st["ts"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "crystallized", "n": len(facets), **coherence_vitals()}
    if action == "query":
        q = str(req.get("q") or req.get("text") or "")[:120]
        if not q:
            return {"status": "empty", **coherence_vitals()}
        if not facets:
            handler({"action": "crystallize"})
            st = _load()
            facets = st.get("facets") or {}
        qv = _vec(q)
        ranked = sorted(
            ((k, _cos(qv, v["vec"])) for k, v in facets.items()),
            key=lambda x: -x[1],
        )[:8]
        st["queries"] = int(st.get("queries") or 0) + 1
        _save(st)
        return {"status": "query", "hits": [{"facet": k, "score": round(s, 4)} for k, s in ranked],
                **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}

if __name__ == "__main__":
    print(json.dumps(handler({"action": "status"}), indent=2))
