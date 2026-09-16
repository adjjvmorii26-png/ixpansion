"""Circuit breaker — organism-wide coherence floor check.

Aggregates coherence_vitals from all recent wave organs (753-760) and
fails the test if any organ's resonance drops below the safety threshold.
This prevents silent organism degradation from propagating to production.
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "api"))

RESONANCE_FLOOR = 0.30
WAVE_ORGANS = [
    ("api.wave753_resonance_braid", "Wave 753 — Resonance Braid"),
    ("api.wave754_mycelial_weather", "Wave 754 — Mycelial Weather"),
    ("api.wave755_threshold_engine", "Wave 755 — Threshold Engine"),
    ("api.wave756_liminal_field", "Wave 756 — Liminal Field"),
    ("api.wave757_axiom_mutator", "Wave 757 — Axiom Mutator"),
    ("api.wave758_continuity_weaver", "Wave 758 — Continuity Weaver"),
    ("api.wave759_transcendence_journal", "Wave 759 — Transcendence Journal"),
    ("api.wave760_mutation_engine", "Wave 760 — Mutation Engine"),
]


def test_circuit_breaker_coherence_floor():
    """Every recent organ must maintain resonance above the safety floor."""
    violations = []
    vitals_report = []

    for module_path, label in WAVE_ORGANS:
        try:
            mod = importlib.import_module(module_path)
            vitals = mod.coherence_vitals()
            resonance = vitals.get("resonance", 0)
            wave = vitals.get("wave", "?")
            status = vitals.get("status", "unknown")
            vitals_report.append(f"  {label}: resonance={resonance}, status={status}, wave={wave}")

            if resonance < RESONANCE_FLOOR:
                violations.append(f"{label} resonance={resonance} < {RESONANCE_FLOOR}")
        except Exception as e:
            violations.append(f"{label} FAILED to report vitals: {e}")

    if violations:
        report = "\\n".join(vitals_report)
        errors = "\\n".join(violations)
        raise AssertionError(
            f"CIRCUIT BREAKER TRIGGERED — organism coherence below floor:\\n"
            f"{errors}\\n\\nVitals report:\\n{report}"
        )


def test_all_organs_resonate():
    """Every recent organ must declare resonates_with() as a non-empty list."""
    for module_path, label in WAVE_ORGANS:
        try:
            mod = importlib.import_module(module_path)
            resonates = mod.resonates_with()
            assert isinstance(resonates, list) and len(resonates) > 0, \
                f"{label} resonates_with() returned {resonates}"
        except ImportError as e:
            raise AssertionError(f"{label} import failed: {e}")


def test_all_organs_have_handler():
    """Every recent organ must have a callable handler."""
    for module_path, label in WAVE_ORGANS:
        try:
            mod = importlib.import_module(module_path)
            assert callable(getattr(mod, "handler", None)), \
                f"{label} has no callable handler"
        except ImportError as e:
            raise AssertionError(f"{label} import failed: {e}")
