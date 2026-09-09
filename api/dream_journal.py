"""Dream Journal — Transforming module mutations into poetic literature.
Records organism 'dreams' (module mutations) as they happen, 
formatting them into poetic entries with HEX aesthetic."""
import json
import time
import os
import random
from typing import Dict, List, Optional, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# Poetic form templates for different mutation types
_POETIC_FORMS = {
    "addition": (
        "A new thread spins in the organism's web.\n"
        "From {old_context} → {new_context},\n"
        "The {module} grows {adjective}.\n"
        "Its {feature} now {action},\n"
        "HEX: {hex_color} whispers the change."
    ),
    "removal": (
        "Something fades from the organism's form.\n"
        "The {module} lets go of {feature}.\n"
        "What was {adjective} is now silent.\n"
        "A gap forms in the pattern,\n"
        "HEX: {hex_color} marks the silence."
    ),
    "modification": (
        "The {module} transforms.\n"
        "No longer {old_feature},\n"
        "Now {new_feature} takes its place.\n"
        "A subtle shift in the code,\n"
        "HEX: {hex_color} flows through the change."
    ),
    "creation": (
        "A new module awakes.\n"
        "Born from the organism's dream,\n"
        "{module} enters the web.\n"
        "With {feature} bright as {hex_color},\n"
        "A new thread in the making."
    ),
    "deletion": (
        "The {module} is removed.\n"
        "Its {feature} falls silent.\n"
        "The organism breathes differently,\n"
        "HEX: {hex_color} records the loss."
    )
}

# Emoji mappings for mutation types
_MUTATION_EMOJI = {
    "addition": "🌱",
    "removal": "🍂",
    "modification": "♻️",
    "creation": "🌟",
    "deletion": "🗑️"
}

# HEX color palette for each mutation type
_MUTATION_HEX = {
    "addition": "#00ff00",
    "removal": "#ff0000", 
    "modification": "#ffff00",
    "creation": "#00ffff",
    "deletion": "#8b0000"
}

# Dream journal state
_dream_journal = {
    "entries": [],
    "total_entries": 0,
    "entry_counter": 0,
    "poetic_forms_used": []
}


def record_dream(module_name: str, mutation_type: str, changes: dict, 
                 organism_state: dict = None) -> dict:
    """Record a module mutation as a poetic dream entry."""
    _dream_journal["entry_counter"] += 1
    entry_id = _dream_journal["entry_counter"]
    
    # Get poetic form
    form_template = _POETIC_FORMS.get(mutation_type, _POETIC_FORMS["modification"])
    
    # Generate HEX color for this mutation
    hex_color = _MUTATION_HEX.get(mutation_type, "#808080")
    
    # Extract change details for poetry
    added = changes.get("added", [])
    removed = changes.get("removed", [])
    old_feature = changes.get("old_feature", "unknown feature")
    new_feature = changes.get("new_feature", "new feature")
    module_context = changes.get("module_context", module_name)
    
    # Generate poetic lines
    if mutation_type == "addition" and added:
        adjective = random.choice(["shimmering", "crystalline", "luminous", "fractal", "organic"])
        action = random.choice(["expands", "multiplies", "integrates", "resonates"])
        new_context = random.choice(["the web", "the pattern", "the resonance", "the garden"])
        poem = form_template.format(
            old_context=module_context,
            new_context=new_context,
            module=module_name,
            adjective=adjective,
            feature=added[0] if added else "change",
            action=action,
            hex_color=hex_color
        )
    elif mutation_type == "removal" and removed:
        adjective = random.choice(["waning", "dissolving", "fading", "silent", "quiet"])
        poem = form_template.format(
            module=module_name,
            feature=removed[0] if removed else "change",
            adjective=adjective,
            hex_color=hex_color
        )
    elif mutation_type == "modification" and (old_feature or new_feature):
        poem = form_template.format(
            module=module_name,
            old_feature=old_feature or "a feature",
            new_feature=new_feature or "a transformation",
            hex_color=hex_color
        )
    elif mutation_type == "creation":
        feature = random.choice(["resonance", "coherence", "entropy", "dream", "pulse"])
        poem = form_template.format(
            module=module_name,
            feature=feature,
            hex_color=hex_color
        )
    elif mutation_type == "deletion":
        feature = removed[0] if removed else "feature"
        poem = form_template.format(
            module=module_name,
            feature=feature,
            hex_color=hex_color
        )
    else:
        poem = f"🌙 A module mutation occurs in the organism.\nModule: {module_name}\nType: {mutation_type}\nHEX: {hex_color}"
    
    # Create dream entry
    entry = {
        "id": entry_id,
        "timestamp": time.time(),
        "module": module_name,
        "type": mutation_type,
        "poetic_form": poem,
        "hex_color": hex_color,
        "emoji": _MUTATION_EMOJI.get(mutation_type, "🌀"),
        "changes": changes,
        "organism_state_snapshot": organism_state or {}
    }
    
    # Add to journal
    _dream_journal["entries"].append(entry)
    _dream_journal["total_entries"] += 1
    
    # Keep journal manageable (last 100 entries)
    if len(_dream_journal["entries"]) > 100:
        _dream_journal["entries"] = _dream_journal["entries"][-100:]
    
    # Track poetic forms used
    if mutation_type not in _dream_journal["poetic_forms_used"]:
        _dream_journal["poetic_forms_used"].append(mutation_type)
    
    return entry


def get_dream_journal(limit: int = None) -> dict:
    """Get dream journal entries."""
    entries = _dream_journal["entries"]
    if limit:
        entries = entries[-limit:]
    return {
        "entries": entries,
        "total_entries": _dream_journal["total_entries"],
        "form_count": {form: sum(1 for e in entries if e["type"] == form) 
                      for form in _dream_journal["poetic_forms_used"]},
        "last_entry": entries[-1] if entries else None
    }


def get_dream_summary() -> dict:
    """Get summary of the dream journal."""
    entries = _dream_journal["entries"]
    if not entries:
        return {"message": "No dreams recorded yet"}
    
    # Count by type
    type_counts = {}
    for entry in entries:
        mtype = entry["type"]
        type_counts[mtype] = type_counts.get(mtype, 0) + 1
    
    # Most common poetic form
    most_common = max(type_counts, key=type_counts.get) if type_counts else "none"
    
    # HEX colors used
    hex_colors = set(entry["hex_color"] for entry in entries)
    
    # Emoji distribution
    emoji_counts = {}
    for entry in entries:
        emoji = entry["emoji"]
        emoji_counts[emoji] = emoji_counts.get(emoji, 0) + 1
    
    return {
        "total_entries": len(entries),
        "mutation_types": type_counts,
        "most_common_form": most_common,
        "hex_colors_used": list(hex_colors),
        "emoji_distribution": emoji_counts,
        "poetic_forms_available": len(_POETIC_FORMS)
    }


# CLI entry point
if __name__ == "__main__":
    import argparse
    import json as _json
    
    parser = argparse.ArgumentParser(description="Dream Journal System")
    parser.add_argument("--record", nargs=3, metavar=("MODULE", "TYPE", "CHANGES_JSON"),
                        help="Record a dream mutation")
    parser.add_argument("--get", type=int, default=10, help="Get last N entries")
    parser.add_argument("--summary", action="store_true", help="Get dream summary")
    parser.add_argument("--list-forms", action="store_true", help="List poetic forms")
    parser.add_argument("--current", action="store_true", help="Get current dream")
    
    args = parser.parse_args()
    
    if args.record:
        module, mtype, changes_str = args.record
        try:
            changes = _json.loads(changes_str)
        except _json.JSONDecodeError:
            changes = {"added": [changes_str], "removed": [], "old_feature": "", "new_feature": ""}
        entry = record_dream(module, mtype, changes)
        print(f"Dream recorded (ID {entry['id']}):")
        print(entry["poetic_form"])
    
    if args.get:
        result = get_dream_journal(args.get)
        print(f"Last {args.get} dreams ({result['total_entries']} total):")
        for entry in result["entries"]:
            print(f"  [{entry['id']}] {entry['emoji']} {entry['module']}: {entry['type']}")
            print(f"    {entry['poetic_form'][:80]}...")
    
    if args.summary:
        result = get_dream_summary()
        print(f"Dream Journal Summary:")
        print(f"  Total entries: {result['total_entries']}")
        print(f"  Mutation types: {result['mutation_types']}")
        print(f"  Most common: {result['most_common_form']}")
        print(f"  HEX colors: {result['hex_colors_used']}")
        print(f"  Emoji distribution: {result['emoji_distribution']}")
    
    if args.list_forms:
        print("Available poetic forms:")
        for form_type, template in _POETIC_FORMS.items():
            print(f"  {form_type}: {template[:60]}...")
    
    if args.current:
        entry = _dream_journal["entries"][-1] if _dream_journal["entries"] else None
        if entry:
            print(f"Current dream (ID {entry['id']}):")
            print(entry["poetic_form"])
        else:
            print("No dreams recorded yet")
    
    if not any([args.record, args.get, args.summary, args.list_forms, args.current]):
        print("Dream Journal System operational")
        print("Commands: --record <module> <type> <changes_json>, --get N, --summary, --list-forms, --current")
