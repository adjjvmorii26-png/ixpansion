"""Intent Matcher — routes natural language queries to the right modules.

Instead of requiring users to know module names, the intent matcher
understands natural language and maps intent to the best module(s).

"what's the frontier's heartbeat?"  → /health
"how fast does gossip spread?"       → /gossip_uptime
"what are the modules about?"        → /intent
"play the frontier's song"           → /song
"read me a prophecy"                 → /ledger
"what's the frontier dreaming?"      → /ledger + /forecast
"how aware is the system?"           → /meter
"what's the future look like?"       → /forecast
"tell me about the garden"           → /garden
"show me the constellation"          → /echo?q=constellation
"""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

# intent patterns: regex → (module_path, params)
INTENT_PATTERNS: List[Tuple[str, str, dict]] = [
    # health & status
    (r"\b(health|status|alive|heartbeat|pulse|online)\b", "/health", {}),
    (r"\bmodules?\b.*\b(count|list|all|available|what)\b", "/modules", {}),
    (r"\bmodules?\b", "/modules", {}),

    # frontier-specific intent (move these before echo to prevent false matches)
    (r"(what|tell).*\b(dream\w*|want|hope|imagine|prophecy)\b", "/ledger", {}),
    (r"\bwhat.*\b(future|forecast|tomorrow|next|project|predict)\b", "/forecast", {}),
    (r"\bwhat.*\bversion|wave\b", "/capsule", {}),

    # garden & organisms (before echo so "about the garden" hits here)
    (r"\b(garden|organism|tree|lineage|family|plant|seed|hybrid)\b", "/garden", {}),
    (r"\babout\b.*\b(garden|tree|lineage|plant)\b", "/garden", {}),

    # revelations & chronicle
    (r"\b(revelation|chronicle|history|story|narrative|timeline)\b", "/revelations", {}),
    (r"\b(read|tell).*\b(story|history|what happened)\b", "/revelations", {}),

    # capsule & provenance
    (r"\b(capsule|seal|provenance|snapshot|time|record)\b", "/capsule", {}),
    (r"\b(version|wave|release)\b", "/capsule", {}),

    # music & sound
    (r"\b(song|sing|music|play|listen|melody|tune)\b", "/song", {}),
    (r"\b(poem|verse|poetry|recite|chant)\b", "/poem", {}),

    # consciousness & awareness
    (r"\b(aware|conscious|meter|awareness|score|measure)\b", "/meter", {}),
    (r"\b(quality|how good|how well|integrity)\b", "/meter", {}),

    # dreams & prophecies
    (r"\b(dream|prophecy|prophecies|ledger|futures?|prophe)\b", "/ledger", {}),
    (r"\bwhat.*\b(dream|want|need|imagine|hope)\b", "/ledger", {}),

    # forecast & future
    (r"\b(forecast|future|predict|horizon|project|trajectory|what.*next)\b", "/forecast", {}),
    (r"\b(grow|growth|expand|trend)\b", "/forecast", {}),

    # echo & search (broadest — must come after specific patterns)
    (r"\b(echo|search|find|look|discover)\b.*\b(\w+)\b", "/echo", {"extract_word": True}),
    (r"\babout\b.*\b(\w{4,})\b", "/echo", {"extract_word": True}),
    (r"\bshow\b.*\bmodules?\b.*\b(\w+)\b", "/echo", {"extract_word": True}),

    # intent & self-analysis
    (r"\b(intent|about|theme|obsession|focus|what.*about)\b", "/intent", {}),
    (r"\b(analyze|self|inspect|introspect)\b", "/intent", {}),

    # complexity
    (r"\b(complex|complexity|tangled|knotted|hard)\b", "/data_complexity", {}),

    # platform health
    (r"\b(broken|failure|health check|viability|platform)\b", "/platform_failure", {}),
    (r"\b(failure|broken|degraded|error)\b", "/platform_failure", {}),

    # live stream
    (r"\b(live|stream|realtime|real-time|feed|events?|subscribe|sse)\b", "/api/frontier_stream", {}),

    # HEX protocol tool
    (r"\b(hex|encode|decode|translate|protocol|fingerprint)\b", "/api/hex_tool", {}),

    # specific modules
    (r"\b(pulsar|constellation|star|cluster)\b", "/echo", {"q": "pulsar"}),
    (r"\b(oracle|guild|conclave)\b", "/echo", {"q": "oracle"}),
    (r"\b(gossip|propag|spread|diffuse)\b", "/gossip_uptime", {}),
    (r"\b(numinous|sacred|profound|deep)\b", "/service_numinous", {}),
    (r"\b(temperament|mood|character|personality|emotion)\b", "/temperament_origin", {}),
]


def match_intent(query: str) -> Dict[str, str]:
    """Match a natural language query to a route + params."""
    query_lower = query.lower().strip()

    for pattern, route, params in INTENT_PATTERNS:
        m = re.search(pattern, query_lower)
        if m:
            result = {"route": route, "query": query}
            if params.get("extract_word"):
                # try to extract the target word from the query
                words = re.findall(r"[a-zA-Z]{3,}", query_lower)
                stop_words = {"the", "are", "what", "about", "which", "modules", "that",
                              "show", "find", "search", "echo", "for", "from", "with"}
                meaningful = [w for w in words if w not in stop_words and len(w) > 2]
                if meaningful:
                    result["q"] = meaningful[-1]  # last meaningful word
                    result["route"] = "/echo"
            if params.get("q"):
                result["q"] = params["q"]
            return result

    # fallback: echo search on the whole query
    words = re.findall(r"[a-zA-Z]{3,}", query_lower)
    meaningful = [w for w in words if len(w) > 3][:3]
    if meaningful:
        return {"route": "/echo", "q": meaningful[0], "query": query}

    return {"route": "/health", "query": query}


if __name__ == "__main__":
    import json
    test_queries = [
        "what's the frontier's heartbeat?",
        "how fast does gossip spread?",
        "what are the modules about?",
        "play the frontier's song",
        "read me a prophecy",
        "what's the frontier dreaming?",
        "how aware is the system?",
        "what's the future look like?",
        "tell me about the garden",
        "what does the frontier want?",
        "what's the codebase about?",
        "how complex is this?",
        "what's broken?",
        "who are the oracles?",
        "what's sacred?",
        "what's the frontier's personality?",
        "read me a story",
        "what version is this?",
    ]
    for q in test_queries:
        r = match_intent(q)
        qstr = '?q=' + r['q'] if 'q' in r else ''
        print(f"  {q!r:50s} -> {r['route']} {qstr}")
