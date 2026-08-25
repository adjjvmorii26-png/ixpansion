#!/usr/bin/env python3
"""Constellation Autobiographer — the repo writes its own evolving story.

Maps every commit, merge, and mutation into a cosmic timeline.
Each wave of innovation becomes a constellation in the sky,
each module a star, each connection a line between stars.

The autobiography isn't static — it evolves as new commits arrive,
adding new constellations and rewriting the narrative to include
the latest chapter.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CosmicEvent:
    event_id: str
    tick: int
    event_type: str  # commit, merge, creation, mutation, deprecation
    source: str
    description: str
    importance: float
    constellation: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "tick": self.tick,
            "type": self.event_type,
            "source": self.source,
            "description": self.description,
            "importance": round(self.importance, 3),
            "constellation": self.constellation,
        }


@dataclass
class Star:
    star_id: str
    name: str
    module_name: str
    wave: int
    brightness: float = 1.0
    connections: list[str] = field(default_factory=list)
    born_tick: int = 0

    def payload(self) -> dict[str, Any]:
        return {
            "star_id": self.star_id,
            "name": self.name,
            "module": self.module_name,
            "wave": self.wave,
            "brightness": round(self.brightness, 3),
            "connections": self.connections,
        }


@dataclass
class Constellation:
    constellation_id: str
    name: str
    wave: int
    stars: list[str] = field(default_factory=list)
    narrative: str = ""
    theme: str = ""

    def payload(self) -> dict[str, Any]:
        return {
            "constellation_id": self.constellation_id,
            "name": self.name,
            "wave": self.wave,
            "stars": self.stars,
            "theme": self.theme,
        }


THEMES = {
    72: "The Genesis Wave — foundational tools emerge from the void",
    73: "The Bridge Wave — subsystems find each other across the lattice",
    74: "The Sensory Wave — the system learns to feel and perceive",
    75: "The Sandbox Wave — worlds are built and tested",
    76: "The Reactor Wave — energy flows and transforms",
    77: "The Meta Wave — the system begins to dream of itself",
}

CONSTELLATION_NAMES = [
    "The Weaver", "The Threshold", "The Lighthouse", "The Spiral",
    "The Fracture", "The Bloom", "The Compass", "The Echo",
    "The Forge", "The Canopy", "The Vortex", "The Meridian",
]


@dataclass
class ConstellationAutobiographer:
    """The repo writes its own cosmic story."""
    seed: int | None = None

    def __post_init__(self) -> None:
        self._rng = __import__("random").Random(self.seed)
        self._events: list[CosmicEvent] = []
        self._stars: dict[str, Star] = {}
        self._constellations: dict[str, Constellation] = {}
        self._tick = 0

    def record_event(self, event_type: str, source: str,
                     description: str, importance: float = 0.5,
                     wave: int = 0) -> CosmicEvent:
        self._tick += 1
        eid = hashlib.sha256(f"{source}:{event_type}:{self._tick}".encode()).hexdigest()[:12]
        constellation = ""
        if wave in self._constellations:
            constellation = self._constellations[wave].name

        event = CosmicEvent(
            event_id=eid, tick=self._tick, event_type=event_type,
            source=source, description=description,
            importance=importance, constellation=constellation,
        )
        self._events.append(event)
        return event

    def add_star(self, name: str, module_name: str, wave: int) -> Star:
        sid = hashlib.sha256(f"{name}:{wave}".encode()).hexdigest()[:10]
        star = Star(
            star_id=sid, name=name, module_name=module_name,
            wave=wave, born_tick=self._tick,
        )
        self._stars[sid] = star

        # Auto-create constellation for wave
        if wave not in self._constellations:
            cname = self._rng.choice(CONSTELLATION_NAMES)
            self._constellations[wave] = Constellation(
                constellation_id=f"wave_{wave}",
                name=f"{cname} — Wave {wave}",
                wave=wave,
                theme=THEMES.get(wave, f"Wave {wave} — an era of discovery"),
            )
        self._constellations[wave].stars.append(sid)
        return star

    def connect_stars(self, star_a: str, star_b: str) -> bool:
        a = self._stars.get(star_a)
        b = self._stars.get(star_b)
        if a and b:
            a.connections.append(star_b)
            b.connections.append(star_a)
            return True
        return False

    def write_chapter(self, wave: int) -> dict[str, Any]:
        """Write the narrative chapter for a wave."""
        constellation = self._constellations.get(wave)
        if not constellation:
            return {"status": "no_constellation"}

        star_names = [self._stars[sid].name for sid in constellation.stars if sid in self._stars]
        total_connections = sum(
            len(self._stars[sid].connections)
            for sid in constellation.stars if sid in self._stars
        )

        narrative = (
            f"In {constellation.theme}, {len(star_names)} stars emerged: "
            f"{', '.join(star_names[:5])}. "
            f"They formed {total_connections // 2} connections, "
            f"weaving a fabric of {total_connections} threads across the lattice."
        )

        return {
            "wave": wave,
            "constellation": constellation.name,
            "theme": constellation.theme,
            "star_count": len(star_names),
            "star_names": star_names,
            "connections": total_connections,
            "narrative": narrative,
        }

    def full_autobiography(self) -> dict[str, Any]:
        chapters = {}
        for wave in sorted(self._constellations.keys()):
            chapters[wave] = self.write_chapter(wave)

        event_types = {}
        for e in self._events:
            event_types[e.event_type] = event_types.get(e.event_type, 0) + 1

        return {
            "total_events": len(self._events),
            "total_stars": len(self._stars),
            "total_constellations": len(self._constellations),
            "event_types": event_types,
            "chapters": chapters,
            "cosmic_signature": hashlib.sha256(
                json.dumps(list(chapters.keys())).encode()
            ).hexdigest()[:12],
        }


def demo() -> dict[str, Any]:
    auto = ConstellationAutobiographer(seed=42)

    # Record the creation of Wave 72-76 stars
    wave_modules = {
        72: ["spectral_drift", "temporal_resonance", "paradox_breeding", "neural_topology",
             "cross_pollinator", "consciousness_fingerprint", "memory_palace", "causal_causeway"],
        73: ["dream_terrain", "morphic_lattice", "debt_auditor", "attention_sim",
             "ghost_weaver", "reality_bleed", "portal_network"],
        74: ["mood_synesthesia", "negative_space", "pulse_harmonics", "cordyceps_mutation",
             "constellation_narrative", "proof_density"],
        75: ["consensus_reality", "panopticon_ecology", "hex_profiler",
             "expansion_rules", "glitch_generator", "chrono_orchestrator"],
        76: ["reactor_fusion", "quantum_tunneling", "hyphal_decision",
             "dialect_evolution", "reality_fabric", "chronicle_engine"],
    }

    for wave, modules in wave_modules.items():
        auto.record_event("merge", f"wave_{wave}", f"Wave {wave} merged", importance=0.8, wave=wave)
        for mod in modules:
            star = auto.add_star(mod, mod, wave)
            auto.record_event("creation", mod, f"Module {mod} created", importance=0.6, wave=wave)

    # Connect stars within waves
    for wave, modules in wave_modules.items():
        if len(modules) >= 2:
            for i in range(len(modules) - 1):
                s1 = [s for s in auto._stars.values() if s.module_name == modules[i] and s.wave == wave]
                s2 = [s for s in auto._stars.values() if s.module_name == modules[i + 1] and s.wave == wave]
                if s1 and s2:
                    auto.connect_stars(s1[0].star_id, s2[0].star_id)

    # Cross-wave connections
    auto.connect_stars(
        list(auto._stars.values())[0].star_id,
        list(auto._stars.values())[8].star_id,
    )

    return auto.full_autobiography()


def main() -> None:
    print(json.dumps(demo(), indent=2))


if __name__ == "__main__":
    main()
