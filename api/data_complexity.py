"""Data Complexity — how complex is the frontier's own knowledge graph?

Measures structural complexity without any external dependencies:
  - module count & average module line-weight (size complexity)
  - token diversity across module names (naming complexity)
  - unique-word coupling (how interconnected the namespaces are)
  - a single Complexity Index (0-100) from all three axes.

Fulfills the `data_complexity` dream from the ledger.
"""
from __future__ import annotations

import math
import re
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]


def _module_stats() -> Dict[str, Any]:
    api_dir = ROOT / "api"
    names = [p.stem for p in api_dir.glob("*.py")
             if p.stem not in ("__init__", "index")]
    sizes = []
    for p in api_dir.glob("*.py"):
        if p.stem in ("__init__", "index"):
            continue
        try:
            sizes.append(len(p.read_text(encoding="utf-8").splitlines()))
        except Exception:
            sizes.append(0)

    tokens = []
    for name in names:
        tokens.extend(re.findall(r"[a-z]+", name.lower()))
    unique = len(set(tokens))
    total_tokens = len(tokens)
    diversity = unique / max(total_tokens, 1)

    # coupling: words shared across >= 2 modules
    word_count: Dict[str, int] = {}
    for tok in tokens:
        word_count[tok] = word_count.get(tok, 0) + 1
    shared = sum(1 for c in word_count.values() if c >= 2)

    size_complexity = min(100, sum(sizes) / max(len(sizes), 1) / 150 * 100)
    naming_complexity = diversity * 100
    coupling_complexity = min(100, shared / max(len(word_count), 1) * 100)

    index = round(
        size_complexity * 0.3 + naming_complexity * 0.4 + coupling_complexity * 0.3,
        1,
    )
    return {
        "modules": len(names),
        "avg_lines": round(sum(sizes) / max(len(sizes), 1), 1),
        "unique_words": unique,
        "total_tokens": total_tokens,
        "naming_diversity": round(diversity, 3),
        "shared_words": shared,
        "size_complexity": round(size_complexity, 1),
        "naming_complexity": round(naming_complexity, 1),
        "coupling_complexity": round(coupling_complexity, 1),
        "complexity_index": index,
    }


def handler(payload: dict = None, context: object = None) -> dict:
    stats = _module_stats()
    return {
        "module": "data_complexity",
        "prophecy": "fulfilled",
        "interpretation": (
            "low (<30): simple frontier, easily navigated; "
            "mid (30-70): rich frontiers; high (>70): labyrinth, "
            "gossip travels slowly"),
        **stats,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(handler(), indent=2))
