import pytest

from mesh.channels import MeshChannels
from mesh.topology import build_agent_mesh, build_topology


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


def test_agent_mesh_gives_star_leaves_an_uplink():
    edges = build_agent_mesh("star", ["observer", "architect"])
    assert ("observer", "origin", "uplink") in edges
    assert ("origin", "observer", "downlink") in edges
    mesh = MeshChannels(edges)
    assert mesh.broadcast("observer", {"type": "record"}) == 1
    assert mesh.broadcast("origin", {"type": "broadcast"}) == 2


def test_agent_mesh_ring_routes_each_agent_forward():
    edges = build_agent_mesh("ring", ["observer", "mutator"])
    mesh = MeshChannels(edges)
    assert mesh.broadcast("observer", {"pulse": 1}) == 1
    assert mesh.inbox_count("mutator") == 1


def test_agent_mesh_chaotic_is_bidirectional():
    edges = build_agent_mesh("chaotic", ["observer"])
    assert ("origin", "observer", "chaotic") in edges
    assert ("observer", "origin", "chaotic") in edges
