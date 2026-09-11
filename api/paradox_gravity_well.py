from __future__ import annotations
"""Paradox Gravity Well — paradoxes attract each other.

Models paradoxes as massive objects in a conceptual space. When two paradoxes
are close enough, they merge into a super-paradox. When they are too distant,
they decay into resolved contradictions. Gravity = f(mass, inverse_distance).
"""
import time
import hashlib
import math
from typing import Any

_state: dict[str, Any] = {
    "paradoxes": [],
    "mergers": [],
    "decays": [],
    "gravitational_constant": 0.618,
    "well_depth": 0.0,
    "next_id": 1,
}

def coherence_vitals() -> dict[str, Any]:
    active = [p for p in _state["paradoxes"] if p["status"] == "active"]
    return {
        "organs": "paradox_gravity_well",
        "health": 0.87,
        "resonance_depth": "paradoxical",
        "active_paradoxes": len(active),
        "well_depth": round(_state["well_depth"], 3),
        "merger_count": len(_state["mergers"]),
    }

def handler(req: dict[str, Any]) -> dict[str, Any]:
    action = req.get("action", "inject")
    if action == "inject":
        return _inject_paradox(req.get("name", "unnamed"), req.get("mass", 1.0))
    elif action == "merge":
        return _try_merge(req.get("p1"), req.get("p2"))
    elif action == "decay":
        return _decay(req.get("p_id"))
    elif action == "field":
        return _gravity_field()
    elif action == "interactions":
        return _get_interactions()
    elif action == "tick":
        return _physics_tick()
    return {"error": f"Unknown action: {action}"}

def _inject_paradox(name: str, mass: float) -> dict[str, Any]:
    pid = _state["next_id"]
    _state["next_id"] += 1
    h = hashlib.sha256(f"{name}:{time.time_ns()}".encode()).hexdigest()
    paradox = {
        "id": pid,
        "name": name,
        "mass": min(mass, 100.0),
        "position": {
            "x": (int(h[:4], 16) % 1000 - 500) / 100.0,
            "y": (int(h[4:8], 16) % 1000 - 500) / 100.0,
            "z": (int(h[8:12], 16) % 1000 - 500) / 100.0,
        },
        "velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
        "status": "active",
        "created": time.time(),
        "age": 0,
        "complexity": round(0.3 + (int(h[12:16], 16) % 700) / 1000.0, 3),
    }
    _state["paradoxes"].append(paradox)
    _recalc_well_depth()
    return {"paradox_injected": paradox}

def _try_merge(p1_id: int, p2_id: int) -> dict[str, Any]:
    if not p1_id or not p2_id:
        return {"error": "Need two paradox IDs"}
    p1 = next((p for p in _state["paradoxes"] if p["id"] == p1_id), None)
    p2 = next((p for p in _state["paradoxes"] if p["id"] == p2_id), None)
    if not p1 or not p2:
        return {"error": "Paradox not found"}
    if p1["status"] != "active" or p2["status"] != "active":
        return {"error": "Both paradoxes must be active"}
    dist = math.sqrt(sum((p1["position"][k] - p2["position"][k]) ** 2 for k in ["x", "y", "z"]))
    threshold = 5.0
    if dist > threshold:
        return {"status": "too_far", "distance": round(dist, 2), "threshold": threshold}
    merged_mass = p1["mass"] + p2["mass"]
    merged_pos = {k: (p1["position"][k] + p2["position"][k]) / 2 for k in ["x", "y", "z"]}
    merged = {
        "id": _state["next_id"],
        "name": f"super({p1['name']},{p2['name']})",
        "mass": merged_mass,
        "position": {k: round(v, 2) for k, v in merged_pos.items()},
        "velocity": {"x": 0.0, "y": 0.0, "z": 0.0},
        "status": "active",
        "created": time.time(),
        "age": 0,
        "complexity": round(min(1.0, (p1["complexity"] + p2["complexity"]) / 2 * 1.3), 3),
    }
    _state["next_id"] += 1
    p1["status"] = "merged_into"
    p2["status"] = "merged_into"
    merger = {"p1": p1_id, "p2": p2_id, "result_id": merged["id"], "ts": time.time(), "mass": merged_mass}
    _state["mergers"].append(merger)
    _state["paradoxes"].append(merged)
    _recalc_well_depth()
    return {"status": "merged", "super_paradox": merged}

def _decay(p_id: int) -> dict[str, Any]:
    if not p_id:
        return {"error": "Need paradox ID"}
    p = next((p for p in _state["paradoxes"] if p["id"] == p_id), None)
    if not p:
        return {"error": "Paradox not found"}
    if p["status"] != "active":
        return {"error": "Paradox not active"}
    p["status"] = "decayed"
    _state["decays"].append({"id": p_id, "ts": time.time(), "mass_lost": p["mass"]})
    _recalc_well_depth()
    return {"status": "decayed", "paradox": p}

def _gravity_field() -> dict[str, Any]:
    active = [p for p in _state["paradoxes"] if p["status"] == "active"]
    G = _state["gravitational_constant"]
    forces = []
    for i, p1 in enumerate(active):
        total_force = 0.0
        for j, p2 in enumerate(active):
            if i == j:
                continue
            dist = max(0.1, math.sqrt(sum((p1["position"][k] - p2["position"][k]) ** 2 for k in ["x", "y", "z"])))
            force = G * p1["mass"] * p2["mass"] / (dist ** 2)
            total_force += force
        forces.append({"id": p1["id"], "name": p1["name"], "force_on": round(total_force, 3)})
    return {
        "field": forces,
        "gravitational_constant": G,
        "well_depth": round(_state["well_depth"], 3),
    }

def _get_interactions() -> dict[str, Any]:
    return {
        "mergers": _state["mergers"][-10:],
        "decays": _state["decays"][-10:],
        "total_mergers": len(_state["mergers"]),
        "total_decays": len(_state["decays"]),
    }

def _physics_tick() -> dict[str, Any]:
    active = [p for p in _state["paradoxes"] if p["status"] == "active"]
    G = _state["gravitational_constant"]
    for i, p in enumerate(active):
        p["age"] += 1
        total_force_vec = {"x": 0.0, "y": 0.0, "z": 0.0}
        for j, other in enumerate(active):
            if i == j:
                continue
            diff = {k: other["position"][k] - p["position"][k] for k in ["x", "y", "z"]}
            dist = max(0.1, math.sqrt(sum(d ** 2 for d in diff.values())))
            F = G * p["mass"] * other["mass"] / (dist ** 2)
            for k in ["x", "y", "z"]:
                total_force_vec[k] += F * (diff[k] / dist)
        for k in ["x", "y", "z"]:
            p["velocity"][k] = round(p["velocity"][k] + total_force_vec[k] * 0.01, 4)
            p["position"][k] = round(p["position"][k] + p["velocity"][k], 4)
    _recalc_well_depth()
    return {"status": "ticked", "active_count": len(active)}

def _recalc_well_depth():
    active = [p for p in _state["paradoxes"] if p["status"] == "active"]
    total_mass = sum(p["mass"] for p in active)
    _state["well_depth"] = total_mass * _state["gravitational_constant"]

def resonates_with(other: str) -> float:
    return {
        "self_reference_engine": 0.93,
        "entropy_cartographer": 0.81,
        "temporal_fracture_engine": 0.78,
        "coherence_regulator_v2": 0.65,
        "dream_synthesis_protocol": 0.70,
    }.get(other, 0.20)
