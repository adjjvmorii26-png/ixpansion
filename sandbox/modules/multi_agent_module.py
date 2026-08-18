#!/usr/bin/env python3
"""Spawn named agents into the sandbox roster."""
from __future__ import annotations
import time

ROLES = {
    "ADJJV-Agent": "owner-intent · product direction",
    "Nexus": "4D organism interface · live canvas",
    "Aegis": "tests · workspace guard",
    "Mycelium": "docs/organs · slow linking",
}

def run(names=None):
    if names is None:
        names = list(ROLES.keys())
    if isinstance(names, str):
        names = [names]
    agents = []
    for n in names:
        agents.append({
            "id": n,
            "role": ROLES.get(n, "generic_agent"),
            "status": "online",
            "inbox": [],
            "outbox": [],
        })
    return {
        "module": "multi_agent_module",
        "count": len(agents),
        "agents": agents,
        "ts": time.time(),
    }
