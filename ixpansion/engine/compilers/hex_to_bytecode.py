from hex.hex_parser import parse


def compile_hex(source: str) -> list[tuple[str, list[str]]]:
    return [(item.opcode, item.operands) for item in parse(source)]
