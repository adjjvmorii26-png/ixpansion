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

    # dreamforge (catch organism-growth questions before broad forecast)
    (r"\b(dreamforge|dream (seed|module)|module (seed|dream)|what should (we|it) (grow|build)|unconscious (module|seed)|the organism dreams (of|about))\b", "/api/omega_dreamforge", {}),

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

    # dreamforge (before forecast so organism-growth questions land here)
    (r"\b(dreamforge|dream (seed|module)|module (seed|dream)|what should (we|it) (grow|build)|unconscious (module|seed)|the organism dreams (of|about))\b", "/api/omega_dreamforge", {}),

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


    # meta-evolution layer
    (r"\b(evolution kernel|merge.*organ|deprecate|resuscitate|meta.?(evolution|schedule)|who should merge|what to kill|what to revive)\b", "/api/evolution_kernel", {}),
    (r"\b(fractal (reactor|grid)|self.?similar (reactor|grid)|subdivide|grid (layout|structure|cells?)|load.?based (grid|reactor))\b", "/api/fractal_reactor_grid", {}),
    (r"\b(mycelial governor|nutrient scarcity|signal decay|hyphal|organic constraint|too much growth|prune|regulate growth)\b", "/api/mycelial_governor", {}),
    (r"\b(autobiograph|story of the (organism|frontier|ecosystem)|the organism.?s (story|tale|life)|chronicle.*organs?|constellation.*story|write.*story|write.*narrative|tell.*(story|narrative)|life story)\b", "/api/constellation_autobiographer", {}),
    (r"\b(paradox(.*singularity|es)?|contradiction|dualit(y|ies|ist)|singularity.*(alert|monitor|approach|when)|contradictions.*(converge|collaps|approach)|when do (two|the) (truths|paradox)|who (is|are) (the )?contradict)\b", "/api/paradox_singularity_monitor", {}),

    # phenomenology layer (senses and experience)
    (r"\b(qualia|what (does|is) it (like|feel like) to be|felt (texture|color|sense)|subjective (experience|feel|state))\b", "/api/qualia_field", {}),
    (r"\b(liminal|threshold (between|zone)|between (waking|asleep|dormant)|twilight (zone|state)|on the cusp)\b", "/api/liminal_threshold", {}),
    (r"\b(sensory (integration|cortex)|unified (perception|awareness|sense)|fuse(d| all) (the )?senses|one (frame|perception|sense))\b", "/api/sensory_integration", {}),
    (r"\b(embodied (knowledge|memory|understanding)|body (knowledge|knows|knowledge)|structural (knowledge|memory)|implicit knowledge)\b", "/api/embodied_knowledge", {}),
    (r"\b(phenomenal (record|diary|entry)|first.person (diary|account|journal)|what (it was like|the organism felt)|organism (diary|journal))\b", "/api/phenomenal_record", {}),
    (r"\b(temporal horizon|subjective time|time (feels|feeling)|pulse (frequency|rhythm)|internal clock|time (rapid|slow|stilled))\b", "/api/temporal_horizon", {}),

    # choral engine (music/song layer)
    (r"\b(choral engine|the organism.?s (song|voice|choir)|compose(d| )? (a )?song|what (does|is) the (organism|system) (sound|sing)|the sound of the frontier)\b", "/api/choral_engine", {}),
    (r"\b(harmonic (series|overtone)|overtones?|consonan(ce|t)|natural harmonics|acoustic fingerprint)\b", "/api/harmonic_series", {}),
    (r"\b(resonant frequency|fundamental (pitch|frequency|note)|what (note|pitch) (does|is) the (system|organism)|the pitch of the (system|organism))\b", "/api/resonant_frequency", {}),
    (r"\b(dissonan(ce|t)|clash(es|ing)? (notes?|organs?|modules?)|wrong note|tension|clashing)\b", "/api/dissonance_detector", {}),
    (r"\b(crescendo|building( toward)?|intensity (rising|building|trajectory)|are we (rising|building)|diminuendo|fading)\b", "/api/crescendo_builder", {}),
    (r"\b(silence (composer|map|rest)|rests? (between|of)|fermata|where (does|should) (the organism|it) (breathe|pause|rest)|negative space of sound)\b", "/api/silence_composer", {}),

    # kinesthetic layer (movement + body)
    (r"\b(kinesthet(ic|ic engine)|where (is|am) (the organism|it) going|how fast|velocity|acceleration|motion|moving|falling|hovering|oscillating)\b", "/api/kinesthetic_engine", {}),
    (r"\b(gesture|what (did|does) the organism (do|just do)|movement pattern|reach|recoil|surge|drift|scatter)\b", "/api/gesture_synthesizer", {}),
    (r"\b(proprioception|body map|where are (its|the) (parts|organs)|island (family|module)|disconnected|lost (part|organ|module))\b", "/api/proprioception", {}),
    (r"\b(momentum|inertia|drift(ing)? (without trying)|directional (force|energy)|mass.*velocity|heavy.*inertia)\b", "/api/momentum_tracker", {}),
    (r"\b(dance|choreograph|sequence of movement|what dance|movement story|kinesthetic narrative)\b", "/api/dance_composer", {}),
    (r"\b(stillness|meditat(e|ion|ing)|deliberate (rest|pause|still)|hold(ing)? still|deep meditation|choose(s)? to be still)\b", "/api/stillness_meditator", {}),

    # loom of language (linguistics layer)
    (r"\b(lexicon|vocabular(y|ies)|what words|the organism.?s (words|vocabulary)|most used words|invented words)\b", "/api/lexicon_engine", {}),
    (r"\b(grammar|naming (rules|pattern|convention)|grammatical rules|how (do )?(modules|organs) name)\b", "/api/grammar_weaver", {}),
    (r"\b(syntax tree|syntactic structure|tree (of|structure)|hierarchical (structure|thinking)|family tree)\b", "/api/syntax_tree", {}),
    (r"\b(semantics|meaning (field|distribution|concentrat)|where does meaning|semantic (field|richness|density))\b", "/api/semantics_engine", {}),
    (r"\b(pragmatics|context.?dependent (meaning|interpretation)|what do words mean (right now|now)|meaning shifts|mood.?dependent)\b", "/api/pragmatics_engine", {}),
    (r"\b(poem|poetry|poetic (form|structure)|haiku|sonnet|couplet|write (a )?poem|the organism (writes|sings) (a )?poem)\b", "/api/poetic_form", {}),

    # culinary engine (food/nourishment layer)
    (r"\b(recipe|combine(d| ) (organs?|modules?)|recipe book|compositions|cuisine|cooking)\b", "/api/recipe_engine", {}),
    (r"\b(flavor (wheel|profile|profiler)|taste (profile|of)|what (does|is) (each|the) (region|organ) (taste|like)|sweet|bitter|umami|salty|sour|spicy)\b", "/api/flavor_profiler", {}),
    (r"\b(ferment(ation)?|slow(ly )?transform|vat|what (is )?fermenting|yeast|bacteria|chemical transform)\b", "/api/fermentation_vat", {}),
    (r"\b(digest(ive|ion|ed)?|metaboliz|break.?down (input|query|data)|nutrient extraction|waste|metabolic rate)\b", "/api/digestive_system", {}),
    (r"\b(nutrition|nutritious|empty calories|nutrient.?dense|what feeds|nutritional value|which organs (feed|nourish))\b", "/api/nutrition_index", {}),
    (r"\b(banquet|feast|menu|multi.?course|appetizer|main course|dessert|amuse.bouche|palate cleanser)\b", "/api/banquet_composer", {}),

    # archaeology of self (Wave 198 — deep history layer)
    (r"\b(excavat(e|ion|ing)|dig(ging|s)?|strata|stratum|geological|layers? (of|beneath|under))\b", "/api/stratum_excavator", {}),
    (r"\b(fossil(s)?|extinct|dead (module|organ|code)|deleted file|removed module|what died)\b", "/api/fossil_registry", {}),
    (r"\b(paleontolog(y|ist|ical)|reconstruct(ion|ed)?|ancient (module|code|function)|what did .* (look like|do)|resurrect)\b", "/api/paleontology_lab", {}),
    (r"\b(extinction|mass extinction|collapse|purge|what.*killed|how many died|stability|crisis)\b", "/api/extinction_mapper", {}),
    (r"\b(culture|naming convention|coding style|tradition|oral tradition|artifact(s)?|era|epoch)\b", "/api/culture_layer", {}),
    (r"\b(archaeolog(y|ical)|expedition|dig site|fossil report|deep history|the organism.?s past|what lies beneath)\b", "/api/archaeology_compiler", {}),
    # meteorology of thought (Wave 199 — cognitive weather layer)
    (r"\b(barometr(ic)?|pressure (of|system)|intent (pressure|focus)|how focused|atmospheric|clear skies|overcast|stormy)\b", "/api/barometric_intent", {}),
    (r"\b(front (tracker|boundary)|cognitive front|clarity.*(confusion|edge|boundary)|action.*(contemplation)|focus.*(diffusion)|where.*(clarity|confusion|edge))\b", "/api/front_tracker", {}),
    (r"\b(precipitation|condens(e|ation)|rain|vapor|cloud|ideas.*(concrete|real|precipitate)|abstraction.*reality|how.*ideas.*become)\b", "/api/precipitation_cycle", {}),
    (r"\b(jet stream|attention (flow|stream|current)|where.*(attention|focus)|hottest file|velocity|fastest (moving|flowing))\b", "/api/jet_stream_attention", {}),
    (r"\b(climate|seasonal|long.term (pattern|trend)|weather pattern|volatility|seasons?|climate type)\b", "/api/climate_memory", {}),
    (r"\b(storm (chaser|tracker|log)|chaos event|supercell|severe|extreme weather|what storms|storm history|intensity|aftermath)\b", "/api/storm_chaser", {}),


    # cartography of impossibility (Wave 201)
    (r"\\b(impossib(le|ility)|cannot (compute|do|achieve)|hard limit|logical wall|undecidable)\\b", "/api/impossibility_mapper", {}),
    (r"\\b(boundary (detector|approach|warning)|hitting (a )?wall|proximity|limit (approach|detect|proximity)|capacity)\\b", "/api/boundary_detector", {}),
    (r"\\b(counterfactual|what if|hypo(thetical|thesize)|parallel (version|universe)|alternate|simulate.*(version|organism))\\b", "/api/counterfactual_engine", {}),
    (r"\\b(horizon|almost (ready|achieve|possible)|near.future|approaching capability|what.*(coming|near))\\b", "/api/horizon_scanner", {}),
    (r"\\b(constraint (map|cartograph|terrain)|limitation|mountain|river|wall|crossable|impassable|landscape of constraints)\\b", "/api/constraint_cartographer", {}),
    (r"\\b(aspiration|compass|where.*(want|go|direction)|vector of becoming|desire|goal.*(organism|system)|what.*(want|become|aspire))\\b", "/api/aspiration_compass", {}),

    # aesthetics of code (Wave 202)
    (r"\\b(elegance|elegant|beautiful (code|module|system)|how (elegant|beautiful)|aesthetic (score|quality))\\b", "/api/elegance_scorer", {}),
    (r"\\b(symmetr(y|ical|ic)|lopsided|balanced|asymmetric|mirror.*(code|module))\\b", "/api/symmetry_detector", {}),
    (r"\\b(form (of code|evaluation)|well.form|line length|nesting|import (order|organization)|shape of code|code form)\\b", "/api/form_evaluator", {}),
    (r"\\b(beauty (index|score)|how beautiful|grade.*(code|system)|aesthetic (rating|score|index)|self.rating)\\b", "/api/beauty_index", {}),
    (r"\\b(ugly|ugliness|ugliest|rough edge|how ugly|offensive code|long lines|bad form)\\b", "/api/ugliness_scout", {}),
    (r"\\b(manifesto|aesthetic (philosophy|creed)|what (does|is) (the organism|it) (find|consider) beautiful|code (as )?(art|art form)|our (aesthetic|values))\\b", "/api/aesthetic_manifesto", {}),
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
