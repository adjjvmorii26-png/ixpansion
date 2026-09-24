"""Wave 806 — organ registry.

Static, side-effect-free inventory of API organs. The registry deliberately
uses AST inspection instead of importing modules, so discovery cannot mutate
state or execute application code.
"""
from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
API = ROOT / "api"
WAVE = 806
NAME = "organ_registry"


def _module_name(path: Path) -> str:
    return path.stem


def _imports(tree: ast.AST) -> list[str]:
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            found.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            found.add(node.module.split(".")[0])
    return sorted(found)


def _functions(tree: ast.AST) -> set[str]:
    return {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }


def _display_path(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def inspect_file(path: Path) -> dict[str, Any]:
    try:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))
    except (OSError, SyntaxError) as exc:
        return {
            "name": _module_name(path),
            "path": _display_path(path),
            "valid": False,
            "error": str(exc)[:160],
        }

    funcs = _functions(tree)
    source_lower = source.lower()
    stateful = any(token in source_lower for token in (
        "state_file", "write_text(", ".replace(", "json.dump(", "json.dumps("
    ))
    return {
        "name": _module_name(path),
        "path": _display_path(path),
        "valid": True,
        "contract": {
            "handler": "handler" in funcs,
            "coherence_vitals": "coherence_vitals" in funcs,
            "resonates_with": "resonates_with" in funcs,
        },
        "functions": sorted(funcs),
        "imports": _imports(tree),
        "stateful": stateful,
    }


def registry(api_dir: Path | None = None) -> dict[str, Any]:
    root = api_dir or API
    files = sorted(root.glob("*.py")) if root.exists() else []
    organs = [inspect_file(path) for path in files]
    valid = [o for o in organs if o.get("valid")]
    contract_complete = [
        o for o in valid
        if all(o["contract"].values())
    ]
    invalid = [o for o in organs if not o.get("valid")]
    return {
        "wave": WAVE,
        "name": NAME,
        "api_root": str(root.relative_to(ROOT)) if root.is_relative_to(ROOT) else str(root),
        "total": len(organs),
        "valid": len(valid),
        "invalid": len(invalid),
        "contract_complete": len(contract_complete),
        "contract_gap": len(valid) - len(contract_complete),
        "stateful": sum(1 for o in valid if o.get("stateful")),
        "organs": organs,
    }


def coherence_vitals() -> dict[str, Any]:
    snap = registry()
    return {
        "wave": WAVE,
        "name": NAME,
        "module": "wave806_organ_registry",
        "ok": snap["invalid"] == 0,
        "layer": "meta",
        "status": "indexed",
        "organs": snap["total"],
        "contract_complete": snap["contract_complete"],
        "contract_gap": snap["contract_gap"],
        "stateful": snap["stateful"],
        "surface": "registry",
    }


def resonates_with() -> list[str]:
    return [
        "wave805_null_choir_counter",
        "coherence_validator",
        "dependency_resolver",
        "organism_genome",
    ]


def handler(req=None) -> dict[str, Any]:
    req = req or {}
    action = str(req.get("action") or "status").lower()
    if action == "status":
        return {**coherence_vitals(), "audio": False}
    if action in {"scan", "registry", "snapshot"}:
        return {**registry(), "status": "indexed", "audio": False}
    return {**coherence_vitals(), "status": "unknown_action", "action": action}


if __name__ == "__main__":
    import json
    print(json.dumps(handler({"action": "status"}), indent=2))
