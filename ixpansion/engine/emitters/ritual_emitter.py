def ritual(agent: str, action: dict) -> str:
    return f"; {agent}\nPUSH 1\nSTORE {action.get('node', 'origin')}\nHALT\n"
