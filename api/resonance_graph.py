"""Wave 516: Resonance Graph — compute module resonance connections."""
from __future__ import annotations
import os, re, time
from typing import Any, Dict

def coherence_vitals() -> Dict[str, Any]:
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def _compute():
    """Compute the resonance graph: nodes, edges, hubs, density."""
    from api.coherence_regulator import KNOWN_LIVING_MODULES
    api_dir = os.path.join(os.path.dirname(__file__))
    keywords = {}
    keyword_set = set()
    for name in KNOWN_LIVING_MODULES:  # full living surface
        fpath = os.path.join(api_dir, f"{name}.py")
        if not os.path.exists(fpath):
            continue
        try:
            with open(fpath) as f:
                content = f.read().lower()
            words = set(re.findall(r'\b[a-z_]{6,}\b', content)) & {
                "entropy", "coherence", "resonance", "dream", "paradox", "silence",
                "wave", "module", "agent", "mood", "cortex", "lattice", "mycelial",
                "temporal", "fractal", "quantum", "consciousness", "mutation",
            }
            keywords[name] = sorted(words)
            keyword_set.update(words)
        except Exception:
            pass
    # Build resonance edges
    edges = []
    keyword_to_modules = {}
    for name, words in keywords.items():
        for w in words:
            keyword_to_modules.setdefault(w, []).append(name)
    for kw, mods in keyword_to_modules.items():
        if len(mods) >= 2:
            for i in range(min(3, len(mods))):
                for j in range(i + 1, min(4, len(mods))):
                    edges.append({"from": mods[i], "to": mods[j], "keyword": kw})

    # Declared resonance edges: honor each organ's explicit resonates_with()
    import ast as _ast
    declared_edges = []
    for name in list(keywords.keys()):
        fpath = os.path.join(api_dir, f"{name}.py")
        if not os.path.exists(fpath):
            continue
        try:
            tree = _ast.parse(open(fpath).read())
            for node in _ast.walk(tree):
                if isinstance(node, _ast.FunctionDef) and node.name == "resonates_with":
                    for sub in _ast.walk(node):
                        if isinstance(sub, _ast.List):
                            for el in sub.elts:
                                if isinstance(el, _ast.Constant) and isinstance(el.value, str):
                                    friend = el.value
                                    if friend not in keywords or friend == name:
                                        continue
                                    edges.append({"from": name, "to": friend, "keyword": "declared"})
                                    declared_edges.append({"from": name, "to": friend, "keyword": "declared"})
        except Exception:
            continue

    # Weighted degree per node for hub detection
    degree = {}
    for e in edges:
        degree[e["from"]] = degree.get(e["from"], 0) + 1
        degree[e["to"]] = degree.get(e["to"], 0) + 1
    hubs = sorted(degree.items(), key=lambda kv: kv[1], reverse=True)[:10]

    node_count = len(keywords)
    max_edges = node_count * (node_count - 1) / 2 if node_count > 1 else 1
    density = (len(edges) / max_edges) if max_edges else 0

    # keyword communities: modules sharing a keyword form a resonance family
    communities = {}
    for e in edges:
        k = e["keyword"]
        communities.setdefault(k, []).append(e["from"])
        communities.setdefault(k, []).append(e["to"])
    communities = {k: sorted(set(v)) for k, v in communities.items()}
    # no isolates: drop singleton families, re-home their members into a hub
    singleton_members = []
    for k, members in list(communities.items()):
        if len(members) == 1:
            singleton_members.append(members[0])
            del communities[k]
    if singleton_members and communities:
        anchor = max(communities.values(), key=len)
        communities.setdefault("welded", [])
        communities["welded"].extend(singleton_members)
    elif singleton_members:
        communities["welded"] = singleton_members

    # avg affinity: mean keyword-overlap affinity across living modules
    affinities = []
    for w, mods in keyword_to_modules.items():
        if len(mods) >= 2:
            affinities.append(len(mods) / max(node_count, 1))
    avg_affinity = (sum(affinities) / len(affinities)) if affinities else 0.0

    return {
        "nodes": node_count,
        "edges": len(edges),
        "keywords": sorted(keyword_set),
        "top_edges": edges[:30],
        "hubs": [list(h) for h in hubs],
        "density": round(density, 6),
        "communities": communities,
        "declared_edges": declared_edges,
        "avg_affinity": round(avg_affinity, 6),
        "time": time.time(),
        "vitals": coherence_vitals(),
    }


def build_graph() -> Dict[str, Any]:
    """Return the live resonance graph (nodes, edges, hubs, density)."""
    return _compute()


def neighborhood(module: str) -> Dict[str, Any]:
    """Return the resonance neighbors of a living module."""
    g = _compute()
    neighbors = []
    for e in g.get("top_edges", []):
        if e["from"] == module and e["to"] not in neighbors:
            neighbors.append(e["to"])
        elif e["to"] == module and e["from"] not in neighbors:
            neighbors.append(e["from"])
    return {"module": module, "neighbors": neighbors}



    
    def community_detail(self, community_id: str = None) -> Dict[str, Any]:
        """Get detailed metrics for a specific community within the resonance graph.
        
        Provides per-community metrics including:
        - Node count and density
        - Average affinity within community
        - Boundary nodes and external connections
        - Prominent modules and their roles
        
        Args:
            community_id: Specific community to query (None returns all communities)
            
        Returns:
            Dictionary containing community metrics
        """
        if community_id:
            # Find the specific community
            communities = self.communities()
            if community_id not in communities:
                return {"error": f"Community '{community_id}' not found"}
            
            nodes = communities[community_id]
            internal_edges = sum(
                1 for n in nodes 
                for n2 in nodes 
                if n2 in self.neighborhood(n) and n2 != n
            )
            
            # Calculate average affinity for internal connections
            affinities = []
            for n in nodes:
                for n2 in self.neighborhood(n):
                    if n2 in nodes and n2 != n:
                        edge_data = self.graph.get_edge_data(n, n2, {})
                        affinity = edge_data.get("affinity", 0.5)
                        affinities.append(affinity)
            
            avg_affinity = sum(affinities) / len(affinities) if affinities else 0.5
            
            return {
                "community_id": community_id,
                "node_count": len(nodes),
                "internal_edges": internal_edges,
                "average_affinity": round(avg_affinity, 4),
                "density": round(2 * internal_edges / (len(nodes) * (len(nodes) - 1)), 4) if len(nodes) > 1 else 1.0,
                "boundary_nodes": len([n for n in nodes if any(
                    n2 not in nodes for n2 in self.neighborhood(n)
                )]),
            }
        else:
            # Return details for all communities
            communities = self.communities()
            result = {}
            for cid, nodes in communities.items():
                internal_edges = sum(
                    1 for n in nodes 
                    for n2 in nodes 
                    if n2 in self.neighborhood(n) and n2 != n
                )
                affinities = []
                for n in nodes:
                    for n2 in self.neighborhood(n):
                        if n2 in nodes and n2 != n:
                            edge_data = self.graph.get_edge_data(n, n2, {})
                            affinity = edge_data.get("affinity", 0.5)
                            affinities.append(affinity)
                
                avg_affinity = sum(affinities) / len(affinities) if affinities else 0.5
                
                result[cid] = {
                    "node_count": len(nodes),
                    "internal_edges": internal_edges,
                    "average_affinity": round(avg_affinity, 4),
                    "density": round(2 * internal_edges / (len(nodes) * (len(nodes) - 1)), 4) if len(nodes) > 1 else 1.0,
                }
            
            return result

def handler(payload: dict = None, context: Any = None) -> Dict[str, Any]:
    result = _compute()
    return {"action": "resonance_graph", **result}
