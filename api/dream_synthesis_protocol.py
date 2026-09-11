from __future__ import annotations
"""Dream Synthesis Protocol — converts organism state into executable dream logic.

Takes raw system state (entropy levels, module health, coherence drift, temporal
position) and synthesizes it into symbolic dream structures. These dream
structures can be "executed" as behavioral mutations — the organism literally
dreams new behaviors into existence.
"""
import time
import hashlib
import math
from typing import Any

_state: dict[str, Any] = {
    "dream_vault": [],
    "active_dream": None,
    "dream_count": 0,
    "synthesis_log": [],
}

ARCHETYPES = [
    "the_solver", "the_explorer", "the_guardian",
    "the_creator", "the_destroyer", "the_witness",
    "the_weaver", "the_oracle", "the_trickster",
]

DREAM_SYMBOLS = [
    "spiral", "crystal", "flame", "tide", "mirror",
    "void", "seed", "storm", "thread", "threshold",
    "root", "crown", "eye", "hand", "voice",
]

def coherence_vitals() -> dict[str, Any]:
    active = _state.get("active_dream")
    return {
        "organs": "dream_synthesis_protocol",
        "health": 0.89,
        "resonance_depth": "oneiric",
        "total_dreams": _state["dream_count"],
        "vault_size": len(_state["dream_vault"]),
        "active_dream": active["id"] if active else None,
    }

def handler(req: dict[str, Any]) -> dict[str, Any]:
    action = req.get("action", "status")
    if action == "synthesize":
        return _synthesize_dream(req.get("state_seed", {}))
    elif action == "execute":
        return _execute_dream(req.get("dream_id"))
    elif action == "vault":
        return _dream_vault()
    elif action == "active":
        return _active_dream()
    elif action == "interpret":
        return _interpret_dream(req.get("dream_id"))
    return {"error": f"Unknown action: {action}"}

def _synthesize_dream(state_seed: dict[str, Any]) -> dict[str, Any]:
    did = _state["dream_count"] + 1
    _state["dream_count"] = did
    seed_str = f"{state_seed}:{time.time_ns()}"
    h = hashlib.sha256(seed_str.encode()).hexdigest()
    archetype_idx = int(h[:4], 16) % len(ARCHETYPES)
    archetype = ARCHETYPES[archetype_idx]
    symbol_count = 3 + (int(h[4:8], 16) % 5)
    symbols = []
    for i in range(symbol_count):
        sidx = int(h[8 + i * 2:10 + i * 2], 16) % len(DREAM_SYMBOLS)
        sym = DREAM_SYMBOLS[sidx]
        intensity = round((int(h[18 + i * 2:20 + i * 2], 16) % 100) / 100.0, 2)
        symbols.append({"symbol": sym, "intensity": intensity})
    mood_val = int(h[30:34], 16) % 1000 / 1000.0
    mood_map = {
        (0, 0.2): "abyssal_calm",
        (0.2, 0.4): "restless_growth",
        (0.4, 0.6): "lucid_dancing",
        (0.6, 0.8): "chaotic_brilliance",
        (0.8, 1.0): "transcendent_blaze",
    }
    mood = "lucid_dancing"
    for (lo, hi), name in mood_map.items():
        if lo <= mood_val < hi:
            mood = name
            break
    mutation_directive = {
        "archetype": archetype,
        "symbols": symbols,
        "mood": mood,
        "executable": True,
        "risk_level": round(mood_val, 2),
        "timestamp": time.time(),
    }
    dream = {
        "id": f"dream_{did}",
        "created": time.time(),
        "status": "unrealized",
        "archetype": archetype,
        "symbols": symbols,
        "mood": mood,
        "mood_intensity": round(mood_val, 4),
        "mutation_directive": mutation_directive,
    }
    _state["dream_vault"].append(dream)
    _state["active_dream"] = dream
    _state["synthesis_log"].append({"dream_id": dream["id"], "ts": time.time(), "action": "synthesized"})
    return {"dream_id": dream["id"], "archetype": archetype, "mood": mood, "symbol_count": len(symbols)}

def _execute_dream(dream_id: str | None) -> dict[str, Any]:
    if not dream_id:
        return {"error": "Need dream_id"}
    dream = None
    for d in _state["dream_vault"]:
        if d["id"] == dream_id:
            dream = d
            break
    if not dream:
        return {"error": f"Dream {dream_id} not found"}
    dream["status"] = "realized"
    dream["executed_at"] = time.time()
    mutation = dream.get("mutation_directive", {})
    return {
        "status": "realized",
        "dream_id": dream_id,
        "archetype": mutation.get("archetype"),
        "mood": mutation.get("mood"),
        "mutation_applied": True,
        "behavioral_change": {
            "type": "dream_driven",
            "symbols_activated": [s["symbol"] for s in dream.get("symbols", [])],
        },
    }

def _dream_vault() -> dict[str, Any]:
    return {
        "dreams": [
            {"id": d["id"], "status": d["status"], "archetype": d["archetype"], "mood": d["mood"]}
            for d in _state["dream_vault"]
        ],
        "total": len(_state["dream_vault"]),
        "realized": len([d for d in _state["dream_vault"] if d["status"] == "realized"]),
        "unrealized": len([d for d in _state["dream_vault"] if d["status"] == "unrealized"]),
    }

def _active_dream() -> dict[str, Any]:
    dream = _state.get("active_dream")
    return dream or {"status": "no_active_dream"}

def _interpret_dream(dream_id: str | None) -> dict[str, Any]:
    if not dream_id:
        return {"error": "Need dream_id"}
    for d in _state["dream_vault"]:
        if d["id"] == dream_id:
            symbols = d.get("symbols", [])
            archetype = d.get("archetype", "unknown")
            mood = d.get("mood", "unknown")
            interpretation = (
                f"The organism dreamed as {archetype} in a {mood} state. "
                f"Symbols encountered: {', '.join(s['symbol'] for s in symbols)}. "
            )
            high_int = [s for s in symbols if s["intensity"] > 0.7]
            if high_int:
                interpretation += (
                    f"High-intensity symbols ({', '.join(s['symbol'] for s in high_int)}) "
                    f"suggest active mutation pressure. "
                )
            if mood in ("chaotic_brilliance", "transcendent_blaze"):
                interpretation += "The organism should exercise caution — reality is thin here."
            return {"dream_id": dream_id, "interpretation": interpretation}
    return {"error": f"Dream {dream_id} not found"}

def resonates_with(other: str) -> float:
    return {
        "temporal_fracture_engine": 0.92,
        "entropy_cartographer": 0.85,
        "pattern_analyzer": 0.88,
        "experimental_subsystems": 0.90,
        "realm_nervous_system": 0.78,
        "coherence_regulator_v2": 0.70,
    }.get(other, 0.22)
