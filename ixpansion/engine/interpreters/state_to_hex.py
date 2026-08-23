def state_to_hex(state: dict) -> str:
    lines = ["PUSH 0"]
    for _key, value in sorted(state.items()):
        lines.extend([f"PUSH {value}", "ADD"])
    lines.extend(["EMIT", "HALT"])
    return "\n".join(lines) + "\n"
