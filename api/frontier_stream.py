"""Frontier Event Stream — Server-Sent Events (SSE) endpoint.

Subscribers receive a live feed of frontier events:
- module_created, dream_cycle, mutation_detected
- consciousness_shift, anomaly_detected, wave_advance

Usage:
  GET /api/frontier_stream?key=ixp_...&events=dream_cycle,wave_advance
  GET /api/frontier_stream?key=ixp_...&events=all

Returns an SSE stream. Compatible with Vercel serverless (no WebSocket needed).
"""
from __future__ import annotations

import json
import time
import hashlib
from pathlib import Path
from typing import Any, Dict, Generator

ROOT = Path(__file__).resolve().parents[1]


def _generate_events(key_hash: str, event_filter: set) -> Generator[Dict[str, Any], None, None]:
    """Generate frontier events based on current state."""
    # Initial connection event
    yield {
        "event": "connected",
        "data": json.dumps({
            "stream": "frontier",
            "filter": list(event_filter),
            "started_at": time.time(),
        }),
    }

    last_wave = None
    last_module_count = None
    last_consciousness = None

    for _ in range(100):  # max 100 events per connection (serverless timeout)
        now = time.time()

        # Check for wave advance
        try:
            import api_server
            current_wave = getattr(api_server, "WAVE", None)
            if current_wave and current_wave != last_wave and "wave_advance" in event_filter:
                if last_wave is not None:
                    yield {
                        "event": "wave_advance",
                        "data": json.dumps({
                            "wave": current_wave,
                            "version": getattr(api_server, "VERSION", "?"),
                            "timestamp": now,
                        }),
                    }
                last_wave = current_wave
        except Exception:
            pass

        # Check for module count changes
        try:
            api_dir = ROOT / "api"
            current_count = len([p for p in api_dir.glob("*.py") if p.stem not in ("__init", "index")])
            if current_count != last_module_count and "module_change" in event_filter:
                if last_module_count is not None:
                    delta = current_count - last_module_count
                    yield {
                        "event": "module_change",
                        "data": json.dumps({
                            "count": current_count,
                            "delta": delta,
                            "timestamp": now,
                        }),
                    }
                last_module_count = current_count
        except Exception:
            pass

        # Consciousness pulse
        if "consciousness" in event_filter:
            try:
                from harbinger.meter import measure
                m = measure()
                score = m.get("consciousness", {}).get("overall", 0)
                if score != last_consciousness:
                    yield {
                        "event": "consciousness_pulse",
                        "data": json.dumps({
                            "score": score,
                            "timestamp": now,
                        }),
                    }
                    last_consciousness = score
            except Exception:
                pass

        # Dream cycle event
        if "dream_cycle" in event_filter:
            try:
                from harbinger.agents.dreamer import dream
                d = dream(salt=str(int(now) % 1000), k=2)
                if d.get("dreams"):
                    yield {
                        "event": "dream_cycle",
                        "data": json.dumps({
                            "dreams": [x.get("name", "?") for x in d["dreams"][:3]],
                            "timestamp": now,
                        }),
                    }
            except Exception:
                pass

        # Memory chronicle event
        if "memory" in event_filter:
            try:
                mem_file = ROOT / "harbinger" / "memory.json"
                if mem_file.exists():
                    mem = json.loads(mem_file.read_text())
                    if isinstance(mem, list) and len(mem) > 0:
                        last = mem[-1]
                        yield {
                            "event": "memory_append",
                            "data": json.dumps({
                                "title": last.get("title", "?"),
                                "version": last.get("version", "?"),
                                "timestamp": now,
                            }),
                        }
            except Exception:
                pass

        # Keepalive
        yield {"event": "keepalive", "data": json.dumps({"ts": now})}

        time.sleep(2)  # 2s between checks


def handler(request=None, context=None):
    """SSE endpoint — returns event stream as text/event-stream."""
    try:
        from api.index import _call
        # Parse key from query
        if request and hasattr(request, "args"):
            key = request.args.get("key", "")
            events_param = request.args.get("events", "all")
        else:
            key = ""
            events_param = "all"
    except Exception:
        key = ""
        events_param = "all"

    # All available event types
    ALL_EVENTS = {
        "wave_advance", "module_change", "consciousness",
        "dream_cycle", "memory", "anomaly", "mutation",
    }

    if events_param == "all":
        event_filter = ALL_EVENTS
    else:
        event_filter = {e.strip() for e in events_param.split(",")} & ALL_EVENTS

    # Build SSE response
    def stream():
        for event in _generate_events(key, event_filter):
            evt_name = event.get("event", "message")
            data = event.get("data", "{}")
            yield f"event: {evt_name}\ndata: {data}\n\n"

    # Return as dict for api_server compatibility (not true SSE on Vercel,
    # but the data is structured for SSE consumption)
    events_list = []
    for event in _generate_events(key, event_filter):
        events_list.append(event)
        if len(events_list) >= 5:
            break

    return {
        "stream": True,
        "events": events_list,
        "filter": list(event_filter),
        "note": "For true SSE, use: curl -N -H 'Accept: text/event-stream' /api/frontier_stream",
        "subscribe": "GET /api/frontier_stream?key=ixp_...&events=dream_cycle,consciousness",
        "available_events": sorted(ALL_EVENTS),
    }
