import json

import pytest

from constellation.engine import build_parser, load_manifest, main, plan, resonance_graph, score_repository


def load():
    return load_manifest()


class TestConstellationCorpus:
    def test_manifest_is_valid_and_unique(self):
        manifest = load()
        assert manifest["schema"] == "aleph.constellation.manifest.v1"
        assert len(manifest["repositories"]) == 28
        assert len({item["name"] for item in manifest["repositories"]}) == 28

    def test_scores_are_bounded_and_classified(self):
        scores = [score_repository(item)["score"] for item in load()["repositories"]]
        assert all(0 <= score <= 100 for score in scores)

    def test_plan_recommends_integrations(self):
        result = plan(load())
        assert result["repositories"] == 28
        assert result["integrate_concept"] > 0
        assert result["corpus_hash"]

    def test_resonance_graph_links_each_repository_to_target(self):
        graph = resonance_graph(load())
        repo_nodes = [node["id"] for node in graph["nodes"] if node["kind"] == "repository"]
        assert len(repo_nodes) == 28
        assert all(edge["source"].startswith("repo:") for edge in graph["edges"])

    def test_invalid_manifest_fails_closed(self, tmp_path):
        bad = tmp_path / "manifest.json"
        bad.write_text(json.dumps({"schema": "wrong", "repositories": []}), encoding="utf-8")
        with pytest.raises(ValueError):
            load_manifest(bad)

    def test_cli_outputs_plan(self, capsys):
        assert main(["plan"]) == 0
        assert json.loads(capsys.readouterr().out)["repositories"] == 28

    def test_parser_supports_graph_command(self):
        assert build_parser().parse_args(["graph"]).command == "graph"
