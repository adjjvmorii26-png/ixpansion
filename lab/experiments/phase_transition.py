from __future__ import annotations
"""Phase Transition — detects sudden qualitative changes in system state.

Like water freezing or boiling, systems can undergo sudden phase transitions
where quantitative changes trigger qualitative reorganization. This module
monitors system metrics and detects when phase transitions occur.
"""
import math
import random
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum

class Phase(Enum):
    SOLID = "solid"
    LIQUID = "liquid"
    GAS = "gas"
    PLASMA = "plasma"
    BOSE_EINSTEIN = "bose_einstein"

@dataclass
class SystemState:
    temperature: float = 0.0
    pressure: float = 1.0
    density: float = 1.0
    energy: float = 0.0
    order_parameter: float = 1.0

@dataclass
class TransitionEvent:
    from_phase: Phase
    to_phase: Phase
    trigger_value: float
    critical_point: float
    timestamp: int
    description: str

class PhaseTransitionDetector:
    CRITICAL_POINTS = {
        (Phase.SOLID, Phase.LIQUID): 0.3,
        (Phase.LIQUID, Phase.GAS): 0.6,
        (Phase.GAS, Phase.PLASMA): 0.85,
        (Phase.SOLID, Phase.BOSE_EINSTEIN): 0.01,
    }

    def __init__(self):
        self.current_phase = Phase.SOLID
        self.history: List[SystemState] = []
        self.transitions: List[TransitionEvent] = []
        self.tick = 0

    def _classify_phase(self, state: SystemState) -> Phase:
        if state.temperature < 0.05:
            return Phase.BOSE_EINSTEIN
        elif state.temperature < 0.3:
            return Phase.SOLID
        elif state.temperature < 0.6:
            return Phase.LIQUID
        elif state.temperature < 0.85:
            return Phase.GAS
        return Phase.PLASMA

    def record(self, temperature: float, pressure: float = 1.0,
               density: float = 1.0) -> Optional[TransitionEvent]:
        self.tick += 1
        state = SystemState(
            temperature=temperature, pressure=pressure, density=density,
            energy=temperature * pressure,
            order_parameter=max(0, 1.0 - temperature),
        )
        self.history.append(state)

        new_phase = self._classify_phase(state)
        transition = None

        if new_phase != self.current_phase:
            pair = (self.current_phase, new_phase)
            critical = self.CRITICAL_POINTS.get(pair, 0.5)
            transition = TransitionEvent(
                from_phase=self.current_phase, to_phase=new_phase,
                trigger_value=temperature, critical_point=critical,
                timestamp=self.tick,
                description=f"Transitioned from {self.current_phase.value} "
                           f"to {new_phase.value} at T={temperature:.3f}",
            )
            self.transitions.append(transition)
            self.current_phase = new_phase

        return transition

    def stability_analysis(self) -> Dict:
        if len(self.history) < 10:
            return {"stable": True, "variance": 0.0}
        recent = [s.temperature for s in self.history[-10:]]
        variance = sum((t - sum(recent)/len(recent))**2 for t in recent) / len(recent)
        return {
            "stable": variance < 0.01,
            "variance": round(variance, 6),
            "current_phase": self.current_phase.value,
            "temperature_trend": "rising" if recent[-1] > recent[0] else "falling",
        }

    def phase_diagram(self) -> Dict:
        phase_counts = {}
        for s in self.history:
            phase = self._classify_phase(s).value
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
        return {
            "total_states": len(self.history),
            "transitions": len(self.transitions),
            "current_phase": self.current_phase.value,
            "phase_distribution": phase_counts,
            "transition_history": [
                {"from": t.from_phase.value, "to": t.to_phase.value,
                 "at_T": round(t.trigger_value, 3), "tick": t.timestamp}
                for t in self.transitions
            ],
        }


def demo():
    detector = PhaseTransitionDetector()
    print("=== Phase Transition Detector ===")

    temperatures = (
        [0.01] * 5 + [0.1] * 5 + [0.2] * 3 + [0.35] * 5 +
        [0.45] * 3 + [0.55] * 5 + [0.65] * 3 + [0.75] * 5 +
        [0.9] * 5 + [0.95] * 3
    )

    transitions_found = 0
    for t in temperatures:
        result = detector.record(t)
        if result:
            transitions_found += 1
            print(f"  {result.description}")

    print(f"\nTotal transitions: {transitions_found}")
    diagram = detector.phase_diagram()
    print(f"Phase distribution: {diagram['phase_distribution']}")
    print(f"Current phase: {diagram['current_phase']}")

    stability = detector.stability_analysis()
    print(f"Stability: stable={stability['stable']}, variance={stability['variance']}")

    return diagram


if __name__ == "__main__":
    demo()
