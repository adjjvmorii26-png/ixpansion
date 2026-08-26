"""Wave 124 -- Temporal Cartography Layer tests."""
from __future__ import annotations

from api.temporal_cartographer import TemporalCartographer
from api.chrono_terrain import ChronoTerrain
from api.time_dilation_mapper import TimeDilationMapper
from api.past_future_bridge import PastFutureBridge
from api.epoch_constellation import EpochConstellation
from api.temporal_weather_system import TemporalWeatherSystem
from api.kairos_detector import KairosDetector
from api.memesis_chronicle import MemesisChronicle


class TestTemporalCartographer:
    def test_plot_and_navigate(self):
        tc = TemporalCartographer()
        a = tc.plot("Big Bang", 0.0)
        b = tc.plot("Now", 13.8e9)
        tc.connect_landmarks(a.id, b.id)
        route = tc.navigate(a.id)
        assert len(route) >= 2

    def test_timeline(self):
        tc = TemporalCartographer()
        tc.plot("First", 1.0)
        tc.plot("Second", 2.0)
        tl = tc.timeline()
        assert tl[0]["name"] == "First"

    def test_status(self):
        tc = TemporalCartographer()
        tc.plot("A", 1.0)
        s = tc.status()
        assert s["landmarks"] == 1


class TestChronoTerrain:
    def test_add_and_explore(self):
        ct = ChronoTerrain()
        ct.add_point("peak", 0.9)
        ct.add_point("valley", 0.05)
        result = ct.explore("peak")
        assert result["terrain"] == "mountain"

    def test_terrain_types(self):
        ct = ChronoTerrain()
        ct.add_point("m", 0.9)
        ct.add_point("v", 0.15)
        assert len(ct.mountains()) == 1
        assert len(ct.valleys()) == 1

    def test_status(self):
        ct = ChronoTerrain()
        ct.add_point("p", 0.5)
        s = ct.status()
        assert s["total_points"] == 1


class TestTimeDilationMapper:
    def test_register_and_measure(self):
        td = TimeDilationMapper()
        td.register_zone("fast", 2.0)
        td.register_zone("slow", 0.5)
        result = td.measure("fast", 10.0)
        assert result["subjective"] == 20.0

    def test_fastest_slowest(self):
        td = TimeDilationMapper()
        td.register_zone("fast", 3.0)
        td.register_zone("slow", 0.2)
        assert td.fastest_zone() == "fast"
        assert td.slowest_zone() == "slow"

    def test_status(self):
        td = TimeDilationMapper()
        td.register_zone("z", 1.0)
        s = td.status()
        assert s["total_zones"] == 1


class TestPastFutureBridge:
    def test_create_and_send(self):
        pfb = PastFutureBridge()
        b = pfb.create_bridge("B1", "past_state", "future_state")
        result = pfb.send(b.id, "hello", "forward")
        assert result["direction"] == "forward"

    def test_backward(self):
        pfb = PastFutureBridge()
        b = pfb.create_bridge("B2", "p", "f")
        result = pfb.send(b.id, "msg", "backward")
        assert result["direction"] == "backward"

    def test_status(self):
        pfb = PastFutureBridge()
        pfb.create_bridge("B", "p", "f")
        s = pfb.status()
        assert s["total_bridges"] == 1


class TestEpochConstellation:
    def test_add_and_connect(self):
        ec = EpochConstellation()
        s1 = ec.add_epoch("E1", 0, 100)
        s2 = ec.add_epoch("E2", 100, 250)
        ok = ec.connect_epochs(s1.id, s2.id)
        assert ok is True

    def test_longest_epoch(self):
        ec = EpochConstellation()
        ec.add_epoch("Short", 0, 10)
        ec.add_epoch("Long", 0, 1000)
        result = ec.longest_epoch()
        assert result["name"] == "Long"

    def test_status(self):
        ec = EpochConstellation()
        ec.add_epoch("E1", 0, 10)
        s = ec.status()
        assert s["total_epochs"] == 1


class TestTemporalWeatherSystem:
    def test_observe_and_change(self):
        tw = TemporalWeatherSystem()
        obs = tw.observe()
        assert obs["pattern"] == "calm"
        changed = tw.change_weather("storm", 0.9)
        assert changed["pattern"] == "storm"

    def test_forecast(self):
        tw = TemporalWeatherSystem()
        preds = tw.forecast(steps=3)
        assert len(preds) == 3

    def test_status(self):
        tw = TemporalWeatherSystem()
        s = tw.status()
        assert s["current"] == "calm"


class TestKairosDetector:
    def test_scan_and_seize(self):
        kd = KairosDetector(threshold=0.5)
        result = kd.scan("opportunity", 0.8)
        assert result["detected"] is True
        moment_id = result["moment"]["id"]
        seized = kd.seize_moment(moment_id)
        assert seized["seized"] is True

    def test_below_threshold(self):
        kd = KairosDetector(threshold=0.9)
        result = kd.scan("weak_signal", 0.3)
        assert result["detected"] is False

    def test_status(self):
        kd = KairosDetector()
        kd.scan("s", 0.5)
        s = kd.status()
        assert s["total_moments"] == 1


class TestMemesisChronicle:
    def test_introduce_and_evolve(self):
        mc = MemesisChronicle()
        meme = mc.introduce("survival of the fittest", 0.9)
        child = mc.evolve(meme.id)
        assert child is not None
        assert child.fitness < meme.fitness

    def test_mutate(self):
        mc = MemesisChronicle()
        meme = mc.introduce("original idea")
        mutant = mc.mutate_meme(meme.id, "improved idea")
        assert mutant is not None
        assert mutant.content == "improved idea"

    def test_fitness_landscape(self):
        mc = MemesisChronicle()
        mc.introduce("a", 0.3)
        mc.introduce("b", 0.9)
        landscape = mc.fitness_landscape()
        assert landscape[0]["fitness"] >= landscape[1]["fitness"]

    def test_status(self):
        mc = MemesisChronicle()
        mc.introduce("x")
        s = mc.status()
        assert s["total_memes"] == 1
