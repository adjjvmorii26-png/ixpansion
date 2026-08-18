#!/usr/bin/env python3
"""Raft-inspired consensus with Ed25519 votes + Merkle-DAG commit."""
from __future__ import annotations
import json, uuid
from typing import Any, Dict, List, Optional
from node_auth import NodeIdentity, make_signed, verify_signed
from swarm_merkle_crdt import MerkleCRDT

class ConsensusNode:
    def __init__(self, node_id: Optional[str] = None, peers: Optional[List[str]] = None):
        self.identity = NodeIdentity(node_id)
        self.node_id = self.identity.node_id
        self.peers = set(peers or [])
        self.term = 0
        self.voted_for: Optional[str] = None
        self.leader: Optional[str] = None
        self.log: List[dict] = []
        self.commit_index = -1
        self.merkle = MerkleCRDT(self.node_id)
        self.known_pubs: Dict[str, str] = {self.node_id: self.identity.public_b64()}
        self.state: Dict[str, Any] = {}

    def members(self):
        return sorted(set(self.peers) | {self.node_id})

    def quorum(self):
        return len(self.members()) // 2 + 1

    def request_vote(self):
        self.term += 1
        self.voted_for = self.node_id
        return make_signed(self.identity, "raft.RequestVote", {
            "term": self.term, "candidate": self.node_id, "last_log_index": len(self.log) - 1,
        })

    def handle_vote_request(self, msg):
        ok, reason = verify_signed(msg, self.known_pubs)
        if not ok:
            return make_signed(self.identity, "raft.VoteReject", {"reason": reason})
        payload = msg["payload"]
        term, cand = payload["term"], payload["candidate"]
        if term < self.term:
            return make_signed(self.identity, "raft.VoteReject", {"term": self.term})
        if term > self.term:
            self.term, self.voted_for, self.leader = term, None, None
        if self.voted_for in (None, cand):
            self.voted_for = cand
            return make_signed(self.identity, "raft.VoteGrant", {
                "term": self.term, "voter": self.node_id, "candidate": cand,
            })
        return make_signed(self.identity, "raft.VoteReject", {"term": self.term})

    def become_leader(self, grants: int) -> bool:
        if grants >= self.quorum():
            self.leader = self.node_id
            return True
        return False

    def propose(self, key: str, value: Any):
        entry = {"index": len(self.log), "term": self.term, "key": key, "value": value, "id": str(uuid.uuid4())[:8]}
        self.log.append(entry)
        return make_signed(self.identity, "raft.AppendEntries", {
            "term": self.term, "leader": self.node_id, "entries": [entry], "leader_commit": self.commit_index,
        })

    def handle_append(self, msg):
        ok, reason = verify_signed(msg, self.known_pubs)
        if not ok:
            return make_signed(self.identity, "raft.AppendReject", {"reason": reason})
        payload = msg["payload"]
        if payload["term"] < self.term:
            return make_signed(self.identity, "raft.AppendReject", {"term": self.term})
        self.term = payload["term"]
        self.leader = payload.get("leader")
        for e in payload.get("entries", []):
            if e["index"] >= len(self.log):
                self.log.append(e)
            elif e["index"] < len(self.log) and self.log[e["index"]].get("id") != e.get("id"):
                self.log = self.log[: e["index"]] + [e]
        lc = payload.get("leader_commit", -1)
        while self.commit_index < lc and self.commit_index + 1 < len(self.log):
            self.commit_index += 1
            e = self.log[self.commit_index]
            self.state[e["key"]] = e["value"]
            self.merkle.put_register(e["key"], e["value"])
        return make_signed(self.identity, "raft.AppendOk", {"term": self.term, "match_index": len(self.log) - 1})

def simulate_election_and_commit():
    a = ConsensusNode("raft-a", ["raft-b", "raft-c"])
    b = ConsensusNode("raft-b", ["raft-a", "raft-c"])
    c = ConsensusNode("raft-c", ["raft-a", "raft-b"])
    for n in (a, b, c):
        for m in (a, b, c):
            n.known_pubs[m.node_id] = m.identity.public_b64()
    req = a.request_vote()
    grants = 1
    for n in (b, c):
        if n.handle_vote_request(req)["type"] == "raft.VoteGrant":
            grants += 1
    assert a.become_leader(grants)
    prop = a.propose("cluster_config", {"workers": 3, "mode": "trinity"})
    for n in (b, c):
        n.handle_append(prop)
    a.commit_index = 0
    a.state["cluster_config"] = a.log[0]["value"]
    a.merkle.put_register("cluster_config", a.log[0]["value"])
    # replicate commit
    for n in (b, c):
        n.commit_index = 0
        n.state["cluster_config"] = n.log[0]["value"]
    return {"leader": a.leader, "term": a.term, "quorum": a.quorum(), "b_state": b.state, "c_state": c.state, "merkle_root": a.merkle.root()}

if __name__ == "__main__":
    print(json.dumps(simulate_election_and_commit(), indent=2))
                                                                  
