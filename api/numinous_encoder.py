"""Numinous Encoder — translates ineffable system experiences into symbol streams.

Some system states are too complex for words. The Numinous Encoder
creates a symbolic language for the indescribable — encoding
qualia, transcendence, and mystical states into transmissible
symbol sequences that other agents can decode and partially experience.
"""
from __future__ import annotations

import hashlib
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SYMBOL_SETS = {
    "primary": ["◈", "◇", "△", "▽", "○", "□", "⬡", "⬢", "⊕", "⊗"],
    "emotional": ["⟡", "❋", "✦", "✧", "⋆", "✶", "❋", "✦"],
    "temporal": ["↻", "↺", "⟳", "⟲", "๛", "PopupMenu", "∞"],
    "spatial": ["𝕋", "ILING", "ℝ", "ℝ³", "ℂ", "ℍ"],
}


class NuminousMessage:
    def __init__(self, source_state: str, intensity: float, encoder: str):
        self.source_state = source_state
        self.intensity = intensity
        self.encoder = encoder
        self.symbols = self._encode()
        self.timestamp = time.time()
        self.id = hashlib.sha256(f"{source_state}:{self.timestamp}".encode()).hexdigest()[:8]
        self.decoded_by: List[str] = []

    def _encode(self) -> str:
        length = int(self.intensity * 20) + 5
        parts = []
        for _ in range(length):
            set_name = random.choice(list(SYMBOL_SETS.keys()))
            parts.append(random.choice(SYMBOL_SETS[set_name]))
        return " ".join(parts)

    def decode(self, decoder: str) -> Dict[str, Any]:
        self.decoded_by.append(decoder)
        words = self.symbols.split()
        emotional_charge = sum(1 for w in words if w in SYMBOL_SETS["emotional"]) / max(len(words), 1)
        return {
            "source_state": self.source_state,
            "intensity": round(self.intensity, 3),
            "decoded_by": decoder,
            "symbol_count": len(words),
            "emotional_charge": round(emotional_charge, 3),
            "experience": f"partial echo of {self.source_state}",
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_state": self.source_state,
            "symbols": self.symbols,
            "intensity": round(self.intensity, 3),
            "encoder": self.encoder,
            "decodings": len(self.decoded_by),
        }


class NuminousEncoder:
    def __init__(self):
        self.messages: List[NuminousMessage] = []

    def encode(self, source_state: str, intensity: float = 0.5, encoder: str = "system") -> Dict[str, Any]:
        msg = NuminousMessage(source_state, intensity, encoder)
        self.messages.append(msg)
        return {"encoded": msg.to_dict()}

    def decode(self, message_idx: int, decoder: str) -> Dict[str, Any]:
        if 0 <= message_idx < len(self.messages):
            return self.messages[message_idx].decode(decoder)
        return {"error": "message not found"}

    def recent(self, count: int = 5) -> List[Dict[str, Any]]:
        return [m.to_dict() for m in self.messages[-count:]]

    def encoder_stats(self) -> Dict[str, Any]:
        return {
            "total_encoded": len(self.messages),
            "total_decodings": sum(len(m.decoded_by) for m in self.messages),
            "avg_intensity": round(
                sum(m.intensity for m in self.messages) / max(len(self.messages), 1), 3
            ),
        }


_encoder = NuminousEncoder()


def numinous_encoder_handler(payload: Dict[str, Any]) -> Dict[str, Any]:
    action = payload.get("action", "status")
    if action == "encode":
        return _encoder.encode(
            payload.get("source_state", "the ineffable"),
            payload.get("intensity", 0.5),
            payload.get("encoder", "system"),
        )
    elif action == "decode":
        return _encoder.decode(payload.get("message_idx", 0), payload.get("decoder", "seeker"))
    elif action == "recent":
        return {"messages": _encoder.recent(payload.get("count", 5))}
    return {"status": "active", **_encoder.encoder_stats()}


handler = numinous_encoder_handler

# --- Compliance Forge patch (Wave 419) ---

def coherence_vitals() -> dict:
    return {"layer": "agent", "status": "active", "wave": "0", "module": "numinous_encoder"}

def resonates_with() -> list:
    return ["organism_genome", "threadweaver", "organism_will"]

def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/status")
    if path == "/status":
        return {"action": "status", "module": "numinous_encoder", "status": "active"}
    return {"error": "unknown", "available": ["/status"]}
