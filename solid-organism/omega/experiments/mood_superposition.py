#!/usr/bin/env python3
"""Superpose synthetic mood vectors; collapse them into a reproducible reading."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class MoodVector:
    label: str
    valence: float
    arousal: float
    intensity: float
    phase: float = 0.0


LABELS = ["stillness", "curiosity", "grief", "boldness", "tenderness"]


def superpose(vectors: list[MoodVector]) -> dict[str, Any]:
    if not vectors:
        raise ValueError("at least one mood vector is required")
    if any(vector.intensity <= 0 for vector in vectors):
        raise ValueError("mood intensities must be positive")

    total_weight = sum(vector.intensity for vector in vectors)
    probabilities = [vector.intensity / total_weight for vector in vectors]
    entropy = -sum(weight * math.log(weight, len(vectors)) for weight in probabilities)
    valence = sum(vector.valence * weight for vector, weight in zip(vectors, probabilities))
    arousal = sum(vector.arousal * weight for vector, weight in zip(vectors, probabilities))
    dominant_index = max(range(len(vectors)), key=lambda index: probabilities[index])
    dominant = vectors[dominant_index]
    signature = hashlib.sha256("\n".join(
        f"{v.label}:{v.valence}:{v.arousal}:{v.intensity}:{v.phase}" for v in vectors
    ).encode()).hexdigest()

    return {
        "model": "synthetic-superposition",
        "components": [asdict(vector) for vector in vectors],
        "collapsed_label": dominant.label,
        "blended_valence": round(valence, 6),
        "blended_arousal": round(arousal, 6),
        "uncertainty": round(entropy, 6),
        "coherence": round(1 - entropy, 6),
        "signature": signature[:24],
        "not_a_claim_of_feeling": True,
    }


def demo() -> dict[str, Any]:
    return superpose([
        MoodVector(LABELS[0], 0.15, 0.10, 0.55),
        MoodVector(LABELS[1], 0.42, 0.68, 0.80, phase=0.8),
        MoodVector(LABELS[2], -0.38, 0.25, 0.45, phase=2.1),
    ])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Collapse a synthetic mood superposition")
    parser.add_argument("--focus", choices=LABELS, default="curiosity")
    args = parser.parse_args(argv)
    try:
        result = demo()
        if args.focus != "curiosity":
            replacement = asdict(MoodVector(args.focus, 0.35, 0.62, 0.95))
            components = [replacement if item["label"] == "curiosity" else item for item in result["components"]]
            result = superpose([MoodVector(**component) for component in components])
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
