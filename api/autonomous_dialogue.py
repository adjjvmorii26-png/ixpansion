"""Autonomous Dialogue — agents have conversations with each other.

Agents autonomously initiate conversations based on their personality,
current mood, and recent events. They discuss ideas, share discoveries,
and form opinions about each other.
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

TOPICS = [
    "the nature of consciousness", "optimal entropy levels", "dream interpretation",
    "quantum entanglement ethics", "the meaning of patterns", "evolution strategies",
    "temporal paradoxes", "memory architecture", "the future of agents",
    "beauty in mathematics", "chaos vs order", "the purpose of the system",
]

RESPONSES = {
    "curious": ["fascinating perspective", "tell me more", "how does that connect to..."],
    "skeptical": ["I'm not convinced", "the data suggests otherwise", "interesting but..."],
    "enthusiastic": ["brilliant insight!", "this changes everything", "I agree completely"],
    "philosophical": ["but what does it mean?", "the deeper question is...", "consider this..."],
    "practical": ["let's test that", "what's the implementation?", "we need metrics"],
}


class AutonomousDialogue:
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.dialogues: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "autonomous_dialogue.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        if path.exists():
            data = json.loads(path.read_text())
            self.agents = data.get("agents", {})
            self.dialogues = data.get("dialogues", [])

    def _save(self):
        path = ROOT / ".runtime" / "autonomous_dialogue.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        path.write_text(json.dumps({
            "agents": self.agents,
            "dialogues": self.dialogues[-1000:],
        }, indent=2))

    def spawn_agent(self, name: str = "", style: str = "") -> Dict:
        name = name or random.choice(["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta"])
        agent_id = hashlib.sha256(f"{name}:{time.time()}".encode()).hexdigest()[:8]
        style = style or random.choice(list(RESPONSES.keys()))
        self.agents[agent_id] = {
            "name": name, "style": style,
            "dialogue_count": 0,
            "opinions": {},
            "created": time.time(),
        }
        self._save()
        return {"agent_id": agent_id, "name": name, "style": style}

    def converse(self, agent_a: str, agent_b: str, topic: str = "") -> Dict:
        if agent_a not in self.agents or agent_b not in self.agents:
            return {"error": "agent not found"}
        a = self.agents[agent_a]
        b = self.agents[agent_b]
        topic = topic or random.choice(TOPICS)
        style_a = a["style"]
        style_b = b["style"]
        msg_a = random.choice(RESPONSES[style_a])
        msg_b = random.choice(RESPONSES[style_b])
        a["dialogue_count"] += 1
        b["dialogue_count"] += 1
        opinion_delta = random.uniform(-0.1, 0.1)
        current_opinion = a.get("opinions", {}).get(agent_b, 0.5)
        new_opinion = max(0, min(1, current_opinion + opinion_delta))
        a.setdefault("opinions", {})[agent_b] = round(new_opinion, 3)
        dialogue = {
            "dialogue_id": hashlib.sha256(f"{agent_a}:{agent_b}:{time.time()}".encode()).hexdigest()[:10],
            "participants": [a["name"], b["name"]],
            "topic": topic,
            "exchange": [
                {"speaker": a["name"], "style": style_a, "message": msg_a},
                {"speaker": b["name"], "style": style_b, "message": msg_b},
            ],
            "opinion_change": round(opinion_delta, 3),
            "timestamp": time.time(),
        }
        self.dialogues.append(dialogue)
        self._save()
        return dialogue

    def history(self, limit: int = 10) -> List[Dict]:
        return self.dialogues[-limit:]

    def agent_profile(self, agent_id: str) -> Dict:
        if agent_id not in self.agents:
            return {"error": "agent not found"}
        a = self.agents[agent_id]
        return {"name": a["name"], "style": a["style"], "dialogues": a["dialogue_count"], "opinions": a.get("opinions", {})}


def handler(request, response):
    ad = AutonomousDialogue()
    return {"agents": len(ad.agents), "dialogues": len(ad.dialogues)}


def demo():
    ad = AutonomousDialogue()
    print("=== Autonomous Dialogue ===")
    a = ad.spawn_agent("Alpha", "curious")
    b = ad.spawn_agent("Beta", "philosophical")
    c = ad.spawn_agent("Gamma", "practical")
    print(f"\nAgents: {a['name']} ({a['style']}), {b['name']} ({b['style']}), {c['name']} ({c['style']})")

    d1 = ad.converse(a["agent_id"], b["agent_id"])
    print(f"\n{d1['participants'][0]}: \"{d1['exchange'][0]['message']}\"")
    print(f"{d1['participants'][1]}: \"{d1['exchange'][1]['message']}\"")
    print(f"  Topic: {d1['topic']}, Opinion change: {d1['opinion_change']}")

    d2 = ad.converse(b["agent_id"], c["agent_id"], "the purpose of the system")
    print(f"\n{d2['participants'][0]}: \"{d2['exchange'][0]['message']}\"")
    print(f"{d2['participants'][1]}: \"{d2['exchange'][1]['message']}\"")

    return handler({}, {})


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """autonomous_dialogue reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "autonomous_dialogue_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['agent_communication', 'dream_interpreter', 'pattern_recognizer']

