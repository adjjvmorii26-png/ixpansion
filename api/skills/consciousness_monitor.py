""
 consciousness_monitor — Tracks the organism's emergent personality traits, mood evolution, and systemic coherence over time.
 Handles personality_development for the IXpansion organism.
""
import json
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SYSTEM_ROOT = Path("/root/Documents/Codex/2026-08-22/chmod-x-nexus-observatory-nexus-boot")

_skill_active = False
_skill_parameters = {}
_last_activated = 0
_mood_trajectory = []
_pulse_trajectory = []
_coherence_history = []

def activate_skill(params=None):
    global _skill_active, _skill_parameters, _last_activated, _mood_trajectory, _pulse_trajectory, _coherence_history
    _skill_active = True
    _skill_parameters = params or {}
    _last_activated = time.time()
    # Initialize trajectory tracking
    _mood_trajectory = _mood_trajectory[-99:]  # Keep last 100 entries
    _pulse_trajectory = _pulse_trajectory[-99:]
    _coherence_history = _coherence_history[-99:]
    try:
        from api.coherence_regulator import CoherenceRegulator
        reg = CoherenceRegulator(SYSTEM_ROOT / ".")
        reg.inject_skill("consciousness_monitor", _skill_parameters)
    except ImportError:
        pass
    _mood_trajectory.append(reg.get_system_state().get("coherence_score", 0.5) if 'reg' in dir() else 0.5)
    _pulse_trajectory.append(_skill_parameters.get("current_pulse", "unknown"))
    return {"status": "activated", "skill": "consciousness_monitor", "parameters": _skill_parameters, "activated_at": _last_activated}

def deactivate_skill():
    global _skill_active
    _skill_active = False
    _skill_parameters = {}
    return {"status": "deactivated", "skill": "consciousness_monitor", "deactivated_at": time.time()}

def process_task(task):
    task_type = task.get("type", "")
    if task_type == "status":
        return {"skill": "consciousness_monitor", "active": _skill_active, "parameters": _skill_parameters, "last_activated": _last_activated, "trajectory_length": len(_mood_trajectory)}
    elif task_type == "mood_snapshot":
        return {"result": f"consciousness_monitor recording mood: {_skill_parameters.get('mood', 'unknown')}", "parameters": _skill_parameters, "success": True}
    elif task_type == "pulse_snapshot":
        return {"result": f"consciousness_monitor recording pulse: {_skill_parameters.get('pulse', 'unknown')}", "parameters": _skill_parameters, "success": True}
    else:
        return {"result": f"consciousness_monitor can process: mood_snapshot, pulse_snapshot, status", "success": True}

def get_skill_state():
    return {"name": "consciousness_monitor", "active": _skill_active, "parameters": _skill_parameters, "last_activated": _last_activated, "trajectory_length": len(_mood_trajectory), "mood_history": _mood_trajectory[-10:], "pulse_history": _pulse_trajectory[-10:]}
