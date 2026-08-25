from __future__ import annotations
"""Neutron Star Core — ultra-dense state compression engine.

Compresses system state into the densest possible representation using
degeneracy pressure principles. If the compressed state exceeds the
Schwarzschild radius equivalent, it collapses into a black hole (data loss).
"""
import math
import hashlib
import json
import struct
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

CHANDRASEKHAR_LIMIT = 1.44
SCHWARZSCHILD_FACTOR = 2.95e-27

@dataclass
class CompressedAtom:
    key: str
    data_hash: str
    original_size: int
    compressed_size: int
    density: float
    degeneracy_pressure: float

    @property
    def compression_ratio(self) -> float:
        if self.original_size == 0:
            return 1.0
        return self.original_size / max(self.compressed_size, 1)

@dataclass
class StellarRemnant:
    name: str
    mass: float
    radius: float
    density: float
    temperature: float
    is_black_hole: bool = False
    atoms: List[CompressedAtom] = field(default_factory=list)

    @property
    def schwarzschild_radius(self) -> float:
        return SCHWARZSCHILD_FACTOR * self.mass

    @property
    def is_unstable(self) -> float:
        return self.mass > CHANDRASEKHAR_LIMIT


class NeutronStarCore:
    def __init__(self, name: str = "core-0"):
        self.name = name
        self.atoms: List[CompressedAtom] = []
        self.total_mass = 0.0
        self.total_original_size = 0
        self.total_compressed_size = 0
        self.collapsed = False

    def _compress_value(self, key: str, value: Any) -> bytes:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        compressed = hashlib.sha256(raw).digest()
        return compressed

    def _calculate_density(self, original: int, compressed: int) -> float:
        if compressed == 0:
            return 0.0
        return original / compressed

    def _degeneracy_pressure(self, density: float) -> float:
        if density < 1.0:
            return 0.0
        return math.log1p(density) / math.log1p(1e15)

    def ingest(self, key: str, value: Any) -> CompressedAtom:
        raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        original_size = len(raw)
        compressed = self._compress_value(key, value)
        compressed_size = len(compressed)
        density = self._calculate_density(original_size, compressed_size)
        pressure = self._degeneracy_pressure(density)

        atom = CompressedAtom(
            key=key,
            data_hash=hashlib.sha256(raw).hexdigest()[:16],
            original_size=original_size,
            compressed_size=compressed_size,
            density=density,
            degeneracy_pressure=pressure,
        )

        self.atoms.append(atom)
        self.total_mass += density / 1e6
        self.total_original_size += original_size
        self.total_compressed_size += compressed_size

        if self.total_mass > CHANDRASEKHAR_LIMIT:
            self.collapsed = True

        return atom

    def stellar_remnant(self) -> StellarRemnant:
        radius = max(1.0, 100.0 / math.sqrt(max(self.total_mass, 0.001)))
        density = self.total_original_size / max(self.total_compressed_size, 1)
        temperature = self.total_mass * 1e9

        return StellarRemnant(
            name=self.name,
            mass=round(self.total_mass, 6),
            radius=round(radius, 4),
            density=round(density, 2),
            temperature=round(temperature, 2),
            is_black_hole=self.collapsed,
            atoms=self.atoms,
        )

    def state_vector(self) -> Dict[str, Any]:
        remnant = self.stellar_remnant()
        return {
            "name": self.name,
            "atom_count": len(self.atoms),
            "total_mass": remnant.mass,
            "radius": remnant.radius,
            "density": remnant.density,
            "temperature": remnant.temperature,
            "is_black_hole": remnant.is_black_hole,
            "schwarzschild_radius": round(remnant.schwarzschild_radius, 10),
            "total_original_bytes": self.total_original_size,
            "total_compressed_bytes": self.total_compressed_size,
            "global_compression": round(
                self.total_original_size / max(self.total_compressed_size, 1), 2
            ),
            "atoms": [
                {"key": a.key, "density": round(a.density, 2),
                 "compression": round(a.compression_ratio, 2)}
                for a in self.atoms
            ],
        }


def demo():
    star = NeutronStarCore("nebula-core")
    print("=== Neutron Star Core ===")
    test_data = [
        ("consciousness_state", {"neurons": 40, "firing_rate": 0.8, "global_workspace": True}),
        ("agent_memory", {"episodes": list(range(100)), "emotional_tags": ["curious", "alert"]}),
        ("world_snapshot", {"entities": [{"id": i, "x": i*0.1, "y": i*0.2} for i in range(50)]}),
        ("protocol_state", {"channels": ["alpha", "delta", "omega"], "messages_sent": 9999}),
        ("hex_bytecode", {"instructions": ["PUSH", "POP", "JMP", "CALL"] * 100, "stack_depth": 50}),
        ("mutation_history", {"generations": list(range(200)), "fitness_curve": [0.1*i for i in range(200)]}),
    ]
    for key, value in test_data:
        atom = star.ingest(key, value)
        print(f"  Ingested '{key}': density={atom.density:.2f}, "
              f"compression={atom.compression_ratio:.1f}x, "
              f"pressure={atom.degeneracy_pressure:.6f}")

    remnant = star.stellar_remnant()
    print(f"\nStellar remnant:")
    print(f"  Mass: {remnant.mass} solar masses")
    print(f"  Radius: {remnant.radius}")
    print(f"  Temperature: {remnant.temperature}K")
    print(f"  Black hole: {remnant.is_black_hole}")
    print(f"  Schwarzschild radius: {remnant.schwarzschild_radius}")

    state = star.state_vector()
    print(f"\n  Global compression: {state['global_compression']}x")

    return state


if __name__ == "__main__":
    demo()
