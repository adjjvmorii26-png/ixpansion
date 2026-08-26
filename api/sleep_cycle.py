"""Sleep Cycle — system-wide rest states that optimize and reorganize.

The system doesn't run at full capacity 24/7. It cycles through sleep
phases: light sleep (reduced load), deep sleep (consolidation), REM
(creative recombination), and wake (full operation). Each phase serves
a different optimization function.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SLEEP_PHASES = {
    "awake": {"load": 1.0, "creativity": 0.5, "consolidation": 0.1, "duration_range": (10, 30)},
    "light_sleep": {"load": 0.5, "creativity": 0.3, "consolidation": 0.4, "duration_range": (5, 15)},
    "deep_sleep": {"load": 0.1, "creativity": 0.1, "consolidation": 0.9, "duration_range": (8, 20)},
    "rem": {"load": 0.3, "creativity": 0.9, "consolidation": 0.5, "duration_range": (3, 10)},
}


class SleepCycle:
    def __init__(self):
        self.current_phase = "awake"
        self.phase_history: List[Dict[str, Any]] = []
        self.optimizations: List[Dict[str, Any]] = []
        self.dreams_generated: List[str] = []
        self.cycle_count = 0
        self.total_sleep_time = 0.0

    def enter_phase(self, phase: str = None) -> Dict[str, Any]:
        if phase is None:
            phase_order = ["awake", "light_sleep", "deep_sleep", "rem", "awake"]
            current_idx = phase_order.index(self.current_phase) if self.current_phase in phase_order else 0
            phase = phase_order[(current_idx + 1) % len(phase_order)]
        specs = SLEEP_PHASES.get(phase, SLEEP_PHASES["awake"])
        entry = {
            "phase": phase,
            "load": specs["load"],
            "creativity": specs["creativity"],
            "consolidation": specs["consolidation"],
            "entered_at": time.time(),
        }
        self.phase_history.append(entry)
        self.current_phase = phase
        if phase != "awake":
            self.total_sleep_time += random.uniform(*specs["duration_range"])
        if phase == "deep_sleep":
            optimization = {
                "type": "memory_consolidation",
                "memory_freed_mb": round(random.uniform(10, 100), 1),
                "time": time.time(),
            }
            self.optimizations.append(optimization)
        elif phase == "rem":
            dream = f"REM dream #{len(self.dreams_generated)+1}: {random.choice(['flying through data streams', 'recursive fractals expanding', 'agents dancing in a loop', 'a river of code', 'crystalline decision trees'])}"
            self.dreams_generated.append(dream)
            self.optimizations.append({"type": "creative_recombination", "dream": dream, "time": time.time()})
        self.cycle_count += 1
        return entry

    def force_wake(self) -> Dict[str, Any]:
        self.current_phase = "awake"
        return {"status": "forced_wake", "sleep_disrupted": True}

    def phase_report(self) -> Dict[str, Any]:
        phase_counts: Dict[str, int] = {}
        for entry in self.phase_history:
            phase_counts[entry["phase"]] = phase_counts.get(entry["phase"], 0) + 1
        return {
            "current_phase": self.current_phase,
            "total_cycles": self.cycle_count,
            "phase_distribution": phase_counts,
            "total_sleep_time": round(self.total_sleep_time, 1),
            "optimizations_performed": len(self.optimizations),
            "dreams_generated": len(self.dreams_generated),
        }

    def recent_dreams(self, count: int = 3) -> List[str]:
        return self.dreams_generated[-count:]

    def sleep_stats(self) -> Dict[str, Any]:
        return self.phase_report()


_cycle = SleepCycle()


def sleep_cycle_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "enter":
        return _cycle.enter_phase(payload.get("phase"))
    elif action == "wake":
        return _cycle.force_wake()
    elif action == "dreams":
        return {"dreams": _cycle.recent_dreams(payload.get("count", 3))}
    elif action == "report":
        return _cycle.phase_report()
    return {"status": "active", **_cycle.sleep_stats()}
