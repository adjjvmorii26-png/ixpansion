#!/usr/bin/env python3
"""Mood Synesthesia Engine — cross-sensory mood translation.

Bridges mood_superposition + spectral_drift + emotional_contagion to
create a system where moods cross sensory channels. A "visual" mood
(transparency, luminance) can be translated to "auditory" mood
(volume, pitch, rhythm) or "tactile" mood (pressure, temperature).

This creates a unified sensory language for agent emotional states —
an agent's mood is described not as a number but as a multi-sensory
experience that other agents can perceive through their preferred channel.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SensoryChannel:
    name: str
    dimensions: tuple[str, ...]
    unit: str


VISUAL = SensoryChannel("visual", ("transparency", "luminance", "saturation"), "lux")
AUDITORY = SensoryChannel("auditory", ("volume", "pitch", "rhythm"), "hz")
TACTILE = SensoryChannel("tactile", ("pressure", "temperature", "texture"), "N")
OLFACTORY = SensoryChannel("olfactory", ("intensity", "valence", "complexity"), "ppm")

CHANNELS = {"visual": VISUAL, "auditory": AUDITORY, "tactile": TACTILE, "olfactory": OLFACTORY}


@dataclass(frozen=True)
class MoodVector:
    valence: float
    arousal: float
    label: str = "neutral"


@dataclass(frozen=True)
class SensoryExpression:
    channel: str
    values: dict[str, float]
    source_mood: str
    signature: str

    def payload(self) -> dict[str, Any]:
        return {
            "channel": self.channel,
            "values": {k: round(v, 4) for k, v in self.values.items()},
            "source_mood": self.source_mood,
            "signature": self.signature,
        }


@dataclass
class SynesthesiaEngine:
    """Translate moods across sensory channels."""
    seed: int | None = None

    def __post_init__(self) -> None:
        self._translation_log: list[dict[str, Any]] = []

    def mood_to_channel(self, mood: MoodVector, channel_name: str) -> SensoryExpression:
        """Translate a mood vector into a sensory expression."""
        channel = CHANNELS.get(channel_name)
        if not channel:
            raise ValueError(f"Unknown channel: {channel_name}")

        # Each channel maps valence/arousal to its dimensions differently
        if channel_name == "visual":
            values = {
                "transparency": max(0.0, 0.5 - mood.valence * 0.3),
                "luminance": max(0.0, 0.3 + mood.arousal * 0.6),
                "saturation": max(0.0, min(1.0, abs(mood.valence) * 0.8 + mood.arousal * 0.2)),
            }
        elif channel_name == "auditory":
            values = {
                "volume": max(0.0, mood.arousal * 0.8),
                "pitch": max(0.0, 0.3 + mood.valence * 0.4),
                "rhythm": max(0.0, min(1.0, mood.arousal * 0.5 + 0.3)),
            }
        elif channel_name == "tactile":
            values = {
                "pressure": max(0.0, mood.arousal * 0.7),
                "temperature": max(0.0, 0.3 + mood.valence * 0.4),
                "texture": max(0.0, min(1.0, abs(mood.valence) * 0.6 + 0.2)),
            }
        elif channel_name == "olfactory":
            values = {
                "intensity": max(0.0, mood.arousal * 0.6),
                "valence": max(0.0, min(1.0, (mood.valence + 1) / 2)),
                "complexity": max(0.0, min(1.0, abs(mood.valence) * mood.arousal + 0.1)),
            }
        else:
            values = {d: 0.5 for d in channel.dimensions}

        raw = json.dumps({"mood": mood.label, "channel": channel_name, "values": values},
                         sort_keys=True, separators=(",", ":"))
        sig = hashlib.sha256(raw.encode()).hexdigest()[:12]

        expression = SensoryExpression(
            channel=channel_name,
            values=values,
            source_mood=mood.label,
            signature=sig,
        )

        self._translation_log.append({
            "mood_label": mood.label,
            "channel": channel_name,
            "signature": sig,
        })
        return expression

    def synthesize_full(self, mood: MoodVector) -> dict[str, Any]:
        """Produce a complete multi-sensory expression of a mood."""
        expressions = {}
        for name in CHANNELS:
            expr = self.mood_to_channel(mood, name)
            expressions[name] = expr.payload()
        return {
            "mood": {"label": mood.label, "valence": mood.valence, "arousal": mood.arousal},
            "channels": expressions,
            "synesthesia_signature": hashlib.sha256(
                json.dumps(expressions, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()[:16],
        }

    def cross_channel_correlation(self) -> dict[str, Any]:
        """Analyze how often different channels are used."""
        channel_counts: dict[str, int] = {}
        for entry in self._translation_log:
            ch = entry["channel"]
            channel_counts[ch] = channel_counts.get(ch, 0) + 1
        return {
            "total_translations": len(self._translation_log),
            "channel_usage": channel_counts,
        }


def demo() -> dict[str, Any]:
    engine = SynesthesiaEngine(seed=42)
    moods = [
        MoodVector(valence=0.8, arousal=0.3, label="serenity"),
        MoodVector(valence=-0.6, arousal=0.9, label="panic"),
        MoodVector(valence=0.2, arousal=0.7, label="anticipation"),
        MoodVector(valence=-0.3, arousal=0.1, label="melancholy"),
    ]
    results = [engine.synthesize_full(m) for m in moods]
    return {
        "expressions": results,
        "correlation": engine.cross_channel_correlation(),
    }


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
