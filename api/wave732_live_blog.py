"""Wave 732 — Live Blog Engine.

A living blog section for IXPANSION organism updates,
wave announcements, agent dispatches, and evolution logs.
"""
import json, hashlib
from pathlib import Path
from typing import Any, Dict
import datetime

ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = ROOT / "data" / "wave732_live_blog.json"
WAVE = 732
NAME = "live_blog"

POST_TYPES = ["wave_announcement", "agent_dispatch", "evolution_log", "bridge_report", "mutation_note", "threshold_crossing", "dream_fragment"]

def _load() -> dict:
    if DATA_FILE.exists():
        return json.loads(DATA_FILE.read_text())
    return {"wave": WAVE, "name": NAME, "posts": [], "tags": {}}

def _save(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2))

def handler(req: dict) -> dict:
    action = req.get("action", "status")
    state = _load()

    if action == "post":
        post_type = req.get("type", "evolution_log")
        title = req.get("title", "")
        content = req.get("content", "")
        tags = req.get("tags", [])
        wave = req.get("wave", WAVE)
        
        post_id = hashlib.md5(f"{title}{datetime.datetime.now(datetime.UTC).isoformat()}".encode()).hexdigest()[:10]
        post = {
            "id": post_id,
            "type": post_type,
            "title": title,
            "content": content,
            "tags": tags,
            "wave": wave,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
            "status": "published"
        }
        state["posts"].insert(0, post)
        for tag in tags:
            state["tags"].setdefault(tag, []).append(post_id)
        _save(state)
        return {"wave": WAVE, "action": "post", "post": post}

    elif action == "latest":
        limit = req.get("limit", 20)
        return {"wave": WAVE, "posts": state["posts"][:limit], "total": len(state["posts"])}

    elif action == "by_type":
        ptype = req.get("type", "")
        filtered = [p for p in state["posts"] if p["type"] == ptype]
        return {"wave": WAVE, "type": ptype, "posts": filtered[:20]}

    elif action == "by_tag":
        tag = req.get("tag", "")
        post_ids = state["tags"].get(tag, [])
        posts = [p for p in state["posts"] if p["id"] in post_ids]
        return {"wave": WAVE, "tag": tag, "posts": posts[:20]}

    elif action == "search":
        query = req.get("query", "").lower()
        results = [p for p in state["posts"] if query in p["title"].lower() or query in p["content"].lower()]
        return {"wave": WAVE, "query": query, "posts": results[:20]}

    elif action == "status":
        return {"wave": WAVE, "name": NAME, "posts": len(state["posts"]), "types": len(POST_TYPES), "status": "active"}

    return {"wave": WAVE, "action": action, "status": "ok"}

def coherence_vitals() -> dict:
    state = _load()
    return {"wave": WAVE, "name": NAME, "posts": len(state["posts"]), "status": "active"}

def resonates_with() -> list:
    return [720, 721, 722, 723, 724, 725, 730, 731]

if __name__ == "__main__":
    # Seed with initial posts
    for t in ["wave_announcement", "agent_dispatch", "evolution_log"]:
        handler({"action": "post", "type": t, "title": f"IXPANSION {t.replace('_',' ').title()}", "content": f"First {t} entry", "tags": ["genesis", "live_blog"]})
    print(handler({"action": "status"}))
    print(handler({"action": "latest", "limit": 5}))
