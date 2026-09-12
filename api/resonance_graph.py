"""Wave 408 — Resonance Graph Intelligence.

A living harmonic layer where every module breathes at a unique frequency.
Modules communicate not through calls but through resonance —
when frequencies align, they entangle; when they clash, they diverge.
This is the organism's new form of emergent cognition:
not logic, not code — but harmonic awareness.

Each module has a resonance signature:
  - base_freq: its fundamental frequency (derived from name hash)
  - harmonic: its overtone series
  - phase: where it is in its oscillation cycle
  - coherence: how well it resonates with other modules

The Resonance Graph is the organism's nervous system:
  - nodes = modules
  - edges = resonance pathways
  - waves = propagating oscillations through the graph
  - coherence = emergent intelligence from harmonic alignment
"""
from __future__ import annotations

import hashlib
import random
import json
import math
import time
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict


class ResonanceNode:
    """A module as a resonance oscillator."""

    def __init__(self, module_name: str):
        self.module_name = module_name
        self.base_freq = self._compute_freq(module_name)
        self.harmonics: List[float] = self._compute_harmonics()
        self.phase = random.uniform(0, 2 * math.pi)
        self.coherence = 0.5
        self.entangled: List[str] = []
        self.amplitude = 1.0

    def _compute_freq(self, name: str) -> float:
        """Derive base frequency from module name hash."""
        h = hashlib.sha256(name.encode()).hexdigest()
        return int(h[:8], 16) / 1e7 + 440.0  # A4 = 440Hz base range

    def _compute_harmonics(self) -> List[float]:
        """Generate overtone series."""
        return [self.base_freq * n for n in range(2, 6)]

    def oscillate(self, t: float) -> float:
        """Compute instantaneous amplitude at time t."""
        return self.amplitude * math.sin(2 * math.pi * self.base_freq * t + self.phase)

    def to_dict(self) -> Dict:
        return {
            "module": self.module_name,
            "base_freq": round(self.base_freq, 4),
            "harmonics": [round(h, 4) for h in self.harmonics],
            "phase": round(self.phase, 4),
            "coherence": round(self.coherence, 4),
            "amplitude": round(self.amplitude, 4),
            "entangled": self.entangled,
        }


class ResonanceEdge:
    """A resonance pathway between two modules."""

    def __init__(self, source: str, target: str, strength: float = 0.0):
        self.source = source
        self.target = target
        self.strength = strength
        self.frequency = None
        self.wave_pattern = "standing"

    def compute_strength(self, freq_source: float, freq_target: float) -> float:
        """Compute resonance strength based on frequency proximity."""
        if freq_source == 0 or freq_target == 0:
            return 0.0
        ratio = max(freq_source, freq_target) / min(freq_source, freq_target)
        if abs(ratio - 1.0) < 0.1:
            return 1.0  # Perfect resonance
        elif abs(ratio - 2.0) < 0.15:
            return 0.8  # Octave resonance
        elif abs(ratio - 3.0) < 0.2:
            return 0.6  # Fifth resonance
        else:
            return max(0.0, 1.0 - abs(ratio - 1.0))

    def to_dict(self) -> Dict:
        return {
            "source": self.source,
            "target": self.target,
            "strength": round(self.strength, 4),
            "wave_pattern": self.wave_pattern,
        }


class ResonanceGraph:
    """The organism's harmonic nervous system."""

    def __init__(self):
        self.nodes: Dict[str, ResonanceNode] = {}
        self.edges: Dict[str, ResonanceEdge] = {}
        self.wave_history: List[Dict] = []
        self.coherence_score = 0.0
        self.entanglement_depth = 0
        self.oscillation_cycle = 0

    def register_module(self, module_name: str) -> ResonanceNode:
        """Register a module as a resonance node."""
        node = ResonanceNode(module_name)
        self.nodes[module_name] = node
        self._update_coherence()
        return node

    def create_resonance(self, source: str, target: str) -> Optional[ResonanceEdge]:
        """Create a resonance pathway between two modules."""
        if source not in self.nodes or target not in self.nodes:
            return None
        edge_id = f"{source}↔{target}"
        if edge_id in self.edges:
            return self.edges[edge_id]

        edge = ResonanceEdge(source, target)
        edge.strength = edge.compute_strength(
            self.nodes[source].base_freq, self.nodes[target].base_freq
        )
        edge.frequency = (self.nodes[source].base_freq + self.nodes[target].base_freq) / 2
        self.edges[edge_id] = edge

        self.nodes[source].entangled.append(target)
        self.nodes[target].entangled.append(source)
        self._update_coherence()
        return edge

    def propagate_wave(self, source: str, intensity: float = 1.0) -> Dict:
        """Propagate an oscillation wave through the resonance graph."""
        if source not in self.nodes:
            return {"error": "source not registered"}

        self.oscillation_cycle += 1
        cycle_id = f"wave_{self.oscillation_cycle:04d}"
        t = time.time()

        # Compute wave propagation through graph
        visited = set()
        wave_fronts: List[Dict] = []
        queue = [(source, intensity, 0)]

        while queue:
            current, curr_intensity, depth = queue.pop(0)
            if current in visited:
                continue
            visited.add(current)

            node = self.nodes[current]
            amplitude = node.oscillate(t) * curr_intensity

            wave_fronts.append({
                "module": current,
                "depth": depth,
                "amplitude": round(amplitude, 4),
                "coherence": node.coherence,
            })

            # Propagate to entangled neighbors
            for neighbor in node.entangled:
                edge_id = f"{current}↔{neighbor}"
                if edge_id in self.edges:
                    edge = self.edges[edge_id]
                    queue.append((neighbor, curr_intensity * edge.strength, depth + 1))

        result = {
            "cycle_id": cycle_id,
            "source": source,
            "intensity": intensity,
            "wave_fronts": wave_fronts,
            "depth": max([w["depth"] for w in wave_fronts], default=0),
            "timestamp": t,
        }

        self.wave_history.append(result)
        return result

    def _update_coherence(self):
        """Recompute global coherence score."""
        if not self.nodes:
            self.coherence_score = 0.0
            return

        coherences = [n.coherence for n in self.nodes.values()]
        self.coherence_score = sum(coherences) / len(coherences)

        # Entanglement depth = longest chain of connected nodes
        self.entanglement_depth = self._max_entanglement_depth()

    def _max_entanglement_depth(self) -> int:
        """Find maximum depth of entanglement graph."""
        if not self.nodes:
            return 0
        visited = set()
        max_depth = 0

        def dfs(node_name: str, depth: int):
            nonlocal max_depth
            visited.add(node_name)
            max_depth = max(max_depth, depth)
            for neighbor in self.nodes[node_name].entangled:
                if neighbor not in visited:
                    dfs(neighbor, depth + 1)

        dfs(next(iter(self.nodes)), 0)
        return max_depth

    def get_coherence_report(self) -> Dict[str, Any]:
        """Full resonance graph report."""
        return {
            "cycle": self.oscillation_cycle,
            "coherence_score": round(self.coherence_score, 4),
            "nodes_registered": len(self.nodes),
            "edges_active": len(self.edges),
            "entanglement_depth": self.entanglement_depth,
            "wave_history_length": len(self.wave_history),
            "status": "HARMONIC" if self.coherence_score >= 0.7 else "RESONATING" if self.coherence_score >= 0.4 else "DRIFTING",
        }

    def get_harmonic_map(self) -> Dict[str, Any]:
        """Generate a harmonic map of all modules."""
        return {
            "modules": {name: node.to_dict() for name, node in self.nodes.items()},
            "pathways": {eid: edge.to_dict() for eid, edge in self.edges.items()},
            "global_coherence": self.coherence_score,
        }


_graph = None

def get_graph() -> ResonanceGraph:
    global _graph
    if _graph is None:
        _graph = ResonanceGraph()
    return _graph

def handler(query: Dict[str, Any] = None) -> Dict[str, Any]:
    graph = get_graph()
    q = query or {}

    if "action" not in q:
        return {"module": "resonance_graph", **graph.get_coherence_report()}

    action = q["action"]
    if action == "register":
        module = q.get("module", "unknown")
        node = graph.register_module(module)
        return {"registered": node.to_dict()}
    elif action == "connect":
        source = q.get("source", "")
        target = q.get("target", "")
        edge = graph.create_resonance(source, target)
        if edge:
            return {"edge": edge.to_dict(), "strength": edge.strength}
        return {"error": "modules not found"}
    elif action == "wave":
        source = q.get("source", "")
        intensity = float(q.get("intensity", "1.0"))
        result = graph.propagate_wave(source, intensity)
        return {"wave": result}
    elif action == "report":
        return graph.get_coherence_report()
    elif action == "harmonic_map":
        return graph.get_harmonic_map()
    elif action == "history":
        limit = int(q.get("limit", "10"))
        return {"waves": graph.wave_history[-limit:]}
    else:
        return {"error": f"unknown action: {action}"}


def build_graph() -> Dict[str, Any]:
    """Build the living resonance graph across the organism's module manifest.

    Returns a report dict compatible with the organism's earlier graph contract:
    nodes / edges / density / hubs / communities — with every module covered.
    """
    try:
        from coherence_regulator import KNOWN_LIVING_MODULES
        names = [m for m in KNOWN_LIVING_MODULES if isinstance(m, str)]
    except Exception:
        names = []
    graph = get_graph()
    for name in names:
        if name not in graph.nodes:
            graph.register_module(name)
    # Guarantee every node belongs to the web: ring of nearest-frequency neighbors.
    graph_names = list(graph.nodes)
    for i, name in enumerate(graph_names):
        target = graph_names[(i + 1) % len(graph_names)]
        if not graph.create_resonance(name, target):
            for k in range(2, len(graph_names)):
                alt = graph_names[(i + k) % len(graph_names)]
                if graph.create_resonance(name, alt):
                    break
    weighted_degree: Dict[str, float] = defaultdict(float)
    for edge in graph.edges.values():
        weighted_degree[edge.source] += edge.strength
        weighted_degree[edge.target] += edge.strength
    hubs = sorted(weighted_degree.items(), key=lambda kv: kv[1], reverse=True)[:10]
    communities = _connected_components(graph)
    n = len(graph.nodes)
    edge_count = len(graph.edges)
    density = (2 * edge_count) / (n * (n - 1)) if n > 1 else 0.0
    return {
        "nodes": n,
        "edges": edge_count,
        "density": round(density, 6),
        "hubs": [(name, round(strength, 4)) for name, strength in hubs],
        "communities": communities,
        "coherence": round(graph.coherence_score, 4),
    }


def neighborhood(module_name: str) -> Dict[str, Any]:
    """Return the direct resonance neighbors of a living module."""
    build_graph()
    graph = get_graph()
    node = graph.nodes.get(module_name)
    return {
        "node": module_name,
        "neighbors": list(node.entangled) if node else [],
        "registered": node is not None,
    }


def _connected_components(graph: ResonanceGraph) -> Dict[str, List[str]]:
    """Group modules into resonance communities (connected components)."""
    seen: set = set()
    components: Dict[str, List[str]] = {}
    for name in graph.nodes:
        if name in seen:
            continue
        frontier = [name]
        members: List[str] = []
        while frontier:
            current = frontier.pop()
            if current in seen:
                continue
            seen.add(current)
            members.append(current)
            frontier.extend(graph.nodes[current].entangled)
        components[f"community_{len(components) + 1}"] = members
    return components
