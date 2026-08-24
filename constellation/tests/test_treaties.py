import json

import pytest

from constellation.engine import build_parser, load_manifest, main
from constellation.loom import rehearse, weave
from constellation.recovery import recover
from constellation.treaties import negotiate


def artifacts():
    ritual = weave(load_manifest())
    rehearsal = rehearse(ritual)
    recovery = recover(ritual, rehearsal)
    return recovery, negotiate(recovery)


class TestLaneTreaties:
    def test_schema_summary_and_ratification(self):
        _, treaties = artifacts()
        assert treaties["schema"] == "aleph.constellation.treaties.v1"
        assert treaties["summary"] == {
            "treaties": 5,
            "ratified": 5,
            "rejected": 0,
            "parties": 10,
            "clauses": 25,
        }
        assert all(treaty["status"] == "ratified" for treaty in treaties["treaties"])

    def test_every_braid_pair_is_covered_exactly_once(self):
        _, treaties = artifacts()
        expected_pairs = []
        for braid in treaties["treaties"]:
            names = sorted(party["thread"] for party in braid["parties"])
            expected_pairs.append(tuple(names))
        assert len(expected_pairs) == len(set(expected_pairs))
        assert len(expected_pairs) == 5

    def test_namespaces_and_clauses_give_consent(self):
        _, treaties = artifacts()
        for treaty in treaties["treaties"]:
            targets = [party["isolated_target"] for party in treaty["parties"]]
            assert len(targets) == len(set(targets))
            assert len(treaty["clauses"]) == 5
            assert all(clause["consent"] for clause in treaty["clauses"])
            assert treaty["signature"]

    def test_arbitration_roles_are_complementary(self):
        _, treaties = artifacts()
        for treaty in treaties["treaties"]:
            arbitration = next(clause for clause in treaty["clauses"] if clause["clause"] == "arbitration")
            first, second = [party["thread"] for party in treaty["parties"]]
            assert first in arbitration["terms"] and second in arbitration["terms"]
            assert first != second

    def test_negotiation_is_deterministic(self):
        assert artifacts()[1] == artifacts()[1]

    def test_invalid_recovery_fails_closed(self):
        with pytest.raises(ValueError):
            negotiate({"schema": "wrong"})

    def test_markdown_and_cli_surfaces(self, capsys):
        _, treaties = artifacts()
        from constellation.treaties import render_treaties

        markdown = render_treaties(treaties)
        assert "# Constellation Lane Treaties" in markdown
        assert "## Treaty `" in markdown
        assert "- Clauses:" in markdown

        assert main(["negotiate"]) == 0
        assert json.loads(capsys.readouterr().out)["schema"] == treaties["schema"]
        arguments = build_parser().parse_args(["negotiate", "--format", "markdown"])
        assert arguments.format == "markdown"
        assert main(["negotiate", "--format", "markdown"]) == 0
        assert capsys.readouterr().out.startswith("# Constellation Lane Treaties")
