import json

import pytest

from bridges.astral_braid import AstralBraidConservatory, ConsentContract
from bridges.chrono_mycelium import AstralTranscript
from bridges.proof_garden import (
    EMPTY_ROOT,
    ProofGarden,
    build_parser,
    leaf_digest,
    main,
    merkle_proof,
    merkle_root,
    verify_proof,
)
from mycelium.cognition.dream_compiler import DreamCompiler, build_demo_network


def fixed_time():
    return "2026-08-23T00:00:00+00:00"


def braid_report(tmp_path, seed=29):
    dream = DreamCompiler().compile(build_demo_network(seed, steps=10))
    return AstralBraidConservatory(
        AstralTranscript(tmp_path / "bus.jsonl"), clock=fixed_time
    ).braid(dream)


def quarantined_report(tmp_path):
    dream = DreamCompiler().compile(build_demo_network(31, steps=10))
    contract = ConsentContract(minimum_confidence=1.01)
    return AstralBraidConservatory(
        AstralTranscript(tmp_path / "quarantine-bus.jsonl"),
        contract,
        clock=fixed_time,
    ).braid(dream)


class TestMerkleCore:
    def test_empty_and_single_roots_are_stable(self):
        assert merkle_root([]) == EMPTY_ROOT

    def test_audit_path_verifies_for_each_leaf(self):
        values = [f"leaf-{index}".encode() for index in range(5)]
        leaves = [leaf_digest(value) for value in values]
        root = merkle_root(leaves)

        for index, leaf in enumerate(leaves):
            assert verify_proof(leaf, merkle_proof(leaves, index), root, index)

    def test_rejects_tampered_audit_leaf(self):
        leaves = [leaf_digest(b"alpha"), leaf_digest(b"beta")]
        proof = merkle_proof(leaves, 0)

        assert not verify_proof(leaf_digest(b"gamma"), proof, merkle_root(leaves), 0)


class TestProofGarden:
    def test_plants_promotion_with_valid_growth_ring(self, tmp_path):
        garden = ProofGarden(tmp_path / "garden.jsonl", clock=fixed_time)
        result = garden.plant(braid_report(tmp_path))

        assert result["verified"] is True
        assert result["record"]["sequence"] == 1
        assert result["record"]["previous_root"] == EMPTY_ROOT
        assert result["record"]["kind"] == "braid.promoted"

    def test_second_ring_links_to_previous_root(self, tmp_path):
        garden = ProofGarden(tmp_path / "garden.jsonl", clock=fixed_time)
        first = garden.plant(braid_report(tmp_path))["record"]
        second = garden.plant(quarantined_report(tmp_path))["record"]

        assert second["sequence"] == 2
        assert second["previous_root"] == first["root"]
        assert second["kind"] == "braid.quarantined"
        assert second["root"] != first["root"]

    def test_portable_packet_verifies_without_ledger_access(self, tmp_path):
        garden = ProofGarden(tmp_path / "garden.jsonl", clock=fixed_time)
        garden.plant(braid_report(tmp_path))
        garden.plant(quarantined_report(tmp_path))
        packet = garden.prove(1)

        assert packet["ledger_size"] == 1
        assert garden.verify_packet(packet)["verified"] is True

    def test_rejects_tampered_packet_event(self, tmp_path):
        garden = ProofGarden(tmp_path / "garden.jsonl", clock=fixed_time)
        garden.plant(braid_report(tmp_path))
        packet = garden.prove(1)
        packet["event"]["candidate_count"] += 1

        with pytest.raises(ValueError, match="Merkle verification"):
            garden.verify_packet(packet)

    def test_detects_corrupted_growth_ring(self, tmp_path):
        ledger = tmp_path / "garden.jsonl"
        garden = ProofGarden(ledger, clock=fixed_time)
        garden.plant(braid_report(tmp_path))
        record = json.loads(ledger.read_text())
        record["source_dream_id"] = "tampered-dream"
        ledger.write_text(json.dumps(record) + "\n")

        with pytest.raises(ValueError, match="failed verification"):
            garden.audit()

    def test_rejects_certificate_that_does_not_match_report(self, tmp_path):
        report = braid_report(tmp_path)
        report["certificate_hash"] = "0" * 64
        garden = ProofGarden(tmp_path / "garden.jsonl", clock=fixed_time)

        with pytest.raises(ValueError, match="certificate hash"):
            garden.plant(report)

    def test_rejects_empty_braid_report(self, tmp_path):
        garden = ProofGarden(tmp_path / "garden.jsonl", clock=fixed_time)

        with pytest.raises(ValueError, match="not produced"):
            garden.plant({"experiment": "something-else"})

    def test_audit_counts_promotions_and_quarantines(self, tmp_path):
        ledger = tmp_path / "garden.jsonl"
        garden = ProofGarden(ledger, clock=fixed_time)
        garden.plant(braid_report(tmp_path))
        garden.plant(quarantined_report(tmp_path))
        latest_root = json.loads(ledger.read_text().splitlines()[-1])["root"]

        assert garden.audit() == {
            "verified": True,
            "events": 2,
            "latest_root": latest_root,
            "promoted": 1,
            "quarantined": 1,
        }

    def test_cli_can_plant_prove_and_verify(self, tmp_path, capsys):
        report_path = tmp_path / "report.json"
        report_path.write_text(json.dumps(braid_report(tmp_path)), encoding="utf-8")
        ledger = tmp_path / "garden.jsonl"
        packet_path = tmp_path / "packet.json"

        assert main(["--ledger", str(ledger), "plant", "--report", str(report_path), "--output", str(packet_path)]) == 0
        capsys.readouterr()
        assert main(["--ledger", str(ledger), "prove", "--sequence", "1", "--output", str(packet_path)]) == 0
        capsys.readouterr()
        assert main(["--ledger", str(ledger), "verify", "--packet", str(packet_path)]) == 0
        assert json.loads(capsys.readouterr().out)["verified"] is True
        assert build_parser().parse_args(["--ledger", "x", "audit"]).command == "audit"
