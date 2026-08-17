import os
import re
import hashlib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import dotenv_values

from tokenrouter_client import TokenRouterClient


@dataclass(frozen=True)
class SkillSpec:
    """Stable metadata for discovering and composing local skills."""

    name: str
    mutates_state: bool = False
    network_required: bool = False


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
    """Offline-first agent with an optional premium TokenRouter model."""

    DEFAULT_MEMORY_LIMIT = 100
    DEFAULT_HISTORY_LIMIT = 200

    def __init__(
        self,
        name: str = "Agent",
        memory: Optional[List[str]] = None,
        model: Optional[str] = None,
        memory_limit: int = DEFAULT_MEMORY_LIMIT,
        history_limit: int = DEFAULT_HISTORY_LIMIT,
    ):
        self.name = name
        if memory_limit < 0 or history_limit < 0:
            raise ValueError("Memory and history limits must be non-negative")
        self.memory_limit = memory_limit
        self.history_limit = history_limit
        self.memory = list(memory or [])[-memory_limit:] if memory_limit else []
        self.history: List[str] = []
        self.api_key = _get_api_key()
        self.model = model or os.getenv("TOKENROUTER_MODEL", "openai/gpt-4.1")
        self.skill_usage: Dict[str, int] = {}
        self.skills = {
            "checklist": self.format_checklist,
            "chunks": self.chunk_text,
            "dedupe": self.deduplicate_lines,
            "emails": self.extract_emails,
            "filename": self.sanitize_filename,
            "find": self.find_keyword,
            "priority": self.score_priority,
            "recycle": self.recycle_usage,
            "summarize": self.summarize,
            "tasks": self.extract_tasks,
            "validate": self.validate_text,
            "check_goal": self.check_goal,
            "export_memory": self.export_memory,
            "flush_memory": self.flush_memory,
            "frequency": self.word_frequency,
            "groups": self.group_lines,
            "hash": self.hash_text,
            "kv": self.parse_key_values,
            "mentions": self.extract_mentions,
            "normalize": self.normalize_text,
            "outline": self.create_outline,
            "redact": self.redact_secrets,
            "sort_tasks": self.sort_tasks,
            "stats": self.text_stats,
            "status": self.checklist_status,
            "usage": self.usage_report,
            "urls": self.extract_urls,
        }
        self.skill_specs = {
            name: SkillSpec(
                name=name,
                mutates_state=name in {"flush_memory", "recycle"},
            )
            for name in self.skills
        }
        self.memory_namespaces: Dict[str, List[str]] = {"default": self.memory}

    def _append_bounded(self, entries: List[str], value: str, limit: int) -> None:
        """Append an entry while retaining only the configured recent window."""
        if not limit:
            return
        entries.append(value)
        del entries[:-limit]

    def _record(self, event: str) -> None:
        self._append_bounded(self.history, event, self.history_limit)

    def list_skills(self) -> List[str]:
        """Return the names of the skills available without network access."""
        return sorted(self.skills)

    def describe_skills(self) -> List[Dict[str, Any]]:
        """Return serializable contracts for local skill discovery."""
        return [
            {
                "name": spec.name,
                "mutates_state": spec.mutates_state,
                "network_required": spec.network_required,
            }
            for _, spec in sorted(self.skill_specs.items())
        ]

    def use_skill(self, skill: str, text: str) -> str:
        """Run a named local skill and record its result."""
        try:
            result = self.skills[skill](text)
        except KeyError as exc:
            available = ", ".join(self.list_skills())
            raise ValueError(f"Unknown skill '{skill}'. Available skills: {available}") from exc
        self.skill_usage[skill] = self.skill_usage.get(skill, 0) + 1
        self._record(f"Used skill: {skill}")
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
        removed_memory = sum(
            max(0, len(entries) - keep)
            for entries in self.memory_namespaces.values()
        )
        self.history = self.history[-keep:] if keep else []
        for namespace, entries in self.memory_namespaces.items():
            self.memory_namespaces[namespace] = entries[-keep:] if keep else []
        self.memory = self.memory_namespaces["default"]
        self.skill_usage.clear()
        return (
            f"Recycled usage: removed {removed_history} history entries and "
            f"{removed_memory} memory entries; retained {keep}."
        )

    def flush_memory(self, text: str = "") -> str:
        """Clear one memory namespace, or all namespaces when requested."""
        namespace = text.strip() or "default"
        if namespace == "all":
            removed = sum(len(entries) for entries in self.memory_namespaces.values())
            self.memory_namespaces = {"default": []}
            self.memory = self.memory_namespaces["default"]
        else:
            entries = self.memory_namespaces.setdefault(namespace, [])
            removed = len(entries)
            entries.clear()
            if namespace == "default":
                self.memory = entries
        if namespace == "default":
            return f"Flushed memory: removed {removed} entries."
        return f"Flushed memory: removed {removed} entries from {namespace}."

    def normalize_text(self, text: str) -> str:
        """Collapse whitespace into a portable single-line representation."""
        cleaned = " ".join(text.split())
        return f"Normalized: {cleaned}" if cleaned else "Normalized: empty."

    def create_outline(self, text: str) -> str:
        """Turn non-empty lines into a compact numbered outline."""
        items = [line.strip() for line in text.splitlines() if line.strip()]
        if not items:
            return "Outline: empty."
        return "Outline:\n" + "\n".join(
            f"{index}. {item}" for index, item in enumerate(items, start=1)
        )

    def redact_secrets(self, text: str) -> str:
        """Redact values assigned to common credential field names."""
        patterns = (
            r"(?i)(\b(?:api[_-]?key|token|secret|password)\b\s*[:=]\s*)[^\s,;]+",
            r"(?i)(\bauthorization\b\s*:\s*bearer\s+)[^\s,;]+",
        )
        redacted = text
        for pattern in patterns:
            redacted = re.sub(
                pattern,
                lambda match: match.group(1) + "<REDACTED>",
                redacted,
            )
        return "Redacted: no secrets found." if redacted == text else redacted

    def sort_tasks(self, text: str) -> str:
        """Sort task lines by urgency while preserving order within a tier."""
        tasks = []
        for line in text.splitlines():
            cleaned = line.strip()
            if cleaned.startswith(("- [ ]", "- ", "TODO:", "Task:")):
                task = cleaned.replace("- [ ]", "", 1).replace("- ", "", 1).strip()
                task = task.removeprefix("TODO:").removeprefix("Task:").strip()
                if task:
                    priority = self.score_priority(task)
                    rank = {"Priority: high.": 0, "Priority: medium.": 1}.get(priority, 2)
                    tasks.append((rank, len(tasks), task))
        if not tasks:
            return "Sorted tasks: none found."
        ordered = sorted(tasks, key=lambda item: (item[0], item[1]))
        return "Sorted tasks:\n" + "\n".join(f"- {item[2]}" for item in ordered)

    def text_stats(self, text: str) -> str:
        """Report line, word, and character counts for text."""
        return (
            f"Stats: lines={len(text.splitlines())}, words={len(text.split())}, "
            f"characters={len(text)}."
        )

    def extract_urls(self, text: str) -> str:
        """Extract unique HTTP(S) URLs in first-seen order."""
        urls = []
        for match in re.findall(r"https?://[^\s<>]+", text):
            url = match.rstrip(".,;:!?)]}")
            if url and url not in urls:
                urls.append(url)
        return "URLs: none found." if not urls else "URLs:\n" + "\n".join(f"- {url}" for url in urls)

    def chunk_text(self, text: str) -> str:
        """Split text into fixed-size chunks; the first line supplies the size."""
        lines = text.splitlines()
        try:
            size = int(lines[0].strip()) if lines else 0
        except ValueError as exc:
            raise ValueError("Chunk size must be a positive integer on the first line") from exc
        content = "\n".join(lines[1:])
        if size <= 0:
            raise ValueError("Chunk size must be a positive integer on the first line")
        chunks = [content[index:index + size] for index in range(0, len(content), size)]
        return "Chunks: none." if not chunks else "Chunks:\n" + "\n".join(
            f"{index}. {chunk}" for index, chunk in enumerate(chunks, start=1)
        )

    def extract_emails(self, text: str) -> str:
        """Extract unique email-like addresses in first-seen order."""
        emails = []
        seen = set()
        for email in re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text):
            if email.casefold() not in seen:
                seen.add(email.casefold())
                emails.append(email)
        return "Emails: none found." if not emails else "Emails:\n" + "\n".join(f"- {email}" for email in emails)

    def sanitize_filename(self, text: str) -> str:
        """Create a portable filename from arbitrary text."""
        filename = re.sub(r"[^A-Za-z0-9._-]+", "_", text.strip()).strip("._")
        return f"Filename: {filename or 'untitled'}"

    def word_frequency(self, text: str) -> str:
        """Count words case-insensitively, ordered by count then alphabetically."""
        words = re.findall(r"[A-Za-z0-9']+", text.casefold())
        if not words:
            return "Frequency: none."
        counts = Counter(words)
        ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return "Frequency:\n" + "\n".join(f"- {word}: {count}" for word, count in ordered)

    def group_lines(self, text: str) -> str:
        """Group non-empty lines by their first whitespace-delimited word."""
        groups: Dict[str, List[str]] = {}
        for line in text.splitlines():
            cleaned = line.strip()
            if cleaned:
                key = cleaned.split()[0].casefold()
                groups.setdefault(key, []).append(cleaned)
        if not groups:
            return "Groups: empty."
        return "Groups:\n" + "\n".join(
            f"{key}: " + " | ".join(groups[key]) for key in sorted(groups)
        )

    def hash_text(self, text: str) -> str:
        """Return a stable SHA-256 digest without storing the input."""
        digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"SHA-256: {digest}"

    def parse_key_values(self, text: str) -> str:
        """Parse non-empty ``key=value`` lines into sorted portable output."""
        values: Dict[str, str] = {}
        for line in text.splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            if key:
                values[key] = value.strip()
        if not values:
            return "Key values: none found."
        return "Key values:\n" + "\n".join(
            f"- {key}: {values[key]}" for key in sorted(values)
        )

    def extract_mentions(self, text: str) -> str:
        """Extract unique @mentions in first-seen order."""
        mentions = []
        seen = set()
        for mention in re.findall(r"@[A-Za-z0-9_]+", text):
            if mention.casefold() not in seen:
                seen.add(mention.casefold())
                mentions.append(mention)
        return "Mentions: none found." if not mentions else "Mentions:\n" + "\n".join(f"- {mention}" for mention in mentions)

    def checklist_status(self, text: str) -> str:
        """Count checked and unchecked Markdown checklist entries."""
        checked = sum(1 for line in text.splitlines() if line.strip().startswith("- [x]"))
        unchecked = sum(1 for line in text.splitlines() if line.strip().startswith("- [ ]"))
        return f"Checklist status: checked={checked}, unchecked={unchecked}."

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

    def export_memory(self, text: str = "") -> str:
        """Return the current memory as a portable plain-text block."""
        namespace = text.strip() or "default"
        entries = self.memory_namespaces.get(namespace, [])
        if not entries:
            return "Memory: empty."
        if namespace == "default":
            return "Memory:\n" + "\n".join(f"- {item}" for item in entries)
        return f"Memory ({namespace}):\n" + "\n".join(f"- {item}" for item in entries)

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
        return TokenRouterClient(self.api_key, model=self.model).complete(prompt)

    def remember(self, item: str, namespace: str = "default") -> None:
        if not namespace.strip():
            raise ValueError("Memory namespace is required")
        entries = self.memory_namespaces.setdefault(namespace, [])
        self._append_bounded(entries, item, self.memory_limit)
        if namespace == "default":
            self.memory = entries
        self._record(f"Remembered: {item}")

    def observe(self, observation: str) -> None:
        self._record(f"Observed: {observation}")
        self.remember(observation)

    def plan(self, goal: str) -> List[str]:
        plan = [
            f"Define goal: {goal}",
            "Gather context",
            "Select next action",
            "Execute action",
            "Review results",
        ]
        self._record(f"Planned: {goal}")
        return plan

    def act(self, action: str) -> str:
        result = f"{self.name} executes '{action}'."
        self._record(result)
        return result

    def run(self, goal: str) -> Dict[str, Any]:
        self.observe(f"Starting goal: {goal}")
        plan = self.plan(goal)
        results = [self.act(action) for action in plan]
        self._record(f"Completed goal: {goal}")
        return {
            "goal": goal,
            "plan": plan,
            "results": results,
            "history": self.history,
            "api_key_configured": bool(self.api_key),
        }
