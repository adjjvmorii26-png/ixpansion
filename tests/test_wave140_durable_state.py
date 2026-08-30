"""Wave 140 — Durable State & Streaming Layer tests."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "api"))

import state_store
from cold_start_kit import ColdStartKit
from snapshot_engine import SnapshotEngine
from event_replay import EventReplay
from stream_gateway import StreamGateway
from state_lock import StateLock
from migration_runner import MigrationRunner
from garbage_collector import GarbageCollector

TEST_NS = "test_wave140_state"


def _cleanup():
    state_store.flush_cache()
    state_store.delete(TEST_NS)
    state_store.delete("test_wave140_state_log")
    snap = SnapshotEngine()
    snap_dir = os.path.join(os.path.dirname(snap.__module__ and __file__), "")
    # snapshots live in .runtime/snapshots — remove any test snapshot
    import pathlib
    for p in pathlib.Path(".runtime/snapshots").glob("test-snapshot-*.json") if pathlib.Path(".runtime/snapshots").exists() else []:
        p.unlink()


def test_wave140_state_store_atomic():
    _cleanup()
    assert state_store.write(TEST_NS, {"workers": 3})
    loaded = state_store.read(TEST_NS)
    assert loaded["workers"] == 3
    assert state_store.append(TEST_NS + "_log", {"event": "hire"})
    log = state_store.read(TEST_NS + "_log", [])
    assert len(log) == 1
    store = state_store.StateStore(TEST_NS)
    updated = store.update({"reputation": 0.9})
    assert updated["reputation"] == 0.9
    assert store.status()["exists"]
    _cleanup()


def test_wave140_cold_start_kit():
    kit = ColdStartKit()
    result = kit.warm()
    assert result["warmed"] >= 0
    assert isinstance(result["namespaces"], list)
    assert kit.status()["warmed"] == result["warmed"]


def test_wave140_snapshot_engine():
    eng = SnapshotEngine()
    state_store.write(TEST_NS, {"snapshot_me": True})
    result = eng.capture(version="3.57.0")
    assert result["namespaces"] >= 1
    assert eng.status()["snapshots"] >= 1
    restore = eng.restore(result["snapshot"])
    assert restore["restored"] >= 1
    assert state_store.read(TEST_NS)["snapshot_me"] is True
    _cleanup()


def test_wave140_event_replay():
    er = EventReplay()
    er.record("router", "route", {"path": "/api/health"})
    er.record("router", "route", {"path": "/api/metrics"})
    er.record("worker", "hire", {"name": "alice"})
    assert er.count() == 3
    replayed = er.replay(module_filter="router")
    assert len(replayed) == 2
    assert er.status()["replays"] == 2


def test_wave140_stream_gateway():
    sg = StreamGateway(heartbeat_s=15.0)
    sg.publish("wave", {"id": 1})
    sg.publish("wave", {"id": 2})
    sg.subscribe("dashboard")
    assert sg.checkpoint("dashboard") == 0
    sg.ack("dashboard", 1)
    assert sg.checkpoint("dashboard") == 1
    since = sg.since(0)
    assert len(since) == 1
    assert "event: wave" in sg.sse(since_id=0)
    assert sg.status()["buffered"] >= 2


def test_wave140_state_lock():
    import threading
    sl = StateLock()
    assert sl.acquire(TEST_NS)
    # another thread is blocked while the main thread holds the lock
    result = {}
    def try_acquire():
        result["acquired"] = sl.acquire(TEST_NS, blocking=False)
    t = threading.Thread(target=try_acquire)
    t.start()
    t.join()
    assert not result["acquired"]
    assert sl.release(TEST_NS)
    assert not sl.release(TEST_NS)  # fully released
    with sl.context(TEST_NS):
        assert TEST_NS in sl._locks
    assert sl.status()["namespaces"] >= 1
    _cleanup()


def test_wave140_migration_runner():
    mr = MigrationRunner()
    mr.register("001-add-version", "add version field", lambda d: {**d, "version": 2})
    mr.register("002-flatten", "flatten nested", lambda d: {"flat": True, **d})
    data = {"name": "state"}
    migrated = mr.apply_all(data)
    assert migrated["version"] == 2
    assert mr.applied() == ["001-add-version", "002-flatten"]
    # re-run is idempotent
    again = mr.apply_all(migrated)
    assert again == migrated
    assert mr.status()["pending"] == 0
    assert mr.status()["executions"] == 2


def test_wave140_garbage_collector():
    gc = GarbageCollector(max_snapshots=1, max_log_bytes=1_000_000)
    result = gc.cleanup()
    assert "tmp" in result and "snapshots" in result and "oversized" in result
    assert gc.status()["max_snapshots"] == 1


def test_wave140_handlers():
    from state_store import handler as h1
    from cold_start_kit import handler as h2
    from snapshot_engine import handler as h3
    from event_replay import handler as h4
    from stream_gateway import handler as h5
    from state_lock import handler as h6
    from migration_runner import handler as h7
    from garbage_collector import handler as h8
    for h in (h1, h2, h3, h4, h5, h6, h7, h8):
        r = h({})
        assert r["status"] == "active"
