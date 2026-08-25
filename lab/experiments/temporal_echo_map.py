from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class TemporalEchoMap:
    def __init__(self, seed=42):
        self.seed = seed; self.events = []; self.echoes = []
    def record_event(self, name, data, tick):
        self.events.append({"name": name, "data": data, "tick": tick})
    def generate_echoes(self, delay=3):
        self.echoes = []
        for i, event in enumerate(self.events):
            for j in range(i+1, len(self.events)):
                if self.events[j]["tick"] - event["tick"] == delay:
                    self.echoes.append({"original": event["name"], "echo": self.events[j]["name"],
                                        "delay": delay, "match": event["data"] == self.events[j]["data"]})
        return self.echoes
    def report(self):
        self.generate_echoes()
        return {"map": "temporal_echo_map", "events": len(self.events), "echoes": len(self.echoes),
                "echo_details": self.echoes[:5]}

def demo():
    m = TemporalEchoMap(42)
    for i in range(15):
        m.record_event(f"event_{i%5}", {"value": i % 3}, i)
    return m.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
