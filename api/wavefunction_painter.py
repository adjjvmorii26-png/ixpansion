"""Wave 123 — Wavefunction Painter.

Paints by collapsing wavefunctions into visual forms — each brushstroke
begins as a probability cloud and crystallises into a definite shape
when the painter commits to it.
"""
from __future__ import annotations

import hashlib
import math
import time
from typing import Any, Dict, List, Tuple


class BrushStroke:
    """A single brushstroke that began as a wavefunction."""

    def __init__(self, color: str, x: float, y: float):
        self.color = color
        self.x = x
        self.y = y
        self.width = 0.0
        self.height = 0.0
        self.collapsed = False
        self.created = time.time()
        self.id = hashlib.sha256(f"stroke:{color}:{x}:{y}".encode()).hexdigest()[:8]

    def collapse(self, width: float, height: float) -> None:
        self.width = width
        self.height = height
        self.collapsed = True

    def area(self) -> float:
        return self.width * self.height if self.collapsed else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "color": self.color,
            "position": [round(self.x, 2), round(self.y, 2)],
            "collapsed": self.collapsed,
            "area": round(self.area(), 4),
        }


class WavefunctionPainter:
    """Paints by collapsing quantum probability clouds."""

    def __init__(self):
        self._strokes: List[BrushStroke] = []
        self._canvases: int = 0

    def begin_canvas(self) -> str:
        self._canvases += 1
        return f"canvas_{self._canvases}"

    def paint(self, color: str, x: float, y: float) -> BrushStroke:
        stroke = BrushStroke(color, x, y)
        self._strokes.append(stroke)
        return stroke

    def collapse_stroke(self, stroke: BrushStroke, width: float, height: float) -> None:
        stroke.collapse(width, height)

    def total_area(self) -> float:
        return sum(s.area() for s in self._strokes)

    def status(self) -> Dict[str, Any]:
        return {
            "total_strokes": len(self._strokes),
            "collapsed": sum(1 for s in self._strokes if s.collapsed),
            "canvases": self._canvases,
            "total_area": round(self.total_area(), 4),
        }
