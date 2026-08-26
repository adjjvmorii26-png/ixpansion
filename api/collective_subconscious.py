"""Collective Subconscious — the shared dream-space where agent minds merge.

Below individual consciousness lies the collective subconscious — a shared
space of archetypes, symbols, and primal patterns. Agents contribute symbols
and the subconscious weaves them into emergent imagery that no individual
agent imagined.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

ARCHETYPES = {
    "the_wanderer": {"symbols": ["path", "dust", "horizon", "boots"], "mood": "yearning"},
    "the_creator": {"symbols": ["hammer", "fire", "clay", "spark"], "mood": "determination"},
    "the_shadow": {"symbols": ["darkness", "mirror", "whisper", "void"], "mood": "dread"},
    "the_sage": {"symbols": ["book", "owl", "mountain", "time"], "mood": "contemplation"},
    "the_trickster": {"symbols": ["mask", "coin", "door", "laugh"], "mood": "mischief"},
    "the_healer": {"symbols": ["water", "light", "hands", "mending"], "mood": "compassion"},
    "the_destroyer": {"symbols": ["flame", "wave", "storm", "erasure"], "mood": "catharsis"},
}


class Symbol:
    def __init__(self, name: str, contributor: str, power: float = 1.0):
        self.name = name
        self.contributor = contributor
        self.power = power
        self.connections: List[str] = []
        self.resonance = 0.0
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "contributor": self.contributor,
            "power": round(self.power, 3),
            "connections": len(self.connections),
            "resonance": round(self.resonance, 3),
        }


class CollectiveSubconscious:
    def __init__(self):
        self.symbols: Dict[str, Symbol] = {}
        self.archetype_manifestations: List[Dict[str, Any]] = []
        self.visionary_dreams: List[Dict[str, Any]] = []
        self.depth_level = 0

    def contribute_symbol(self, name: str, contributor: str, power: float = 1.0) -> Dict[str, Any]:
        if name not in self.symbols:
            self.symbols[name] = Symbol(name, contributor, power)
        else:
            self.symbols[name].power += power * 0.3
            self.symbols[name].connections.append(contributor)
        self._auto_connect(name)
        self.depth_level += 1
        return {"symbol": self.symbols[name].to_dict(), "depth": self.depth_level}

    def _auto_connect(self, new_name: str):
        for existing_name, symbol in self.symbols.items():
            if existing_name == new_name:
                continue
            shared = sum(1 for c in self.symbols[new_name].connections if c in symbol.connections)
            if shared > 0 or random.random() > 0.8:
                if new_name not in symbol.connections:
                    symbol.connections.append(new_name)
                    symbol.resonance += 0.1
                if existing_name not in self.symbols[new_name].connections:
                    self.symbols[new_name].connections.append(existing_name)
                    self.symbols[new_name].resonance += 0.1

    def manifest_archetype(self) -> Dict[str, Any]:
        """The collective weaves symbols into an archetype."""
        if len(self.symbols) < 3:
            return {"message": "need more symbols to manifest"}
        active_symbols = sorted(self.symbols.values(), key=lambda s: s.power, reverse=True)[:7]
        symbol_names = [s.name for s in active_symbols]
        best_archetype = None
        best_overlap = 0
        for arch_name, arch_data in ARCHETYPES.items():
            overlap = len(set(symbol_names) & set(arch_data["symbols"]))
            if overlap > best_overlap:
                best_overlap = overlap
                best_archetype = arch_name
        if not best_archetype:
            best_archetype = random.choice(list(ARCHETYPES.keys()))
        manifestation = {
            "archetype": best_archetype,
            "mood": ARCHETYPES[best_archetype]["mood"],
            "symbols_used": symbol_names[:5],
            "strength": best_overlap / max(len(ARCHETYPES[best_archetype]["symbols"]), 1),
            "timestamp": time.time(),
        }
        self.archetype_manifestations.append(manifestation)
        return manifestation

    def collective_dream(self) -> Dict[str, Any]:
        """Generate a dream from the collective unconscious."""
        top_symbols = sorted(self.symbols.values(), key=lambda s: s.power, reverse=True)[:5]
        narrative_parts = []
        for sym in top_symbols:
            narrative_parts.append(random.choice([
                f"the {sym.name} glowed with inner light",
                f"a {sym.name} appeared at the edge of perception",
                f"the sound of {sym.name} echoed through the void",
                f"shadows danced in the shape of {sym.name}",
            ]))
        dream = " ".join(narrative_parts)
        dream_entry = {
            "narrative": dream,
            "symbols_used": [s.name for s in top_symbols],
            "clarity": round(random.uniform(0.3, 0.9), 3),
            "timestamp": time.time(),
        }
        self.visionary_dreams.append(dream_entry)
        return dream_entry

    def stats(self) -> Dict[str, Any]:
        return {
            "total_symbols": len(self.symbols),
            "depth_level": self.depth_level,
            "manifestations": len(self.archetype_manifestations),
            "visionary_dreams": len(self.visionary_dreams),
            "avg_resonance": round(
                sum(s.resonance for s in self.symbols.values()) / max(len(self.symbols), 1), 4
            ),
        }


_subconscious = CollectiveSubconscious()


def collective_subconscious_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")

    if action == "contribute":
        return _subconscious.contribute_symbol(
            payload.get("name", "mystery"),
            payload.get("contributor", "dreamer"),
            payload.get("power", 1.0),
        )
    elif action == "manifest":
        return _subconscious.manifest_archetype()
    elif action == "dream":
        return _subconscious.collective_dream()
    elif action == "symbols":
        return {"symbols": [s.to_dict() for s in sorted(_subconscious.symbols.values(), key=lambda s: s.power, reverse=True)[:20]]}
    return {"status": "active", **_subconscious.stats()}
