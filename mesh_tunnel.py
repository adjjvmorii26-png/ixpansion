#!/usr/bin/env python3
"""
Zero-Trust Mesh Tunnel (Noise-inspired)
X25519 handshake + ChaCha20-Poly1305 record layer for gossip peers.
"""
from __future__ import annotations
import base64, json, os, time
from typing import Dict, Optional, Tuple
from swarm_secure_channel import SessionKeys, ReplayGuard, make_signed_protected, verify_signed_protected
from node_auth import NodeIdentity

class MeshTunnel:
    """Per-peer encrypted channel after Noise-like XX pattern (simplified)."""

    def __init__(self, node_id: Optional[str] = None, token: str = ""):
        self.identity = NodeIdentity(node_id)
        self.node_id = self.identity.node_id
        self.token = token
        self.session = SessionKeys()
        self.replay = ReplayGuard(window_sec=10)
        self.peers: Dict[str, dict] = {}  # peer_id -> {pub_static, session_ready}

    def handshake_init(self) -> dict:
        """Message 1: e (ephemeral pub) + signed identity."""
        return make_signed_protected(
            self.identity,
            "noise.hello",
            {"e": self.session.public_b64(), "node_id": self.node_id},
            token=self.token,
            replay=self.replay,
        )

    def handshake_respond(self, hello_msg: dict) -> Tuple[dict, bool]:
        pubs = {self.node_id: self.identity.public_b64()}
        ok, reason = verify_signed_protected(hello_msg, pubs, self.token, self.replay)
        if not ok:
            return make_signed_protected(self.identity, "noise.reject", {"reason": reason}, self.token, self.replay), False
        peer = hello_msg["origin"]
        e = hello_msg["payload"]["e"]
        self.session.accept_peer(peer, e)
        self.peers[peer] = {"session_ready": True}
        # Message 2: e, ee
        return make_signed_protected(
            self.identity,
            "noise.reply",
            {"e": self.session.public_b64(), "node_id": self.node_id},
            token=self.token,
            replay=self.replay,
        ), True

    def handshake_finish(self, reply_msg: dict) -> bool:
        pubs = {self.node_id: self.identity.public_b64()}
        ok, reason = verify_signed_protected(reply_msg, pubs, self.token, self.replay)
        if not ok:
            return False
        peer = reply_msg["origin"]
        self.session.accept_peer(peer, reply_msg["payload"]["e"])
        self.peers[peer] = {"session_ready": True}
        return True

    def seal(self, peer_id: str, payload: dict) -> Optional[str]:
        raw = json.dumps(payload, sort_keys=True).encode()
        return self.session.seal(peer_id, raw)

    def open(self, peer_id: str, blob: str) -> Optional[dict]:
        pt = self.session.open(peer_id, blob)
        if pt is None:
            return None
        return json.loads(pt)


if __name__ == "__main__":
    a, b = MeshTunnel("tun-a"), MeshTunnel("tun-b")
    hello = a.handshake_init()
    reply, ok = b.handshake_respond(hello)
    assert ok and a.handshake_finish(reply)
    blob = a.seal("tun-b", {"lattice_energy": 3.14, "secret": True})
    print("opened", b.open("tun-a", blob))
  
