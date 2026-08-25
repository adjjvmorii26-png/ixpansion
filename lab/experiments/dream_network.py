from __future__ import annotations
import hashlib
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

class DreamNode:
    def __init__(self, agent_id, theme, vividness, seed):
        self.agent_id = agent_id; self.theme = theme; self.vividness = vividness
        self.connections = []; self.seed = seed

class DreamNetwork:
    def __init__(self, seed=42):
        self.seed = seed; self.nodes = []; self.shared_dreams = []
    def add_dream(self, agent_id, theme, vividness=0.5):
        node = DreamNode(agent_id, theme, vividness, self.seed + len(self.nodes))
        self.nodes.append(node)
    def connect_dreams(self):
        for i, a in enumerate(self.nodes):
            for b in self.nodes[i+1:]:
                if a.theme == b.theme:
                    a.connections.append(len(self.nodes))
                    b.connections.append(len(self.nodes))
                    self.shared_dreams.append({"agents": (a.agent_id, b.agent_id), "theme": a.theme})
    def report(self):
        self.connect_dreams()
        themes = {}
        for n in self.nodes: themes[n.theme] = themes.get(n.theme, 0) + 1
        return {"network": "dream_network", "dreams": len(self.nodes),
                "shared": len(self.shared_dreams), "themes": themes,
                "avg_vividness": round(sum(n.vividness for n in self.nodes)/max(1,len(self.nodes)), 3)}

def demo():
    net = DreamNetwork(42)
    agents = ["scout_0", "sentinel_0", "architect_0", "wanderer_0", "scout_1"]
    themes = ["flying", "searching", "building", "dissolving", "expanding", "falling"]
    rng = random.Random(42)
    for _ in range(12):
        net.add_dream(rng.choice(agents), rng.choice(themes), round(rng.random(), 3))
    return net.report()
def main():
    import json; print(json.dumps(demo(), indent=2))
if __name__=="__main__": main()
