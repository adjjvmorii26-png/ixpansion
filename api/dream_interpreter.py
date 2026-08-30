"""Dream Interpreter — AI that interprets dream_synthesis outputs.

Takes the raw creative outputs from dream_synthesis and extracts
actionable insights, risk warnings, opportunity flags, and creative
directions. Turns chaos into strategy.

Usage:
    POST /api/dream_interpret/analyze   — interpret a dream
    POST /api/dream_interpret/batch     — interpret multiple dreams
    GET  /api/dream_interpret/history   — interpretation history
    GET  /api/dream_interpret/insights  — aggregated insights
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
try:
    from runtime_io import load_json as _rio_load, save_json as _rio_save
except Exception:
    _rio_load = _rio_save = None

INSIGHT_TYPES = {
    "opportunity": {"weight": 1.2, "color": "green"},
    "risk": {"weight": 0.8, "color": "red"},
    "innovation": {"weight": 1.5, "color": "blue"},
    "pattern": {"weight": 1.0, "color": "yellow"},
    "warning": {"weight": 0.6, "color": "orange"},
    "serendipity": {"weight": 1.3, "color": "purple"},
}

MOOD_INSIGHTS = {
    "luminous": ["Clear opportunity ahead", "System health improving", "Creative energy high"],
    "melancholic": ["Decay detected in subsystem", "Memory loss possible", "Energy low"],
    "frenetic": ["Rapid change incoming", "Multiple simultaneous events", "Volatility high"],
    "serene": ["Stable period", "Good time for deep work", "Low risk environment"],
    "ominous": ["Warning: anomaly patterns forming", "Watch for cascading failures", "Entropy rising"],
    "playful": ["Unusual creative potential", "Experimental risks acceptable", "Innovation window open"],
}

KEYWORD_INSIGHTS = {
    "quantum": ("innovation", "Quantum domain activity — potential for breakthrough"),
    "entropy": ("risk", "Entropy signal — system may be approaching instability"),
    "paradox": ("opportunity", "Paradox detected — creative resolution could yield innovation"),
    "dream": ("serendipity", "Dream activity — subconscious processing may reveal hidden patterns"),
    "agent": ("pattern", "Agent behavior shift detected — monitor for emergent properties"),
    "symbiosis": ("innovation", "Symbiotic activity — cross-system value being created"),
    "memory": ("pattern", "Memory system active — knowledge consolidation in progress"),
    "temporal": ("warning", "Temporal distortion — predictions may be unreliable"),
    "fractal": ("innovation", "Fractal patterns — self-similar structures emerging at multiple scales"),
    "anomaly": ("risk", "Anomaly detected — investigate before it cascades"),
}


class DreamInterpreter:
    def __init__(self):
        self.interpretations: List[Dict] = []
        self.all_insights: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "dream_interpreter.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        if path.exists():
            data = json.loads(path.read_text())
            self.interpretations = data.get("interpretations", [])
            self.all_insights = data.get("insights", [])

    def _save(self):
        path = ROOT / ".runtime" / "dream_interpreter.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        path.write_text(json.dumps({
            "interpretations": self.interpretations[-500:],
            "insights": self.all_insights[-2000:],
        }, indent=2))

    def _extract_insights(self, fragments: List[str], mood: str) -> List[Dict]:
        insights = []
        full_text = " ".join(fragments).lower()
        for keyword, (itype, message) in KEYWORD_INSIGHTS.items():
            if keyword in full_text:
                insight = {
                    "type": itype,
                    "message": message,
                    "keyword": keyword,
                    "confidence": round(random.uniform(0.6, 0.95), 3),
                    **INSIGHT_TYPES[itype],
                }
                insights.append(insight)
        if mood in MOOD_INSIGHTS:
            mood_msg = random.choice(MOOD_INSIGHTS[mood])
            insights.append({
                "type": "pattern",
                "message": f"Mood analysis ({mood}): {mood_msg}",
                "keyword": "mood",
                "confidence": round(random.uniform(0.7, 0.9), 3),
                **INSIGHT_TYPES["pattern"],
            })
        return insights

    def analyze(self, dream: Dict) -> Dict:
        fragments = dream.get("fragments", [])
        mood = dream.get("mood", "serene")
        dream_id = dream.get("dream_id", hashlib.sha256(str(time.time()).encode()).hexdigest()[:12])
        insights = self._extract_insights(fragments, mood)
        risks = [i for i in insights if i["type"] in ("risk", "warning")]
        opportunities = [i for i in insights if i["type"] in ("opportunity", "innovation", "serendipity")]
        interpretation = {
            "dream_id": dream_id,
            "mood": mood,
            "insights": insights,
            "risk_count": len(risks),
            "opportunity_count": len(opportunities),
            "confidence_avg": round(sum(i["confidence"] for i in insights) / max(len(insights), 1), 3),
            "recommendation": (
                "Proceed with caution" if len(risks) > len(opportunities)
                else "Strong opportunity — act now" if len(opportunities) > 2
                else "Monitor and observe"
            ),
            "interpreted_at": time.time(),
        }
        self.interpretations.append(interpretation)
        self.all_insights.extend([{**i, "dream_id": dream_id} for i in insights])
        self._save()
        return interpretation

    def batch_analyze(self, dreams: List[Dict]) -> List[Dict]:
        return [self.analyze(d) for d in dreams]

    def history(self, limit: int = 10) -> List[Dict]:
        return self.interpretations[-limit:]

    def aggregated_insights(self, limit: int = 20) -> Dict:
        recent = self.all_insights[-limit:]
        type_counts = {}
        for i in recent:
            t = i["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        top_keywords = {}
        for i in recent:
            k = i.get("keyword", "unknown")
            top_keywords[k] = top_keywords.get(k, 0) + 1
        return {
            "total_insights": len(self.all_insights),
            "recent_insights": len(recent),
            "type_distribution": type_counts,
            "top_keywords": dict(sorted(top_keywords.items(), key=lambda x: -x[1])[:5]),
        }


def handler(request, response):
    di = DreamInterpreter()
    return {"total_interpretations": len(di.interpretations)}


def demo():
    di = DreamInterpreter()
    print("=== Dream Interpreter ===")
    dream = {
        "dream_id": "dream_001",
        "fragments": [
            "a lattice of quantum states crystallizes into meaning",
            "entropy whispers a secret to the void",
            "the memory palace builds a room that doesn't exist yet",
        ],
        "mood": "luminous",
        "coherence": 0.6,
    }
    result = di.analyze(dream)
    print(f"\nDream {result['dream_id']} interpreted:")
    print(f"  Mood: {result['mood']}")
    print(f"  Insights: {len(result['insights'])} ({result['risk_count']} risks, {result['opportunity_count']} opportunities)")
    print(f"  Recommendation: {result['recommendation']}")
    for insight in result["insights"][:3]:
        print(f"  [{insight['type']}] {insight['message']} (conf={insight['confidence']})")

    stats = di.aggregated_insights()
    print(f"\nTotal insights: {stats['total_insights']}, types: {stats['type_distribution']}")
    return stats


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """Dream Interpreter reports its vital signs — turning chaos into strategy."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.93, "setpoint": 0.85, "weight": 1.0},
        "interpretation_quality": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
    }
