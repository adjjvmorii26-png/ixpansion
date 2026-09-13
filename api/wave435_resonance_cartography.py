"""Wave 435 Resonance Cartography — living atlas of energetic topology between modules."""
from __future__ import annotations
import json, hashlib, math
from pathlib import Path
from datetime import datetime, timezone
DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave435_resonance_cartography.json"
DIM = 16
DEFAULT = {"module": "wave435_resonance_cartography", "wave": 435, "nodes": [], "edges": [], "surveys": 0}
def _vec(name: str):
    h = hashlib.sha256(name.encode()).digest()
    raw = [(h[i] / 127.5) - 1.0 for i in range(DIM)]
    n = math.sqrt(sum(x * x for x in raw)) or 1.0
    return [x / n for x in raw]
def _cos(a, b):
    return sum(x * y for x, y in zip(a, b))
def _load():
    if STATE_FILE.exists():
        try: return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError: pass
    return dict(DEFAULT)
def _save(state):
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")
def coherence_vitals():
    st = _load()
    return {"wave": 435, "module": "wave435_resonance_cartography", "ok": True, "nodes": len(st.get("nodes") or []), "edges": len(st.get("edges") or []), "surveys": st.get("surveys", 0)}
def resonates_with():
    return ["wave431_homestead", "wave432_mycelial_index", "wave428_resonance_chamber"]
def survey(names, threshold=0.15):
    names = [str(n)[:80] for n in names if n][:40]
    vectors = {n: _vec(n) for n in names}
    edges = []
    for i, a in enumerate(names):
        for b in names[i+1:]:
            c = _cos(vectors[a], vectors[b])
            if c >= threshold:
                edges.append({"a": a, "b": b, "energy": round(c, 4)})
    edges.sort(key=lambda e: -e["energy"])
    return {"nodes": names, "edges": edges[:80], "threshold": threshold}
def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "survey":
        raw = req.get("modules") or req.get("names") or []
        if isinstance(raw, str):
            raw = [x.strip() for x in raw.split(",") if x.strip()]
        if not raw:
            raw = ["wave431_homestead", "wave432_mycelial_index", "wave435_resonance_cartography", "lab_smoke", "doctrine_diff"]
        thr = float(req.get("threshold") or 0.15)
        carto = survey(list(raw), threshold=thr)
        st["nodes"], st["edges"] = carto["nodes"], carto["edges"]
        st["surveys"] = int(st.get("surveys") or 0) + 1
        st["last_survey"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "surveyed", **carto, **coherence_vitals()}
    if action == "atlas":
        return {"status": "atlas", "nodes": st.get("nodes") or [], "edges": st.get("edges") or [], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}
