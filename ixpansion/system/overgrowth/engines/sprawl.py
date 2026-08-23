def sprawl(nodes: list[str], count: int = 1) -> list[str]:
    return nodes + [f"sprawl-{index + 1}" for index in range(max(0, count))]
