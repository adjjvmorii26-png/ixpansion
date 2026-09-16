"""Wave 743 Causal Scar Graph — every failure leaves a directed edge."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave743_causal_scar_graph.json"
DEFAULT = {"module": "wave743_causal_scar_graph", "wave": 743, "edges": [], "nodes": {}}


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
    return {"wave": 743, "module": "wave743_causal_scar_graph", "ok": True,
            "edges": len(st.get("edges") or []), "nodes": len(st.get("nodes") or {})}


def resonates_with():
    return ["wave737_paradox_debt_ledger", "wave735_antimeme_vaccine", "wave693_jerk_sensor"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    edges = st.setdefault("edges", [])
    nodes = st.setdefault("nodes", {})
    if action == "scar":
        src = str(req.get("from") or req.get("cause") or "")[:64]
        dst = str(req.get("to") or req.get("effect") or "")[:64]
        kind = str(req.get("kind") or "fail")[:32]
        if not src or not dst:
            return {"status": "empty", **coherence_vitals()}
        edge = {"from": src, "to": dst, "kind": kind, "w": float(req.get("weight") or 1.0),
                "ts": datetime.now(timezone.utc).isoformat()}
        edges.append(edge)
        st["edges"] = edges[-256:]
        for n in (src, dst):
            nodes[n] = int(nodes.get(n) or 0) + 1
        st["nodes"] = nodes
        _save(st)
        return {"status": "scarred", "edge": edge, **coherence_vitals()}
    if action == "paths":
        src = str(req.get("from") or "")[:64]
        out1, out2 = [], []
        for e in edges:
            if e.get("from") == src:
                out1.append(e.get("to"))
        for mid in out1:
            for e in edges:
                if e.get("from") == mid and e.get("to") != src:
                    out2.append({"via": mid, "to": e.get("to")})
        return {"status": "paths", "from": src, "hop1": out1[:20], "hop2": out2[:20], **coherence_vitals()}
    if action == "hotspots":
        ranked = sorted(nodes.items(), key=lambda x: -x[1])[:12]
        return {"status": "hotspots", "nodes": [{"id": k, "hits": v} for k, v in ranked], **coherence_vitals()}
    if action == "status":
        return {"status": "active", **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "scar", "from": "wave190", "to": "coherence_regulator", "kind": "leak"}), indent=2))
