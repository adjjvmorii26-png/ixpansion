"""Unification Layer — the organism's shared ontology.

Tests that the vocabulary, layers, identity, and status normalization
are internally consistent — the single source of truth.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api"))

import organism_ontology as ont


def test_ontology_is_living():
    from api import coherence_regulator as cr
    living = set(cr._candidate_modules())
    assert "organism_ontology" in living


def test_status_vocabulary_is_closed():
    """Every alias maps to a canonical vocabulary word."""
    for alias, canonical in ont.STATUS_ALIASES.items():
        assert canonical in ont.STATUS_VOCABULARY, f"{alias} -> {canonical} not in vocab"


def test_canonical_status_always_valid():
    """Any input normalizes to a vocab word."""
    for raw in ["healthy", "active", "degraded", "elite", "beauty",
                "max_resonant", "broken", "down", "", "weird-value"]:
        result = ont.canonical_status(raw)
        assert result in ont.STATUS_VOCABULARY, f"{raw!r} -> {result}"


def test_classify_layer_covers_codebase():
    """All the wave modules classify to a meaningful layer."""
    samples = {
        "stratum_excavator": "Archaeology",
        "elegance_scorer": "Aesthetics",
        "barometric_intent": "Meteorology",
        "symbiosis_detector": "Ecology",
        "impossibility_mapper": "Limits",
        "choral_engine": "Sound",
    }
    for module, expected in samples.items():
        assert ont.classify_layer(module) == expected, f"{module} -> {expected}"


def test_identity_is_single():
    """Identity is the canonical version/wave source."""
    ident = ont.identity()
    assert ident["version"] == "3.90.0"
    assert ident["wave"] == 202
    assert len(ident["narrative_arc"]) == 13
    assert ident["wave_name"] == "The Aesthetics of Code"


def test_layers_taxonomy_consistent():
    """Every family belongs to a declared layer."""
    layers = ont.layers()
    assert len(layers["layers"]) >= 10
    for layer, keywords in ont.LAYER_FAMILIES.items():
        assert layer in layers["layers"], f"{layer} not in taxonomy"
        assert len(keywords) >= 1


def test_ontology_feed_state():
    """organism_state uses ontology as source of truth."""
    from api.organism_state import full_state
    state = full_state()
    ident = ont.identity()
    assert state["version"] == ident["version"]
    assert state["wave"] == ident["wave"]
    assert state["status"] in ont.STATUS_VOCABULARY
