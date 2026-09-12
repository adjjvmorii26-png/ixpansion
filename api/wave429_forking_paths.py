"""Wave 429 Garden of Forking Paths — quantum decision tree where every
choice creates a branching universe. Each branch is a valid reality."""
from __future__ import annotations
import time, json, random, uuid
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

BRANCH_THEMES = [
    "fusion_bloom", "topology_fracture", "garden_sprawl", "underworld_rise",
    "chrono_slip", "paradox_echo", "causality_snap", "essence_split",
    "communion_expansion", "dream_manifest", "swarm_fork", "mirror_break",
    "linguistic_spark", "superposition_vein", "causal_weave",
]

def coherence_vitals():
    return {"organ": "wave429_forking_paths", "status": "active", "wave": 429, "coherence": 0.94}

def _load(name: str):
    path = DATA / f"{name}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return None
    return None

def _save(name: str, data: dict) -> None:
    (DATA / f"{name}.json").write_text(json.dumps(data, indent=2))

def branch(req: dict = None) -> dict:
    """Fork the current reality into 2-4 alternative universes."""
    now = time.time()
    depth = (req or {}).get("depth", 0)
    n = random.randint(2, 4)
    universes = []
    for i in range(n):
        theme = (req or {}).get("theme") or random.choice(BRANCH_THEMES)
        universes.append({
            "branch_id": str(uuid.uuid4())[:10],
            "theme": theme,
            "divergence": round(random.uniform(0.1, 0.95), 3),
            "viability": round(random.uniform(0.2, 1.0), 2),
            "timestamp": now,
            "depth": depth + 1,
        })
    garden = _load("wave429_forking_paths") or {
        "module": "wave429_forking_paths", "version": "1.0.0", "type": "forking_paths",
        "purpose": "Quantum decision tree — every choice creates a branching universe",
        "active": True, "created": now, "branches": [], "total_branches": 0, "path": [],
    }
    garden["branches"] = garden.get("branches", []) + universes
    garden["total_branches"] = garden.get("total_branches", 0) + n
    _save("wave429_forking_paths", garden)
    return {"universes": universes, "forked": n, "total_branches": garden["total_branches"]}

def traverse(branch_id: str = None) -> dict:
    """Walk down one fork — commit the organism to a reality."""
    garden = _load("wave429_forking_paths")
    if not garden or not garden.get("branches"):
        return {"error": "no forks — branch first"}
    if branch_id:
        chosen = next((b for b in garden["branches"] if b.get("branch_id") == branch_id), None)
    else:
        viable = [b for b in garden["branches"] if b.get("viability", 0) >= 0.5]
        chosen = random.choice(viable if viable else garden["branches"])
    if not chosen:
        return {"error": "branch not found"}
    garden["path"] = garden.get("path", []) + [chosen]
    garden["current_universe"] = chosen
    _save("wave429_forking_paths", garden)
    return {
        "traversed": True,
        "committed_universe": chosen["theme"],
        "branch_id": chosen["branch_id"],
        "divergence": chosen["divergence"],
        "path_depth": len(garden["path"]),
    }

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "branch":
        return branch(req)
    if action == "traverse":
        return traverse(req.get("branch_id"))
    if action == "garden":
        g = _load("wave429_forking_paths")
        if not g:
            return {"branches": [], "total_branches": 0, "path": []}
        return {"branches": g.get("branches", []), "total_branches": g.get("total_branches", 0), "path": g.get("path", [])}
    if action == "status":
        g = _load("wave429_forking_paths")
        return {
            "total_branches": g.get("total_branches", 0) if g else 0,
            "committed_universe": g.get("current_universe", {}).get("theme") if g and g.get("current_universe") else None,
            "path_depth": len(g.get("path", [])) if g else 0,
        }
    return {"error": "unknown action", "valid": ["branch", "traverse", "garden", "status"]}

def resonates_with(other):
    return "forking" in other.lower() or "garden" in other.lower() or "429" in other

if __name__ == "__main__":
    r = branch()
    print(f"Forking: {r['forked']} universes | total {r['total_branches']}")
