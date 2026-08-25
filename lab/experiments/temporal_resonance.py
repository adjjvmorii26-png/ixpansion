#!/usr/bin/env python3
"""Temporal Resonance Scanner — detect repeating patterns across event sequences.

Scans a sequence of events (from any source) and detects:
- Recurring motifs (exact subsequences)
- Periodic pulses (events that repeat at regular intervals)
- Resonance peaks (moments where multiple patterns align)

Bridges chronicle logs, mycelium journal events, and entropy signals
to find hidden temporal structure in what looks like noise.
"""
from __future__ import annotations

import hashlib
import json
import math
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Event:
    label: str
    tick: int
    amplitude: float = 1.0
    source: str = "unknown"

    def payload(self) -> dict[str, Any]:
        return {"label": self.label, "tick": self.tick,
                "amplitude": self.amplitude, "source": self.source}


@dataclass(frozen=True)
class Motif:
    """A recurring subsequence."""
    sequence: tuple[str, ...]
    occurrences: list[tuple[int, int]]  # (start_tick, end_tick)
    strength: float
    motif_id: str


@dataclass(frozen=True)
class PeriodicPulse:
    """An event type that repeats at regular intervals."""
    label: str
    period: int
    phase: float
    confidence: float
    occurrences: list[int]


@dataclass(frozen=True)
class ResonancePeak:
    """A tick where multiple patterns align."""
    tick: int
    overlapping_motifs: list[str]
    overlapping_pulses: list[str]
    resonance_strength: float


def _label_hash(labels: tuple[str, ...]) -> str:
    raw = json.dumps(list(labels), separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()[:12]


@dataclass
class ResonanceScanner:
    """Scan event sequences for temporal patterns."""
    min_motif_length: int = 2
    max_motif_length: int = 6
    min_occurrences: int = 2
    period_tolerance: int = 1
    min_pulse_count: int = 3

    def scan(self, events: list[Event]) -> dict[str, Any]:
        if not events:
            return {"motifs": [], "pulses": [], "resonances": [], "summary": {}}

        sorted_events = sorted(events, key=lambda e: e.tick)
        motifs = self._find_motifs(sorted_events)
        pulses = self._find_pulses(sorted_events)
        resonances = self._find_resonances(motifs, pulses)
        summary = self._summarize(sorted_events, motifs, pulses, resonances)

        return {
            "motifs": [self._motif_dict(m) for m in motifs],
            "pulses": [self._pulse_dict(p) for p in pulses],
            "resonances": [self._resonance_dict(r) for r in resonances],
            "summary": summary,
        }

    def _find_motifs(self, events: list[Event]) -> list[Motif]:
        motifs: list[Motif] = []
        for length in range(self.min_motif_length, self.max_motif_length + 1):
            seen: dict[tuple[str, ...], list[int]] = defaultdict(list)
            for i in range(len(events) - length + 1):
                seq = tuple(e.label for e in events[i:i + length])
                seen[seq].append(events[i].tick)

            for seq, ticks in seen.items():
                if len(ticks) < self.min_occurrences:
                    continue
                pairs = [(ticks[i], ticks[-1]) for i in range(len(ticks))]
                occurrences = []
                for start_tick in ticks:
                    occurrences.append((start_tick, start_tick + length - 1))

                # Strength: how regular the spacing is
                if len(ticks) > 1:
                    spacings = [ticks[i + 1] - ticks[i] for i in range(len(ticks) - 1)]
                    mean_spacing = sum(spacings) / len(spacings)
                    if mean_spacing > 0:
                        variance = sum((s - mean_spacing) ** 2 for s in spacings) / len(spacings)
                        regularity = 1.0 / (1.0 + math.sqrt(variance) / mean_spacing)
                    else:
                        regularity = 1.0
                else:
                    regularity = 1.0

                strength = regularity * min(1.0, len(ticks) / 5.0)
                motifs.append(Motif(
                    sequence=seq,
                    occurrences=occurrences[:10],  # cap for display
                    strength=round(strength, 4),
                    motif_id=_label_hash(seq),
                ))

        return sorted(motifs, key=lambda m: (-m.strength, m.motif_id))[:20]

    def _find_pulses(self, events: list[Event]) -> list[PeriodicPulse]:
        label_ticks: dict[str, list[int]] = defaultdict(list)
        for e in events:
            label_ticks[e.label].append(e.tick)

        pulses: list[PeriodicPulse] = []
        for label, ticks in label_ticks.items():
            if len(ticks) < self.min_pulse_count:
                continue

            # Detect dominant period via spacing histogram
            spacings = [ticks[i + 1] - ticks[i] for i in range(len(ticks) - 1)]
            if not spacings:
                continue

            spacing_counts = Counter()
            for s in spacings:
                for candidate in range(max(1, s - self.period_tolerance), s + self.period_tolerance + 1):
                    spacing_counts[candidate] += 1

            if not spacing_counts:
                continue

            best_period, best_count = spacing_counts.most_common(1)[0]
            confidence = best_count / len(spacings) if spacings else 0

            if confidence >= 0.5:
                phase = ticks[0] % best_period if best_period > 0 else 0
                pulses.append(PeriodicPulse(
                    label=label,
                    period=best_period,
                    phase=float(phase),
                    confidence=round(confidence, 4),
                    occurrences=ticks,
                ))

        return sorted(pulses, key=lambda p: (-p.confidence, p.label))

    def _find_resonances(
        self, motifs: list[Motif], pulses: list[PeriodicPulse]
    ) -> list[ResonancePeak]:
        tick_to_motifs: dict[int, list[str]] = defaultdict(list)
        for m in motifs:
            for start, _end in m.occurrences:
                for t in range(start, _end + 1):
                    tick_to_motifs[t].append(m.motif_id)

        tick_to_pulses: dict[int, list[str]] = defaultdict(list)
        for p in pulses:
            for t in p.occurrences:
                tick_to_pulses[t].append(p.label)

        resonances: list[ResonancePeak] = []
        for tick in sorted(set(tick_to_motifs) | set(tick_to_pulses)):
            m_ids = tick_to_motifs.get(tick, [])
            p_ids = tick_to_pulses.get(tick, [])
            if len(m_ids) + len(p_ids) >= 2:
                strength = len(m_ids) * 0.5 + len(p_ids) * 0.3
                resonances.append(ResonancePeak(
                    tick=tick,
                    overlapping_motifs=m_ids,
                    overlapping_pulses=p_ids,
                    resonance_strength=round(strength, 4),
                ))

        return sorted(resonances, key=lambda r: (-r.resonance_strength, r.tick))[:10]

    def _summarize(self, events, motifs, pulses, resonances) -> dict[str, Any]:
        labels = [e.label for e in events]
        return {
            "total_events": len(events),
            "unique_labels": len(set(labels)),
            "tick_range": [events[0].tick, events[-1].tick] if events else [0, 0],
            "motif_count": len(motifs),
            "pulse_count": len(pulses),
            "resonance_count": len(resonances),
            "dominant_label": Counter(labels).most_common(1)[0][0] if labels else "none",
            "temporal_density": len(events) / max(1, events[-1].tick - events[0].tick + 1) if events else 0,
        }

    def _motif_dict(self, m: Motif) -> dict[str, Any]:
        return {
            "motif_id": m.motif_id,
            "sequence": list(m.sequence),
            "occurrences": len(m.occurrences),
            "strength": m.strength,
        }

    def _pulse_dict(self, p: PeriodicPulse) -> dict[str, Any]:
        return {
            "label": p.label,
            "period": p.period,
            "phase": p.phase,
            "confidence": p.confidence,
            "occurrences": len(p.occurrences),
        }

    def _resonance_dict(self, r: ResonancePeak) -> dict[str, Any]:
        return {
            "tick": r.tick,
            "motifs": r.overlapping_motifs,
            "pulses": r.overlapping_pulses,
            "strength": r.resonance_strength,
        }


def demo() -> dict[str, Any]:
    events = []
    tick = 0
    for cycle in range(12):
        events.append(Event(label="pulse", tick=tick, source="heartbeat"))
        events.append(Event(label="signal", tick=tick + 1, source="mycelium"))
        events.append(Event(label="echo", tick=tick + 3, source="constellation"))
        tick += 5

    # Add some noise
    events.append(Event(label="glitch", tick=7, source="chaos"))
    events.append(Event(label="glitch", tick=22, source="chaos"))
    events.append(Event(label="pulse", tick=15, source="heartbeat"))

    scanner = ResonanceScanner()
    return scanner.scan(events)


def main() -> None:
    result = demo()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
