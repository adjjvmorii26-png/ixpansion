import re
import tomllib
from datetime import date
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def _package_version(relative_path: str) -> str:
    data = tomllib.loads((ROOT / relative_path).read_text(encoding="utf-8"))
    return data["project"]["version"]


def _latest_changelog_version() -> str:
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    match = re.search(r"^## \[(\d+\.\d+\.\d+)\]", text, flags=re.MULTILINE)
    assert match is not None
    return match.group(1)


class TestReleaseMetadata:
    def test_python_packages_share_the_release_version(self):
        root_version = _package_version("pyproject.toml")
        fractal_version = _package_version("omega_fractal_engine/pyproject.toml")
        assert root_version == fractal_version

    def test_citation_matches_latest_release(self):
        with (ROOT / "CITATION.cff").open(encoding="utf-8") as stream:
            citation = yaml.safe_load(stream)
        latest = _latest_changelog_version()
        assert citation["version"] == latest
        date.fromisoformat(citation["date-released"])

    def test_release_ledger_documents_the_current_version(self):
        current = _package_version("pyproject.toml")
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        assert f"## [{current}]" in text
