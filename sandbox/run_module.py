#!/usr/bin/env python3
"""sandbox.run_module(name, *args) — dispatch to modules."""
from __future__ import annotations
import importlib.util
import json
import sys
from pathlib import Path

MOD_DIR = Path(__file__).resolve().parent / "modules"
OUT_DIR = Path(__file__).resolve().parent / "output"


def run_module(name: str, *args):
    path = MOD_DIR / f"{name}.py"
    if not path.exists():
        raise FileNotFoundError(f"module not found: {name}")
    spec = importlib.util.spec_from_file_location(f"sandbox_mod_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if hasattr(mod, "run"):
        result = mod.run(*args)
    else:
        result = {"ok": False, "error": "no run()"}
    OUT_DIR.mkdir(exist_ok=True)
    stamp = Path(OUT_DIR / f"{name}_last.json")
    stamp.write_text(json.dumps(result, indent=2, default=str))
    return result


if __name__ == "__main__":
    name = sys.argv[1]
    rest = sys.argv[2:]
    args = []
    for a in rest:
        if a.startswith("[") and a.endswith("]"):
            inner = a[1:-1]
            args.append([x.strip().strip("'\"") for x in inner.split(",") if x.strip()])
        else:
            args.append(a)
    print(json.dumps(run_module(name, *args), indent=2, default=str))
