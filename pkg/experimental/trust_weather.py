#!/usr/bin/env python3
"""Map trust scores to weather metaphors."""
from __future__ import annotations

def forecast(trust: float) -> dict:
    t = max(0.0, min(1.0, float(trust)))
    if t >= 0.85: sky, note = "clear", "high trust — open routes"
    elif t >= 0.65: sky, note = "fair", "stable traffic"
    elif t >= 0.45: sky, note = "overcast", "prefer fallbacks"
    elif t >= 0.25: sky, note = "storm", "HITL likely"
    else: sky, note = "whiteout", "isolate node"
    return {"trust": t, "sky": sky, "note": note}
