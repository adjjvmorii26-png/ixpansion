from __future__ import annotations
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class PhaseTransitionMonitor:
    def __init__(self, seed=42):
        self.seed = seed; self.readings = []; self.transitions = []
    def read(self, metric_name, value, threshold_high=0.8, threshold_low=0.2):
        phase = "critical" if value > threshold_high or value < threshold_low else "stable"
        self.readings.append({"metric": metric_name, "value": value, "phase": phase})
    def detect_transitions(self):
        self.transitions = []
        for i in range(1, len(self.readings)):
            prev = self.readings[i-1]; curr = self.readings[i]
            if prev["phase"] != curr["phase"]:
                self.transitions.append({"from": prev["phase"], "to": curr["phase"],
                                         "metric": curr["metric"], "value": curr["value"]})
        return self.transitions
    def report(self):
        self.detect_transitions()
        phases = {}
        for r in self.readings: phases[r["phase"]] = phases.get(r["phase"], 0) + 1
        return {"monitor": "phase_transition_monitor", "readings": len(self.readings),
                "transitions": len(self.transitions), "phase_distribution": phases,
                "transition_details": self.transitions[:5]}

def demo():
    m = PhaseTransitionMonitor(42); rng = random.Random(42)
    for i in range(20):
        v = 0.5 + 0.4 * (1 if i % 7 == 0 else -1) * rng.uniform(0.5, 1.0)
        m.read("entropy", max(0, min(1, v)))
    return m.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
