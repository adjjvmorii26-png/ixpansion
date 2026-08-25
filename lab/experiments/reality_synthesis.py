from __future__ import annotations
"""Reality Synthesis — merges outputs from multiple subsystems into coherent narratives.

Bridges the constellation atlas, mycelium dreams, and lab experiments
into a unified "reality stream" where each subsystem contributes its
perspective to a shared understanding of system state.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

@dataclass
class RealityFragment:
    source_system: str
    fragment_type: str
    content: Dict[str, Any]
    confidence: float = 0.8
    timestamp: int = 0
    resonance_score: float = 0.0

@dataclass
class SynthesizedReality:
    fragments: List[RealityFragment]
    coherence_score: float
    narrative: str
    dominant_theme: str
    contradictions: List[Dict]

class RealitySynthesizer:
    def __init__(self):
        self.fragments: List[RealityFragment] = []
        self.synthesis_count = 0
        self.tick = 0

    def ingest_constellation(self, atlas_data: Dict) -> RealityFragment:
        fragment = RealityFragment(
            source_system="constellation",
            fragment_type="atlas",
            content={"treaties": atlas_data.get("treaties", []),
                     "atlas_hash": atlas_data.get("hash", "")},
            confidence=0.9,
        )
        self.fragments.append(fragment)
        return fragment

    def ingest_mycelium(self, dream_data: Dict) -> RealityFragment:
        fragment = RealityFragment(
            source_system="mycelium",
            fragment_type="dream",
            content={"dream_id": dream_data.get("dream_id", ""),
                     "hypothesis": dream_data.get("hypothesis", ""),
                     "genome": dream_data.get("genome", {})},
            confidence=dream_data.get("confidence", 0.5),
        )
        self.fragments.append(fragment)
        return fragment

    def ingest_experiment(self, experiment_data: Dict) -> RealityFragment:
        fragment = RealityFragment(
            source_system="lab",
            fragment_type="experiment",
            content={"name": experiment_data.get("name", ""),
                     "result": experiment_data.get("result", {}),
                     "metrics": experiment_data.get("metrics", {})},
            confidence=experiment_data.get("confidence", 0.7),
        )
        self.fragments.append(fragment)
        return fragment

    def ingest_bridge(self, bridge_data: Dict) -> RealityFragment:
        fragment = RealityFragment(
            source_system="bridges",
            fragment_type="bridge_event",
            content={"event": bridge_data.get("event", ""),
                     "origin": bridge_data.get("origin", ""),
                     "target": bridge_data.get("target", "")},
            confidence=bridge_data.get("confidence", 0.8),
        )
        self.fragments.append(fragment)
        return fragment

    def _compute_coherence(self) -> float:
        if len(self.fragments) < 2:
            return 1.0
        systems = set(f.source_system for f in self.fragments)
        type_counts = {}
        for f in self.fragments:
            type_counts[f.fragment_type] = type_counts.get(f.fragment_type, 0) + 1
        diversity = len(systems) / 4.0
        balance = 1.0 - (max(type_counts.values()) - min(type_counts.values())) / max(max(type_counts.values()), 1)
        avg_confidence = sum(f.confidence for f in self.fragments) / len(self.fragments)
        return (diversity * 0.3 + balance * 0.3 + avg_confidence * 0.4)

    def _find_contradictions(self) -> List[Dict]:
        contradictions = []
        for i, a in enumerate(self.fragments):
            for b in self.fragments[i + 1:]:
                if a.source_system != b.source_system:
                    if a.fragment_type == b.fragment_type:
                        conf_diff = abs(a.confidence - b.confidence)
                        if conf_diff > 0.3:
                            contradictions.append({
                                "system_a": a.source_system,
                                "system_b": b.source_system,
                                "type": a.fragment_type,
                                "confidence_gap": round(conf_diff, 3),
                            })
        return contradictions

    def _extract_theme(self) -> str:
        all_content = []
        for f in self.fragments:
            all_content.extend(str(v) for v in f.content.values())
        combined = " ".join(all_content)
        themes = {
            "growth": ["grow", "expand", "evolve", "bloom", "spread"],
            "repair": ["fix", "heal", "kintsugi", "restore", "recover"],
            "exploration": ["explore", "discover", "search", "wander", "drift"],
            "connection": ["connect", "bridge", "link", "network", "weave"],
            "mystery": ["dream", "shadow", "paradox", "unknown", "void"],
        }
        scores = {}
        for theme, keywords in themes.items():
            scores[theme] = sum(combined.lower().count(k) for k in keywords)
        return max(scores, key=scores.get) if scores else "emergent"

    def synthesize(self) -> SynthesizedReality:
        self.tick += 1
        self.synthesis_count += 1
        coherence = self._compute_coherence()
        contradictions = self._find_contradictions()
        theme = self._extract_theme()

        sources = set(f.source_system for f in self.fragments)
        narrative_parts = []
        if "constellation" in sources:
            narrative_parts.append("The atlas maps the integration pathways")
        if "mycelium" in sources:
            narrative_parts.append("The dreams suggest hidden connections")
        if "lab" in sources:
            narrative_parts.append("Experiments reveal measurable patterns")
        if "bridges" in sources:
            narrative_parts.append("Bridges carry signals between realities")

        narrative = ". ".join(narrative_parts) + "."
        if not narrative_parts:
            narrative = "The system contemplates its own structure."

        for f in self.fragments:
            f.resonance_score = coherence * f.confidence

        return SynthesizedReality(
            fragments=self.fragments,
            coherence_score=round(coherence, 4),
            narrative=narrative,
            dominant_theme=theme,
            contradictions=contradictions,
        )

    def state(self) -> Dict:
        return {
            "fragments": len(self.fragments),
            "synthesis_count": self.synthesis_count,
            "systems_represented": list(set(f.source_system for f in self.fragments)),
            "avg_confidence": round(
                sum(f.confidence for f in self.fragments) / max(len(self.fragments), 1), 3
            ),
        }


def demo():
    synth = RealitySynthesizer()
    print("=== Reality Synthesizer ===")

    synth.ingest_constellation({
        "treaties": ["alpha_concordance", "beta_treaty"],
        "hash": "abc123",
    })
    synth.ingest_mycelium({
        "dream_id": "dream_001",
        "hypothesis": "The system grows through connected exploration",
        "genome": {"curiosity": 0.8, "stability": 0.6},
        "confidence": 0.75,
    })
    synth.ingest_experiment({
        "name": "photon_memory",
        "result": {"fidelity": 0.85},
        "metrics": {"samples": 256},
        "confidence": 0.8,
    })
    synth.ingest_bridge({
        "event": "resonance_detected",
        "origin": "mycelium",
        "target": "constellation",
        "confidence": 0.9,
    })
    synth.ingest_experiment({
        "name": "coral_reef",
        "result": {"alive": 5, "symbioses": 2},
        "confidence": 0.7,
    })

    reality = synth.synthesize()
    print(f"  Coherence: {reality.coherence_score}")
    print(f"  Theme: {reality.dominant_theme}")
    print(f"  Narrative: {reality.narrative}")
    print(f"  Contradictions: {len(reality.contradictions)}")
    for c in reality.contradictions:
        print(f"    {c['system_a']} vs {c['system_b']}: gap={c['confidence_gap']}")

    state = synth.state()
    print(f"\n  Systems: {state['systems_represented']}")
    print(f"  Avg confidence: {state['avg_confidence']}")

    return state


if __name__ == "__main__":
    demo()
