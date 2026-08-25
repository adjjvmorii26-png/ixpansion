from __future__ import annotations
"""Alchemy Transmutation — transforms data between incompatible types.

Like medieval alchemists trying to turn lead into gold, this module
attempts to transform data between types that shouldn't be compatible.
It discovers unexpected conversion paths and measures "transmutation
purity" — how much of the original meaning survives.
"""
import math
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

@dataclass
class TransmutationResult:
    source_type: str
    target_type: str
    source_value: Any
    target_value: Any
    purity: float
    path: List[str]
    success: bool

class AlchemyEngine:
    ELEMENTS = {
        "str": {"symbol": "☿", "quality": "mutable"},
        "int": {"symbol": "♄", "quality": "stable"},
        "float": {"symbol": "☽", "quality": "flowing"},
        "list": {"symbol": "♃", "quality": "collective"},
        "dict": {"symbol": "☉", "quality": "structured"},
        "bool": {"symbol": "♂", "quality": "binary"},
        "tuple": {"symbol": "♆", "quality": "immutable"},
        "set": {"symbol": "⊕", "quality": "unique"},
    }

    def __init__(self):
        self.transmutations: List[TransmutationResult] = []
        self.known_paths: Dict[str, List[str]] = {}

    def _detect_type(self, value: Any) -> str:
        return type(value).__name__

    def _transmute(self, value: Any, target_type: str) -> TransmutationResult:
        source_type = self._detect_type(value)
        path = [f"{source_type}→{target_type}"]
        try:
            if target_type == "str":
                target = str(value)
                purity = 0.9
            elif target_type == "int":
                if isinstance(value, str):
                    target = int(''.join(filter(str.isdigit, value)) or '0')
                    purity = 0.5
                elif isinstance(value, float):
                    target = int(value)
                    purity = 0.8
                elif isinstance(value, bool):
                    target = int(value)
                    purity = 1.0
                else:
                    target = int(value)
                    purity = 0.7
            elif target_type == "float":
                if isinstance(value, str):
                    digits = ''.join(c for c in value if c.isdigit() or c == '.')
                    target = float(digits) if digits else 0.0
                    purity = 0.4
                else:
                    target = float(value)
                    purity = 0.7
            elif target_type == "list":
                if isinstance(value, str):
                    target = list(value)
                    purity = 0.8
                elif isinstance(value, (int, float)):
                    target = [value]
                    purity = 0.6
                elif isinstance(value, dict):
                    target = list(value.items())
                    purity = 0.5
                else:
                    target = list(value)
                    purity = 0.7
            elif target_type == "dict":
                if isinstance(value, str):
                    target = {"value": value, "hash": hashlib.md5(value.encode()).hexdigest()[:8]}
                    purity = 0.4
                elif isinstance(value, list):
                    target = {str(i): v for i, v in enumerate(value)}
                    purity = 0.6
                else:
                    target = {"value": value}
                    purity = 0.5
            elif target_type == "bool":
                if isinstance(value, (int, float)):
                    target = bool(value)
                    purity = 0.9
                elif isinstance(value, str):
                    target = len(value) > 0
                    purity = 0.6
                else:
                    target = bool(value)
                    purity = 0.7
            elif target_type == "tuple":
                if isinstance(value, (list, set)):
                    target = tuple(value)
                    purity = 0.9
                elif isinstance(value, str):
                    target = tuple(value)
                    purity = 0.7
                else:
                    target = (value,)
                    purity = 0.6
            elif target_type == "set":
                if isinstance(value, (list, tuple)):
                    target = set(value)
                    purity = 0.8
                elif isinstance(value, str):
                    target = set(value)
                    purity = 0.7
                else:
                    target = {value}
                    purity = 0.5
            else:
                target = value
                purity = 1.0
                path.append("identity")
        except Exception as e:
            target = None
            purity = 0.0
            path.append(f"error: {str(e)[:50]}")

        result = TransmutationResult(
            source_type=source_type, target_type=target_type,
            source_value=value, target_value=target,
            purity=purity, path=path, success=purity > 0,
        )
        self.transmutations.append(result)
        key = f"{source_type}→{target_type}"
        if key not in self.known_paths:
            self.known_paths[key] = path
        return result

    def transmute_chain(self, value: Any, chain: List[str]) -> List[TransmutationResult]:
        results = []
        current = value
        for target_type in chain:
            result = self._transmute(current, target_type)
            results.append(result)
            current = result.target_value
            if not result.success:
                break
        return results

    def purity_report(self) -> Dict:
        successful = [t for t in self.transmutations if t.success]
        return {
            "total_transmutations": len(self.transmutations),
            "successful": len(successful),
            "avg_purity": sum(t.purity for t in successful) / max(len(successful), 1),
            "paths_discovered": len(self.known_paths),
        }


def demo():
    alchemy = AlchemyEngine()
    print("=== Alchemy Transmutation Engine ===")

    tests = [
        ("hello", "int"), (42, "str"), (3.14, "int"),
        ([1, 2, 3], "str"), ({"a": 1}, "list"),
        ("12345", "float"), (True, "int"),
    ]
    for value, target in tests:
        result = alchemy._transmute(value, target)
        status = "✓" if result.success else "✗"
        print(f"  {status} {type(value).__name__}({value!r}) → {target}: "
              f"{result.target_value!r} (purity={result.purity:.2f})")

    print("\nChain transmutation: str → list → tuple → str")
    chain = alchemy.transmute_chain("hello", ["list", "tuple", "str"])
    for r in chain:
        print(f"  {r.source_type} → {r.target_type}: {r.target_value!r} (purity={r.purity:.2f})")

    report = alchemy.purity_report()
    print(f"\nReport: {report['successful']}/{report['total_transmutations']} "
          f"successful, avg purity={report['avg_purity']:.2f}")

    return report


if __name__ == "__main__":
    demo()
