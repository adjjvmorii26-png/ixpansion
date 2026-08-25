from __future__ import annotations
"""Information Entropy Decay — measures how information degrades over time.

Like radioactive decay but for information. Stored data gradually loses
fidelity through bit rot, cache invalidation, and reference decay.
This module models decay rates and predicts when information will become
unrecoverable.
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class InformationPacket:
    packet_id: str
    original_data: str
    current_data: str
    integrity: float = 1.0
    age: int = 0
    decay_constant: float = 0.01
    half_life: float = 50.0

    def decay(self, ticks: int = 1) -> float:
        for _ in range(ticks):
            self.age += 1
            self.integrity *= math.exp(-self.decay_constant)
            if self.integrity < 0.01:
                self.current_data = ""
            else:
                corrupted = list(self.current_data)
                for i in range(len(corrupted)):
                    if random.random() < (1 - self.integrity) * 0.1:
                        corrupted[i] = chr(random.randint(32, 126))
                self.current_data = "".join(corrupted)
        return self.integrity

    def recoverable(self) -> bool:
        return self.integrity > 0.1

@dataclass
class DecayCurve:
    packet_id: str
    measurements: List[float]
    estimated_half_life: float
    predicted_unrecoverable_tick: int

class InformationEntropyDecay:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.packets: Dict[str, InformationPacket] = {}
        self.decay_curves: Dict[str, DecayCurve] = {}
        self.tick = 0

    def store(self, packet_id: str, data: str,
              decay_constant: float = 0.01) -> InformationPacket:
        packet = InformationPacket(
            packet_id=packet_id,
            original_data=data,
            current_data=data,
            decay_constant=decay_constant,
            half_life=math.log(2) / decay_constant,
        )
        self.packets[packet_id] = packet
        return packet

    def step(self):
        self.tick += 1
        for packet in self.packets.values():
            packet.decay(1)

    def measure_integrity(self) -> Dict[str, float]:
        return {
            pid: round(p.integrity, 4)
            for pid, p in self.packets.items()
        }

    def build_decay_curve(self, packet_id: str) -> Optional[DecayCurve]:
        if packet_id not in self.packets:
            return None
        packet = self.packets[packet_id]
        measurements = []
        saved_data = packet.current_data
        saved_integrity = packet.integrity
        saved_age = packet.age

        test_packet = InformationPacket(
            packet_id=packet_id,
            original_data=packet.original_data,
            current_data=packet.original_data,
            decay_constant=packet.decay_constant,
        )
        for t in range(100):
            test_packet.decay(1)
            measurements.append(test_packet.integrity)
            if test_packet.integrity < 0.01:
                break

        half_life_tick = 0
        for i, val in enumerate(measurements):
            if val <= 0.5:
                half_life_tick = i + 1
                break

        unrecoverable_tick = len(measurements)
        for i, val in enumerate(measurements):
            if val < 0.1:
                unrecoverable_tick = i + 1
                break

        curve = DecayCurve(
            packet_id=packet_id,
            measurements=measurements,
            estimated_half_life=half_life_tick,
            predicted_unrecoverable_tick=unrecoverable_tick,
        )
        self.decay_curves[packet_id] = curve
        return curve

    def survival_report(self) -> Dict:
        alive = sum(1 for p in self.packets.values() if p.recoverable())
        dead = len(self.packets) - alive
        avg_integrity = sum(p.integrity for p in self.packets.values()) / max(len(self.packets), 1)
        return {
            "total_packets": len(self.packets),
            "surviving": alive,
            "lost": dead,
            "avg_integrity": round(avg_integrity, 4),
            "tick": self.tick,
        }

    def run(self, ticks: int = 100) -> List[Dict]:
        history = []
        for _ in range(ticks):
            self.step()
            history.append(self.measure_integrity())
        return history


def demo():
    engine = InformationEntropyDecay(seed=42)
    print("=== Information Entropy Decay ===")

    packets_data = [
        ("critical_config", '{"key": "value"}', 0.005),
        ("agent_memory", "episode_42: saw a unicorn", 0.01),
        ("temp_log", "tick_001: nominal", 0.02),
        ("ancient_code", "def legacy(): pass", 0.003),
        ("volatile_cache", "data_x_99", 0.05),
    ]
    for pid, data, dc in packets_data:
        engine.store(pid, data, decay_constant=dc)

    print(f"  Stored {len(engine.packets)} packets")

    history = engine.run(ticks=80)
    final = engine.measure_integrity()
    print(f"\nAfter 80 ticks:")
    for pid, integrity in final.items():
        status = "ALIVE" if integrity > 0.1 else "LOST"
        print(f"  {pid}: integrity={integrity:.4f} [{status}]")

    report = engine.survival_report()
    print(f"\nSurvival: {report['surviving']}/{report['total_packets']} alive")

    for pid in ["critical_config", "volatile_cache"]:
        curve = engine.build_decay_curve(pid)
        if curve:
            print(f"\n{pid} decay curve:")
            print(f"  Estimated half-life: {curve.estimated_half_life} ticks")
            print(f"  Unrecoverable at: tick {curve.predicted_unrecoverable_tick}")

    return report


if __name__ == "__main__":
    demo()
