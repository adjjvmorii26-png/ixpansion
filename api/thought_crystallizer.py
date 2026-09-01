"""Thought Crystallizer — converts abstract concepts into concrete module blueprints.

When the organism imagines a new capability, this module generates the
actual code structure needed to implement it: file paths, function signatures,
dependency lists, and coherence_vitals stubs.
"""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, List, Optional

crystals: List[Dict[str, Any]] = []

def crystallize(concept: str, dependencies: Optional[List[str]] = None) -> Dict[str, Any]:
    """Convert an abstract concept into a concrete module blueprint."""
    h = hashlib.sha256(concept.encode()).hexdigest()[:8]
    module_name = concept.lower().replace(" ", "_").replace("-", "_")[:30]
    
    deps = dependencies or ["hashlib", "time", "typing"]
    
    blueprint = {
        "id": f"crystal_{h}",
        "concept": concept,
        "module_name": module_name,
        "file_path": f"api/{module_name}.py",
        "functions": [
            f"def coherence_vitals() -> Dict[str, Any]:",
            f"def resonates_with() -> List[str]:",
            f"def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:",
            f"def {module_name}_core() -> Dict[str, Any]:",
        ],
        "imports": deps,
        "template": f'''"""{"=" * len(concept)}\\n{concept}\\n{"=" * len(concept)}"""\\nfrom __future__ import annotations\\nimport time\\nfrom typing import Any, Dict, List, Optional\\n\\ndef coherence_vitals() -> Dict[str, Any]:\\n    return {{"layer": "Crystallized Thought", "status": "dormant", "resonance": 0.5}}\\n\\ndef resonates_with() -> List[str]:\\n    return []\\n\\ndef handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:\\n    return {{"status": "crystallized"}}''',
        "created": time.time(),
        "status": "crystallized",
    }
    crystals.append(blueprint)
    return blueprint

def crystal_gallery() -> List[Dict[str, Any]]:
    return [{"id": c["id"], "concept": c["concept"], "module": c["module_name"]} for c in crystals]

def coherence_vitals() -> Dict[str, Any]:
    return {
        "layer": "Creative Synthesis",
        "status": "resonant" if crystals else "dormant",
        "crystals": len(crystals),
        "resonance": min(1.0, len(crystals) / 10),
    }

def resonates_with() -> List[str]:
    return ["imagination_engine", "autogenesis", "genesis_forge", "codecalligraphy"]

def handler(payload: Dict[str, Any], context=None) -> Dict[str, Any]:
    action = payload.get("action", "crystallize")
    if action == "crystallize":
        return crystallize(payload.get("concept", "unknown"), payload.get("dependencies"))
    elif action == "gallery":
        return {"crystals": crystal_gallery()}
    return {"action": action, "crystals": len(crystals)}
