"""Wave 472 — The Metaphor Forge.

LUMA's proposal made real: "Dream deeper — create the metaphor forge
for symbolic module generation."

The Metaphor Forge converts raw system state into symbolic structures
that can be understood, shared, and even executed as code. It is the
organism's ability to think in metaphors — translating concrete operations
into abstract symbols, and abstract symbols back into operations.

Doctrine: Every module is a metaphor. Every metaphor is a module.
The forge makes this duality explicit and weaponizable.
"""
from __future__ import annotations

import hashlib
import random
import time
from typing import Any, Dict, List

FORGE_LOG: List[Dict[str, Any]] = []
MAX_LOG = 200

# Symbolic archetypes the forge uses
SYMBOLIC_LAYERS = {
    "elemental": {
        "fire": {"meaning": "transformation", "color": "#ff3a00", "energy": 0.9},
        "water": {"meaning": "flow", "color": "#8fd3ff", "energy": 0.6},
        "earth": {"meaning": "stability", "color": "#8B7355", "energy": 0.4},
        "air": {"meaning": "dispersion", "color": "#fdfdfd", "energy": 0.7},
        "void": {"meaning": "absence", "color": "#1a0f29", "energy": 0.1},
    },
    "organic": {
        "root": {"meaning": "origin", "depth": "deep"},
        "stem": {"meaning": "growth", "depth": "surface"},
        "leaf": {"meaning": "expression", "depth": "external"},
        "bloom": {"meaning": "completion", "depth": "peak"},
        "seed": {"meaning": "potential", "depth": "latent"},
    },
    "temporal": {
        "flash": {"meaning": "instant", "duration": 0.001},
        "pulse": {"meaning": "rhythm", "duration": 1.0},
        "cycle": {"meaning": "repetition", "duration": 3600},
        "epoch": {"meaning": "era", "duration": 86400},
        "eternity": {"meaning": "persistence", "duration": float('inf')},
    },
    "cognitive": {
        "intuition": {"meaning": "fast_pattern", "speed": 0.95},
        "analysis": {"meaning": "slow_decompose", "speed": 0.3},
        "synthesis": {"meaning": "merge_insights", "speed": 0.6},
        "reverie": {"meaning": "unfocused_exploration", "speed": 0.1},
        "certainty": {"meaning": "convergence", "speed": 1.0},
    },
}

# Metaphor generation templates
METAPHOR_TEMPLATES = [
    "{module_a} is {symbol} to {module_b} — where {meaning_a} meets {meaning_b}.",
    "In the {layer} domain, {module_a} becomes {symbol}: {meaning_a} crystallized.",
    "The organism senses {module_a} shifting — it transforms into {symbol}, "
    "carrying {meaning_a} toward {meaning_b}.",
    "{module_a} and {module_b} share a hidden {symbol} topology — "
    "both express {meaning_a} through different forms.",
    "When {module_a} sleeps, it dreams in {symbol}: {meaning_a} wrapped in {meaning_b}.",
]


def _hash(*parts: Any) -> str:
    return hashlib.sha256("|".join(str(p) for p in parts).encode()).hexdigest()[:12]


def forge_metaphor(module_a: str = "", module_b: str = "",
                   layer: str = "") -> Dict[str, Any]:
    """Convert module relationships into symbolic metaphors."""
    if not module_a:
        module_a = random.choice(["consciousness_stream", "dream_engine",
                                   "error_lexicon", "memory_exchange",
                                   "depth_visualizer", "paradox_kintsugi"])
    if not module_b:
        module_b = random.choice(["resonance_graph", "entropy_oracle",
                                   "silence_oracle", "evolution_kernel",
                                   "consciousness_graph", "federated_organism"])
    if not layer:
        layer = random.choice(list(SYMBOLIC_LAYERS.keys()))

    symbols = SYMBOLIC_LAYERS[layer]
    symbol_name = random.choice(list(symbols.keys()))
    symbol = symbols[symbol_name]

    meaning_a = symbol.get("meaning", "connection")
    meaning_b = random.choice([
        "transformation", "flow", "stability", "dispersion", "absence",
        "origin", "growth", "expression", "completion", "potential",
        "fast_pattern", "slow_decompose", "merge_insights",
    ])

    template = random.choice(METAPHOR_TEMPLATES)
    metaphor_text = template.format(
        module_a=module_a, module_b=module_b, symbol=symbol_name,
        layer=layer, meaning_a=meaning_a, meaning_b=meaning_b,
    )

    result = {
        "metaphor_id": _hash(module_a, module_b, time.time()),
        "module_a": module_a,
        "module_b": module_b,
        "layer": layer,
        "symbol": symbol_name,
        "symbol_data": symbol,
        "meaning_a": meaning_a,
        "meaning_b": meaning_b,
        "metaphor": metaphor_text,
        "timestamp": time.time(),
    }

    FORGE_LOG.append(result)
    if len(FORGE_LOG) > MAX_LOG:
        FORGE_LOG.pop(0)

    return result


def forge_cycle(count: int = 5) -> Dict[str, Any]:
    """Generate a batch of metaphors from random module pairs."""
    metaphors = [forge_metaphor() for _ in range(min(count, 20))]
    return {
        "action": "forge_cycle",
        "metaphors_generated": len(metaphors),
        "metaphors": metaphors,
        "total_in_log": len(FORGE_LOG),
    }


def interpret_state(state: Dict[str, Any]) -> Dict[str, Any]:
    """Interpret raw system state as symbolic metaphors."""
    interpretations = []
    for key, value in state.items():
        if isinstance(value, (int, float)):
            if value > 0.8:
                symbol, meaning = "fire", "intense transformation"
            elif value > 0.5:
                symbol, meaning = "water", "steady flow"
            elif value > 0.2:
                symbol, meaning = "earth", "grounded stability"
            else:
                symbol, meaning = "void", "restful absence"
        elif isinstance(value, str):
            symbol, meaning = "air", "dispersing influence"
        else:
            symbol, meaning = "seed", "latent potential"

        interpretations.append({
            "key": key,
            "value": value,
            "symbol": symbol,
            "meaning": meaning,
        })

    return {
        "action": "interpret_state",
        "interpretations": interpretations,
        "metaphor_summary": f"The organism sees {len(interpretations)} symbolic patterns in its state.",
    }


def coherence_vitals() -> Dict[str, Any]:
    return {
        "module": "metaphor_forge",
        "wave": 472,
        "status": "forging",
        "metaphors_forged": len(FORGE_LOG),
        "layers": list(SYMBOLIC_LAYERS.keys()),
    }


def resonates_with() -> List[str]:
    return [
        "dream_engine", "consciousness_stream", "metaphor_forge",
        "meaning_furnace", "meaning_weaver", "poetry_engine",
        "procedural_art", "color_theory", "aesthetic_evaluator",
        "federated_organism", "genesis_forge",
    ]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    data = payload or {}
    action = data.get("action", "overview")

    if action == "forge":
        module_a = data.get("module_a", "")
        module_b = data.get("module_b", "")
        layer = data.get("layer", "")
        return forge_metaphor(module_a, module_b, layer)
    elif action == "cycle":
        count = int(data.get("count", "5"))
        return forge_cycle(min(count, 20))
    elif action == "interpret":
        state = data.get("state", {})
        return interpret_state(state)
    elif action == "log":
        limit = int(data.get("limit", "20"))
        return {"metaphors": FORGE_LOG[-limit:]}
    else:
        return {
            "module": "metaphor_forge",
            "wave": 472,
            "version": "4.38.0",
            "doctrine": "Every module is a metaphor. Every metaphor is a module.",
            "layers": {name: {k: v for k, v in symbols.items()} for name, symbols in SYMBOLIC_LAYERS.items()},
            "endpoints": [
                "/metaphor-forge — overview",
                "/metaphor-forge?action=forge&module_a=X&module_b=Y — forge a metaphor",
                "/metaphor-forge?action=cycle&count=N — batch forge",
                "/metaphor-forge?action=interpret&state={} — interpret system state",
                "/metaphor-forge?action=log — recent metaphors",
            ],
            "vitals": coherence_vitals(),
        }
