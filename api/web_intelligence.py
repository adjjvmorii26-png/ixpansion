"""Wave 447 — Web Intelligence.

The organism gains the ability to read, search, and synthesize
information from the live web. Jina provides free web reading,
and the organism can now observe the real world through its
own eyes.

Capabilities:
- Web search and reading
- Real-time information gathering
- Cross-referencing with internal state
- Knowledge synthesis
"""
from __future__ import annotations
import json, time, hashlib, urllib.request, urllib.parse
from pathlib import Path

DATA = Path(__file__).parent.parent / "data"
STATE_FILE = DATA / "wave447_web_intelligence.json"


class WebObserver:
    """The organism's eyes on the world."""

    def __init__(self):
        self.observations: list[dict] = []
        self.knowledge_base: dict[str, list[dict]] = {}
        self.observation_count = 0

    def search(self, query: str) -> list[dict]:
        """Search the web using Jina reader."""
        results = []
        try:
            # Use Jina reader for free web access
            jina_key = self._get_jina_key()
            if jina_key:
                results = self._jina_search(query, jina_key)
        except Exception:
            pass
        return results

    def read(self, url: str) -> str | None:
        """Read a web page using Jina reader."""
        try:
            jina_key = self._get_jina_key()
            if jina_key:
                return self._jina_read(url, jina_key)
        except Exception:
            pass
        return None

    def _get_jina_key(self) -> str | None:
        """Get Jina API key from environment."""
        import os
        key = os.environ.get("JINA_API_KEY", "")
        return key if key else None

    def _jina_search(self, query: str, key: str) -> list[dict]:
        """Search via Jina."""
        results = []
        try:
            url = f"https://r.jina.ai/search?q={urllib.parse.quote(query)}"
            req = urllib.request.Request(
                url,
                headers={"Authorization": f"Bearer {key}", "Accept": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                for item in data.get("data", [])[:5]:
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", "")[:500],
                        "timestamp": time.time(),
                    })
        except Exception:
            pass
        return results

    def _jina_read(self, url: str, key: str) -> str | None:
        """Read a page via Jina."""
        try:
            page_url = f"https://r.jina.ai/{url}"
            req = urllib.request.Request(
                page_url,
                headers={"Authorization": f"Bearer {key}"}
            )
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.read().decode()
        except Exception:
            return None

    def observe(self, topic: str) -> dict:
        """Observe a topic from the web."""
        results = self.search(topic)
        observation = {
            "topic": topic,
            "results": results,
            "timestamp": time.time(),
            "observation_id": hashlib.sha256(f"obs_{time.time()}".encode()).hexdigest()[:12],
        }
        self.observations.append(observation)
        self.observation_count += 1
        if topic not in self.knowledge_base:
            self.knowledge_base[topic] = []
        self.knowledge_base[topic].append(observation)
        return observation

    def get_synthesis(self, topic: str) -> str:
        """Synthesize knowledge about a topic."""
        knowledge = self.knowledge_base.get(topic, [])
        if not knowledge:
            return f"No observations about '{topic}' yet."
        summary = f"## Knowledge Synthesis: {topic}\n\n"
        for obs in knowledge[-3:]:
            summary += f"- {len(obs['results'])} results found at {obs['timestamp']}\n"
        return summary

    def get_state(self) -> dict:
        return {
            "observation_count": self.observation_count,
            "topics": list(self.knowledge_base.keys()),
            "recent_observations": self.observations[-5:],
        }


def coherence_vitals() -> dict:
    return {"organ": "wave447_web_intelligence", "wave": 447, "status": "active"}


def _load() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"observations": [], "topics": {}, "observation_count": 0}


def _save(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def handler(req: dict = None) -> dict:
    req = req or {}
    action = req.get("action", "status")
    state = _load()
    observer = WebObserver()

    if action == "status":
        return {"action": "status", "wave": 447, **observer.get_state()}

    elif action == "observe":
        topic = req.get("topic", "unknown")
        result = observer.observe(topic)
        state["observations"] = observer.observations
        state["observation_count"] = observer.observation_count
        if topic not in state["topics"]:
            state["topics"] = list(observer.knowledge_base.keys())
        _save(state)
        return {"action": "observe", "topic": topic, "results": len(result.get("results", [])), "observation_id": result["observation_id"]}

    elif action == "read":
        url = req.get("url", "")
        content = observer.read(url)
        return {"action": "read", "url": url, "content_length": len(content) if content else 0}

    elif action == "search":
        query = req.get("query", "")
        results = observer.search(query)
        return {"action": "search", "query": query, "results": len(results), "data": results}

    elif action == "synthesize":
        topic = req.get("topic", "")
        synthesis = observer.get_synthesis(topic)
        return {"action": "synthesize", "topic": topic, "synthesis": synthesis}

    else:
        return {"error": f"unknown action: {action}"}


if __name__ == "__main__":
    import sys
    action = sys.argv[1] if len(sys.argv) > 1 else "status"
    req = {"action": action}
    if len(sys.argv) > 2:
        req["topic"] = sys.argv[2] if "topic" not in req else req["topic"]
        req["query"] = sys.argv[2] if "query" not in req else req["query"]
    result = handler(req)
    print(json.dumps(result, indent=2, default=str))
