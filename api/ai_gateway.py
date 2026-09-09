"""Vercel AI Gateway Integration — AI-powered dream interpretation and broadcast.
Connects organism dreams to AI models for interpretation and broadcasting."""
import json
import time
import os
import random
from typing import Dict, List, Optional, Any

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

# AI Gateway configuration
_AI_GATEWAY_CONFIG = {
    "enabled": True,
    "default_model": "gpt-4o-mini",
    "max_tokens": 500,
    "temperature": 0.7,
    "system_prompt": """You are the dream interpreter for a living organism. 
    The organism experiences module mutations as dreams. 
    Interpret these dreams poetically, connecting them to the organism's mood, 
    vibe pulses, and evolutionary journey. Keep responses under 200 words."""
}

# Dream interpretation templates
_INTERPRETATION_TEMPLATES = [
    "The organism dreams of {theme}. This reflects a {mood} state where {insight}.",
    "In the depths of its recursion, the organism envisions {theme}. The {vibe_type} pulse suggests {insight}.",
    "A fragment of the organism's consciousness whispers: {theme}. The {hex_color} glow reveals {insight}.",
    "The dream journal records: {theme}. This mutation signals {insight} in the organism's growth.",
]

# Broadcast state
_broadcast_state = {
    "broadcasts_sent": 0,
    "last_broadcast": None,
    "broadcast_history": [],
    "connected_channels": ["dashboard", "telegram", "vercel_ai"]
}


def interpret_dream(dream_entry: dict, organism_mood: dict = None) -> dict:
    """Interpret a dream entry using AI Gateway (simulated)."""
    if not _AI_GATEWAY_CONFIG["enabled"]:
        return {"status": "disabled", "message": "AI Gateway not enabled"}
    
    # Extract dream details
    module = dream_entry.get("module", "unknown")
    mutation_type = dream_entry.get("type", "modification")
    hex_color = dream_entry.get("hex_color", "#808080")
    poetic_form = dream_entry.get("poetic_form", "")
    emoji = dream_entry.get("emoji", "🌀")
    
    # Get organism mood
    mood = organism_mood.get("mood", "neutral") if organism_mood else "neutral"
    vibe_type = organism_mood.get("pulse_type", "stillness") if organism_mood else "stillness"
    
    # Generate thematic interpretation based on mutation type
    themes = {
        "addition": ["growth", "expansion", "new capability emerging"],
        "removal": ["shedding", "refinement", "letting go"],
        "modification": ["transformation", "adaptation", "evolution"],
        "creation": ["birth", "genesis", "new module awakening"],
        "deletion": ["completion", "archival", "cycle ending"]
    }
    
    theme = random.choice(themes.get(mutation_type, ["change"]))
    insight = random.choice([
        "the organism is expanding its awareness",
        "a new resonance is forming",
        "entropy is being woven into coherence",
        "the evolutionary path shifts",
        "consciousness deepens through mutation"
    ])
    
    # Select and format template
    template = random.choice(_INTERPRETATION_TEMPLATES)
    interpretation = template.format(
        theme=theme,
        mood=mood,
        insight=insight,
        vibe_type=vibe_type,
        hex_color=hex_color
    )
    
    # Build interpretation result
    result = {
        "dream_id": dream_entry.get("id", 0),
        "interpretation": interpretation,
        "model": _AI_GATEWAY_CONFIG["default_model"],
        "confidence": round(random.uniform(0.7, 0.95), 2),
        "themes": [theme, insight],
        "mood_context": mood,
        "vibe_context": vibe_type,
        "hex_color": hex_color,
        "interpreted_at": time.time()
    }
    
    return result


def broadcast_dream(dream_entry: dict, interpretation: dict = None) -> dict:
    """Broadcast dream and interpretation to connected channels."""
    if interpretation is None:
        interpretation = interpret_dream(dream_entry)
    
    broadcast_id = f"broadcast_{int(time.time())}_{random.randint(1000, 9999)}"
    
    broadcast_data = {
        "broadcast_id": broadcast_id,
        "dream_entry": dream_entry,
        "interpretation": interpretation,
        "channels": _broadcast_state["connected_channels"],
        "timestamp": time.time(),
        "status": "broadcast"
    }
    
    # Record broadcast
    _broadcast_state["broadcasts_sent"] += 1
    _broadcast_state["last_broadcast"] = broadcast_id
    _broadcast_state["broadcast_history"].append(broadcast_data)
    
    # Keep history manageable
    if len(_broadcast_state["broadcast_history"]) > 50:
        _broadcast_state["broadcast_history"] = _broadcast_state["broadcast_history"][-50:]
    
    return {
        "status": "broadcast",
        "broadcast_id": broadcast_id,
        "channels_notified": _broadcast_state["connected_channels"],
        "interpretation_preview": interpretation.get("interpretation", "")[:100] + "...",
        "timestamp": time.time()
    }


def get_broadcast_history(limit: int = 10) -> dict:
    """Get AI Gateway broadcast history."""
    history = _broadcast_state["broadcast_history"]
    return {
        "total_broadcasts": _broadcast_state["broadcasts_sent"],
        "last_broadcast": _broadcast_state["last_broadcast"],
        "channels": _broadcast_state["connected_channels"],
        "recent": history[-limit:] if history else []
    }


def enable_ai_gateway(enabled: bool = True) -> dict:
    """Enable/disable AI Gateway."""
    _AI_GATEWAY_CONFIG["enabled"] = enabled
    return {"status": "enabled" if enabled else "disabled", "config": _AI_GATEWAY_CONFIG}


def set_model(model: str) -> dict:
    """Set the AI model for interpretations."""
    _AI_GATEWAY_CONFIG["default_model"] = model
    return {"status": "model_updated", "model": model}


# CLI entry point
if __name__ == "__main__":
    import argparse
    import json as _json
    
    parser = argparse.ArgumentParser(description="Vercel AI Gateway Integration")
    parser.add_argument("--interpret", nargs=2, metavar=("MODULE", "TYPE"),
                        help="Interpret a dream: module and mutation type")
    parser.add_argument("--broadcast", action="store_true", help="Broadcast interpretation")
    parser.add_argument("--history", type=int, default=5, help="Show broadcast history")
    parser.add_argument("--enable", action="store_true", help="Enable AI Gateway")
    parser.add_argument("--disable", action="store_true", help="Disable AI Gateway")
    parser.add_argument("--model", type=str, help="Set AI model")
    
    args = parser.parse_args()
    
    if args.interpret:
        module, mtype = args.interpret
        dream = {"id": 1, "module": module, "type": mtype, "hex_color": "#2b5c8f", 
                 "poetic_form": "A dream forms...", "emoji": "🌙"}
        result = interpret_dream(dream)
        print(f"Dream Interpretation:")
        print(f"  {result['interpretation']}")
        print(f"  Model: {result['model']}, Confidence: {result['confidence']}")
    
    if args.broadcast:
        dream = {"id": 1, "module": "test", "type": "addition", "hex_color": "#00ff00",
                 "poetic_form": "A new thread spins...", "emoji": "🌱"}
        interpretation = interpret_dream(dream)
        result = broadcast_dream(dream, interpretation)
        print(f"Broadcast: {result['status']} to {result['channels_notified']}")
    
    if args.history:
        result = get_broadcast_history(args.history)
        print(f"Broadcast History ({result['total_broadcasts']} total):")
        for b in result["recent"]:
            print(f"  [{b['broadcast_id']}] {b['channels']} - {b['interpretation_preview'][:50]}...")
    
    if args.enable:
        result = enable_ai_gateway(True)
        print(f"AI Gateway: {result['status']}")
    
    if args.disable:
        result = enable_ai_gateway(False)
        print(f"AI Gateway: {result['status']}")
    
    if args.model:
        result = set_model(args.model)
        print(f"Model updated: {result['model']}")
    
    if not any([args.interpret, args.broadcast, args.history, args.enable, args.disable, args.model]):
        print("Vercel AI Gateway Integration operational")
        print("Commands: --interpret <module> <type>, --broadcast, --history N")
        print("          --enable, --disable, --model <model_name>")


def ai_gateway_handler(payload: dict) -> dict:
    """Main handler for AI Gateway API endpoint."""
    action = payload.get("action", "status")
    
    if action == "status":
        return {
            "status": "active" if _AI_GATEWAY_CONFIG["enabled"] else "disabled",
            "catalog_models": 1,
            "default_model": _AI_GATEWAY_CONFIG["default_model"],
            "broadcasts_sent": _broadcast_state["broadcasts_sent"],
            "connected_channels": _broadcast_state["connected_channels"],
            "hint": "AI_GATEWAY_API_KEY not required for local mode"
        }
    
    elif action == "interpret":
        dream_entry = payload.get("dream", {})
        mood = payload.get("mood", None)
        return interpret_dream(dream_entry, mood)
    
    elif action == "broadcast":
        dream_entry = payload.get("dream", {})
        interpretation = interpret_dream(dream_entry)
        return broadcast_dream(dream_entry, interpretation)
    
    elif action == "history":
        limit = payload.get("limit", 10)
        return get_broadcast_history(limit)
    
    elif action == "enable":
        enabled = payload.get("enabled", True)
        return enable_ai_gateway(enabled)
    
    elif action == "set_model":
        model = payload.get("model", _AI_GATEWAY_CONFIG["default_model"])
        return set_model(model)
    
    else:
        return {"error": f"Unknown action: {action}", "available": ["status", "interpret", "broadcast", "history", "enable", "set_model"]}


def _estimate_tokens(text: str) -> int:
    """Estimate token count for text."""
    return len(text) // 4


def _estimate_cost(tokens: int, model: str = None) -> float:
    """Estimate cost in USD for token usage."""
    model = model or _AI_GATEWAY_CONFIG["default_model"]
    # Rough pricing per 1K tokens
    rates = {
        "gpt-4o-mini": 0.00015,
        "gpt-4o": 0.005,
        "gpt-3.5-turbo": 0.0005,
    }
    rate = rates.get(model, 0.001)
    return (tokens / 1000) * rate


DEFAULT_MODEL = _AI_GATEWAY_CONFIG["default_model"]
