"""Coherence Regulator — the living backbone of the frontier.

Every module in this ecosystem is a cell in a larger organism. The Coherence
Regulator is the governance layer that lets them live together: it discovers
modules, reads their vital signs, measures how aligned the whole system is,
and — when coherence drifts — issues regulation.

THE PLUG-IN PROTOCOL
====================
Any module in api/ can join the living system by implementing ONE function:

    def coherence_vitals() -> dict:
        # Return a snapshot of this module's state.
        # Keys are metric names; values are numbers (higher = healthier).
        # Optional: {"metric": value, "setpoint": target, "weight": importance}
        return {
            "balance": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
            "throughput": 42,
        }

The regulator scans api/*.py at pulse time and discovers these modules
automatically. No central registry, no manual wiring — drop a module in,
implement coherence_vitals(), and it is alive in the system.

WHAT THE REGULATOR DOES
=======================
1. DISCOVER  — find all modules implementing coherence_vitals()
2. PULSE     — call their vital signs, compute aggregate coherence
3. MEMORY    — persist a coherence history so drift is visible over time
4. REGULATE  — when coherence drops below tolerance, emit advisories:
               warming, rebalancing, or quarantine suggestions
5. REPORT    — expose the full living-state to the gateway + dashboard

Usage:
  GET  /api/coherence_regulator?read=1        — current coherence reading
  POST /api/coherence_regulator {"pulse": 1}  — trigger a live pulse
  GET  /api/coherence_regulator?modules=1     — list living modules
  GET  /api/coherence_regulator?history=10    — coherence history
"""
from __future__ import annotations

import importlib
import json
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

STATE_FILE = ROOT / ".runtime" / "coherence_regulator.json"

# System-wide coherence targets (the organism's setpoints)
SYSTEM_SETPOINTS = {
    "module_health": 0.75,
    "module_resonance": 0.7,
    "ecosystem_diversity": 0.6,
    "frontier_alignment": 0.8,
}

COHERENCE_TOLERANCE = 0.7          # below this → advisories fire
REGULATION_THRESHOLD = 0.5         # below this → strong regulation
PULSE_INTERVAL = 60.0              # seconds between automatic pulses
ECOSYSTEM_TARGET = 24            # living modules = a full bloom


# ---------------------------------------------------------------------------
# Serverless resilience
# ---------------------------------------------------------------------------

# In a serverless sandbox (Vercel), only the invoked module is present on the
# filesystem, so globbing api/*.py finds nothing.  To keep the living system
# alive even there, we embed a static manifest of known living modules.  The
# regulator attempts to import & pulse each one; modules that load get reported.
# Keep this list in sync as new modules implement coherence_vitals().
KNOWN_LIVING_MODULES: List[str] = [
    "chronicle_storyteller",
    "constellation_cartographer",
    "dream_sequencer",
    "frontier_stream",
    "hex_tool",
    "organism_index",
    "reality_weaver",
    "reflection_pool",
    "sound_cauldron",
    "synesthesia",
    "thought_meteorology",
]



# ---------------------------------------------------------------------------
# State (living memory)
# ---------------------------------------------------------------------------

def _load_state() -> Dict[str, Any]:
    if not STATE_FILE.exists():
        return {"modules": {}, "history": [], "pulses": 0, "created_at": time.time()}
    try:
        return json.loads(STATE_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return {"modules": {}, "history": [], "pulses": 0, "created_at": time.time()}


def _save_state(state: Dict[str, Any]) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


# ---------------------------------------------------------------------------
# Discovery — the living-system plug-in
# ---------------------------------------------------------------------------

def _candidate_modules() -> List[str]:
    """Living candidates: modules whose *source* defines coherence_vitals().

    Uses a fast text scan so we never import dormant modules just to check.
    In a serverless sandbox (no api/ dir on disk) we fall back to the static
    manifest, then verify each name with an import attempt at pulse time.
    """
    api_dir = ROOT / "api"
    try:
        scanned = sorted(p.stem for p in api_dir.glob("*.py"))
    except (OSError, ValueError):
        scanned = []
    if not scanned:
        return list(KNOWN_LIVING_MODULES)
    living = []
    for stem in scanned:
        if stem in ("__init__", "index", "unified_router", "coherence_regulator"):
            continue
        path = api_dir / f"{stem}.py"
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        if "def coherence_vitals" in text or "coherence_vitals =" in text:
            living.append(stem)
    return living


def _normalize_vitals(raw: Any, module_name: str) -> Dict[str, Any]:
    """Coerce whatever coherence_vitals() returns into a flat metric map."""
    metrics: Dict[str, Dict[str, Any]] = {}
    if not isinstance(raw, dict):
        return metrics
    for key, val in raw.items():
        if isinstance(val, dict) and "value" in val:
            metrics[key] = {
                "value": float(val.get("value", 0)),
                "setpoint": float(val.get("setpoint", 0.8)),
                "weight": float(val.get("weight", 1.0)),
            }
        elif isinstance(val, (int, float)):
            metrics[key] = {
                "value": float(val),
                "setpoint": 0.8,  # default health target
                "weight": 1.0,
            }
    return metrics


def _call_vitals(module_name: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    """Call a module's coherence_vitals() safely."""
    try:
        module = importlib.import_module(module_name)
        fn: Optional[Callable] = getattr(module, "coherence_vitals", None)
        if fn is None:
            return None, "no coherence_vitals"
        raw = fn()
        return _normalize_vitals(raw, module_name), None
    except Exception as e:  # pragma: no cover - defensive
        return None, f"error: {e}"


def discover_modules(force_pulse: bool = False) -> Dict[str, Any]:
    """Find every module with coherence_vitals(). Returns the living registry."""
    state = _load_state()
    modules = state.setdefault("modules", {})

    discovered = []
    for name in _candidate_modules():
        vitals, err = _call_vitals(name)
        if vitals is None:
            continue  # not a living module — not part of the system yet
        modules[name] = {
            "first_seen": modules.get(name, {}).get("first_seen", time.time()),
            "last_pulse": time.time(),
            "metris": vitals,
            "health": _module_health(vitals),
        }
        discovered.append(name)

    _save_state(state)
    return {"living_modules": sorted(discovered), "count": len(discovered)}


def _module_health(vitals: Dict[str, Dict[str, Any]]) -> float:
    """Aggregate a module's metrics into a 0..1 health score."""
    if not vitals:
        return 0.0
    total_weight = 0.0
    weighted = 0.0
    for metric in vitals.values():
        value = metric.get("value", 0.0)
        setpoint = metric.get("setpoint", 0.8) or 0.8
        weight = metric.get("weight", 1.0) or 1.0
        # health = proximity to setpoint, higher value toward setpoint is better
        if setpoint > 0:
            health = min(1.0, value / setpoint)
        else:
            health = min(1.0, max(0.0, 1.0 - abs(value)))  # negative setpoint = avoid
        weighted += health * weight
        total_weight += weight
    return round(weighted / max(total_weight, 0.001), 4)


# ---------------------------------------------------------------------------
# Coherence engine
# ---------------------------------------------------------------------------

def measure_coherence(module_states: Dict[str, Any] = None) -> Dict[str, Any]:
    """Compute the whole-system coherence from module states."""
    state = _load_state()
    modules = module_states if module_states is not None else state.get("modules", {})

    if not modules:
        return {"coherence": 0.0, "components": {}, "living_modules": 0, "status": "dormant"}

    # 1. module health — average health across living modules
    healths = [m.get("health", 0.0) for m in modules.values() if m.get("health") is not None]
    module_health = sum(healths) / max(len(healths), 1)

    # 2. resonance — fraction of module pairs that share at least one metric
    #    (two modules resonate when they speak the same vital-sign language)
    module_list = list(modules.keys())
    pairs = 0
    resonating_pairs = 0
    for i in range(len(module_list)):
        for j in range(i + 1, len(module_list)):
            m1 = set((modules[module_list[i]].get("metris") or {}).keys())
            m2 = set((modules[module_list[j]].get("metris") or {}).keys())
            pairs += 1
            if m1 & m2:
                resonating_pairs += 1
    resonance = resonating_pairs / max(pairs, 1)

    # 3. diversity — how far the living system is toward a full bloom.
    #    Not a fixed fraction of every api/*.py file (dozens of tools exist
    #    outside the organism); it measures progress toward ECOSYSTEM_TARGET
    #    living modules, so the metric is directional and reachable.
    living = len(modules)
    candidates = len(_candidate_modules())
    diversity = min(1.0, living / max(ECOSYSTEM_TARGET, 1))

    # 4. frontier alignment — how well module healths cluster near system setpoints
    deviations = [abs(h - SYSTEM_SETPOINTS["module_health"]) for h in healths]
    alignment = 1.0 - (sum(deviations) / max(len(deviations), 1))

    components = {
        "module_health": round(module_health, 4),
        "module_resonance": round(resonance, 4),
        "ecosystem_diversity": round(diversity, 4),
        "frontier_alignment": round(max(0.0, min(1.0, alignment)), 4),
    }

    # weighted aggregate (setpoints define ideal targets)
    weighted = 0.0
    total_w = 0.0
    for key, value in components.items():
        target = SYSTEM_SETPOINTS.get(key, 0.7)
        weight = 1.0
        weighted += min(1.0, value / max(target, 0.01)) * weight
        total_w += weight
    coherence = round(weighted / max(total_w, 0.001), 4)

    return {
        "coherence": coherence,
        "components": components,
        "living_modules": living,
        "total_candidates": candidates,
        "status": _status_label(coherence),
    }


def _status_label(coherence: float) -> str:
    if coherence >= 0.85:
        return "resonant"
    if coherence >= COHERENCE_TOLERANCE:
        return "coherent"
    if coherence >= REGULATION_THRESHOLD:
        return "drifting"
    return "fracturing"


# ---------------------------------------------------------------------------
# Regulation
# ---------------------------------------------------------------------------

def _advisories(reading: Dict[str, Any]) -> List[str]:
    """Generate regulation advisories from a coherence reading."""
    advisories = []
    coherence = reading["coherence"]
    components = reading["components"]

    if coherence >= 0.85:
        advisories.append("No regulation needed. The frontier is in resonance.")
        return advisories

    if components.get("module_health", 1.0) < SYSTEM_SETPOINTS["module_health"]:
        advisories.append(
            "WARMING: module health below target. Consider adding coherence_vitals() "
            "reporting to more modules, or increasing setpoint fidelity."
        )
    if components.get("module_resonance", 1.0) < SYSTEM_SETPOINTS["module_resonance"]:
        advisories.append(
            "REBALANCING: low resonance between modules. Shared metric vocabularies "
            "help modules resonate — align your coherence_vitals() metric names."
        )
    if components.get("ecosystem_diversity", 1.0) < SYSTEM_SETPOINTS["ecosystem_diversity"]:
        advisories.append(
            "DIVERSITY: few modules are currently living. Implement coherence_vitals() "
            "in dormant modules to raise ecosystem diversity."
        )
    if coherence < REGULATION_THRESHOLD:
        advisories.append(
            "QUARANTINE SUGGESTION: coherence critically low. Modules with health "
            "below 0.3 should be reviewed or reset before they drag the system down."
        )
    if not advisories:
        advisories.append(
            "LIGHT TOUCH: coherence is within tolerance. Continue steady regulation."
        )
    return advisories


def regulate() -> Dict[str, Any]:
    """Run one full regulation cycle: discover → pulse → measure → advise."""
    discovered = discover_modules(force_pulse=True)
    state = _load_state()
    reading = measure_coherence(state.get("modules", {}))
    advisories = _advisories(reading)

    # Record into living memory
    history = state.setdefault("history", [])
    history.append({
        "ts": time.time(),
        "coherence": reading["coherence"],
        "components": reading["components"],
        "living_modules": reading["living_modules"],
        "advisories": advisories,
    })
    state["history"] = history[-200:]  # keep a generous living memory
    state["pulses"] = state.get("pulses", 0) + 1
    _save_state(state)

    reading["pulse"] = state["pulses"]
    reading["advisories"] = advisories
    reading["discovered"] = discovered
    reading["philosophy"] = (
        "A living system is not a collection of working parts. It is a web of "
        "mutual awareness. The regulator does not command — it listens, measures, "
        "and invites each module to keep the whole alive."
    )
    return reading


# ---------------------------------------------------------------------------
# Handler API
# ---------------------------------------------------------------------------

def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}

    # Pulse: force a regulation cycle
    if payload.get("pulse") or payload == {"read": None} or "pulse" in payload:
        return regulate()

    # Read-only current reading (no new pulse)
    reading = measure_coherence()

    # List living modules
    if payload.get("modules") or payload.get("list"):
        modules = _load_state().get("modules", {})
        return {
            "action": "modules",
            "living_modules": sorted(modules.keys()),
            "count": len(modules),
            "dossiers": {
                name: {"health": m.get("health"), "metrics": list((m.get("metris") or {}).keys()),
                       "first_seen": m.get("first_seen")}
                for name, m in sorted(modules.items())
            },
        }

    # History
    if payload.get("history"):
        limit = int(payload["history"])
        history = _load_state().get("history", [])[-limit:]
        return {"action": "history", "limit": limit, "entries": history}

    # Full reading
    reading["action"] = "read"
    reading["setpoints"] = SYSTEM_SETPOINTS
    reading["plug_in_protocol"] = (
        "Implement coherence_vitals() in any api/*.py module to join the living "
        "system. Return {metric: number} or {metric: {value, setpoint, weight}}."
    )
    return reading


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Coherence Regulator")
    ap.add_argument("--pulse", action="store_true", help="Run a full regulation cycle")
    ap.add_argument("--read", action="store_true", help="Current coherence reading")
    ap.add_argument("--modules", action="store_true", help="List living modules")
    ap.add_argument("--history", type=int, default=0, help="Show coherence history")
    args = ap.parse_args()

    if args.pulse:
        print(json.dumps(regulate(), indent=2, default=str))
    elif args.modules:
        print(json.dumps(handler({"modules": 1}), indent=2, default=str))
    elif args.history:
        print(json.dumps(handler({"history": args.history}), indent=2, default=str))
    else:
        print(json.dumps(handler({"read": 1}), indent=2, default=str))
