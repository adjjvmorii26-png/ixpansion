import hashlib
import json

from lab.experiments.constellation_caption import describe_constellation


FIXED_CLOCK = lambda: "2026-08-25T11:00:00+00:00"


def _hash(result):
    material = {k: v for k, v in result.items() if k != "caption_hash"}
    return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_single_node_caption():
    nodes = [{"id": "A", "sigil": "◆", "x": 0.5, "y": 0.5, "weight": 1.0}]
    result = describe_constellation(nodes, clock=FIXED_CLOCK)
    assert result["node_count"] == 1
    assert result["caption_hash"] == _hash(result)
    assert "solitary" in result["summary"]


def test_multi_node_descriptions():
    nodes = [
        {"id": "A", "sigil": "◇", "x": 0.9, "y": 0.1, "weight": 2.0},
        {"id": "B", "sigil": "○", "x": 0.1, "y": 0.9, "weight": 0.3},
    ]
    result = describe_constellation(nodes, clock=FIXED_CLOCK)
    assert result["node_count"] == 2
    assert "prominent" in result["captions"][0]
    assert "subtle" in result["captions"][1]


def test_empty_constellation():
    result = describe_constellation([], clock=FIXED_CLOCK)
    assert result["node_count"] == 0
    assert "0" in result["summary"]


def test_deterministic_output():
    nodes = [{"id": "X", "sigil": "★", "x": 0.3, "y": 0.7, "weight": 1.0}]
    assert describe_constellation(nodes, clock=FIXED_CLOCK) == describe_constellation(nodes, clock=FIXED_CLOCK)
