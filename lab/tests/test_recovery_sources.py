import pytest

from lab.recovery_atlas import compile_atlas
from lab.recovery_quorum import convene
from lab.recovery_sources import RECOVERY_DERIVED_LEDGERS, source_ledgers
from lab.repair_dreams import weave
from lab.repair_theater import rehearse
from lab.runtime_vault import append_jsonl
from lab.temporal_paradox import resolve


def test_recovery_derived_ledger_boundary_is_complete():
    assert RECOVERY_DERIVED_LEDGERS == {
        "paradox-resolutions.jsonl",
        "repair-dreams.jsonl",
        "repair-theater.jsonl",
        "recovery-quorums.jsonl",
        "recovery-atlases.jsonl",
        "recovery-treaties.jsonl",
        "recovery-dossiers.jsonl",
    }


def test_explicit_sources_are_deduplicated_sorted_and_verified(tmp_path):
    first = tmp_path / "b.jsonl"
    second = tmp_path / "a.jsonl"
    append_jsonl(first, {"event_id": "one"})
    append_jsonl(second, {"event_id": "two"})
    assert source_ledgers([first, second, second]) == [second.resolve(), first.resolve()]
    with pytest.raises(ValueError, match="does not exist"):
        source_ledgers([tmp_path / "missing.jsonl"])


def test_default_recovery_chain_ignores_all_derived_feedback(tmp_path, monkeypatch):
    monkeypatch.setenv("NEXUS_LAB_RUNTIME", str(tmp_path))
    vault = tmp_path / "ledgers"
    vault.mkdir(parents=True, exist_ok=True)
    source_ledger = vault / "source.jsonl"
    append_jsonl(source_ledger, {
        "event_id": "clean-event", "subject_id": "agent", "tick": 1
    })

    # These deliberately contain contradictions; any boundary leak would turn them
    # into false input evidence for later recovery commands.
    derived_payloads = {
        "paradox-resolutions.jsonl": [{"event_id": "collision", "value": 1}],
        "repair-dreams.jsonl": [{"event_id": "collision", "value": 2}],
        "repair-theater.jsonl": [{"subject_id": "ghost", "tick": 9}],
        "recovery-quorums.jsonl": [{"subject_id": "ghost", "tick": 2}],
        "recovery-atlases.jsonl": [{"event_id": "collision", "value": 3}],
        "recovery-treaties.jsonl": [{"event_id": "collision", "value": 4}],
        "recovery-dossiers.jsonl": [{"subject_id": "ghost", "tick": 1}],
    }
    for name, records in derived_payloads.items():
        path = vault / name
        for record in records:
            append_jsonl(path, record)

    diagnosis = resolve(record=False)
    assert set(diagnosis["sources"]["audits"]) == {"source.jsonl"}
    assert diagnosis["verdict"] == "coherent"

    dream = weave(record=False)
    assert dream["verdict"] == "lucid"
    assert dream["operation_count"] == 0

    theater = rehearse(record=False)
    assert theater["stage_count"] == 0

    quorum = convene(record=False)
    assert quorum["scene_count"] == 0

    atlas = compile_atlas(record=False)
    assert atlas["sources"]["ledger_count"] == 1
    assert atlas["upstream"]["paradox"]["count"] == 0
    assert atlas["verdict"] == "dormant"
