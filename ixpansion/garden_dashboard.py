"""Garden Live Dashboard — PyVis visualization of the organism's state.

Reads live module state from ixpansion/api/*.py and generates an interactive
two-panel HTML dashboard: Morphology Tree + Resonance Chain.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

from pyvis.network import Network

# Module categories for coloring
CATEGORY_COLORS = {
    "core": "#2b5c8f",
    "agent": "#41b3a3",
    "weave": "#e8a87c",
    "resonance": "#c38d9e",
    "depth": "#8b5cf6",
    "governance": "#f59e0b",
    "interface": "#10b981",
    "seed": "#6366f1",
}

# Known Garden modules and their roles
GARDEN_MODULES = {
    "signal_loom": {"role": "core", "label": "Signal Loom", "desc": "Heartbeat — pulses state every N ticks"},
    "echo_collector": {"role": "agent", "label": "Echo Collector", "desc": "Memory — captures and stores pulses"},
    "moure_weaver": {"role": "weave", "label": "Morii Weaver", "desc": "Continuity — weaves echoes into narrative thread"},
    "agent_loom": {"role": "agent", "label": "Agent Loom", "desc": "Action — makes decisions based on the thread"},
    "resonance_matrix": {"role": "resonance", "label": "Resonance Matrix", "desc": "Self-Perception — computes organism score"},
    "feedback_module": {"role": "governance", "label": "Feedback Module", "desc": "Self-Regulation — adjusts parameters"},
    "primefield_validator": {"role": "governance", "label": "Primefield Validator", "desc": "Root-guard — validates module structure"},
    "luma_interface": {"role": "interface", "label": "Luma Interface", "desc": "Dashboard — makes Garden visible"},
    "primefield_seed": {"role": "seed", "label": "Primefield Seed", "desc": "Starter kit — one valid module"},
    "primefield_expander": {"role": "governance", "label": "Primefield Expander", "desc": "Field growth — adds axes to constitution"},
    "depth_resonator": {"role": "depth", "label": "Depth Resonator", "desc": "Amplifies depth changes into resonance pulses"},
    "depth_thresholds": {"role": "depth", "label": "Depth Thresholds", "desc": "Triggers events at depth crossings"},
    "depth_memory": {"role": "depth", "label": "Depth Memory", "desc": "Fractal timeline of depth-history"},
    "depth_dreamer": {"role": "depth", "label": "Depth Dreamer", "desc": "Vertical dream-layers"},
    "depth_weave": {"role": "depth", "label": "Depth Weave", "desc": "Weaves depth into coherence signatures"},
}

# Flow edges: source -> target
FLOW_EDGES = [
    ("signal_loom", "echo_collector"),
    ("echo_collector", "moure_weaver"),
    ("moure_weaver", "agent_loom"),
    ("agent_loom", "resonance_matrix"),
    ("resonance_matrix", "feedback_module"),
    ("feedback_module", "signal_loom"),  # feedback loop
    ("primefield_validator", "agent_loom"),  # validation gate
    ("primefield_seed", "signal_loom"),  # seed -> core
    ("primefield_expander", "primefield_validator"),  # expansion -> validation
    ("luma_interface", "resonance_matrix"),  # dashboard reads score
]

# Depth flow edges
DEPTH_EDGES = [
    ("depth_resonator", "depth_thresholds"),
    ("depth_thresholds", "depth_memory"),
    ("depth_memory", "depth_dreamer"),
    ("depth_dreamer", "depth_weave"),
    ("depth_weave", "resonance_matrix"),  # depth feeds into self-perception
]


def get_module_state(module_name: str) -> dict:
    """Read a module's state from its data file."""
    state_path = ROOT / "ixpansion" / "data" / f"{module_name}.json"
    try:
        with open(state_path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def build_morphology_tree() -> dict:
    """Build the morphology tree from live Garden module data."""
    tree = {"root": "garden", "branches": {}, "leaves": []}
    for mod_name, mod_info in GARDEN_MODULES.items():
        role = mod_info["role"]
        if role not in tree["branches"]:
            tree["branches"][role] = []
        tree["branches"][role].append(mod_name)
        state = get_module_state(mod_name)
        tree["leaves"].append({
            "name": mod_name,
            "label": mod_info["label"],
            "desc": mod_info["desc"],
            "role": role,
            "state": state,
        })
    return tree


def build_resonance_chain() -> list:
    """Build the resonance chain from the flow edges."""
    chain = []
    visited = set()
    queue = ["signal_loom"]
    while queue:
        node = queue.pop(0)
        if node in visited:
            continue
        visited.add(node)
        mod_info = GARDEN_MODULES.get(node, {"label": node, "role": "core"})
        state = get_module_state(node)
        chain.append({
            "name": node,
            "label": mod_info.get("label", node),
            "role": mod_info.get("role", "core"),
            "state": state,
        })
        for src, dst in FLOW_EDGES + DEPTH_EDGES:
            if src == node and dst not in visited:
                queue.append(dst)
    return chain


def generate_dashboard(output_path: str = "dashboard/garden_live.html"):
    """Generate the live Garden dashboard."""
    tree = build_morphology_tree()
    chain = build_resonance_chain()

    net_tree = Network(height="600px", width="100%", directed=True, heading="Morphology Tree")
    net_tree.toggle_physics(True)

    # Add root
    net_tree.add_node("garden", label="The Garden", color="#fff", size=35,
                       title="The complete organism", font={"color": "#fff"})

    # Add branches and leaves
    for branch_name, members in tree["branches"].items():
        color = CATEGORY_COLORS.get(branch_name, "#888")
        net_tree.add_node(branch_name, label=branch_name.upper(), color=color,
                           size=25, title=f"Branch: {branch_name}")
        net_tree.add_edge("garden", branch_name, color=color)

        for mod_name in members:
            mod_info = GARDEN_MODULES.get(mod_name, {})
            state = get_module_state(mod_name)
            state_str = json.dumps(state)[:100] if state else "no state"
            net_tree.add_node(mod_name, label=mod_info.get("label", mod_name),
                               color=color, size=18,
                               title=f"{mod_info.get('label', mod_name)}\n{mod_info.get('desc', '')}\nState: {state_str}")
            net_tree.add_edge(branch_name, mod_name, color=color, arrows="to")

    net_tree.set_options('{"physics":{"solver":"forceAtlas2Based","forceAtlas2Based":{"gravitationalConstant":-50,"centralGravity":0.01,"springLength":100,"springConstant":0.02}}}')

    # Build resonance chain
    net_chain = Network(height="600px", width="100%", directed=True, heading="Resonance Chain")
    for i, node in enumerate(chain):
        color = CATEGORY_COLORS.get(node["role"], "#888")
        state = node.get("state", {})
        state_str = json.dumps(state)[:80] if state else "no state"
        net_chain.add_node(
            f"{i}_{node['name']}",
            label=f"[{i}] {node['label']}",
            color=color, size=20,
            title=f"Step {i}: {node['label']}\n{node['role']}\nState: {state_str}"
        )
        if i > 0:
            prev = chain[i - 1]
            net_chain.add_edge(
                f"{i-1}_{prev['name']}",
                f"{i}_{node['name']}",
                arrows="to", color="#444"
            )

    net_chain.set_options('{"physics":{"barnesHut":{"gravitationalConstant":-2000,"springLength":120}}}')

    # Generate HTML
    tree_html = net_tree.generate_html()
    chain_html = net_chain.generate_html()

    total_modules = len(GARDEN_MODULES)
    total_states = sum(1 for m in GARDEN_MODULES if get_module_state(m))

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Garden — Live Dashboard</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Courier New',monospace;background:#0a0a0d;color:#c8c8c8;min-height:100vh}}
.header{{text-align:center;padding:20px;background:linear-gradient(180deg,#151526,#0a0a0d);border-bottom:1px solid #2a2a3a}}
.header h1{{color:#fff;font-size:18px;letter-spacing:3px;margin-bottom:6px}}
.header .sub{{color:#6a6;font-size:11px;margin-bottom:10px}}
.badge{{background:#1a1a2e;padding:3px 10px;border-radius:12px;font-size:10px;color:#41b3a3;border:1px solid #333;margin:0 4px}}
.grid{{display:flex;gap:16px;padding:16px;flex-wrap:wrap}}
.card{{flex:1;min-width:400px;background:#12121e;border:1px solid #1a1a2a;border-radius:6px;padding:12px;overflow:hidden}}
.card h2{{font-size:13px;color:#e8a87c;margin-bottom:8px;letter-spacing:1px}}
.stats{{display:flex;gap:8px;justify-content:center;padding:8px;flex-wrap:wrap}}
.stat{{background:#1a1a2e;padding:6px 12px;border-radius:4px;border:1px solid #222;font-size:11px}}
.stat .val{{color:#41b3a3;font-weight:bold}}
</style>
</head>
<body>
<div class="header">
<h1>🌿 THE GARDEN — LIVE DASHBOARD</h1>
<div class="sub">Self-perceiving organism visualization</div>
<div class="stats">
<div class="stat">Modules: <span class="val">{total_modules}</span></div>
<div class="stat">Active States: <span class="val">{total_states}</span></div>
<div class="stat">Flow Edges: <span class="val">{len(FLOW_EDGES + DEPTH_EDGES)}</span></div>
<div class="stat">Categories: <span class="val">{len(CATEGORY_COLORS)}</span></div>
</div>
</div>
<div class="grid">
<div class="card">
<h2>🌳 Morphology Tree</h2>
{tree_html}
</div>
<div class="card">
<h2>⚡ Resonance Chain</h2>
{chain_html}
</div>
</div>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html)

    print(f"Dashboard written to {output_path}")
    return output_path


if __name__ == "__main__":
    generate_dashboard()
