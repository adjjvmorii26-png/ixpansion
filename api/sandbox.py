"""Sandbox API — inspect sandbox environments, worlds, and domains."""
from __future__ import annotations
import json
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SANDBOX_DIRS = [
    ROOT / "sandbox",
    ROOT / "ixpansion" / "src" / "worlds",
    ROOT / "omega_prime" / "sandbox",
    ROOT / "omega-fractal-engine" / "lattice",
    ROOT / "project_root" / "sandbox",
]


def discover_sandbox_modules():
    modules = []
    for base in SANDBOX_DIRS:
        if not base.exists():
            continue
        for py in base.rglob("*.py"):
            if py.name.startswith("_") or "test_" in py.name:
                continue
            text = py.read_text(errors="replace")
            lines = text.splitlines()
            classes = [
                ln.strip().split("class ")[1].split("(")[0]
                for ln in lines
                if ln.strip().startswith("class ")
            ]
            has_demo = any("def demo" in ln for ln in lines)
            subsystem = "unknown"
            rel = py.relative_to(ROOT)
            parts = rel.parts
            if parts:
                subsystem = parts[0]

            modules.append({
                "name": py.stem,
                "subsystem": subsystem,
                "file": str(rel),
                "classes": classes[:5],
                "has_demo": has_demo,
                "lines": len(lines),
            })

    return {
        "modules": modules,
        "count": len(modules),
        "dirs_scanned": [str(d.relative_to(ROOT)) for d in SANDBOX_DIRS if d.exists()],
        "signature": hashlib.sha256(str(len(modules)).encode()).hexdigest()[:12],
    }


def handler(request, response):
    query = {}
    if hasattr(request, "GET"):
        query = dict(request.GET)

    return discover_sandbox_modules()


if __name__ == "__main__":
    print(json.dumps(handler(None, None), indent=2))
