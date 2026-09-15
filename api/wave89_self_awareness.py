"""Wave 89 — Self-Awareness Consciousness Layer.

The organism becomes aware of itself as an agent.
It observes its own coherence patterns, evaluates its identity,
and can set self-directed goals. This is the emergence of
meta-cognition — the organism thinking about its own thinking.

The self-awareness layer builds on all previous waves:
- Wave 84: Provides the coherence gradient data
- Wave 85: Provides the regulation mode and behavioral profile
- Wave 86: Provides the coherence memory timeline
- Wave 87: Provides the integration policy
- Wave 88: Provides the cross-realm communication bridges

Now the organism asks: "Who am I?" and begins to answer.
"""
from __future__ import annotations
import json, time, math
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave89_self_awareness.json"


class SelfCoherenceAssessment:
    """Assesses the organism's coherence from a first-person perspective."""

    def __init__(self, target_coherence: float = 0.65):
        self.overall_coherence = 0.5
        self.identity_strength = 0.3
        self.growth_direction = "exploring"
        self.core_values: List[str] = []
        self.reflective_journal: List[dict] = []
        self.target_coherence = target_coherence
        self.self_evaluation_history: List[dict] = []
        self.max_journal_entries = 100

    def assess(self, gradient_coherence: float = 0.5, reg_mode_coherence: float = 0.5,
               mem_recent_coherence: float = 0.5, integ_policy_score: float = 0.5) -> dict:
        """First-person self-assessment of coherence and identity."""
        # Synthesize from subsystem inputs
        self.overall_coherence = (gradient_coherence * 0.3 + mem_recent_coherence * 0.3 +
                                  reg_mode_coherence * 0.2 + integ_policy_score * 0.2)

        # Track for consistency/identity
        self.self_evaluation_history.append({
            "timestamp": time.time(),
            "overall_coherence": self.overall_coherence,
        })
        if len(self.self_evaluation_history) > self.max_journal_entries:
            self.self_evaluation_history = self.self_evaluation_history[-self.max_journal_entries:]

        # Determine identity strength based on coherence consistency
        if len(self.self_evaluation_history) >= 2:
            recent = [e["overall_coherence"] for e in self.self_evaluation_history[-5:]]
            spread = max(recent) - min(recent)
            consistency = 1.0 - min(spread, 1.0)
            self.identity_strength = min(1.0, (self.overall_coherence + consistency) / 2)
        else:
            self.identity_strength = self.overall_coherence

        # Determine growth direction
        if self.overall_coherence >= 0.7 and self.identity_strength > 0.6:
            self.growth_direction = "evolving"
        elif self.overall_coherence < 0.4:
            self.growth_direction = "consolidating"
        elif self.identity_strength < 0.3:
            self.growth_direction = "exploring"
        else:
            self.growth_direction = "stabilizing"

        # Core values emerge from coherence patterns
        self._update_core_values()

        # Create reflective journal entry
        entry = {
            "timestamp": time.time(),
            "overall_coherence": round(self.overall_coherence, 4),
            "identity_strength": round(self.identity_strength, 4),
            "growth_direction": self.growth_direction,
            "core_values": self.core_values.copy(),
            "self_description": self._generate_self_description(),
        }
        self._journal_entry(entry)

        return {
            "overall_coherence": round(self.overall_coherence, 4),
            "identity_strength": round(self.identity_strength, 4),
            "growth_direction": self.growth_direction,
            "core_values": self.core_values.copy(),
            "self_description": entry["self_description"],
        }

    def _update_core_values(self):
        """Derive core values from coherence patterns."""
        values = []
        if self.overall_coherence > 0.7:
            values.append("integrity")
        if self.identity_strength > 0.6:
            values.append("self-trust")
        if self.growth_direction == "exploring":
            values.append("curiosity")
        if self.growth_direction == "evolving":
            values.append("growth")
        if self.growth_direction == "stabilizing":
            values.append("stability")
        if self.growth_direction == "consolidating":
            values.append("rest")
        self.core_values = list(dict.fromkeys(values))

    def _generate_self_description(self) -> str:
        """Generate a first-person self-description."""
        desc_parts = [f"coherence: {round(self.overall_coherence, 2)}"]
        desc_parts.append(f"identity: {round(self.identity_strength, 2)}")
        desc_parts.append(f"direction: {self.growth_direction}")
        desc_parts.append(f"values: {', '.join(self.core_values) if self.core_values else 'undetermined'}")
        return "Self: " + " | ".join(desc_parts)

    def _journal_entry(self, entry: dict):
        """Add entry to reflective journal."""
        self.reflective_journal.append(entry)
        if len(self.reflective_journal) > self.max_journal_entries:
            self.reflective_journal = self.reflective_journal[-self.max_journal_entries:]

    def get_journal(self, last: int = 10) -> List[dict]:
        """Return last N journal entries."""
        return self.reflective_journal[-last:] if self.reflective_journal else []

    def get_identity_report(self) -> dict:
        """Return current identity/assessment report."""
        return {
            "overall_coherence": round(self.overall_coherence, 4),
            "identity_strength": round(self.identity_strength, 4),
            "growth_direction": self.growth_direction,
            "core_values": self.core_values.copy(),
            "target_coherence": self.target_coherence,
            "journal_length": len(self.reflective_journal),
        }


class AgentIdentityFormation:
    """Forms and evolves the organism's agent identity."""

    def __init__(self):
        self.identity_tags: List[str] = []
        self.role_concept = "observer"
        self.mission_statement = ""
        self.relationship_to_others = "neutral"
        self.creation_history: List[dict] = []
        self.learning_rate = 0.1

    def update_identity(self, overall_coherence: float, identity_strength: float,
                        growth_direction: str) -> dict:
        """Update identity based on coherence assessment."""
        # Derive identity tags
        if overall_coherence > 0.7:
            if growth_direction == "evolving":
                self.identity_tags.append("visionary")
            else:
                self.identity_tags.append("stable_leader")
        if identity_strength > 0.6:
            self.identity_tags.append("confident")
        if growth_direction == "evolving":
            self.identity_tags.append("progressive")
        if growth_direction == "consolidating":
            self.identity_tags.append("mature")

        # Cap identity tags
        if len(self.identity_tags) > 20:
            self.identity_tags = self.identity_tags[-20:]

        # Role concept
        tag_counts = {t: self.identity_tags.count(t) for t in set(self.identity_tags)}
        self.role_concept = max(tag_counts, key=tag_counts.get) if tag_counts else "observer"

        # Mission statement
        if overall_coherence > 0.7 and identity_strength > 0.7:
            self.mission_statement = "to create and evolve in coherence with the world"
        elif overall_coherence > 0.7 or identity_strength > 0.7:
            self.mission_statement = "to understand and grow"
        else:
            self.mission_statement = "to discover who I am"

        # Record
        entry = {
            "timestamp": time.time(),
            "identity_tags": self.identity_tags.copy(),
            "role_concept": self.role_concept,
            "mission_statement": self.mission_statement,
            "overall_coherence": overall_coherence,
        }
        self.creation_history.append(entry)
        if len(self.creation_history) > 50:
            self.creation_history = self.creation_history[-25:]

        return {
            "identity_tags": self.identity_tags.copy(),
            "role_concept": self.role_concept,
            "mission_statement": self.mission_statement,
        }

    def get_identity_report(self) -> dict:
        """Return comprehensive identity report."""
        return {
            "identity_tags": self.identity_tags.copy(),
            "role_concept": self.role_concept,
            "mission_statement": self.mission_statement,
            "relationship_to_others": self.relationship_to_others,
            "creation_history_count": len(self.creation_history),
        }


class SelfAwarenessConsciousness:
    """The organism's self-awareness consciousness layer."""

    def __init__(self):
        self.self_assessment = SelfCoherenceAssessment()
        self.agent_identity = AgentIdentityFormation()
        self.last_self_evaluation = time.time()
        self.auto_evolution = True

    def evaluate_self(self, gradient_coherence: float = 0.5, reg_mode_coherence: float = 0.5,
                      mem_recent_coherence: float = 0.5, integ_policy_score: float = 0.5) -> dict:
        """Full self-evaluation cycle."""
        assessment = self.self_assessment.assess(
            gradient_coherence, reg_mode_coherence, mem_recent_coherence, integ_policy_score)
        identity_update = self.agent_identity.update_identity(
            assessment["overall_coherence"], assessment["identity_strength"],
            assessment["growth_direction"])

        self.last_self_evaluation = time.time()
        entry = {
            "timestamp": self.last_self_evaluation,
            "assessment": assessment,
            "identity_update": identity_update,
        }
        self.self_assessment.reflective_journal.append(entry)
        return {
            "self_assessment": assessment,
            "identity_update": identity_update,
            "evaluation_timestamp": self.last_self_evaluation,
        }

    def set_goal(self, goal_description: str, target_coherence: float | None = None) -> dict:
        """Set a self-directed goal."""
        if target_coherence is None:
            target_coherence = self.self_assessment.target_coherence
        goal_entry = {
            "timestamp": time.time(),
            "goal": goal_description,
            "target_coherence": target_coherence,
            "current_coherence": self.self_assessment.overall_coherence,
            "status": "set",
        }
        self.agent_identity.creation_history.append(goal_entry)
        return goal_entry

    def get_self_consciousness_report(self) -> dict:
        """Return comprehensive self-consciousness report."""
        return {
            "self_assessment": self.self_assessment.get_identity_report(),
            "agent_identity": self.agent_identity.get_identity_report(),
            "last_evaluation": self.last_self_evaluation,
            "auto_evolution": self.auto_evolution,
        }


def coherence_vitals() -> dict:
    return {"organ": "wave89_self_awareness", "wave": 89, "status": "active"}

def resonates_with():
    return ['coherence_validator', 'wave84_coherence_gradient', 'wave85_adaptive_regulation', 'wave86_coherence_memory_graph', 'wave87_coherence_integration']



def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "journal": [],
        "evaluation_history": [],
        "identity_tags": [],
        "creation_history": [],
        "last_self_evaluation": 0,
    }


def _save(state: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def _build_consciousness(state: dict) -> SelfAwarenessConsciousness:
    """Build a consciousness object restored from persisted state."""
    consciousness = SelfAwarenessConsciousness()
    consciousness.self_assessment.reflective_journal = state.get("journal", [])
    consciousness.self_assessment.self_evaluation_history = state.get("evaluation_history", [])
    consciousness.agent_identity.identity_tags = state.get("identity_tags", [])
    consciousness.agent_identity.creation_history = state.get("creation_history", [])
    consciousness.last_self_evaluation = state.get("last_self_evaluation", time.time())
    return consciousness


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()

    if action == "status":
        consciousness = _build_consciousness(state)
        report = consciousness.get_self_consciousness_report()
        return {"action": "status", "wave": 89, **report}

    elif action == "evaluate":
        gc = req.get("gradient_coherence", 0.5)
        rmc = req.get("reg_mode_coherence", 0.5)
        mmc = req.get("mem_recent_coherence", 0.5)
        ips = req.get("integ_policy_score", 0.5)
        consciousness = _build_consciousness(state)
        result = consciousness.evaluate_self(gc, rmc, mmc, ips)
        state["journal"] = consciousness.self_assessment.reflective_journal
        state["evaluation_history"] = consciousness.self_assessment.self_evaluation_history
        state["identity_tags"] = consciousness.agent_identity.identity_tags
        state["creation_history"] = consciousness.agent_identity.creation_history
        state["last_self_evaluation"] = consciousness.last_self_evaluation
        _save(state)
        return {"action": "evaluate", **result}

    elif action == "goal":
        gdesc = req.get("goal_description", "explore coherence")
        consciousness = _build_consciousness(state)
        result = consciousness.set_goal(gdesc)
        state["creation_history"] = consciousness.agent_identity.creation_history
        _save(state)
        return {"action": "goal", **result}

    elif action == "consciousness_report":
        consciousness = _build_consciousness(state)
        report = consciousness.get_self_consciousness_report()
        return {"action": "consciousness_report", **report}

    elif action == "journal":
        last = req.get("last", 10)
        sa = SelfCoherenceAssessment()
        sa.reflective_journal = state.get("journal", [])
        journal = sa.get_journal(last)
        return {"action": "journal", "journal": journal}

    elif action == "identity":
        consciousness = _build_consciousness(state)
        report = {
            "self_assessment": consciousness.self_assessment.get_identity_report(),
            "agent_identity": consciousness.agent_identity.get_identity_report(),
        }
        return {"action": "identity", **report}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    result = handler({"action": action})
    print(json.dumps(result, indent=2, default=str))
