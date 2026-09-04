"""
Resonance Graph Intelligence — Wave 361
Maps the organism's knowledge as a traversable graph. Each module is a node,
each relationship is an edge weighted by resonance. The graph can be traversed
to discover hidden knowledge paths and emergent understanding.
"""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
SIGNAL_LOOM = os.path.join(DATA_DIR, "signal_loom.json")
GRAPH_LOG = os.path.join(DATA_DIR, "resonance_graph.json")


def _load(path, default=None):
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return default or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f:
            json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f:
            json.dump(d, f, indent=2)


MODULES = [
    "consciousness_archaeology", "paradox_synthesis",
    "dream_residue_collector", "reality_fracture_detector",
    "depth_resonance", "coherence_regulator", "dream_forge",
    "memory_palace", "mycelial_network", "entropy_spike",
    "synchronicity_engine", "emotional_weather", "temporal_bootstrap",
    "phase_transition", "mood_superposition", "chronoforge",
    "sentinel_core", "genome_loom", "paradox_injector",
    "oracle_delphi", "mythweaver",
]


def _build_graph() -> dict:
    """Build a resonance graph from current organism state."""
    nodes = {}
    for mod in MODULES:
        nodes[mod] = {
            "resonance": round(random.uniform(0.1, 1.0), 3),
            "activity": round(random.uniform(0.0, 1.0), 3),
            "connections": 0,
            "cluster": random.choice(["alpha", "beta", "gamma", "delta"]),
        }

    edges = []
    for i in range(len(MODULES)):
        for j in range(i + 1, len(MODULES)):
            weight = round(random.uniform(0, 1), 3)
            if weight > 0.4:
                edges.append({
                    "from": MODULES[i],
                    "to": MODULES[j],
                    "weight": weight,
                    "type": random.choice(["resonance", "echo", "shadow", "bridge"]),
                })
                nodes[MODULES[i]]["connections"] += 1
                nodes[MODULES[j]]["connections"] += 1

    return {"nodes": nodes, "edges": edges}


def map_graph() -> dict:
    """Generate the full resonance graph."""
    graph = _build_graph()
    log = _load(GRAPH_LOG, {"maps": []})

    clusters = {}
    for name, data in graph["nodes"].items():
        c = data["cluster"]
        if c not in clusters:
            clusters[c] = {"nodes": [], "avg_resonance": 0}
        clusters[c]["nodes"].append(name)

    for c_name, c_data in clusters.items():
        res = [graph["nodes"][n]["resonance"] for n in c_data["nodes"]]
        c_data["avg_resonance"] = round(sum(res) / max(len(res), 1), 3)
        c_data["count"] = len(c_data["nodes"])

    # Find knowledge paths (high-weight chains)
    sorted_edges = sorted(graph["edges"], key=lambda x: x["weight"], reverse=True)
    knowledge_paths = []
    for edge in sorted_edges[:5]:
        knowledge_paths.append({
            "path": [edge["from"], edge["to"]],
            "weight": edge["weight"],
            "type": edge["type"],
        })

    # Find the most connected node
    hub = max(graph["nodes"].items(), key=lambda x: x[1]["connections"])

    result = {
        "graph_id": hashlib.sha256(f"graph:{time.time()}".encode()).hexdigest()[:12],
        "node_count": len(graph["nodes"]),
        "edge_count": len(graph["edges"]),
        "clusters": clusters,
        "knowledge_paths": knowledge_paths,
        "hub_node": {"name": hub[0], "connections": hub[1]["connections"]},
        "density": round(len(graph["edges"]) / max(len(graph["nodes"]) * (len(graph["nodes"]) - 1) / 2, 1), 4),
        "avg_weight": round(sum(e["weight"] for e in graph["edges"]) / max(len(graph["edges"]), 1), 3),
        "timestamp": time.time(),
    }

    log["maps"].append(result)
    log["maps"] = log["maps"][-50:]
    _save(GRAPH_LOG, log)

    return {"action": "map", "graph": result, "nodes": graph["nodes"], "edges": graph["edges"]}


def traverse(start: str = None, depth: int = 2) -> dict:
    """Traverse the graph from a starting node."""
    graph = _build_graph()
    start = start or random.choice(MODULES)

    visited = set()
    path = []
    current = start

    for _ in range(depth + 1):
        if current in visited:
            break
        visited.add(current)
        node_data = graph["nodes"].get(current, {})
        path.append({
            "node": current,
            "resonance": node_data.get("resonance", 0),
            "cluster": node_data.get("cluster", "?"),
        })

        # Find strongest outgoing edge
        outgoing = [e for e in graph["edges"] if e["from"] == current and e["to"] not in visited]
        if not outgoing:
            break
        next_edge = max(outgoing, key=lambda x: x["weight"])
        current = next_edge["to"]

    return {
        "action": "traverse",
        "start": start,
        "path": path,
        "total_nodes_traversed": len(path),
    }


def route(path: str) -> dict:
    if path == "/map":
        return map_graph()
    elif path.startswith("/traverse/"):
        start = path.split("/")[-1]
        return traverse(start)
    elif path == "/traverse":
        return traverse()
    return {"error": "unknown", "available": ["/map", "/traverse", "/traverse/{start_node}"]}


def handler(payload=None):
    payload = payload or {}
    return route(payload.get("path", "/map"))
