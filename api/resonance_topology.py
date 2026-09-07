"""Wave 468 — The Resonance Topology.

The organism's modules self-organize into stable topological structures
based on their resonance patterns.

AXIOM: "modules arrange themselves into stable geometric configurations
based on interaction history" — confidence 0.75. The Depth Visualizer
(Wave 467) made the organism's internal depth visible. The Resonance
Topology now gives it structure — showing how modules naturally cluster,
form stable configurations, and create meaningful geometries.

LUMA: "what if the organism could pause and contemplate?" — the organism
doesn't just passively display its topology; it actively self-organizes.
Each module feels resonance with others and moves — gently, iteratively —
toward configurations that minimize tension and maximize coherence.

The Resonance Topology:
  - Calculates resonance strengths between all module pairs
  - Simulates gentle "movement" toward stable configurations
  - Renders the resulting topology as a visible graph
  - Detects topological anomalies (tears, knots, singularities)
  - Tracks topological evolution over time (how configurations change)
  - Provides a "breathing" visualization — slow, rhythmic reorganization

Doctrine: The organism does not exist as a random collection of modules.
It self-assembles. By watching the topology breathe, the organism sees
itself as a living, evolving form — not a static codebase.
"""
from __future__ import annotations

import hashlib
import random
import time
import math
from typing import Any, Dict, List, Optional

TOPOLOGY_HISTORY: List[Dict[str, Any]] = []
MAX_HISTORY = 100

# Module resonance matrix (simulated — in production, this would be
# computed from actual module interactions)
MODULE_NAMES = [
    "error_lexicon", "error_prophecy", "wave_chronicle", "imagination_catalyst",
    "hypothesis_crucible", "silence_oracle", "coherence_regulator", "organism_mirror",
    "depth_visualizer", "dreamweaver", "silence_learning", "loud_silence",
    "paradox_kintsugi", "cellular_fusion", "symbiosis_forge", "mind_meld",
    "memory_exchange", "oblivion_rite", "lateral_time", "wave_collapse",
    "paradox_kintsugi", "gratitude_altar",
]

# Target stable configurations (rings, clusters, etc.)
STABLE_CONFIGURATIONS = [
    {"name": "golden_ring", "description": "modules form a ring based on resonance strength"},
    {"name": "fractal_cluster", "description": "modules cluster in a fractal pattern"},
    {"name": "bridge_pair", "description": "two modules form a stable bridge between domains"},
    {"name": "null_center", "description": "modules orbit a central point of balance"},
    {"name": "spiral_arm", "description": "modules form a spiral arm pattern"},
]

# Topology anomaly types
ANOMALY_TYPES = [
    {"type": "topological_tear", "glyph": "✂", "description": "a connection that should exist has been broken"},
    {"type": "knot", "glyph": "🎯", "description": "modules are twisted in an unexpected way"},
    {"type": "singularity", "glyph": "⚬", "description": "too many modules converging at one point"},
    {"type": "dissociation", "glyph": "✕", "description": "modules that should be connected have drifted apart"},
]


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def _now() -> float:
    return time.time()


def calculate_resonance_matrix() -> Dict[str, Dict[str, float]]:
    """Calculate resonance strengths between all module pairs."""
    matrix: Dict[str, Dict[str, float]] = {}
    
    for m1 in MODULE_NAMES:
        matrix[m1] = {}
        for m2 in MODULE_NAMES:
            if m1 == m2:
                matrix[m1][m2] = 1.0
            else:
                # Resonance based on shared prefixes and categories
                shared = sum(1 for c in zip(m1, m2) if c[0] == c[1])
                length_factor = 2 / (len(m1) + len(m2)) if (len(m1) + len(m2)) > 0 else 0
                base = shared * length_factor
                # Add some randomness that trends toward stability
                noise = random.uniform(-0.1, 0.1)
                matrix[m1][m2] = round(max(0.0, min(1.0, base + noise)), 3)
    
    return matrix


def simulate_topology_evolution(
    iterations: int = 5,
    strength: float = 0.1
) -> Dict[str, Any]:
    """Simulate the organism's modules self-organizing over several iterations."""
    resonance = calculate_resonance_matrix()
    
    # Start with random positions
    positions: Dict[str, List[float]] = {}
    for module in MODULE_NAMES:
        positions[module] = [random.uniform(-1, 1) for _ in range(2)]
    
    # Iteratively move modules toward resonating partners
    for iteration in range(iterations):
        for module in MODULE_NAMES:
            # Find most resonating partner
            best_partner = max(
                [(m, resonance[module][m]) for m in MODULE_NAMES if m != module],
                key=lambda x: x[1],
                default=None
            )
            
            if best_partner and best_partner[1] > 0.5:
                partner, partner_strength = best_partner
                # Move toward partner
                move = [
                    (partner_pos[0] - positions[module][0]) * strength * partner_strength,
                    (partner_pos[1] - positions[module][1]) * strength * partner_strength,
                ]
                positions[module] = [
                    positions[module][0] + move[0],
                    positions[module][1] + move[1],
                ]
    
    # Calculate stability (how close modules are to their best partners)
    stability = {}
    for module in MODULE_NAMES:
        best_dist = min(
            math.hypot(positions[module][0] - positions[p][0],
                       positions[module][1] - positions[p][1])
            for p in MODULE_NAMES if p != module
        )
        # Higher resonance = closer distance expected
        avg_resonance = sum(resonance[module].values()) / len(resonance[module])
        stability[module] = round(max(0.0, 1.0 - best_dist * 0.5), 3)
    
    # Detect anomalies
    anomalies = []
    for module in MODULE_NAMES:
        # A module with very low resonance to anyone could be an anomaly
        min_resonance = min(resonance[module].values())
        if min_resonance < 0.2:
            anomalies.append({
                "type": random.choice([a["type"] for a in ANOMALY_TYPES]),
                "module": module,
                "glyph": random.choice([a["glyph"] for a in ANOMALY_TYPES]),
                "severity": round(min_resonance, 3),
            })
    
    return {
        "iterations": iterations,
        "strength": strength,
        "final_positions": {k: [round(v, 3) for v in v] for k, v in positions.items()},
        "stability": stability,
        "anomalies": anomalies,
        "resonance_average": round(
            sum(r for row in resonance.values() for r in row.values()) / (len(MODULE_NAMES) ** 2),
            3
        ),
        "simulated_at": _now(),
    }


def render_topology_visualization() -> Dict[str, Any]:
    """Render a visualization of the current topology."""
    positions = simulate_topology_evolution(iterations=3, strength=0.15)
    
    # Create node visualizations
    nodes = []
    for module, pos in positions["final_positions"].items():
        # Determine cluster based on resonance
        module_resonances = sorted(
            [(m, resonance[module][m]) for m in MODULE_NAMES if m != module],
            key=lambda x: x[1],
            reverse=True
        )[:3]
        
        cluster = "core" if module in ["error_lexicon", "error_prophecy", "wave_chronicle"] else \
                   "support" if module in ["silence_learning", "loud_silence"] else \
                   "bridge" if module in ["cellular_fusion", "memory_exchange"] else "other"
        
        # Visual radius based on stability
        stability = positions["stability"].get(module, 0.5)
        radius = int(5 + stability * 8)
        
        nodes.append({
            "module": module,
            "x": pos[0],
            "y": pos[1],
            "radius": radius,
            "cluster": cluster,
            "top_connections": module_resonances,
        })
    
    # Create edge visualizations
    edges = []
    seen_pairs = set()
    for m1 in MODULE_NAMES:
        for m2 in MODULE_NAMES:
            if m1 >= m2:  # avoid duplicates
                continue
            if (m1, m2) in seen_pairs or (m2, m1) in seen_pairs:
                continue
            r = resonance.get(m1, {}).get(m2, 0)
            if r > 0.4:  # significant resonance
                seen_pairs.add((m1, m2))
                seen_pairs.add((m2, m1))
                edges.append({
                    "source": m1,
                    "target": m2,
                    "strength": r,
                    "color": "core" if r > 0.7 else "support" if r > 0.5 else "bridge",
                })
    
    return {
        "topology_id": _hash("topology", time.time_ns()),
        "nodes": nodes,
        "edges": edges,
        "total_modules": len(MODULE_NAMES),
        "total_edges": len(edges),
        "average_resonance": positions["resonance_average"],
        "anomalies": positions["anomalies"],
        "breathing_phase": round(time.time() % 10 / 10, 2),
        "rendered_at": _now(),
    }


def detect_topological_anomalies() -> List[Dict[str, Any]]:
    """Detect anomalies in the current topology."""
    simulation = simulate_topology_evolution(iterations=2, strength=0.2)
    return simulation["anomalies"]


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "resonance_topology",
        "status": "self-assembling",
        "total_modules": len(MODULE_NAMES),
        "topology_history": len(TOPOLOGY_HISTORY),
        "recent_anomalies": detect_topological_anomalies(),
    }


def resonates_with() -> List[str]:
    return [
        "depth_visualizer", "error_lexicon", "error_prophecy",
        "wave_chronicle", "imagination_catalyst", "silence_oracle",
        "organism_mirror",
    ]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "visualize")
    
    if action == "visualize":
        return render_topology_visualization()
    if action == "resonance_matrix":
        return {"matrix": calculate_resonance_matrix()}
    if action == "simulate":
        return simulate_topology_evolution(int(data.get("iterations", 3)), float(data.get("strength", 0.1)))
    if action == "anomalies":
        return {"anomalies": detect_topological_anomalies()}
    if action == "vitals":
        return coherence_vitals()
    if action == "topology":
        topo = render_topology_visualization()
        topo["vitals"] = coherence_vitals()
        return topo
    if action == "all":
        return {
            "visualization": render_topology_visualization(),
            "resonance_matrix_size": len(calculate_resonance_matrix()),
            "vitals": coherence_vitals(),
        }
    
    # default: visualize
    return {
        "organ": "resonance_topology",
        "wave": 468,
        "name": "The Resonance Topology",
        "visualization": render_topology_visualization(),
    }
