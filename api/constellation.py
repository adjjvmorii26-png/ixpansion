"""Constellation API — navigate the inter-module dependency graph."""
from __future__ import annotations
import json
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def build_constellation():
    """Build a dependency graph across all subsystems by analyzing imports."""
    nodes = []
    edges = []

    subsystems = {
        "lab": ROOT / "lab",
        "bridges": ROOT / "bridges",
        "constellation": ROOT / "constellation",
        "mycelium": ROOT / "mycelium",
        "ixpansion": ROOT / "ixpansion",
        "omega_prime": ROOT / "omega_prime",
        "omega_fractal_engine": ROOT / "omega_fractal_engine",
        "solid-organism": ROOT / "solid-organism",
        "api": ROOT / "api",
    }

    module_map = {}  # stem -> subsystem

    for subsystem, base in subsystems.items():
        if not base.exists():
            continue
        for py in base.rglob("*.py"):
            if py.name.startswith("_") or py.name == "conftest.py":
                continue
            stem = py.stem
            module_map[stem] = subsystem
            rel = str(py.relative_to(ROOT))
            text = py.read_text(errors="replace")
            import_count = sum(
                1 for ln in text.splitlines()
                if ln.strip().startswith(("import ", "from "))
            )
            nodes.append({
                "id": stem,
                "subsystem": subsystem,
                "file": rel,
                "imports": import_count,
                "weight": len(text.splitlines()),
            })

    # Build edges from import analysis
    for subsystem, base in subsystems.items():
        if not base.exists():
            continue
        for py in base.rglob("*.py"):
            if py.name.startswith("_") or py.name == "conftest.py":
                continue
            text = py.read_text(errors="replace")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("from ") or stripped.startswith("import "):
                    for stem, target_sub in module_map.items():
                        if stem != py.stem and stem in stripped:
                            edges.append({
                                "source": py.stem,
                                "target": stem,
                                "type": "import",
                            })

    # Deduplicate edges
    seen = set()
    unique_edges = []
    for e in edges:
        key = (e["source"], e["target"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    # Compute density
    n = len(nodes)
    e = len(unique_edges)
    max_edges = n * (n - 1) if n > 1 else 1
    density = e / max_edges if max_edges > 0 else 0

    # Subsystem clusters
    clusters = {}
    for node in nodes:
        s = node["subsystem"]
        if s not in clusters:
            clusters[s] = []
        clusters[s].append(node["id"])

    return {
        "nodes": nodes[:200],
        "edges": unique_edges[:500],
        "clusters": {k: len(v) for k, v in clusters.items()},
        "stats": {
            "total_nodes": n,
            "total_edges": e,
            "density": round(density, 4),
            "most_connected": sorted(
                [(nid, sum(1 for ed in unique_edges if ed["source"] == nid or ed["target"] == nid))
                 for nid in module_map],
                key=lambda x: x[1], reverse=True
            )[:10],
        },
        "signature": hashlib.sha256(f"{n}:{e}".encode()).hexdigest()[:12],
    }


def handler(request, response):
    return build_constellation()


if __name__ == "__main__":
    result = handler(None, None)
    print(json.dumps(result, indent=2))

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "constellation"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
