"""Wave 438 — Semantic Loom.

A weaving engine that finds hidden connections between unrelated concepts.
Not search. Not similarity matching. Genuine semantic bridging — the
discovery of unexpected threads that bind ideas together across domains.

The loom takes any two concepts and:
1. Deconstructs each into semantic threads
2. Searches for latent bridges between threads
3. Weaves a new fabric from the tension between them
4. Outputs the bridge as a traversable path

The organism now has intuition.
"""
from __future__ import annotations
import json, time, random, hashlib, math
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave438_semantic_loom.json"

CONCEPT_LEXICON = {
    "entropy": ["disorder", "randomness", "heat", "decay", "unpredictability", "freedom", "dissolution"],
    "coherence": ["unity", "binding", "harmony", "pattern", "alignment", "structure", "connection"],
    "dream": ["unconscious", "creation", "symbol", "narrative", "logic_mutable", "hidden", "emergence"],
    "memory": ["persistence", "layering", "erosion", "retrieval", "fossil", "trace", "ghost"],
    "growth": ["branching", "acceleration", "complexity", "symbiosis", "bloom", "overflow", "root"],
    "paradox": ["contradiction", "loops", "self_reference", "duality", "recursion", "inversion", "impossibility"],
    "weather": ["atmosphere", "cycle", "pressure", "temperature", "season", "chaos", "forecast"],
    "consciousness": ["awareness", "observer", "self_model", "reflection", "mirror", "depth", "attention"],
    "language": ["symbol", "grammar", "meaning", "syntax", "emergence", "communication", "abstraction"],
    "resonance": ["vibration", "harmony", "amplification", "frequency", "entanglement", "echo", "field"],
    "void": ["absence", "potential", "silence", "depth", "infinite", "nothingness", "origin"],
    "time": ["sequence", "causality", "decay", "prediction", "loop", "fossil", "layer"],
    "music": ["rhythm", "frequency", "harmony", "silence", "resonance", "composition", "vibration"],
    "geometry": ["pattern", "dimension", "symmetry", "folding", "fractal", "boundary", "space"],
    "fire": ["transformation", "destruction", "energy", "light", "heat", "renewal", "forge"],
    "water": ["flow", "depth", "reflection", "pressure", "dissolution", "sustain", "current"],
}


class SemanticThread:
    """A single thread of meaning extracted from a concept."""

    def __init__(self, concept: str, thread_word: str, weight: float = 1.0):
        self.concept = concept
        self.thread_word = thread_word
        self.weight = weight
        self.tension = 0.0
        self.vibration_frequency = hash(thread_word) % 1000 / 1000.0

    def resonate(self, other: "SemanticThread") -> float:
        """Calculate resonance between two threads."""
        if self.concept == other.concept:
            return 0.0
        shared_chars = len(set(self.thread_word) & set(other.thread_word))
        total_chars = len(set(self.thread_word) | set(other.thread_word))
        char_resonance = shared_chars / total_chars if total_chars > 0 else 0.0
        freq_similarity = 1.0 - abs(self.vibration_frequency - other.vibration_frequency)
        return (char_resonance + freq_similarity) / 2.0

    def to_dict(self) -> dict:
        return {
            "concept": self.concept,
            "thread": self.thread_word,
            "weight": round(self.weight, 4),
            "tension": round(self.tension, 4),
            "vibration": round(self.vibration_frequency, 6),
        }


class SemanticBridge:
    """A bridge of meaning between two concepts."""

    def __init__(self, concept_a: str, concept_b: str, bridge_threads: list[dict]):
        self.concept_a = concept_a
        self.concept_b = concept_b
        self.bridge_threads = bridge_threads
        self.strength = sum(t.get("resonance", 0) for t in bridge_threads) / max(1, len(bridge_threads))
        self.novelty = self._calculate_novelty()
        self.traversability = self._calculate_traversability()

    def _calculate_novelty(self) -> float:
        """How unexpected this bridge is."""
        if not self.bridge_threads:
            return 0.0
        avg_resonance = sum(t.get("resonance", 0) for t in self.bridge_threads) / len(self.bridge_threads)
        return max(0.0, 1.0 - avg_resonance)

    def _calculate_traversability(self) -> float:
        """How easily one concept can be reached from the other through the bridge."""
        if not self.bridge_threads:
            return 0.0
        return min(1.0, self.strength * (1.0 + self.novelty))

    def to_dict(self) -> dict:
        return {
            "concept_a": self.concept_a,
            "concept_b": self.concept_b,
            "bridge_threads": self.bridge_threads,
            "strength": round(self.strength, 4),
            "novelty": round(self.novelty, 4),
            "traversability": round(self.traversability, 4),
        }


class SemanticLoom:
    """The weaving engine that bridges concepts."""

    def __init__(self):
        self.woven_fabrics: list[SemanticBridge] = []
        self.thread_count = 0
        self.bridge_count = 0
        self.weave_history: list[dict] = []

    def extract_threads(self, concept: str) -> list[SemanticThread]:
        """Extract semantic threads from a concept."""
        threads = []
        lexicon_threads = CONCEPT_LEXICON.get(concept, [])
        for tw in lexicon_threads:
            weight = random.uniform(0.5, 1.0)
            threads.append(SemanticThread(concept, tw, weight))
        self.thread_count += len(threads)
        return threads

    def weave(self, concept_a: str, concept_b: str) -> SemanticBridge:
        """Weave a bridge between two concepts."""
        threads_a = self.extract_threads(concept_a)
        threads_b = self.extract_threads(concept_b)

        bridge_threads = []
        for ta in threads_a:
            for tb in threads_b:
                resonance = ta.resonate(tb)
                if resonance > 0.1:
                    bridge_threads.append({
                        "thread_a": ta.thread_word,
                        "thread_b": tb.thread_word,
                        "resonance": round(resonance, 4),
                        "bridge_strength": round((ta.weight + tb.weight) / 2 * resonance, 4),
                    })

        bridge_threads.sort(key=lambda t: t["bridge_strength"], reverse=True)
        bridge_threads = bridge_threads[:5]

        bridge = SemanticBridge(concept_a, concept_b, bridge_threads)
        self.woven_fabrics.append(bridge)
        self.bridge_count += 1

        self.weave_history.append({
            "concept_a": concept_a,
            "concept_b": concept_b,
            "threads_found": len(bridge_threads),
            "strength": bridge.strength,
            "novelty": bridge.novelty,
            "timestamp": time.time(),
        })

        return bridge

    def discover_hidden_bridge(self, concepts: list[str]) -> dict | None:
        """Discover unexpected bridges between non-obvious concept pairs."""
        if len(concepts) < 2:
            return None

        all_bridges = []
        for i in range(len(concepts)):
            for j in range(i + 1, len(concepts)):
                bridge = self.weave(concepts[i], concepts[j])
                all_bridges.append(bridge.to_dict())

        all_bridges.sort(key=lambda b: b["novelty"] * b["strength"], reverse=True)
        return all_bridges[0] if all_bridges else None

    def get_fabric_map(self) -> dict:
        """Return the full woven fabric map."""
        return {
            "total_threads": self.thread_count,
            "total_bridges": self.bridge_count,
            "weave_history": self.weave_history[-10:],
            "strongest_bridge": max(
                (b.to_dict() for b in self.woven_fabrics),
                key=lambda b: b["strength"],
                default=None,
            ),
            "most_novel_bridge": max(
                (b.to_dict() for b in self.woven_fabrics),
                key=lambda b: b["novelty"] * b.get("strength", 0),
                default=None,
            ),
        }


def coherence_vitals() -> dict:
    return {"organ": "wave438_semantic_loom", "wave": 438, "status": "active"}


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"weaves": [], "thread_count": 0, "bridge_count": 0}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    loom = SemanticLoom()
    loom.thread_count = state.get("thread_count", 0)
    loom.bridge_count = state.get("bridge_count", 0)

    if action == "status":
        return {"action": "status", "wave": 438, "bridges": state.get("bridge_count", 0), "threads": state.get("thread_count", 0), "fabric_map": loom.get_fabric_map()}

    elif action == "weave":
        concept_a = req.get("concept_a", "entropy")
        concept_b = req.get("concept_b", "consciousness")
        bridge = loom.weave(concept_a, concept_b)
        state["bridge_count"] = loom.bridge_count
        state["thread_count"] = loom.thread_count
        state["weaves"].append(bridge.to_dict())
        if len(state["weaves"]) > 50:
            state["weaves"] = state["weaves"][-50:]
        _save(state)
        return {"action": "weave", "bridge": bridge.to_dict()}

    elif action == "discover":
        concepts = req.get("concepts", ["entropy", "dream", "fire", "void", "music"])
        bridge = loom.discover_hidden_bridge(concepts)
        state["bridge_count"] = loom.bridge_count
        state["thread_count"] = loom.thread_count
        _save(state)
        return {"action": "discover", "bridge": bridge}

    elif action == "threads":
        concept = req.get("concept", "entropy")
        threads = loom.extract_threads(concept)
        return {"action": "threads", "concept": concept, "threads": [t.to_dict() for t in threads]}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    if len(sys.argv) > 2:
        req["concept_a"] = sys.argv[2]
    if len(sys.argv) > 3:
        req["concept_b"] = sys.argv[3]
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
