"""Dream Logic Compiler — compiles dream outputs into executable logic.

Takes the chaotic, non-linear outputs from dream_synthesis and
transforms them into structured, executable decision trees.
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


class DreamLogicCompiler:
    def __init__(self):
        self.compilations: List[Dict] = []
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "dream_logic.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            self.compilations = json.loads(path.read_text()).get("compilations", [])

    def _save(self):
        path = ROOT / ".runtime" / "dream_logic.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"compilations": self.compilations[-200:]}, indent=2))

    def compile(self, dream_fragments: List[str], mood: str = "luminous") -> Dict:
        tree = {"type": "root", "mood": mood, "children": []}
        for fragment in dream_fragments:
            node_type = random.choice(["action", "condition", "observation", "synthesis"])
            node = {
                "type": node_type,
                "fragment": fragment[:100],
                "confidence": round(random.uniform(0.3, 0.9), 3),
                "children": [],
            }
            if node_type == "condition":
                node["branches"] = [
                    {"label": "true", "action": random.choice(dream_fragments)[:50]},
                    {"label": "false", "action": "wait"},
                ]
            tree["children"].append(node)
        compilation_id = hashlib.sha256(f"{json.dumps(dream_fragments)}:{time.time()}".encode()).hexdigest()[:10]
        result = {
            "compilation_id": compilation_id,
            "tree": tree,
            "node_count": len(tree["children"]),
            "avg_confidence": round(sum(n["confidence"] for n in tree["children"]) / max(len(tree["children"]), 1), 3),
        }
        self.compilations.append(result)
        self._save()
        return result

    def history(self, limit: int = 10) -> List[Dict]:
        return self.compilations[-limit:]


def handler(request, response):
    dlc = DreamLogicCompiler()
    return {"compilations": len(dlc.compilations)}


def demo():
    dlc = DreamLogicCompiler()
    print("=== Dream Logic Compiler ===")
    fragments = [
        "a lattice of quantum states crystallizes",
        "entropy whispers a secret",
        "the memory palace builds a new room",
        "symbiosis creates a third mind",
    ]
    result = dlc.compile(fragments, "luminous")
    print(f"\nCompiled {result['node_count']} nodes (avg confidence: {result['avg_confidence']})")
    for child in result["tree"]["children"]:
        print(f"  [{child['type']}] {child['fragment'][:50]}... (conf={child['confidence']})")
    return handler({}, {})


if __name__ == "__main__":
    demo()
