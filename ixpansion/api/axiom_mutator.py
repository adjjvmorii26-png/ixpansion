from __future__ import annotations
"""Axiom mutator — rewrites foundational assumptions of the organism."""
import json
import time
from pathlib import Path
from typing import Any, Dict, List

_AXIOM_PATH = Path(__file__).resolve().parent.parent / "data" / "axioms.json"

def handler(payload: Dict[str, Any] = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Mutate a foundational axiom."""
    axioms = _load_axioms()
    if payload and "axiom" in payload and "new_definition" in payload:
        axioms[payload["axiom"]] = payload["new_definition"]
        axioms["mutated_at"] = time.time()
        _save_axioms(axioms)
    return {"axioms_count": len(axioms), "mutated": payload.get("axiom") if payload else None}

def _load_axioms() -> Dict[str, Any]:
    try:
        return json.load(open(_AXIOM_PATH, encoding="utf-8"))
    except Exception:
        return {"base_axioms": [], "mutated_at": None}

def _save_axioms(axioms: Dict[str, Any]) -> None:
    _AXIOM_PATH.write_text(json.dumps(axioms, indent=2, ensure_ascii=False))
