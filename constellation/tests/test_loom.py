import json

from constellation.engine import build_parser, load_manifest, main, weave
from constellation.loom import render_loom


def load():
    return load_manifest()


class TestRitualLoom:
    def test_every_repository_becomes_a_three_gate_thread(self):
        ritual = weave(load())
        assert len(ritual["threads"]) == 28
        assert all(len(thread["gates"]) == 3 for thread in ritual["threads"])
        assert [gate["gate"] for gate in ritual["threads"][0]["gates"]] == ["contract", "adapter", "release"]

    def test_threads_are_batched_into_deterministic_waves(self):
        ritual = weave(load())
        assert [wave["phase"] for wave in ritual["waves"]] == list(range(1, 7))
        assert all(wave["threads"] for wave in ritual["waves"])
        assert all(len(wave["threads"]) <= 5 for wave in ritual["waves"])
        assert ritual["policy"]["max_threads_per_wave"] == 5

    def test_weave_is_reproducible(self):
        assert weave(load()) == weave(load())

    def test_markdown_contains_phase_and_release_gates(self):
        markdown = render_loom(weave(load()))
        assert "# Constellation Ritual Loom" in markdown
        assert "## Phase 1 —" in markdown
        assert "Release: Emit a deterministic witness" in markdown

    def test_cli_outputs_json_ritual(self, capsys):
        assert main(["weave"]) == 0
        ritual = json.loads(capsys.readouterr().out)
        assert ritual["schema"] == "aleph.constellation.ritual.v1"
        assert ritual["weave_hash"]

    def test_cli_supports_markdown_format(self, capsys):
        arguments = build_parser().parse_args(["weave", "--format", "markdown"])
        assert arguments.command == "weave"
        assert arguments.format == "markdown"
        assert main(["weave", "--format", "markdown"]) == 0
        assert capsys.readouterr().out.startswith("# Constellation Ritual Loom")
