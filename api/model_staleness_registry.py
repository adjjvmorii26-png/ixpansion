"""Wave 620: Model Staleness Registry — keep test models from going stale.

Living registry for frontier and test models used by ALEPH / IXpansion.
Implements freshness tiers, drift detection, relative ranking, automatic
sunset rules, and knowledge-cutoff aware evaluation so older test models
do not silently degrade primary metrics.
"""
from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
REGISTRY_PATH = os.path.join(DATA_DIR, "wave620_model_staleness_registry.json")

# Freshness tiers
TIER_A = "A"  # live: < 90 days or continuously refreshed
TIER_B = "B"  # reference: older models for regression / historical only
TIER_C = "C"  # archive: frozen, never used for primary decisions

DEFAULT_SUNSET_DAYS = 90
DRIFT_THRESHOLD = 0.12  # relative score drop vs frontier reference


def _load() -> Dict[str, Any]:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(REGISTRY_PATH):
        seed = {
            "models": {
                "spacexai/grok-4.6": {
                    "id": "spacexai/grok-4.6",
                    "release_date": "2026-08-12",
                    "last_refresh": time.time(),
                    "tier": TIER_A,
                    "staleness_score": 0.0,
                    "knowledge_cutoff": "2026-07",
                    "notes": "current default frontier",
                }
            },
            "frontier_reference": "spacexai/grok-4.6",
            "probes": [],
            "last_sweep": None,
            "config": {
                "sunset_days": DEFAULT_SUNSET_DAYS,
                "drift_threshold": DRIFT_THRESHOLD,
            },
        }
        _save(seed)
        return seed
    with open(REGISTRY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(state: Dict[str, Any]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(REGISTRY_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def _days_since(ts: float) -> float:
    return (time.time() - ts) / 86400.0


def _compute_staleness(model: Dict[str, Any], config: Dict[str, Any]) -> float:
    """0.0 = fresh, 1.0 = fully stale."""
    last = model.get("last_refresh") or 0.0
    days = _days_since(last)
    sunset = float(config.get("sunset_days", DEFAULT_SUNSET_DAYS))
    base = min(1.0, days / max(sunset, 1.0))
    # mild penalty if never refreshed after release
    return round(base, 4)


def register_or_update(
    model_id: str,
    *,
    release_date: Optional[str] = None,
    knowledge_cutoff: Optional[str] = None,
    notes: str = "",
    force_tier: Optional[str] = None,
) -> Dict[str, Any]:
    state = _load()
    models = state.setdefault("models", {})
    entry = models.get(model_id, {"id": model_id})
    entry["id"] = model_id
    if release_date:
        entry["release_date"] = release_date
    if knowledge_cutoff:
        entry["knowledge_cutoff"] = knowledge_cutoff
    if notes:
        entry["notes"] = notes
    entry["last_refresh"] = time.time()
    entry["staleness_score"] = 0.0
    if force_tier in (TIER_A, TIER_B, TIER_C):
        entry["tier"] = force_tier
    else:
        entry["tier"] = TIER_A
    models[model_id] = entry
    _save(state)
    return {"status": "ok", "model": entry}


def probe_drift(
    model_id: str,
    relative_score: float,
    *,
    probe_name: str = "generic",
    knowledge_dependent: bool = False,
) -> Dict[str, Any]:
    """Record a staleness probe result. relative_score is performance vs current frontier (1.0 = equal)."""
    state = _load()
    models = state.get("models", {})
    if model_id not in models:
        return {"status": "error", "error": f"unknown model {model_id}"}
    config = state.get("config", {})
    threshold = float(config.get("drift_threshold", DRIFT_THRESHOLD))
    entry = models[model_id]
    entry["last_probe"] = time.time()
    entry["last_relative_score"] = relative_score
    entry["staleness_score"] = _compute_staleness(entry, config)

    drifted = relative_score < (1.0 - threshold)
    if drifted and entry.get("tier") == TIER_A:
        entry["tier"] = TIER_B
        entry["notes"] = (entry.get("notes") or "") + f" | auto-demoted after drift probe {probe_name}"

    probe = {
        "ts": time.time(),
        "model": model_id,
        "probe": probe_name,
        "relative_score": relative_score,
        "drifted": drifted,
        "knowledge_dependent": knowledge_dependent,
        "new_tier": entry["tier"],
    }
    state.setdefault("probes", []).append(probe)
    # keep last 200 probes
    state["probes"] = state["probes"][-200:]
    models[model_id] = entry
    _save(state)
    return {"status": "ok", "probe": probe, "model": entry}


def sunset_sweep() -> Dict[str, Any]:
    """Apply automatic sunset rules. Models past sunset_days without refresh move to B then C."""
    state = _load()
    config = state.get("config", {})
    sunset = float(config.get("sunset_days", DEFAULT_SUNSET_DAYS))
    models = state.get("models", {})
    changed = []
    for mid, entry in models.items():
        score = _compute_staleness(entry, config)
        entry["staleness_score"] = score
        days = _days_since(entry.get("last_refresh") or 0.0)
        old_tier = entry.get("tier", TIER_A)
        if days > sunset * 2 and old_tier != TIER_C:
            entry["tier"] = TIER_C
            changed.append({"id": mid, "from": old_tier, "to": TIER_C, "days": round(days, 1)})
        elif days > sunset and old_tier == TIER_A:
            entry["tier"] = TIER_B
            changed.append({"id": mid, "from": old_tier, "to": TIER_B, "days": round(days, 1)})
        models[mid] = entry
    state["last_sweep"] = time.time()
    _save(state)
    return {"status": "ok", "changed": changed, "models_checked": len(models)}


def list_models(tier: Optional[str] = None) -> Dict[str, Any]:
    state = _load()
    models = state.get("models", {})
    if tier:
        models = {k: v for k, v in models.items() if v.get("tier") == tier}
    return {
        "status": "ok",
        "frontier_reference": state.get("frontier_reference"),
        "count": len(models),
        "models": models,
        "last_sweep": state.get("last_sweep"),
    }


def set_frontier(model_id: str) -> Dict[str, Any]:
    state = _load()
    if model_id not in state.get("models", {}):
        return {"status": "error", "error": f"unknown model {model_id}"}
    state["frontier_reference"] = model_id
    # keep frontier in Tier A
    state["models"][model_id]["tier"] = TIER_A
    state["models"][model_id]["last_refresh"] = time.time()
    state["models"][model_id]["staleness_score"] = 0.0
    _save(state)
    return {"status": "ok", "frontier_reference": model_id}


def primary_allowed(model_id: str) -> bool:
    """True only if model is Tier A (safe for primary metrics / decisions)."""
    state = _load()
    entry = state.get("models", {}).get(model_id)
    if not entry:
        return False
    return entry.get("tier") == TIER_A


def coherence_vitals() -> dict:
    state = _load()
    models = state.get("models", {})
    tiers = {TIER_A: 0, TIER_B: 0, TIER_C: 0}
    for m in models.values():
        t = m.get("tier", TIER_A)
        if t in tiers:
            tiers[t] += 1
    return {
        "layer": "intelligence",
        "status": "active",
        "wave": "620",
        "module": "model_staleness_registry",
        "models_tracked": len(models),
        "tier_A": tiers[TIER_A],
        "tier_B": tiers[TIER_B],
        "tier_C": tiers[TIER_C],
        "frontier": state.get("frontier_reference"),
    }


def resonates_with() -> list:
    return ["gateway_ink", "ai_gateway", "oracle_meter", "cognition_forge"]


def handler(payload=None, context=None):
    payload = payload or {}
    action = payload.get("action") or "status"

    if action == "status":
        return coherence_vitals()

    if action == "list":
        return list_models(payload.get("tier"))

    if action == "register":
        mid = payload.get("model") or payload.get("id")
        if not mid:
            return {"status": "error", "error": "model required"}
        return register_or_update(
            mid,
            release_date=payload.get("release_date"),
            knowledge_cutoff=payload.get("knowledge_cutoff"),
            notes=payload.get("notes", ""),
            force_tier=payload.get("tier"),
        )

    if action == "probe":
        mid = payload.get("model")
        score = payload.get("relative_score")
        if mid is None or score is None:
            return {"status": "error", "error": "model and relative_score required"}
        return probe_drift(
            mid,
            float(score),
            probe_name=str(payload.get("probe_name") or "generic"),
            knowledge_dependent=bool(payload.get("knowledge_dependent")),
        )

    if action == "sunset":
        return sunset_sweep()

    if action == "set_frontier":
        mid = payload.get("model")
        if not mid:
            return {"status": "error", "error": "model required"}
        return set_frontier(mid)

    if action == "primary_allowed":
        mid = payload.get("model")
        return {"status": "ok", "model": mid, "allowed": primary_allowed(mid or "")}

    return {
        "status": "error",
        "error": f"unknown action: {action}",
        "available": ["status", "list", "register", "probe", "sunset", "set_frontier", "primary_allowed"],
    }
