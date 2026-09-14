"""Wave 92 — Entropy Rituals Scheduler.

Scheduled events where the organism intentionally mutates itself,
creating controlled entropy waves that drive innovation and adaptation.
"""

from __future__ import annotations
import json, time, math, hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave92_entropy_rituals.json"


class EntropyRitual:
    """A single entropy ritual with scheduled activation."""

    def __init__(self, ritual_id: str, trigger_time: float, mutation_strength: float,
                 mutation_type: str, description: str):
        self.ritual_id = ritual_id
        self.trigger_time = trigger_time
        self.mutation_strength = mutation_strength
        self.mutation_type = mutation_type
        self.description = description
        self.executed = False
        self.executed_at = None
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute deterministic hash for ritual tracking."""
        data = f"{self.ritual_id}:{self.trigger_time}:{self.mutation_strength}:{self.mutation_type}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    def should_activate(self, current_time: float) -> bool:
        """Check if ritual should activate now."""
        return not self.executed and current_time >= self.trigger_time

    def execute(self, current_time: float) -> Dict[str, Any]:
        """Execute the ritual and record results."""
        self.executed = True
        self.executed_at = current_time
        return {
            "ritual_id": self.ritual_id,
            "executed_at": self.executed_at,
            "mutation_strength": self.mutation_strength,
            "mutation_type": self.mutation_type,
            "description": self.description,
            "entropy_injected": self.mutation_strength,
        }


class EntropyRitualScheduler:
    """Scheduler that manages timed entropy rituals for the organism."""

    def __init__(self):
        self.rituals: Dict[str, EntropyRitual] = {}
        self.next_ritual_id = 1
        self.last_check = time.time()

    def schedule_ritual(self, trigger_days: int, mutation_strength: float,
                        mutation_type: str, description: str) -> EntropyRitual:
        """Schedule a ritual to trigger after specified days."""
        trigger_time = time.time() + (trigger_days * 86400)
        ritual = EntropyRitual(
            ritual_id=f"ritual_{self.next_ritual_id:03d}",
            trigger_time=trigger_time,
            mutation_strength=mutation_strength,
            mutation_type=mutation_type,
            description=description,
        )
        self.rituals[ritual.ritual_id] = ritual
        self.next_ritual_id += 1
        return ritual

    def check_and_execute(self, current_time: float = None) -> List[Dict[str, Any]]:
        """Check all rituals and execute those due."""
        if current_time is None:
            current_time = time.time()
        executed = []
        for ritual_id, ritual in self.rituals.items():
            if ritual.should_activate(current_time):
                result = ritual.execute(current_time)
                executed.append(result)
        return executed

    def get_ritual_status(self) -> Dict[str, Any]:
        """Get status of all scheduled rituals."""
        total = len(self.rituals)
        due = sum(1 for r in self.rituals.values() if r.should_activate(time.time()))
        executed = sum(1 for r in self.rituals.values() if r.executed)
        return {
            "total_rituals": total,
            "due_rituals": due,
            "executed_rituals": executed,
            "pending_rituals": total - executed,
        }

    def coherence_vitals(self) -> Dict[str, Any]:
        """Return vitality metrics for entropy rituals."""
        status = self.get_ritual_status()
        return {
            "wave": 92,
            "ritual_scheduler_active": True,
            **status,
            "average_entropy": round(
                sum(r.mutation_strength for r in self.rituals.values()) / max(len(self.rituals), 1), 4
            ) if self.rituals else 0.0,
        }


def handler(req: dict) -> dict:
    """Wave 92 handler: entropy ritual scheduling."""
    action = req.get("action", "status")
    scheduler = EntropyRitualScheduler()

    if action == "status":
        return {
            "action": "status",
            "wave": 92,
            "rituals": scheduler.coherence_vitals(),
            "message": "Entropy ritual scheduler status",
        }

    if action == "schedule":
        ritual = scheduler.schedule_ritual(
            trigger_days=int(req.get("trigger_days", 7)),
            mutation_strength=float(req.get("strength", 0.3)),
            mutation_type=req.get("type", "structural"),
            description=req.get("description", "Scheduled entropy ritual"),
        )
        return {
            "action": "schedule",
            "wave": 92,
            "ritual_id": ritual.ritual_id,
            "scheduled_for": ritual.trigger_time,
            "message": "Ritual scheduled",
        }

    if action == "execute-due":
        executed = scheduler.check_and_execute()
        return {
            "action": "execute-due",
            "wave": 92,
            "executed": executed,
            "message": f"Executed {len(executed)} due rituals",
        }

    return {"ok": False, "error": f"Unknown action: {action}"}


def coherence_vitals() -> dict:
    """Wave 92 vitals."""
    return EntropyRitualScheduler().coherence_vitals()
