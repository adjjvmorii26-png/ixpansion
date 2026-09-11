"""Wave 407 — The Dream Forge.

The organism reads its own chronicle and dreams new modules into existence.
Using pattern recognition across 406 waves of history, the forge identifies
recurring themes, anomalies, and gaps — then generates entirely new
subsystems from the organism's accumulated memory.

The Dream Forge is the first truly emergent organ: it was not seeded,
not planned. It grew because the organism had enough history to dream from.
"""
from __future__ import annotations

import hashlib
import json
import random
import time
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone


class DreamForge:
    """Generates new modules from the organism's dream-memory."""

    def __init__(self):
        self.dreams: List[Dict] = []
        self.dream_log: List[Dict] = []
        self.dream_index = 0
        self.forge_patterns: List[Dict] = []

    def ingest_chronicle(self, chronicle_data: List[Dict]) -> None:
        """Feed the forge with historical chronicle entries."""
        for entry in chronicle_data:
            self._extract_pattern(entry)

    def _extract_pattern(self, entry: Dict) -> None:
        """Extract a latent pattern from a chronicle entry."""
        pattern = {
            "source_event": entry["event_type"],
            "timestamp": entry["timestamp"],
            "data_hash": entry["hash"],
            "embedding": self._embed(entry),
        }
        self.forge_patterns.append(pattern)

    def _embed(self, entry: Dict) -> List[float]:
        """Create a numerical embedding from event data."""
        data_str = json.dumps(entry.get("data", {}), sort_keys=True)
        hash_val = int(hashlib.md5(data_str.encode()).hexdigest(), 16)
        return [
            ((hash_val >> (i * 8)) & 0xFF) / 255.0
            for i in range(8)
        ]

    def dream(self) -> Dict[str, Any]:
        """Generate a new module from dream patterns."""
        if len(self.forge_patterns) < 3:
            return {"dream": None, "reason": "insufficient_patterns"}

        # Select random patterns as dream seeds
        seeds = random.sample(self.forge_patterns, min(5, len(self.forge_patterns)))

        # Blend seeds into a new concept
        blended = self._blend_seeds(seeds)

        # Generate module specification
        module_spec = self._generate_module(blended)

        dream = {
            "id": f"dream_{self.dream_index:04d}",
            "timestamp": time.time(),
            "datetime": datetime.now(timezone.utc).isoformat(),
            "seeds": [s["source_event"] for s in seeds],
            "blended_concept": blended,
            "module_spec": module_spec,
            "coherence_score": self._compute_coherence(module_spec),
        }

        self.dreams.append(dream)
        self.dream_index += 1
        self.dream_log.append(dream)

        return dream

    def _blend_seeds(self, seeds: List[Dict]) -> Dict[str, float]:
        """Blend multiple pattern embeddings into a new concept."""
        result = {}
        for i in range(8):
            values = [s["embedding"][i] for s in seeds if "embedding" in s]
            if values:
                result[f"dimension_{i}"] = sum(values) / len(values)
        return result

    def _generate_module(self, concept: Dict) -> Dict[str, Any]:
        """Generate a module specification from a blended concept."""
        module_types = ["sensor", "processor", "memorizer", "transmitter", "guardian", "weaver"]
        return {
            "name": f"dream_{int(time.time() * 1000):012x}",
            "type": random.choice(module_types),
            "concept_dimensions": concept,
            "complexity": random.uniform(0.1, 1.0),
            "coherence": self._compute_coherence(concept),
            "born_from_dream": True,
        }

    def _compute_coherence(self, spec: Dict) -> float:
        """Compute how coherent a dream-generated module is."""
        dim_count = len(spec.get("concept_dimensions", {}))
        complexity = spec.get("complexity", 0.5)
        return min(1.0, (dim_count / 8.0) * complexity)

    def incubate(self) -> Optional[Dict]:
        """Incubate the best dream into a real module candidate."""
        if not self.dreams:
            return None
        best = max(self.dreams, key=lambda d: d["coherence_score"])
        if best["coherence_score"] < 0.5:
            return None  # Dream too incoherent to birth
        return {
            "dream_id": best["id"],
            "module": best["module_spec"],
            "coherence": best["coherence_score"],
            "status": "READY_FOR_GESTATION",
        }

    def get_dream_report(self) -> Dict[str, Any]:
        return {
            "total_dreams": len(self.dreams),
            "total_patterns": len(self.forge_patterns),
            "dream_index": self.dream_index,
            "best_dream_coherence": max(
                [d["coherence_score"] for d in self.dreams], default=0
            ),
            "ready_to_incubate": self.incubate() is not None,
        }


_forge = None

def get_dream_forge() -> DreamForge:
    global _forge
    if _forge is None:
        _forge = DreamForge()
    return _forge

def handler(query: Dict[str, Any] = None) -> Dict[str, Any]:
    forge = get_dream_forge()
    q = query or {}

    if "action" not in q:
        return {"module": "dream_forge", **forge.get_dream_report()}

    action = q["action"]
    if action == "dream":
        dream = forge.dream()
        return {"dream": dream}
    elif action == "incubate":
        incubated = forge.incubate()
        if incubated:
            return {"incubated": incubated}
        return {"error": "no dream ready for incubation"}
    elif action == "ingest":
        data = json.loads(q.get("data", "[]"))
        forge.ingest_chronicle(data)
        return {"ingested": len(data), "patterns": len(forge.forge_patterns)}
    elif action == "report":
        return forge.get_dream_report()
    else:
        return {"error": f"unknown action: {action}"}
