"""Wave 129 — Meaning Furnace.

Burns raw data to extract pure meaning — a thermal process where
noise is burned away and only the essential semantic signal remains.
The hotter the furnace, the purer the extracted meaning.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List


class MeaningExtract:
    """A batch of meaning extracted from raw data."""

    def __init__(self, raw_data: str, temperature: float = 100.0):
        self.raw_data = raw_data
        self.temperature = temperature
        self.pure_meaning: str = ""
        self.noise_removed = 0.0
        self.created = time.time()
        self.id = hashlib.sha256(f"extract:{raw_data[:20]}".encode()).hexdigest()[:10]

    def burn(self) -> Dict[str, Any]:
        self.pure_meaning = f"PURIFIED({self.raw_data[:30]})"
        self.noise_removed = min(1.0, self.temperature / 1000.0)
        return {"input_length": len(self.raw_data),
                "noise_removed": round(self.noise_removed, 4),
                "temperature": self.temperature}

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "temperature": self.temperature,
                "noise_removed": round(self.noise_removed, 4),
                "meaning": self.pure_meaning[:50] if self.pure_meaning else ""}


class MeaningFurnace:
    """Burns raw data to extract pure meaning."""

    def __init__(self, temperature: float = 100.0):
        self.temperature = temperature
        self._extracts: List[MeaningExtract] = []
        self._total_burned = 0

    def burn(self, raw_data: str) -> MeaningExtract:
        extract = MeaningExtract(raw_data, self.temperature)
        extract.burn()
        self._extracts.append(extract)
        self._total_burned += len(raw_data)
        return extract

    def temperature_up(self, amount: float = 50.0) -> float:
        self.temperature += amount
        return self.temperature

    def status(self) -> Dict[str, Any]:
        avg_noise = sum(e.noise_removed for e in self._extracts) / max(len(self._extracts), 1)
        return {"temperature": self.temperature, "total_extracts": len(self._extracts),
                "total_burned": self._total_burned, "avg_noise_removed": round(avg_noise, 4)}


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    action = payload.get("action", "status")
    return {"status": "active", "module": "meaning_furnace", "action": action}
