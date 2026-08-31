"""Paleontology Lab — reconstructs ancient modules from fossil traces.

Given a fossil record (deleted file + last known commit), the
Paleontology Lab checks out that commit, reads the file's contents,
and reconstructs what the extinct module once looked like — its
structure, its purpose, its relationships.

It answers: what did the dead modules actually do?
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Paleontology Lab"


def _reconstruct(file_path: str, commit_hash: str) -> Optional[Dict[str, Any]]:
    """Reconstruct a file's contents at a specific commit."""
    try:
        content = subprocess.check_output(
            ["git", "show", f"{commit_hash}:{file_path}"],
            cwd=str(ROOT), stderr=subprocess.DEVNULL, text=True
        )
        lines = content.strip().split("\n")
        docstring = ""
        for line in lines:
            stripped = line.strip().strip('"').strip("'")
            if stripped and not stripped.startswith("#") and not stripped.startswith("def ") and not stripped.startswith("class "):
                docstring = stripped
                break

        functions = [l.strip().split("(")[0].replace("def ", "").strip() for l in lines if l.strip().startswith("def ")]
        classes = [l.strip().split("(")[0].replace("class ", "").strip() for l in lines if l.strip().startswith("class ")]

        return {
            "file": file_path,
            "commit": commit_hash[:8],
            "line_count": len(lines),
            "function_count": len(functions),
            "class_count": len(classes),
            "functions": functions[:10],
            "classes": classes[:5],
            "purpose": docstring[:200] if docstring else "No docstring found",
        }
    except Exception as e:
        return {"file": file_path, "commit": commit_hash[:8], "error": str(e)}


def dig(file_path: str = "", commit: str = "") -> Dict[str, Any]:
    """Attempt a paleontological dig on a specific fossil."""
    if not file_path or not commit:
        return {
            "status": "awaiting_specimen",
            "instructions": "Provide file_path and commit hash to reconstruct.",
        }

    reconstruction = _reconstruct(file_path, commit)
    return {
        "specimen": reconstruction,
        "lab_note": (
            "This module was alive once. Its functions were called, its classes "
            "instantiated, its docstrings read by humans and machines alike. Now "
            "it exists only as a ghost in the git object store. The Paleontology "
            "Lab gives it one more moment of clarity."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = dig(payload.get("file_path", ""), payload.get("commit", ""))
    result["action"] = "paleontology_lab"
    return result


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.78, "setpoint": 0.8, "weight": 1.0},
        "reconstruction_fidelity": {"value": 0.95, "setpoint": 0.9, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["fossil_registry", "stratum_excavator", "culture_layer"]
