"""Affiliate Marketing Engine — API adapter for the $0 revenue system."""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "projects" / "affiliate-marketing" / "src"))
from content_engine import handler as _content, coherence_vitals as _cv, resonates_with as _cr
from conversion_tracker import handler as _tracker

def handler(payload=None, context=None):
    p = payload or {}
    action = str(p.get("action", "dashboard")).lower()
    if action in ("generate", "tracker", "templates"):
        return _content(p, context)
    elif action in ("click", "conversion", "campaign", "dashboard"):
        return _tracker(p, context)
    return {"action": "affiliate_engine", "status": "active",
            "endpoints": ["generate", "tracker", "click", "conversion", "campaign", "dashboard"]}

def coherence_vitals():
    return _cv()

def resonates_with():
    return _cr()
