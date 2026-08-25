from __future__ import annotations
"""Urban Legend Engine — code patterns that spread and mutate like legends.

Some code patterns propagate through a codebase like urban legends —
being retold, modified, and distorted as they spread. This module tracks
how code snippets mutate as they're "told" (copied) between modules,
measuring mutation rate, spread velocity, and cultural fitness.
"""
import math
import random
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Legend:
    name: str
    original: str
    current: str
    generation: int = 0
    spread_count: int = 0
    mutation_rate: float = 0.0
    tellers: List[str] = field(default_factory=list)

    def mutate(self, mutation_rate: float = 0.1, rng: random.Random = None) -> str:
        if rng is None:
            rng = random.Random()
        chars = list(self.current)
        mutations = 0
        for i in range(len(chars)):
            if rng.random() < mutation_rate:
                chars[i] = chr(rng.randint(32, 126))
                mutations += 1
        self.current = "".join(chars)
        self.generation += 1
        self.mutation_rate = mutations / max(len(chars), 1)
        return self.current

    def fitness(self) -> float:
        if not self.current:
            return 0.0
        original_set = set(self.original)
        current_set = set(self.current)
        overlap = len(original_set & current_set) / max(len(original_set | current_set), 1)
        return overlap * (1.0 / (1.0 + self.generation * 0.1))

class UrbanLegendEngine:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.legends: Dict[str, Legend] = {}
        self.spread_log: List[Dict] = []

    def create_legend(self, name: str, code: str) -> Legend:
        legend = Legend(name=name, original=code, current=code)
        self.legends[name] = legend
        return legend

    def tell(self, legend_name: str, teller: str, mutation_rate: float = 0.1) -> Optional[Legend]:
        if legend_name not in self.legends:
            return None
        legend = self.legends[legend_name]
        old = legend.current
        legend.mutate(mutation_rate, self.rng)
        legend.spread_count += 1
        legend.tellers.append(teller)
        self.spread_log.append({
            "legend": legend_name, "teller": teller,
            "generation": legend.generation,
            "old": old[:50], "new": legend.current[:50],
            "mutation_rate": round(legend.mutation_rate, 3),
        })
        return legend

    def folklore_report(self) -> Dict:
        return {
            "total_legends": len(self.legends),
            "total_tells": sum(l.spread_count for l in self.legends.values()),
            "avg_generation": sum(l.generation for l in self.legends.values()) / max(len(self.legends), 1),
            "legends": sorted([
                {"name": l.name, "generation": l.generation,
                 "spreads": l.spread_count, "fitness": round(l.fitness(), 3)}
                for l in self.legends.values()
            ], key=lambda x: x["spreads"], reverse=True),
        }


def demo():
    engine = UrbanLegendEngine(seed=42)
    print("=== Urban Legend Engine ===")

    legends_data = [
        ("the_null_check", "if x is not None: do_something(x)"),
        ("the_retry_loop", "for attempt in range(3): try_it()"),
        ("the_config_hack", "config['secret'] = os.environ.get('KEY')"),
        ("the_cache_decorator", "@cache\ndef expensive(): pass"),
    ]
    for name, code in legends_data:
        engine.create_legend(name, code)

    print(f"  Created {len(engine.legends)} urban legends")
    for _ in range(30):
        name = self_name = engine.rng.choice(list(engine.legends.keys()))
        teller = f"module_{engine.rng.randint(0, 5)}"
        engine.tell(name, teller, mutation_rate=0.05)

    report = engine.folklore_report()
    print(f"  Total tells: {report['total_tells']}")
    print(f"  Avg generation: {report['avg_generation']:.1f}")
    print("\nLegend status:")
    for l in report["legends"]:
        print(f"  {l['name']}: gen={l['generation']}, "
              f"spreads={l['spreads']}, fitness={l['fitness']}")

    return report


if __name__ == "__main__":
    demo()
