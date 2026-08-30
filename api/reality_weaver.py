"""Reality Weaver — generates emergent realities from text seeds.

Describe a seed concept and the Reality Weaver generates a complete
micro-reality with physics, inhabitants, emergent behaviors, and
prophecy. It's not a simulation — it's a generative architecture.

Usage:
  POST /api/reality_weaver
  {"seed": "underwater civilization that communicates through bioluminescence"}
  {"seed": "a city where gravity flows sideways", "factions": 3}

  GET /api/reality_weaver?seed=clockwork+forest
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from typing import Any, Dict, List


ELEMENTS = ["fire", "water", "earth", "air", "void", "light", "shadow",
            "time", "entropy", "crystal", "moss", "rust", "glass", "silk"]
FORCE_TYPES = ["gravity", "magnetism", "pressure", "tension", "resonance",
               "diffusion", "turbulence", "oscillation"]
ARCHITECTURE_TYPES = ["lattice", "helix", "tree", "web", "sphere",
                       "wave", "crystal", "foam", "fractal", "membrane"]
BEHAVIOR_TYPES = ["symbiotic", "competitive", "parasitic", "mutualistic",
                   "neutral", "emergent", "cyclic", "chaotic"]

种子_HASH_CACHE: Dict[str, int] = {}


def _seed_hash(text: str) -> int:
    h = hashlib.sha256(text.encode()).hexdigest()[:8]
    return int(h, 16)


def _words_from_seed(seed: str) -> List[str]:
    """Extract meaningful words from a seed phrase."""
    stopwords = {"the", "a", "an", "in", "on", "at", "of", "to", "for",
                 "and", "or", "but", "that", "this", "with", "is", "are"}
    return [w for w in re.findall(r"[a-z]+", seed.lower())
            if len(w) > 2 and w not in stopwords]


def generate_reality(seed: str, num_factions: int = 2,
                     time_horizon: int = 100) -> Dict[str, Any]:
    """Generate a complete micro-reality from a text seed."""
    words = _words_from_seed(seed)
    rng = random.Random(_seed_hash(seed))
    rng_state = rng.getstate()

    # --- Physics Layer ---
    primary_element = rng.choice(ELEMENTS)
    secondary_element = rng.choice([e for e in ELEMENTS if e != primary_element])
    force = rng.choice(FORCE_TYPES)
    architecture = rng.choice(ARCHITECTURE_TYPES)
    base_laws = {
        "primary_element": primary_element,
        "secondary_element": secondary_element,
        "dominant_force": force,
        "structure": architecture,
        "entropy_direction": rng.choice(["increasing", "decreasing", "oscillating"]),
        "time_flow": rng.choice(["linear", "circular", "branching", "sporadic"]),
    }

    # --- Inhabitants ---
    factions = []
    for i in range(num_factions):
        behavior = rng.choice(BEHAVIOR_TYPES)
        power = round(rng.uniform(0.1, 0.9), 3)
        factions.append({
            "name": f"{primary_element.title()}_{'glyph' if i % 2 else 'weave'}_{i + 1}",
            "dominant_behavior": behavior,
            "power": power,
            "resource_need": rng.choice(ELEMENTS),
            "threat": rng.choice(ELEMENTS),
            "reproduction_rate": round(rng.uniform(0.1, 2.0), 2),
        })

    # --- Interaction Matrix ---
    interaction_matrix = []
    for i in range(num_factions):
        for j in range(i + 1, num_factions):
            b1, b2 = factions[i]["dominant_behavior"], factions[j]["dominant_behavior"]
            synergy = 0.0
            if b1 == "symbiotic" or b2 == "symbiotic":
                synergy = rng.uniform(0.3, 0.8)
            elif b1 == "competitive" and b2 == "competitive":
                synergy = -rng.uniform(0.3, 0.8)
            else:
                synergy = rng.uniform(-0.3, 0.3)
            interaction_matrix.append({
                "factions": [factions[i]["name"], factions[j]["name"]],
                "synergy": round(synergy, 3),
                "predicted_outcome": "cooperation" if synergy > 0 else "conflict",
            })

    # --- Prophecy ---
    dominant_faction = max(factions, key=lambda f: f["power"])
    volatile_interaction = min(interaction_matrix, key=lambda m: m["synergy"])
    prophecies = [
        f"The {dominant_faction['name']} faction will rise to dominance through {dominant_faction['dominant_behavior']} behavior",
        f"A {volatile_interaction['predicted_outcome']} between {volatile_interaction['factions'][0]} and {volatile_interaction['factions'][1]} will reshape the {architecture}",
        f"The {secondary_element} crisis will force a new alliance between all factions",
        f"The {primary_element} element will undergo a phase transition, fundamentally altering the {force} landscape",
    ]

    # --- Time Simulation ---
    timeline = []
    pop = [rng.randint(100, 1000) for _ in range(num_factions)]
    for step in range(time_horizon):
        for i in range(num_factions):
            growth = rng.gauss(0.01, 0.05)
            pop[i] = max(1, int(pop[i] * (1 + growth)))
        timeline.append({
            "step": step,
            "populations": {factions[i]["name"]: pop[i] for i in range(num_factions)},
        })

    # --- World State ---
    initial_pop = sum(timeline[0]["populations"][factions[i]["name"]]
                    for i in range(num_factions)) if timeline else 0
    final_pop = sum(timeline[-1]["populations"][factions[i]["name"]]
                   for i in range(num_factions)) if timeline else 0

    world_state = {
        "seed": seed,
        "physical_laws": base_laws,
        "factions": factions,
        "interaction_matrix": interaction_matrix,
        "prophecies": prophecies,
        "timeline_summary": {
            "initial_pop": initial_pop,
            "final_pop": final_pop,
            "steps": time_horizon,
        },
        "world_name": f"The {primary_element.title()} Realm of {words[0].title() if words else 'Chaos'}",
    }

    return world_state


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    seed = payload.get("seed", "emergent consciousness in a fractured lattice")
    num_factions = int(payload.get("factions", 2))
    time_horizon = int(payload.get("time", 100))

    reality = generate_reality(seed, num_factions, time_horizon)
    reality["action"] = "weave"
    reality["message"] = f"Reality woven from: \"{seed}\""
    return reality
