from __future__ import annotations
"""Quantum Tunneling — state passes through impossible barriers.

Simulates quantum tunneling where system states can pass through error
states, deadlocks, and failure barriers that would classically block
progress. The probability of tunneling depends on barrier width and
energy differential.
"""
import math
import random
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

@dataclass
class Barrier:
    name: str
    width: float = 1.0
    height: float = 5.0
    position: float = 0.0
    penetrated: bool = False
    penetration_attempts: int = 0

@dataclass
class QuantumState:
    name: str
    energy: float = 1.0
    position: float = 0.0
    wave_function: List[complex] = field(default_factory=list)
    tunnel_events: int = 0
    collapsed: bool = False

    def compute_tunnel_probability(self, barrier: Barrier) -> float:
        if self.energy >= barrier.height:
            return 1.0
        kappa = math.sqrt(2 * (barrier.height - self.energy)) / 1.0
        probability = math.exp(-2 * kappa * barrier.width)
        return min(1.0, max(0.0, probability))

    def advance(self, dt: float = 0.1):
        self.position += self.energy * dt * 0.01
        phase = self.position * math.pi
        self.wave_function = [
            complex(math.cos(phase + i * 0.1), math.sin(phase + i * 0.1))
            for i in range(16)
        ]


class QuantumTunnelingEngine:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.states: Dict[str, QuantumState] = {}
        self.barriers: List[Barrier] = []
        self.tunnel_log: List[Dict] = []
        self.tick = 0

    def add_state(self, name: str, energy: float = 1.0, position: float = 0.0) -> QuantumState:
        state = QuantumState(name=name, energy=energy, position=position)
        state.advance()
        self.states[name] = state
        return state

    def add_barrier(self, name: str, width: float = 1.0, height: float = 5.0,
                    position: float = 5.0) -> Barrier:
        barrier = Barrier(name=name, width=width, height=height, position=position)
        self.barriers.append(barrier)
        return barrier

    def attempt_tunnel(self, state_name: str, barrier_idx: int) -> Dict:
        if state_name not in self.states or barrier_idx >= len(self.barriers):
            return {"success": False, "reason": "not_found"}
        state = self.states[state_name]
        barrier = self.barriers[barrier_idx]
        barrier.penetration_attempts += 1
        probability = state.compute_tunnel_probability(barrier)
        roll = self.rng.random()
        success = roll < probability

        result = {
            "state": state_name,
            "barrier": barrier.name,
            "probability": round(probability, 6),
            "roll": round(roll, 6),
            "success": success,
            "energy": state.energy,
            "barrier_height": barrier.height,
        }

        if success:
            state.position = barrier.position + barrier.width + 1
            state.tunnel_events += 1
            barrier.penetrated = True
            state.advance()
            result["new_position"] = state.position
        else:
            state.energy *= 0.95
            result["energy_remaining"] = state.energy

        self.tunnel_log.append(result)
        return result

    def step(self):
        self.tick += 1
        for state in self.states.values():
            state.advance(0.1)

    def run_scenario(self, state_name: str, barrier_idx: int, attempts: int = 100) -> Dict:
        successes = 0
        for _ in range(attempts):
            result = self.attempt_tunnel(state_name, barrier_idx)
            if result["success"]:
                successes += 1
        return {
            "state": state_name,
            "barrier": self.barriers[barrier_idx].name if barrier_idx < len(self.barriers) else "?",
            "attempts": attempts,
            "successes": successes,
            "empirical_rate": successes / max(attempts, 1),
            "theoretical_rate": self.states[state_name].compute_tunnel_probability(
                self.barriers[barrier_idx]
            ) if barrier_idx < len(self.barriers) else 0,
        }

    def state_vector(self) -> Dict:
        return {
            "tick": self.tick,
            "states": len(self.states),
            "barriers": len(self.barriers),
            "tunnel_events": sum(s.tunnel_events for s in self.states.values()),
            "states_detail": {
                name: {"energy": s.energy, "position": round(s.position, 2),
                       "tunnels": s.tunnel_events}
                for name, s in self.states.items()
            },
        }


def demo():
    engine = QuantumTunnelingEngine(seed=42)
    print("=== Quantum Tunneling Engine ===")

    engine.add_state("electron_a", energy=3.0, position=0)
    engine.add_state("electron_b", energy=1.5, position=0)
    engine.add_state("proton", energy=8.0, position=0)

    engine.add_barrier("error_wall", width=1.0, height=5.0, position=5.0)
    engine.add_barrier("deadlock_gate", width=2.0, height=4.0, position=10.0)
    engine.add_barrier("thin membrane", width=0.3, height=6.0, position=15.0)

    print("  Running tunnel scenarios...")
    for state_name in ["electron_a", "electron_b", "proton"]:
        for b_idx in range(3):
            result = engine.run_scenario(state_name, b_idx, attempts=50)
            print(f"  {state_name} vs {engine.barriers[b_idx].name}: "
                  f"empirical={result['empirical_rate']:.2f}, "
                  f"theoretical={result['theoretical_rate']:.4f}")

    state = engine.state_vector()
    print(f"\nTotal tunnel events: {state['tunnel_events']}")
    for name, detail in state["states_detail"].items():
        print(f"  {name}: energy={detail['energy']:.2f}, "
              f"position={detail['position']}, tunnels={detail['tunnels']}")

    return state


if __name__ == "__main__":
    demo()
