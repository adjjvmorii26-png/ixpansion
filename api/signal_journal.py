"""
Signal Journal — Wave 391
The organism's living diary. Every sealed signal — undernet broadcasts,
concertos, shrine offerings, and prophecies — flows into a single timeline.
The journal is not written by one module; it is the memory of the whole.
"""
import json, time, os, sys

sys.path.insert(0, os.path.dirname(__file__))


def _feed_sources() -> list:
    entries = []
    # 1. undertone bulletin archive
    try:
        from mycelial_radio import _archive_read
        data = _archive_read()
        for x in data.get("bulletins", []):
            entries.append({
                "icon": "📻", "type": "broadcast", "wave": 390,
                "title": x.get("headline", "").replace("Hidden relationship surfaces: ", ""),
                "text": f"☂ {x.get('weather','')} · omen: {x.get('omen','')}",
                "timestamp": x.get("timestamp", 0),
            })
        for x in data.get("concertos", []):
            entries.append({
                "icon": "♪", "type": "concerto", "wave": 390,
                "title": x.get("title", "Undernet Concerto"),
                "text": f"{len(x.get('steps', []))} steps · tempo {x.get('tempo', 96)}",
                "timestamp": x.get("timestamp", 0),
            })
    except Exception:
        pass
    # 2. shrine offerings
    try:
        from lucid_shrine import hall as _hall
        h = _hall()
        for r in h.get("runs", [])[:20]:
            entries.append({
                "icon": "🏛", "type": "offering", "wave": 384,
                "title": f"{r.get('name','Wanderer')} the {r.get('title','Wayfarer')}",
                "text": f"score {r.get('score',0)} · cleared {r.get('realms_cleared',0)}/10 · {r.get('realm','?').replace('_',' ')}",
                "timestamp": r.get("timestamp", 0),
            })
    except Exception:
        pass
    # 3. prophecy seals
    try:
        from wave_prophecy import _load as _pload, PROPHECY_LOG
        log = _pload(PROPHECY_LOG, {"prophecies": []})
        seen = set()
        for x in log.get("prophecies", [])[-60:]:
            seal = x.get("seal") or x.get("prophecy", "")[:30]
            if seal in seen:
                continue
            seen.add(seal)
            entries.append({
                "icon": "🜁", "type": "prophecy", "wave": x.get("wave", 375),
                "title": f"Prophecy — Wave {x.get('wave','?')}",
                "text": f"{x.get('prophecy','')[:120]} · omen: {x.get('omen','')} · seal {seal}",
                "timestamp": x.get("timestamp", 0),
            })
    except Exception:
        pass
    entries.sort(key=lambda e: -e.get("timestamp", 0))
    return entries


def feed(limit: int = 40) -> dict:
    entries = _feed_sources()[:limit]
    counts = {}
    for e in entries:
        counts[e["type"]] = counts.get(e["type"], 0) + 1
    return {"action": "feed", "entries": entries, "count": len(entries), "sources": counts}


def sources() -> dict:
    entries = _feed_sources()
    counts = {}
    for e in entries:
        counts[e["type"]] = counts.get(e["type"], 0) + 1
    return {"action": "sources", "counts": counts, "total": len(entries)}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/feed")
    if path == "/feed":
        return feed(int(payload.get("limit", 40)) if str(payload.get("limit", "40")).isdigit() else 40)
    if path == "/sources":
        return sources()
    return {"error": "unknown", "available": ["/feed", "/sources"]}
