"""Wave 517: Evolution Simulator — simulate natural selection over module names."""
from __future__ import annotations
import random, time
from typing import Any, Dict

def coherence_vitals():
    try:
        from api.coherence_regulator import coherence_vitals as cv
        return cv()
    except Exception:
        return {"coherence": 1.0}

def _mutate(name: str, rng) -> str:
    ops = [
        lambda s: s + rng.choice(["_", "_v2", "_prime", "_echo", "_void", "_pulse"]),
        lambda s: s + rng.choice(["r", "s", "n", "x"]),
        lambda s: "".join(rng.choice([c, c.upper()]) for c in s),
    ]
    return rng.choice(ops)(name)

def handler(payload=None, context=None):
    payload = payload or {}
    from api.coherence_regulator import KNOWN_LIVING_MODULES
    rng = random.Random(time.time())
    generations = int(payload.get("generations", 5))
    pop = list(KNOWN_LIVING_MODULES[:20])
    history = [{"gen": 0, "population": pop[:]}]
    for gen in range(1, generations + 1):
        # Selection
        survivors = rng.sample(pop, min(len(pop), max(5, len(pop) - 3)))
        # Mutation
        mutants = [_mutate(n, rng) for n in survivors]
        # New birth
        new_births = [_mutate(rng.choice(pop), rng) for _ in range(3)]
        pop = survivors + mutants + new_births
        history.append({"gen": gen, "population": pop[:]})
    return {
        "action": "evolution_simulator",
        "generations": generations,
        "final_population": pop,
        "survived": len(pop),
        "lineage": history,
        "lesson": "Names evolve like species — the organism selects for fitness.",
        "time": time.time(),
        "vitals": coherence_vitals(),
    }
