import json

from bridges.concordance_engine import (
    TreatyPolicy,
    main,
    negotiate_treaty,
)


class TestConcordanceEngine:
    def test_default_lexical_policy_selects_minimum(self):
        report = negotiate_treaty(
            {"mode": "restore", "level": 10},
            {"mode": "observe", "level": 4},
            TreatyPolicy(default="lexical_min"),
        )

        assert report["merged_state"] == {"level": 4, "mode": "observe"}
        assert report["clause_count"] == 2
        assert report["matches_baseline"] is False
        assert report["matches_twin"] is True
        assert report["ratified"] is True

    def test_authority_can_favor_either_reality(self):
        policy = TreatyPolicy(
            default="lexical_min",
            authorities={"$.keep": -1.0, "$.replace": 1.0},
            default_authority_baseline=0.0,
            default_authority_twin=0.0,
        )
        report = negotiate_treaty(
            {"keep": "baseline", "replace": "baseline"},
            {"keep": "twin", "replace": "twin"},
            policy,
        )

        assert report["merged_state"] == {"keep": "baseline", "replace": "twin"}
        assert {clause["path"]: clause["resolution"] for clause in report["clauses"]} == {
            "$.keep": "baseline",
            "$.replace": "twin",
        }

    def test_union_merges_collections_without_overwriting(self):
        report = negotiate_treaty(
            {
                "tags": ["core", "safe"],
                "traits": {"color": "blue"},
                "scalar": 1,
            },
            {
                "tags": ["safe", "new"],
                "traits": {"size": "small"},
                "scalar": 2,
            },
            TreatyPolicy(default="union"),
        )
        merged = report["merged_state"]

        assert merged["tags"] == ["core", "safe", "new"]
        assert merged["traits"] == {"color": "blue", "size": "small"}
        assert merged["scalar"]["$concordance"]["baseline"] == 1

    def test_conflicts_can_be_preserved_rather_than_hidden(self):
        report = negotiate_treaty(
            {"truth": "baseline"},
            {"truth": "twin"},
            TreatyPolicy(overrides={"$.truth": "preserve_conflict"}),
        )
        clause = report["clauses"][0]

        assert report["preserved_conflicts"] == 1
        assert clause["resolved_value"]["$conflict"] == {
            "baseline": "baseline", "twin": "twin",
        }
        assert report["merged_state"]["truth"]["$conflict"]["baseline"] == "baseline"

    def test_array_removals_apply_in_reverse_index_order(self):
        report = negotiate_treaty(
            {"sequence": ["remove-a", "keep-b", "remove-c", "keep-d"]},
            {"sequence": ["keep-b", "keep-d"]},
            TreatyPolicy(default="twin"),
        )

        assert report["merged_state"] == {"sequence": ["keep-b", "keep-d"]}
        operations = [clause["operation"] for clause in report["clauses"]]
        assert operations.count("changed") == 2
        assert operations.count("removed") == 2

    def test_treaty_hash_is_deterministic(self):
        baseline = {"agents": {"scout": {"trust": 1}}}
        twin = {"agents": {"scout": {"trust": 3}, "new": True}}
        policy = TreatyPolicy(
            overrides={"$.agents.new": "twin"},
            authorities={"$.agents.scout": -1},
        )
        first = negotiate_treaty(baseline, twin, policy)
        second = negotiate_treaty(baseline, twin, policy)

        assert first == second
        assert first["treaty_hash"] == second["treaty_hash"]

    def test_cli_forges_atomic_treaty_artifact(self, tmp_path):
        spec = tmp_path / "states.json"
        output = tmp_path / "treaty.json"
        spec.write_text(json.dumps({
            "baseline_state": {"value": "baseline", "removed": True},
            "twin_state": {"value": "twin"},
            "policy": {
                "overrides": {"$.value": "lexical_max"},
                "authorities": {"$.removed": -1},
            },
        }), encoding="utf-8")
        assert main(["forge", "--spec", str(spec), "--output", str(output)]) == 0
        report = json.loads(output.read_text())

        assert report["ratified"] is True
        assert report["merged_state"] == {"value": "twin"}
        assert report["treaty_hash"]
