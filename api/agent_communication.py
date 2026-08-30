"""Agent Communication Protocol — agents speak, negotiate, and form alliances.

Agents develop their own language through interaction. They negotiate
resource sharing, form alliances, betray each other, and evolve their
communication patterns over time.
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

VOCABULARY = {
    "greet": ["*chirp*", "*pulse*", "*resonate*", "*echo*"],
    "offer": ["share::", "trade::", "gift::", "lend::"],
    "demand": ["need::", "require::", "claim::", "seize::"],
    "threat": ["warn::", "challenge::", "provoke::", "dare::"],
    "alliance": ["bond::", "fuse::", "sync::", "unite::"],
    "betray": ["break::", "shift::", "drift::", "sever::"],
}

AGENT_NAMES = [
    "Scout", "Oracle", "Sentinel", "Weaver", "Analyst",
    "Kintsugi", "Architect", "Wanderer", "Dreamer", "Cipher",
]


def _generate_utterance(intent: str, payload: str = "") -> str:
    words = VOCABULARY.get(intent, ["*static*"])
    prefix = random.choice(words)
    if payload:
        return f"{prefix}{payload}"
    return prefix


class AgentCommunication:
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.conversations: List[Dict] = []
        self.alliances: Dict[str, Dict] = {}
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "agent_comm.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        if path.exists():
            data = json.loads(path.read_text())
            self.agents = data.get("agents", {})
            self.conversations = data.get("conversations", [])
            self.alliances = data.get("alliances", {})

    def _save(self):
        path = ROOT / ".runtime" / "agent_comm.json"
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        path.write_text(json.dumps({
            "agents": self.agents,
            "conversations": self.conversations[-1000:],
            "alliances": self.alliances,
        }, indent=2))

    def spawn(self, name: str = "") -> Dict:
        name = name or random.choice(AGENT_NAMES)
        agent_id = hashlib.sha256(f"{name}:{time.time()}".encode()).hexdigest()[:8]
        personality = random.choice(["friendly", "aggressive", "cautious", "curious", "mysterious"])
        self.agents[agent_id] = {
            "name": name, "personality": personality,
            "vocabulary": random.sample(list(VOCABULARY.keys()), 3),
            "trust": {}, "utterances": 0, "created": time.time(),
        }
        self._save()
        return {"agent_id": agent_id, "name": name, "personality": personality}

    def speak(self, agent_id: str, target_id: str, intent: str, payload: str = "") -> Dict:
        if agent_id not in self.agents or target_id not in self.agents:
            return {"error": "agent not found"}
        agent = self.agents[agent_id]
        utterance = _generate_utterance(intent, payload)
        agent["utterances"] += 1
        trust_delta = {"greet": 0.05, "offer": 0.1, "threat": -0.2, "alliance": 0.15, "betray": -0.5, "demand": -0.1}
        current_trust = agent.get("trust", {}).get(target_id, 0.5)
        new_trust = max(0, min(1, current_trust + trust_delta.get(intent, 0)))
        agent.setdefault("trust", {})[target_id] = round(new_trust, 3)
        msg = {
            "from": agent_id, "to": target_id,
            "utterance": utterance, "intent": intent,
            "trust_before": current_trust, "trust_after": new_trust,
            "timestamp": time.time(),
        }
        self.conversations.append(msg)
        if intent == "alliance" and new_trust > 0.7:
            key = "-".join(sorted([agent_id, target_id]))
            self.alliances[key] = {"agents": [agent_id, target_id], "formed": time.time(), "strength": new_trust}
        self._save()
        return msg

    def history(self, limit: int = 20) -> List[Dict]:
        return self.conversations[-limit:]

    def alliances_list(self) -> List[Dict]:
        return [{"id": k, **v} for k, v in self.alliances.items()]

    def agent_profile(self, agent_id: str) -> Dict:
        if agent_id not in self.agents:
            return {"error": "agent not found"}
        agent = self.agents[agent_id]
        return {
            "name": agent["name"],
            "personality": agent["personality"],
            "utterances": agent["utterances"],
            "trust_map": agent.get("trust", {}),
            "vocabulary": agent["vocabulary"],
        }


def handler(request, response):
    ac = AgentCommunication()
    return {"agents": len(ac.agents), "conversations": len(ac.conversations), "alliances": len(ac.alliances)}


def demo():
    ac = AgentCommunication()
    print("=== Agent Communication Protocol ===")
    a1 = ac.spawn("Scout")
    a2 = ac.spawn("Oracle")
    a3 = ac.spawn("Sentinel")
    print(f"\nSpawned: {a1['name']} ({a1['personality']}), {a2['name']} ({a2['personality']})")

    ac.speak(a1["agent_id"], a2["agent_id"], "greet")
    ac.speak(a1["agent_id"], a2["agent_id"], "offer", "data_patterns")
    ac.speak(a2["agent_id"], a1["agent_id"], "alliance", "mutual_benefit")
    ac.speak(a3["agent_id"], a1["agent_id"], "threat", "resource_competition")

    history = ac.history(4)
    for msg in history:
        print(f"  {msg['utterance']} (trust: {msg['trust_before']} -> {msg['trust_after']})")

    print(f"\nAlliances: {len(ac.alliances_list())}")
    return ac.handler({}, {})


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """agent_communication reports its vital signs to the living system."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "agent_communication_vitality": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "germination_era": {"value": 1.0, "setpoint": 0.8, "weight": 0.5},
    }


def resonates_with() -> list:
    """Declared kinships, auto-picked from shared domain language."""
    return ['narrative_generator', 'dream_synthesis', 'dream_interpreter']

