"""Contract-suite fixtures, isolated from the repository-wide test bootstrap."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def _json_fixture(name: str):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def vercel_data():
    return _json_fixture("vercel_manifests.json")


@pytest.fixture
def wp_payload():
    return _json_fixture("wp_blocks.json")


@pytest.fixture
def gitlab_pipelines():
    return yaml.safe_load(
        (FIXTURES / "gitlab_pipelines.yml").read_text(encoding="utf-8")
    )


@pytest.fixture
def handoff_data():
    return _json_fixture("conductor_handoffs.json")
