#!/usr/bin/env python3
"""Scoped RNG for deterministic demos."""
from __future__ import annotations
import random
from contextlib import contextmanager
from typing import Iterator

@contextmanager
def scoped_rng(seed: int = 0) -> Iterator[random.Random]:
    yield random.Random(seed)

def seed_demo(seed: int = 7) -> random.Random:
    return random.Random(seed)
