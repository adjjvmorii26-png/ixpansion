def event_to_metric(event: dict) -> dict:
    return {"name": f"ixpansion.{event.get('topic', 'unknown')}", "value": 1}
