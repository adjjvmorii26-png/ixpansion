import json

import echolalia
import interloper
import schism
import tide_clock
import listening_post


class TestProjectLabs:
    def test_echolalia_preserves_all_generations(self):
        result = echolalia.echo("lattice", 4)
        assert [voice["generation"] for voice in result["voices"]] == [0, 1, 2, 3, 4]
        assert result["final"] == result["voices"][-1]["text"]

    def test_schism_keeps_a_treaty_path_between_factions(self):
        result = schism.demo()
        assert result["dawn"] == ["keystone", "lantern"]
        assert result["dusk"] == ["moth", "salt"]
        assert result["treaty_possible"] is True

    def test_invalid_threshold_fails_closed(self):
        import pytest
        with pytest.raises(ValueError):
            schism.schism([], threshold=2)

    def test_tide_clock_cycles_backwards_and_forwards(self):
        forward = tide_clock.read(3)
        backward = tide_clock.read(-5)
        assert forward["phase"] == "flood"
        assert backward["phase"] == forward["phase"]
        assert backward["height"] == forward["height"]

    def test_interloper_identifies_distant_point(self):
        result = interloper.inspect()
        assert result["interloper"]["id"] == "interloper"
        assert result["confidence"] > 0

    def test_listening_post_aggregates_four_labs(self):
        result = listening_post.listen()
        assert result["listening_post"]["channels"] == 4
        assert result["listening_post"]["state"] == "receiving"
        assert all(signal["ok"] for signal in result["signals"])

    def test_lab_scripts_emit_json_objects(self, capsys):
        for module in (echolalia, schism, tide_clock, interloper, listening_post):
            exit_code = module.main([])
            captured = capsys.readouterr().out
            assert exit_code == 0
            assert isinstance(json.loads(captured), dict)
