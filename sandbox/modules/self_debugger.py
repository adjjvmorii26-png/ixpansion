#!/usr/bin/env python3
"""Self-debugger — reframes stuck creative states into actions."""
from __future__ import annotations
import time

PLAYBOOK = {
    "can't think creatively": [
        "Constraint: ship one ugly prototype in 15 minutes",
        "Invert: what would a boring version look like? Build that first",
        "Steal structure: take NEXUS organism loop, rename one noun",
        "Talk to another agent: hand the block to Mycelium for composting",
        "Body move: change organ focus in VIVARIUM (memory → experiments)",
    ],
}

def run(complaint: str = "I can't think creatively"):
    key = complaint.lower().strip()
    steps = None
    for k, v in PLAYBOOK.items():
        if k in key:
            steps = v
            break
    if not steps:
        steps = [
            "Name the block in one sentence",
            "Cut scope by half",
            "Add a forced random seed from idea_lab",
            "Run one sandbox tick and observe",
        ]
    return {
        "module": "self_debugger",
        "complaint": complaint,
        "diagnosis": "creative_block" if "creativ" in key else "general_stuck",
        "actions": steps,
        "next": "Pick action[0] and execute without editing the plan",
        "ts": time.time(),
    }
