"""Module DNA — generates unique genetic fingerprints for every module.

Each module has a DNA sequence derived from its code structure, function
names, imports, and complexity. These fingerprints can be used to find
evolutionary relationships between modules, detect clones, and measure
genetic diversity across the codebase.
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
_dna_cache: Dict[str, Dict[str, Any]] = {}

_NUCLEOTIDES = "ACGT"

def _code_to_dna(code: str) -> str:
    """Convert code hash to DNA-like sequence."""
    h = hashlib.sha256(code.encode()).hexdigest()
    dna = ""
    for ch in h:
        idx = int(ch, 16)
        dna += _NUCLEOTIDES[idx % 4]
    return dna[:64]

def _gene_markers(code: str) -> Dict[str, str]:
    """Extract gene markers from code features."""
    markers = {}
    if "async" in code:
        markers["async"] = "present"
    if "class " in code:
        markers["class"] = "present"
    if "def handler" in code:
        markers["handler"] = "present"
    if "def coherence_vitals" in code:
        markers["vitals"] = "present"
    if "import json" in code:
        markers["json"] = "present"
    if "time.time()" in code:
        markers["temporal"] = "present"
    lines = code.split("\n")
    markers["complexity"] = "high" if len(lines) > 100 else "medium" if len(lines) > 40 else "low"
    return markers

def sequence(module_name: str) -> Dict[str, Any]:
    """Generate DNA sequence for a module."""
    if module_name in _dna_cache:
        return _dna_cache[module_name]
    
    path = ROOT / "api" / f"{module_name}.py"
    if not path.exists():
        return {"error": f"module {module_name} not found"}
    
    code = path.read_text(encoding="utf-8")
    dna = _code_to_dna(code)
    markers = _gene_markers(code)
    
    seq = {
        "module": module_name,
        "dna": dna,
        "markers": markers,
        "gc_content": round((dna.count("G") + dna.count("C")) / len(dna), 3),
        "line_count": len(code.split("\n")),
    }
    _dna_cache[module_name] = seq
    return seq

def genetic_diversity(module_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """Measure genetic diversity across modules."""
    if not module_names:
        api_dir = ROOT / "api"
        module_names = [f.stem for f in api_dir.glob("*.py") if not f.name.startswith("_")][:20]
    
    sequences = [sequence(m) for m in module_names if "error" not in sequence(m)]
    if not sequences:
        return {"modules": 0, "avg_gc": 0, "diversity": 0}
    
    avg_gc = sum(s["gc_content"] for s in sequences) / len(sequences)
    
    # Count unique DNA prefixes (first 8 chars)
    prefixes = set(s["dna"][:8] for s in sequences)
    
    return {
        "modules": len(sequences),
        "avg_gc": round(avg_gc, 3),
        "unique_prefixes": len(prefixes),
        "diversity_score": round(len(prefixes) / max(len(sequences), 1), 3),
    }

def coherence_vitals() -> Dict[str, Any]:
    div = genetic_diversity()
    return {
        "layer": "Self-Analysis",
        "status": "resonant",
        "modules_sequenced": div["modules"],
        "diversity": div["diversity_score"],
        "resonance": div["diversity_score"],
    }

def resonates_with() -> List[str]:
    return ["codecalligraphy", "dream_archaeologist", "ancestor_map", "evolution_kernel"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "diversity")
    if action == "sequence":
        return sequence(payload.get("module", ""))
    elif action == "diversity":
        return {"diversity": genetic_diversity(payload.get("modules"))}
    return {"action": action, "status": "genetic"}
