"""Experiments API — list, run, and query experimental modules."""
from __future__ import annotations
import json
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def list_experiments():
    """List all available experimental modules."""
    lab_dir = ROOT / "lab" / "experiments"
    if not lab_dir.exists():
        return {"experiments": [], "count": 0}

    experiments = []
    for py_file in sorted(lab_dir.glob("*.py")):
        if py_file.name.startswith("_") or py_file.name == "__init__.py":
            continue
        experiments.append({
            "name": py_file.stem,
            "file": str(py_file.relative_to(ROOT)),
            "size_bytes": py_file.stat().st_size,
        })

    return {"experiments": experiments, "count": len(experiments)}


def run_experiment(name: str):
    """Run a specific experiment by name."""
    lab_dir = ROOT / "lab" / "experiments"
    module_path = lab_dir / f"{name}.py"
    if not module_path.exists():
        return {"error": f"experiment '{name}' not found"}

    try:
        spec = importlib.util.spec_from_file_location(f"lab.experiments.{name}", str(module_path))
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            if hasattr(mod, "demo"):
                result = mod.demo()
                return {"name": name, "result": result}
            elif hasattr(mod, "main"):
                return {"name": name, "status": "has_main_no_demo"}
            return {"name": name, "status": "no_demo_function"}
    except Exception as e:
        return {"name": name, "error": str(e)}


def handler(request, response):
    """Route to list or run based on query params."""
    query = {}
    if hasattr(request, "GET"):
        query = dict(request.GET)

    name = query.get("name")
    action = query.get("action", "list")

    if action == "run" and name:
        return run_experiment(name)
    return list_experiments()


if __name__ == "__main__":
    result = handler(None, None)
    print(json.dumps(result, indent=2))
