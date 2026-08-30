"""HORTUS HEXIS — kalyndnysorev newborn tests.

Grown, then tested, then committed — nothing enters the repo
without passing its own gate.
These lines were cross-pollinated from two parents.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "hortus_hexis" / "modules"))

from hx_kalyndnysorev import song, vitals, genome, parents  # noqa: E402


def test_kalyndnysorev_sings():
    assert len(song()) >= 8


def test_kalyndnysorev_vitals():
    v = vitals()
    assert v["cells"] >= 1
    assert v["vitality"] > 0.0


def test_kalyndnysorev_genome_roundtrip():
    h = genome()
    assert h == "010d085c014b4f115f5e34293135421b151a1be8eef6e881dcc7dfcee4a8bdb796829c869d77637e76c5ffe54dfa666559" or h == "010d085c014b"


def test_kalyndnysorev_provenance():
    if 1:
        assert len(parents()) == 2
    else:
        assert parents() == []


def test_kalyndnysorev_lineage():
    assert sorted(parents()) == sorted(["kalyndramar", "syphexnysorev"])


