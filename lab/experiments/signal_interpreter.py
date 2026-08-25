from __future__ import annotations
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class SignalInterpreter:
    def __init__(self, seed=42):
        self.seed = seed; self.signals = []; self.interpretations = []
    def receive(self, source, signal_type, payload, strength=1.0):
        self.signals.append({"source": source, "type": signal_type, "payload": payload, "strength": strength})
    def interpret(self):
        self.interpretations = []
        for sig in self.signals:
            meaning = "neutral"
            if sig["strength"] > 0.8: meaning = "urgent"
            elif sig["strength"] < 0.3: meaning = "whisper"
            if sig["type"] == "alert": meaning = "danger:" + meaning
            elif sig["type"] == "discovery": meaning = "opportunity:" + meaning
            self.interpretations.append({"source": sig["source"], "meaning": meaning, "strength": sig["strength"]})
        return self.interpretations
    def report(self):
        self.interpret()
        types = {}
        for s in self.signals: types[s["type"]] = types.get(s["type"], 0) + 1
        return {"interpreter": "signal_interpreter", "signals": len(self.signals),
                "interpretations": len(self.interpretations), "types": types,
                "top_interpretations": self.interpretations[:5]}

def demo():
    si = SignalInterpreter(42)
    si.receive("scout_0", "discovery", {"target": "anomaly"}, 0.9)
    si.receive("sentinel_0", "alert", {"threat": 7}, 0.95)
    si.receive("architect_0", "status", {"progress": 0.6}, 0.4)
    si.receive("wanderer_0", "discovery", {"target": "pattern"}, 0.6)
    return si.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
