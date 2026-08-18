#!/usr/bin/env python3
"""Aggregate organ activity into body temperature."""
from __future__ import annotations
import json
from pathlib import Path

def temperature(body_path: str = "content_output/vivarium_body.json") -> dict:
    p = Path(body_path)
    if not p.exists():
        return {"celsius": 36.5, "note": "no body index"}
    body = json.loads(p.read_text())
    n = max(1, body.get("cell_count", 1))
    pulse = body.get("pulse", 0)
    c = 36.0 + 2.5 * (pulse / n) + min(1.5, n / 500)
    note = "resting" if c < 36.8 else ("active" if c < 37.6 else "fever")
    return {"celsius": round(c, 2), "cells": n, "pulse": pulse, "note": note}
