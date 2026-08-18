#!/usr/bin/env python3
"""Chaos/ops summaries as 5-7-5 haiku."""
from __future__ import annotations

def haiku(pass_: bool, blocked: int = 0, drained: int = 0) -> str:
    if pass_:
        return f"ring holds the storm\n{blocked} writes wait offshore\nquorum breathes again"
    return f"fault lines open wide\n{drained} frames spill into night\nwatchdog still awake"
