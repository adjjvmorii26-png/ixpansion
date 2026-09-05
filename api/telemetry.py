"""Telemetry API — real-time system telemetry endpoint."""
from __future__ import annotations
import json
import sys
import hashlib
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def collect_telemetry():
    """Gather telemetry from all subsystems."""
    subsystems = {}

    # Count modules per subsystem
    dirs = {
        "bridges": ROOT / "bridges",
        "constellation": ROOT / "constellation",
        "mycelium": ROOT / "mycelium",
        "ixpansion": ROOT / "ixpansion",
        "omega_prime": ROOT / "omega_prime",
        "omega_fractal_engine": ROOT / "omega_fractal_engine",
        "lab": ROOT / "lab",
    }

    for name, path in dirs.items():
        if path.exists():
            py_files = list(path.rglob("*.py"))
            test_files = list(path.rglob("test_*.py"))
            subsystems[name] = {
                "modules": len(py_files) - len(test_files),
                "tests": len(test_files),
                "total_lines": sum(
                    len(f.read_text(errors="replace").splitlines())
                    for f in py_files if f.is_file()
                ),
            }

    # Lab experiments count
    lab_dir = ROOT / "lab" / "experiments"
    if lab_dir.exists():
        lab_exps = [f for f in lab_dir.glob("*.py") if not f.name.startswith("_")]
        subsystems["lab_experiments"] = {
            "count": len(lab_exps),
            "names": [f.stem for f in lab_exps],
        }

    total_modules = sum(s.get("modules", 0) for s in subsystems.values() if isinstance(s, dict))
    total_tests = sum(s.get("tests", 0) for s in subsystems.values() if isinstance(s, dict))

    return {
        "subsystems": subsystems,
        "summary": {
            "total_modules": total_modules,
            "total_tests": total_tests,
            "subsystem_count": len([s for s in subsystems.values() if isinstance(s, dict) and "modules" in s]),
        },
        "signature": hashlib.sha256(
            json.dumps(str(total_modules) + str(total_tests)).encode()
        ).hexdigest()[:12],
    }


def handler(request, response):
    return collect_telemetry()


if __name__ == "__main__":
    print(json.dumps(handler(None, None), indent=2))

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "interface", "status": "active", "wave": "0", "module": "telemetry"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]
