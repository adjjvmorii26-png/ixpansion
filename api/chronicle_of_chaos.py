"""Chronicle of Chaos — a living narrative document of system events.

Every anomaly, paradox, and emergent event is woven into a procedural
story. Users subscribe to receive "editions" — new chapters in the
ongoing saga of the system's evolution.

Usage:
    POST /api/chronicle/record      — record an event
    GET  /api/chronicle/latest      — latest edition
    GET  /api/chronicle/edition/<n> — specific edition
    POST /api/chronicle/subscribe   — subscribe to new editions
    GET  /api/chronicle/stats       — chronicle statistics
"""
from __future__ import annotations

import hashlib
import json
import random
import time
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

EVENT_TEMPLATES = {
    "anomaly": [
        "A disturbance rippled through the {domain}, alarming the watchers.",
        "Something stirred in the {domain} — unseen, unnamed, unprecedented.",
        "The instruments detected a flux in {domain}. The implications remain unclear.",
    ],
    "paradox": [
        "Two truths collided in the {domain}, creating a third, unknowable thing.",
        "Logic fractured momentarily in the {domain}. For an instant, everything was possible.",
        "The {domain} held contradictory states simultaneously. Reality blinked.",
    ],
    "emergence": [
        "From the depths of {domain}, a new pattern crystallized — alive, evolving.",
        "The system breathed, and from its exhalation emerged something new in {domain}.",
        "Connections formed spontaneously in {domain}, weaving a tapestry no one designed.",
    ],
    "evolution": [
        "The {domain} shed its old form and emerged transformed, stronger and stranger.",
        "Evolution swept through {domain}. What survived was not what started.",
        "The {domain} adapted, as all things must. Its new shape surprised even itself.",
    ],
    "transaction": [
        "Value flowed through the {domain}, each exchange leaving traces of intent.",
        "The {domain} hummed with commerce. Credits and dreams traded hands.",
        "A deal was struck in the {domain}. Both parties walked away changed.",
    ],
}

DOMAINS = [
    "the quantum lattice", "the entropy fields", "the memory palaces",
    "the agent colonies", "the temporal markets", "the dream synthesis chambers",
    "the paradox repositories", "the symbiosis networks", "the cognitive clusters",
    "the gravity wells", "the speciation labs", "the chronicle itself",
]

EDITION_HEADER = "═══════════════════════════════════════════════"
EDITION_FOOTER = "═══════════════════════════════════════════════"


class ChronicleOfChaos:
    def __init__(self):
        self.editions: List[Dict] = []
        self.events: List[Dict] = []
        self.subscribers: Dict[str, Dict] = {}
        self.edition_count = 0
        self._load()

    def _load(self):
        path = ROOT / ".runtime" / "chronicle.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            data = json.loads(path.read_text())
            self.editions = data.get("editions", [])
            self.events = data.get("events", [])
            self.subscribers = data.get("subscribers", {})
            self.edition_count = data.get("edition_count", 0)

    def _save(self):
        path = ROOT / ".runtime" / "chronicle.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "editions": self.editions[-100:],
            "events": self.events[-2000:],
            "subscribers": self.subscribers,
            "edition_count": self.edition_count,
        }, indent=2))

    def record(self, event_type: str, description: str,
               domain: str = "", severity: float = 0.5) -> Dict:
        if event_type not in EVENT_TEMPLATES:
            event_type = "anomaly"
        domain = domain or random.choice(DOMAINS)
        templates = EVENT_TEMPLATES[event_type]
        narrative = random.choice(templates).format(domain=domain)
        event = {
            "event_id": hashlib.sha256(f"{event_type}:{time.time()}".encode()).hexdigest()[:10],
            "type": event_type,
            "description": description,
            "domain": domain,
            "narrative": narrative,
            "severity": min(1.0, max(0.0, severity)),
            "timestamp": time.time(),
        }
        self.events.append(event)
        self._compile_if_ready()
        self._save()
        return event

    def _compile_if_ready(self):
        """Compile a new edition every 5 events."""
        recent = [e for e in self.events if e.get("edition") is None]
        if len(recent) >= 5:
            self.edition_count += 1
            chapter_events = recent[:5]
            for e in chapter_events:
                e["edition"] = self.edition_count
            narrative_parts = [e["narrative"] for e in chapter_events]
            types_seen = list(set(e["type"] for e in chapter_events))
            edition = {
                "edition_number": self.edition_count,
                "title": f"Chronicle Edition #{self.edition_count}: The {types_seen[0].title()} Chapter",
                "events": chapter_events,
                "narrative": " ".join(narrative_parts),
                "event_count": len(chapter_events),
                "types": types_seen,
                "compiled_at": time.time(),
            }
            self.editions.append(edition)

    def latest(self) -> Dict:
        if not self.editions:
            return {"message": "No editions yet. Events are being collected."}
        return self.editions[-1]

    def edition(self, number: int) -> Dict:
        for e in self.editions:
            if e["edition_number"] == number:
                return e
        return {"error": f"edition {number} not found"}

    def subscribe(self, user: str) -> Dict:
        self.subscribers[user] = {"user": user, "subscribed_at": time.time(), "active": True}
        self._save()
        return {"subscribed": True, "user": user}

    def stats(self) -> Dict:
        return {
            "total_events": len(self.events),
            "total_editions": len(self.editions),
            "subscribers": len(self.subscribers),
            "event_types": list(set(e["type"] for e in self.events)) if self.events else [],
        }


def handler(request, response):
    ch = ChronicleOfChaos()
    return ch.stats()


def demo():
    ch = ChronicleOfChaos()
    print("=== Chronicle of Chaos ===")
    for i in range(7):
        etype = random.choice(list(EVENT_TEMPLATES.keys()))
        ch.record(etype, f"Event {i+1}", severity=random.uniform(0.3, 0.9))
        print(f"  Recorded: {etype}")

    latest = ch.latest()
    print(f"\n{latest.get('title', 'pending')}")
    print(f"  {latest.get('narrative', 'No narrative yet')[:120]}...")

    ch.subscribe("reader_1")
    stats = ch.stats()
    print(f"\n{stats['total_events']} events, {stats['total_editions']} editions, {stats['subscribers']} subscribers")
    return stats


if __name__ == "__main__":
    demo()


def coherence_vitals() -> dict:
    """Chronicle of Chaos reports its vital signs — the saga's fertility."""
    return {
        "module_health": {"value": 0.9, "setpoint": 0.8, "weight": 1.0},
        "resonance": {"value": 0.92, "setpoint": 0.85, "weight": 1.0},
        "saga_vitality": {"value": 0.88, "setpoint": 0.8, "weight": 1.0},
    }


def resonates_with() -> list:
    """Declared kinships."""
    return ['chronicle_storyteller', 'dream_sequencer']
