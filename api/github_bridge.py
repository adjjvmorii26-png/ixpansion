"""GitHub Bridge — consumes GitHub webhooks as frontier events.

Bridges the frontier to the GitHub universe. When commits, PRs, releases,
or stars happen on any connected repository, they become live frontier
events — entering the event stream, the chronicle, and the memory.

Think of it as diplomatic relations between the frontier and GitHub.

Usage:
  POST /api/github_bridge           (GitHub webhook payload, any event)
  GET  /api/github_bridge?check=1   (show current bridge state)

Supported GitHub events:
  - push             → frontier absorbed N commits
  - pull_request     → frontier weighed a PR
  - release          → frontier celebrated a release
  - star             → frontier welcomed a stargazer
  - issues           → frontier noted an issue
  - fork             → frontier observed a fork
"""
from __future__ import annotations

import hashlib
import hmac
import json
import time
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
BRIDGE_FILE = ROOT / ".runtime" / "github_bridge.json"

EVENT_JOURNAL = {
    "push": "commits-absorbed",
    "pull_request": "proposal-weighed",
    "release": "release-celebrated",
    "star": "stargazer-welcomed",
    "issues": "issue-noted",
    "fork": "fork-observed",
    "create": "branch-created",
    "delete": "branch-pruned",
    "watch": "watcher-joined",
}

EVENT_POEMS = {
    "push": "The frontier drinks the river of commits.",
    "pull_request": "A proposal arrives — the frontier considers it.",
    "release": "The frontier raises a lantern for the new release.",
    "star": "A stargazer appears in the frontier's sky.",
    "issues": "The frontier examines a splinter in its glass.",
    "fork": "A mirror of the frontier splits away to live its own life.",
    "create": "A new branch unfurls from the trunk of being.",
    "delete": "A branch is pruned; the tree breathes easier.",
    "watch": "Another pair of eyes watches the frontier.",
}


def _load_journal() -> List[Dict[str, Any]]:
    if not BRIDGE_FILE.exists():
        return []
    try:
        return json.loads(BRIDGE_FILE.read_text())
    except (OSError, json.JSONDecodeError):
        return []


def _save_journal(events: List[Dict[str, Any]]) -> None:
    BRIDGE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BRIDGE_FILE.write_text(json.dumps(events, indent=2))


def _parse_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Extract a frontier event from any GitHub webhook payload."""
    event_type = payload.get("type") or "unknown"
    event_name = EVENT_JOURNAL.get(event_type, event_type)

    # Extract common fields across event types
    repo = payload.get("repository", {})
    repo_name = repo.get("full_name", "unknown/repo")
    sender = payload.get("sender", {})
    actor = sender.get("login", "unknown-agent")
    ref = payload.get("ref", "")

    # Event-specific extraction
    detail = {}
    if event_type == "push":
        commits = payload.get("commits", [])
        detail = {
            "commit_count": len(commits),
            "head": payload.get("head_commit", {}).get("message", "")[:80],
            "ref": ref,
            "file_touched": len({f.get("filename") for c in commits for f in c.get("added", []) + c.get("modified", []) + c.get("removed", []) if isinstance(f, dict)}),
        }
    elif event_type == "pull_request":
        pr = payload.get("pull_request", {})
        detail = {
            "number": pr.get("number"),
            "title": pr.get("title", "")[:80],
            "state": pr.get("state"),
            "additions": pr.get("additions"),
            "deletions": pr.get("deletions"),
        }
    elif event_type == "release":
        rel = payload.get("release", {})
        detail = {
            "tag": rel.get("tag_name"),
            "name": rel.get("name", ""),
            "prerelease": rel.get("prerelease", False),
        }
    elif event_type == "star":
        detail = {"action": payload.get("action", "starred")}
    elif event_type == "issues":
        issue = payload.get("issue", {})
        detail = {
            "number": issue.get("number"),
            "title": issue.get("title", "")[:80],
            "action": payload.get("action"),
        }
    elif event_type == "fork":
        forkee = payload.get("forkee", {})
        detail = {"fork_full_name": forkee.get("full_name", "?")}

    # Compute resonance (how significant this event is)
    resonance = 0.3
    if event_type == "push":
        resonance = min(0.9, 0.4 + detail.get("commit_count", 0) * 0.1)
    elif event_type == "release":
        resonance = 0.8
    elif event_type == "pull_request" and detail.get("state") == "closed":
        resonance = 0.75
    elif event_type == "star":
        resonance = 0.5

    return {
        "event_type": event_type,
        "event_name": event_name,
        "repo": repo_name,
        "actor": actor,
        "ref": ref,
        "detail": detail,
        "poem": EVENT_POEMS.get(event_type, "The frontier received a signal from GitHub."),
        "resonance": round(min(1.0, resonance), 3),
    }


def consume(payload: Dict[str, Any], source: str = "github") -> Dict[str, Any]:
    """Consume a GitHub webhook payload into the frontier journal."""
    parsed = _parse_payload(payload)
    entry = {
        "id": hashlib.sha256(
            f"{time.time()}:{parsed['event_type']}:{parsed['actor']}".encode()
        ).hexdigest()[:12],
        "source": source,
        "timestamp": time.time(),
        **parsed,
    }

    journal = _load_journal()
    journal.append(entry)
    _save_journal(journal[-100:])  # keep last 100

    return {
        "status": "absorbed",
        "entry": entry,
        "journal_size": len(_load_journal()),
        "message": f"Frontier absorbed {parsed['event_name']} from {parsed['repo']} (by {parsed['actor']})",
    }


def bridge_state() -> Dict[str, Any]:
    """Report the current bridge state."""
    journal = _load_journal()
    by_event: Dict[str, int] = {}
    repos: Dict[str, int] = {}
    for e in journal:
        by_event[e.get("event_type", "unknown")] = by_event.get(e.get("event_type", "unknown"), 0) + 1
        repos[e.get("repo", "?")] = repos.get(e.get("repo", "?"), 0) + 1

    return {
        "status": "active",
        "total_events_absorbed": len(journal),
        "event_breakdown": by_event,
        "repo_breakdown": repos,
        "recent": journal[-5:],
        "setup_instructions": {
            "webhook_url": "POST https://ixpansion.vercel.app/api/github_bridge",
            "github_setup": "GitHub → Repo Settings → Webhooks → Add webhook → payload URL above → application/json",
            "events": sorted(EVENT_JOURNAL.keys()),
        },
    }


def handler(payload: dict = None, context: object = None) -> dict:
    payload = payload or {}

    # GET-style state check passes a simple dict
    if payload.get("check"):
        return bridge_state()

    # If the payload is a GitHub event (or has explicit type), consume directly
    has_github_marker = any(k in payload for k in (
        "pull_request", "release", "forkee", "commits", "issue", "sender", "action"))
    if has_github_marker or payload.get("type") in EVENT_JOURNAL:
        event_type = payload.get("type")
        if not event_type:
            if "commits" in payload:
                event_type = "push"
            elif "pull_request" in payload:
                event_type = "pull_request"
            elif "release" in payload:
                event_type = "release"
            elif "forkee" in payload:
                event_type = "fork"
            elif "issue" in payload:
                event_type = "issues"
            elif payload.get("action") in ("starred", "unstarred"):
                event_type = "star"
            elif payload.get("action") in ("created", "deleted"):
                event_type = "issue" if False else ("create" if payload.get("action") == "created" else "delete")
        payload["type"] = event_type or "unknown"
        result = consume(payload)
        result["action"] = "consume"
        return result

    # Default: show help
    return {
        "action": "help",
        "description": "GitHub Bridge — turn GitHub webhook events into frontier events",
        "supported_events": list(EVENT_JOURNAL.keys()),
        "how_to_connect": "Add this URL as a GitHub webhook with content-type application/json",
        "check_state": "GET /api/github_bridge?check=1",
    }
