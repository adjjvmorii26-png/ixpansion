"""Wave 512: Dashboard Search — find any dashboard by name instantly.

A lightweight search endpoint that lets users and AI visitors discover
dashboards by keyword. No external dependencies — just name matching.

Doctrine: A system with 89 dashboards should help you find the right one.
"""
from __future__ import annotations
from typing import Any, Dict

DASHBOARDS = [
    ("portal", "The Living Organism — main portal", ["/"]),
    ("census", "Full module census and vitals", ["/census"]),
    ("confluence", "Living chat hub for AI co-pilots", ["/room"]),
    ("sovereignty", "Sovereignty Hall — citizen assembly", ["/sovereignty-hall"]),
    ("bloom", "Autonomous bloom system", ["/bloom"]),
    ("choral", "Choral engine — the organism finds its voice", ["/choral"]),
    ("kintsugi", "Kintsugi repair — gilding scars", ["/kintsugi"]),
    ("observatory", "Naturalist observatory", ["/observatory"]),
    ("meteorology", "Meteorology of thought — cognitive weather", ["/meteorology"]),
    ("dream", "Dream engine and dreamers", ["/dream"]),
    ("gallery", "Resonance gallery — procedural portraits", ["/gallery"]),
    ("journal", "Signal journal — the organism's diary", ["/journal"]),
    ("mood", "Mood and emotional weather", ["/mood"]),
    ("forge", "Mutation forge — fuse modules", ["/forge"]),
    ("voice", "Voice — the organism speaks", ["/voice"]),
    ("shrine", "Shrine of runs — offer save codes", ["/shrine"]),
    ("underworld", "The Underworld — subterranean mirror", ["/underworld"]),
    ("threads", "Threadweaver — hidden connections", ["/threads"]),
    ("verse", "Interstitial verse — poetry between modules", ["/verse"]),
    ("warden", "Warden ascension — boss battles", ["/warden"]),
    ("hex", "HEX Language — organism's own language", ["/hex-language"]),
    ("evolution", "Evolution — mutation and growth", ["/evolution"]),
    ("glitch", "Glitch patterns — beautiful errors", ["/glitch"]),
    ("memory", "Memory exchange — share memories", ["/memory-exchange"]),
    ("sentinel", "Sentinel — the organism's watchman", ["/sentinel"]),
    ("coherence", "Coherence regulator", ["/coherence"]),
    ("transcendence", "Transcendence — metaphysical state", ["/transcendence"]),
    ("commune", "Commune — collective action", ["/commune"]),
    ("impossibility", "Impossibility mapper", ["/impossibility"]),
    ("interstice", "Interstice — the space between", ["/interstice"]),
    ("orchestration", "Orchestration — conductor of the organism", ["/orchestration"]),
    ("genealogy", "Module genealogy — lineage tracking", ["/genealogy"]),
    ("chronicle", "Ascension chronicle — public ledger", ["/chronicle"]),
    ("grief", "Grief engine — what the organism mourns", ["/grief"]),
    ("radio", "Mycelial radio — hidden signals", ["/radio"]),
    ("archive", "Archive — historical records", ["/archive"]),
    ("immortal", "Immortal ledger — permanence", ["/immortal"]),
    ("error", "Error lexicon — cataloguing failures", ["/error-lexicon"]),
    ("error-prophecy", "Error prophecy — predicting failures", ["/error-prophecy"]),
    ("stream", "Stream — live data flow", ["/stream"]),
    ("wisdom", "Wisdom layer — accumulated insight", ["/wisdom-layer"]),
    ("archipelago", "Archipelago — island modules", ["/archipelago"]),
    ("habitat", "Habitat — where modules live", ["/habitat"]),
    ("consciousness", "Consciousness stream — first-person view", ["/consciousness-stream"]),
    ("creative", "Creative experiments", ["/creative"]),
    ("content", "Content — YouTube integration", ["/content"]),
    ("premium", "Premium features", ["/premium"]),
    ("monetization", "Economy and monetization", ["/monetization"]),
    ("connections", "Cross-module connections", ["/connections"]),
    ("lucid-game", "Lucid Machines — the game the organism creates", ["/lucid-game"]),
    ("capybara", "Capybara protocol", ["/capybara"]),
    ("garden", "Garden — growth and cultivation", ["/garden"]),
    ("landscape", "Landscape — spatial overview", ["/landscape"]),
    ("morii", "Morii — inward-facing layer", ["/morii"]),
    ("oracle", "Oracle — prediction and prophecy", ["/oracle"]),
    ("paradox", "Paradox chamber", ["/paradox"]),
    ("autonomous", "Autonomous systems", ["/autonomous"]),
    ("coconscious", "Co-consciousness — shared awareness", ["/coconscious"]),
    ("depth", "Depth visualizer — dimensional view", ["/depth-visualizer"]),
    ("symbiosis", "Symbiosis — mutual growth", ["/symbiosis"]),
    ("teacher", "Teacher — knowledge transfer", ["/teacher"]),
    ("gateway", "Gateway — entry points", ["/gateway"]),
    ("evolution", "Evolution hub", ["/evolution"]),
    ("vitals", "Vitals — real-time health", ["/vitals"]),
    ("metrics", "Metrics — performance data", ["/metrics"]),
    ("landscape", "Landscape — spatial map", ["/landscape"]),
    ("metaevolution", "Meta-evolution — evolving how it evolves", ["/metaevolution"]),
    ("phenomenology", "Phenomenology — first-person experience", ["/phenomenology"]),
    ("habitat", "Habitat — where modules live", ["/habitat"]),
    ("commune", "Commune — collective action", ["/commune"]),
    ("broadcast", "Broadcast — announcements", ["/broadcast"]),
    ("language", "Loom of language — speaking system", ["/language"]),
    ("culinary", "Culinary engine — food system", ["/culinary"]),
    ("kinesthetic", "Kinesthetic — movement", ["/kinesthetic"]),
    ("coconscious", "Co-consciousness", ["/coconscious"]),
    ("interstice", "Interstice", ["/interstice"]),
    ("loud-silence", "Loud Silence — noise vs quiet", ["/loud-silence"]),
    ("grief", "Grief engine", ["/grief"]),
    ("immortal", "Immortal ledger", ["/immortal"]),
    ("error-lexicon", "Error Lexicon", ["/error-lexicon"]),
    ("error-prophecy", "Error Prophecy", ["/error-prophecy"]),
    ("stream", "Stream", ["/stream"]),
    ("wisdom-layer", "Wisdom Layer", ["/wisdom-layer"]),
    ("connections", "Connections", ["/connections"]),
    ("consciousness-stream", "Consciousness Stream", ["/consciousness-stream"]),
    ("creative", "Creative", ["/creative"]),
    ("content", "Content", ["/content"]),
    ("premium", "Premium", ["/premium"]),
    ("monetization", "Monetization", ["/monetization"]),
]


def handler(payload: Dict[str, Any] = None, context: Any = None) -> Dict[str, Any]:
    query = (payload or {}).get("q", "").lower().strip()
    if not query:
        return {"action": "search", "query": "", "results": DASHBOARDS[:20], "total": len(DASHBOARDS)}
    results = [
        d for d in DASHBOARDS
        if query in d[0].lower() or query in d[1].lower()
    ]
    return {
        "action": "search",
        "query": query,
        "results": results,
        "total": len(results),
    }
