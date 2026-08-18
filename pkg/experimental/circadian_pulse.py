#!/usr/bin/env python3
"""Circadian mesh pulse — activity factor from local clock."""
from __future__ import annotations
import math
from datetime import datetime

def solar_factor(hour: float | None = None) -> float:
    if hour is None:
        hour = datetime.now().hour + datetime.now().minute / 60.0
    x = (hour - 14.0) / 12.0
    return 0.35 + 0.65 * (0.5 * (1 + math.cos(math.pi * min(1.0, abs(x)))))

def recommend_particles(base: int = 12) -> int:
    return max(3, int(base * solar_factor()))

if __name__ == "__main__":
    print({"hour_factor": round(solar_factor(), 3), "particles": recommend_particles()})
