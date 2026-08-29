"""Trait Inheritance — parent agents pass traits to children with variation.

When agents spawn descendants, traits are inherited with probability-based
variation. Some traits dominate, some are recessive, and some are lethal
when combined. Over generations, complex trait lineages emerge.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class Trait:
    def __init__(self, name: str, value: float, dominance: float = 0.5):
        self.name = name
        self.value = min(max(value, 0.0), 1.0)
        self.dominance = min(max(dominance, 0.0), 1.0)

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "value": round(self.value, 3), "dominance": round(self.dominance, 3)}


class InheritanceAgent:
    def __init__(self, agent_id: str, traits: Dict[str, float] = None):
        self.agent_id = agent_id
        self.traits: Dict[str, Trait] = {}
        self.generation = 0
        self.parent_id: Optional[str] = None
        self.children: List[str] = []
        self.born_at = time.time()
        self.id = hashlib.sha256(f"{agent_id}:{self.born_at}".encode()).hexdigest()[:8]
        default_traits = traits or {
            "strength": 0.5, "speed": 0.5, "wisdom": 0.5,
            "creativity": 0.5, "resilience": 0.5,
        }
        for name, value in default_traits.items():
            self.traits[name] = Trait(name, value, random.uniform(0.3, 0.8))

    def reproduce(self, partner: "InheritanceAgent") -> "InheritanceAgent":
        """Create a child with inherited traits."""
        child_id = f"gen{self.generation + 1}_{self.agent_id[:4]}x{partner.agent_id[:4]}"
        child_traits = {}
        for gene_name in self.traits:
            parent_trait = self.traits[gene_name]
            partner_trait = partner.traits.get(gene_name, parent_trait)
            if random.random() < 0.5:
                base = parent_trait if parent_trait.dominance > partner_trait.dominance else partner_trait
            else:
                base = partner_trait if partner_trait.dominance >= parent_trait.dominance else parent_trait
            value = base.value + random.uniform(-0.1, 0.1)
            value = max(0.0, min(1.0, value))
            dominance = (parent_trait.dominance + partner_trait.dominance) / 2 + random.uniform(-0.05, 0.05)
            child_traits[gene_name] = value
        child = InheritanceAgent(child_id, child_traits)
        child.generation = max(self.generation, partner.generation) + 1
        child.parent_id = self.agent_id
        self.children.append(child_id)
        partner.children.append(child_id)
        return child

    def trait_expression(self) -> Dict[str, Any]:
        """Determine expressed phenotype."""
        expression = {}
        for name, trait in self.traits.items():
            if trait.dominance > 0.6:
                expression[name] = "dominant"
            elif trait.dominance < 0.3:
                expression[name] = "recessive"
            else:
                expression[name] = "co-dominant"
        return expression

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "generation": self.generation,
            "traits": {k: v.to_dict() for k, v in self.traits.items()},
            "children": len(self.children),
            "born_at": self.born_at,
        }


class TraitInheritanceSystem:
    def __init__(self):
        self.agents: Dict[str, InheritanceAgent] = {}
        self.lineages: Dict[str, List[str]] = {}
        self.generation_count = 0

    def create_agent(self, agent_id: str, traits: Dict[str, float] = None) -> Dict[str, Any]:
        agent = InheritanceAgent(agent_id, traits)
        self.agents[agent.id] = agent
        self.lineages[agent_id] = [agent.id]
        return {"created": agent.to_dict()}

    def breed(self, parent_a_id: str, parent_b_id: str) -> Dict[str, Any]:
        parent_a = None
        parent_b = None
        for agent in self.agents.values():
            if agent.agent_id == parent_a_id:
                parent_a = agent
            if agent.agent_id == parent_b_id:
                parent_b = agent
        if not parent_a or not parent_b:
            return {"error": "parent not found"}
        child = parent_a.reproduce(parent_b)
        self.agents[child.id] = child
        self.generation_count = max(self.generation_count, child.generation)
        return {"child": child.to_dict()}

    def lineage(self, agent_id: str) -> List[Dict[str, Any]]:
        ids = self.lineages.get(agent_id, [])
        return [self.agents[i].to_dict() for i in ids if i in self.agents]

    def generation_report(self, gen: int) -> List[Dict[str, Any]]:
        return [a.to_dict() for a in self.agents.values() if a.generation == gen]

    def inheritance_stats(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self.agents),
            "generations": self.generation_count,
            "total_lineages": len(self.lineages),
            "avg_traits_per_agent": round(
                sum(len(a.traits) for a in self.agents.values()) / max(len(self.agents), 1), 2
            ),
        }


_system = TraitInheritanceSystem()


def trait_inheritance_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "create":
        return _system.create_agent(
            payload.get("agent_id", f"organism_{random.randint(1000,9999)}"),
            payload.get("traits"),
        )
    elif action == "breed":
        return _system.breed(
            payload.get("parent_a", ""), payload.get("parent_b", ""),
        )
    elif action == "lineage":
        return {"lineage": _system.lineage(payload.get("agent_id", ""))}
    elif action == "generation":
        return {"agents": _system.generation_report(payload.get("generation", 0))}
    return {"status": "active", **_system.inheritance_stats()}


handler = trait_inheritance_handler
