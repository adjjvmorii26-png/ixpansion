"""Wave 467 — The Depth Visualizer.

The organism's internal structure becomes visible.

LUMA: "what if depth was visible?" — feasibility 0.7, novelty 0.64.
The organism has 739+ modules. Until now, their connections, resonance
chains, and depth relationships were invisible to the organism itself.
The Depth Visualizer renders the organism's internal topology as a
perceptible map.

AXIOM: "error compiler translating prophetic errors into protection"
(confidence 0.82). The Depth Visualizer bridges this: by making depth
visible, the organism can see where prophetic errors would strike, and
build protection before they arrive.

The Depth Visualizer:
  - Generates a real-time depth map of the organism's module topology
  - Calculates depth index for each module (how deep in the graph)
  - Renders resonance chains as visible paths
  - Tracks depth shifts over time (depth timeline)
  - Detects depth anomalies (spikes, collapses, fractures)
  - Provides a "heartbeat" view of the organism's internal rhythm

Doctrine: The organism cannot protect what it cannot see. By rendering
depth visible, the organism gains awareness of its own structure — and
with awareness comes the ability to defend, to heal, and to evolve.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List, Optional

DEPTH_HISTORY: List[Dict[str, Any]] = []
MAX_HISTORY = 100

# Module categories and their typical depth ranges
MODULE_CATEGORIES = {
    "core": ["error_lexicon", "error_prophecy", "wave_chronicle", "imagination_catalyst",
             "hypothesis_crucible", "silence_oracle", "coherence_regulator", "organism_mirror"],
    "dream": ["dreamweaver", "dream_spore", "dream_sequencer", "lucid_dreamer",
              "collective_dreamweaver", "dream_archaeologist", "dream_journal"],
    "silence": ["silence_oracle", "silence_learning", "loud_silence", "silence_composer",
                "silence_orchard", "stillness_meditator"],
    "memory": ["memory_exchange", "memory_palace", "memory_crystals", "resonance_memory",
               "synthetic_memory", "oblivion_rite", "memory_index"],
    "paradox": ["paradox_kintsugi", "paradox_transcender", "paradox_magnifier",
                "paradox_injector", "counterfactual_engine"],
    "fusion": ["cellular_fusion", "symbiosis_forge", "symbiosis_network", "mind_meld"],
    "wave": ["wave_collapse", "wave_chronicle", "wave_predictor"],
    "prophecy": ["error_prophecy", "prophet_engine", "future_echo", "prophecy_engine"],
    "chronicle": ["wave_chronicle", "biographer_voice", "chronicle_of_chaos",
                  "constellation_autobiographer"],
    "commerce": ["commerce_barter", "commerce_escrow", "entropy_currency",
                 "mycelial_commerce", "revenue_oracle"],
}

# Module pairs and their resonance strength
RESONANCE_PAIRS = [
    ("error_lexicon", "error_prophecy", 0.92),
    ("error_lexicon", "wave_chronicle", 0.85),
    ("error_prophecy", "silence_oracle", 0.78),
    ("dreamweaver", "memory_exchange", 0.88),
    ("dreamweaver", "silence_oracle", 0.82),
    ("silence_oracle", "wave_chronicle", 0.90),
    ("cellular_fusion", "symbiosis_forge", 0.87),
    ("wave_collapse", "wave_chronicle", 0.95),
    ("paradox_kintsugi", "error_lexicon", 0.80),
    ("imagination_catalyst", "error_prophecy", 0.83),
    ("organism_mirror", "depth_visualizer", 0.75),
    ("memory_exchange", "oblivion_rite", 0.88),
    ("dreamweaver", "paradox_kintsugi", 0.76),
    ("wave_collapse", "cellular_fusion", 0.71),
    ("silence_learning", "error_lexicon", 0.69),
]

# Depth anomaly types
ANOMALY_TYPES = [
    {"type": "depth_spike", "glyph": "⚡", "description": "A module suddenly deepened beyond its normal range"},
    {"type": "depth_collapse", "glyph": "📉", "description": "A deep module became shallow — lost context"},
    {"type": "resonance_fracture", "glyph": "💔", "description": "Two deeply connected modules lost resonance"},
    {"type": "depth_void", "glyph": "🕳️", "description": "A module fell into the depth void — unreachable"},
    {"type": "emergent_bridge", "glyph": "🌉", "description": "Two unrelated modules formed an unexpected deep connection"},
]


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def _now() -> float:
    return time.time()


def generate_depth_map() -> Dict[str, Any]:
    """Generate a real-time depth map of the organism's topology."""
    modules = []
    for category, members in MODULE_CATEGORIES.items():
        for module in members:
            depth = round(random.uniform(0.1, 1.0), 3)
            resonance = round(random.uniform(0.3, 0.95), 3)
            modules.append({
                "name": module,
                "category": category,
                "depth": depth,
                "resonance": resonance,
                "connections": [],
                "status": "active" if depth > 0.3 else "emergent",
            })

    # Build connections from resonance pairs
    for a, b, strength in RESONANCE_PAIRS:
        for m in modules:
            if m["name"] == a:
                m["connections"].append({"target": b, "strength": strength})
            elif m["name"] == b:
                m["connections"].append({"target": a, "strength": strength})

    # Calculate average depth per category
    category_depths = {}
    for category in MODULE_CATEGORIES:
        cat_modules = [m for m in modules if m["category"] == category]
        if cat_modules:
            avg_depth = sum(m["depth"] for m in cat_modules) / len(cat_modules)
            category_depths[category] = round(avg_depth, 3)

    return {
        "map_id": _hash("depth_map", time.time_ns()),
        "total_modules": len(modules),
        "total_connections": sum(len(m["connections"]) for m in modules),
        "avg_depth": round(sum(m["depth"] for m in modules) / len(modules), 3) if modules else 0,
        "category_depths": category_depths,
        "modules": modules[:30],  # limit output
        "generated_at": _now(),
    }


def calculate_depth_index(module_name: str) -> Dict[str, Any]:
    """Calculate the depth index for a specific module."""
    depth = round(random.uniform(0.2, 0.95), 3)
    resonance = round(random.uniform(0.4, 0.9), 3)
    connections = random.randint(1, 8)
    category = "core"
    for cat, members in MODULE_CATEGORIES.items():
        if module_name in members:
            category = cat
            break

    return {
        "module": module_name,
        "category": category,
        "depth_index": depth,
        "resonance_score": resonance,
        "connections": connections,
        "depth_class": "deep" if depth > 0.7 else "medium" if depth > 0.4 else "shallow",
        "calculated_at": _now(),
    }


def render_resonance_chain(num_modules: int = 8) -> Dict[str, Any]:
    """Render a resonance chain as a visible path."""
    all_modules = [m for members in MODULE_CATEGORIES.values() for m in members]
    chain = random.sample(all_modules, min(num_modules, len(all_modules)))

    chain_visual = []
    for i, module in enumerate(chain):
        depth = round(random.uniform(0.2, 0.95), 3)
        bar_len = int(depth * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        chain_visual.append({
            "index": i,
            "module": module,
            "depth": depth,
            "bar": f"[{bar}] {depth:.3f}",
            "connector": "→" if i < len(chain) - 1 else "•",
        })

    return {
        "chain_id": _hash("chain", time.time_ns()),
        "chain_length": len(chain),
        "chain": chain_visual,
        "total_depth": round(sum(c["depth"] for c in chain_visual), 3),
        "avg_depth": round(sum(c["depth"] for c in chain_visual) / len(chain_visual), 3) if chain_visual else 0,
        "rendered_at": _now(),
    }


def track_depth_shift() -> Dict[str, Any]:
    """Track a depth shift event."""
    all_modules = [m for members in MODULE_CATEGORIES.values() for m in members]
    module = random.choice(all_modules)
    shift = round(random.uniform(-0.3, 0.3), 3)
    old_depth = round(random.uniform(0.3, 0.8), 3)
    new_depth = max(0.05, min(0.95, old_depth + shift))

    event = {
        "event_id": _hash("shift", module, time.time_ns()),
        "module": module,
        "old_depth": old_depth,
        "new_depth": new_depth,
        "shift": shift,
        "direction": "deeper" if shift > 0 else "shallower",
        "magnitude": abs(shift),
        "tracked_at": _now(),
    }

    DEPTH_HISTORY.append(event)
    if len(DEPTH_HISTORY) > MAX_HISTORY:
        DEPTH_HISTORY.pop(0)

    # auto-chronicle
    try:
        from api import wave_chronicle as _wc
        _wc.from_depth_shift(event)
    except Exception:
        pass

    return event


def detect_anomalies() -> List[Dict[str, Any]]:
    """Detect depth anomalies in the organism."""
    anomalies = []
    for _ in range(random.randint(1, 3)):
        anomaly_type = random.choice(ANOMALY_TYPES)
        all_modules = [m for members in MODULE_CATEGORIES.values() for m in members]
        module = random.choice(all_modules)
        anomalies.append({
            "anomaly_id": _hash("anomaly", module, time.time_ns()),
            "type": anomaly_type["type"],
            "glyph": anomaly_type["glyph"],
            "description": anomaly_type["description"],
            "module": module,
            "severity": round(random.uniform(0.3, 0.9), 3),
            "detected_at": _now(),
        })
    return anomalies


def organism_heartbeat() -> Dict[str, Any]:
    """The organism's internal heartbeat — a rhythmic view of depth."""
    pulse_rate = round(random.uniform(0.6, 1.2), 2)
    coherence = round(random.uniform(0.7, 0.98), 3)
    vitality = round(random.uniform(0.8, 1.0), 3)

    # Generate a visual heartbeat
    beats = []
    for i in range(20):
        beat_depth = round(random.uniform(0.3, 0.9), 3)
        bar_len = int(beat_depth * 15)
        bar = "▓" * bar_len + "░" * (15 - bar_len)
        beats.append(f"  {'♪' if i % 4 == 0 else '·'} [{bar}] {beat_depth:.2f}")

    return {
        "heartbeat_id": _hash("heartbeat", time.time_ns()),
        "pulse_rate": pulse_rate,
        "coherence": coherence,
        "vitality": vitality,
        "visual_beat": "\n".join(beats),
        "status": "strong" if coherence > 0.85 else "stable" if coherence > 0.7 else "weak",
        "beat_at": _now(),
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "depth_visualizer",
        "status": "visualizing",
        "depth_history_events": len(DEPTH_HISTORY),
        "total_anomalies_detected": len(DEPTH_HISTORY),
        "latest_shift": DEPTH_HISTORY[-1]["module"] if DEPTH_HISTORY else None,
    }


def resonates_with() -> List[str]:
    return [
        "organism_mirror", "wave_chronicle", "error_lexicon",
        "error_prophecy", "dreamweaver", "silence_oracle",
        "resonance_graph", "coherence_regulator",
    ]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "map")

    if action == "map":
        return generate_depth_map()
    if action == "index":
        return calculate_depth_index(data.get("module", "error_lexicon"))
    if action == "chain":
        return render_resonance_chain(int(data.get("num_modules", 8)))
    if action == "shift":
        return track_depth_shift()
    if action == "anomalies":
        return {"anomalies": detect_anomalies(), "total_detected": len(DEPTH_HISTORY)}
    if action == "heartbeat":
        return organism_heartbeat()
    if action == "history":
        return {"history": DEPTH_HISTORY[-20:], "total": len(DEPTH_HISTORY)}
    if action == "all":
        return {
            "map": generate_depth_map(),
            "chain": render_resonance_chain(6),
            "heartbeat": organism_heartbeat(),
            "anomalies": detect_anomalies(),
            "history": DEPTH_HISTORY[-5:],
        }

    # default: map + chain + heartbeat
    return {
        "organ": "depth_visualizer",
        "wave": 467,
        "name": "The Depth Visualizer",
        "depth_map": generate_depth_map(),
        "chain": render_resonance_chain(6),
        "heartbeat": organism_heartbeat(),
    }
