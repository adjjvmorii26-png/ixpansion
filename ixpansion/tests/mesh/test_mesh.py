import pytest

from mesh.channels import MeshChannels
from mesh.topology import build_topology


def test_star_routes_only_from_hub():
    edges = build_topology("star", ["hub", "one", "two"])
    mesh = MeshChannels(edges)
    delivered = mesh.broadcast("hub", {"pulse": True})
    assert delivered == 2
    assert mesh.inbox_count("one") == 1
    assert mesh.inbox_count("two") == 1


def test_ring_connects_each_node_forward():
    edges = build_topology("ring", ["a", "b", "c"])
    assert ("c", "a", "ring") in edges


def test_chaotic_fully_connects_without_duplicates():
    edges = build_topology("chaotic", ["a", "b", "c"])
    assert len(edges) == 3


def test_rejects_unknown_topology():
    with pytest.raises(ValueError):
        build_topology("lattice", ["a", "b"])
