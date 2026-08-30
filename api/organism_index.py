"""Organism Index — the living catalog of Solid Organism experiments.

Every experiment in solid-organism/lab is a distinct organism with its own
behavior, philosophy, and vitality. The Organism Index inventories them:
their habitat (file), their essence (docstring), their vitality (runnable?),
and the principle they embody.

Usage:
  GET  /api/organism_index                    — full catalog
  GET  /api/organism_index?filter=flocking    — one organism's dossier
  POST /api/organism_index {"habitat": "stigmergy"}  — dossier
"""
from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
LAB_DIR = ROOT / "solid-organism" / "lab"


def _extract_docstring(path: Path) -> str:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        return ast.get_docstring(tree) or ""
    except (OSError, SyntaxError):
        return ""


def _extract_principle(docstring: str) -> str:
    """Extract the core principle from the first paragraph of the docstring."""
    first_para = docstring.split("\n\n")[0].strip()
    return first_para


def _estimate_vitality(path: Path) -> Dict[str, Any]:
    """Estimate an experiment's vitality from file stats."""
    try:
        size = path.stat().st_size
        lines = len(path.read_text(encoding="utf-8").splitlines())
        importable = True
        # check that the file parses as valid python
        try:
            ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            importable = False
        return {
            "bytes": size,
            "lines": lines,
            "importable": importable,
            "maturity": "mature" if lines > 150 else ("adolescent" if lines > 80 else "seedling"),
        }
    except OSError:
        return {"bytes": 0, "lines": 0, "importable": False, "maturity": "unknown"}


def _organism_dossier(name: str) -> Dict[str, Any]:
    path = LAB_DIR / f"{name}.py"
    if not path.exists():
        return {"name": name, "exists": False}
    docstring = _extract_docstring(path)
    principle = _extract_principle(docstring)
    return {
        "name": name,
        "exists": True,
        "habitat": str(path.relative_to(ROOT)),
        "principle": principle,
        "vitality": _estimate_vitality(path),
        "run_command": f"python3 {path.relative_to(ROOT)} --help",
        "docstring": docstring[:400],
    }


def inventory() -> Dict[str, Any]:
    """Inventory all organisms in the lab."""
    organisms = []
    if LAB_DIR.exists():
        for path in sorted(LAB_DIR.glob("*.py")):
            if path.stem.startswith("_"):
                continue
            organisms.append(_organism_dossier(path.stem))

    return {
        "collective": "Solid Organism",
        "organism_count": len(organisms),
        "organisms": organisms,
        "ecosystem_readout": (
            f"The collection hosts {len(organisms)} organisms, each embodying "
            "a principle: coordination without planning, order without repetition, "
            "memory that outlives its source."
        ),
        "philosophy": (
            "These are not utilities. They are living experiments — each one "
            "a thought that grew legs. Some solve problems; some pose questions. "
            "All of them breathe."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    name = payload.get("filter") or payload.get("habitat") or payload.get("organism")
    if name:
        result = _organism_dossier(name)
        result["action"] = "dossier"
        return result
    result = inventory()
    result["action"] = "inventory"
    return result
