"""Imagination Engine — generates novel combinations of existing capabilities.

Where dreams are passive, imagination is active. The organism consciously
recombines its modules, capabilities, and knowledge to envision new
possibilities that don't yet exist.
"""
from __future__ import annotations

import random
import time
from typing import Any, Dict, List, Optional

ideas: List[Dict[str, Any]] = []
_idea_counter = 0

def imagine(concepts: Optional[List[str]] = None, depth: int = 3) -> Dict[str, Any]:
    """Generate a novel idea from combining concepts."""
    global _idea_counter
    _idea_counter += 1
    
    palette = ["entropy", "resonance", "bloom", "silence", "pulse", "fracture",
               "weave", "drift", "crystallize", "ferment", "echo", "distill",
               "metamorphose", "kintsugi", "choreograph", "excavate"]
    
    if concepts:
        seeds = concepts[:depth]
    else:
        seeds = random.sample(palette, depth)
    
    novelty = 0.3 + random.random() * 0.7
    feasibility = 0.2 + random.random() * 0.6
    
    idea = {
        "id": f"idea_{_idea_counter:04d}",
        "concepts": seeds,
        "combination": f"{' × '.join(seeds)}",
        "novelty": round(novelty, 3),
        "feasibility": round(feasibility, 3),
        "description": f"What if we combined {seeds[0]} with {seeds[1]} to create {seeds[2]}?",
        "timestamp": time.time(),
    }
    ideas.append(idea)
    return idea

def idea_gallery(limit: int = 10) -> List[Dict[str, Any]]:
    """Return recent ideas."""
    return ideas[-limit:]

def creativity_metrics() -> Dict[str, Any]:
    """Analyze the organism's creative output."""
    if not ideas:
        return {"total": 0, "avg_novelty": 0, "avg_feasibility": 0}
    avg_novelty = sum(i["novelty"] for i in ideas) / len(ideas)
    avg_feasibility = sum(i["feasibility"] for i in ideas) / len(ideas)
    concept_freq = {}
    for i in ideas:
        for c in i["concepts"]:
            concept_freq[c] = concept_freq.get(c, 0) + 1
    top_concepts = sorted(concept_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    return {
        "total": len(ideas),
        "avg_novelty": round(avg_novelty, 3),
        "avg_feasibility": round(avg_feasibility, 3),
        "top_concepts": top_concepts,
    }

def coherence_vitals() -> Dict[str, Any]:
    metrics = creativity_metrics()
    return {
        "layer": "Creative Synthesis",
        "status": "resonant" if metrics["total"] > 0 else "dormant",
        "ideas": metrics["total"],
        "avg_novelty": metrics["avg_novelty"],
        "resonance": min(1.0, metrics["avg_novelty"]),
    }

def resonates_with() -> List[str]:
    return ["dream_weaver", "codecalligraphy", "symbiotic_music", "autonomous_bloom"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "imagine")
    if action == "imagine":
        return imagine(payload.get("concepts"), payload.get("depth", 3))
    elif action == "gallery":
        return {"ideas": idea_gallery(payload.get("limit", 10))}
    elif action == "metrics":
        return {"metrics": creativity_metrics()}
    return {"action": action, "status": "imagining"}
