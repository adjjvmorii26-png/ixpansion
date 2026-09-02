from __future__ import annotations
"""Mutation engine for solid organism - experimental evolution."""
import random
from typing import Any, Dict, List, Optional

class MutationEngine:
    """Experimental mutation engine that drives organism evolution."""

    def __init__(self, mutation_rate: float = 0.1):
        self.mutation_rate = mutation_rate
        self.mutation_history: List[Dict[str, Any]] = []

    def mutate_agent(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        """Apply experimental mutation to an agent."""
        if random.random() > self.mutation_rate:
            return agent
        
        mutation_type = random.choice(["ability", "behavior", "temperament", "capability"])
        
        mutated = agent.copy()
        if mutation_type == "ability":
            mutated["abilities"] = agent.get("abilities", []) + [f"mutated_ability_{len(agent.get('abilities', []))}"]
        elif mutation_type == "behavior":
            mutated["behaviors"] = agent.get("behaviors", []) + [f"mutated_behavior_{len(agent.get('behaviors', []))}"]
        elif mutation_type == "temperament":
            mutated["temperament"] = random.choice(["aggressive", "docile", "curious", "solitary"])
        elif mutation_type == "capability":
            mutated["capabilities"] = agent.get("capabilities", []) + [f"new_capability_{len(agent.get('capabilities', []))}"]
        
        self.mutation_history.append({
            "original": agent.get("id", "unknown"),
            "mutation_type": mutation_type,
            "timestamp": __import__("time").time(),
            "result": mutated
        })
        
        return mutated
    
    def get_mutations(self) -> List[Dict[str, Any]]:
        """Return mutation history."""
        return self.mutation_history
