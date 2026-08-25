from __future__ import annotations
"""Bioacoustic Monitor — listens to system sounds and detects anomalies.

Like bioacousticians who monitor forest sounds to detect species health,
this module analyzes system event streams as "soundscapes" and detects
anomalous patterns — unusual rhythms, missing beats, or new frequencies.
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

@dataclass
class AcousticEvent:
    timestamp: float
    frequency: float
    amplitude: float
    source: str
    is_anomaly: bool = False

@dataclass
class Soundscape:
    name: str
    baseline_frequencies: Dict[str, float]
    current_frequencies: Dict[str, float]
    anomaly_score: float = 0.0

class BioacousticMonitor:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.events: List[AcousticEvent] = []
        self.soundscapes: Dict[str, Soundscape] = {}
        self.anomalies: List[Dict] = []
        self.tick = 0

    def _event_to_frequency(self, event_type: str) -> float:
        h = int(hashlib.md5(event_type.encode()).hexdigest()[:8], 16)
        return (h % 1000) / 100.0

    def record_event(self, source: str, event_type: str,
                     amplitude: float = 1.0) -> AcousticEvent:
        freq = self._event_to_frequency(event_type)
        event = AcousticEvent(
            timestamp=self.tick, frequency=freq,
            amplitude=amplitude, source=source,
        )
        self.events.append(event)
        self.tick += 1
        return event

    def learn_baseline(self, soundscape_name: str, event_types: List[str]):
        freqs = {}
        for et in event_types:
            freqs[et] = self._event_to_frequency(et)
        self.soundscapes[soundscape_name] = Soundscape(
            name=soundscape_name,
            baseline_frequencies=freqs,
            current_frequencies=dict(freqs),
        )

    def detect_anomalies(self, window: int = 10) -> List[Dict]:
        self.anomalies.clear()
        recent = self.events[-window:] if len(self.events) >= window else self.events
        if len(recent) < 3:
            return []

        freqs = [e.frequency for e in recent]
        amps = [e.amplitude for e in recent]
        mean_freq = sum(freqs) / len(freqs)
        mean_amp = sum(amps) / len(amps)

        for event in recent:
            freq_dev = abs(event.frequency - mean_freq) / max(mean_freq, 0.001)
            amp_dev = abs(event.amplitude - mean_amp) / max(mean_amp, 0.001)
            score = freq_dev * 0.5 + amp_dev * 0.5
            if score > 0.5:
                event.is_anomaly = True
                self.anomalies.append({
                    "timestamp": event.timestamp,
                    "source": event.source,
                    "frequency": round(event.frequency, 2),
                    "amplitude": round(event.amplitude, 3),
                    "anomaly_score": round(score, 3),
                })
        return self.anomalies

    def soundscape_health(self) -> Dict:
        total = len(self.events)
        anomalous = sum(1 for e in self.events if e.is_anomaly)
        return {
            "total_events": total,
            "anomalies": anomalous,
            "health_score": round(1.0 - anomalous / max(total, 1), 3),
            "soundscapes": len(self.soundscapes),
        }


def demo():
    monitor = BioacousticMonitor(seed=42)
    print("=== Bioacoustic Monitor ===")
    normal_types = ["heartbeat", "tick", "log", "status", "metric"]
    for _ in range(30):
        source = f"module_{monitor.rng.randint(0, 3)}"
        etype = monitor.rng.choice(normal_types)
        monitor.record_event(source, etype, amplitude=monitor.rng.uniform(0.8, 1.2))

    monitor.record_event("rogue", "ERROR_CASCADE", amplitude=5.0)
    monitor.record_event("rogue", "NULL_FLOOD", amplitude=4.5)

    monitor.learn_baseline("normal", normal_types)
    anomalies = monitor.detect_anomalies(window=15)
    print(f"  Anomalies detected: {len(anomalies)}")
    for a in anomalies:
        print(f"    {a['source']}: freq={a['frequency']}, "
              f"amp={a['amplitude']}, score={a['anomaly_score']}")
    health = monitor.soundscape_health()
    print(f"\n  Health: {health['health_score']}")
    print(f"  Total events: {health['total_events']}")
    return health


if __name__ == "__main__":
    demo()
