def actions_to_hex(actions: list[dict]) -> str:
    lines = [f"PUSH {action.get('value', 1)}" for action in actions]
    lines.extend(["ADD"] * max(0, len(lines) - 1))
    lines.append("HALT")
    return "\n".join(lines) + "\n"
