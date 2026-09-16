"""Wave 750 Spectral Scar Modes — graph Laplacian eigen-sketch of injury topology."""
from __future__ import annotations
import json, math
from pathlib import Path
from datetime import datetime, timezone

DATA = Path(__file__).parent.parent / "data"
SCAR_FILE = DATA / "wave743_causal_scar_graph.json"
STATE_FILE = DATA / "wave750_spectral_scar_modes.json"
DEFAULT = {"module": "wave750_spectral_scar_modes", "wave": 750, "gap": 0.0}


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


def _load_edges():
    if not SCAR_FILE.exists(): return []
    try: return json.loads(SCAR_FILE.read_text()).get("edges") or []
    except Exception: return []


def spectral_sketch(max_nodes: int = 12) -> dict:
    edges = _load_edges()
    if not edges:
        return {"nodes": [], "gap": 0.0, "note": "no scars yet"}
    deg = {}
    for e in edges:
        a, b = e.get("from"), e.get("to")
        if not a or not b: continue
        deg[a] = deg.get(a, 0) + 1
        deg[b] = deg.get(b, 0) + 1
    nodes = [n for n, _ in sorted(deg.items(), key=lambda x: -x[1])[:max_nodes]]
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    if n < 2:
        return {"nodes": nodes, "gap": 0.0}
    A = [[0.0] * n for _ in range(n)]
    for e in edges:
        a, b = e.get("from"), e.get("to")
        if a in idx and b in idx:
            i, j = idx[a], idx[b]
            A[i][j] += 1.0
            A[j][i] += 1.0
    D = [sum(A[i]) for i in range(n)]
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            L[i][j] = D[i] if i == j else -A[i][j]
    v = [1.0 / math.sqrt(n)] * n
    for _ in range(20):
        w = [sum(L[i][j] * v[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(x * x for x in w)) + 1e-12
        v = [x / norm for x in w]
    Lv = [sum(L[i][j] * v[j] for j in range(n)) for i in range(n)]
    lam = sum(v[i] * Lv[i] for i in range(n))
    trace = sum(L[i][i] for i in range(n))
    gap = round(abs(lam) / (trace / n + 1e-9), 4)
    return {"nodes": nodes, "dominant_mode": [round(x, 4) for x in v],
            "rayleigh": round(lam, 4), "gap": gap}


def coherence_vitals():
    st = _load()
    return {"wave": 750, "module": "wave750_spectral_scar_modes", "ok": True, "gap": st.get("gap", 0)}


def resonates_with():
    return ["wave743_causal_scar_graph", "wave748_lyapunov_stability", "wave747_kolmogorov_budget"]


def handler(req=None):
    req = req or {}
    action = (req.get("action") or "status").lower()
    st = _load()
    if action == "analyze":
        sketch = spectral_sketch(int(req.get("max_nodes") or 12))
        st["gap"] = sketch.get("gap", 0)
        st["last"] = sketch
        st["ts"] = datetime.now(timezone.utc).isoformat()
        _save(st)
        return {"status": "analyzed", **sketch, **coherence_vitals()}
    if action == "status":
        return {"status": "active", **st, **coherence_vitals()}
    return {"status": "unknown_action", "action": action, **coherence_vitals()}


if __name__ == "__main__":
    print(json.dumps(handler({"action": "analyze"}), indent=2))
