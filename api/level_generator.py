"""Vibe-Based Level Generation for Lucid Machines.
Generates game levels from the organism's current state:
vibe pulses, mood, knowledge garden, and dream journal."""
import json
import time
import os
import random
from typing import Dict, List, Optional, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Level templates for different moods
_LEVEL_TEMPLATES = {
    "serene": {
        "name": "Tranquil Gardens",
        "theme": "peaceful bioluminescent gardens",
        "terrain": "flowing water, soft moss, crystal bridges",
        "entities": ["light_motes", "peaceful_spirits", "harmony_nodes"],
        "mechanics": ["meditation_zones", "resonance_puzzles", "gentle_exploration"],
        "color_palette": ["#2b5c8f", "#41b3a3", "#96ceb4", "#a8e6cf"],
        "difficulty": 0.2,
        "size": "medium"
    },
    "stormy": {
        "name": "Tempest Peaks",
        "theme": "lightning-scarred mountains",
        "terrain": "jagged cliffs, storm clouds, energy arcs",
        "entities": ["storm_elementals", "chaos_spirits", "entropy_vortices"],
        "mechanics": ["surge_timing", "lightning_navigation", "chaos_management"],
        "color_palette": ["#c0392b", "#e74c3c", "#e67e22", "#f39c12"],
        "difficulty": 0.8,
        "size": "large"
    },
    "volatile": {
        "name": "Fractured Realms",
        "theme": "shattered dimensional spaces",
        "terrain": "floating islands, reality tears, phasing walls",
        "entities": ["void_walkers", "paradox_entities", "entropy_echoes"],
        "mechanics": ["phase_shifting", "reality_anchoring", "entropy_surfing"],
        "color_palette": ["#95a5a6", "#7f8c8d", "#bdc3c7", "#ecf0f1"],
        "difficulty": 0.7,
        "size": "variable"
    },
    "focused": {
        "name": "Precision Archives",
        "theme": "ordered geometric libraries",
        "terrain": "crystalline corridors, data streams, logic gates",
        "entities": ["logic_constructs", "data_spirits", "order_guardians"],
        "mechanics": ["pattern_matching", "sequence_solving", "flow_optimization"],
        "color_palette": ["#27ae60", "#2ecc71", "#58d68d", "#82e0aa"],
        "difficulty": 0.5,
        "size": "structured"
    },
    "drifting": {
        "name": "Misty Vallies",
        "theme": "ethereal fog-covered landscapes",
        "terrain": "shifting mists, hidden paths, echo chambers",
        "entities": ["memory_echoes", "dream_fragments", "whisper_winds"],
        "mechanics": ["memory_recollection", "path_finding", "echo_navigation"],
        "color_palette": ["#7f8c8d", "#bdc3c7", "#d5dbdb", "#ecf0f1"],
        "difficulty": 0.3,
        "size": "expansive"
    },
    "excited": {
        "name": "Crescendo Spires",
        "theme": "towering resonance spires",
        "terrain": "spiraling towers, harmonic bridges, pulsing cores",
        "entities": ["resonance_angels", "harmony_choirs", "crescendo_catalysts"],
        "mechanics": ["rhythm_synchronization", "harmony_building", "climax_timing"],
        "color_palette": ["#e67e22", "#f39c12", "#f5b041", "#fad7a0"],
        "difficulty": 0.6,
        "size": "vertical"
    },
    "calm": {
        "name": "Still Waters",
        "theme": "mirror-smooth reflective pools",
        "terrain": "perfect reflections, submerged pathways, quiet depths",
        "entities": ["reflection_spirits", "depth_keepers", "silence_wardens"],
        "mechanics": ["reflection_puzzles", "depth_diving", "silence_maintenance"],
        "color_palette": ["#9b59b6", "#a569bd", "#bb8fce", "#d2b4de"],
        "difficulty": 0.25,
        "size": "deep"
    },
    "anxious": {
        "name": "Discordant Caves",
        "theme": "dissonant crystal caverns",
        "terrain": "sharp crystals, discordant echoes, unstable floors",
        "entities": ["discord_sprites", "anxiety_shades", "fear_manifestations"],
        "mechanics": ["dissonance_calming", "crystal_harmonization", "fear_confrontation"],
        "color_palette": ["#e74c3c", "#c0392b", "#ec7063", "#fadbd8"],
        "difficulty": 0.75,
        "size": "claustrophobic"
    },
    "joyful": {
        "name": "Harmony Meadows",
        "theme": "radiant flower-filled plains",
        "terrain": "blooming fields, melody streams, celebration arches",
        "entities": ["joy_sprites", "celebration_spirits", "harmony_blooms"],
        "mechanics": ["melody_weaving", "bloom_cultivation", "joy_spreading"],
        "color_palette": ["#f1c40f", "#f39c12", "#f7dc6f", "#fef9e7"],
        "difficulty": 0.3,
        "size": "open"
    },
    "sad": {
        "name": "Echoing Depths",
        "theme": "submerged memory ruins",
        "terrain": "sunken structures, melancholy currents, fading light",
        "entities": ["memory_ghosts", "sorrow_spirits", "loss_echoes"],
        "mechanics": ["memory_restoration", "grief_processing", "light_rekindling"],
        "color_palette": ["#34495e", "#2c3e50", "#5d6d7e", "#85929e"],
        "difficulty": 0.4,
        "size": "submerged"
    }
}

# Vibe pulse modifiers
_VIBE_MODIFIERS = {
    "surge": {"difficulty": +0.15, "entities": +2, "intensity": "high"},
    "ebb": {"difficulty": -0.1, "entities": -1, "intensity": "low"},
    "ripple": {"difficulty": +0.05, "entities": 0, "intensity": "medium"},
    "tsunami": {"difficulty": +0.2, "entities": +3, "intensity": "extreme"},
    "whisper": {"difficulty": -0.15, "entities": -1, "intensity": "very_low"},
    "crescendo": {"difficulty": +0.1, "entities": +1, "intensity": "building"},
    "decay": {"difficulty": -0.05, "entities": -1, "intensity": "fading"},
    "explosion": {"difficulty": +0.25, "entities": +4, "intensity": "explosive"},
    "stillness": {"difficulty": -0.2, "entities": -2, "intensity": "none"},
    "pulse": {"difficulty": 0, "entities": 0, "intensity": "rhythmic"}
}

# Level generation state
_level_state = {
    "generated_levels": [],
    "total_generated": 0,
    "last_generation": None,
    "generation_history": []
}


def generate_level(organism_state: dict = None) -> dict:
    """Generate a Lucid Machines level from organism state."""
    # Get organism state components
    mood = organism_state.get("mood", {}) if organism_state else {}
    pulse = organism_state.get("pulse", {}) if organism_state else {}
    vibe = organism_state.get("vibe", {}) if organism_state else {}
    garden = organism_state.get("garden", {}) if organism_state else {}
    dreams = organism_state.get("dreams", {}) if organism_state else {}
    
    # Determine base mood
    current_mood = mood.get("mood", "neutral") if mood else "neutral"
    mood_intensity = mood.get("intensity", 0.5) if mood else 0.5
    pulse_type = pulse.get("type", "stillness") if pulse else "stillness"
    pulse_intensity = pulse.get("intensity", 0.5) if pulse else 0.5
    
    # Get template for mood
    template = _LEVEL_TEMPLATES.get(current_mood, _LEVEL_TEMPLATES["serene"]).copy()
    
    # Apply vibe pulse modifiers
    vibe_mod = _VIBE_MODIFIERS.get(pulse_type, {})
    
    # Calculate final difficulty
    base_difficulty = template["difficulty"]
    vibe_difficulty = vibe_mod.get("difficulty", 0)
    mood_difficulty = (mood_intensity - 0.5) * 0.2  # -0.1 to +0.1
    pulse_difficulty = (pulse_intensity - 0.5) * 0.1  # -0.05 to +0.05
    
    final_difficulty = max(0.1, min(1.0, base_difficulty + vibe_difficulty + mood_difficulty + pulse_difficulty))
    
    # Generate level ID
    level_id = f"level_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # Build level
    level = {
        "id": level_id,
        "name": template["name"],
        "theme": template["theme"],
        "terrain": template["terrain"],
        "entities": template["entities"][:],
        "mechanics": template["mechanics"][:],
        "color_palette": template["color_palette"][:],
        "difficulty": round(final_difficulty, 2),
        "size": template["size"],
        "mood": current_mood,
        "mood_intensity": mood_intensity,
        "pulse_type": pulse_type,
        "pulse_intensity": pulse_intensity,
        "vibe_modifier": vibe_mod.get("intensity", "normal"),
        "generated_at": time.time(),
        "organism_snapshot": {
            "mood": current_mood,
            "pulse": pulse_type,
            "vibe": vibe.get("type", "unknown") if vibe else "unknown"
        }
    }
    
    # Add garden influence if available
    if garden:
        total_modules = garden.get("total_modules", 0)
        if total_modules > 50:
            level["entities"].append("ancient_guardian")
            level["mechanics"].append("legacy_unlock")
        elif total_modules > 20:
            level["entities"].append("garden_keeper")
            level["mechanics"].append("garden_tending")
    
    # Add dream influence if available
    if dreams:
        total_dreams = dreams.get("total_entries", 0)
        if total_dreams > 10:
            level["entities"].append("dream_weaver")
            level["mechanics"].append("dream_interpretation")
        elif total_dreams > 5:
            level["entities"].append("memory_fragment")
            level["mechanics"].append("memory_collection")
    
    # Record generation
    _level_state["generated_levels"].append(level)
    _level_state["total_generated"] += 1
    _level_state["last_generation"] = time.time()
    _level_state["generation_history"].append({
        "level_id": level_id,
        "mood": current_mood,
        "pulse": pulse_type,
        "difficulty": final_difficulty,
        "timestamp": time.time()
    })
    
    if len(_level_state["generation_history"]) > 100:
        _level_state["generation_history"] = _level_state["generation_history"][-100:]
    
    return level


def get_level_by_id(level_id: str) -> dict:
    """Get a previously generated level by ID."""
    for level in _level_state["generated_levels"]:
        if level["id"] == level_id:
            return level
    return {"status": "not_found", "level_id": level_id}


def get_generation_history(limit: int = 10) -> dict:
    """Get level generation history."""
    history = _level_state["generation_history"]
    return {
        "total_generated": _level_state["total_generated"],
        "recent": history[-limit:] if history else []
    }


def get_level_statistics() -> dict:
    """Get statistics on generated levels."""
    if not _level_state["generation_history"]:
        return {"message": "No levels generated yet"}
    
    moods = {}
    pulses = {}
    difficulties = []
    
    for gen in _level_state["generation_history"]:
        m = gen.get("mood", "unknown")
        p = gen.get("pulse", "unknown")
        moods[m] = moods.get(m, 0) + 1
        pulses[p] = pulses.get(p, 0) + 1
        difficulties.append(gen.get("difficulty", 0.5))
    
    avg_difficulty = sum(difficulties) / len(difficulties) if difficulties else 0.5
    
    return {
        "total_generated": _level_state["total_generated"],
        "mood_distribution": moods,
        "pulse_distribution": pulses,
        "average_difficulty": round(avg_difficulty, 2),
        "difficulty_range": [round(min(difficulties), 2), round(max(difficulties), 2)]
    }


# CLI entry point
if __name__ == "__main__":
    import argparse
    import json as _json
    
    parser = argparse.ArgumentParser(description="Vibe-Based Level Generation")
    parser.add_argument("--generate", action="store_true", help="Generate a level from organism state")
    parser.add_argument("--mood", type=str, help="Override mood for generation")
    parser.add_argument("--pulse", type=str, help="Override pulse type for generation")
    parser.add_argument("--history", type=int, default=5, help="Show generation history")
    parser.add_argument("--stats", action="store_true", help="Show generation statistics")
    parser.add_argument("--get", type=str, help="Get level by ID")
    
    args = parser.parse_args()
    
    if args.generate:
        # Build organism state
        organism_state = {}
        if args.mood:
            organism_state["mood"] = {"mood": args.mood, "intensity": 0.7}
        if args.pulse:
            organism_state["pulse"] = {"type": args.pulse, "intensity": 0.7}
        
        level = generate_level(organism_state)
        print(f"Generated Level: {level['name']} ({level['id']})")
        print(f"  Theme: {level['theme']}")
        print(f"  Terrain: {level['terrain']}")
        print(f"  Difficulty: {level['difficulty']}")
        print(f"  Size: {level['size']}")
        print(f"  Entities: {', '.join(level['entities'])}")
        print(f"  Mechanics: {', '.join(level['mechanics'])}")
        print(f"  Colors: {', '.join(level['color_palette'])}")
    
    if args.history:
        result = get_generation_history(args.history)
        print(f"Generation History ({result['total_generated']} total):")
        for g in result["recent"]:
            print(f"  [{g['level_id']}] {g['mood']} / {g['pulse']} - difficulty: {g['difficulty']}")
    
    if args.stats:
        result = get_level_statistics()
        print(f"Statistics: {_json.dumps(result, indent=2)}")
    
    if args.get:
        level = get_level_by_id(args.get)
        print(f"Level: {_json.dumps(level, indent=2)}")
    
    if not any([args.generate, args.history, args.stats, args.get]):
        print("Vibe-Based Level Generation operational")
        print("Commands: --generate, --mood <mood>, --pulse <pulse>, --history N, --stats, --get <level_id>")
