from typing import Any


class OmegaPrimeError(Exception):
    def __init__(self, message: str, code: str = "OP_ERR") -> None:
        super().__init__(message)
        self.code = code


class AgentSpawnError(OmegaPrimeError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, "AGENT_SPAWN")


class RealmError(OmegaPrimeError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, "REALM")


class HexEncodeError(OmegaPrimeError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, "HEX_ENC")


class HexDecodeError(OmegaPrimeError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg, "HEX_DEC")


ERROR_MAP: dict[str, type[OmegaPrimeError]] = {
    "AGENT_SPAWN": AgentSpawnError,
    "REALM": RealmError,
    "HEX_ENC": HexEncodeError,
    "HEX_DEC": HexDecodeError,
}


def raise_for_code(code: str, message: str) -> None:
    exc_cls = ERROR_MAP.get(code, OmegaPrimeError)
    raise exc_cls(message)
