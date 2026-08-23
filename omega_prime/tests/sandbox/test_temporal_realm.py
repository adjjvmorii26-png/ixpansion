import pytest
from omega_prime.sandbox.realms.temporal_realm import TemporalRealm


class TestTemporalRealm:
    def test_materialize_creates_zones(self):
        realm = TemporalRealm()
        realm.materialize({})
        obs = realm.observation
        assert len(obs["zones"]) > 0

    def test_time_dilation_rates(self):
        realm = TemporalRealm()
        realm.materialize({})
        for _ in range(10):
            realm.advance([])
        obs = realm.observation
        times = {name: z["local_t"] for name, z in obs["zones"].items()}
        # Fast zones should have more local time than slow zones
        if "chronos" in times and "tardus" in times:
            assert times["chronos"] > times["tardus"]

    def test_move_agent_between_zones(self):
        realm = TemporalRealm()
        realm.materialize({"agents": ["scout-01"]})
        assert realm.move_agent("scout-01", "chronos")
        obs = realm.observation
        assert "scout-01" in obs["zones"]["chronos"]["agents"]

    def test_move_to_invalid_zone_fails(self):
        realm = TemporalRealm()
        realm.materialize({})
        assert not realm.move_agent("x", "nonexistent_zone")
