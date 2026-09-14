"""Wave 95 — Ritual Governance.

Entropy rituals (Wave 92) become formal governance protocols.
The organism makes decisions through ritualized processes:
proposals are raised, votes are cast with weighted influence,
quorum gates must be passed, and enacted decisions amend the
organism's policy. Governance becomes a living ceremony.

Builds upon:
- Wave 92: Entropy Rituals Scheduler (ritual primitives)
- Wave 90: Axiom Forge (governance aligns with principles)
- Wave 85: Adaptive Regulation (modes contextualize governance)
"""
from __future__ import annotations
import json, time, hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave95_ritual_governance.json"

QUORUM_DEFAULT = 0.6          # fraction of active members needed to pass
INFLUENCE_DECAY = 0.02        # weighting toward mature members


class GovernanceProposal:
    """A proposal subject to ritual governance."""

    def __init__(self, proposal_id: str, title: str, body: str,
                 sponsor: str, kind: str = "policy"):
        self.proposal_id = proposal_id
        self.title = title
        self.body = body
        self.sponsor = sponsor
        self.kind = kind          # policy | ritual | axiom | structure
        self.votes: Dict[str, float] = {}
        self.created_at = time.time()
        self.closed_at: Optional[float] = None
        self.status = "open"      # open | quorum-met | passed | failed | enacted
        self.result: Optional[str] = None

    def cast_vote(self, member: str, weight: float, choice: str) -> bool:
        if self.status != "open":
            return False
        value = weight if choice in ("yes", "aye", "for") else -weight
        if choice in ("yes", "aye", "for", "no", "nay", "against"):
            self.votes[member] = value
            return True
        return False

    def tally(self) -> Tuple[float, float, int]:
        total = sum(abs(v) for v in self.votes.values())
        support = sum(v for v in self.votes.values() if v > 0)
        return support, total, len(self.votes)

    def evaluate(self, members: Dict[str, float]) -> str:
        """Evaluate against member registry and quorum."""
        support, total, count = self.tally()
        quorum = QUORUM_DEFAULT * len(members)
        if count < quorum:
            self.status = "open"
            return self.status
        if total == 0:
            self.status = "failed"
            return self.status
        majority = support / total
        self.status = "passed" if majority >= QUORUM_DEFAULT else "failed"
        self.result = "adopted" if self.status == "passed" else "rejected"
        return self.status

    def to_dict(self) -> dict:
        support, total, count = self.tally()
        return {
            "proposal_id": self.proposal_id,
            "title": self.title,
            "sponsor": self.sponsor,
            "kind": self.kind,
            "status": self.status,
            "result": self.result,
            "votes": len(self.votes),
            "support_weight": round(support, 4),
            "total_weight": round(total, 4),
            "created_at": round(self.created_at, 4),
        }


class RitualGovernance:
    """Governance body: members, proposals, enactments."""

    def __init__(self):
        self.members: Dict[str, float] = {}   # member -> influence weight
        self.proposals: Dict[str, GovernanceProposal] = {}
        self.enacted: List[dict] = []
        self.next_id = 1

    def register_member(self, member: str, weight: float = 1.0) -> bool:
        if member in self.members:
            return False
        self.members[member] = max(0.0, min(10.0, weight))
        return True

    def propose(self, title: str, body: str, sponsor: str,
                kind: str = "policy") -> GovernanceProposal:
        if sponsor not in self.members:
            self.register_member(sponsor, 1.0)
        pid = f"P{self.next_id:03d}"
        self.next_id += 1
        proposal = GovernanceProposal(pid, title, body, sponsor, kind)
        self.proposals[pid] = proposal
        return proposal

    def vote(self, proposal_id: str, member: str, choice: str) -> bool:
        proposal = self.proposals.get(proposal_id)
        if proposal is None:
            return False
        weight = self.members.get(member, 0.0)
        return proposal.cast_vote(member, weight, choice)

    def close(self, proposal_id: str) -> str:
        """Evaluate and optionally enact a proposal."""
        proposal = self.proposals.get(proposal_id)
        if proposal is None:
            return "unknown"
        status = proposal.evaluate(self.members)
        if status == "passed":
            proposal.status = "enacted"
            proposal.closed_at = time.time()
            self.enacted.append(proposal.to_dict())
        elif status == "failed":
            proposal.closed_at = time.time()
        return status

    def governance_state(self) -> Dict[str, Any]:
        open_count = sum(1 for p in self.proposals.values() if p.status == "open")
        enacted_count = len(self.enacted)
        return {
            "members": len(self.members),
            "open_proposals": open_count,
            "enacted_decisions": enacted_count,
            "total_proposals": len(self.proposals),
            "quorum": QUORUM_DEFAULT,
        }

    def coherence_vitals(self) -> Dict[str, Any]:
        state = self.governance_state()
        return {
            "wave": 95,
            **state,
            "average_influence": round(
                sum(self.members.values()) / max(len(self.members), 1), 4
            ),
            "last_action": round(time.time(), 4),
        }


def _load() -> RitualGovernance:
    """Load governance state from living state file."""
    gov = RitualGovernance()
    if STATE_FILE.exists():
        try:
            data = json.loads(STATE_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            data = {}
        gov.members = data.get("members", {})
        gov.next_id = data.get("next_id", 1)
        for entry in data.get("proposals", []):
            prop = GovernanceProposal(
                entry["proposal_id"], entry["title"], entry.get("body", ""),
                entry["sponsor"], entry.get("kind", "policy"),
            )
            prop.votes = entry.get("votes", {})
            prop.status = entry.get("status", "open")
            prop.result = entry.get("result")
            prop.closed_at = entry.get("closed_at")
            prop.created_at = entry.get("created_at", prop.created_at)
            gov.proposals[prop.proposal_id] = prop
        gov.enacted = data.get("enacted", [])
    return gov


def _save(gov: RitualGovernance) -> None:
    """Persist governance state to living state file."""
    data = {
        "members": gov.members,
        "next_id": gov.next_id,
        "proposals": [
            {
                **prop.to_dict(),
                "body": prop.body,
                "votes": prop.votes,
                "closed_at": prop.closed_at,
            }
            for prop in gov.proposals.values()
        ],
        "enacted": gov.enacted,
    }
    STATE_FILE.write_text(json.dumps(data, indent=2))


def handler(req: dict) -> dict:
    """Wave 95 handler: ritual governance operations."""
    action = req.get("action", "status")
    gov = _load()

    if action == "status":
        return {
            "action": "status",
            "wave": 95,
            "governance": gov.coherence_vitals(),
            "message": "Ritual governance status",
        }

    if action == "register":
        member = req.get("member", "")
        weight = float(req.get("weight", 1.0))
        if not member:
            return {"ok": False, "error": "member required"}
        added = gov.register_member(member, weight)
        _save(gov)
        return {
            "action": "register",
            "wave": 95,
            "member": member,
            "added": added,
            "members": len(gov.members),
            "message": f"Registered {member}" if added else f"{member} already registered",
        }

    if action == "propose":
        title = req.get("title", "")
        sponsor = req.get("sponsor", "organism")
        if not title:
            return {"ok": False, "error": "title required"}
        proposal = gov.propose(title, req.get("body", ""), sponsor, req.get("kind", "policy"))
        _save(gov)
        return {
            "action": "propose",
            "wave": 95,
            "proposal": proposal.to_dict(),
            "message": f"Proposal {proposal.proposal_id} raised by {sponsor}",
        }

    if action == "vote":
        pid = req.get("proposal_id", "")
        member = req.get("member", "")
        choice = req.get("choice", "")
        ok = gov.vote(pid, member, choice)
        if ok:
            _save(gov)
        return {
            "action": "vote",
            "wave": 95,
            "recorded": ok,
            "message": f"Vote recorded for {member}" if ok else "Vote not recorded",
        }

    if action == "close":
        status = gov.close(req.get("proposal_id", ""))
        if status in ("passed", "failed"):
            _save(gov)
        return {
            "action": "close",
            "wave": 95,
            "status": status,
            "message": f"Proposal closed with status: {status}",
        }

    if action == "list":
        return {
            "action": "list",
            "wave": 95,
            "proposals": [p.to_dict() for p in gov.proposals.values()],
            "enacted": gov.enacted,
            "message": f"{len(gov.proposals)} proposals, {len(gov.enacted)} enacted",
        }

    return {"ok": False, "error": f"Unknown action: {action}"}


def coherence_vitals() -> dict:
    """Wave 95 vitals."""
    return RitualGovernance().coherence_vitals()
