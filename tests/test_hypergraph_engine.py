import asyncio
import hashlib
import json

import pytest

from lab.core.hypergraph_omni_engine import (
    HypergraphEngineError,
    HypergraphOmniEngine,
)


def test_seeded_runs_produce_same_state_and_seals():
    async def run():
        first = HypergraphOmniEngine(seed=42)
        second = HypergraphOmniEngine(seed=42)

        a = await first.execute_resonance_cycle(cycles=3)
        b = await second.execute_resonance_cycle(cycles=3)

        assert [x["aggregate_drift"] for x in a] == [
            x["aggregate_drift"] for x in b
        ]
        assert [x["chained_seal"] for x in a] == [
            x["chained_seal"] for x in b
        ]
        assert {
            k: v.to_dict() for k, v in first.nodes.items()
        } == {
            k: v.to_dict() for k, v in second.nodes.items()
        }

    asyncio.run(run())


@pytest.mark.parametrize("cycles", [0, -1, 51, True, False, 1.5, "3"])
def test_invalid_cycle_counts_are_rejected(cycles):
    async def run():
        engine = HypergraphOmniEngine(seed=42)
        with pytest.raises(HypergraphEngineError):
            await engine.execute_resonance_cycle(cycles=cycles)

    asyncio.run(run())


def test_invalid_node_reference_is_rejected():
    engine = HypergraphOmniEngine(seed=42)

    with pytest.raises(HypergraphEngineError):
        engine.entangle_nodes("node_genome", "missing_node")


def test_weights_remain_bounded():
    async def run():
        engine = HypergraphOmniEngine(seed=1337)
        await engine.execute_resonance_cycle(cycles=50)

        for node in engine.nodes.values():
            assert 0.0 <= node.vector_weight <= 1.0
            assert 0.0 <= node.entropy_drift <= 0.05

    asyncio.run(run())


def test_history_is_bounded():
    async def run():
        engine = HypergraphOmniEngine(seed=42)

        for _ in range(3):
            await engine.execute_resonance_cycle(cycles=50)

        assert len(engine.resonance_manifold_history) <= engine.MAX_HISTORY

    asyncio.run(run())


def test_seal_uses_full_sha256_digest():
    engine = HypergraphOmniEngine(seed=42)
    seal = engine._generate_canonical_seal(0.05)

    digest = seal.removeprefix("0xOMEGA_")
    assert len(digest) == 64
    assert all(c in "0123456789ABCDEF" for c in digest)


def test_concurrent_cycles_preserve_valid_state():
    async def run():
        engine = HypergraphOmniEngine(seed=42)

        await asyncio.gather(
            engine.execute_resonance_cycle(cycles=5),
            engine.execute_resonance_cycle(cycles=5),
        )

        assert len(engine.resonance_manifold_history) == 10
        assert all(
            0.0 <= node.vector_weight <= 1.0
            for node in engine.nodes.values()
        )

    asyncio.run(run())


def test_chained_seal_changes_when_state_changes():
    engine = HypergraphOmniEngine(seed=42)

    first = engine._generate_canonical_seal(0.01)
    engine.nodes["node_atlas"].vector_weight = 0.1234
    second = engine._generate_canonical_seal(0.01)

    assert first != second


def test_audit_seal_has_valid_sha256_structure():
    engine = HypergraphOmniEngine(seed=42)
    seal = engine._generate_canonical_seal(0.05)

    assert seal.startswith("0xOMEGA_")
    assert len(seal.removeprefix("0xOMEGA_")) == 64
