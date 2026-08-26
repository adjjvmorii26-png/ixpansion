"""Pattern Recognizer — finds hidden patterns across all experiments.

Scans experiment outputs, system metrics, and agent behavior to find
correlations, cycles, and anomalies that no single module would detect.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


class PatternRecognizer:
    def __init__(self):
        self.datapoints: List[Dict] = []
        self.patterns: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "patterns.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.datapoints = data.get("datapoints", [])
            self.patterns = data.get("patterns", [])

    def _save(self):
        path = ROOT / ".runtime" / "patterns.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "datapoints": self.datapoints[-2000:],
            "patterns": self.patterns[-500:],
        }, indent=2))

    def record(self, source: str, metric: str, value: float) -> Dict:
        dp = {"source": source, "metric": metric, "value": value, "timestamp": time.time()}
        self.datapoints.append(dp)
        self._scan_for_patterns(source, metric)
        self._save()
        return dp

    def _scan_for_patterns(self, source: str, metric: str):
        recent = [d for d in self.datapoints if d["source"] == source and d["metric"] == metric]
        if len(recent) < 5:
            return
        values = [d["value"] for d in recent[-10:]]
        mean = sum(values) / len(values)
        trend = values[-1] - values[0]
        if abs(trend) > 0.3:
            self.patterns.append({
                "pattern_id": hashlib.sha256(f"{source}:{metric}:{time.time()}".encode()).hexdigest()[:10],
                "type": "trend", "source": source, "metric": metric,
                "direction": "rising" if trend > 0 else "falling",
                "strength": round(abs(trend), 4),
                "detected_at": time.time(),
            })
        if len(values) >= 6:
            ups = sum(1 for i in range(1, len(values)) if values[i] > values[i-1])
            if ups >= len(values) - 1:
                self.patterns.append({
                    "pattern_id": hashlib.sha256(f"cycle:{source}:{time.time()}".encode()).hexdigest()[:10],
                    "type": "cycle", "source": source, "metric": metric,
                    "period": len(values), "detected_at": time.time(),
                })

    def scan_all(self) -> List[Dict]:
        sources = set(d["source"] for d in self.datapoints)
        metrics = set(d["metric"] for d in self.datapoints)
        for source in sources:
            for metric in metrics:
                self._scan_for_patterns(source, metric)
        self._save()
        return self.patterns

    def recent_patterns(self, limit: int = 20) -> List[Dict]:
        return self.patterns[-limit:]

    def stats(self) -> Dict:
        return {
            "datapoints": len(self.datapoints),
            "patterns_found": len(self.patterns),
            "sources": len(set(d["source"] for d in self.datapoints)),
        }


def handler(request, response):
    pr = PatternRecognizer()
    return pr.stats()


def demo():
    pr = PatternRecognizer()
    print("=== Pattern Recognizer ===")
    for i in range(12):
        pr.record("neural_fabric", "activation", 0.3 + i * 0.05 + random.uniform(-0.02, 0.02))
    pr.record("dream_synthesis", "coherence", 0.8)
    pr.scan_all()
    for p in pr.recent_patterns(3):
        print(f"\n  Pattern: {p['type']} in {p['source']}")
        print(f"    Direction: {p.get('direction', 'N/A')}, Strength: {p.get('strength', 'N/A')}")
    return pr.stats()


if __name__ == "__main__":
    demo()
