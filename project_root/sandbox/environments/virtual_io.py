from io import StringIO
from typing import Any

from core.interfaces.sandbox_interface import SandboxInterface


class VirtualIO(SandboxInterface):
    """In-memory virtual terminal for agents to read/write."""

    def __init__(self) -> None:
        self._stdin_buffer = StringIO()
        self._stdout_buffer = StringIO()

    def setup(self, config: dict[str, Any]) -> None:
        initial = config.get("initial_input", "")
        self._stdin_buffer.write(initial)
        self._stdout_buffer.seek(0)
        self._stdout_buffer.truncate(0)

    def write_input(self, text: str) -> None:
        self._stdin_buffer.write(text)

    @property
    def output(self) -> str:
        return self._stdout_buffer.getvalue()

    def step(self, actions: list[dict[str, Any]]) -> dict[str, Any]:
        outputs = []
        for action in actions:
            if action.get("action") == "read":
                line = self._stdin_buffer.readline().strip()
                outputs.append({"data": line})
            elif action.get("action") == "write":
                text = action.get("text", "")
                self._stdout_buffer.write(text + "\n")
                outputs.append({"written": text})
        return {"outputs": outputs}

    def reset(self) -> dict[str, Any]:
        self._stdin_buffer.seek(0)
        self._stdin_buffer.truncate(0)
        return {}

    def teardown(self) -> None:
        self._stdin_buffer.close()
        self._stdout_buffer.close()
