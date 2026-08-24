import json

from constellation.engine import build_parser, load_manifest, main
from constellation.loom import rehearse, weave


def load():
    return load_manifest()


class TestShadowRehearsal:
    def test_every_thread_has_exactly_one_outcome(self):
        rehearsal = rehearse(weave(load()))
        assert rehearsal["schema"] == "aleph.constellation.rehearsal.v1"
        assert rehearsal["summary"]["threads"] == 28
        outcomes = sum(
            len(wave[field])
            for wave in rehearsal["waves"]
            for field in ("passed", "rolled_back", "quarantined")
        )
        assert outcomes == 28

    def test_nested_target_collisions_are_quarantined(self):
        rehearsal = rehearse(weave(load()))
        quarantined = {
            name
            for wave in rehearsal["waves"]
            for name in wave["quarantined"]
        }
        assert {"astral-forge", "metamorph-forge", "multiself-engine", "quantum-folio"}.issubset(quarantined)
        assert rehearsal["summary"]["collision_groups"] >= 5

    def test_rollback_ledger_is_complete_and_witnessed(self):
        rehearsal = rehearse(weave(load()))
        ledger = rehearsal["rollback_ledger"]
        assert len(ledger) == 28
        assert len({entry["thread"] for entry in ledger}) == 28
        failures = [entry for entry in ledger if entry.get("status") == "rolled_back"]
        assert failures
        assert all(entry["witness"] for entry in failures)

    def test_wave_batches_remain_bounded(self):
        rehearsal = rehearse(weave(load()))
        assert len(rehearsal["waves"]) == 6
        assert all(len(wave["threads"] if "threads" in wave else wave["passed"] + wave["rolled_back"] + wave["quarantined"]) <= 5 for wave in rehearsal["waves"])

    def test_rehearsal_is_deterministic(self):
        ritual = weave(load())
        assert rehearse(ritual) == rehearse(ritual)

    def test_markdown_reports_summary_and_ledger(self):
        from constellation.loom import render_rehearsal

        markdown = render_rehearsal(rehearse(weave(load())))
        assert "# Constellation Shadow Rehearsal" in markdown
        assert "| Phase | Status | Passed | Rolled Back | Quarantined |" in markdown
        assert "## Rollback Ledger" in markdown

    def test_cli_outputs_json_and_supports_markdown(self, capsys):
        assert main(["rehearse"]) == 0
        rehearsal = json.loads(capsys.readouterr().out)
        assert rehearsal["experiment"] == "ritual-shadow-rehearsal"

        arguments = build_parser().parse_args(["rehearse", "--format", "markdown"])
        assert arguments.command == "rehearse"
        assert main(["rehearse", "--format", "markdown"]) == 0
        assert capsys.readouterr().out.startswith("# Constellation Shadow Rehearsal")
