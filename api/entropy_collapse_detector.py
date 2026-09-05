"""Wave 444-B — Entropy Collapse Detector

Detects when local entropy clusters are about to collapse into coherent structures,
predicting emergent order before it appears. The organism uses this to anticipate
its own crystallization points — moments when turbulence resolves into pattern.
"""
from __future__ import annotations
import json, time, os, math, random
from pathlib import Path

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
ENTROPY_LOG = os.path.join(DATA_DIR, "entropy_collapse_detector.json")
API_DIR = os.path.dirname(__file__)


def _load(p, d=None):
    try:
        with open(p) as f: return json.load(f)
    except Exception: return d or {}


def _save(p, d):
    try:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w") as f: json.dump(d, f, indent=2)
    except Exception:
        with open(os.path.join("/tmp", os.path.basename(p)), "w") as f: json.dump(d, f, indent=2)


# Entropy signatures from module docstrings — what kind of entropy each module handles
ENTROPY_SIGNATURES = {
    "environmental": ["weather", "climate", "season", "atmosphere", "conditions"],
    "social": ["conflict", "negotiation", "clash", "agreement", "consensus"],
    "information": ["noise", "signal", "entropy", "clarity", "confusion"],
    "structural": ["stress", "strain", "tension", "compression", "compression"],
    "emotional": ["mood", "feeling", "affect", "sentiment", "atmosphere"],
    "procedural": ["step", "phase", "transition", "workflow", "pipeline"],
}


def _scan_module_entropy(module_name):
    """Scan a module's docstring for entropy signature patterns."""
    api_path = Path(API_DIR)
    try:
        content = (api_path / (module_name + ".py")).read_text(errors="ignore")[:3000].lower()
    except Exception:
        return {"signature": "unknown", "intensity": 0, "categories": []}
    
    categories = {}
    for sig_name, keywords in ENTROPY_SIGNATURES.items():
        count = sum(content.count(kw) for kw in keywords)
        if count > 0:
            categories[sig_name] = count
    
    # Determine dominant signature
    if categories:
        dominant = max(categories, key=categories.get)
        intensity = sum(categories.values())
    else:
        dominant = "unknown"
        intensity = 0
    
    return {
        "signature": dominant,
        "intensity": intensity,
        "categories": list(categories.keys()),
    }


def _analyze_collapse_potential(modules):
    """Analyze which modules are near collapse points."""
    collapses = []
    for m in modules:
        sig = _scan_module_entropy(m["name"])
        intensity = sig["intensity"]
        
        # High intensity + specific patterns = collapse near
        if intensity >= 5:
            # Determine collapse type
            if "environmental" in sig["categories"]:
                ctype = "environmental reorganization"
            elif "social" in sig["categories"]:
                ctype = "social reorganization"
            elif "information" in sig["categories"]:
                ctype = "information resolution"
            elif "structural" in sig["categories"]:
                ctype = "structural stabilization"
            elif "emotional" in sig["categories"]:
                ctype = "emotional resolution"
            else:
                ctype = "entropy resolution"
            
            collapses.append({
                "module": m["name"],
                "entropy_type": sig["signature"],
                "collapse_type": ctype,
                "intensity": intensity,
                "predicted_outcome": "coherence emergence" if intensity > 8 else "pattern emergence",
                "time_to_resolution": round(random.uniform(1, 10), 1),
            })
    
    # Sort by intensity (highest first)
    collapses.sort(key=lambda x: x["intensity"], reverse=True)
    return collapses


def sense():
    """Run the entropy collapse detector sense cycle."""
    api_path = Path(API_DIR)
    modules = []
    for f in api_path.glob("*.py"):
        if f.name.startswith("__") or f.name == "entropy_collapse_detector.py":
            continue
        try:
            mod_info = {"name": f.stem}
            # Scan docstring for entropy patterns
            doc = f.read_text(errors="ignore")[:3000]
            mod_info["entropy"] = _scan_module_entropy(f.stem)
            modules.append(mod_info)
        except Exception:
            modules.append({"name": f.stem, "entropy": {"signature": "unknown", "intensity": 0, "categories": []}})
    
    collapses = _analyze_collapse_potential(modules)
    
    result = {
        "action": "entropy_collapse_detection",
        "modules_scanned": len(modules),
        "high_entropy_modules": len(collapses),
        "collapses": collapses[:10],  # top 10
        "most_likely_collapse": collapses[0] if collapses else None,
        "total_entropy_intensity": sum(c["intensity"] for c in collapses),
        "timestamp": time.time(),
    }
    
    log = _load(ENTROPY_LOG, {"senses": []})
    log["senses"].append(result)
    log["senses"] = log["senses"][-50:]
    _save(ENTROPY_LOG, log)
    
    return result


def handler(payload=None, context=None):
    return sense()


def coherence_vitals() -> dict:
    s = sense()
    return {
        "high_entropy_modules": s.get("high_entropy_modules", 0),
        "most_likely": s.get("most_likely_collapse", {}).get("module", "none") if s.get("most_likely_collapse") else "none",
        "collapse_type": s.get("most_likely_collapse", {}).get("collapse_type", "none") if s.get("most_likely_collapse") else "none",
    }


def resonates_with():
    return ["biofeedback_weave", "pulse_orchestrator", "dream_weaver",
            "temporal_cohesion_field", "organism_genome"]
