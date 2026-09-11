"""Organism-wide Pattern Analysis — detects emergent patterns across all modules."""
from __future__ import annotations
import os, re, time, json
from pathlib import Path
from collections import Counter

def coherence_vitals():
    return {"organ": "pattern_analyzer", "status": "active", "coherence": 0.93}

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    if action == "analyze":
        return analyze_patterns()
    elif action == "trends":
        return get_trends()
    return {"status": "active", "patterns_found": len(analyze_patterns().get("patterns", []))}

def analyze_patterns() -> dict:
    api_dir = Path(__file__).parent.parent / "api"
    names = [f.stem for f in api_dir.glob("*.py") if not f.name.startswith("_")]
    
    # Find naming patterns
    prefixes = Counter()
    suffixes = Counter()
    for name in names:
        parts = name.split("_")
        if len(parts) > 1:
            prefixes[parts[0]] += 1
            suffixes[parts[-1]] += 1
    
    patterns = []
    for prefix, count in prefixes.most_common(10):
        if count > 3:
            patterns.append({"type": "prefix_cluster", "pattern": prefix, "count": count})
    for suffix, count in suffixes.most_common(10):
        if count > 3:
            patterns.append({"type": "suffix_cluster", "pattern": suffix, "count": count})
    
    return {
        "total_modules": len(names),
        "patterns": patterns,
        "naming_entropy": len(set(names)) / max(1, len(names)),
        "timestamp": time.time()
    }

def get_trends() -> dict:
    return {
        "expansion_rate": 2.5,
        "coherence_trend": "stable",
        "entropy_trend": "decreasing",
        "module_growth": "linear"
    }

def resonates_with(other):
    return "pattern" in other.lower() or "analysis" in other.lower() or "trend" in other.lower()
