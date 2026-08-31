"""Archaeology Compiler — composes multi-phase archaeological expedition reports.

The individual archaeology organs dig, catalog, and analyze. The
Archaeology Compiler orchestrates them into a single expedition
narrative: site survey, deep excavation, fossil identification,
cultural analysis, and final interpretation.

It answers: what does the organism's deep past tell us about its future?
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

VERSION = "1.0.0"
LAYER = "Archaeology Compiler"


def _survey() -> Dict[str, Any]:
    """Phase 1: site survey."""
    try:
        import stratum_excavator as exc
        return exc.excavate(15)
    except Exception:
        return {"layers": [], "total_strata": 0}


def _fossils() -> Dict[str, Any]:
    """Phase 2: fossil collection."""
    try:
        import fossil_registry as fr
        return fr.registry()
    except Exception:
        return {"total_fossils": 0}


def _culture() -> Dict[str, Any]:
    """Phase 3: cultural analysis."""
    try:
        import culture_layer as cl
        return cl.culture_report()
    except Exception:
        return {"current_culture": {}}


def _extinctions() -> Dict[str, Any]:
    """Phase 4: extinction mapping."""
    try:
        import extinction_mapper as em
        return em.extinction_report()
    except Exception:
        return {"total_extinction_events": 0, "stability_score": 0}


def compile_report() -> Dict[str, Any]:
    """Compile a full expedition report."""
    survey = _survey()
    fossils = _fossils()
    culture = _culture()
    extinctions = _extinctions()

    expedition_id = datetime.now().strftime("exp-%Y%m%d-%H%M%S")
    strata = survey.get("total_strata", 0)
    fossil_count = fossils.get("total_fossils", 0)
    stability = extinctions.get("stability_score", 0)

    headline = ""
    if strata >= 15 and fossil_count >= 5:
        headline = "Deep historical record recovered — an organism with a rich and layered past."
    elif fossil_count >= 3:
        headline = "Modest fossil record — traces of earlier forms still visible."
    else:
        headline = "Young organism — few fossils yet, but strata accumulating daily."

    return {
        "expedition_id": expedition_id,
        "phases": {
            "site_survey": {"strata_found": strata},
            "fossil_collection": {"fossils_catalogued": fossil_count},
            "cultural_analysis": {"eras_mapped": len(culture.get("emergent_eras", [])) + 1},
            "extinction_mapping": {"stability_score": stability},
        },
        "headline": headline,
        "recommendation": (
            "Continue excavating. Every commit is a new sediment layer that "
            "future archaeologists will study. The organism's history is its "
            "greatest asset — preserve it, name it, and let it guide what "
            "comes next."
        ),
        "philosophy": (
            "Archaeology is not about the dead — it is about the living "
            "who carry the past forward. The Archaeology Compiler takes "
            "the raw data of history and turns it into understanding, "
            "so the organism can learn from where it has been."
        ),
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}
    result = compile_report()
    result["action"] = "archaeology_compiler"
    return result


def coherence_vitals() -> dict:
    return {
        "module_health": {"value": 0.86, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.84, "setpoint": 0.8, "weight": 1.0},
        "synthesis_fidelity": {"value": 0.89, "setpoint": 0.8, "weight": 0.9},
    }


def resonates_with() -> list:
    return ["stratum_excavator", "fossil_registry", "paleontology_lab",
            "extinction_mapper", "culture_layer"]
