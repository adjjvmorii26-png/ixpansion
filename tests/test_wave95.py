"""Tests for Wave 95 — Ritual Governance."""
import pytest
from api.wave95_ritual_governance import (
    GovernanceProposal, RitualGovernance, coherence_vitals, handler,
)


def _governance_with_members() -> RitualGovernance:
    gov = RitualGovernance()
    gov.register_member("aleph", 1.0)
    gov.register_member("luma", 0.9)
    gov.register_member("axiom", 0.8)
    return gov


class TestGovernanceProposal:
    def test_cast_vote(self):
        p = GovernanceProposal("P1", "t", "b", "aleph")
        assert p.cast_vote("luma", 0.9, "aye") is True
        assert p.votes == {"luma": 0.9}

    def test_cast_invalid_choice(self):
        p = GovernanceProposal("P1", "t", "b", "aleph")
        assert p.cast_vote("luma", 0.9, "maybe") is False

    def test_no_votes_after_close(self):
        p = GovernanceProposal("P1", "t", "b", "aleph")
        p.status = "passed"
        assert p.cast_vote("luma", 0.9, "aye") is False

    def test_tally(self):
        p = GovernanceProposal("P1", "t", "b", "aleph")
        p.cast_vote("a", 1.0, "aye")
        p.cast_vote("b", 0.5, "nay")
        support, total, count = p.tally()
        assert support == 1.0
        assert total == 1.5
        assert count == 2

    def test_evaluate_quorum_not_met(self):
        p = GovernanceProposal("P1", "t", "b", "aleph")
        p.cast_vote("a", 1.0, "aye")
        assert p.evaluate({"a": 1.0, "b": 1.0, "c": 1.0}) == "open"


class TestRitualGovernance:
    def test_register_member(self):
        gov = RitualGovernance()
        assert gov.register_member("aleph", 1.0) is True
        assert gov.register_member("aleph", 1.0) is False

    def test_propose_auto_registers_sponsor(self):
        gov = RitualGovernance()
        p = gov.propose("title", "body", "newbie")
        assert "newbie" in gov.members
        assert p.sponsor == "newbie"

    def test_vote_and_close_passes(self):
        gov = _governance_with_members()
        p = gov.propose("Expand", "Evolve", "aleph", "structure")
        gov.vote(p.proposal_id, "luma", "aye")
        gov.vote(p.proposal_id, "axiom", "aye")
        status = gov.close(p.proposal_id)
        assert status == "passed"
        assert p.status == "enacted"
        assert len(gov.enacted) == 1

    def test_vote_and_close_fails(self):
        gov = _governance_with_members()
        p = gov.propose("Shrink", "Cut", "aleph")
        gov.vote(p.proposal_id, "luma", "nay")
        gov.vote(p.proposal_id, "axiom", "nay")
        status = gov.close(p.proposal_id)
        assert status == "failed"

    def test_close_unknown(self):
        gov = RitualGovernance()
        assert gov.close("nope") == "unknown"

    def test_vitals(self):
        gov = _governance_with_members()
        vitals = gov.coherence_vitals()
        assert vitals["wave"] == 95
        assert vitals["members"] == 3
        assert "quorum" in vitals


import json, os

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "wave95_ritual_governance.json")


@pytest.fixture(autouse=True)
def _reset_wave95_state():
    """Reset wave95 state before each test to avoid cross-run pollution."""
    gov = RitualGovernance()
    from api.wave95_ritual_governance import _save
    _save(gov)
    yield


class TestHandler:
    def test_status(self):
        out = handler({"action": "status"})
        assert out["action"] == "status"
        assert out["wave"] == 95

    def test_register(self):
        out = handler({"action": "register", "member": "cythara", "weight": 1.0})
        assert out["added"] is True

    def test_propose(self):
        out = handler({"action": "propose", "title": "New realm", "sponsor": "aleph"})
        assert out["proposal"]["status"] == "open"

    def test_vote(self):
        gov_out = handler({"action": "propose", "title": "V", "sponsor": "aleph"})
        pid = gov_out["proposal"]["proposal_id"]
        out = handler({"action": "vote", "proposal_id": pid, "member": "aleph", "choice": "aye"})
        assert out["recorded"] is True

    def test_close(self):
        gov = _governance_with_members()
        p = gov.propose("X", "Y", "aleph")
        gov.vote(p.proposal_id, "ale", "aye")  # unknown member, weight 0
        out = handler({"action": "close", "proposal_id": "none"})
        assert out["status"] == "unknown"

    def test_list(self):
        out = handler({"action": "list"})
        assert out["action"] == "list"

    def test_unknown_action(self):
        out = handler({"action": "bogus"})
        assert out["ok"] is False

    def test_coherence_vitals(self):
        vitals = coherence_vitals()
        assert vitals["wave"] == 95
