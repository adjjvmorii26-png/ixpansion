#!/usr/bin/env python3
"""
Node Identity & Lightweight Auth for Swarm Federation
- Each node generates (or loads) an Ed25519 keypair
- Capability announces and task messages carry a signature
- Hub and peers verify signatures before accepting claims
- Simple shared-secret bootstrap token optional for private swarms
"""

import argparse
import asyncio
import base64
import hashlib
import json
import os
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

import websockets
from websockets.client import connect
from websockets.server import serve

KEYS_DIR = Path("/home/workdir/artifacts/.node_keys")
KEYS_DIR.mkdir(exist_ok=True)
DEFAULT_HOST, DEFAULT_PORT = "127.0.0.1", 8765


# ---------------------------------------------------------------------------
# Identity
# ---------------------------------------------------------------------------

class NodeIdentity:
    def __init__(self, node_id: Optional[str] = None):
        self.node_id = node_id or f"node-{uuid.uuid4().hex[:8]}"
        self.key_path = KEYS_DIR / f"{self.node_id}.pem"
        self.pub_path = KEYS_DIR / f"{self.node_id}.pub"
        self._private: Ed25519PrivateKey
        self._public: Ed25519PublicKey
        self._load_or_create()

    def _load_or_create(self):
        if self.key_path.exists() and self.pub_path.exists():
            pem = self.key_path.read_bytes()
            self._private = serialization.load_pem_private_key(pem, password=None)
            pub_bytes = self.pub_path.read_bytes()
            self._public = Ed25519PublicKey.from_public_bytes(pub_bytes)
            print(f"[Identity] loaded keys for {self.node_id}")
        else:
            self._private = Ed25519PrivateKey.generate()
            self._public = self._private.public_key()
            pem = self._private.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption(),
            )
            pub = self._public.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw,
            )
            self.key_path.write_bytes(pem)
            self.pub_path.write_bytes(pub)
            print(f"[Identity] generated new keys for {self.node_id}")

    def public_bytes(self) -> bytes:
        return self._public.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def public_b64(self) -> str:
        return base64.urlsafe_b64encode(self.public_bytes()).decode()

    def sign(self, data: bytes) -> str:
        sig = self._private.sign(data)
        return base64.urlsafe_b64encode(sig).decode()

    @staticmethod
    def verify(pub_b64: str, data: bytes, sig_b64: str) -> bool:
        try:
            pub = Ed25519PublicKey.from_public_bytes(base64.urlsafe_b64decode(pub_b64))
            pub.verify(base64.urlsafe_b64decode(sig_b64), data)
            return True
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Signed envelope
# ---------------------------------------------------------------------------

def canonical(payload: dict) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def make_signed(identity: NodeIdentity, msg_type: str, payload: dict, token: str = "") -> dict:
    body = {
        "v": 1,
        "type": msg_type,
        "origin": identity.node_id,
        "ts": datetime.now(timezone.utc).isoformat(),
        "payload": payload,
        "pub": identity.public_b64(),
        "token": token,
    }
    body["sig"] = identity.sign(canonical({k: body[k] for k in ("v", "type", "origin", "ts", "payload")}))
    return body


def verify_signed(msg: dict, known_pubs: Dict[str, str], required_token: str = "") -> Tuple[bool, str]:
    """Returns (ok, reason)."""
    origin = msg.get("origin", "")
    pub = msg.get("pub", "")
    sig = msg.get("sig", "")
    token = msg.get("token", "")

    if required_token and token != required_token:
        return False, "bad_token"

    # First message from a node registers its pub key
    if origin not in known_pubs:
        known_pubs[origin] = pub
    elif known_pubs[origin] != pub:
        return False, "pub_mismatch"

    data = canonical({k: msg[k] for k in ("v", "type", "origin", "ts", "payload") if k in msg})
    if not NodeIdentity.verify(pub, data, sig):
        return False, "bad_signature"
    return True, "ok"


# ---------------------------------------------------------------------------
# Authenticated Hub
# ---------------------------------------------------------------------------

class AuthHub:
    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, token: str = ""):
        self.host, self.port = host, port
        self.token = token
        self.clients = set()
        self.known_pubs: Dict[str, str] = {}

    async def handler(self, websocket):
        self.clients.add(websocket)
        print(f"[AuthHub] + n={len(self.clients)}")
        try:
            async for raw in websocket:
                try:
                    msg = json.loads(raw)
                    ok, reason = verify_signed(msg, self.known_pubs, self.token)
                    if not ok:
                        print(f"[AuthHub] REJECT {msg.get('type')} from {msg.get('origin')}: {reason}")
                        continue
                    await self.broadcast(raw, exclude=websocket)
                    if msg.get("type") == "capability.announce":
                        print(f"[AuthHub] OK announce {msg['payload'].get('card',{}).get('name')} from {msg['origin']}")
                except Exception as e:
                    print(f"[AuthHub] err {e}")
        except websockets.ConnectionClosed:
            pass
        finally:
            self.clients.discard(websocket)

    async def broadcast(self, raw, exclude=None):
        for ws in list(self.clients):
            if ws is exclude:
                continue
            try:
                await ws.send(raw)
            except Exception:
                self.clients.discard(ws)

    async def run(self):
        print(f"[AuthHub] ws://{self.host}:{self.port} token={'set' if self.token else 'none'}")
        async with serve(self.handler, self.host, self.port):
            print("[AuthHub] online")
            await asyncio.Future()


# ---------------------------------------------------------------------------
# Authenticated Node
# ---------------------------------------------------------------------------

class AuthNode:
    def __init__(self, hub_url: str, token: str = "", node_id: Optional[str] = None):
        self.hub_url = hub_url
        self.token = token
        self.identity = NodeIdentity(node_id)
        self.known_pubs: Dict[str, str] = {self.identity.node_id: self.identity.public_b64()}
        self.ws = None

    async def send(self, msg_type: str, payload: dict):
        if self.ws:
            msg = make_signed(self.identity, msg_type, payload, self.token)
            await self.ws.send(json.dumps(msg))

    async def on_message(self, raw: str):
        try:
            msg = json.loads(raw)
        except Exception:
            return
        ok, reason = verify_signed(msg, self.known_pubs, self.token)
        if not ok:
            print(f"[{self.identity.node_id}] REJECT {msg.get('type')}: {reason}")
            return
        if msg.get("origin") == self.identity.node_id:
            return
        mtype = msg.get("type")
        if mtype == "capability.announce":
            name = msg.get("payload", {}).get("card", {}).get("name")
            print(f"[{self.identity.node_id}] verified peer {name} @{msg['origin']}")
        elif mtype == "ping":
            await self.send("pong", {"to": msg["origin"]})

    async def run(self):
        print(f"[{self.identity.node_id}] joining {self.hub_url}")
        async for ws in connect(self.hub_url):
            self.ws = ws
            print(f"[{self.identity.node_id}] connected (pub={self.identity.public_b64()[:16]}…)")
            try:
                # Hello + optional capability announce stub
                await self.send("node.hello", {
                    "node_id": self.identity.node_id,
                    "pub": self.identity.public_b64(),
                })
                await self.send("capability.announce", {
                    "card": {
                        "agent_id": "auth_demo",
                        "name": f"AuthNode-{self.identity.node_id[-4:]}",
                        "capabilities": ["ping", "secure_echo"],
                        "version": "0.1.0",
                    },
                    "node": self.identity.node_id,
                })
                async for raw in ws:
                    await self.on_message(raw)
            except websockets.ConnectionClosed:
                print(f"[{self.identity.node_id}] retry")
                await asyncio.sleep(2)
            finally:
                self.ws = None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

async def amain():
    p = argparse.ArgumentParser(description="Node Identity & Auth")
    p.add_argument("--hub", action="store_true")
    p.add_argument("--join", type=str)
    p.add_argument("--token", default=os.environ.get("SWARM_TOKEN", ""), help="Shared bootstrap token")
    p.add_argument("--host", default=DEFAULT_HOST)
    p.add_argument("--port", type=int, default=DEFAULT_PORT)
    p.add_argument("--node-id", default=None)
    args = p.parse_args()

    if args.hub:
        await AuthHub(args.host, args.port, token=args.token).run()
    elif args.join:
        await AuthNode(args.join, token=args.token, node_id=args.node_id).run()
    else:
        p.print_help()
        print("\n  SWARM_TOKEN=secret python node_auth.py --hub")
        print("  SWARM_TOKEN=secret python node_auth.py --join ws://127.0.0.1:8765")


if __name__ == "__main__":
    asyncio.run(amain())
          
