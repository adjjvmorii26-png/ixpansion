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
        self.skill_usage: Dict[str, int] = {}
        self.skills = {
            "checklist": self.format_checklist,
            "dedupe": self.deduplicate_lines,
            "find": self.find_keyword,
            "priority": self.score_priority,
            "recycle": self.recycle_usage,
            "summarize": self.summarize,
            "tasks": self.extract_tasks,
            "validate": self.validate_text,
            "check_goal": self.check_goal,
            "export_memory": self.export_memory,
            "usage": self.usage_report,
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
        self.skill_usage[skill] = self.skill_usage.get(skill, 0) + 1
        self.history.append(f"Used skill: {skill}")
        return result

    def usage_report(self, _text: str = "") -> str:
        """Report how often each local skill has been used."""
        if not self.skill_usage:
            return "Skill usage: none."
        usage = ", ".join(
            f"{skill}={self.skill_usage[skill]}"
            for skill in sorted(self.skill_usage)
        )
        return f"Skill usage: {usage}."

    def recycle_usage(self, text: str = "") -> str:
        """Trim old agent state and reset usage counters.

        The optional text is the number of recent entries to retain; it defaults
        to five and never permits a negative retention count.
        """
        try:
            keep = max(0, int(text.strip())) if text.strip() else 5
        except ValueError as exc:
            raise ValueError("Recycle count must be a non-negative integer") from exc
        removed_history = max(0, len(self.history) - keep)
        removed_memory = max(0, len(self.memory) - keep)
        self.history = self.history[-keep:] if keep else []
        self.memory = self.memory[-keep:] if keep else []
        self.skill_usage.clear()
        return (
            f"Recycled usage: removed {removed_history} history entries and "
            f"{removed_memory} memory entries; retained {keep}."
        )

    def score_priority(self, text: str) -> str:
        """Classify text as high, medium, or low priority from its wording."""
        lowered = text.lower()
        if any(word in lowered for word in ("urgent", "critical", "immediately")):
            return "Priority: high."
        if any(word in lowered for word in ("important", "soon", "deadline")):
            return "Priority: medium."
        return "Priority: low."

    def validate_text(self, text: str) -> str:
        """Check whether text is present and contains at least three words."""
        words = text.split()
        if not words:
            return "Validation: empty text."
        if len(words) < 3:
            return "Validation: too short."
        return "Validation: valid."

    def deduplicate_lines(self, text: str) -> str:
        """Remove repeated non-empty lines while preserving their first order."""
        seen = set()
        lines = []
        for line in text.splitlines():
            cleaned = line.strip()
            if cleaned and cleaned not in seen:
                seen.add(cleaned)
                lines.append(cleaned)
        return "\n".join(lines) if lines else "No unique lines found."

    def find_keyword(self, text: str) -> str:
        """Find a case-insensitive keyword in text.

        The first line is the keyword and the remaining lines are searched.
        """
        lines = text.splitlines()
        keyword = lines[0].strip() if lines else ""
        content = "\n".join(lines[1:])
        if not keyword:
            return "Find: provide a keyword on the first line."
        return (
            f"Find: '{keyword}' found."
            if keyword.lower() in content.lower()
            else f"Find: '{keyword}' not found."
        )

    def format_checklist(self, text: str) -> str:
        """Format non-empty lines as unchecked Markdown checklist items."""
        items = [line.strip(" -\t") for line in text.splitlines() if line.strip()]
        if not items:
            return "Checklist: empty."
        return "Checklist:\n" + "\n".join(f"- [ ] {item}" for item in items)

    def export_memory(self, _text: str = "") -> str:
        """Return the current memory as a portable plain-text block."""
        if not self.memory:
            return "Memory: empty."
        return "Memory:\n" + "\n".join(f"- {item}" for item in self.memory)

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
