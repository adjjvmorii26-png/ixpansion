"""Wave 128 -- Dimensional Threading Layer tests."""
from __future__ import annotations

from api.dimensional_thread import DimensionalThreadingNetwork, DimensionalThread
from api.reality_fork import RealityForkManager, RealityFork
from api.parallel_universe_mapper import ParallelUniverseMapper, UniverseNode
from api.timeline_weaver import TimelineWeaver, TimelineStrand
from api.dimension_lock import DimensionLockManager, DimensionLock
from api.multiverse_navigator import MultiverseNavigator
from api.quantum_entanglement_network import QuantumEntanglementNetwork, EntangledPair
from api.dimensional_drift import DimensionalDriftTracker, DriftVector


class TestDimensionalThread:
    def test_create_and_send(self):
        dtn = DimensionalThreadingNetwork()
        t = dtn.create_thread("bridge_alpha", "dim_1", "dim_2")
        result = dtn.send(t.id, "hello across dimensions")
        assert result["sent"] is True
        assert t.strength > 0.9

    def test_active_threads(self):
        dtn = DimensionalThreadingNetwork()
        t = dtn.create_thread("t1", "d1", "d2")
        active = dtn.active_threads()
        assert len(active) == 1

    def test_status(self):
        dtn = DimensionalThreadingNetwork()
        dtn.create_thread("t", "d1", "d2")
        s = dtn.status()
        assert s["total_threads"] == 1
        assert s["dimensions"] == 2


class TestRealityFork:
    def test_fork_and_branch(self):
        rfm = RealityForkManager()
        f = rfm.fork("alpha_timeline")
        child = rfm.branch(f.id, "divergence_point")
        assert child is not None
        assert child.parent_id == f.id

    def test_merge(self):
        rfm = RealityForkManager()
        f = rfm.fork("test_fork")
        f.add_event("e1")
        result = rfm.merge_fork(f.id)
        assert result["merged"] is True

    def test_status(self):
        rfm = RealityForkManager()
        rfm.fork("f1")
        s = rfm.status()
        assert s["total_forks"] == 1


class TestParallelUniverseMapper:
    def test_add_and_portal(self):
        pum = ParallelUniverseMapper()
        u1 = pum.add_universe("Universe_A", 0.1)
        u2 = pum.add_universe("Universe_B", 0.5)
        ok = pum.open_portal(u1.id, u2.id)
        assert ok is True

    def test_nearest(self):
        pum = ParallelUniverseMapper()
        pum.add_universe("close", 0.1)
        pum.add_universe("far", 0.9)
        nearest = pum.nearest_universe("close")
        assert nearest is not None

    def test_status(self):
        pum = ParallelUniverseMapper()
        pum.add_universe("u1")
        s = pum.status()
        assert s["total_universes"] == 1


class TestTimelineWeaver:
    def test_create_and_weave(self):
        tw = TimelineWeaver()
        s1 = tw.create_strand("past", "origin")
        s2 = tw.create_strand("present", "origin")
        result = tw.weave([s1.id, s2.id])
        assert result["strands"] == 2

    def test_status(self):
        tw = TimelineWeaver()
        tw.create_strand("s1", "o1")
        s = tw.status()
        assert s["total_strands"] == 1


class TestDimensionLock:
    def test_lock_and_unlock(self):
        dlm = DimensionLockManager()
        result = dlm.lock_dimension("alpha", keyholder="admin")
        assert result["locked"] is True
        assert dlm.is_locked("alpha")
        dlm.unlock_dimension("alpha")
        assert not dlm.is_locked("alpha")

    def test_locked_dimensions(self):
        dlm = DimensionLockManager()
        dlm.lock_dimension("d1")
        dlm.lock_dimension("d2")
        locked = dlm.locked_dimensions()
        assert len(locked) == 2

    def test_status(self):
        dlm = DimensionLockManager()
        dlm.lock_dimension("x")
        s = dlm.status()
        assert s["total_locks"] == 1


class TestMultiverseNavigator:
    def test_navigate(self):
        mn = MultiverseNavigator()
        for d in ["A", "B", "C", "D"]:
            mn.add_dimension(d)
        mn.connect("A", "B")
        mn.connect("B", "C")
        mn.connect("C", "D")
        path = mn.navigate("A", "D")
        assert path is not None
        assert len(path) == 4

    def test_discover_hidden(self):
        mn = MultiverseNavigator()
        mn.add_dimension("X")
        mn.add_dimension("Y")
        mn.connect("X", "Y")
        result = mn.discover_hidden("X", "Y")
        assert result["discovered"] is True

    def test_status(self):
        mn = MultiverseNavigator()
        mn.add_dimension("A")
        s = mn.status()
        assert s["dimensions"] == 1


class TestQuantumEntanglementNetwork:
    def test_entangle_and_measure(self):
        qen = QuantumEntanglementNetwork()
        pair = qen.entangle("module_A", "module_B")
        result = qen.measure(pair.id, "collapsed")
        assert result["state_a"] == "collapsed"
        assert result["state_b"] == "collapsed"
        assert pair.is_entangled()

    def test_status(self):
        qen = QuantumEntanglementNetwork()
        qen.entangle("m1", "m2")
        s = qen.status()
        assert s["total_pairs"] == 1


class TestDimensionalDrift:
    def test_register_and_tick(self):
        ddt = DimensionalDriftTracker()
        vec = ddt.register("dim_a", "dim_b", rate=0.05)
        ddt.tick_all()
        assert vec.total_drift == 0.05

    def test_fastest_drift(self):
        ddt = DimensionalDriftTracker()
        ddt.register("d1", "d2", 0.1)
        ddt.register("d3", "d4", 0.01)
        fastest = ddt.fastest_drift()
        assert fastest["rate"] == 0.1

    def test_status(self):
        ddt = DimensionalDriftTracker()
        ddt.register("d1", "d2")
        s = ddt.status()
        assert s["total_vectors"] == 1
