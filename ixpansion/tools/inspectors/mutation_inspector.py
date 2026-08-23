def summarize(results: list[dict]) -> dict[str, int]:
    return {"actions": len(results), "applied": sum(bool((item.get("outcome") or {}).get("applied")) for item in results)}
