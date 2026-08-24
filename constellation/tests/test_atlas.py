import json

from constellation.atlas import compile_atlas, render_atlas
from constellation.engine import load_manifest, main
from constellation.loom import rehearse, weave
from constellation.recovery import recover
from constellation.treaties import negotiate


def load():
    return load_manifest()


class TestConstellationAtlas:
    def test_compiles_complete_pipeline(self):
        atlas = compile_atlas(load())
        assert atlas["schema"] == "aleph.constellation.atlas.v1"
        assert atlas["summaries"] == {
            "repositories": 28,
            "systems": 9,
            "threads": 28,
            "passed": 9,
            "rolled_back": 9,
            "quarantined": 10,
            "braids": 5,
            "retry_orbits": 9,
            "treaties": 5,
            "ratified_treaties": 5,
        }

    def test_source_hashes_match_pipeline_stages(self):
        manifest = load()
        ritual = weave(manifest)
        rehearsal = rehearse(ritual)
        recovery = recover(ritual, rehearsal)
        treaties = negotiate(recovery)
        atlas = compile_atlas(manifest)
        assert atlas["source_hashes"] == {
            "corpus_hash": atlas["source_hashes"]["corpus_hash"],
            "graph_hash": atlas["source_hashes"]["graph_hash"],
            "weave_hash": ritual["weave_hash"],
            "rehearsal_hash": rehearsal["rehearsal_hash"],
            "recovery_hash": recovery["recovery_hash"],
            "treaty_hash": treaties["treaty_hash"],
        }

    def test_every_braid_has_a_ratified_treaty_view(self):
        atlas = compile_atlas(load())
        assert len(atlas["braids"]) == 5
        assert all(braid["treaty_status"] == "ratified" for braid in atlas["braids"])
        assert all(braid["treaty_signature"] for braid in atlas["braids"])
        assert len({braid["braid_id"] for braid in atlas["braids"]}) == 5

    def test_html_contains_all_concepts_without_scripting(self):
        html = render_atlas(compile_atlas(load()))
        assert "<!doctype html>" in html.lower()
        assert html.count('class="concept-node"') == 28
        assert 'data-name="astral-forge"' in html
        assert "<script" not in html.lower()
        assert "http://" not in html and "https://" not in html

    def test_dynamic_content_is_escaped(self):
        manifest = load()
        manifest["repositories"][0]["name"] = "<script>alert(1)</script>"
        html = render_atlas(compile_atlas(manifest))
        assert "<script>alert(1)</script>" not in html
        assert "&lt;script&gt;" in html

    def test_html_is_deterministic(self):
        first = render_atlas(compile_atlas(load()))
        second = render_atlas(compile_atlas(load()))
        assert first == second

    def test_cli_json_mode_outputs_model(self, capsys):
        assert main(["atlas", "--format", "json"]) == 0
        atlas = json.loads(capsys.readouterr().out)
        assert atlas["experiment"] == "constellation-atlas"
        assert atlas["atlas_hash"]

    def test_cli_html_file_output_is_atomic_manifest(self, tmp_path, capsys):
        output = tmp_path / "nested" / "constellation-atlas.html"
        assert main(["atlas", "--output", str(output)]) == 0
        result = json.loads(capsys.readouterr().out)
        expected = compile_atlas(load())
        assert output.exists()
        assert result == {"ok": True, "output": str(output), "atlas_hash": expected["atlas_hash"]}
        assert render_atlas(expected) == output.read_text(encoding="utf-8")
