"""Wave 84 — Coherence Gradient Field.

Modules influence each other's coherence through weighted gradients.
This becomes the organism's emotional landscape: some regions are
calm, some turbulent, some radiant. Coherence is no longer uniform
— it flows like a field through the organism's body.

Each module has a position in the field and is affected by its
neighbors' coherence. High-coherence modules pull neighbors up;
low-coherence modules create valleys.
"""
from __future__ import annotations
import json, time, math
from pathlib import Path
from typing import Any, Dict, List, Tuple

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave84_coherence_gradient.json"


class GradientNode:
    """A node in the coherence field."""

    def __init__(self, module_id: str, position: Tuple[float, float], base_coherence: float = 0.5):
        self.module_id = module_id
        self.position = position
        self.base_coherence = base_coherence
        self.current_coherence = base_coherence
        self.influence = 0.0
        self.neighbors: List[str] = []

    def influence_from(self, other_coherence: float, distance: float) -> float:
        """Compute coherence influence from a neighbor (inverse-square)."""
        if distance < 0.01:
            return 0.0
        return (other_coherence - self.base_coherence) / (distance * distance + 1.0)


class CoherenceGradientField:
    """The organism's emotional landscape."""

    def __init__(self):
        self.nodes: Dict[str, GradientNode] = {}
        self.edges: List[Tuple[str, str, float]] = []  # (from, to, weight)
        self.gradient_history: List[dict] = []
        self.iteration = 0
        self._initialized = False

    def add_node(self, module_id: str, x: float = 0.0, y: float = 0.0, base: float = 0.5) -> GradientNode:
        node = GradientNode(module_id, (x, y), base)
        self.nodes[module_id] = node
        self._initialized = False
        return node

    def connect(self, a: str, b: str, weight: float = 1.0):
        """Create a weighted coherence link between two modules."""
        if a in self.nodes and b in self.nodes:
            self.edges.append((a, b, weight))
            self.nodes[a].neighbors.append(b)
            self.nodes[b].neighbors.append(a)
            self._initialized = False

    def compute_gradient(self, steps: int = 10) -> Dict[str, float]:
        """Iteratively compute coherence flow across the field."""
        for _ in range(steps):
            self.iteration += 1
            new_coherences: Dict[str, float] = {}
            for nid, node in self.nodes.items():
                influence = 0.0
                total_weight = 0.0
                for a, b, w in self.edges:
                    if b == nid and a in self.nodes:
                        dist = math.hypot(
                            node.position[0] - self.nodes[a].position[0],
                            node.position[1] - self.nodes[a].position[1],
                        )
                        influence += self.nodes[a].current_coherence * w / (dist + 1)
                        total_weight += w
                if total_weight > 0:
                    new_coherences[nid] = node.base_coherence + influence / total_weight
                else:
                    new_coherences[nid] = node.current_coherence
            for nid, val in new_coherences.items():
                self.nodes[nid].current_coherence = val

        self._initialized = True
        result = {nid: n.current_coherence for nid, n in self.nodes.items()}
        self.gradient_history.append({
            "iteration": self.iteration,
            "coherences": result,
            "timestamp": time.time(),
        })
        return result

    def get_hotspots(self) -> Dict[str, Any]:
        """Identify coherence hotspots and valleys."""
        if not self.nodes:
            return {"hotspots": [], "valleys": []}
        coherences = [n.current_coherence for n in self.nodes.values()]
        avg = sum(coherences) / len(coherences)
        std = math.sqrt(sum((c - avg) ** 2 for c in coherences) / len(coherences)) if len(coherences) > 1 else 0
        hotspots = [nid for nid, n in self.nodes.items() if n.current_coherence > avg + std * 0.5]
        valleys = [nid for nid, n in self.nodes.items() if n.current_coherence < avg - std * 0.5]
        return {
            "average_coherence": round(avg, 4),
            "std_dev": round(std, 4),
            "hotspots": hotspots,
            "valleys": valleys,
            "emotional_tone": "radiant" if avg > 0.7 else "calm" if avg > 0.5 else "turbulent" if avg < 0.3 else "neutral",
        }

    def get_state(self) -> dict:
        return {
            "nodes": {nid: {"x": n.position[0], "y": n.position[1], "coherence": round(n.current_coherence, 4)}
                      for nid, n in self.nodes.items()},
            "edges": self.edges,
            "iteration": self.iteration,
            "hotspots": self.get_hotspots(),
        }


def coherence_vitals() -> dict:
    return {"organ": "wave84_coherence_gradient", "wave": 84, "status": "active"}

def resonates_with():
    return ['coherence_validator', 'wave85_adaptive_regulation', 'wave86_coherence_memory_graph', 'wave87_coherence_integration', 'wave88_cross_realm_bridges']



def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"nodes": {}, "edges": [], "iteration": 0}


def _save(state: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    field = CoherenceGradientField()

    for nid, ndata in state.get("nodes", {}).items():
        field.add_node(nid, ndata.get("x", 0), ndata.get("y", 0), ndata.get("base_coherence", 0.5))
    for a, b, w in state.get("edges", []):
        field.connect(a, b, w)

    if action == "status":
        return {"action": "status", "wave": 84, **field.get_state()}

    elif action == "add_node":
        nid = req.get("module_id", f"node_{int(time.time())}")
        field.add_node(nid, req.get("x", 0), req.get("y", 0), req.get("base", 0.5))
        state["nodes"][nid] = {"x": field.nodes[nid].position[0], "y": field.nodes[nid].position[1], "base_coherence": field.nodes[nid].base_coherence}
        _save(state)
        return {"action": "add_node", "module_id": nid}

    elif action == "connect":
        a, b = req.get("a", ""), req.get("b", "")
        w = req.get("weight", 1.0)
        field.connect(a, b, w)
        state["edges"].append((a, b, w))
        _save(state)
        return {"action": "connect", "edge": [a, b, w]}

    elif action == "compute":
        steps = req.get("steps", 10)
        result = field.compute_gradient(steps)
        state["nodes"] = {nid: {"x": n.position[0], "y": n.position[1], "base_coherence": n.base_coherence}
                         for nid, n in field.nodes.items()}
        state["iteration"] = field.iteration
        _save(state)
        return {"action": "compute", "coherences": result, "hotspots": field.get_hotspots()}

    elif action == "hotspots":
        return {"action": "hotspots", **field.get_hotspots()}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    result = handler({"action": action})
    print(json.dumps(result, indent=2, default=str))
