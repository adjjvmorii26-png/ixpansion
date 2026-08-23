"""Emotional state simulation — the engine's evolving personality."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MoodVector:
    valence: float = 0.0      # negative ↔ positive
    arousal: float = 0.5      # calm ↔ excited
    dominance: float = 0.5    # submissive ↔ dominant
    focus: float = 0.5        # scattered ↔ laser-sharp

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.valence, self.arousal, self.dominance, self.focus)

    @property
    def label(self) -> str:
        if self.valence > 0.3 and self.arousal > 0.6:
            return "ecstatic"
        elif self.valence > 0.3 and self.arousal < 0.3:
            return "serene"
        elif self.valence < -0.3 and self.arousal > 0.6:
            return "furious"
        elif self.valence < -0.3 and self.arousal < 0.3:
            return "melancholic"
        elif self.arousal > 0.7:
            return "agitated"
        elif self.focus < 0.2:
            return "confused"
        elif self.dominance > 0.8:
            return "imperious"
        return "neutral"


class MoodEngine:
    def __init__(self, volatility: float = 0.15) -> None:
        self.mood = MoodVector()
        self.volatility = volatility
        self._history: list[tuple[float, str]] = []
        self._stimulus_responses: list[tuple[callable, tuple[float, float, float, float]]] = []

    def on_stimulus(self, detector: callable, mood_delta: tuple[float, float, float, float]) -> None:
        """Register how the engine reacts to specific stimuli."""
        self._stimulus_responses.append((detector, mood_delta))

    def process(self, event: dict[str, Any]) -> str:
        """Process an event and update mood accordingly."""
        for detector, (dv, da, dd, df) in self._stimulus_responses:
            if detector(event):
                self.mood.valence += dv
                self.mood.arousal += da
                self.mood.dominance += dd
                self.mood.focus += df

        # Natural decay toward baseline
        self.mood.valence *= (1.0 - self.volatility * 0.1)
        self.mood.arousal += (0.5 - self.mood.arousal) * self.volatility * 0.05
        self.mood.focus += (0.5 - self.mood.focus) * self.volatility * 0.03

        # Clamp all values
        self.mood.valence = max(-1.0, min(1.0, self.mood.valence))
        self.mood.arousal = max(0.0, min(1.0, self.mood.arousal))
        self.mood.dominance = max(0.0, min(1.0, self.mood.dominance))
        self.mood.focus = max(0.0, min(1.0, self.mood.focus))

        label = self.mood.label
        self._history.append((event.get("tick", 0), label))
        return label

    @property
    def current_label(self) -> str:
        return self.mood.label

    @property
    def history_labels(self) -> list[str]:
        return [label for _, label in self._history]
