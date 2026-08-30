"""Garden lineage — family tree tests (offline, deterministic)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from hortus_hexis import lineage  # noqa: E402


def _node(name, content="", words="", parents=None):
    return {"name": name, "content": content, "words": words, "parents": parents or []}


def test_parents_of_colon_hybrid():
    n = _node("kid", content="hybrid:ada+grace")
    assert lineage.parents_of(n) == ["ada", "grace"]


def test_parents_of_word_hybrid():
    n = _node("kid", words="hybrid of ada and grace")
    assert lineage.parents_of(n) == ["ada", "grace"]


def test_parents_of_explicit_field():
    n = _node("kid", parents=["ada", "grace"])
    assert lineage.parents_of(n) == ["ada", "grace"]


def test_parents_ignores_self_and_empty():
    n = _node("kid", content="hybrid:kid+grace", parents=["", "grace", "kid"])
    assert lineage.parents_of(n) == ["grace"]


def test_children_indexed_per_parent():
    nodes = [_node("ada"), _node("grace"), _node("kid", content="hybrid:ada+grace")]
    index = lineage.lineage_index(nodes)
    assert index["ada"]["children"] == ["kid"]
    assert index["grace"]["children"] == ["kid"]
    assert index["kid"]["children"] == []


def test_generations_founders_and_depth():
    nodes = [_node("ada"), _node("grace"),
             _node("kid", content="hybrid:ada+grace"),
             _node("grandkid", content="hybrid:kid+ada")]
    gen = lineage._generations_from(nodes)
    assert gen["founders"] == ["ada", "grace"]
    assert gen["depths"]["ada"] == 0
    assert gen["depths"]["kid"] == 1
    assert gen["depths"]["grandkid"] == 2
    assert gen["max_generation"] == 2


def test_render_ascii_contains_names():
    nodes = [_node("ada"), _node("kid", content="hybrid:ada+grace"),
             _node("grace")]
    out = lineage.render_ascii(nodes)
    assert "ada" in out and "kid" in out and "grace" in out


def test_export_writes_json(tmp_path):
    target = tmp_path / "family_lineage.json"
    p = lineage.export(target)
    payload = json.loads(p.read_text())
    assert payload["count"] >= 1
    assert "nodes" in payload and "generations" in payload


def test_build_parses_live_registry():
    nodes = lineage.build()
    names = [n.get("name") for n in nodes]
    assert "orevurinys" in names
    # the garden's most famous hybrid pair
    found = [n for n in nodes if n["name"] == "orevurysveln"]
    if found:
        assert set(found[0]["parents"]) == {"orevurinys", "draknysveln"}
