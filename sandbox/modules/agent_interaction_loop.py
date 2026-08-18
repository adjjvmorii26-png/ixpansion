#!/usr/bin/env python3
"""Round-robin message exchange among roster agents."""
from __future__ import annotations
import json, time
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "output"

def run(*_):
    roster_path = OUT / "multi_agent_module_last.json"
    if roster_path.exists():
        roster = json.loads(roster_path.read_text())["agents"]
    else:
        roster = [
            {"id": "ADJJV-Agent"}, {"id": "Nexus"},
            {"id": "Aegis"}, {"id": "Mycelium"},
        ]
    messages = []
    scripts = {
        "ADJJV-Agent": "Evolve the sandbox; keep it unique.",
        "Nexus": "Rendering 4D field; organisms stable.",
        "Aegis": "I will test whatever you ship next.",
        "Mycelium": "Linking docs to organs; memory warm.",
    }
    for rnd in range(2):
        for i, a in enumerate(roster):
            speaker = a["id"]
            listener = roster[(i + 1) % len(roster)]["id"]
            body = scripts.get(speaker, f"{speaker} pings the mesh")
            messages.append({"round": rnd, "from": speaker, "to": listener, "body": body})
    return {"module": "agent_interaction_loop", "rounds": 2, "messages": messages, "ts": time.time()}
