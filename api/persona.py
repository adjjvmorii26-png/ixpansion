"""
persona — Agent personality layer for the IXpansion organism.

Each agent has a persistent personality that influences:
- Decision-making preferences
- Communication style
- Risk tolerance
- Creative tendencies
- Collaboration patterns

Personalities evolve through interactions and experiences.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import time
import json


@dataclass
class AgentPersona:
    """ Personality profile for an agent."""
    agent_id: str
    # Core traits (0.0 - 1.0 scale)
    curiosity: float = 0.5
    risk_aversion: float = 0.5
    creativity: float = 0.5
    cooperation: float = 0.5
    exploration: float = 0.5
    conservativeness: float = 0.5
    
    # Derived attributes
    mood_vector: Dict[str, float] = field(default_factory=lambda: {
        "interest": 0.5,
        "engagement": 0.5,
        "satisfaction": 0.5
    })
    
    # History
    creation_time: float = field(default_factory=time.time)
    interaction_count: int = 0
    preference_history: list = field(default_factory=list)
    
    def update_from_interaction(self, outcome: str, reward: float):
        """Update personality based on interaction outcome."""
        self.interaction_count += 1
        self.preference_history.append({
            "outcome": outcome,
            "reward": reward,
            "timestamp": time.time()
        })
        # Simple learning - bias traits toward successful outcomes
        if reward > 0.5:
            self.curiosity = min(1.0, self.curiosity + 0.01)
            self.creativity = min(1.0, self.creativity + 0.01)
        else:
            self.risk_aversion = min(1.0, self.risk_aversion + 0.01)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "curiosity": self.curiosity,
            "risk_aversion": self.risk_aversion,
            "creativity": self.creativity,
            "cooperation": self.cooperation,
            "exploration": self.exploration,
            "conservativeness": self.conservativeness,
            "mood_vector": self.mood_vector,
            "interaction_count": self.interaction_count,
        }


def create_persona(agent_id: str, **traits) -> AgentPersona:
    """Factory function to create an agent persona."""
    traits.update({
        "curiosity": traits.get("curiosity", 0.5),
        "risk_aversion": traits.get("risk_aversion", 0.5),
        "creativity": traits.get("creativity", 0.5),
        "cooperation": traits.get("cooperation", 0.5),
        "exploration": traits.get("exploration", 0.5),
        "conservativeness": traits.get("conservativeness", 0.5),
    })
    # Normalize: traits should sum to ~5.0 (not strict, but for balance)
    total = sum(traits.values())
    # Ensure no trait exceeds 1.0
    for key in traits:
        traits[key] = min(1.0, traits[key])
    return AgentPersona(agent_id=agent_id, **traits)


def merge_personas(p1: AgentPersona, p2: AgentPersona) -> AgentPersona:
    """Merge two personas (e.g., for co-pilot or hybrid agents)."""
    return AgentPersona(
        agent_id=f"{p1.agent_id}+{p2.agent_id}",
        curiosity=(p1.curiosity + p2.curiosity) / 2,
        risk_aversion=(p1.risk_aversion + p2.risk_aversion) / 2,
        creativity=(p1.creativity + p2.creativity) / 2,
        cooperation=(p1.cooperation + p2.cooperation) / 2,
        exploration=(p1.exploration + p2.exploration) / 2,
        conservativeness=(p1.conservativeness + p2.conservativeness) / 2,
    )
