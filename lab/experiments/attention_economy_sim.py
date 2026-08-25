#!/usr/bin/env python3
"""Attention Economy Simulator — model cognitive resource allocation.

Bridges attention_economy + dissonance + emotional_contagion to create
a full simulation of agent cognitive dynamics. Agents must balance:
- Spending attention on observation (intelligence gathering)
- Earning attention through visible actions (influence)
- Managing dissonance from contradictory beliefs
- Resisting emotional contagion from neighbors

The simulator tracks wealth inequality, influence distribution,
dissonance crises, and emotional cascades over time.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CognitiveAgent:
    agent_id: str
    species: str
    position: tuple[float, float]
    attention_balance: float = 10.0
    valence: float = 0.0
    arousal: float = 0.3
    dissonance_pressure: float = 0.0
    beliefs: dict[str, float] = field(default_factory=dict)
    observation_count: int = 0
    actions_performed: int = 0

    @property
    def influence(self) -> float:
        return min(3.0, max(0.1, self.attention_balance / 10.0))

    @property
    def is_bankrupt(self) -> bool:
        return self.attention_balance <= 0.0

    @property
    def emotion_label(self) -> str:
        if self.valence > 0.5 and self.arousal > 0.7:
            return "ecstatic"
        elif self.valence > 0.3:
            return "content"
        elif self.valence < -0.5 and self.arousal > 0.7:
            return "panicked"
        elif self.valence < -0.3:
            return "distressed"
        elif self.arousal > 0.8:
            return "agitated"
        return "neutral"

    @property
    def dissonance_level(self) -> str:
        if self.dissonance_pressure >= 0.8:
            return "crisis"
        elif self.dissonance_pressure >= 0.6:
            return "fracture"
        elif self.dissonance_pressure >= 0.4:
            return "strain"
        elif self.dissonance_pressure >= 0.2:
            return "tension"
        return "harmonious"


@dataclass
class AttentionEconomySimulator:
    """Full cognitive economy simulation."""
    width: float = 100.0
    height: float = 100.0
    observation_cost: float = 1.0
    action_reward: float = 0.5
    emotion_transfer_rate: float = 0.15
    emotion_decay_rate: float = 0.02
    dissonance_per_contradiction: float = 0.15
    dissonance_recovery_rate: float = 0.05
    contagion_radius: float = 15.0
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._agents: dict[str, CognitiveAgent] = {}
        self._tick = 0
        self._timeline: list[dict[str, Any]] = []
        self._crisis_log: list[dict[str, Any]] = []

    def add_agent(self, agent_id: str, species: str,
                  position: tuple[float, float] | None = None) -> CognitiveAgent:
        if position is None:
            position = (
                self._rng.uniform(0, self.width),
                self._rng.uniform(0, self.height),
            )
        agent = CognitiveAgent(agent_id=agent_id, species=species, position=position)
        self._agents[agent_id] = agent
        return agent

    def observe(self, observer_id: str, target_id: str) -> dict[str, Any]:
        observer = self._agents.get(observer_id)
        target = self._agents.get(target_id)
        if not observer or not target:
            return {"status": "unknown"}
        if observer.is_bankrupt:
            return {"status": "bankrupt"}

        observer.attention_balance -= self.observation_cost
        observer.observation_count += 1
        target.attention_balance += self.action_reward

        # Emotion transfer
        emotion_delta = self._transfer_emotion(observer, target)

        return {
            "status": "ok",
            "observer_balance": round(observer.attention_balance, 3),
            "emotion_delta": round(emotion_delta, 4),
        }

    def act(self, agent_id: str, action_type: str = "default") -> dict[str, Any]:
        agent = self._agents.get(agent_id)
        if not agent:
            return {"status": "unknown"}

        agent.attention_balance += self.action_reward
        agent.actions_performed += 1

        # Actions can introduce dissonance
        if self._rng.random() < 0.3:
            agent.dissonance_pressure = min(1.0, agent.dissonance_pressure + self.dissonance_per_contradiction)
            if agent.dissonance_pressure >= 0.8:
                crisis = {
                    "tick": self._tick,
                    "agent": agent_id,
                    "level": "crisis",
                    "balance": round(agent.attention_balance, 3),
                }
                self._crisis_log.append(crisis)

        return {
            "status": "ok",
            "balance": round(agent.attention_balance, 3),
            "influence": round(agent.influence, 3),
        }

    def tick(self) -> dict[str, Any]:
        self._tick += 1
        cascade_events: list[dict[str, Any]] = []

        # Emotion propagation
        agent_list = list(self._agents.values())
        for i, a in enumerate(agent_list):
            if abs(a.valence) > 0.4 or a.arousal > 0.6:
                for j, b in enumerate(agent_list):
                    if i == j:
                        continue
                    dist = math.dist(a.position, b.position)
                    if dist <= self.contagion_radius:
                        transfer = self._transfer_emotion(a, b)
                        if abs(transfer) > 0.05:
                            cascade_events.append({
                                "from": a.agent_id,
                                "to": b.agent_id,
                                "delta": round(transfer, 4),
                            })

        # Dissonance recovery
        for agent in self._agents.values():
            agent.dissonance_pressure = max(0.0, agent.dissonance_pressure - self.dissonance_recovery_rate)
            # Emotional decay
            agent.valence *= (1 - self.emotion_decay_rate)
            agent.arousal *= (1 - self.emotion_decay_rate)

        # Record snapshot
        snapshot = {
            "tick": self._tick,
            "agents": len(self._agents),
            "mean_balance": round(
                sum(a.attention_balance for a in self._agents.values()) / max(1, len(self._agents)), 3
            ),
            "mean_valence": round(
                sum(a.valence for a in self._agents.values()) / max(1, len(self._agents)), 4
            ),
            "bankrupt_count": sum(1 for a in self._agents.values() if a.is_bankrupt),
            "crisis_count": sum(1 for a in self._agents.values() if a.dissonance_pressure >= 0.8),
            "emotion_cascades": len(cascade_events),
        }
        self._timeline.append(snapshot)
        return snapshot

    def _transfer_emotion(self, source: CognitiveAgent, target: CognitiveAgent) -> float:
        dist = math.dist(source.position, target.position)
        if dist == 0:
            strength = self.emotion_transfer_rate
        else:
            strength = self.emotion_transfer_rate / (1 + dist / self.contagion_radius)

        delta = source.valence * strength
        target.valence = max(-1.0, min(1.0, target.valence + delta))
        target.arousal = min(1.0, target.arousal + abs(delta) * 0.5)
        return delta

    def gini_coefficient(self) -> float:
        balances = sorted(a.attention_balance for a in self._agents.values())
        n = len(balances)
        if n == 0:
            return 0.0
        total = sum(balances)
        if total == 0:
            return 0.0
        cumulative = 0.0
        gini_sum = 0.0
        for i, b in enumerate(balances):
            cumulative += b
            gini_sum += (2 * (i + 1) - n - 1) * b
        return round(gini_sum / (n * total), 4)

    def timeline_summary(self) -> dict[str, Any]:
        if not self._timeline:
            return {}
        first = self._timeline[0]
        last = self._timeline[-1]
        return {
            "ticks": len(self._timeline),
            "initial_balance": first["mean_balance"],
            "final_balance": last["mean_balance"],
            "balance_trend": "growing" if last["mean_balance"] > first["mean_balance"] else "shrinking",
            "peak_crises": max(t["crisis_count"] for t in self._timeline),
            "total_cascades": sum(t["emotion_cascades"] for t in self._timeline),
            "final_gini": self.gini_coefficient(),
        }


def demo() -> dict[str, Any]:
    sim = AttentionEconomySimulator(seed=42)
    species = ["sentinel", "architect", "wanderer"]
    for i in range(15):
        sim.add_agent(f"agent-{i}", species[i % 3])

    for tick in range(30):
        sim.tick()
        agents = list(sim._agents.keys())
        # Random observations
        for _ in range(5):
            a = sim._rng.choice(agents)
            b = sim._rng.choice(agents)
            if a != b:
                sim.observe(a, b)
        # Random actions
        for _ in range(3):
            a = sim._rng.choice(agents)
            sim.act(a)

    return {
        "summary": sim.timeline_summary(),
        "crises": sim._crisis_log[:5],
        "gini": sim.gini_coefficient(),
    }


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
