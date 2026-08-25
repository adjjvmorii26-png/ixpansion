"""Temporal Echo Engine — Creates and detects echoes across time.

Models how past events reverberate through the system, creating
temporal echoes that can be detected and analyzed.
"""
from __future__ import annotations
import hashlib
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TemporalEcho:
    def __init__(self, source_tick: int, content: dict, strength: float = 1.0):
        self.source_tick = source_tick
        self.content = content
        self.strength = strength
        self.decay_rate = 0.1
        self.detected = False

    def decay(self, current_tick: int):
        age = current_tick - self.source_tick
        self.strength *= (1 - self.decay_rate) ** age

    def to_dict(self) -> dict:
        return {
            "source_tick": self.source_tick,
            "strength": round(self.strength, 4),
            "content": self.content,
        }


class TemporalEchoEngine:
    def __init__(self, echo_interval: int = 5, seed=42):
        self.echo_interval = echo_interval
        self.seed = seed
        self.tick_count = 0
        self.events: list[dict] = []
        self.echoes: list[TemporalEcho] = []
        self.detections: list[dict] = []

    def tick(self, event: dict = None):
        self.tick_count += 1
        if event:
            self.events.append({"tick": self.tick_count, **event})
        if self.tick_count % self.echo_interval == 0:
            echo_content = {
                "source_tick": self.tick_count,
                "events_since": len([e for e in self.events if e["tick"] > self.tick_count - self.echo_interval]),
            }
            echo = TemporalEcho(self.tick_count, echo_content, strength=1.0)
            self.echoes.append(echo)
        for echo in self.echoes:
            echo.decay(self.tick_count)
            if echo.strength < 0.01 and not echo.detected:
                echo.detected = True
                self.detections.append({
                    "echo_source": echo.source_tick,
                    "final_strength": round(echo.strength, 4),
                    "lifetime": self.tick_count - echo.source_tick,
                })

    def detect_echoes(self, threshold: float = 0.1) -> list[dict]:
        active = [e for e in self.echoes if e.strength >= threshold and not e.detected]
        return [{"source_tick": e.source_tick, "strength": round(e.strength, 4)} for e in active]

    def simulate(self, ticks=30):
        import random
        rng = random.Random(self.seed)
        for _ in range(ticks):
            event = {"type": rng.choice(["action", "signal", "pulse"]), "data": rng.randint(0, 100)}
            self.tick(event)
        return {
            "ticks": ticks,
            "total_events": len(self.events),
            "total_echoes": len(self.echoes),
            "total_detections": len(self.detections),
            "active_echoes": len(self.detect_echoes()),
        }

    def report(self) -> dict:
        return {
            "engine": "temporal_echo_engine",
            "ticks": self.tick_count,
            "events": len(self.events),
            "echoes": len(self.echoes),
            "detections": len(self.detections),
            "active": self.detect_echoes()[:5],
        }


def demo():
    engine = TemporalEchoEngine(echo_interval=5, seed=42)
    sim = engine.simulate(ticks=30)
    return {"simulation": sim, "report": engine.report()}


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
