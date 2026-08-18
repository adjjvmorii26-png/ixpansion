#!/usr/bin/env python3
"""LUMEN — trust scores projected as constellation stars"""
from __future__ import annotations
import hashlib, math
from dataclasses import dataclass
from typing import Dict


@dataclass
class Constellation:
    name: str
    signature: str
    stars: list


class LumenProjector:
    def __init__(self, seed: int = 1):
        self.seed = seed

    def project(self, trust_map: Dict[str, float]) -> Constellation:
        stars = []
        for k, v in sorted(trust_map.items()):
            h = hashlib.sha1(f"{self.seed}:{k}".encode()).hexdigest()
            x = int(h[:8], 16) % 1000 / 1000.0
            y = int(h[8:16], 16) % 1000 / 1000.0
            mag = 1.0 - max(0.0, min(1.0, float(v)))
            stars.append({"id": k, "x": x, "y": y, "mag": mag, "trust": float(v)})
        sig = hashlib.sha1(str(sorted(trust_map.items())).encode()).hexdigest()[:16]
        name = "Vectra-Arc" if sum(trust_map.values()) / max(1, len(trust_map)) > 0.6 else "Dim-Cluster"
        return Constellation(name=name, signature=sig, stars=stars)
