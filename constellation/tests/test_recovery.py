import json

import pytest

from constellation.engine import build_parser, load_manifest, main
from constellation.loom import rehearse, weave
from constellation.recovery import recover


def artifacts():
    ritual = weave(load_manifest())
    rehearsal = rehearse(ritual)
    return ritual, rehearsal, recover(ritual, rehearsal)


class TestRecoveryBraids:
    def test_recovery_schema_and_summary_are_complete(self):
        _, _, recovery = artifacts()
        assert recovery["schema"] == "aleph.constellation.recovery.v1"
        assert recovery["summary"] == {
            "braids": 5,
            "lanes": 10,
            "quarantined_covered": 10,
            "retry_orbits": 9,
            "max_retry_attempts": 3,
        }

    def test_every_quarantined_thread_has_one_isolated_lane(self):
        ritual, rehearsal, recovery = artifacts()
        quarantined = {name for wave in rehearsal["waves"] for name in wave["quarantined"]}
        lanes = [lane for braid in recovery["braids"] for lane in braid["lanes"]]
        assert {lane["thread"] for lane in lanes} == quarantined
        assert len(lanes) == len(quarantined)
        assert len({lane["isolated_target"] for lane in lanes}) == len(lanes)
        assert all(lane["isolated_target"].startswith("braid/") for lane in lanes)

    def test_braid_lanes_never_overlap_each_other(self):
        from constellation.loom import _targets_overlap

        _, _, recovery = artifacts()
        targets = [lane["isolated_target"] for braid in recovery["braids"] for lane in braid["lanes"]]
        assert not any(_targets_overlap(left, right) for left in targets for right in targets if left != right)

    def test_every_rollback_has_a_three_attempt_orbit(self):
        _, rehearsal, recovery = artifacts()
        rolled_back = {
            entry["thread"]
            for entry in rehearsal["rollback_ledger"]
            if entry.get("status") == "rolled_back"
        }
        orbits = recovery["retry_orbits"]
        assert {orbit["thread"] for orbit in orbits} == rolled_back
        assert all(len(orbit["attempts"]) == 3 for orbit in orbits)
        assert all(orbit["failed_gate"] in {"contract", "adapter", "release"} for orbit in orbits)

    def test_recovery_is_deterministic(self):
        first = recover(*artifacts()[:2])
        second = recover(*artifacts()[:2])
        assert first == second

    def test_invalid_rehearsal_fails_closed(self):
        ritual, _, _ = artifacts()
        with pytest.raises(ValueError):
            recover(ritual, {"schema": "wrong"})

    def test_markdown_and_cli_surfaces(self, capsys):
        _, _, recovery = artifacts()
        from constellation.recovery import render_recovery

        markdown = render_recovery(recovery)
        assert "# Constellation Recovery Braids" in markdown
        assert "## Isolated Collision Braids" in markdown
        assert "## Witnessed Retry Orbits" in markdown

        assert main(["recover"]) == 0
        assert json.loads(capsys.readouterr().out)["schema"] == recovery["schema"]
        arguments = build_parser().parse_args(["recover", "--format", "markdown"])
        assert arguments.format == "markdown"
        assert main(["recover", "--format", "markdown"]) == 0
        assert capsys.readouterr().out.startswith("# Constellation Recovery Braids")
