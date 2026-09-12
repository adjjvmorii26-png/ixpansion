import os
"""Autonomous Naming Ceremonies with HEX Aesthetics.
Generates module names from purpose with HEX color schemes and broadcasts
naming ceremonies to the organism dashboard."""
import json
import time
import random
from typing import Dict, List, Optional, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# HEX aesthetic naming templates
_HEX_NAME_TEMPLATES = [
    # Function-based names with HEX color prefix
    "{hex_prefix}_oracle_{function}",
    "{hex_prefix}_weaver_{function}", 
    "{hex_prefix}_forger_{function}",
    "{hex_prefix}_architect_{function}",
    
    # Dream-based names
    "dream_{hex_prefix}_{function}",
    "lucid_{hex_prefix}_{function}",
    
    # Resonance-based names
    "resonance_{hex_prefix}_{function}",
    "coherence_{hex_prefix}_{function}",
    
    # Entropy-based names
    "entropy_{hex_prefix}_{function}",
    "void_{hex_prefix}_{function}",
]

# HEX color prefixes mapped to mood types
_MOOD_HEX_PREFIXES = {
    "serene": "#2b5c8f",      # deep blue - stillness
    "stormy": "#c0392b",      # red - surge
    "volatile": "#95a5a6",    # gray - decay
    "focused": "#27ae60",     # green - ripple
    "drifting": "#7f8c8d",    # gray - ebb
    "excited": "#e67e22",     # orange - crescendo
    "calm": "#9b59b6",        # purple - stillness
    "anxious": "#e74c3c",     # red - discord
    "joyful": "#f1c40f",      # yellow - harmony
    "sad": "#34495e",         # dark blue - decay
}

# Naming ceremony state
_naming_ceremony_state = {
    "ceremonies_held": 0,
    "names_generated": 0,
    "naming_history": [],
    "current_hex_scheme": "#2b5c8f",  # default: serene/blue
}


def generate_hex_name(module_purpose: str, mood: str = None) -> dict:
    """Generate a HEX-aesthetic module name from purpose and optional mood."""
    # Determine mood and HEX prefix
    if mood and mood in _MOOD_HEX_PREFIXES:
        hex_prefix = _MOOD_HEX_PREFIXES[mood]
        # Remove # for template formatting, add back later
        hex_base = hex_prefix.replace("#", "")
    else:
        hex_prefix = "8b44ad"  # default purple
        hex_base = "8b44ad"
    
    # Determine function category from purpose
    purpose_lower = module_purpose.lower()
    function_category = "wave"  # default
    
    if "entropy" in purpose_lower:
        function_category = "entropy"
    elif "dream" in purpose_lower:
        function_category = "dream"
    elif "resonance" in purpose_lower:
        function_category = "resonance"
    elif "coherence" in purpose_lower:
        function_category = "coherence"
    elif "wave" in purpose_lower:
        function_category = "wave"
    
    # Pick a template
    template = random.choice(_HEX_NAME_TEMPLATES)
    
    # Format the name
    name = template.format(hex_prefix=hex_prefix, function=function_category)
    
    # Add HEX color as separate field
    full_name = {
        "name": name,
        "hex_color": hex_prefix,
        "function_category": function_category,
        "mood": mood or "neutral",
        "generated_at": time.time(),
        "ceremony_id": f"ceremony_{int(time.time())}_{random.randint(1000,9999)}"
    }
    
    # Record in naming history
    _naming_ceremony_state["names_generated"] += 1
    _naming_ceremony_state["naming_history"].append(full_name)
    
    # Keep history manageable
    if len(_naming_ceremony_state["naming_history"]) > 50:
        _naming_ceremony_state["naming_history"] = _naming_ceremony_state["naming_history"][-50:]
    
    return full_name


def hold_naming_ceremony(module_purpose: str, mood: str = None, 
                         broadcast: bool = True) -> dict:
    """Hold a full naming ceremony for a new module."""
    # Generate the name
    name_data = generate_hex_name(module_purpose, mood)
    
    # Determine associated pulse type based on mood
    mood_pulse_map = {
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
    
    pulse_type = mood_pulse_map.get(mood, "stillness")
    
    # Create ceremony record
    ceremony = {
        "id": name_data["ceremony_id"],
        "module_purpose": module_purpose,
        "generated_name": name_data["name"],
        "hex_color": name_data["hex_color"],
        "mood": mood or "neutral",
        "pulse_type": pulse_type,
        "emoji": _MOOD_EMOJI_MAP.get(mood, "😐") if 'MOOD_EMOJI_MAP' in dir() else "😐",
        "timestamp": time.time(),
        "broadcast": broadcast
    }
    
    # Record in history
    _naming_ceremony_state["ceremonies_held"] += 1
    _naming_ceremony_state["naming_history"].append(ceremony)
    
    if len(_naming_ceremony_state["naming_history"]) > 50:
        _naming_ceremony_state["naming_history"] = _naming_ceremony_state["naming_history"][-50:]
    
    return ceremony


def get_naming_history(limit: int = 10) -> dict:
    """Get naming ceremony history."""
    history = _naming_ceremony_state["naming_history"]
    return {
        "ceremonies_held": _naming_ceremony_state["ceremonies_held"],
        "names_generated": _naming_ceremony_state["names_generated"],
        "last_n": history[-limit:] if history else [],
        "current_hex_scheme": _naming_ceremony_state["current_hex_scheme"]
    }


# CLI entry point
if __name__ == "__main__":
    import argparse
    import json as _json
    import sys
    
    parser = argparse.ArgumentParser(description="Autonomous Naming Ceremonies")
    parser.add_argument("--ceremony", nargs=2, metavar=("PURPOSE", "MOOD"),
                        help="Hold naming ceremony: purpose and optional mood")
    parser.add_argument("--name", type=str, help="Generate name for given purpose")
    parser.add_argument("--mood", type=str, help="Set mood for naming ceremony")
    parser.add_argument("--history", type=int, default=5, help="Show last N ceremonies")
    parser.add_argument("--current", action="store_true", help="Show current hex scheme")
    
    args = parser.parse_args()
    
    if args.ceremony:
        purpose, mood = args.ceremony
        ceremony = hold_naming_ceremony(purpose, mood)
        print(f"🌀 Naming Ceremony #{_naming_ceremony_state['ceremonies_held']}:")
        print(f"  Purpose: {purpose}")
        print(f"  Mood: {ceremony['mood']} {_MOOD_EMOJI_MAP.get(ceremony['mood'], '😐')}")
        print(f"  Generated Name: {ceremony['generated_name']}")
        print(f"  HEX Color: {ceremony['hex_color']}")
        print(f"  Pulse Type: {ceremony['pulse_type']}")
        print(f"  Emoji: {ceremony['emoji']}")
    
    if args.name:
        result = generate_hex_name(args.name, args.mood)
        print(f"Generated name: {result['name']}")
        print(f"HEX Color: {result['hex_color']}")
        print(f"Function: {result['function_category']}")
    
    if args.history:
        result = get_naming_history(args.history)
        print(f"Naming History ({result['names_generated']} total):")
        for c in result["last_n"]:
            emoji = _MOOD_EMOJI_MAP.get(c['mood'], "😐") if 'MOOD_EMOJI_MAP' else "😐"
            print(f"  [{c['ceremony_id']}] {c['generated_name']} ({c['mood']}{emoji}) - {c['hex_color']}")
    
    if args.current:
        result = get_naming_history(1)
        print(f"Current HEX scheme: {result['current_hex_scheme']}")
        print(f"Total ceremonies: {result['ceremonies_held']}, names: {result['names_generated']}")

    if not any([args.ceremony, args.name, args.history, args.current]):
        print("Naming Ceremonies System operational")
        print("Commands: --ceremony <purpose> <mood>, --name <purpose> --mood <mood>")
        print("          --history N, --current")


def handler(req: dict) -> dict:
    """Unified route handler — legacy HEX naming plus Wave 430 self-naming council."""
    try:
        import wave430_naming_ceremony as council
    except Exception:
        council = None
    action = (req or {}).get("action", "status")
    if council is not None and action in ("propose", "vote", "seal"):
        return council.handler(req)
    if action == "generate" or action == "name":
        return generate_hex_name((req or {}).get("purpose", ""), (req or {}).get("mood"))
    if action == "hold" or action == "ceremony":
        return hold_naming_ceremony((req or {}).get("purpose", ""), (req or {}).get("mood"))
    if action == "history":
        return get_naming_history(int((req or {}).get("limit", 10)))
    if action in ("status", "state") and council is not None:
        return council.status()
    return {
        "action": action,
        "valid": ["propose", "vote", "seal", "status", "generate", "hold", "history"],
        "council_available": council is not None,
        "legacy": get_naming_history(3),
    }
