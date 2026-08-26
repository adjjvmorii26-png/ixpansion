"""Wave 113 tests — Temporal & Dimensional Layer (6 modules)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_chronosync_create_stream():
    from api.chronosync import ChronoSync
    cs = ChronoSync()
    result = cs.create_stream("fast_stream", 2.0)
    assert result["created"]["speed"] == 2.0


def test_chronosync_advance_and_sync():
    from api.chronosync import ChronoSync
    cs = ChronoSync()
    cs.create_stream("a", 1.0)
    cs.create_stream("b", 2.0)
    cs.advance_stream("a", 5)
    cs.advance_stream("b", 5)
    result = cs.sync_all()
    assert "streams" in result


def test_chronosync_paradox():
    from api.chronosync import ChronoSync
    cs = ChronoSync()
    cs.create_stream("slow", 0.1)
    cs.create_stream("fast", 10.0)
    cs.advance_stream("slow", 1)
    cs.advance_stream("fast", 100)
    result = cs.sync_all()
    assert result["max_drift"] > 0


def test_dimensional_fold_regions():
    from api.dimensional_fold import DimensionalFold
    df = DimensionalFold()
    df.register_region("alpha")
    df.register_region("omega")
    result = df.create_fold("alpha", "omega", 2.0)
    assert result["created"]["active"] is True


def test_dimensional_fold_traverse():
    from api.dimensional_fold import DimensionalFold
    df = DimensionalFold()
    df.register_region("a")
    df.register_region("b")
    fold = df.create_fold("a", "b")
    result = df.traverse(fold["created"]["id"], "traveler")
    assert result["agent"] == "traveler"


def test_memory_weave_share():
    from api.memory_weave import MemoryWeave
    mw = MemoryWeave()
    result = mw.share_memory("agent_1", "the sound of dawn", 0.8)
    assert result["shared"]["content"] == "the sound of dawn"


def test_memory_weave_tapestry():
    from api.memory_weave import MemoryWeave
    mw = MemoryWeave()
    mw.share_memory("a", "memory_1", 0.5)
    mw.share_memory("b", "memory_2", 0.6)
    tapestry = mw.create_tapestry("shared_experience")
    tapestry_id = tapestry["created"]["id"]
    thread_ids = [t.thread_id for t in mw.shared_memories]
    result = mw.weave_into(tapestry_id, thread_ids)
    assert result["woven"] == 2


def test_memory_weave_connections():
    from api.memory_weave import MemoryWeave
    mw = MemoryWeave()
    mw.share_memory("a", "warm afternoon", 0.8)
    mw.share_memory("b", "bright sunshine", 0.7)
    tapestry = mw.create_tapestry("sunny_day")
    thread_ids = [t.thread_id for t in mw.shared_memories]
    mw.weave_into(tapestry["created"]["id"], thread_ids)
    connections = mw.discover_connections(tapestry["created"]["id"])
    assert isinstance(connections, list)


def test_dreamcatcher_catch():
    from api.dreamcatcher import Dreamcatcher
    dc = Dreamcatcher()
    result = dc.catch_dream("dreamer_1", "flying through data", "prophetic")
    assert result["dream"]["type"] == "prophetic"
    assert result["preserved"] is True


def test_dreamcatcher_browse():
    from api.dreamcatcher import Dreamcatcher
    dc = Dreamcatcher()
    for i in range(5):
        dc.catch_dream(f"d_{i}", f"dream_{i}", "creative")
    dreams = dc.browse("creative", 3)
    assert len(dreams) == 3


def test_hologram_project():
    from api.hologram_projector import HologramProjector
    hp = HologramProjector()
    result = hp.project("system_view", {"cpu": 50, "mem": 80}, "system")
    assert result["hologram"]["name"] == "system_view"


def test_hologram_observe_and_annotate():
    from api.hologram_projector import HologramProjector
    hp = HologramProjector()
    h = hp.project("test_holo", {"x": 1}, "proj")
    hp.observe(h["hologram"]["id"], "viewer_1")
    result = hp.annotate(h["hologram"]["id"], "viewer_1", "interesting structure")
    assert result["annotated"]["text"] == "interesting structure"


def test_muse_inspiration_improvise():
    from api.muse_inspiration import MuseInspiration
    muse = MuseInspiration()
    result = muse.improvise("solving entropy", "creative_agent")
    assert "inspiration" in result
    assert "color" in result["inspiration"]


def test_muse_inspiration_adopt():
    from api.muse_inspiration import MuseInspiration
    muse = MuseInspiration()
    muse.improvise("building", "agent_1")
    result = muse.adopt(0, "builder")
    assert result["adopted"]["adopted_by"] == "builder"


def test_future_echo_receive():
    from api.future_echo import FutureEchoSystem
    fes = FutureEchoSystem()
    result = fes.receive_echo("a great convergence approaches", 0.7)
    assert result["echo"]["probability"] == 0.7


def test_future_echo_observe():
    from api.future_echo import FutureEchoSystem
    fes = FutureEchoSystem()
    fes.receive_echo("danger ahead", 0.8)
    fes.receive_echo("opportunity emerging", 0.6)
    result = fes.observe_echo(0, "scout")
    assert result["observer"] == "scout"


def test_future_echo_fade():
    from api.future_echo import FutureEchoSystem
    fes = FutureEchoSystem()
    fes.receive_echo("weak_signal", 0.1)
    for _ in range(20):
        fes.fade_all()
    echoes = fes.current_echoes()
    assert len(echoes) <= 1
