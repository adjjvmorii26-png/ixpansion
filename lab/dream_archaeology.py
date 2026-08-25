"""Dream Archaeology — Excavates patterns from past dream states.

Analyzes the dream journal, finds recurring symbols, and reconstructs
the "dream archaeology" of the system — what has it dreamed about most,
and what patterns keep recurring across dream cycles.
"""
from __future__ import annotations
import hashlib
import random
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DreamArtifact:
    def __init__(self, symbol: str, era: str, frequency: int, mystery_level: float):
        self.symbol = symbol
        self.era = era
        self.frequency = frequency
        self.mystery_level = mystery_level
        self.connections: list[str] = []

    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol, "era": self.era,
            "frequency": self.frequency,
            "mystery": round(self.mystery_level, 3),
            "connections": len(self.connections),
        }


class DreamArchaeologist:
    def __init__(self, seed=42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.artifacts: list[DreamArtifact] = []
        self.eras = ["primordial", "ancient", "classical", "medieval", "modern"]
        self.dig_sites: list[dict] = []

    def excavate(self, dream_count: int = 50):
        symbols = [
            "spiral", "void", "lattice", "crystal", "echo", "flame",
            "shadow", "prism", "vortex", "nexus", "fractal", "wave",
            "node", "field", "pulse", "orbit", "weave", "bloom",
            "tide", "spark", "drift", "bloom", "thread", "silk",
        ]
        emotions = ["wonder", "dread", "calm", "urgency", "recognition", "confusion"]

        for i in range(dream_count):
            era = self.rng.choice(self.eras)
            symbol = self.rng.choice(symbols)
            frequency = self.rng.randint(1, 10)
            mystery = self.rng.random()
            artifact = DreamArtifact(symbol, era, frequency, mystery)
            self.artifacts.append(artifact)

    def find_recurring_symbols(self, min_frequency: int = 3) -> list[dict]:
        symbol_counts = Counter(a.symbol for a in self.artifacts)
        recurring = []
        for symbol, count in symbol_counts.most_common():
            if count >= min_frequency:
                eras = [a.era for a in self.artifacts if a.symbol == symbol]
                recurring.append({
                    "symbol": symbol, "occurrences": count,
                    "eras": list(set(eras)),
                    "avg_mystery": round(
                        sum(a.mystery_level for a in self.artifacts if a.symbol == symbol) /
                        max(1, count), 3
                    ),
                })
        return recurring

    def find_dig_sites(self) -> list[dict]:
        era_counts = Counter(a.era for a in self.artifacts)
        self.dig_sites = []
        for era, count in era_counts.most_common():
            avg_mystery = sum(a.mystery_level for a in self.artifacts if a.era == era) / max(1, count)
            self.dig_sites.append({
                "era": era, "artifacts": count,
                "avg_mystery": round(avg_mystery, 3),
                "significance": "high" if count > 10 else "medium" if count > 5 else "low",
            })
        return self.dig_sites

    def reconstruct_narrative(self) -> str:
        lines = ["═══ DREAM ARCHAEOLOGY REPORT ═══", ""]
        recurring = self.find_recurring_symbols(min_frequency=2)
        lines.append(f"Excavated {len(self.artifacts)} dream artifacts across {len(set(a.era for a in self.artifacts))} eras.")
        lines.append("")
        lines.append("Recurring Symbols:")
        for r in recurring[:5]:
            lines.append(f"  ◆ {r['symbol']}: {r['occurrences']} occurrences across {r['eras']}")
        lines.append("")
        lines.append("Dig Sites:")
        for site in self.find_dig_sites()[:3]:
            lines.append(f"  ⛏ {site['era']}: {site['artifacts']} artifacts, mystery={site['avg_mystery']}")
        return "\n".join(lines)

    def report(self) -> dict:
        recurring = self.find_recurring_symbols()
        sites = self.find_dig_sites()
        narrative = self.reconstruct_narrative()
        return {
            "archaeology": "dream_archaeology",
            "total_artifacts": len(self.artifacts),
            "recurring_symbols": len(recurring),
            "dig_sites": len(sites),
            "top_recurring": recurring[:5],
            "top_sites": sites[:3],
            "narrative": narrative,
        }


def demo():
    arch = DreamArchaeologist(seed=42)
    arch.excavate(dream_count=50)
    return arch.report()


def main():
    import json
    result = demo()
    print(result["narrative"])
    print()
    print(json.dumps({k: v for k, v in result.items() if k != "narrative"}, indent=2))


if __name__ == "__main__":
    main()
