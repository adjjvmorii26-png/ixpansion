from __future__ import annotations
"""Fractal Language — meaning emerges from recursive symbol composition.

A minimal alphabet of 4 base symbols is recursively composed into
increasingly complex meanings. Each composition level adds semantic
depth. The language self-organizes into grammar rules through usage
patterns.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Symbol:
    char: str
    meaning: str = ""
    depth: int = 0
    children: List["Symbol"] = field(default_factory=list)

    def compose(self) -> str:
        if not self.children:
            return self.char
        return "(" + "".join(c.compose() for c in self.children) + ")"

    def semantic_vector(self) -> List[float]:
        if not self.children:
            base_map = {"A": [1,0,0,0], "B": [0,1,0,0], "C": [0,0,1,0], "D": [0,0,0,1]}
            return base_map.get(self.char, [0,0,0,0])
        child_vectors = [c.semantic_vector() for c in self.children]
        result = [0.0] * 4
        for cv in child_vectors:
            for i in range(min(4, len(cv))):
                result[i] += cv[i] / len(child_vectors)
        return result

@dataclass
class GrammarRule:
    pattern: str
    frequency: int = 0
    strength: float = 0.0

class FractalLanguageEngine:
    BASES = ["A", "B", "C", "D"]
    MEANINGS = {
        "A": "existence", "B": "change", "C": "relation", "D": "void"
    }

    def __init__(self, max_depth: int = 5, seed: int = 42):
        self.max_depth = max_depth
        self.vocabulary: Dict[str, Symbol] = {}
        self.grammar_rules: Dict[str, GrammarRule] = {}
        self.composition_count = 0

    def _create_symbol(self, char: str, depth: int = 0) -> Symbol:
        return Symbol(char=char, meaning=self.MEANINGS.get(char, ""), depth=depth)

    def compose(self, parent_char: str, child_chars: List[str], depth: int = 0) -> Symbol:
        if depth >= self.max_depth:
            return self._create_symbol(parent_char, depth)
        parent = self._create_symbol(parent_char, depth)
        parent.children = [self._create_symbol(c, depth + 1) for c in child_chars]
        key = parent.compose()
        self.vocabulary[key] = parent
        self.composition_count += 1

        pattern = f"{parent_char} -> {''.join(child_chars)}"
        if pattern not in self.grammar_rules:
            self.grammar_rules[pattern] = GrammarRule(pattern=pattern)
        self.grammar_rules[pattern].frequency += 1
        self.grammar_rules[pattern].strength = min(1.0,
            self.grammar_rules[pattern].frequency / 10.0)

        return parent

    def generate_sentence(self, length: int = 5) -> str:
        import random
        rng = random.Random(self.composition_count)
        symbols = []
        for _ in range(length):
            char = rng.choice(self.BASES)
            children = [rng.choice(self.BASES) for _ in range(rng.randint(2, 4))]
            sym = self.compose(char, children, depth=0)
            symbols.append(sym.compose())
        return " ".join(symbols)

    def meaning_of(self, expression: str) -> List[float]:
        if expression in self.vocabulary:
            return self.vocabulary[expression].semantic_vector()
        return [0.0] * 4

    def grammar_report(self) -> Dict:
        return {
            "vocabulary_size": len(self.vocabulary),
            "compositions": self.composition_count,
            "grammar_rules": len(self.grammar_rules),
            "top_rules": sorted(
                [{"pattern": r.pattern, "freq": r.frequency,
                  "strength": round(r.strength, 3)}
                 for r in self.grammar_rules.values()],
                key=lambda x: x["freq"], reverse=True
            )[:10],
        }


def demo():
    engine = FractalLanguageEngine(max_depth=3, seed=42)
    print("=== Fractal Language Engine ===")

    compositions = [
        ("A", ["B", "C", "D"]), ("B", ["A", "A", "C"]),
        ("C", ["D", "B", "A"]), ("D", ["A", "B", "B"]),
        ("A", ["A", "B", "C", "D"]), ("B", ["C", "D", "A"]),
    ]
    for parent, children in compositions:
        sym = engine.compose(parent, children)
        print(f"  {parent}({','.join(children)}): {sym.compose()}")

    sentence = engine.generate_sentence(length=4)
    print(f"\nGenerated sentence: {sentence}")

    report = engine.grammar_report()
    print(f"\nVocabulary: {report['vocabulary_size']}")
    print(f"Grammar rules: {report['grammar_rules']}")
    print("Top rules:")
    for rule in report["top_rules"][:5]:
        print(f"  {rule['pattern']}: freq={rule['freq']}, strength={rule['strength']}")

    return report


if __name__ == "__main__":
    demo()
