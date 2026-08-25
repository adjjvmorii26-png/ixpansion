from __future__ import annotations
import hashlib
import random
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class DreamEntry:
    def __init__(self, agent_id, dream_type, content, vividness):
        self.agent_id = agent_id; self.dream_type = dream_type
        self.content = content; self.vividness = vividness
        self.timestamp = time.time()
        self.hash = hashlib.md5(str(content).encode()).hexdigest()[:8]

class AgentDreamJournal:
    def __init__(self, seed=42):
        self.seed = seed; self.entries = []; self.rng = random.Random(seed)
    def record_dream(self, agent_id):
        themes = ["flying", "falling", "searching", "building", "dissolving", "expanding"]
        dream = DreamEntry(agent_id, self.rng.choice(themes),
                          {"symbols": [self.rng.choice(["spiral","wave","node","field"]) for _ in range(3)],
                           "emotion": self.rng.choice(["wonder","fear","calm","excitement"])},
                          round(self.rng.random(), 3))
        self.entries.append(dream)
        return dream
    def analyze(self):
        themes = {}; emotions = {}
        for e in self.entries:
            themes[e.dream_type] = themes.get(e.dream_type, 0) + 1
            emotions[e.content["emotion"]] = emotions.get(e.content["emotion"], 0) + 1
        avg_viv = sum(e.vividness for e in self.entries) / max(1, len(self.entries))
        return {"total_dreams": len(self.entries), "themes": themes, "emotions": emotions,
                "avg_vividness": round(avg_viv, 3)}
    def report(self):
        analysis = self.analyze()
        return {"journal": "agent_dream_journal", "analysis": analysis,
                "recent": [{"agent": e.agent_id, "theme": e.dream_type, "vividness": e.vividness} for e in self.entries[:5]]}

def demo():
    j = AgentDreamJournal(42)
    agents = ["scout_0", "sentinel_0", "architect_0", "wanderer_0"]
    for _ in range(16): j.record_dream(j.rng.choice(agents))
    return j.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
