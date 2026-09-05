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
    # 3. remembrances (Organurna Loop)
    try:
        from organurna_loop import _remembrances_read
        rem = _remembrances_read().get("remembrances", [])
        for x in rem[::-1][:20]:
            entries.append({
                "icon": "🏝", "type": "remembrance", "wave": 393,
                "title": f"Re-membered: {x.get('module','?').replace('_',' ')}",
                "text": f"{x.get('verse','')} · sigil {x.get('sigil','')}",
                "timestamp": x.get("timestamp", 0),
            })
    except Exception:
        pass
    # 4. prophecy seals
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


import base64, urllib.parse, urllib.request, urllib.error, random

GH_TOKEN = os.environ.get("IXP_GH_TOKEN", "")
CHAPTER_PATH = "data/signal_memoir.json"
CHAPTER_SPAN = 25  # one chapter per N waves


def _gh_call(method, url, payload=None):
    if not GH_TOKEN:
        return {"ok": False}
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", "Bearer " + GH_TOKEN)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    data = json.dumps(payload).encode() if payload is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=15) as resp:
            return {"ok": True, "status": resp.status, "body": json.loads(resp.read().decode() or "{}")}
    except urllib.error.HTTPError as e:
        try:
            return {"ok": False, "status": e.code, "body": json.loads(e.read().decode() or "{}")}
        except Exception:
            return {"ok": False, "status": e.code, "body": {}}


def _memoir_read() -> dict:
    fallback = {"chapters": []}
    if GH_TOKEN:
        r = _gh_call("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + CHAPTER_PATH + "?ref=main")
        if r["ok"]:
            try:
                return json.loads(base64.b64decode(r["body"]["content"]).decode())
            except Exception:
                return fallback
    f = os.path.join(os.path.dirname(__file__), "..", "data", "signal_memoir.json")
    for _p in (f, os.path.join("/tmp", "signal_memoir.json")):
        try:
            with open(_p) as fh:
                return json.load(fh)
        except Exception:
            pass
    return fallback


def _memoir_write(data: dict) -> bool:
    if GH_TOKEN:
        r = _gh_call("GET", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + CHAPTER_PATH + "?ref=main")
        sha = r["body"].get("sha") if r["ok"] else None
        payload = {
            "message": "MEMOIR — the organism writes a chapter",
            "content": base64.b64encode(json.dumps(data, indent=2).encode()).decode(),
            "branch": "main",
        }
        if sha:
            payload["sha"] = sha
        return _gh_call("PUT", "https://api.github.com/repos/adjjvmorii26-png/ixpansion/contents/" + CHAPTER_PATH, payload)["ok"]
    f = os.path.join(os.path.dirname(__file__), "..", "data", "signal_memoir.json")
    try:
        with open(f, "w") as fh:
            json.dump(data, fh, indent=2)
    except OSError:
        with open(os.path.join("/tmp", "signal_memoir.json"), "w") as fh:
            json.dump(data, fh, indent=2)
    return True


def _latest_wave() -> int:
    entries = _feed_sources()
    waves = [e.get("wave", 0) for e in entries]
    return max(waves) if waves else 390


def _chapter_title() -> str:
    entries = _feed_sources()
    pairs = [e for e in entries if e["type"] == "broadcast"]
    if not pairs:
        return "The Chapter of the First Signal"
    title_parts = (pairs[0].get("title", "") or "").split(" ↔ ")
    a = (title_parts[0] or "a module").replace("_", " ")
    b = (title_parts[1] or "another module").replace("_", " ") if len(title_parts) > 1 else "the lattice"
    return f"The Chapter of {a.title()} and {b.title()}"


def seal_chapter() -> dict:
    data = _memoir_read()
    chapters = data.get("chapters", [])
    wave = _latest_wave()
    threshold = (wave // CHAPTER_SPAN) * CHAPTER_SPAN
    if any(c.get("threshold") == threshold for c in chapters):
        return {"action": "chapter", "sealed": False,
                "chapter": next(c for c in chapters if c.get("threshold") == threshold),
                "note": "chapter already sealed"}
    entries = _feed_sources()
    chapter = {
        "number": len(chapters) + 1,
        "threshold": threshold,
        "wave": wave,
        "title": _chapter_title(),
        "snippet": (entries[0].get("text", "")[:140] if entries else ""),
        "signal_count": len(entries),
        "top_signal": entries[0].get("title", "") if entries else "",
        "sealed_at": time.time(),
    }
    # conflict-retry append
    for attempt in range(4):
        merged = _memoir_read()
        merged.setdefault("chapters", []).append(chapter)
        merged["chapters"] = merged["chapters"][-40:]
        if _memoir_write(merged):
            return {"action": "chapter", "sealed": True, "chapter": chapter, "total": len(merged["chapters"])}
    return {"action": "chapter", "sealed": False, "error": "memoir is busy; try again"}


def memoir() -> dict:
    data = _memoir_read()
    chapters = data.get("chapters", [])
    return {"action": "memoir", "chapters": chapters[::-1], "total": len(chapters),
            "persisted": "github" if GH_TOKEN else "local"}


def handler(payload=None, context=None):
    payload = payload or {}
    path = payload.get("path", "/feed")
    if path == "/feed":
        result = feed(int(payload.get("limit", 40)) if str(payload.get("limit", "40")).isdigit() else 40)
        try:
            result["chapter"] = seal_chapter()
            result["memoir"] = memoir()
        except Exception:
            pass
        return result
    if path == "/sources":
        return sources()
    if path == "/chapter":
        return seal_chapter()
    if path == "/memoir":
        return memoir()
    return {"error": "unknown", "available": ["/feed", "/sources", "/chapter", "/memoir"]}
