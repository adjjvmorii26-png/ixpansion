#!/usr/bin/env python3
"""Constellation Narrative — weave stories from star patterns.

Bridges constellation_dice + constellation_caption + echolalia to
create a narrative generator that reads star positions and edges,
then generates multi-voice stories where each "voice" represents
a different interpretation of the same star pattern.

The narrative isn't fixed — it evolves through echolalia-style
mutation, creating a living mythology for each constellation.
"""
from __future__ import annotations

import hashlib
import json
import math
import random
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Star:
    name: str
    x: int
    y: int
    brightness: float = 1.0


@dataclass(frozen=True)
class Edge:
    from_star: str
    to_star: str
    distance: int


@dataclass
class Constellation:
    name: str
    stars: list[Star]
    edges: list[Edge]
    seed: int = 0

    @property
    def span(self) -> int:
        return sum(e.distance for e in self.edges)

    @property
    def center(self) -> tuple[float, float]:
        if not self.stars:
            return (0.0, 0.0)
        return (
            sum(s.x for s in self.stars) / len(self.stars),
            sum(s.y for s in self.stars) / len(self.stars),
        )

    @property
    def compactness(self) -> float:
        if not self.stars:
            return 0.0
        cx, cy = self.center
        spread = sum(math.dist((s.x, s.y), (cx, cy)) for s in self.stars) / len(self.stars)
        return max(0.0, 1.0 - spread / 10.0)


NOUNS = ["lighthouse", "cathedral", "wound", "threshold", "mirror", "library", "ship", "garden"]
VERBS = ["sings", "remembers", "fractures", "emerges", "dissolves", "calls", "waits", "burns"]
ADJECTIVES = ["ancient", "hollow", "luminous", "forgotten", "recursive", "fractured", "patient"]

VOICE_SHIFTS = {
    "reversed": lambda text: text[::-1],
    "whispered": lambda text: text.lower(),
    "amplified": lambda text: text.upper(),
    "eroded": lambda text: " ".join(text.split()[::2]),
}


@dataclass
class NarrativeWeaver:
    """Generate multi-voice narratives from constellation patterns."""
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = random.Random(self.seed)
        self._narratives: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def weave(self, constellation: Constellation, voices: int = 3) -> dict[str, Any]:
        """Generate a multi-voice narrative for a constellation."""
        rng = self._rng

        # Base narrative from star positions
        base_words = []
        for star in constellation.stars:
            noun = NOUNS[star.x % len(NOUNS)]
            verb = VERBS[star.y % len(VERBS)]
            adj = ADJECTIVES[(star.x + star.y) % len(ADJECTIVES)]
            base_words.append(f"The {adj} {noun} {verb}")

        # Edge-based connections
        connections = []
        for edge in constellation.edges:
            connections.append(
                f"From {edge.from_star} to {edge.to_star}, "
                f"distance {edge.distance} units of silence"
            )

        base_narrative = ". ".join(base_words)
        if connections:
            base_narrative += ". " + ". ".join(connections)

        # Generate voices
        voice_results = []
        voice_names = ["archivist", "dreamer", "dissident", "oracle", "child"]
        for v in range(voices):
            voice_name = voice_names[v % len(voice_names)]
            shift_name = list(VOICE_SHIFTS.keys())[v % len(VOICE_SHIFTS)]
            shift_fn = VOICE_SHIFTS[shift_name]
            voice_text = shift_fn(base_narrative)

            voice_results.append({
                "voice": voice_name,
                "shift": shift_name,
                "text": voice_text,
                "text_hash": hashlib.sha256(voice_text.encode()).hexdigest()[:8],
            })

        # Meta-narrative
        meta = (
            f"Constellation '{constellation.name}' contains {len(constellation.stars)} stars "
            f"and {len(constellation.edges)} edges, spanning {constellation.span} units. "
            f"Its {voices} voices disagree on meaning but agree on shape."
        )

        signature = hashlib.sha256(
            json.dumps([v["text"] for v in voice_results], sort_keys=True).encode()
        ).hexdigest()[:16]

        self._narratives[constellation.name].append({
            "voices": voice_results,
            "meta": meta,
            "signature": signature,
        })

        return {
            "constellation": constellation.name,
            "stars": len(constellation.stars),
            "compactness": round(constellation.compactness, 4),
            "span": constellation.span,
            "meta_narrative": meta,
            "voices": voice_results,
            "narrative_signature": signature,
        }


def demo() -> dict[str, Any]:
    weaver = NarrativeWeaver(seed=42)

    c1 = Constellation(
        name="The Patient Threshold",
        stars=[
            Star("Alpha", 2, 3), Star("Beta", 4, 1), Star("Gamma", 6, 4),
            Star("Delta", 3, 6), Star("Epsilon", 7, 5),
        ],
        edges=[
            Edge("Alpha", "Beta", 3), Edge("Beta", "Gamma", 4),
            Edge("Gamma", "Delta", 4), Edge("Delta", "Epsilon", 5),
        ],
    )

    c2 = Constellation(
        name="Fractured Mirror",
        stars=[
            Star("Alpha", 1, 1), Star("Beta", 3, 2), Star("Gamma", 5, 1),
            Star("Delta", 4, 4),
        ],
        edges=[
            Edge("Alpha", "Beta", 3), Edge("Beta", "Gamma", 3),
            Edge("Gamma", "Delta", 4),
        ],
    )

    return {
        "narratives": [
            weaver.weave(c1, voices=3),
            weaver.weave(c2, voices=3),
        ],
    }


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
