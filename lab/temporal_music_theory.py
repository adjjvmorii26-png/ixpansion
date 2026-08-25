"""Temporal Music Theory — Maps code evolution to musical structures.

Translates git history, commit patterns, and code complexity into
musical compositions — finding the rhythm, melody, and harmony of
how the codebase evolves.
"""
from __future__ import annotations
import hashlib
import math
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MusicalNote:
    NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

    def __init__(self, pitch: int, duration: float = 1.0, velocity: float = 0.7):
        self.pitch = pitch % 12
        self.octave = pitch // 12
        self.duration = duration
        self.velocity = velocity

    @property
    def name(self) -> str:
        return f"{self.NOTES[self.pitch]}{self.octave}"

    def frequency(self) -> float:
        return 440.0 * (2 ** ((self.pitch - 9 + self.octave * 12) / 12))

    def to_dict(self) -> dict:
        return {"name": self.name, "freq": round(self.frequency(), 1),
                "duration": round(self.duration, 2), "velocity": round(self.velocity, 2)}


class TemporalComposer:
    def __init__(self, seed=42):
        self.seed = seed
        self.notes: list[MusicalNote] = []
        self.composition: list[dict] = []
        self.chords: list[list[MusicalNote]] = []

    def read_git_rhythm(self) -> list[int]:
        try:
            result = subprocess.run(
                ["git", "log", "--all", "--format=%s", "-100"],
                capture_output=True, text=True, cwd=str(ROOT), timeout=10
            )
            commits = result.stdout.strip().splitlines()
            rhythm = [len(c) % 12 for c in commits if c]
            return rhythm
        except Exception:
            return [0] * 20

    def compose_melody(self, rhythm: list[int]) -> list[MusicalNote]:
        melody = []
        for i, pitch in enumerate(rhythm):
            duration = 0.5 + (i % 3) * 0.25
            velocity = 0.5 + (pitch / 12) * 0.5
            note = MusicalNote(pitch, duration, velocity)
            melody.append(note)
            self.notes.append(note)
        return melody

    def compose_chords(self, melody: list[MusicalNote]) -> list[list[MusicalNote]]:
        self.chords = []
        for i in range(0, len(melody) - 2, 3):
            root = melody[i]
            third = MusicalNote((root.pitch + 4) % 12, root.duration, root.velocity * 0.8)
            fifth = MusicalNote((root.pitch + 7) % 12, root.duration, root.velocity * 0.6)
            self.chords.append([root, third, fifth])
        return self.chords

    def analyze_harmony(self) -> dict:
        if not self.notes:
            return {"consonance": 0, "dissonance": 0}
        intervals = []
        for i in range(len(self.notes) - 1):
            interval = abs(self.notes[i].pitch - self.notes[i+1].pitch) % 12
            intervals.append(interval)
        consonant = sum(1 for i in intervals if i in [0, 3, 4, 7, 8, 9])
        dissonant = sum(1 for i in intervals if i in [1, 2, 5, 6, 10, 11])
        return {
            "consonance": round(consonant / max(1, len(intervals)), 3),
            "dissonance": round(dissonant / max(1, len(intervals)), 3),
            "total_intervals": len(intervals),
        }

    def report(self) -> dict:
        rhythm = self.read_git_rhythm()
        melody = self.compose_melody(rhythm)
        chords = self.compose_chords(melody)
        harmony = self.analyze_harmony()
        return {
            "theory": "temporal_music_theory",
            "notes_composed": len(self.notes),
            "chords_composed": len(self.chords),
            "harmony": harmony,
            "melody_preview": [n.to_dict() for n in melody[:10]],
            "chord_preview": [[n.to_dict() for n in c] for c in chords[:3]],
            "key_signature": self._detect_key(),
        }

    def _detect_key(self) -> str:
        if not self.notes:
            return "unknown"
        pitch_counts = {}
        for n in self.notes:
            pitch_counts[n.pitch] = pitch_counts.get(n.pitch, 0) + 1
        root = max(pitch_counts, key=pitch_counts.get)
        key_names = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
        return f"{key_names[root]} major"


def demo():
    composer = TemporalComposer(seed=42)
    return composer.report()


def main():
    import json
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
