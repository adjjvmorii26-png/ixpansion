#!/usr/bin/env python3
"""Dream buffer — idle mutations of task proposals."""
from __future__ import annotations
import json, time
from pathlib import Path
from random import Random

class DreamBuffer:
    def __init__(self, path: str | Path = "content_output/dreams.jsonl", seed: int = 0):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.rng = Random(seed)
    def dream(self, prompt: str) -> dict:
        mut = {
            "ts": time.time(),
            "seed_prompt": prompt,
            "mutation": self.rng.choice([
                "invert constraints", "halve particle count",
                "prefer green organ", "require dual HITL", "run lumen first",
            ]),
            "priority": round(self.rng.random(), 3),
        }
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(mut) + "\n")
        return mut
