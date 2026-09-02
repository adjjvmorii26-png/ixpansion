"""Wave 221 — The Organism Commands: Constellation Console.

A command dispatcher that turns a single directed action into a
constellation-wide operation. When the operator says "census all
islands", the console fans the command out across the appropriate
organs and reports a consolidated return.

Commands:
  census      → census every island (island_census)
  epitaphs    → read the epitaph archive (bridge_epitaphs)
  cascades    → cascade state (resonance_cascade)
  lifecycles  → stone lifecycle report (bridge_lifecycle)
  topology    → constellation topology (constellation_topology)
  rhythm      → rhythm pulse (rhythm_pulse)
  sentinel    → web health (resonance_sentinel)
"""
from __future__ import annotations

from typing import Any, Dict

_COMMANDS = {
    "census": ("api.island_census", "census"),
    "epitaphs": ("api.bridge_epitaphs", "all"),
    "cascades": ("api.resonance_cascade", "state"),
    "lifecycles": ("api.bridge_lifecycle", "report"),
    "topology": ("api.constellation_topology", "map"),
    "rhythm": ("api.rhythm_pulse", "pulse"),
    "sentinel": ("api.resonance_sentinel", "report"),
}


def _run(module_path: str, action: str) -> Dict[str, Any]:
    try:
        mod = __import__(module_path, fromlist=["handler"])
        if action == "all":
            return mod.handler({})
        return mod.handler({"action": action})
    except Exception as exc:
        return {"error": str(exc)}


def coherence_vitals() -> Dict[str, Any]:
    return {"layer": "console", "status": "dispatching", "resonance": 0.86, "wave": 221}


def resonates_with() -> list:
    return ["command", "console", "dispatch", "federation", "orchestrate", "constellation-wide"]


def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    payload = payload or {}
    context = context or {}
    action = payload.get("action", "list")
    command = payload.get("command", "")

    if command in _COMMANDS:
        module_path, cmd_action = _COMMANDS[command]
        result = _run(module_path, cmd_action)
        return {"command": command, "status": "executed", "result": result}

    if action == "list":
        return {
            "commands": sorted(_COMMANDS.keys()),
            "note": "One command, whole archipelago.",
        }

    if action == "storm":
        results = {}
        for name, (module_path, cmd_action) in _COMMANDS.items():
            results[name] = _run(module_path, cmd_action)
        return {"status": "storming", "dispatch": results}

    return {"status": "active", "note": "Send ?command=census to fan out a command.",
            "commands": sorted(_COMMANDS.keys())}
