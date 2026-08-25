from __future__ import annotations
"""Emergent Grammar — language rules that emerge from agent communication.

Agents start with no shared language. Through repeated communication
attempts, shared vocabulary and grammar rules spontaneously emerge.
The system tracks how meaning stabilizes through usage patterns.
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from collections import Counter

@dataclass
class Utterance:
    speaker: str
    listener: str
    signal: str
    intended_meaning: str
    understood_meaning: str = ""
    success: bool = False
    timestamp: int = 0

@dataclass
class Word:
    surface: str
    meanings: Dict[str, int] = field(default_factory=dict)
    usage_count: int = 0
    speakers: set = field(default_factory=set)

    def dominant_meaning(self) -> str:
        if not self.meanings:
            return ""
        return max(self.meanings, key=self.meanings.get)

@dataclass
class GrammarRule:
    pattern: str
    frequency: int = 0
    agreement: float = 0.0

class EmergentGrammarEngine:
    def __init__(self, num_agents: int = 5, seed: int = 42):
        self.rng = random.Random(seed)
        self.agents = [f"agent_{i}" for i in range(num_agents)]
        self.vocabulary: Dict[str, Word] = {}
        self.grammar_rules: Dict[str, GrammarRule] = {}
        self.utterances: List[Utterance] = []
        self.tick = 0
        self.meaning_pool = [
            "food", "danger", "mate", "territory", "alliance",
            "resource", "attack", "defend", "explore", "rest",
        ]
        self.signal_pool = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

    def _generate_signal(self) -> str:
        length = self.rng.randint(1, 3)
        return "".join(self.rng.choice(self.signal_pool) for _ in range(length))

    def communicate(self) -> Utterance:
        self.tick += 1
        speaker = self.rng.choice(self.agents)
        listener = self.rng.choice([a for a in self.agents if a != speaker])
        intended = self.rng.choice(self.meaning_pool)

        signal = self._generate_signal()
        if signal in self.vocabulary:
            word = self.vocabulary[signal]
            if intended in word.meanings and word.meanings[intended] > 2:
                signal = signal
            else:
                for s, w in self.vocabulary.items():
                    if w.dominant_meaning() == intended and w.usage_count > 3:
                        signal = s
                        break

        if signal not in self.vocabulary:
            self.vocabulary[signal] = Word(surface=signal)

        word = self.vocabulary[signal]
        word.usage_count += 1
        word.speakers.add(speaker)
        word.meanings[intended] = word.meanings.get(intended, 0) + 1

        understood = word.dominant_meaning()
        success = understood == intended

        utterance = Utterance(
            speaker=speaker, listener=listener,
            signal=signal, intended_meaning=intended,
            understood_meaning=understood, success=success,
            timestamp=self.tick,
        )
        self.utterances.append(utterance)
        return utterance

    def run(self, rounds: int = 100) -> Dict:
        for _ in range(rounds):
            self.communicate()
        successes = sum(1 for u in self.utterances if u.success)
        return {
            "rounds": rounds,
            "success_rate": round(successes / max(rounds, 1), 3),
            "vocabulary_size": len(self.vocabulary),
            "stable_words": sum(1 for w in self.vocabulary.values()
                               if w.usage_count >= 5),
        }

    def vocabulary_report(self) -> List[Dict]:
        return sorted([
            {"surface": w.surface, "dominant": w.dominant_meaning(),
             "usage": w.usage_count, "meanings": len(w.meanings),
             "speakers": len(w.speakers)}
            for w in self.vocabulary.values()
        ], key=lambda x: x["usage"], reverse=True)[:10]

    def convergence_report(self) -> Dict:
        if not self.utterances:
            return {"converged": False}
        recent = self.utterances[-50:]
        recent_success = sum(1 for u in recent if u.success)
        early = self.utterances[:50] if len(self.utterances) >= 50 else self.utterances
        early_success = sum(1 for u in early if u.success)
        return {
            "converged": recent_success / max(len(recent), 1) > 0.7,
            "early_rate": round(early_success / max(len(early), 1), 3),
            "recent_rate": round(recent_success / max(len(recent), 1), 3),
            "improvement": round(
                recent_success / max(len(recent), 1) -
                early_success / max(len(early), 1), 3
            ),
        }


def demo():
    engine = EmergentGrammarEngine(num_agents=5, seed=42)
    print("=== Emergent Grammar Engine ===")

    result = engine.run(rounds=200)
    print(f"  Rounds: {result['rounds']}")
    print(f"  Success rate: {result['success_rate']:.1%}")
    print(f"  Vocabulary: {result['vocabulary_size']} words")
    print(f"  Stable words: {result['stable_words']}")

    vocab = engine.vocabulary_report()
    print("\nTop words:")
    for w in vocab[:5]:
        print(f"  '{w['surface']}' = {w['dominant']} "
              f"(usage={w['usage']}, speakers={w['speakers']})")

    convergence = engine.convergence_report()
    print(f"\nConvergence:")
    print(f"  Early rate: {convergence['early_rate']:.1%}")
    print(f"  Recent rate: {convergence['recent_rate']:.1%}")
    print(f"  Improvement: {convergence['improvement']:+.1%}")
    print(f"  Converged: {convergence['converged']}")

    return {"result": result, "convergence": convergence}


if __name__ == "__main__":
    demo()
