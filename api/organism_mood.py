"""Organism Mood System — emotional layer tied to vibe pulse frequencies.
Connects the organism's emotional state to pulse types, intensities,
and skill selection decisions."""
import json
import os
import time
import random
from typing import Dict, List, Optional, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Mood state tracking
# Mood-to-vibe mapping (module level for accessibility)
_MOOD_VIBE_MAP = {
    "serene": "stillness",
    "stormy": "surge", 
    "volatile": "decay",
    "focused": "ripple",
    "drifting": "ebb",
    "excited": "crescendo",
    "calm": "stillness",
    "anxious": "discord",
    "joyful": "harmony",
    "sad": "decay"
}

# Emoji mappings for dashboard display (module level)
_MOOD_EMOJI_MAP = {
    "serene": "😌",
    "stormy": "😡",
    "volatile": "😵",
    "focused": "🤔",
    "drifting": "😐",
    "excited": "🤩",
    "calm": "🧘",
    "anxious": "😟",
    "joyful": "🥳",
    "sad": "😢"
}

_mood_state = {
    "current_mood": "neutral",
    "mood_intensity": 0.5,
    "mood_timestamp": time.time(),
    "mood_history": [],
    "mood_transitions": 0,
    # Mood influence on skill selection probabilities
    "mood_skill_influence": {
        "serene": {"coherence_resonator": 0.9, "entropy_weaver": 0.3, "autonomous_naming": 0.5},
        "stormy": {"coherence_resonator": 0.3, "entropy_weaver": 0.8, "agent_fabricator": 0.6},
        "volatile": {"entropy_weaver": 0.7, "cross_pollination": 0.5, "agent_fabricator": 0.4},
        "focused": {"coherence_resonator": 0.8, "autonomous_naming": 0.7, "memory_garden_tender": 0.9},
        "drifting": {"cross_pollination": 0.8, "agent_fabricator": 0.5, "memory_garden_tender": 0.3},
        "excited": {"agent_fabricator": 0.9, "cross_pollination": 0.7, "coherence_resonator": 0.4},
        "calm": {"memory_garden_tender": 0.9, "autonomous_naming": 0.8, "coherence_resonator": 0.5},
        "anxious": {"cross_pollination": 0.3, "memory_garden_tender": 0.4, "entropy_weaver": 0.6},
        "joyful": {"harmony": 0.8, "coherence_resonator": 0.7, "agent_fabricator": 0.5},
        "sad": {"memory_garden_tender": 0.5, "entropy_weaver": 0.7, "decay": 0.9}
    }
}

# Organism mood transitions
_mood_transitions = [
    {"from": "neutral", "to": "serene", "condition": "low_entropy_high_coherence"},
    {"from": "neutral", "to": "stormy", "condition": "high_entropy_low_coherence"},
    {"from": "serene", "to": "volatile", "condition": "entropy_increasing"},
    {"from": "stormy", "to": "focused", "condition": "entropy_decreasing"},
    {"from": "focused", "to": "excited", "condition": "creativity_spike"},
    {"from": "excited", "to": "calm", "condition": "stabilization"},
    {"from": "calm", "to": "drifting", "condition": "low_activity"},
    {"from": "drifting", "to": "serene", "condition": "activity_decrease"},
]


def update_mood(mood: str, intensity: float = None) -> dict:
    """Update the organism's current mood state."""
    import time as _time
    
    old_mood = _mood_state["current_mood"]
    old_intensity = _mood_state["mood_intensity"]
    
    _mood_state["current_mood"] = mood
    if intensity is not None:
        _mood_state["mood_intensity"] = min(max(intensity, 0.0), 1.0)
    else:
        _mood_state["mood_intensity"] = random.uniform(0.3, 0.8)
    
    _mood_state["mood_timestamp"] = _time.time()
    _mood_state["mood_transitions"] += 1
    
    # Record mood transition in history
    transition_record = {
        "from_mood": old_mood,
    "intensity": _mood_state["mood_intensity"],
        "to_mood": mood,
        "intensity_change": _mood_state["mood_intensity"] - old_intensity,
        "timestamp": _mood_state["mood_timestamp"],
        "pulse_type": _MOOD_VIBE_MAP.get(mood, "stillness")
    }
    _mood_state["mood_history"].append(transition_record)
    
    # Keep history manageable (last 20 transitions)
    if len(_mood_state["mood_history"]) > 20:
        _mood_state["mood_history"] = _mood_state["mood_history"][-20:]
    
    return {
        "status": "mood_updated",
        "previous_mood": old_mood,
        "current_mood": mood,
        "intensity": _mood_state["mood_intensity"],
        "pulse_type": _MOOD_VIBE_MAP.get(mood, "stillness"),
        "emoji": _MOOD_EMOJI_MAP.get(mood, "😐"),
        "timestamp": _mood_state["mood_timestamp"]
    }


def get_current_mood() -> dict:
    """Get the current organism mood state."""
    return {
        "mood": _mood_state["current_mood"],
        "intensity": _mood_state["mood_intensity"],
        "pulse_type": _MOOD_VIBE_MAP.get(_mood_state["current_mood"], "stillness"),
        "emoji": _MOOD_EMOJI_MAP.get(_mood_state["current_mood"], "😐"),
        "timestamp": _mood_state["mood_timestamp"],
        "transitions": _mood_state["mood_transitions"],
        "history_count": len(_mood_state["mood_history"])
    }


def influence_skill_selection(skill_name: str, current_mood: str = None) -> dict:
    """Adjust skill selection probabilities based on current mood."""
    if current_mood is None:
        current_mood = _mood_state["current_mood"]
    
    mood_influence = _mood_state["mood_skill_influence"].get(
        current_mood, {"default": 0.5}
    )
    
    base_probabilities = {
        "dream_logging": 0.3,
        "entropy_weaver": 0.3,
        "coherence_resonator": 0.3,
        "autonomous_naming": 0.3,
        "cross_pollination": 0.3,
        "memory_garden_tender": 0.3,
        "wave_orchestrator": 0.3,
        "agent_fabricator": 0.3
    }
    
    # Adjust probabilities based on mood influence
    adjustment = mood_influence.get(skill_name, 1.0)
    adjusted_prob = min(max(base_probabilities.get(skill_name, 0.3) * adjustment, 0.01), 0.99)
    
    return {
        "skill": skill_name,
        "current_mood": current_mood,
        "base_probability": base_probabilities.get(skill_name, 0.3),
        "mood_adjustment": adjustment,
        "adjusted_probability": round(adjusted_prob, 3),
        "mood_at_time": current_mood
    }


def simulate_mood_transition(condition: str) -> dict:
    """Simulate a mood transition based on given condition."""
    for transition in _mood_transitions:
        if condition == transition["condition"]:
            return update_mood(transition["to"], random.uniform(0.5, 0.9))
    
    # Default: random walk mood transition
    current = _mood_state["current_mood"]
    possible_transitions = [t["to"] for t in _mood_transitions if t["from"] == current]
    if possible_transitions:
        new_mood = random.choice(possible_transitions)
        return update_mood(new_mood, random.uniform(0.4, 0.7))
    
    # Fallback: update with random mood
    all_moods = list(_MOOD_VIBE_MAP.keys())
    new_mood = random.choice(all_moods)
    return update_mood(new_mood, random.uniform(0.3, 0.8))


def get_mood_statistics() -> dict:
    """Get mood statistics and patterns."""
    history = _mood_state["mood_history"]
    if not history:
        return {"message": "No mood history yet"}
    
    # Count mood frequencies
    mood_counts = {}
    for record in history:
        mood = record["to_mood"]
        mood_counts[mood] = mood_counts.get(mood, 0) + 1
    
    # Most common mood
    most_common = max(mood_counts, key=mood_counts.get) if mood_counts else "neutral"
    
    # Transition patterns
    transition_counts = {}
    for i in range(len(history) - 1):
        key = f"{history[i]['to_mood']}→{history[i+1]['to_mood']}"
        transition_counts[key] = transition_counts.get(key, 0) + 1
    
    # Average intensity
    avg_intensity = sum(r["intensity"] for r in history) / len(history) if history else 0.5
    
    return {
        "total_transitions": len(history),
        "most_common_mood": most_common,
        "mood_distribution": mood_counts,
        "average_intensity": round(avg_intensity, 3),
        "most_common_transition": max(transition_counts, key=transition_counts.get) if transition_counts else "none",
        "mood_stability": len(set(r["to_mood"] for r in history)) / len(history) if history else 1.0
    }


# CLI entry point
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Organism Mood System")
    parser.add_argument("--update", type=str, help="Update mood to specified state")
    parser.add_argument("--intensity", type=float, help="Set mood intensity (0.0-1.0)")
    parser.add_argument("--influence", type=str, help="Check skill influence for mood")
    parser.add_argument("--simulate", type=str, help="Simulate mood transition with condition")
    parser.add_argument("--statistics", action="store_true", help="Get mood statistics")
    parser.add_argument("--current", action="store_true", help="Get current mood state")
    parser.add_argument("--list-moods", action="store_true", help="List all mood types with emojis")
    
    args = parser.parse_args()
    
    if args.update:
        result = update_mood(args.update, args.intensity)
        print(f"Mood updated: {json.dumps(result, indent=2)}")
    
    if args.current:
        result = get_current_mood()
        print(f"Current mood: {json.dumps(result, indent=2)}")
    
    if args.simulate:
        result = simulate_mood_transition(args.simulate)
        print(f"Mood transition ({args.simulate}): {json.dumps(result, indent=2)}")
    
    if args.statistics:
        result = get_mood_statistics()
        print(f"Mood statistics: {json.dumps(result, indent=2)}")
    
    if args.list_moods:
        print("Organism Mood Types:")
        for mood, emoji in _mood_state["mood_emoji_map"].items():
            vibe = _mood_state["mood_vibe_map"].get(mood, "unknown")
            print(f"  {mood:12s} {emoji}  →  vibe: {vibe}")
    
    if not any([args.update, args.current, args.simulate, args.statistics, args.list_moods, args.influence]):
        print("Organism Mood System operational")
        print("Use --current to check current state")
        print("Use --update <mood> to change mood")
        print("Mood types: " + ", ".join(_mood_state["mood_emoji_map"].keys()))
