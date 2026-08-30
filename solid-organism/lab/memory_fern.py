#!/usr/bin/env python3
"""Memory Fern: fractal memory based on L-system growth rules.

A fern grows by applying simple rewrite rules recursively. Memory Fern
uses the same principle: a "seed" string undergoes recursive rewrites
through generations, creating a fractal memory structure. The final form
encodes the entire growth history in a single self-similar structure.

This is how DNA works: a simple sequence, recursively expressed, generates
a complete organism.

Usage:
    python3 memory_fern.py --seed "A" --generations 5
    python3 memory_fern.py --seed "F" --generations 6 --rule-type branching
"""
from __future__ import annotations

import argparse
import json
from typing import Any, Dict, List


# Standard L-system rules for different growth patterns
RULES = {
    "fern": {
        "F": "F[+F]F[-F]F",
        "+": "+",
        "-": "-",
        "[": "[",
        "]": "]",
        "A": "F[+A][-A]FA",
    },
    "sierpinski": {
        "F": "F-G-F",
        "G": "F+G+F",
        "+": "+",
        "-": "-",
    },
    "dragon": {
        "X": "X+YF+",
        "Y": "-FX-Y",
        "F": "F",
        "+": "+",
        "-": "-",
    },
    "branching": {
        "F": "FF",
        "X": "F+[[X]-X]-F[-FX]+X",
        "+": "+",
        "-": "-",
        "[": "[",
        "]": "]",
    },
    "kelp": {
        "F": "F[+F][-F]F[+F]",
        "+": "+",
        "-": "-",
        "[": "[",
        "]": "]",
    },
}


def grow(axiom: str, rules: Dict[str, str], generations: int) -> List[str]:
    """Apply L-system rewrite rules recursively."""
    current = axiom
    history = [current]
    for _ in range(generations):
        next_chars = []
        for char in current:
            next_chars.append(rules.get(char, char))
        current = "".join(next_chars)
        history.append(current)
    return history


def _count_brackets(text: str) -> Dict[str, int]:
    return {"open": text.count("["), "close": text.count("]"), "balanced": text.count("[") == text.count("]")}


def _fractal_dimension(text: str) -> float:
    """Estimate fractal dimension from growth ratio."""
    f_count = text.count("F")
    total = max(len(text), 1)
    if f_count == 0:
        return 0.0
    return round(f_count / total * 3.0, 3)


def analyze_growth(axiom: str, rule_type: str, generations: int) -> Dict[str, Any]:
    """Grow and analyze a memory fern."""
    rules = RULES.get(rule_type, RULES["fern"])
    history = grow(axiom, rules, generations)

    growth_curve = []
    for i, s in enumerate(history):
        brackets = _count_brackets(s)
        growth_curve.append({
            "generation": i,
            "length": len(s),
            "f_count": s.count("F"),
            "bracket_depth": brackets["open"],
            "balanced": brackets["balanced"],
            "fractal_dim": _fractal_dimension(s),
        })

    # Memory encoding: each generation encodes the history
    encoding = {
        "seed": axiom,
        "rule_type": rule_type,
        "generations": generations,
        "total_symbols": len(history[-1]),
        "growth_ratio": round(len(history[-1]) / max(len(axiom), 1), 1),
        "self_similarity": round(
            sum(1 for i in range(1, min(4, len(history)))
                if history[i] in history[i+1:min(i+3, len(history))]) / max(1, min(3, len(history)-1)),
            3
        ),
    }

    return {
        "growth_curve": growth_curve,
        "encoding": encoding,
        "final_form_preview": history[-1][:200] + ("..." if len(history[-1]) > 200 else ""),
        "growth_summary": {
            "generations": generations,
            "start_length": len(axiom),
            "end_length": len(history[-1]),
            "total_growth": f"{encoding['growth_ratio']}x",
        },
        "philosophy": (
            "A fern encodes its entire history in a single leaf. Each generation "
            "is a recursive application of the same rule. The complexity is not "
            "in the rules — it is in the recursion. Memory is not stored. "
            "Memory is grown."
        ),
    }


def main():
    ap = argparse.ArgumentParser(description="Memory Fern L-system growth")
    ap.add_argument("--seed", default="A", help="Starting axiom string")
    ap.add_argument("--rule-type", choices=list(RULES.keys()), default="fern")
    ap.add_argument("--generations", type=int, default=5)
    args = ap.parse_args()
    result = analyze_growth(args.seed, args.rule_type, args.generations)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
