"""Agents API — query and inspect agent registry across all subsystems."""
from __future__ import annotations
import json
import sys
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

AGENT_DIRS = {
    "ixpansion": ROOT / "ixpansion" / "src" / "agents",
    "omega_prime": ROOT / "omega_prime" / "agents",
    "nexus_observatory": ROOT / "nexus_observatory",
    "solid_organism": ROOT / "solid-organism",
    "project_root": ROOT / "project_root" / "agents",
}


def discover_agents():
    """Scan all subsystem directories for agent-like modules."""
    agents = []
    for subsystem, base in AGENT_DIRS.items():
        if not base.exists():
            continue
        for py in base.rglob("*.py"):
            if py.name.startswith("_") or "test_" in py.name:
                continue
            text = py.read_text(errors="replace")
            lines = text.splitlines()
            # Heuristic: look for class definitions with 'agent' in name
            classes = [
                ln.strip().split("class ")[1].split("(")[0]
                for ln in lines
                if ln.strip().startswith("class ") and "agent" in ln.lower()
            ]
            # Look for demo/main functions
            has_demo = any("def demo" in ln for ln in lines)
            has_main = any("def main" in ln for ln in lines)
            # Extract docstring if present
            doc = ""
            in_doc = False
            for ln in lines:
                stripped = ln.strip()
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    if in_doc:
                        break
                    doc = stripped.strip("\"'")
                    in_doc = True
                elif in_doc and stripped:
                    doc += " " + stripped
            agents.append({
                "name": py.stem,
                "subsystem": subsystem,
                "file": str(py.relative_to(ROOT)),
                "classes": classes,
                "has_demo": has_demo,
                "has_main": has_main,
                "doc": doc[:120] if doc else "",
                "size": py.stat().st_size,
            })

    return {
        "agents": agents,
        "count": len(agents),
        "subsystems_scanned": list(AGENT_DIRS.keys()),
        "signature": hashlib.sha256(
            "".join(a["name"] for a in agents).encode()
        ).hexdigest()[:12],
    }


def get_agent_detail(name: str):
    """Get detailed info about a specific agent module."""
    for subsystem, base in AGENT_DIRS.items():
        if not base.exists():
            continue
        for py in base.rglob(f"{name}.py"):
            text = py.read_text(errors="replace")
            lines = text.splitlines()
            classes = []
            functions = []
            for ln in lines:
                stripped = ln.strip()
                if stripped.startswith("class "):
                    classes.append(stripped.split("(")[0].replace("class ", ""))
                elif stripped.startswith("def "):
                    functions.append(stripped.split("(")[0].replace("def ", ""))

            return {
                "name": name,
                "subsystem": subsystem,
                "file": str(py.relative_to(ROOT)),
                "classes": classes,
                "functions": functions,
                "lines": len(lines),
                "size": py.stat().st_size,
            }
    return {"error": f"agent '{name}' not found"}


def handler(request, response):
    query = {}
    if hasattr(request, "GET"):
        query = dict(request.GET)

    name = query.get("name")
    if name:
        return get_agent_detail(name)
    return discover_agents()


if __name__ == "__main__":
    print(json.dumps(handler(None, None), indent=2))

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "agents"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
