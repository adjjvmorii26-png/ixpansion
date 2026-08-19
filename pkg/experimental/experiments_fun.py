#!/usr/bin/env python3
"""Playful experimental organs — moon bias, constellation, weather haiku."""
from __future__ import annotations
from datetime import date
from typing import List

def moon_phase_bias(day: date | None = None) -> float:
    d = (day or date.today()).day
    x = abs((d % 30) - 15) / 15.0
    return round(0.02 - 0.04 * x, 4)

def constellation_name(organs: List[dict]) -> str:
    top = sorted(organs, key=lambda o: -float(o.get("score", 0)))[:3]
    return "-".join(o.get("id", "?") for o in top).upper() if top else "VOID"

def trust_weather(score: float) -> str:
    t = max(0.0, min(1.0, float(score)))
    if t >= 0.9: return "aurora"
    if t >= 0.8: return "clear"
    if t >= 0.7: return "fair"
    if t >= 0.55: return "overcast"
    if t >= 0.4: return "squall"
    return "whiteout"

def agent_haiku(body_score: float, weather: str) -> str:
    return f"score {int(body_score)} holds still / {weather} over the ten organs / pulse keeps the watch"

def fun_snapshot(st: dict) -> dict:
    organs = st.get("organs") or []
    bs = float(st.get("body_score") or 0)
    avg = (sum(float(o.get("score", 0)) for o in organs) / len(organs)) if organs else 0
    weather = trust_weather(avg)
    return {"moon_bias": moon_phase_bias(), "constellation": constellation_name(organs),
            "weather": weather, "haiku": agent_haiku(bs, weather), "body_score": bs}
