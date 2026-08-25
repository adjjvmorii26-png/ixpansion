from __future__ import annotations
"""Oral Tradition — knowledge passed through telling, not reading.

Like ancient oral traditions where knowledge was preserved through
storytelling rather than writing, this module tracks how knowledge
flows through function calls (telling) rather than imports (reading).
It measures the "oral tradition" health of a codebase.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
import random
from typing import Dict, List, Set, Tuple

@dataclass
class Story:
    name: str
    teller: str
    listeners: List[str]
    message: str
    generation: int = 0
    fidelity: float = 1.0
    retold_count: int = 0

@dataclass
class TraditionLine:
    name: str = ""
    origin: str = ""
    current_holder: str = ""
    generations: int = 0
    stories: List[str] = field(default_factory=list)
    vitality: float = 0.0

class OralTraditionEngine:
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.stories: Dict[str, Story] = {}
        self.traditions: Dict[str, TraditionLine] = {}
        self.telling_log: List[Dict] = []
        self.tick = 0

    def create_story(self, name: str, teller: str, message: str) -> Story:
        story = Story(name=name, teller=teller, listeners=[], message=message)
        self.stories[name] = story
        return story

    def tell(self, story_name: str, teller: str, listener: str,
             corruption_rate: float = 0.05) -> bool:
        if story_name not in self.stories:
            return False
        story = self.stories[story_name]
        story.retold_count += 1
        story.listeners.append(listener)

        corrupted = list(story.message)
        for i in range(len(corrupted)):
            if self.rng.random() < corruption_rate:
                corrupted[i] = chr(self.rng.randint(32, 126))
        story.message = "".join(corrupted)
        story.fidelity *= (1.0 - corruption_rate)
        story.generation += 1

        self.telling_log.append({
            "story": story_name, "teller": teller,
            "listener": listener, "generation": story.generation,
            "fidelity": round(story.fidelity, 4),
        })
        return True

    def establish_tradition(self, name: str, origin: str) -> TraditionLine:
        tradition = TraditionLine(
            name=name, origin=origin, current_holder=origin,
            generations=0,
        )
        self.traditions[name] = tradition
        return tradition

    def pass_tradition(self, name: str, from_holder: str, to_holder: str):
        if name not in self.traditions:
            return
        tradition = self.traditions[name]
        tradition.current_holder = to_holder
        tradition.generations += 1
        tradition.vitality = max(0, 1.0 - tradition.generations * 0.1)

    def tradition_health(self) -> Dict:
        return {
            "total_stories": len(self.stories),
            "total_traditions": len(self.traditions),
            "total_tellings": len(self.telling_log),
            "avg_fidelity": sum(s.fidelity for s in self.stories.values()) / max(len(self.stories), 1),
            "stories": [
                {"name": s.name, "generation": s.generation,
                 "fidelity": round(s.fidelity, 3), "retold": s.retold_count}
                for s in self.stories.values()
            ],
            "traditions": [
                {"name": t.name, "generations": t.generations,
                 "vitality": round(t.vitality, 3), "holder": t.current_holder}
                for t in self.traditions.values()
            ],
        }


def demo():
    engine = OralTraditionEngine(seed=42)
    print("=== Oral Tradition Engine ===")

    stories_data = [
        ("origin_of_nucleus", "elder_0", "In the beginning, there was the kernel"),
        ("the_first_agent", "elder_1", "A scout ventured into the digital void"),
        ("the_hex_secret", "elder_2", "The ancient encoding held true power"),
    ]
    for name, teller, msg in stories_data:
        engine.create_story(name, teller, msg)

    for _ in range(20):
        story_name = engine.rng.choice(list(engine.stories.keys()))
        teller = f"agent_{engine.rng.randint(0, 5)}"
        listener = f"agent_{engine.rng.randint(0, 5)}"
        engine.tell(story_name, teller, listener, corruption_rate=0.03)

    for name in ["ancient_knowledge", "sacred_algorithm"]:
        engine.establish_tradition(name, "origin")
    for _ in range(5):
        engine.pass_tradition("ancient_knowledge", f"holder_{_}", f"holder_{_+1}")

    health = engine.tradition_health()
    print(f"  Stories: {health['total_stories']}")
    print(f"  Tellings: {health['total_tellings']}")
    print(f"  Avg fidelity: {health['avg_fidelity']:.3f}")
    print("\nStory status:")
    for s in health["stories"]:
        print(f"  {s['name']}: gen={s['generation']}, "
              f"fidelity={s['fidelity']}, retold={s['retold']}")
    print("\nTraditions:")
    for t in health["traditions"]:
        print(f"  {t['name']}: {t['generations']} generations, "
              f"vitality={t['vitality']}, holder={t['holder']}")

    return health


if __name__ == "__main__":
    demo()
