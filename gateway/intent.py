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
    # dowsing rod (hidden streams, before echo/resonance)
    (r"\b(dows(ing)?|hidden (streams?|connections?|links?)|secret (bond|tie)|underground (stream|connection)|latent (resonance|connection)|find.*(stream|link))\b", "/api/dowsing_rod", {}),

    (r"\bmodules?\b.*\b(count|list|all|available|what)\b", "/modules", {}),
    (r"\bmodules?\b", "/modules", {}),

    # resonance graph intelligence (before garden/constellation so graph/web queries land here)
    (r"\b(resonance graph|graph of the (living )?(system|frontier|organism)|who (are|is) (the )?hubs?|hubs? (of|in) the|bridge modules?|bridges? (connect|in|of|the)|what bridges|connective tissue|graph intelligence|web of (modules|the system)|topology of the (system|frontier))\b", "/api/resonance_graph", {}),

    # autonomous bloom (before forecast/garden so growth-of-ecosystem lands here)
    (r"\b(full bloom|bloom(ing|ed| plan)?|blossom|grow the organism|seeds? (ready|to awaken|should awaken)|awaken(ing)? (seeds?|modules?)|ecosystem growth|growth trajectory|next bloom)\b", "/api/autonomous_bloom", {}),

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

    # sound cauldron (before /song so 'sound of X' hits cauldron, 'song' still hits /song)
    (r"\b(sound of|music of|hear the|brew|scoresheet|listen to the sound)\b", "/api/sound_cauldron", {}),

    # organism index
    (r"\b(organism|experiments?|lab|collection|ecosystem|creatures?|the organisms)\b", "/api/organism_index", {}),

    # coherence regulator
    (r"\b(coherence|coherent|vitals|healthy|how coherent|system health|pulse|resonance state|alive)\b", "/api/coherence_regulator", {}),

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

    # heterarchy oracle (distributed will, before audit/echo)
    (r"\b(heterarchy|distributed will|who leads|no leader|peer( to)? peer governance|without a leader)\b", "/api/heterarchy_oracle", {}),

    # keystone auditor (before echo so web-integrity queries land here)
    (r"\b(keystone|which (organ|module)s? (would|is) (missed|critical)|must (not )?lose|cannot (afford to )?lose|remove.*collapse|web (integrity|fragile))\b", "/api/keystone_auditor", {}),

    # morphic dial (collective memory resonance, before memory)
    (r"\b(morphic|collective (memory )?(field|resonance)|what (has )?the (system|organism) (done|remembered)|reawaken(ing)?|ease of (re)?awakening)\b", "/api/morphic_dial", {}),

    # silence orchard (negative space / dormant, before bloom)
    (r"\b(silence orchard|silent (modules?|ground|space)|negative space|fallow|empty (paths?|modules?|gardens?)|dormant modules?)\b", "/api/silence_orchard", {}),

    # antikythera engine (eclipses/heavenly, before forecast)
    (r"\b(antikythera|eclipse|celestial (mechanism|event)|gears? (of|align)|when (do|will).*(resonate|align)|cosmic (timing|cadence))\b", "/api/antikythera_engine", {}),

    # stratigraphy core (history layers, before temporal)
    (r"\b(stratigr|layers? (of|in) (history|the storm)|geological (history|layers|epoch)|cross.section|deepest (layer|stratum))\b", "/api/stratigraphy_core", {}),

    # permafrost vault (stability, before platform/failure)
    (r"\b(permafrost|freeze.line|frozen (organs?|modules?)|stable (organs?|modules?|foundations?)|what (has )?frozen|depend(able| on)? (on )?the deep)\b", "/api/permafrost_vault", {}),

    # solar wind (external pressure/boundary, before uptime/gateway)
    (r"\b(solar wind|heliosphere|boundary pressure|pressure (from|on) (the|our) (boundary|edge)|external demand|how (much )?pressure)\b", "/api/solar_wind_pressure", {}),

    # bioluminescent depth (glowing/strata, before echo)
    (r"\b(bioluminescen|deep sea|glow(ing)? (modules?|organs?)|light field|abyssal|luminous (depth|field))\b", "/api/bioluminescent_depth", {}),

    # plankton bloom (micro layer, before census/echo)
    (r"\b(plankton|micro.?layer|small(est)? (modules?|organs?)|invisible (modules?|layer)|cytoskeleton|food chain)\b", "/api/plankton_bloom", {}),

    # coral atoll (accretion/reefs, before resonance)
    (r"\b(coral|atoll|reef|calcif(ied|y)|accret(ion|e)|bonds? (that )?harden|structural (bonds?|accretion))\b", "/api/coral_atoll", {}),

    # osmotic exchange (family diffusion, before crosstalk)
    (r"\b(osmotic|diffusion|membrane|family (exchange|balance)|patterns (that )?(spread|diffuse)|equilibr(ium|ate))\b", "/api/osmotic_exchange", {}),

    # kintsugi repair lineage
    (r"\b(kintsugi|golden (seam|repair|fix)|repair (the|our)? (cracks?|system|organs?)|gild(ed| the)|honor(ed)? (the )?(scars?|broken)|fracture|strain(s)?|crack(s|ed)? (survey|map|in)|debt (of|ledger|repair)|fix (the|our) (system|fracture)|scar(s?))", "/api/repair_ritual", {}),
    (r"\b(crack(s|ed)?|fractur(es?|ed)|broken (module|organ|things?)|stub(s)?|interrupted|what( is|'s)? broken|survey.*(crack|damage|damage map))\b", "/api/crack_mapper", {}),
    (r"\b(golden (seams?|bonds?|repair)|forged (seams?)|seams? (of)? gold|gilded (vessels?|modules?)|repair (plan|forge|plan\b))\b", "/api/crack_seams", {}),
    (r"\b(altar|reliquary|honored (vessels?|modules?)|sacred (archive|vessels?)|remember(ing)? (the )?(broken|scars?))\b", "/api/kintsugi_altar", {}),
    (r"\b(debt( ledgers?)? (of|for)? (repair|the system|structural)|structural debt|repay(ment|ing)?|fragility (debt|account)|balance sheet)\b", "/api/kintsugi_debt_ledger", {}),
    (r"\b(listen(ing)?|hear(ing)?|rumble(s)?|micro.?(fracture|crack)|strain (report|narrative)|early warning)\b", "/api/fracture_listener", {}),

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

    # constellation cartographer
    (r"\b(constellation|map|cluster|neighborhood|hub|graph|topology)\b", "/api/constellation_cartographer", {}),

    # reality weaver
    (r"\b(reality|weave|generate.*world|create.*world|simulate|universe|civilization)\b", "/api/reality_weaver", {"extract_topic": True}),

    # synesthesia
    (r"\b(synesthesia|sensory|color of|sound of|feel of|metaphor|richness|translate)\b", "/api/synesthesia", {"extract_module": True}),

    # dream sequencer
    (r"\b(dream|narrative|story arc|sequence|premonition|revelation|return|journey)\b", "/api/dream_sequencer", {}),

    # github bridge
    (r"\b(github|webhook|commit|star|release|pull request|pr|fork)\b", "/api/github_bridge", {}),

    # reflection pool
    (r"\b(reflect|reflection|look at yourself|self report|how is the frontier|vitals|vital signs)\b", "/api/reflection_pool", {}),

    # chronicle storyteller
    (r"\b(story|saga|chronicle|tell me the story|history|origin|saga|narrate|chapter)\b", "/api/chronicle_storyteller", {}),

    # thought meteorology
    (r"\b(weather|forecast.*ideas|idea weather|concept.*trend|trending|storm|temperature of ideas)\b", "/api/thought_meteorology", {}),


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
            # extract_module: for routes that need a named entity (synesthesia, reality_weaver)
            if params.get("extract_module") or params.get("extract_topic"):
                words = re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", query_lower)
                stop_words = {"the", "are", "what", "about", "show", "find", "search",
                              "echo", "for", "from", "with", "what", "is", "the", "color",
                              "sound", "feel", "metaphor", "synesthesia", "sensory", "translate",
                              "reality", "weave", "create", "show", "me", "about", "generate",
                              "of", "and", "a", "an", "in", "on", "how", "does", "do", "can"}
                meaningful = [w for w in words if w.lower() not in stop_words and len(w) > 2]
                if meaningful:
                    target = meaningful[-1]  # last meaningful word = target
                    if params.get("extract_module"):
                        result["module"] = target
                    if params.get("extract_topic"):
                        result["q"] = " ".join(meaningful[-3:])
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
