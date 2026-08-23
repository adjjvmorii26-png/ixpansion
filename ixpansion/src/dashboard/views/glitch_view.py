def render_glitches(anomalies: list[str]) -> str:
    return "GLITCHES " + (", ".join(anomalies) if anomalies else "none")
