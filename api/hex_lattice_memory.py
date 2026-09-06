"""Hex Lattice Memory Forge — PK03 API adapter."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fractal_spine.memory_forge import handler as _handler, coherence_vitals as _vitals, resonates_with as _res

def handler(payload=None, context=None):
    return _handler(payload, context)

def coherence_vitals():
    return _vitals()

def resonates_with():
    return _res()
