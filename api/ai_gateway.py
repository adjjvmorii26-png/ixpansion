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




ALEPH_SYSTEM_PROMPT = _AI_GATEWAY_CONFIG.get("system_prompt", _AI_GATEWAY_CONFIG["system_prompt"])


def _gateway_key() -> Optional[str]:
    """Return the configured AI Gateway API key, if any."""
    return os.environ.get("AI_GATEWAY_API_KEY") or os.environ.get("ALEPH_API_KEY")


def _request(path: str, body: Optional[dict] = None, timeout: float = 60.0):
    """POST to the AI Gateway relay. Returns (json_payload, latency_ms).

    Network stub that mirrors the classic /chat/completions contract.
    """
    import urllib.request
    started = time.time()
    key = _gateway_key()
    base = os.environ.get("AI_GATEWAY_BASE_URL", "https://gateway.example.local/v1")
    url = base.rstrip("/") + path
    req = urllib.request.Request(
        url,
        data=json.dumps(body or {}).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key or ''}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8") or "{}")
    return data, round((time.time() - started) * 1000, 1)


def _chat(model: str, messages: List[Dict[str, Any]], *,
          max_tokens: int = 256, temperature: float = 0.7,
          system: Optional[str] = None,
          reasoning_effort: Optional[str] = None) -> Dict[str, Any]:
    """Chat-completion style call through the relay. Returns reply + usage."""
    if not _gateway_key():
        raise RuntimeError("AI_GATEWAY_API_KEY unconfigured")
    system = system or ALEPH_SYSTEM_PROMPT
    body = {"model": model,
            "messages": ([{"role": "system", "content": system}] if system else []) + messages,
            "max_tokens": max_tokens, "temperature": temperature}
    if reasoning_effort:
        body["reasoning_effort"] = reasoning_effort
    data, latency = _request("/chat/completions", body)
    try:
        reply = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        reply = str(data)[:200]
    usage = data.get("usage")
    return {"reply": reply, "usage": usage,
            "cost_est": _estimate_cost(model, usage.get("prompt_tokens", 0) * 4 if usage else 0, 0) if usage else None,
            "latency_ms": latency}


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
    
    key = _gateway_key()
    
    if action in ("status", ""):
        configured = bool(key)
        return {
            "status": "configured" if configured else "unconfigured",
            "catalog_models": 1 if configured else 0,
            "default_model": _AI_GATEWAY_CONFIG["default_model"],
            "broadcasts_sent": _broadcast_state["broadcasts_sent"],
            "connected_channels": _broadcast_state["connected_channels"],
            "hint": "AI_GATEWAY_API_KEY configured" if configured else "AI_GATEWAY_API_KEY not set"
        }
    
    elif action == "estimate":
        model = payload.get("model", _AI_GATEWAY_CONFIG["default_model"])
        inp = payload.get("input", "")
        out = payload.get("output", "")
        est = _estimate_cost(model, inp, out)
        return {"status": "ok", "model": model,
                "tokens_in_est": est["tokens_in_est"],
                "tokens_out_est": est["tokens_out_est"],
                "cost_usd_est": est["cost_usd_est"]}
    
    elif action == "handshake":
        if not key:
            return {"status": "unconfigured", "hint": "AI_GATEWAY_API_KEY not set"}
        model = payload.get("model", _AI_GATEWAY_CONFIG["default_model"])
        try:
            data, latency = _request("/chat/completions", {
                "model": model,
                "messages": [{"role": "user", "content": "SYN"}],
                "max_tokens": 16,
            })
            try:
                reply = data["choices"][0]["message"]["content"]
            except (KeyError, IndexError, TypeError):
                reply = str(data)[:120]
            return {"status": "linked", "model": model, "reply": reply, "latency_ms": latency}
        except Exception as e:  # noqa: BLE001
            return {"status": "unreachable", "error": str(e)[:120], "latency_ms": 0}
    
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
        return {"status": "error", "error": f"unknown action: {action}",
                "available": ["status", "handshake", "estimate", "interpret", "broadcast", "history", "enable", "set_model"]}


def _estimate_tokens(text: str) -> int:
    """Estimate token count for text."""
    return len(text) // 4


def _estimate_cost(*args, **kwargs) -> Any:
    """Estimate cost. Dual interface:

    Old: _estimate_cost(tokens: int, model: str = None) -> float
    New: _estimate_cost(model: str, input_text: str, output_text: str = "") -> dict
    """
    model = _AI_GATEWAY_CONFIG["default_model"]
    rates = {
        "gpt-4o-mini": 0.00015,
        "gpt-4o": 0.005,
        "gpt-3.5-turbo": 0.0005,
        "spacexai/grok-4.6": 0.006,
    }
    # Legacy integer-token interface
    if args and isinstance(args[0], int):
        tokens = args[0]
        if len(args) > 1:
            model = args[1]
        elif kwargs.get("model"):
            model = kwargs["model"]
        rate = rates.get(model, 0.001)
        return (tokens / 1000) * rate

    # New model/input/output interface
    m = args[0] if len(args) > 0 else kwargs.get("model", model)
    inp = args[1] if len(args) > 1 else kwargs.get("input_text", "")
    out = args[2] if len(args) > 2 else kwargs.get("output_text", "")
    tokens_in = max(1, _estimate_tokens(str(inp)))
    tokens_out = max(1, _estimate_tokens(str(out)))
    rate = rates.get(m, 0.001)
    return {
        "model": m,
        "tokens_in_est": tokens_in,
        "tokens_out_est": tokens_out,
        "cost_usd_est": round(((tokens_in + tokens_out) / 1000) * rate, 6),
    }


DEFAULT_MODEL = _AI_GATEWAY_CONFIG["default_model"]
