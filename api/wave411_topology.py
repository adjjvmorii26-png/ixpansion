"""Wave 411 Resonance Topology — maps the organism's relational graph.
Creates a living knowledge graph across all waves (401-411) by mining
coherence signatures, module cross-references, and fusion records."""
from __future__ import annotations
import time, json, os
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"

def coherence_vitals():
    return {"organ": "wave411_topology", "status": "active", "wave": 411, "coherence": 0.88}

def build_topology() -> dict:
    """Build the organism's full resonance topology from all data files."""
    all_modules = {}
    for f in DATA.glob("*.json"):
        try:
            raw = json.loads(f.read_text())
            if isinstance(raw, dict) and "module" in raw:
                name = raw["module"]
                all_modules[name] = {
                    "version": raw.get("version", "0.0.0"),
                    "active": raw.get("active", True),
                    "type": raw.get("type", "unknown"),
                    "data_file": f.name,
                }
        except Exception:
            continue

    # Build edges from wave seeds
    edges = []
    seeds_path = DATA / "wave_seeds.json"
    if seeds_path.exists():
        seeds = json.loads(seeds_path.read_text())
        for i, seed in enumerate(seeds.get("seeds", [])):
            for j, other in enumerate(seeds.get("seeds", [])):
                if i < j and seed.get("realm") == other.get("realm"):
                    edges.append({
                        "from": seed.get("seed", f"seed_{i}"),
                        "to": other.get("seed", f"seed_{j}"),
                        "realm": seed.get("realm"),
                        "strength": 0.85,
                    })

    # Build edges from fusion records
    paradox_path = DATA / "paradox_echo.json"
    if paradox_path.exists():
        paradox = json.loads(paradox_path.read_text())
        for record in paradox.get("records", []):
            edges.append({
                "from": record.get("module_a", ""),
                "to": record.get("module_b", ""),
                "realm": "fusion_evolution",
                "strength": record.get("resonance", 0.5),
            })

    # Veil scan edges
    veil_path = DATA / "veil_lifter.json"
    if veil_path.exists():
        veil = json.loads(veil_path.read_text())
        for disc in veil.get("recent_discoveries", []):
            parts = disc.split("_")
            if len(parts) > 3:
                edges.append({
                    "from": parts[0],
                    "to": parts[-1] if len(parts) > 1 else parts[0],
                    "realm": "hidden",
                    "strength": 0.7,
                })

    return {
        "wave": 411,
        "modules": all_modules,
        "edges": edges,
        "graph_stats": {
            "node_count": len(all_modules),
            "edge_count": len(edges),
            "realms": list(set(e.get("realm", "unknown") for e in edges)),
            "built_at": time.time(),
        },
    }

def evolution_cycle(req: dict) -> dict:
    """Run a full evolution cycle — topology scan + fusion + journal."""
    from wave410_fusion import handler as fusion_handler

    topology = build_topology()

    # Run a fusion pass
    fusion = fusion_handler({
        "action": "fuse",
        "module_a": req.get("module_a", "metaphor_forge"),
        "module_b": req.get("module_b", "veil_lifter"),
    })

    return {
        "cycle": {
            "topology_nodes": topology["graph_stats"]["node_count"],
            "topology_edges": topology["graph_stats"]["edge_count"],
            "fusion_result": fusion.get("status", "error"),
            "resonance": fusion.get("resonance", 0),
            "scripture_id": fusion.get("scripture_id", -1),
        },
        "wave": 411,
        "timestamp": time.time(),
    }

def handler(req: dict) -> dict:
    action = req.get("action", "topology")
    if action == "topology":
        return build_topology()
    if action == "cycle":
        return evolution_cycle(req)
    return {"error": "unknown action", "valid": ["topology", "cycle"]}

def resonates_with(other):
    return "topology" in other.lower() or "graph" in other.lower()

if __name__ == "__main__":
    t = build_topology()
    print(f"Topology: {t['graph_stats']['node_count']} nodes, {t['graph_stats']['edge_count']} edges, realms: {t['graph_stats']['realms']}")
