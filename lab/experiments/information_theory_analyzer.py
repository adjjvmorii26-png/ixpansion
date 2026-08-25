from __future__ import annotations
"""Information Theory Analyzer — measures entropy, mutual information, and capacity.

Applies Shannon's information theory to measure how much information
flows through the system, where bottlenecks are, and what the channel
capacity is between subsystems.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class Channel:
    name: str
    capacity: float
    utilization: float
    noise: float
    mutual_information: float

class InformationTheoryAnalyzer:
    def __init__(self):
        self.channels: Dict[str, Channel] = {}
        self.message_log: List[Dict] = []

    def add_channel(self, name: str, capacity: float = 1.0):
        self.channels[name] = Channel(
            name=name, capacity=capacity,
            utilization=0.0, noise=0.1, mutual_information=0.0,
        )

    def send(self, channel_name: str, message_size: float, noise_level: float = 0.1):
        if channel_name not in self.channels:
            return
        ch = self.channels[channel_name]
        ch.noise = noise_level
        ch.utilization = min(1.0, message_size / ch.capacity)
        ch.mutual_information = max(0, ch.capacity * (1 - noise_level) * ch.utilization)
        self.message_log.append({
            "channel": channel_name, "size": message_size,
            "noise": noise_level,
            "mutual_info": round(ch.mutual_information, 4),
        })

    def channel_report(self) -> List[Dict]:
        return [
            {"name": ch.name, "capacity": ch.capacity,
             "utilization": round(ch.utilization, 3),
             "noise": round(ch.noise, 3),
             "mutual_info": round(ch.mutual_information, 4),
             "shannon_limit": round(ch.capacity * math.log2(1 + (1 - ch.noise)), 4)}
            for ch in self.channels.values()
        ]

    def system_entropy(self) -> float:
        if not self.channels:
            return 0.0
        total_mi = sum(ch.mutual_information for ch in self.channels.values())
        total_cap = sum(ch.capacity for ch in self.channels.values())
        return total_mi / max(total_cap, 0.001)


def demo():
    analyzer = InformationTheoryAnalyzer()
    print("=== Information Theory Analyzer ===")
    analyzer.add_channel("nucleus→agent", capacity=10.0)
    analyzer.add_channel("agent→sandbox", capacity=8.0)
    analyzer.add_channel("sandbox→protocol", capacity=6.0)
    analyzer.add_channel("protocol→nucleus", capacity=5.0)
    analyzer.send("nucleus→agent", 7.0, noise_level=0.05)
    analyzer.send("agent→sandbox", 6.0, noise_level=0.1)
    analyzer.send("sandbox→protocol", 4.0, noise_level=0.15)
    analyzer.send("protocol→nucleus", 3.0, noise_level=0.2)
    report = analyzer.channel_report()
    print("  Channel analysis:")
    for ch in report:
        print(f"    {ch['name']}: util={ch['utilization']}, "
              f"MI={ch['mutual_info']}, shannon={ch['shannon_limit']}")
    entropy = analyzer.system_entropy()
    print(f"\n  System entropy: {entropy:.4f}")
    return {"channels": report, "entropy": entropy}


if __name__ == "__main__":
    demo()
