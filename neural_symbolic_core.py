#!/usr/bin/env python3
"""
Hyperdimensional Neural-Symbolic Core
Maps natural language intents <-> VSA hypervectors (SLM-ready interface).
Uses deterministic phrase embedding as local SLM stand-in.
"""
from __future__ import annotations
import re
from typing import Dict, List, Optional
from vsa_memory import VSAMemory, cosine, bundle
from vsa_semantic_router import SemanticRouter

class NeuralSymbolicCore:
    def __init__(self):
        self.vsa = VSAMemory()
        self.router = SemanticRouter()
        self.intent_memory: Dict[str, List[int]] = {}

    def phrase_to_hv(self, text: str) -> List[int]:
        tokens = re.findall(r"[a-z0-9_]+", text.lower())
        parts = [self.vsa.atom(f"tok:{t}") for t in tokens[:24]]
        return bundle(parts) if parts else self.vsa.atom("empty")

    def register_intent(self, name: str, examples: List[str]):
        vecs = [self.phrase_to_hv(e) for e in examples]
        self.intent_memory[name] = bundle(vecs)

    def classify_intent(self, text: str, top_k: int = 3) -> List[dict]:
        q = self.phrase_to_hv(text)
        scored = [(name, cosine(q, vec)) for name, vec in self.intent_memory.items()]
        scored.sort(key=lambda x: -x[1])
        return [{"intent": n, "similarity": round(s, 4)} for n, s in scored[:top_k]]

    def intent_to_task(self, text: str) -> dict:
        hits = self.classify_intent(text, top_k=1)
        intent = hits[0]["intent"] if hits else "search"
        mapping = {
            "simulate": ("ixpansion", "lattice simulation"),
            "research": ("research_search", "research query"),
            "code": ("search", "code search"),
            "evolve": ("tool_generation", "genetic kernel"),
            "publish": ("content_pipeline", "youtube package"),
        }
        cap, desc = mapping.get(intent, ("search", text))
        return {"required_capability": cap, "description": desc or text, "intent": intent, "similarity": hits[0]["similarity"] if hits else 0}

if __name__ == "__main__":
    core = NeuralSymbolicCore()
    core.register_intent("simulate", ["run lattice", "ixpansion simulation", "physics grid energy"])
    core.register_intent("research", ["find papers", "research gossip", "summarize documentation"])
    core.register_intent("evolve", ["mutate kernel", "genetic optimize physics"])
    core.register_intent("publish", ["youtube upload", "content package for channel"])
    print(core.classify_intent("please run the coupled oscillator lattice"))
    print(core.intent_to_task("optimize physics kernel genetically"))
  
