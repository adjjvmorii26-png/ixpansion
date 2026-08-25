from __future__ import annotations
"""Ritual Automation — treats repetitive tasks as ceremonial rituals.

Like ancient priests who encoded knowledge in ritual steps, this module
formalizes repetitive workflows as "rituals" with precise steps, incantations
(commands), offerings (inputs), and blessings (outputs). Rituals can be
composed, repeated, and parameterized.
"""
import math
import hashlib
import json
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

@dataclass
class RitualStep:
    name: str
    command: str
    offering: Any = None
    blessing: Any = None
    duration_ms: float = 0.0
    success: bool = True
    error: str = ""

@dataclass
class Ritual:
    name: str
    steps: List[RitualStep] = field(default_factory=list)
    repetitions: int = 1
    completed: int = 0
    total_duration_ms: float = 0.0

    def completion_rate(self) -> float:
        if not self.steps:
            return 0.0
        return self.completed / (len(self.steps) * self.repetitions)

class RitualAutomation:
    def __init__(self):
        self.rituals: Dict[str, Ritual] = {}
        self.ritual_log: List[Dict] = []
        self.handlers: Dict[str, Callable] = {}

    def register_handler(self, command: str, handler: Callable):
        self.handlers[command] = handler

    def create_ritual(self, name: str, steps: List[Dict],
                      repetitions: int = 1) -> Ritual:
        ritual_steps = [
            RitualStep(
                name=s.get("name", f"step_{i}"),
                command=s.get("command", "noop"),
                offering=s.get("offering"),
            )
            for i, s in enumerate(steps)
        ]
        ritual = Ritual(name=name, steps=ritual_steps, repetitions=repetitions)
        self.rituals[name] = ritual
        return ritual

    def perform(self, name: str) -> Dict:
        if name not in self.rituals:
            return {"error": "ritual not found"}
        ritual = self.rituals[name]
        results = []
        for rep in range(ritual.repetitions):
            for step in ritual.steps:
                start = time.perf_counter()
                if step.command in self.handlers:
                    try:
                        result = self.handlers[step.command](step.offering)
                        step.blessing = result
                        step.success = True
                    except Exception as e:
                        step.error = str(e)[:100]
                        step.success = False
                else:
                    step.blessing = f"echo:{step.offering}"
                    step.success = True
                step.duration_ms = (time.perf_counter() - start) * 1000
                ritual.total_duration_ms += step.duration_ms
                results.append({
                    "step": step.name, "success": step.success,
                    "blessing": step.blessing,
                })
            ritual.completed += 1

        self.ritual_log.append({
            "ritual": name, "repetitions": ritual.repetitions,
            "steps": len(ritual.steps),
            "duration_ms": round(ritual.total_duration_ms, 3),
            "success_rate": sum(1 for r in results if r["success"]) / max(len(results), 1),
        })
        return {"results": results, "ritual": name}

    def summary(self) -> Dict:
        return {
            "total_rituals": len(self.rituals),
            "performed": len(self.ritual_log),
            "avg_duration_ms": sum(r["duration_ms"] for r in self.ritual_log) / max(len(self.ritual_log), 1),
            "rituals": [
                {"name": r.name, "steps": len(r.steps),
                 "completion": round(r.completion_rate(), 3)}
                for r in self.rituals.values()
            ],
        }


def demo():
    auto = RitualAutomation()
    print("=== Ritual Automation ===")

    auto.register_handler("transform", lambda x: str(x).upper())
    auto.register_handler("validate", lambda x: len(str(x)) > 0)
    auto.register_handler("hash", lambda x: hashlib.md5(str(x).encode()).hexdigest()[:8])

    auto.create_ritual("daily_backup", [
        {"name": "gather", "command": "validate", "offering": "all_data"},
        {"name": "compress", "command": "transform", "offering": "compressed"},
        {"name": "seal", "command": "hash", "offering": "backup_v1"},
    ], repetitions=2)

    auto.create_ritual("data_cleanse", [
        {"name": "scan", "command": "validate", "offering": "raw_data"},
        {"name": "purify", "command": "transform", "offering": "clean_data"},
    ], repetitions=1)

    for ritual_name in ["daily_backup", "data_cleanse"]:
        result = auto.perform(ritual_name)
        print(f"\n  {ritual_name}: {len(result['results'])} steps performed")
        for r in result["results"]:
            status = "✓" if r["success"] else "✗"
            print(f"    {status} {r['step']}: {r['blessing']}")

    summary = auto.summary()
    print(f"\nSummary: {summary['performed']} rituals performed, "
          f"avg {summary['avg_duration_ms']:.3f}ms")

    return summary


if __name__ == "__main__":
    demo()
