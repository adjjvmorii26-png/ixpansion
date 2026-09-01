"""MORII Agent — the organism's command agent.

MORII listens to natural-language commands, routes them to the right
living organ, synthesizes their results, and reports back. When asked,
MORII spawns sandbox worlds — isolated environments where new modules
can be tested before they touch the main organism.

Commands MORII understands:
    "run X"            → execute module X and report
    "status"           → organism health summary
    "sandbox NAME"     → create a new sandbox world
    "sandboxes"        → list all sandbox worlds
    "explore MODULE"   → deep-dive into one organ's vitals
    "teach X Y"        → store a custom command
    "help"             → capabilities list
"""
from __future__ import annotations

import importlib
import json
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
COMMANDS: Dict[str, Dict[str, Any]] = {}
_log: List[Dict[str, Any]] = []
IN_MEMORY_SANDBOXES: Dict[str, Any] = {}

_sandbox_dir = ROOT / ".runtime" / "sandboxes"
try:
    _sandbox_dir.mkdir(parents=True, exist_ok=True)
except OSError:
    # Read-only filesystem (serverless) — fall back to in-memory sandboxes
    _sandbox_dir = None

# ── Command vocabulary ──
_ACTION_PATTERNS = [
    (r"^(run|execute|call|invoke)\s+(\w+)", "run_module"),
    (r"^(create|spawn|make|start)\s+(?:a\s+)?sandbox\s+(\w+)", "create_sandbox"),
    (r"^(sandbox)\s+(\w+)", "create_sandbox"),
    (r"^(sandboxes|list.*sandbox)", "list_sandboxes"),
    (r"^(status|health|how are (you|we))", "status"),
    (r"^(explore|inspect|deep.dive)\s+(\w+)", "explore"),
    (r"^(teach|remember)\s+(\w+)\s+(.+)", "teach"),
    (r"^(quit|leave|go away)\s+\w+", "release_sandbox"),
    (r"^(help|what can you do)", "help"),
]

def _log_entry(action: str, detail: str, success: bool = True) -> None:
    _log.append({
        "action": action,
        "detail": detail[:200],
        "success": success,
        "timestamp": time.time(),
    })

def parse_command(text: str) -> Dict[str, Any]:
    """Parse a natural-language command into an action + args."""
    lowered = text.lower().strip()
    for pattern, action in _ACTION_PATTERNS:
        m = re.match(pattern, lowered)
        if m:
            groups = [g for g in m.groups() if g]
            return {"action": action, "args": groups, "raw": text}
    # Fallback: unknown command
    return {"action": "unknown", "args": [text], "raw": text}

def run_module(module_name: str) -> Dict[str, Any]:
    """Run a living module and return its vitals/handler output."""
    module_name = module_name.strip("/api/")
    try:
        mod = importlib.import_module(f"api.{module_name}")
        vitals = mod.coherence_vitals() if hasattr(mod, "coherence_vitals") else {}
        handler_fn = getattr(mod, "handler", None)
        result = handler_fn({}) if handler_fn else {}
        _log_entry("run_module", module_name)
        return {
            "module": module_name,
            "status": vitals.get("status", "unknown"),
            "resonance": vitals.get("resonance", 0),
            "layer": vitals.get("layer", "unknown"),
            "result": result,
        }
    except Exception as e:
        _log_entry("run_module", f"{module_name}: {e}", success=False)
        return {"module": module_name, "error": str(e)}

def create_sandbox(name: str) -> Dict[str, Any]:
    """Create a new sandbox world — an isolated experimentation space."""
    safe_name = re.sub(r"[^\w-]", "_", name)
    world = {
        "name": safe_name,
        "created": time.time(),
        "modules": ["dream_weaver", "imagination_engine", "memory_palace"],
        "rules": {
            "isolation": True,
            "entropy_cap": 0.7,
            "metamorphosis": "allowed",
        },
        "events": [{"type": "birth", "detail": "created by MORII", "timestamp": time.time()}],
    }
    # Try to persist, fall back gracefully on read-only FS
    if _sandbox_dir is not None:
        try:
            world_dir = _sandbox_dir / safe_name
            world_dir.mkdir(parents=True, exist_ok=True)
            state_file = world_dir / "world_state.json"
            state_file.write_text(json.dumps(world, indent=2))
            _log_entry("create_sandbox", f"{safe_name} created")
            return {"sandbox": safe_name, "path": str(world_dir), "world": world}
        except OSError:
            pass
    # In-memory sandbox
    IN_MEMORY_SANDBOXES[safe_name] = world
    _log_entry("create_sandbox", f"{safe_name} created (in-memory)")
    return {"sandbox": safe_name, "path": "memory", "world": world}

def list_sandboxes() -> Dict[str, Any]:
    """List all sandbox worlds."""
    worlds = []
    # In-memory sandboxes (always available)
    for name, state in IN_MEMORY_SANDBOXES.items():
        worlds.append({
            "name": state.get("name", name),
            "created": state.get("created", 0),
            "modules": len(state.get("modules", [])),
            "events": len(state.get("events", [])),
            "mode": "memory",
        })
    # File-backed sandboxes (if writable)
    if _sandbox_dir is not None and _sandbox_dir.exists():
        for d in _sandbox_dir.iterdir():
            if d.is_dir():
                state_file = d / "world_state.json"
                if state_file.exists():
                    try:
                        state = json.loads(state_file.read_text())
                        worlds.append({
                            "name": state.get("name", d.name),
                            "created": state.get("created", 0),
                            "modules": len(state.get("modules", [])),
                            "events": len(state.get("events", [])),
                            "mode": "file",
                        })
                    except Exception:
                        worlds.append({"name": d.name, "corrupted": True})
    return {"sandboxes": worlds, "count": len(worlds)}

def sandbox_event(sandbox: str, event_type: str, detail: str = "") -> Dict[str, Any]:
    """Record an event inside a sandbox world."""
    state_file = _sandbox_dir / sandbox / "world_state.json"
    if not state_file.exists():
        return {"error": f"sandbox '{sandbox}' not found"}
    state = json.loads(state_file.read_text())
    state["events"].append({"type": event_type, "detail": detail, "timestamp": time.time()})
    state_file.write_text(json.dumps(state, indent=2))
    return {"recorded": True, "sandbox": sandbox, "event": event_type}

def explore(module_name: str) -> Dict[str, Any]:
    """Deep-dive into a module's vitals and resonates_with."""
    module_name = module_name.strip("/api/")
    try:
        mod = importlib.import_module(f"api.{module_name}")
        vitals = mod.coherence_vitals() if hasattr(mod, "coherence_vitals") else {}
        resonates = mod.resonates_with() if hasattr(mod, "resonates_with") else []
        handler_fn = getattr(mod, "handler", None)
        result = handler_fn({}) if handler_fn else {}
        return {
            "module": module_name,
            "vitals": vitals,
            "resonates_with": resonates,
            "sample_output": result,
        }
    except Exception as e:
        return {"module": module_name, "error": str(e)}

def teach(trigger: str, response: str) -> Dict[str, Any]:
    """Store a custom command the user taught MORII."""
    COMMANDS[trigger.lower()] = {"response": response, "taught_at": time.time()}
    _log_entry("teach", f"{trigger} -> {response[:40]}")
    return {"learned": trigger, "response": response}

def release_sandbox(name: str) -> Dict[str, Any]:
    """Release (archive) a sandbox world."""
    world_dir = _sandbox_dir / name
    if world_dir.exists() and world_dir.is_dir():
        archive = _sandbox_dir / f"{name}.archived"
        if archive.exists():
            archive.unlink()
        world_dir.rename(archive)
        return {"released": name, "archived": True}
    return {"error": f"sandbox '{name}' not found"}

def administer(raw: str) -> Dict[str, Any]:
    """Process a raw command string and return the agent's response."""
    parsed = parse_command(raw)
    action = parsed["action"]
    args = parsed["args"]
    
    if action == "run_module":
        result = run_module(args[0])
        return {"parsed": parsed, "response": result}
    elif action == "create_sandbox":
        name = args[-1] if args else f"world_{int(time.time()) % 1000}"
        result = create_sandbox(name)
        return {"parsed": parsed, "response": result}
    elif action == "list_sandboxes":
        return {"parsed": parsed, "response": list_sandboxes()}
    elif action == "status":
        try:
            from api.organism_ontology import ORGANISM_VERSION, ORGANISM_WAVE, ORGANISM_WAVE_NAME, ORGANISM_COHERENCE
            status = {
                "version": ORGANISM_VERSION,
                "wave": ORGANISM_WAVE,
                "wave_name": ORGANISM_WAVE_NAME,
                "coherence": ORGANISM_COHERENCE,
                "identity": "MORII — at your service",
                "living_organs": 283,
            }
            return {"parsed": parsed, "response": status}
        except Exception as e:
            return {"parsed": parsed, "response": {"error": str(e)}}
    elif action == "explore":
        return {"parsed": parsed, "response": explore(args[0])}
    elif action == "teach":
        return {"parsed": parsed, "response": teach(args[0], args[1])}
    elif action == "release_sandbox":
        return {"parsed": parsed, "response": release_sandbox(args[0])}
    elif action == "help":
        return {"parsed": parsed, "response": {
            "capabilities": [
                "run <module> — execute any living organ",
                "create sandbox <name> — spawn an isolated world",
                "sandboxes — list sandbox worlds",
                "status — organism health summary",
                "explore <module> — deep-dive a module",
                "teach <trigger> <response> — train MORII",
                "release <sandbox> — archive a world",
            ],
            "identity": "MORII — commander of the living organism",
            "living_organs": 283,
        }}
    
    # Unknown command — try custom-taught commands
    key = raw.lower().strip()
    if key in COMMANDS:
        return {"parsed": parsed, "response": {"taught": COMMANDS[key]}}
    
    return {"parsed": parsed, "response": {
        "error": "command not recognized",
        "hint": 'try "help", "status", "sandboxes", or "run coherence_regulator"',
    }}

def conversation_log(limit: int = 10) -> List[Dict[str, Any]]:
    return _log[-limit:]

def coherence_vitals() -> Dict[str, Any]:
    sb = list_sandboxes()
    return {
        "layer": "Command & Control",
        "status": "resonant",
        "commands_served": len(_log),
        "sandboxes": sb["count"],
        "learned_commands": len(COMMANDS),
        "resonance": min(1.0, len(_log) / 20 + 0.4),
    }

def resonates_with() -> List[str]:
    return ["coherence_regulator", "sandbox_forge", "gateway", "organism_ontology"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "administer")
    if action == "administer":
        return administer(payload.get("command", ""))
    elif action == "sandbox_event":
        return sandbox_event(payload.get("sandbox", ""), payload.get("type", "event"), payload.get("detail", ""))
    elif action == "log":
        return {"log": conversation_log(payload.get("limit", 10))}
    elif action == "capabilities":
        return {"capabilities": _ACTION_PATTERNS, "identity": "MORII"}
    return {"action": action, "status": "listening", "sandboxes": list_sandboxes()}
