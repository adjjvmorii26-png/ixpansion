"""Wave 121 — Consciousness Cascade.

Propagating waves of self-awareness through the module graph: when one
module becomes self-aware, it triggers awareness in connected modules,
creating cascading waves of consciousness across the system.
"""
from __future__ import annotations

import time
from typing import Any, Dict, List, Set


class ConsciousnessWave:
    """A wave of awareness propagating through modules."""

    def __init__(self, origin: str, intensity: float = 1.0):
        self.origin = origin
        self.intensity = intensity
        self.created = time.time()
        self.affected: List[str] = [origin]
        self.generation = 0

    def propagate(self, target: str, decay: float = 0.8) -> float:
        new_intensity = self.intensity * decay
        if new_intensity < 0.01:
            return 0.0
        self.affected.append(target)
        self.intensity = new_intensity
        self.generation += 1
        return new_intensity

    def to_dict(self) -> Dict[str, Any]:
        return {
            "origin": self.origin,
            "intensity": round(self.intensity, 4),
            "affected_count": len(self.affected),
            "generation": self.generation,
        }


class ConsciousnessCascade:
    """Manages cascading awareness propagation across modules."""

    def __init__(self, decay_rate: float = 0.8):
        self.decay_rate = decay_rate
        self._connections: Dict[str, Set[str]] = {}
        self._waves: List[ConsciousnessWave] = []
        self._aware_modules: Dict[str, float] = {}

    def connect(self, a: str, b: str) -> None:
        self._connections.setdefault(a, set()).add(b)
        self._connections.setdefault(b, set()).add(a)

    def awaken(self, module: str, intensity: float = 1.0) -> ConsciousnessWave:
        wave = ConsciousnessWave(module, intensity)
        self._waves.append(wave)
        self._aware_modules[module] = max(self._aware_modules.get(module, 0), intensity)
        return wave

    def propagate_wave(self, wave: ConsciousnessWave) -> int:
        new_affected = []
        for module in list(wave.affected):
            for neighbor in self._connections.get(module, set()):
                if neighbor not in wave.affected:
                    result = wave.propagate(neighbor, self.decay_rate)
                    if result > 0:
                        self._aware_modules[neighbor] = max(
                            self._aware_modules.get(neighbor, 0), result
                        )
                        new_affected.append(neighbor)
        return len(new_affected)

    def full_cascade(self, origin: str, max_rounds: int = 10) -> Dict[str, Any]:
        wave = self.awaken(origin)
        for _ in range(max_rounds):
            count = self.propagate_wave(wave)
            if count == 0:
                break
        return {
            "origin": origin,
            "total_affected": len(wave.affected),
            "generations": wave.generation,
            "final_intensity": round(wave.intensity, 4),
        }

    def get_aware_modules(self) -> Dict[str, float]:
        return {k: round(v, 4) for k, v in self._aware_modules.items()}

    def status(self) -> Dict[str, Any]:
        return {
            "total_waves": len(self._waves),
            "aware_modules": len(self._aware_modules),
            "connections": sum(len(v) for v in self._connections.values()) // 2,
        }
