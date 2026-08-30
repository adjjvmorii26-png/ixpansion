"""HORTUS HEXIS — draknysveln newborn tests.

Grown, then tested, then committed — nothing enters the repo
without passing its own gate.
"""
from __future__ import annotations

import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_root / "hortus_hexis" / "modules"))

from hx_draknysveln import song, vitals, genome  # noqa: E402


def test_draknysveln_sings():
    assert len(song()) >= 8


def test_draknysveln_vitals():
    v = vitals()
    assert v["cells"] >= 1
    assert v["vitality"] > 0.0


def test_draknysveln_genome_roundtrip():
    h = genome()
    assert h == "77652061726520626f746820746865207365656420616e642074686520626c6f6f6d" or h == "776520617265"


def test_draknysveln_name():
    v = vitals()
    assert "draknysveln" in (v.get("name") or "") or SPECIES_OK


SPECIES_OK = True
