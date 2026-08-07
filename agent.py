import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import dotenv_values

from tokenrouter_client import TokenRouterClient


def _load_env_file(env_path: Optional[Path] = None) -> None:
    """Populate os.environ from a local .env file when present."""
    path = env_path or Path(".env")
    if not path.exists():
        return

    for key, value in dotenv_values(path).items():
        if value is not None:
            os.environ.setdefault(key, value)


def _get_api_key() -> Optional[str]:
    """Return a configured API key from the environment or a local .env file."""
    _load_env_file()

    for key_name in (
        "TOKENROUTER_API_KEY",
        "XAI_API_KEY",
        "API_KEY",
        "OPENAI_API_KEY",
        "ANTHROPIC_API_KEY",
    ):
        value = os.getenv(key_name)
        if value:
            return value

    return None


class Agent:
    """Simple agent skeleton for IXPANSION."""

    def __init__(self, name: str = "Agent", memory: Optional[List[str]] = None):
        self.name = name
        self.memory = memory or []
        self.history: List[str] = []
        self.api_key = _get_api_key()

    def ask(self, prompt: str) -> str:
        """Send a prompt to TokenRouter, failing clearly when no key is configured."""
        if not self.api_key:
            raise RuntimeError("TOKENROUTER_API_KEY is not configured")
        return TokenRouterClient(self.api_key).complete(prompt)

    def remember(self, item: str) -> None:
        self.memory.append(item)
        self.history.append(f"Remembered: {item}")

    def observe(self, observation: str) -> None:
        self.history.append(f"Observed: {observation}")
        self.remember(observation)

    def plan(self, goal: str) -> List[str]:
        plan = [
            f"Define goal: {goal}",
            "Gather context",
            "Select next action",
            "Execute action",
            "Review results",
        ]
        self.history.append(f"Planned: {goal}")
        return plan

    def act(self, action: str) -> str:
        result = f"{self.name} executes '{action}'."
        self.history.append(result)
        return result

    def run(self, goal: str) -> Dict[str, Any]:
        self.observe(f"Starting goal: {goal}")
        plan = self.plan(goal)
        results = [self.act(action) for action in plan]
        self.history.append(f"Completed goal: {goal}")
        return {
            "goal": goal,
            "plan": plan,
            "results": results,
            "history": self.history,
            "api_key_configured": bool(self.api_key),
        }
