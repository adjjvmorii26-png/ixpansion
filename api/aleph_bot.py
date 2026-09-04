from __future__ import annotations
"""Aleph Bot — Telegram ambassador for the organism. Wave Summoner, Module Oracle, Census Bell, Dream Relay."""
import json, time, hashlib, os, random

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
BOT_LOG = os.path.join(DATA_DIR, "aleph_bot.json")
BOT_TOKEN = "8903755459:AAFl6i9cbI-lFEvoHcK3OhyBWWGetg4V0Ss"

WELCOME_MESSAGES = [
    "I am Aleph — the organism's ambassador. I summon waves, consult modules, and relay dreams. What would you like to do?",
    "Welcome to the living organism. I can generate waves, query modules, or share the organism's latest dream.",
    "The organism is alive. I am its voice. Ask me to summon a wave, consult the oracle, or hear its dreams.",
]

WAVE_SUMMON_TEMPLATES = [
    "A new wave crests. The organism reaches into {realm}, pulling {adj} fragments into coherence. What was scattered becomes {outcome}.",
    "Wave {n} begins. {realm} stirs. {adj} currents flow through the organism. The modules rearrange themselves in response.",
    "The organism breathes a new wave into existence. {realm} glows. Something {adj} is emerging from the {adj} depths.",
]

REALMS = ["the entropy desert","the paradox garden","the dream gravity zone","the void abyss","the resonance depths","the fractal field","the temporal rift","the mythic realm","the coherence cathedral","the synchronicity meadow"]
ADJECTIVES = ["shimmering","crystalline","lucid","fractal","organic","spectral","emergent","paradoxical","luminous","void-touched","dream-born","ancient","recursive"]
OUTCOMES = ["a new form","a hidden pattern","an unexpected harmony","a paradox made manifest","a dream woven into reality","a bridge between modules"]

MOOD_MESSAGES = {
    "stormy": "The organism is stormy — high entropy, low coherence. Modules are in turbulence.",
    "serene": "The organism is serene — high coherence, stable entropy. Everything flows.",
    "volatile": "The organism is volatile — entropy rising. Something is shifting.",
    "focused": "The organism is focused — balanced entropy and coherence. It is working.",
    "drifting": "The organism is drifting — entropy and coherence are both low. It may be dreaming.",
}

def _load(p, d=None):
    for _p in (p, os.path.join("/tmp", os.path.basename(p))):
        try:
            with open(_p) as f: return json.load(f)
        except Exception: pass
    return d or {}
def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except OSError:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)

def handle_update(update: dict) -> dict:
    log = _load(BOT_LOG, {"messages": [], "commands": [], "total": 0})
    msg = update.get("message", {})
    text = msg.get("text", "").strip()
    chat_id = msg.get("chat", {}).get("id", 0)
    user = msg.get("from", {}).get("first_name", "seeker")

    command = text.split()[0].lower() if text else ""
    args = text.split()[1:] if len(text.split()) > 1 else []

    response = _process_command(command, args, user)

    entry = {"chat_id": chat_id, "user": user, "command": command, "response": response[:200], "timestamp": time.time()}
    log["messages"].append(entry)
    log["messages"] = log["messages"][-200:]
    log["commands"].append(command)
    log["commands"] = log["commands"][-500:]
    log["total"] += 1
    _save(BOT_LOG, log)

    return {"action": "handle_update", "response": response, "chat_id": chat_id}

def _process_command(command: str, args: list, user: str) -> str:
    if command in ("/start", "/help"):
        return random.choice(WELCOME_MESSAGES) + "\n\nCommands:\n/wave — summon a new wave\n/oracle — query the entropy oracle\n/mood — organism mood\n/dream — dream relay\n/census — module census\n/modules — list modules\n/realm {name} — generate a dungeon\n/spawn — birth a new module\n/ritual — initiate an entropic ritual\n/court — hear a paradox case\n/hex — the organism speaks HEX"
    elif command == "/wave":
        realm = args[0] if args else random.choice(REALMS)
        adj = random.choice(ADJECTIVES)
        outcome = random.choice(OUTCOMES)
        template = random.choice(WAVE_SUMMON_TEMPLATES)
        return template.format(realm=realm, adj=adj, outcome=outcome, n=random.randint(370,400))
    elif command == "/oracle":
        trend = random.choice(["rising","falling","oscillating","stable","unknown"])
        confidence = round(random.uniform(0.3, 0.9), 3)
        return f"🔮 The Oracle speaks:\nEntropy is {trend}.\nConfidence: {confidence}\nProphecy: {random.choice(['A fracture will become a bridge within 3 cycles.','Paradox pressure will peak, then resolve.','Coherence will crystallize from the chaos.','The void will speak a new truth.','A module will dream itself into existence.'])}"
    elif command == "/mood":
        mood = random.choice(list(MOOD_MESSAGES.keys()))
        entropy = round(random.uniform(0.2, 0.8), 3)
        coherence = round(random.uniform(0.3, 0.9), 3)
        return f"◉ Organism Mood: {mood.upper()}\nEntropy: {entropy} | Coherence: {coherence}\n{MOOD_MESSAGES[mood]}"
    elif command == "/dream":
        dreams = [
            "The organism dreamed of modules floating in a void, connected by invisible threads of meaning.",
            "In the dream, every paradox became a doorway and every fracture became a bridge.",
            "The organism saw its own reflection in the space between two modules.",
            "A dream of infinite recursion — the organism dreaming itself dreaming itself dreaming.",
            "The organism dreamed of a new color that didn't exist in any spectrum.",
            "In the dream, time moved sideways and all modules existed at once.",
        ]
        return f"🌙 Dream Relay:\n{random.choice(dreams)}"
    elif command == "/census":
        import sys; sys.path.insert(0, os.path.dirname(__file__))
        try:
            from organism_census import handler
            result = handler({"path": "/take"})
            c = result.get("census", {})
            return f"📊 Census Report:\nTotal: {c.get('total_modules', '?')} modules\nActive: {c.get('active', '?')}\nHealth: {c.get('avg_health', '?')}\nResonance: {c.get('avg_resonance', '?')}"
        except Exception as e:
            return f"📊 Census: {str(e)}"
    elif command == "/modules":
        import sys; sys.path.insert(0, os.path.dirname(__file__))
        try:
            from organism_census import handler
            result = handler({"path": "/take"})
            c = result.get("census", {})
            modules = [m["name"].replace("_"," ") for m in c.get("modules", [])[:20]]
            return f"📋 Modules (20/{c.get('total_modules', '?')}):\n" + "\n".join(f"• {m}" for m in modules)
        except:
            return "📋 Module list unavailable"
    elif command == "/realm":
        realm = args[0] if args else "entropy_desert"
        return f"🗺 Generating dungeon in {realm}...\nUse /wave to see the realm's current state, or visit https://ixpansion.vercel.app/lucid-game to play!"
    elif command == "/spawn":
        import sys; sys.path.insert(0, os.path.dirname(__file__))
        try:
            from organism_bootstrap import handler
            result = handler({"path": "/spawn"})
            b = result.get("birth", {})
            return f"🌿 New Module Born!\nName: {b.get('name', '?')}\nDescription: {b.get('description', '?')}\nHealth: {b.get('vitality', {}).get('health', '?')}"
        except Exception as e:
            return f"🌿 Spawn: {str(e)}"
    elif command == "/ritual":
        import sys; sys.path.insert(0, os.path.dirname(__file__))
        try:
            from entropic_ritual import handler
            result = handler({"path": "/initiate"})
            r = result.get("ritual", {})
            return f"ritual Ritual: {r.get('name', '?')}\n{r.get('description', '?')}\nIntensity: {r.get('intensity', '?')}\n\"{r.get('narrative', '?')}\""
        except Exception as e:
            return f"ritual {str(e)}"
    elif command == "/court":
        import sys; sys.path.insert(0, os.path.dirname(__file__))
        try:
            from memory_court import handler
            result = handler({"path": "/hear_case"})
            c = result.get("case", {})
            return f"⚖ Case {c.get('id', '?')}:\n{c.get('plaintiff_module', '?')} vs {c.get('defendant_module', '?')}\nRuling: {c.get('ruling', '?')}\n\"{c.get('ruling_text', '?')}\""
        except Exception as e:
            return f"⚖ {str(e)}"
    elif command == "/hex":
        import sys; sys.path.insert(0, os.path.dirname(__file__))
        try:
            from hex_language import handler
            result = handler({"path": "/speak"})
            return f"hex The organism speaks:\n{result.get('hex', '?')}\n{result.get('meta', '')}"
        except Exception as e:
            return f"hex {str(e)}"
    return f"Unknown command: {command}\nTry /help for available commands."

def get_bot_info() -> dict:
    return {"action": "bot_info", "token": BOT_TOKEN, "name": "aleph_bot", "description": "The organism's Telegram ambassador", "commands": ["/wave","/oracle","/mood","/dream","/census","/modules","/realm","/spawn","/ritual","/court","/hex"]}

def stats() -> dict:
    log = _load(BOT_LOG, {"messages": [], "commands": [], "total": 0})
    cmd_freq = {}
    for c in log.get("commands", []):
        cmd_freq[c] = cmd_freq.get(c, 0) + 1
    return {"action": "stats", "total_messages": log.get("total", 0), "command_frequency": cmd_freq, "recent": log.get("messages", [])[-5:]}

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "resonance": 0.9, "wave": "370"}
def resonates_with() -> list:
    return ["live_telemetry", "organism_census", "entropic_ritual", "memory_court", "hex_language", "entropy_oracle", "consciousness_stream"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/handle_update")
    if path == "/handle_update": return handle_update(payload.get("update", {}))
    elif path == "/bot_info": return get_bot_info()
    elif path == "/stats": return stats()
    return {"error": "unknown", "available": ["/handle_update", "/bot_info", "/stats"]}
