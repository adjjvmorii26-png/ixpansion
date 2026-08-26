"""Wave 130 -- Astral Navigation Layer tests."""
from __future__ import annotations

from api.stellar_compass import StellarCompass, Star
from api.nebula_mapper import NebulaMapper, Nebula
from api.cosmic_ray_detector import CosmicRayDetector, CosmicRay
from api.solar_wind_analyzer import SolarWindAnalyzer, SolarWindStream
from api.gravity_well_mapper import GravityWellMapper, GravityWell
from api.event_horizon_monitor import EventHorizonMonitor, EventHorizon
from api.pulsar_clock import PulsarClock, PulsarBeat
from api.supernova_remnant import SupernovaRemnant, Remnant


class TestStellarCompass:
    def test_chart_and_navigate(self):
        sc = StellarCompass()
        sc.chart_star("Polaris", 0.0, 1.0)
        sc.chart_star("Sirius", 3.0, 4.0)
        result = sc.navigate("Polaris", "Sirius")
        assert result["distance"] > 0
        assert "bearing_degrees" in result

    def test_nearest_star(self):
        sc = StellarCompass()
        sc.chart_star("A", 1.0, 1.0)
        sc.chart_star("B", 10.0, 10.0)
        nearest = sc.nearest_star(1.5, 1.5)
        assert nearest["name"] == "A"

    def test_status(self):
        sc = StellarCompass()
        sc.chart_star("S", 0, 0)
        s = sc.status()
        assert s["total_stars"] == 1


class TestNebulaMapper:
    def test_discover_and_collapse(self):
        nm = NebulaMapper()
        n = nm.discover("Orion", 0.9)
        result = nm.collapse(n.id)
        assert result["collapsed"] is True

    def test_ready_for_formation(self):
        nm = NebulaMapper()
        nm.discover("dense", 0.8)
        nm.discover("sparse", 0.3)
        ready = nm.ready_for_formation()
        assert len(ready) == 1

    def test_status(self):
        nm = NebulaMapper()
        nm.discover("N", 0.5)
        s = nm.status()
        assert s["total_nebulae"] == 1


class TestCosmicRayDetector:
    def test_detect(self):
        crd = CosmicRayDetector(sensitivity=0.3)
        result = crd.detect("distant_star", 0.9, "north")
        assert result["detected"] is True

    def test_below_sensitivity(self):
        crd = CosmicRayDetector(sensitivity=0.9)
        result = crd.detect("weak", 0.1)
        assert result["detected"] is False

    def test_status(self):
        crd = CosmicRayDetector()
        crd.detect("s", 0.5)
        s = crd.status()
        assert s["detections"] == 1


class TestSolarWindAnalyzer:
    def test_create_and_measure(self):
        swa = SolarWindAnalyzer()
        stream = swa.create_stream("Sun", "Earth", 2.0)
        readings = swa.measure_all()
        assert len(readings) == 1
        assert readings[0]["velocity"] == 2.0

    def test_fastest_stream(self):
        swa = SolarWindAnalyzer()
        swa.create_stream("A", "B", 1.0)
        swa.create_stream("C", "D", 5.0)
        fastest = swa.fastest_stream()
        assert fastest["velocity"] == 5.0

    def test_status(self):
        swa = SolarWindAnalyzer()
        swa.create_stream("A", "B")
        s = swa.status()
        assert s["total_streams"] == 1


class TestGravityWellMapper:
    def test_place_and_orbit(self):
        gwm = GravityWellMapper()
        gwm.place_well("Sun", 100.0)
        ok = gwm.orbit("Sun", "Earth")
        assert ok is True

    def test_strongest_well(self):
        gwm = GravityWellMapper()
        gwm.place_well("small", 1.0)
        gwm.place_well("massive", 200.0)
        strongest = gwm.strongest_well()
        assert strongest["name"] == "massive"
        assert strongest["type"] == "black_hole"

    def test_status(self):
        gwm = GravityWellMapper()
        gwm.place_well("W", 5.0)
        s = gwm.status()
        assert s["total_wells"] == 1


class TestEventHorizonMonitor:
    def test_check_proximity(self):
        ehm = EventHorizonMonitor()
        ehm.establish("BH1", radius=2.0)
        result = ehm.check("BH1", "module_A", 1.5)
        assert result["crossed"] is True

    def test_no_breach(self):
        ehm = EventHorizonMonitor()
        ehm.establish("BH1", radius=2.0)
        result = ehm.check("BH1", "module_A", 5.0)
        assert result["crossed"] is False

    def test_status(self):
        ehm = EventHorizonMonitor()
        ehm.establish("H", 1.0)
        s = ehm.status()
        assert s["total_horizons"] == 1


class TestPulsarClock:
    def test_register_and_tick(self):
        pc = PulsarClock()
        pc.register_pulsar("PSR_B1919+21", 1.337)
        results = pc.tick_all()
        assert len(results) == 1
        assert results[0]["beat"] == 1

    def test_status(self):
        pc = PulsarClock()
        pc.register_pulsar("P1", 1.0)
        s = pc.status()
        assert s["total_pulsars"] == 1


class TestSupernovaRemnant:
    def test_record_explosion(self):
        sr = SupernovaRemnant()
        remnant = sr.record_explosion("old_module", 20)
        assert remnant.debris_count == 20
        assert sr.total_enrichment() > 0

    def test_status(self):
        sr = SupernovaRemnant()
        sr.record_explosion("x", 5)
        s = sr.status()
        assert s["total_remnants"] == 1
