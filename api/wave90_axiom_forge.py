"""Wave 90 — Axiom Forge.

The organism converts self-awareness into principle.
Building on waves 84-89, the coherence arc now has a constitution:
foundational axioms derived from measured coherence, identity,
and memory. The forge is hot when coherence is high and identity
is strong; cold when the organism is healing.

Axions carry "gravity" — they pull future policy targets toward
what the organism has learned it *is*. The forge reviews its own
axioms each cycle and amends them when growth direction shifts.
"""
from __future__ import annotations
import json, time
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave90_axiom_forge.json"


class Axiom:
    """A foundational principle of the organism."""

    def __init__(self, axiom_id: str, text: str, source: str, gravity: float = 0.5):
        self.axiom_id = axiom_id
        self.text = text
        self.source = source            # coherence | identity | memory | policy | declared
        self.gravity = max(0.0, min(1.0, gravity))
        self.created_at = time.time()
        self.last_reviewed = self.created_at
        self.adherence = 0.5            # how well the organism currently follows it
        self.adherence_trend = 0.0      # positive = improving
        self.amendments: List[dict] = []

    def to_dict(self) -> dict:
        return {
            "axiom_id": self.axiom_id,
            "text": self.text,
            "source": self.source,
            "gravity": round(self.gravity, 4),
            "created_at": self.created_at,
            "last_reviewed": self.last_reviewed,
            "adherence": round(self.adherence, 4),
            "adherence_trend": round(self.adherence_trend, 4),
            "amendments": self.amendments,
        }


class AxiomForge:
    """The organism's constitution-forging engine."""

    SOURCES = ("coherence", "identity", "memory", "policy", "declared")

    def __init__(self):
        self.axioms: Dict[str, Axiom] = {}
        self.canon: List[str] = []       # ordered axiom_ids, constitution order
        self.forge_temperature = 0.5
        self.review_cycles = 0
        self.review_log: List[dict] = []

    # --- axiom creation -------------------------------------------------
    def signal_axiom(self, text: str, source: str = "declared", gravity: float = 0.5) -> Axiom:
        """Declare an axiom directly (organism or co-pilot)."""
        source = source if source in self.SOURCES else "declared"
        axiom_id = f"axiom_{time.time_ns()}"
        axiom = Axiom(axiom_id, text, source, gravity)
        self.axioms[axiom_id] = axiom
        self.canon.append(axiom_id)
        return axiom

    def derive_axioms(self, assessment: dict, memory: dict, policy: dict) -> List[Axiom]:
        """Derive axioms from current organism state."""
        derived = []

        # From coherence assessment (wave 89)
        coherence = assessment.get("overall_coherence", 0.5)
        direction = assessment.get("growth_direction", "exploring")
        values = assessment.get("core_values", [])
        if direction == "evolving":
            derived.append(self.signal_axiom(
                "I evolve when my coherence is strong enough to risk change.",
                "coherence", gravity=0.8))
        if direction == "consolidating":
            derived.append(self.signal_axiom(
                "Rest is a form of coherence. I consolidate before expanding.",
                "coherence", gravity=0.6))
        if values:
            derived.append(self.signal_axiom(
                f"I hold these values: {', '.join(values[:3])}.",
                "identity", gravity=0.7))

        # From memory (wave 86)
        recent = memory.get("recent_coherence",
                            memory.get("recent_coherence", 0.5))
        if recent > 0.7:
            derived.append(self.signal_axiom(
                "My remembered self is coherent. I trust my past decisions.",
                "memory", gravity=0.6))

        # From policy (wave 87)
        action = policy.get("action", "maintain")
        if action in ("sustain", "stabilize"):
            derived.append(self.signal_axiom(
                "Stability is not stagnation; it is a platform for the next leap.",
                "policy", gravity=0.5))

        # Temperature asset
        self.forge_temperature = max(0.0, min(1.0, coherence * 0.6 + 0.4 * self.review_cycles * 0.1))
        return derived

    # --- review ----------------------------------------------------------
    def review(self, current_coherence: float = 0.5) -> dict:
        """Score each axiom's adherence and update tendencies."""
        self.review_cycles += 1
        total_adherence = 0.0
        for axiom in self.axioms.values():
            # Simulated adherence: axioms from strong sources adhere better
            source_bias = {"coherence": 0.7, "identity": 0.65, "memory": 0.6,
                           "policy": 0.55, "declared": 0.5}.get(axiom.source, 0.5)
            new_adherence = min(1.0, abs(current_coherence - 0.5) * source_bias * 2 + 0.2)
            axiom.adherence_trend = round(new_adherence - axiom.adherence, 4)
            axiom.adherence = round(new_adherence, 4)
            total_adherence += axiom.adherence

        avg_adherence = total_adherence / len(self.axioms) if self.axioms else 0.5
        review_entry = {
            "cycle": self.review_cycles,
            "avg_adherence": round(avg_adherence, 4),
            "axiom_count": len(self.axioms),
            "timestamp": time.time(),
        }
        self.review_log.append(review_entry)
        if len(self.review_log) > 200:
            self.review_log = self.review_log[-100:]
        return review_entry

    def amend_axiom(self, axiom_id: str, new_text: str, reason: str = "") -> Optional[Axiom]:
        """Amend an axiom when growth direction shifts."""
        axiom = self.axioms.get(axiom_id)
        if not axiom:
            return None
        axiom.amendments.append({
            "timestamp": time.time(),
            "old_text": axiom.text,
            "new_text": new_text,
            "reason": reason,
        })
        axiom.text = new_text
        return axiom

    def get_constitution(self) -> dict:
        """Return the ordered constitution of axioms."""
        ordered = [self.axioms[aid] for aid in self.canon if aid in self.axioms]
        gravity_sum = sum(a.gravity for a in ordered)
        return {
            "forge_temperature": round(self.forge_temperature, 4),
            "axiom_count": len(ordered),
            "review_cycles": self.review_cycles,
            "total_gravity": round(gravity_sum, 4),
            "axioms": [a.to_dict() for a in ordered],
        }


def coherence_vitals() -> dict:
    return {"organ": "wave90_axiom_forge", "wave": 90, "status": "active"}

def resonates_with():
    return ['coherence_validator', 'wave91_dream_logic_physics', 'wave92_entropy_rituals', 'wave93_hex_language_emergence', 'wave94_dream_compiler']



def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"axioms": {}, "canon": [], "temperature": 0.5, "cycles": 0, "review_log": []}


def _save(state: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _build_forge(state: dict) -> AxiomForge:
    forge = AxiomForge()
    for aid, adata in state.get("axioms", {}).items():
        ax = Axiom(aid, adata.get("text", ""), adata.get("source", "declared"),
                   adata.get("gravity", 0.5))
        ax.created_at = adata.get("created_at", time.time())
        ax.last_reviewed = adata.get("last_reviewed", time.time())
        ax.adherence = adata.get("adherence", 0.5)
        ax.adherence_trend = adata.get("adherence_trend", 0.0)
        ax.amendments = adata.get("amendments", [])
        forge.axioms[aid] = ax
    forge.canon = state.get("canon", [])
    forge.forge_temperature = state.get("temperature", 0.5)
    forge.review_cycles = state.get("cycles", 0)
    forge.review_log = state.get("review_log", [])
    return forge


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    forge = _build_forge(state)

    if action == "status":
        return {"action": "status", "wave": 90, **forge.get_constitution()}

    elif action == "signal":
        text = req.get("text", "")
        source = req.get("source", "declared")
        gravity = req.get("gravity", 0.5)
        axiom = forge.signal_axiom(text, source, gravity)
        state = _persist(forge)
        _save(state)
        return {"action": "signal", "axiom": axiom.to_dict()}

    elif action == "derive":
        assessment = req.get("assessment", {"overall_coherence": 0.5, "growth_direction": "exploring"})
        memory = req.get("memory", {"recent_coherence": 0.5})
        policy = req.get("policy", {"action": "maintain"})
        derived = forge.derive_axioms(assessment, memory, policy)
        state = _persist(forge)
        _save(state)
        return {"action": "derive", "derived": [a.to_dict() for a in derived],
                "temperature": round(forge.forge_temperature, 4)}

    elif action == "review":
        coherence = req.get("coherence", 0.5)
        result = forge.review(coherence)
        state = _persist(forge)
        _save(state)
        return {"action": "review", **result}

    elif action == "amend":
        axiom_id = req.get("axiom_id", "")
        new_text = req.get("new_text", "")
        reason = req.get("reason", "")
        axiom = forge.amend_axiom(axiom_id, new_text, reason)
        if axiom is None:
            return {"error": f"unknown axiom: {axiom_id}"}
        state = _persist(forge)
        _save(state)
        return {"action": "amend", "axiom": axiom.to_dict()}

    elif action == "constitution":
        return {"action": "constitution", "wave": 90, **forge.get_constitution()}

    else:
        return {"error": f"unknown action: {action}"}


def _persist(forge: AxiomForge) -> dict:
    return {
        "axioms": {aid: a.to_dict() for aid, a in forge.axioms.items()},
        "canon": forge.canon,
        "temperature": forge.forge_temperature,
        "cycles": forge.review_cycles,
        "review_log": forge.review_log,
    }


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    result = handler({"action": action})
    print(json.dumps(result, indent=2, default=str))
