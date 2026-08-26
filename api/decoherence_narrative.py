"""Wave 123 — Decoherence Narrative.

Stories that lose coherence over time, then re-cohere into new forms —
mimicking quantum decoherence where quantum superposition collapses
into classical reality, then re-enters superposition.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Optional


class NarrativeState:
    """The coherence state of a narrative."""

    COHERENCE_LEVELS = ["quantum", "fuzzy", "classical", "decayed", "reborn"]

    def __init__(self, title: str, initial_text: str):
        self.title = title
        self.texts: List[str] = [initial_text]
        self.coherence = 1.0
        self.phase = "quantum"
        self.created = time.time()
        self.decay_count = 0

    def decay(self) -> float:
        self.coherence = max(0.0, self.coherence - 0.2)
        self.decay_count += 1
        if self.coherence <= 0.2:
            self.phase = "decayed"
        elif self.coherence <= 0.5:
            self.phase = "classical"
        elif self.coherence <= 0.8:
            self.phase = "fuzzy"
        return self.coherence

    def rehere(self, new_text: str) -> float:
        self.coherence = min(1.0, self.coherence + 0.4)
        self.texts.append(new_text)
        self.phase = "reborn" if self.decay_count > 0 else "quantum"
        return self.coherence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "coherence": round(self.coherence, 4),
            "phase": self.phase,
            "text_versions": len(self.texts),
            "decay_count": self.decay_count,
        }


class DecoherenceNarrative:
    """Manages narratives that decay and re-cohere."""

    def __init__(self):
        self._narratives: List[NarrativeState] = []
        self._cycle_count = 0

    def begin(self, title: str, text: str) -> NarrativeState:
        narrative = NarrativeState(title, text)
        self._narratives.append(narrative)
        return narrative

    def cycle(self, narrative: NarrativeState, new_text: str) -> Dict[str, Any]:
        narrative.decay()
        narrative.rehere(new_text)
        self._cycle_count += 1
        return {
            "title": narrative.title,
            "coherence": round(narrative.coherence, 4),
            "phase": narrative.phase,
        }

    def full_cycle(self, narrative: NarrativeState, text: str, rounds: int = 3) -> List[Dict[str, Any]]:
        history = []
        for i in range(rounds):
            result = self.cycle(narrative, f"{text}_v{i+1}")
            history.append(result)
        return history

    def status(self) -> Dict[str, Any]:
        return {
            "total_narratives": len(self._narratives),
            "total_cycles": self._cycle_count,
        }
