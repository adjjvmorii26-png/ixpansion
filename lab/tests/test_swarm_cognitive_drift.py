import hashlib
import json
from pathlib import Path

import pytest

from lab.swarm_cognitive_drift import accumulate_observations


FIXED_CLOCK = lambda: "2026-08-25T08:00:00+00:00"


def _hash(result):
    material = {k: v for k, v in result.items() if k != "drift_hash"}
    return hashlib.sha256(json.dumps(material, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def test_single_observation_creates_profile(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    obs = [{"agent_id": "sentinel-01", "species": "sentinel", "verdict": "preserve", "attention": 0.8}]
    result = accumulate_observations(obs, clock=FIXED_CLOCK, record=False)
    assert result["observation_count"] == 1
    assert result["agent_count"] == 1
    assert result["updated_agents"][0]["temperament"] == "preservative"
    assert result["drift_hash"] == _hash(result)


def test_accumulation_shifts_drift(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    obs = [{"agent_id": f"a-{i}", "species": "wanderer", "verdict": "drift", "attention": 0.3} for i in range(10)]
    result = accumulate_observations(obs, clock=FIXED_CLOCK, record=False)
    agent = result["updated_agents"][0]
    assert agent["drift"] < 0
    assert agent["curiosity"] == 0.0


def test_recorded_profiles_persist(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    obs = [{"agent_id": "b-01", "species": "archivist", "verdict": "inspect", "attention": 0.6}]
    result = accumulate_observations(obs, clock=FIXED_CLOCK, record=True)
    profiles = json.loads((tmp_path / "state" / "swarm" / "cognitive_profiles.json").read_text())
    assert "b-01" in profiles["agents"]
    assert profiles["agents"]["b-01"]["temperament"] == "preservative"


def test_empty_observations(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    result = accumulate_observations([], clock=FIXED_CLOCK, record=False)
    assert result["observation_count"] == 0
    assert result["agent_count"] == 0
