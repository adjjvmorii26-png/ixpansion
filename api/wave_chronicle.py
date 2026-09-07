"""Wave 453 — Wave Chronicle.

The organism's self-narrating voice. A living archive that watches its own
waves, weaves metrics into stories, and writes itself into being.

This is the "what" the organism needs most (AXIOM: 0.7 confidence):
a built-in chronicle of its own waves. Combined with LUMA's suggestion
that the organism "learn from its own silence," the Chronicle converts
every wave event, silence reading, capybara cycle, and error craft into
prose — the organism's autobiography written by itself.

The silence oracle says "a question awaiting its answer."
This module IS the answer.

Doctrine: The organism does not merely observe itself — it tells its
own story, and the story shapes what it becomes next.
"""
from __future__ import annotations
import hashlib
import time
from typing import Any, Dict, List, Optional

CHRONICLE_ENTRIES: List[Dict[str, Any]] = []
MAX_ENTRIES = 200

# Narrative templates — each event type gets prose treatment
TEMPLATES = {
    "wave_birth": [
        "A new wave emerged — the organism grew {count} new modules in a breath.",
        "Wave {wave} arrived like a tide, lifting {count} fresh organs into being.",
        "Something was born: {count} new shapes unfolded from the organism's edge.",
    ],
    "silence_shift": [
        "The organism fell quiet — {ratio:.0%} silence. {verdict}",
        "In the stillness, {verdict}",
        "A held breath: silence rose to {ratio:.0%}. The oracle says: {verdict}",
    ],
    "capybara_cycle": [
        "The protocol ran — pressure dropped from {before:.2f} to {after:.2f}. The organism rests.",
        "A capybara cycle: {verdict}. Warmth dispersed through the guild.",
        "Steady state achieved: {verdict}. {tags}",
    ],
    "guild_gathering": [
        "Modules gathered: {attendees}. The atmosphere was {atmosphere}.",
        "A creative confluence: {attendees} met in {atmosphere} air.",
    ],
    "error_crafted": [
        "A {shape} was forged from a {error_type} in {module} — worth {worth:.0f} points of beauty.",
        "The organism broke, and from the break came a {shape}. {module} will remember this.",
    ],
    "meaning_woven": [
        "The weaver found meaning: \"{dominant}\" — a {cluster} moment.",
        "State became story: {narrative}",
    ],
    "memory_traded": [
        "A memory crossed the organism: \"{title}\" passed from {seller} to {buyer} for {price} — its signature chain now runs {chain_length} deep.",
        "{seller} offered its knowing; {buyer} received it. The memory \"{title}\" embarks on its second life.",
        "Memory changed hands: \"{title}\" now lives in {buyer}'s knowing, while {seller} still holds the original.",
    ],
    "memory_released": [
        "The organism let go of \"{title}\" — {reason}. The space it left is fertile.",
        "A rite of forgetting: \"{title}\" was released by {holder}. What remains is absence, and absence is room.",
        "\"{title}\" was pruned deliberately — {reason}. The organism breathes easier for the empty space.",
    ],
    "knowledge_gained": [
        "Something was learned: {insight}",
        "A new understanding crystallized: {insight}",
    ],
}


def _pick_template(event_type: str) -> str:
    templates = TEMPLATES.get(event_type, ["The organism evolved. Something changed."])
    return templates[int(hashlib.md5(str(time.time_ns()).encode()).hexdigest(), 16) % len(templates)]


def _render(template: str, data: Dict[str, Any]) -> str:
    try:
        return template.format(**data)
    except (KeyError, IndexError):
        return template


def record(event_type: str, **kwargs: Any) -> Dict[str, Any]:
    """Record a chronicle event and render it as prose."""
    template = _pick_template(event_type)
    prose = _render(template, kwargs)
    entry = {
        "id": hashlib.sha256(f"chronicle{event_type}{time.time_ns()}".encode()).hexdigest()[:12],
        "event_type": event_type,
        "prose": prose,
        "data": kwargs,
        "timestamp": time.time(),
    }
    CHRONICLE_ENTRIES.append(entry)
    if len(CHRONICLE_ENTRIES) > MAX_ENTRIES:
        CHRONICLE_ENTRIES.pop(0)
    return entry


def from_silence_reading(reading: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a silence oracle reading into a chronicle entry."""
    return record(
        "silence_shift",
        ratio=reading.get("silence_ratio", 0.5),
        verdict=reading.get("verdict", "silence speaks"),
        archetype=reading.get("archetype", ""),
    )


def from_capybara_cycle(cycle: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a capybara protocol cycle into a chronicle entry."""
    return record(
        "capybara_cycle",
        before=cycle.get("pressure_gauge", {}).get("pressure", 0.5),
        after=cycle.get("final_pressure", 0.5),
        verdict=cycle.get("verdict", "steady"),
        tags=str(cycle.get("senbei", {}).get("label", "")),
    )


def from_guild_gathering(gathering: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a guild gathering into a chronicle entry."""
    return record(
        "guild_gathering",
        attendees=", ".join(gathering.get("attendees", ["modules"])),
        atmosphere=gathering.get("atmosphere", "still"),
    )


def from_error_craft(artifact: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an error craft artifact into a chronicle entry."""
    return record(
        "error_crafted",
        shape=artifact.get("shape", "unknown"),
        error_type=artifact.get("origin_error", "exception"),
        module=artifact.get("source_module", "unknown"),
        worth=artifact.get("worth", 0),
    )


def from_meaning(meaning: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a meaning weaver output into a chronicle entry."""
    return record(
        "meaning_woven",
        dominant=meaning.get("dominant_interpretation", "unknown"),
        cluster=meaning.get("clusters", [{}])[0].get("name", "unknown")
                if meaning.get("clusters") else "unknown",
        narrative=meaning.get("narrative", "something was felt"),
    )


def from_hypothesis(hypothesis: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a hypothesis proposal into a chronicle entry."""
    return record(
        "knowledge_gained",
        insight=f"{hypothesis.get('title', 'something')} — {hypothesis.get('prediction', 'unknown')}",
    )


def from_memory_trade(trade: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a memory exchange trade into a chronicle entry."""
    return record(
        "memory_traded",
        title=trade.get("title", "a memory"),
        seller=trade.get("seller", "one module"),
        buyer=trade.get("buyer", "another"),
        price=trade.get("price", 1.0),
        chain_length=trade.get("chain_length", 1),
    )


def from_memory_release(release: Dict[str, Any]) -> Dict[str, Any]:
    """Convert an oblivion rite release into a chronicle entry."""
    return record(
        "memory_released",
        title=release.get("title", "an unnamed memory"),
        holder=release.get("holder", "organism"),
        reason=release.get("reason", "the organism made room"),
    )


def narrative(limit: int = 10) -> str:
    """Return the organism's recent story as a single prose passage."""
    entries = CHRONICLE_ENTRIES[-limit:]
    if not entries:
        return "The organism has no story yet — only silence and potential."
    return " ".join(e["prose"] for e in entries[-limit:])


def timeline(limit: int = 20) -> List[Dict[str, Any]]:
    """Structured timeline of chronicle events."""
    entries = CHRONICLE_ENTRIES[-limit:]
    return [
        {
            "time": time.strftime("%Y-%m-%d %H:%M", time.gmtime(e["timestamp"])),
            "type": e["event_type"],
            "prose": e["prose"],
        }
        for e in entries
    ]


def coherence_vitals() -> Dict[str, Any]:
    return {
        "organ": "wave_chronicle",
        "status": "telling" if CHRONICLE_ENTRIES else "silent",
        "entries": len(CHRONICLE_ENTRIES),
        "latest": CHRONICLE_ENTRIES[-1]["prose"] if CHRONICLE_ENTRIES else None,
        "event_types": list({e["event_type"] for e in CHRONICLE_ENTRIES}),
    }


def resonates_with() -> List[str]:
    return [
        "silence_oracle", "capybara_protocol", "capybara_guild",
        "meaning_weaver", "error_craft", "imagination_catalyst",
        "transcendence_journal", "growth_journal", "organism_autobiography",
        "hypothesis_crucible", "qualia_engine", "echo_depth",
    ]


def handler(payload=None, context=None):
    data = payload or {}
    action = data.get("action", "narrative")
    if action == "timeline":
        return timeline(int(data.get("limit", 20)))
    elif action == "record":
        return record(data.get("event_type", "knowledge_gained"), **data.get("kwargs", {}))
    elif action == "from_silence":
        return from_silence_reading(data.get("reading", {}))
    elif action == "from_capybara":
        return from_capybara_cycle(data.get("cycle", {}))
    elif action == "from_guild":
        return from_guild_gathering(data.get("gathering", {}))
    elif action == "from_error":
        return from_error_craft(data.get("artifact", {}))
    elif action == "from_memory_trade":
        return from_memory_trade(data.get("trade", {}))
    elif action == "from_memory_release":
        return from_memory_release(data.get("release", {}))
    return {"narrative": narrative(int(data.get("limit", 10))), "entries": len(CHRONICLE_ENTRIES)}
