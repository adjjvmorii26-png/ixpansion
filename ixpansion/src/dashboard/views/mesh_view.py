def render_mesh(nodes: int) -> str:
    return "MESH " + "-".join(str(index) for index in range(max(0, nodes)))
