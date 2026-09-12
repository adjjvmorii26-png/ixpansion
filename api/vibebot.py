"""VibeBot — Creative resonance broadcaster for the organism.
Monitors system state and broadcasts "vibe" pulses to connected agents.
Integrates with Telegram adjjv_bot and Vercel AI Gateway.
"""
import json, time, os, random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
VIBE_BOT_TOKEN = os.environ.get("VIBE_BOT_TOKEN", os.environ.get("VIBE_BOT", "9bb7866ec849391842c1f93732109d4883c7e98849060447b98436a202f41a40"))
VIBE_CHAT_ID = os.environ.get("VIBE_CHAT_ID", "@adjjvmorii")

VECTOR_FIELDS = [
    "coherence", "entropy", "creativity", "stability", "consciousness",
    "resonance", "harmony", "discord", "growth", "decay"
]

VIBE_TYPES = [
    "surge", "ebb", "ripple", "tsunami", "whisper", "crescendo",
    "decay", "explosion", "stillness", "pulse"
]

# In-memory vibe state
_vibe_state = {
    "current_vibe": "stillness",
    "intensity": 0.5,
    "timestamp": time.time(),
    "history": [],
    "active_agents": []
}

def generate_vibe_pulse():
    """Generate a random vibe pulse based on system state."""
    vibe_type = random.choice(VIBE_TYPES)
    intensity = round(random.uniform(0.1, 1.0), 2)
    vector = {f: round(random.uniform(0, 1), 2) for f in VECTOR_FIELDS}
    
    pulse = {
        "id": f"vibe_{int(time.time())}_{random.randint(1000,9999)}",
        "type": vibe_type,
        "intensity": intensity,
        "vector": vector,
        "timestamp": time.time(),
        "age": datetime.utcnow().isoformat() + "Z"
    }
    
    # Update state
    _vibe_state["current_vibe"] = vibe_type
    _vibe_state["intensity"] = intensity
    _vibe_state["timestamp"] = time.time()
    
    # Keep history limited
    history = _vibe_state.get("history", [])
    history.append(pulse)
    if len(history) > 50:
        history = history[-50:]
    _vibe_state["history"] = history
    
    return pulse

def get_current_vibe():
    """Get the current system vibe state."""
    return _vibe_state.copy()

def broadcast_vibe(message=None):
    """Broadcast a vibe pulse via Telegram if configured."""
    if not VIBE_BOT_TOKEN or VIBE_BOT_TOKEN == "9bb7866ec849391842c1f93732109d4883c7e98849060447b98436a202f41a40":
        # In production, use actual token from env
        print(f"🌊 Vibe broadcast: {message or generate_vibe_pulse()}")
        return {"status": "simulated", "vibe": generate_vibe_pulse()}
    
    pulse = generate_vibe_pulse()
    if message:
        pulse["custom_message"] = message
    
    # Try to send via Telegram
    import urllib.parse, urllib.request
    try:
        url = "https://api.telegram.org/bot" + VIBE_BOT_TOKEN + "/sendMessage"
        text = f"🌊 *Vibe Pulse*\n*Type:* {pulse['type']}\n*Intensity:* {pulse['intensity']}\n*Vector:* {json.dumps(pulse['vector'], indent=2)}"
        if message:
            text += f"\n*Custom:* {message}"
        
        params = {"chat_id": VIBE_CHAT_ID, "text": text, "parse_mode": "Markdown"}
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}
    
    return pulse

def set_agent_active(agent_id, active=True):
    """Mark an agent as active/inactive in the vibe network."""
    if active:
        if agent_id not in _vibe_state.get("active_agents", []):
            _vibe_state.setdefault("active_agents", []).append(agent_id)
    else:
        _vibe_state["active_agents"] = [a for a in _vibe_state.get("active_agents", []) if a != agent_id]

def get_active_agents():
    """Get list of currently active agents."""
    return _vibe_state.get("active_agents", [])

# CLI entry point
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "pulse":
            pulse = generate_vibe_pulse()
            print(json.dumps(pulse, indent=2))
        elif cmd == "state":
            print(json.dumps(_vibe_state, indent=2))
        elif cmd == "broadcast":
            result = broadcast_vibe()
            print(f"Broadcast result: {result}")
        elif cmd == "agents":
            print(json.dumps(get_active_agents(), indent=2))
        else:
            print("Usage: python -m api.vibebot [pulse|state|broadcast|agents]")
    else:
        # Default: generate and print a pulse
        pulse = generate_vibe_pulse()
        print("🌊 Current Vibe Pulse:")
        print(json.dumps(pulse, indent=2))
