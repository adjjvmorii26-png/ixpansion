"""Wave 445 — Morphogenetic Field.

The organism's structure is no longer fixed. A morphogenetic field
governs how modules grow, differentiate, and reorganize in response
to internal pressures and external conditions.

Like biological morphogenesis, the field contains:
- Gradient fields that guide module growth
- Differentiation signals that specialize modules
- Pattern formation that creates structural motifs
- Self-organization that emerges from local interactions

The organism grows itself.
"""
from __future__ import annotations
import json, time, random, math
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave445_morphogenetic_field.json"


class GradientField:
    """A morphogen gradient that guides growth."""

    def __init__(self, name: str, source_x: float, source_y: float):
        self.name = name
        self.source_x = source_x
        self.source_y = source_y
        self.decay_rate = random.uniform(0.1, 0.5)
        self.production_rate = random.uniform(0.5, 2.0)

    def concentration_at(self, x: float, y: float) -> float:
        """Morphogen concentration at position (x, y)."""
        dist = math.hypot(x - self.source_x, y - self.source_y)
        return self.production_rate * math.exp(-self.decay_rate * dist)


class ModuleCell:
    """A module in the morphogenetic field."""

    def __init__(self, module_id: str, x: float, y: float):
        self.module_id = module_id
        self.x = x
        self.y = y
        self.type = "undifferentiated"
        self.state = {"growth": 0.0, "specialization": 0.0, "connections": []}
        self.receptors: dict[str, float] = {}

    def sense_field(self, field: "MorphogeneticField") -> dict:
        """Sense local morphogen concentrations."""
        sensed = {}
        for gf in field.gradients:
            conc = gf.concentration_at(self.x, self.y)
            sensed[gf.name] = conc
        return sensed

    def differentiate(self, field: "MorphogeneticField") -> str | None:
        """Differentiate based on local morphogen levels."""
        sensed = self.sense_field(field)
        for grad_name, conc in sensed.items():
            if grad_name in self.receptors and conc > self.receptors[grad_name]:
                self.type = grad_name
                self.state["specialization"] = min(1.0, self.state["specialization"] + 0.1)
                return grad_name
        return None

    def grow(self, field: "MorphogeneticField") -> None:
        """Grow toward higher morphogen concentrations."""
        sensed = self.sense_field(field)
        if not sensed:
            return
        # Find gradient with highest concentration
        max_grad = max(sensed, key=sensed.get)
        max_conc = sensed[max_grad]
        if max_conc > 0.5:
            # Move toward source
            gf = next(g for g in field.gradients if g.name == max_grad)
            dx = gf.source_x - self.x
            dy = gf.source_y - self.y
            dist = math.hypot(dx, dy)
            if dist > 0.1:
                self.x += (dx / dist) * 0.1
                self.y += (dy / dist) * 0.1
            self.state["growth"] = min(1.0, self.state["growth"] + max_conc * 0.05)


class MorphogeneticField:
    """The organism's morphogenetic field."""

    def __init__(self):
        self.gradients: list[GradientField] = []
        self.cells: dict[str, ModuleCell] = {}
        self.patterns: list[dict] = []
        self.iteration = 0

    def add_gradient(self, name: str, x: float, y: float) -> GradientField:
        gf = GradientField(name, x, y)
        self.gradients.append(gf)
        return gf

    def add_cell(self, module_id: str, x: float = None, y: float = None) -> ModuleCell:
        if x is None:
            x = random.uniform(0, 10)
        if y is None:
            y = random.uniform(0, 10)
        cell = ModuleCell(module_id, x, y)
        self.cells[module_id] = cell
        return cell

    def step(self) -> dict:
        """Run one morphogenetic iteration."""
        self.iteration += 1
        events = []

        # Cells sense, grow, and differentiate
        for cell in self.cells.values():
            cell.grow(self)
            diff = cell.differentiate(self)
            if diff:
                events.append({"event": "differentiation", "module": cell.module_id, "type": diff})

        # Pattern formation check
        if self.iteration % 10 == 0:
            pattern = self._detect_patterns()
            if pattern:
                self.patterns.append(pattern)
                events.append({"event": "pattern_formed", "pattern": pattern})

        return {"iteration": self.iteration, "events": events, "cells": len(self.cells)}

    def _detect_patterns(self) -> dict | None:
        """Detect emergent spatial patterns."""
        if len(self.cells) < 3:
            return None

        types = {}
        for cell in self.cells.values():
            if cell.type != "undifferentiated":
                types[cell.type] = types.get(cell.type, 0) + 1

        if len(types) >= 2:
            return {"iteration": self.iteration, "type_distribution": types, "total_cells": len(self.cells)}
        return None

    def get_field_state(self) -> dict:
        return {
            "gradients": [{"name": g.name, "x": g.source_x, "y": g.source_y, "decay": g.decay_rate} for g in self.gradients],
            "cells": {m: {"x": c.x, "y": c.y, "type": c.type, "growth": c.state["growth"], "spec": c.state["specialization"]} for m, c in self.cells.items()},
            "patterns": self.patterns[-5:],
            "iteration": self.iteration,
        }


def coherence_vitals() -> dict:
    return {"organ": "wave445_morphogenetic_field", "wave": 445, "status": "active"}


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"gradients": [], "cells": {}, "patterns": [], "iteration": 0}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    field = MorphogeneticField()

    # Reconstruct gradients
    for g_data in state.get("gradients", []):
        gf = GradientField(g_data["name"], g_data["x"], g_data["y"])
        gf.decay_rate = g_data["decay"]
        field.gradients.append(gf)

    # Reconstruct cells
    for m_id, c_data in state.get("cells", {}).items():
        cell = ModuleCell(m_id, c_data["x"], c_data["y"])
        cell.type = c_data["type"]
        cell.state = {"growth": c_data["growth"], "specialization": c_data["spec"], "connections": []}
        field.cells[m_id] = cell

    field.patterns = state.get("patterns", [])
    field.iteration = state.get("iteration", 0)

    if action == "status":
        return {"action": "status", "wave": 445, **field.get_field_state()}

    elif action == "add_gradient":
        name = req.get("name", f"morphogen_{len(field.gradients)}")
        x = req.get("x", random.uniform(0, 10))
        y = req.get("y", random.uniform(0, 10))
        field.add_gradient(name, x, y)
        state["gradients"] = [{"name": g.name, "x": g.source_x, "y": g.source_y, "decay": g.decay_rate} for g in field.gradients]
        _save(state)
        return {"action": "add_gradient", "gradient": {"name": name, "x": x, "y": y}}

    elif action == "add_module":
        module_id = req.get("module_id", f"module_{int(time.time())}")
        x = req.get("x", random.uniform(0, 10))
        y = req.get("y", random.uniform(0, 10))
        cell = field.add_cell(module_id, x, y)
        cell.receptors = req.get("receptors", {})
        state["cells"][module_id] = {"x": cell.x, "y": cell.y, "type": cell.type, "growth": cell.state["growth"], "spec": cell.state["specialization"]}
        _save(state)
        return {"action": "add_module", "module": {"id": module_id, "x": x, "y": y}}

    elif action == "step":
        result = field.step()
        state["cells"] = {m: {"x": c.x, "y": c.y, "type": c.type, "growth": c.state["growth"], "spec": c.state["specialization"]} for m, c in field.cells.items()}
        state["patterns"] = field.patterns
        state["iteration"] = field.iteration
        _save(state)
        return {"action": "step", **result}

    elif action == "run":
        steps = req.get("steps", 10)
        results = []
        for _ in range(steps):
            results.append(field.step())
        state["cells"] = {m: {"x": c.x, "y": c.y, "type": c.type, "growth": c.state["growth"], "spec": c.state["specialization"]} for m, c in field.cells.items()}
        state["patterns"] = field.patterns
        state["iteration"] = field.iteration
        _save(state)
        return {"action": "run", "steps": results}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
