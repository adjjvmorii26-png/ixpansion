def bytecode_to_actions(bytecode: list[tuple[str, list[str]]]) -> list[dict]:
    actions: list[dict] = []
    for opcode, operands in bytecode:
        if opcode == "EMIT":
            actions.append({"type": "emit"})
        elif opcode == "STORE":
            actions.append({"type": "store", "target": operands[0]})
    return actions
