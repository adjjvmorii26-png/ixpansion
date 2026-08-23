def render_timeline(timeline: list[dict]) -> str:
    return "TIMELINE " + " -> ".join(str(item.get("tick")) for item in timeline)
