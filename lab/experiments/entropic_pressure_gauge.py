from __future__ import annotations
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class EntropicPressureGauge:
    def __init__(self, seed=42):
        self.seed = seed; self.readings = []
    def measure(self, label, value, baseline=0.5):
        deviation = abs(value - baseline)
        pressure = min(100.0, deviation * 200)
        self.readings.append({"label": label, "value": value, "baseline": baseline,
                              "pressure": round(pressure, 2),
                              "status": "critical" if pressure > 75 else "warning" if pressure > 40 else "normal"})
    def avg_pressure(self):
        return round(sum(r["pressure"] for r in self.readings) / max(1, len(self.readings)), 2)
    def report(self):
        return {"gauge": "entropic_pressure_gauge", "readings": len(self.readings),
                "avg_pressure": self.avg_pressure(),
                "critical": sum(1 for r in self.readings if r["status"]=="critical"),
                "warning": sum(1 for r in self.readings if r["status"]=="warning"),
                "details": self.readings[:10]}

def demo():
    g = EntropicPressureGauge(42)
    g.measure("entropy", 0.8, 0.5); g.measure("cohesion", 0.2, 0.7)
    g.measure("complexity", 0.9, 0.4); g.measure("stability", 0.6, 0.5)
    return g.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
