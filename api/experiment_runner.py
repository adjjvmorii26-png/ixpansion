"""Experiment Runner — bridges 157+ lab experiments to the REST API.

Discovers, categorizes, and runs experiments from lab/experiments/.
Provides a unified API interface to the full experiment catalog.

Usage:
    GET  /api/experiments/catalog    — full experiment catalog
    GET  /api/experiments/<name>     — experiment details
    POST /api/experiments/run        — run an experiment
    GET  /api/experiments/categories — categorized listing
    GET  /api/experiments/search?q=  — search experiments
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

EXPERIMENTS_DIR = ROOT / "lab" / "experiments"

CATEGORY_KEYWORDS = {
    "quantum": ["quantum", "tunnel", "superposition", "entangle", "qubit", "photon"],
    "ecology": ["coral", "ecosystem", "species", "ecology", "habitat", "symbio"],
    "chaos": ["chaos", "entropy", "fractal", "turbulence", "strange"],
    "memory": ["memory", "recall", "forget", "palace", "archive"],
    "time": ["temporal", "time", "clock", "chronological", "history"],
    "social": ["social", "community", "culture", "folklore", "myth"],
    "neural": ["neural", "brain", "cognitive", "synapse", "network"],
    "cosmic": ["cosmic", "star", "galaxy", "universe", "astronom"],
    "bio": ["bio", "organism", "cell", "dna", "evolution", "tardigrade"],
    "creative": ["dream", "art", "music", "poetry", "creative"],
}


def _categorize(name: str) -> str:
    name_lower = name.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return cat
    return "general"


def _scan_experiments() -> List[Dict]:
    """Scan lab/experiments/ and build catalog."""
    if not EXPERIMENTS_DIR.exists():
        return []
    experiments = []
    for py in sorted(EXPERIMENTS_DIR.glob("*.py")):
        if py.name.startswith("_"):
            continue
        try:
            text = py.read_text(errors="replace")
            lines = text.splitlines()
        except Exception:
            continue

        docstring = ""
        for line in lines[:10]:
            stripped = line.strip().strip('"').strip("'")
            if stripped and not stripped.startswith("from") and not stripped.startswith("import"):
                docstring = stripped
                break

        has_demo = any("def demo" in line for line in lines)
        has_main = any('if __name__' in line for line in lines)
        line_count = len(lines)

        name = py.stem
        category = _categorize(name)

        experiments.append({
            "name": name,
            "file": f"lab/experiments/{py.name}",
            "category": category,
            "description": docstring[:200] if docstring else f"Experiment: {name}",
            "has_demo": has_demo,
            "has_main": has_main,
            "lines": line_count,
        })
    return experiments


class ExperimentRunner:
    def __init__(self):
        self.catalog: List[Dict] = []
        self.run_history: List[Dict] = []
        self._scan()

    def _scan(self):
        self.catalog = _scan_experiments()

    def get_catalog(self) -> List[Dict]:
        if not self.catalog:
            self._scan()
        return self.catalog

    def get_experiment(self, name: str) -> Dict:
        for exp in self.catalog:
            if exp["name"] == name:
                return exp
        return {"error": f"experiment '{name}' not found"}

    def run_experiment(self, name: str, timeout: int = 30) -> Dict:
        exp = self.get_experiment(name)
        if "error" in exp:
            return exp
        exp_path = ROOT / exp["file"]
        start = time.time()
        try:
            result = subprocess.run(
                [sys.executable, str(exp_path)],
                capture_output=True, text=True, timeout=timeout, cwd=str(ROOT)
            )
            elapsed = round(time.time() - start, 3)
            record = {
                "name": name,
                "status": "success" if result.returncode == 0 else "error",
                "elapsed_seconds": elapsed,
                "stdout": result.stdout[:2000] if result.stdout else "",
                "stderr": result.stderr[:500] if result.stderr else "",
                "return_code": result.returncode,
                "run_at": time.time(),
            }
        except subprocess.TimeoutExpired:
            elapsed = round(time.time() - start, 3)
            record = {
                "name": name,
                "status": "timeout",
                "elapsed_seconds": elapsed,
                "stdout": "",
                "stderr": f"Timed out after {timeout}s",
                "return_code": -1,
                "run_at": time.time(),
            }
        except Exception as e:
            record = {
                "name": name,
                "status": "error",
                "elapsed_seconds": round(time.time() - start, 3),
                "stdout": "",
                "stderr": str(e),
                "return_code": -1,
                "run_at": time.time(),
            }
        self.run_history.append(record)
        return record

    def categories(self) -> Dict[str, List[str]]:
        cats: Dict[str, List[str]] = {}
        for exp in self.catalog:
            cat = exp["category"]
            if cat not in cats:
                cats[cat] = []
            cats[cat].append(exp["name"])
        return cats

    def search(self, query: str) -> List[Dict]:
        q = query.lower()
        return [e for e in self.catalog if q in e["name"].lower() or q in e.get("description", "").lower()]


def handler(request, response):
    runner = ExperimentRunner()
    return {"total": len(runner.catalog), "categories": list(runner.categories().keys())}


def demo():
    runner = ExperimentRunner()
    print("=== Experiment Runner ===")
    print(f"\n  Total experiments: {len(runner.catalog)}")

    cats = runner.categories()
    print(f"  Categories: {', '.join(f'{k}({len(v)})' for k, v in sorted(cats.items(), key=lambda x: -len(x[1])))}")

    results = runner.run_experiment("quantum_tunneling")
    print(f"\n  Ran 'quantum_tunneling': {results['status']} ({results['elapsed_seconds']}s)")

    search = runner.search("quantum")
    print(f"  Search 'quantum': {len(search)} results")

    return {"total": len(runner.catalog), "categories": len(cats)}


if __name__ == "__main__":
    demo()
