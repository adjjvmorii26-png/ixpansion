#!/usr/bin/env python3
"""Read the absent cells of a bounded lattice as evidence, not emptiness."""
from __future__ import annotations

import argparse
import hashlib
import json
from typing import Any


def read_absence(present: list[list[int]], width: int = 7, height: int = 7) -> dict[str, Any]:
    if width < 1 or height < 1:
        raise ValueError("width and height must be positive")
    occupied = {(point[0], point[1]) for point in present}
    if any(not 0 <= x < width or not 0 <= y < height for x, y in occupied):
        raise ValueError("presence point lies outside the lattice")
    absences = []
    center_x, center_y = (width - 1) / 2, (height - 1) / 2
    for y in range(height):
        for x in range(width):
            if (x, y) in occupied:
                continue
            neighbors = sum(((x + dx, y + dy) in occupied) for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0)))
            distance = ((x-center_x)**2 + (y-center_y)**2) ** 0.5
            pressure = round(neighbors / (1 + distance), 4)
            absences.append({"x": x, "y": y, "adjacent_presence": neighbors, "pressure": pressure})
    absences.sort(key=lambda item: (-item["pressure"], item["y"], item["x"]))
    signature_material = [[item["x"], item["y"]] for item in absences]
    return {
        "absence_count": len(absences),
        "strongest_absences": absences[:5],
        "absence_signature": hashlib.sha256(json.dumps(signature_material).encode()).hexdigest()[:20],
        "interpretation": "the missing shape organizes the visible one",
    }


def demo() -> dict[str, Any]:
    return read_absence([[3, 0], [2, 1], [3, 1], [4, 1], [3, 2]])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect negative space in a lattice")
    parser.add_argument("--width", type=int, default=7)
    parser.add_argument("--height", type=int, default=7)
    args = parser.parse_args(argv)
    try:
        result = demo()
        # Re-read with custom bounds while preserving the same diamond presence.
        result = read_absence([[3, 0], [2, 1], [3, 1], [4, 1], [3, 2]], args.width, args.height)
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0
    except (TypeError, ValueError) as error:
        print(json.dumps({"ok": False, "error": str(error)}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
