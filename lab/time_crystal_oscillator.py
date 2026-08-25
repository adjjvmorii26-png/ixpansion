"""Time Crystal Oscillator — Creates periodic patterns that return to initial state.

A discrete-time crystal that periodically returns to its initial state
after N pulses, creating temporal recursion where the system remembers
its own future by recalling what it did last cycle.
"""
from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TimeCrystal:
    def __init__(self, period: int = 6, seed=42):
        self.period = period
        self.seed = seed
        self.tick_count = 0
        self.state_history: list[dict] = []
        self.echoes: list[dict] = []
        self.resonances: list[dict] = []

    def pulse(self, agent_states: dict = None) -> dict:
        self.tick_count += 1
        phase = self.tick_count % self.period
        state = {
            "tick": self.tick_count,
            "phase": phase,
            "agents": agent_states or {},
        }
        self.state_history.append(state)
        is_echo = phase == 0
        if is_echo:
            echo = {
                "tick": self.tick_count,
                "echo_of": self.period,
                "agents": dict(agent_states or {}),
                "strength": 1.0,
            }
            self.echoes.append(echo)
        if phase == self.period // 2:
            resonance = {
                "tick": self.tick_count,
                "half_period": True,
                "agents": dict(agent_states or {}),
            }
            self.resonances.append(resonance)
        return {"tick": self.tick_count, "phase": phase, "is_echo": is_echo, "is_resonance": phase == self.period // 2}

    def get_echo(self, ticks_back: int = None) -> dict | None:
        if ticks_back is None and self.echoes:
            return self.echoes[-1]
        if ticks_back is not None:
            target_tick = self.tick_count - ticks_back
            for echo in reversed(self.echoes):
                if echo["tick"] == target_tick:
                    return echo
        return None

    def simulate(self, ticks=30, agents=None) -> dict:
        agent_names = agents or ["scout", "sentinel", "architect", "wanderer"]
        for i in range(ticks):
            agent_states = {name: {"energy": 0.5 + (i * 0.01) % 0.5} for name in agent_names}
            self.pulse(agent_states)
        return {
            "ticks": ticks,
            "period": self.period,
            "echoes": len(self.echoes),
            "resonances": len(self.resonances),
            "total_phases": self.tick_count,
        }

    def report(self) -> dict:
        return {
            "crystal": "time_crystal_oscillator",
            "period": self.period,
            "tick": self.tick_count,
            "echoes": len(self.echoes),
            "resonances": len(self.resonances),
        }


def demo():
    crystal = TimeCrystal(period=6, seed=42)
    sim = crystal.simulate(ticks=30)
    echo = crystal.get_echo()
    return {"simulation": sim, "echo": echo, "report": crystal.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
