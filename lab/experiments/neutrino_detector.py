from __future__ import annotations
"""Neutrino Detector — ultra-sensitive event detection system.

Like real neutrino detectors that catch nearly invisible particles, this
system detects subtle anomalies, rare events, and faint signals buried
in noise. Uses coincidence detection, statistical filtering, and
pattern recognition to separate signal from noise.
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import Counter

@dataclass
class SignalEvent:
    timestamp: float
    channel: str
    amplitude: float
    energy: float
    direction: Tuple[float, float]
    raw_data: List[float] = field(default_factory=list)
    classified: str = "unknown"
    confidence: float = 0.0

@dataclass
class Detection:
    event_a: str
    event_b: str
    coincidence_score: float
    time_delta: float
    classification: str

class NeutrinoDetector:
    def __init__(self, channels: int = 8, noise_floor: float = 0.1, seed: int = 42):
        self.channels = channels
        self.noise_floor = noise_floor
        self.rng = random.Random(seed)
        self.events: List[SignalEvent] = []
        self.detections: List[Detection] = []
        self.stats: Dict[str, int] = Counter()

    def generate_noise(self, count: int = 100) -> List[SignalEvent]:
        noise_events = []
        for i in range(count):
            amplitude = abs(self.rng.gauss(0, self.noise_floor))
            event = SignalEvent(
                timestamp=self.rng.uniform(0, 1000),
                channel=f"ch_{self.rng.randint(0, self.channels - 1)}",
                amplitude=amplitude,
                energy=amplitude * self.rng.uniform(0.5, 1.5),
                direction=(self.rng.uniform(-1, 1), self.rng.uniform(-1, 1)),
                raw_data=[self.rng.gauss(0, self.noise_floor) for _ in range(10)],
                classified="noise",
            )
            noise_events.append(event)
        self.events.extend(noise_events)
        self.stats["noise"] += len(noise_events)
        return noise_events

    def inject_signal(self, timestamp: float = 500.0, amplitude: float = 2.0,
                      channel: str = "ch_0", energy: float = 10.0) -> SignalEvent:
        signal = SignalEvent(
            timestamp=timestamp,
            channel=channel,
            amplitude=amplitude,
            energy=energy,
            direction=(0.5, -0.3),
            raw_data=[amplitude * math.sin(i * 0.5) + self.rng.gauss(0, 0.05)
                      for i in range(10)],
        )
        self.events.append(signal)
        self.stats["signal"] += 1
        return signal

    def inject_coincidence(self, time_delta: float = 0.001,
                           amplitude: float = 3.0) -> Tuple[SignalEvent, SignalEvent]:
        t = self.rng.uniform(100, 900)
        ch1 = f"ch_{self.rng.randint(0, self.channels // 2 - 1)}"
        ch2 = f"ch_{self.rng.randint(self.channels // 2, self.channels - 1)}"
        e1 = SignalEvent(
            timestamp=t, channel=ch1, amplitude=amplitude,
            energy=amplitude * 2,
            direction=(0.1, 0.2),
            raw_data=[amplitude + self.rng.gauss(0, 0.1) for _ in range(10)],
        )
        e2 = SignalEvent(
            timestamp=t + time_delta, channel=ch2, amplitude=amplitude * 0.9,
            energy=amplitude * 1.8,
            direction=(0.1, 0.2),
            raw_data=[amplitude * 0.9 + self.rng.gauss(0, 0.1) for _ in range(10)],
        )
        self.events.extend([e1, e2])
        self.stats["signal"] += 2
        return e1, e2

    def detect_coincidences(self, time_window: float = 0.01,
                            min_amplitude: float = 1.0) -> List[Detection]:
        candidates = [e for e in self.events if e.amplitude > min_amplitude]
        candidates.sort(key=lambda e: e.timestamp)
        self.detections.clear()

        for i, a in enumerate(candidates):
            for b in candidates[i + 1:]:
                dt = abs(b.timestamp - a.timestamp)
                if dt > time_window:
                    continue
                direction_match = 1.0 - math.sqrt(
                    (a.direction[0] - b.direction[0]) ** 2 +
                    (a.direction[1] - b.direction[1]) ** 2
                ) / 2.0
                amplitude_match = 1.0 - abs(a.amplitude - b.amplitude) / max(a.amplitude, b.amplitude)
                time_score = 1.0 - dt / time_window
                score = (direction_match * 0.3 + amplitude_match * 0.3 + time_score * 0.4)

                if score > 0.5:
                    classification = "neutrino" if score > 0.8 else "候选"
                    det = Detection(
                        event_a=f"{a.channel}@{a.timestamp:.3f}",
                        event_b=f"{b.channel}@{b.timestamp:.3f}",
                        coincidence_score=score,
                        time_delta=dt,
                        classification=classification,
                    )
                    self.detections.append(det)
                    self.stats["detection"] += 1

        return self.detections

    def classify_events(self) -> Dict[str, int]:
        for event in self.events:
            if event.classified != "unknown":
                continue
            if event.amplitude < self.noise_floor * 2:
                event.classified = "noise"
            elif event.amplitude > self.noise_floor * 5:
                event.classified = "signal"
            else:
                event.classified = "marginal"
            self.stats[event.classified] += 1
        return dict(self.stats)

    def sensitivity_report(self) -> Dict:
        signal_events = [e for e in self.events if e.classified == "signal"]
        noise_events = [e for e in self.events if e.classified == "noise"]
        avg_signal = sum(e.amplitude for e in signal_events) / max(len(signal_events), 1)
        avg_noise = sum(e.amplitude for e in noise_events) / max(len(noise_events), 1)

        return {
            "total_events": len(self.events),
            "signal_count": len(signal_events),
            "noise_count": len(noise_events),
            "detections": len(self.detections),
            "avg_signal_amplitude": round(avg_signal, 4),
            "avg_noise_amplitude": round(avg_noise, 4),
            "signal_to_noise": round(avg_signal / max(avg_noise, 1e-10), 2),
            "sensitivity": round(avg_noise * 3, 4),
            "stats": dict(self.stats),
        }


def demo():
    detector = NeutrinoDetector(channels=8, noise_floor=0.1, seed=42)
    print("=== Neutrino Detector ===")

    detector.generate_noise(count=200)
    print(f"  Generated 200 noise events")

    detector.inject_signal(timestamp=500.0, amplitude=2.5, channel="ch_3")
    detector.inject_signal(timestamp=750.0, amplitude=3.0, channel="ch_5")
    detector.inject_coincidence(time_delta=0.0005, amplitude=4.0)
    detector.inject_coincidence(time_delta=0.0008, amplitude=3.5)
    print(f"  Injected 2 signals + 2 coincidences")

    classifications = detector.classify_events()
    print(f"\n  Classifications: {classifications}")

    detections = detector.detect_coincidences(time_window=0.01, min_amplitude=1.0)
    print(f"\n  Coincidences found: {len(detections)}")
    for d in detections:
        print(f"    {d.event_a} <-> {d.event_b}: score={d.coincidence_score:.3f} "
              f"dt={d.time_delta:.6f} class={d.classification}")

    report = detector.sensitivity_report()
    print(f"\n  Signal-to-noise ratio: {report['signal_to_noise']}")
    print(f"  Sensitivity threshold: {report['sensitivity']}")

    return report


if __name__ == "__main__":
    demo()
