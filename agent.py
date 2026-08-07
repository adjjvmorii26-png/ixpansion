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
        self.skills = {
            "summarize": self.summarize,
            "tasks": self.extract_tasks,
            "check_goal": self.check_goal,
        }

    def list_skills(self) -> List[str]:
        """Return the names of the skills available without network access."""
        return sorted(self.skills)

    def use_skill(self, skill: str, text: str) -> str:
        """Run a named local skill and record its result."""
        try:
            result = self.skills[skill](text)
        except KeyError as exc:
            available = ", ".join(self.list_skills())
            raise ValueError(f"Unknown skill '{skill}'. Available skills: {available}") from exc
        self.history.append(f"Used skill: {skill}")
        return result

    def summarize(self, text: str) -> str:
        """Return a compact first-sentence summary of text."""
        cleaned = " ".join(text.split())
        if not cleaned:
            return "No content provided."
        first_sentence = cleaned.split(".", 1)[0].strip()
        return f"Summary: {first_sentence}."

    def extract_tasks(self, text: str) -> str:
        """Extract simple task lines from text using common task markers."""
        tasks = []
        for line in text.splitlines():
            cleaned = line.strip()
            if cleaned.startswith(("- [ ]", "- ", "TODO:", "Task:")):
                task = cleaned.replace("- [ ]", "", 1).replace("- ", "", 1).strip()
                task = task.removeprefix("TODO:").removeprefix("Task:").strip()
                if task:
                    tasks.append(task)
        if not tasks:
            return "Tasks: none found."
        return "Tasks:\n" + "\n".join(f"- {task}" for task in tasks)

    def check_goal(self, goal: str) -> str:
        """Report whether a goal contains enough detail to act on."""
        cleaned = " ".join(goal.split())
        if len(cleaned.split()) < 3:
            return "Goal needs more detail. Add an outcome and useful constraints."
        return "Goal is actionable."

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
