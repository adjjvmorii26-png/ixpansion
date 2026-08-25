from __future__ import annotations
"""Fractal Documentation — self-similar docs that grow with the codebase.

Like fractals that reveal more detail at every zoom level, this module
generates documentation that works at multiple granularities: high-level
overview, module summary, function detail, and implementation deep-dive.
Each level contains the same information at different resolutions.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class DocLevel:
    level: int
    granularity: str
    content: str
    children: List[str] = field(default_factory=list)
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = hashlib.md5(self.content.encode()).hexdigest()[:8]

class FractalDocumentation:
    GRANULARITIES = ["overview", "module", "function", "implementation"]

    def __init__(self):
        self.levels: Dict[str, List[DocLevel]] = {}
        self.module_count = 0

    def document_module(self, name: str, overview: str, module_doc: str,
                        functions: List[Dict], implementation: str = ""):
        levels = []
        levels.append(DocLevel(level=0, granularity="overview", content=overview))
        levels.append(DocLevel(level=1, granularity="module", content=module_doc))
        for func in functions:
            func_doc = f"{func.get('name', 'unknown')}: {func.get('docstring', '')}"
            levels.append(DocLevel(level=2, granularity="function", content=func_doc))
        if implementation:
            levels.append(DocLevel(level=3, granularity="implementation", content=implementation))
        self.levels[name] = levels
        self.module_count += 1

    def get_level(self, module_name: str, granularity: str) -> Optional[DocLevel]:
        if module_name not in self.levels:
            return None
        for level in self.levels[module_name]:
            if level.granularity == granularity:
                return level
        return None

    def summary(self) -> Dict:
        total_levels = sum(len(levels) for levels in self.levels.values())
        return {
            "modules_documented": self.module_count,
            "total_doc_levels": total_levels,
            "granularities": self.GRANULARITIES,
            "modules": {
                name: [l.granularity for l in levels]
                for name, levels in self.levels.items()
            },
        }


def demo():
    docs = FractalDocumentation()
    print("=== Fractal Documentation ===")
    docs.document_module(
        "photon_memory",
        overview="Interference-pattern based information storage",
        module_doc="Stores memories as photon wave patterns with fidelity measurement",
        functions=[
            {"name": "store", "docstring": "Store a memory as an interference pattern"},
            {"name": "read", "docstring": "Read a memory using reference wave superposition"},
        ],
        implementation="Uses complex amplitude arrays with wavelength-based encoding",
    )
    docs.document_module(
        "coral_reef",
        overview="Ecosystem growth simulation",
        module_doc="Modules grow like coral polyps competing for resources",
        functions=[
            {"name": "spawn_polyp", "docstring": "Create a new polyp at given position"},
            {"name": "advance_tick", "docstring": "Advance simulation by one tick"},
        ],
    )
    overview = docs.get_level("photon_memory", "overview")
    print(f"  Overview: {overview.content if overview else 'not found'}")
    func_doc = docs.get_level("photon_memory", "function")
    print(f"  Function: {func_doc.content if func_doc else 'not found'}")
    summary = docs.summary()
    print(f"\n  Modules: {summary['modules_documented']}")
    print(f"  Total doc levels: {summary['total_doc_levels']}")
    return summary


if __name__ == "__main__":
    demo()
