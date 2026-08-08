import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib import error, request

from agent import Agent, _get_api_key, _load_env_file
from tokenrouter_client import TokenRouterClient, TokenRouterClientError


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(
            {"choices": [{"message": {"content": "TokenRouter response"}}]}
        ).encode("utf-8")


class InvalidJsonResponse(FakeResponse):
    def read(self):
        return b"not-json"


class MissingContentResponse(FakeResponse):
    def read(self):
        return json.dumps({"choices": []}).encode("utf-8")


class AgentTests(unittest.TestCase):
    def test_env_file_does_not_override_shell_values(self):
        with tempfile.TemporaryDirectory() as directory:
            env_path = Path(directory) / ".env"
            env_path.write_text("TOKENROUTER_API_KEY=file-key\nNEW_VALUE=from-file\n")
            with patch.dict(
                os.environ, {"TOKENROUTER_API_KEY": "shell-key"}, clear=False
            ):
                _load_env_file(env_path)
                self.assertEqual(os.environ["TOKENROUTER_API_KEY"], "shell-key")
                self.assertEqual(os.environ["NEW_VALUE"], "from-file")

    def test_missing_key_is_reported(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(_get_api_key())
            with self.assertRaisesRegex(RuntimeError, "TOKENROUTER_API_KEY"):
                Agent().ask("hello")

    @patch.object(request, "urlopen", return_value=FakeResponse())
    def test_tokenrouter_client_returns_message_content(self, urlopen):
        result = TokenRouterClient("test-key").complete("hello")
        self.assertEqual(result, "TokenRouter response")
        sent_request = urlopen.call_args.args[0]
        self.assertEqual(sent_request.get_header("Authorization"), "Bearer test-key")
        payload = json.loads(sent_request.data)
        self.assertEqual(payload["model"], "openai/gpt-4.1")
        self.assertEqual(payload["messages"][1]["content"], "hello")

    @patch.object(request, "urlopen", return_value=FakeResponse())
    def test_agent_uses_explicit_model(self, urlopen):
        with patch.dict(os.environ, {"TOKENROUTER_API_KEY": "test-key"}, clear=True):
            Agent(model="anthropic/claude-sonnet-4").ask("hello")

        payload = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(payload["model"], "anthropic/claude-sonnet-4")

    @patch.object(request, "urlopen", return_value=InvalidJsonResponse())
    def test_tokenrouter_client_rejects_invalid_json(self, urlopen):
        with self.assertRaisesRegex(TokenRouterClientError, "invalid JSON"):
            TokenRouterClient("test-key").complete("hello")

    @patch.object(request, "urlopen", return_value=MissingContentResponse())
    def test_tokenrouter_client_rejects_missing_message_content(self, urlopen):
        with self.assertRaisesRegex(TokenRouterClientError, "message content"):
            TokenRouterClient("test-key").complete("hello")

    def test_agent_run_builds_plan_and_history(self):
        output = Agent(name="test").run("goal")
        self.assertEqual(output["goal"], "goal")
        self.assertEqual(len(output["plan"]), 5)
        self.assertTrue(output["history"])

    def test_local_skills_are_discoverable_and_callable(self):
        agent = Agent(name="test")
        self.assertEqual(
            agent.list_skills(),
            [
                "check_goal",
                "checklist",
                "chunks",
                "dedupe",
                "emails",
                "export_memory",
                "filename",
                "find",
                "flush_memory",
                "frequency",
                "groups",
                "hash",
                "kv",
                "mentions",
                "normalize",
                "outline",
                "priority",
                "recycle",
                "redact",
                "sort_tasks",
                "stats",
                "status",
                "summarize",
                "tasks",
                "urls",
                "usage",
                "validate",
            ],
        )
        self.assertEqual(
            agent.use_skill("summarize", "Inspect the API. Then run tests."),
            "Summary: Inspect the API.",
        )
        self.assertIn("Used skill: summarize", agent.history)

    def test_skill_contracts_are_discoverable(self):
        contracts = Agent().describe_skills()
        self.assertEqual(contracts[0]["name"], "check_goal")
        self.assertTrue(any(contract["name"] == "flush_memory" and contract["mutates_state"] for contract in contracts))
        self.assertTrue(all(not contract["network_required"] for contract in contracts))

    def test_tasks_skill_extracts_task_markers(self):
        result = Agent().use_skill("tasks", "- [ ] Add tests\nTODO: update docs")
        self.assertEqual(result, "Tasks:\n- Add tests\n- update docs")

    def test_unknown_skill_lists_available_skills(self):
        with self.assertRaisesRegex(ValueError, "Available skills"):
            Agent().use_skill("missing", "text")

    def test_usage_skill_reports_and_recycles_agent_state(self):
        agent = Agent()
        agent.remember("old context")
        agent.remember("keep context")
        agent.use_skill("summarize", "One sentence.")
        self.assertIn("summarize=1", agent.use_skill("usage", ""))

        result = agent.use_skill("recycle", "1")
        self.assertIn("retained 1", result)
        self.assertEqual(agent.memory, ["keep context"])
        self.assertEqual(agent.skill_usage, {"recycle": 1})

    def test_recycle_requires_a_non_negative_integer(self):
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            Agent().use_skill("recycle", "many")

    def test_memory_is_bounded_and_can_be_flushed(self):
        agent = Agent(memory_limit=2, history_limit=2)
        agent.remember("first")
        agent.remember("second")
        agent.remember("third")

        self.assertEqual(agent.memory, ["second", "third"])
        self.assertEqual(agent.use_skill("flush_memory", ""),
                         "Flushed memory: removed 2 entries.")
        self.assertEqual(agent.memory, [])

    def test_invalid_state_limits_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "limits"):
            Agent(memory_limit=-1)

    def test_priority_and_validation_skills(self):
        agent = Agent()
        self.assertEqual(
            agent.use_skill("priority", "Critical production issue"),
            "Priority: high.",
        )
        self.assertEqual(
            agent.use_skill("validate", "This has enough words"),
            "Validation: valid.",
        )

    def test_dedupe_and_checklist_skills(self):
        agent = Agent()
        self.assertEqual(
            agent.use_skill("dedupe", "one\none\ntwo\n\ntwo"),
            "one\ntwo",
        )
        self.assertEqual(
            agent.use_skill("checklist", "First\nSecond"),
            "Checklist:\n- [ ] First\n- [ ] Second",
        )

    def test_find_and_export_memory_skills(self):
        agent = Agent(memory=["API context", "test context"])
        self.assertEqual(
            agent.use_skill("find", "api\nReview the API context"),
            "Find: 'api' found.",
        )
        self.assertEqual(
            agent.use_skill("export_memory", ""),
            "Memory:\n- API context\n- test context",
        )

    def test_memory_namespaces_are_isolated_and_flushable(self):
        agent = Agent()
        agent.remember("project context", namespace="project")
        agent.remember("runtime context", namespace="runtime")
        self.assertEqual(agent.use_skill("export_memory", "project"), "Memory (project):\n- project context")
        self.assertEqual(agent.use_skill("flush_memory", "project"), "Flushed memory: removed 1 entries from project.")
        self.assertEqual(agent.use_skill("export_memory", "runtime"), "Memory (runtime):\n- runtime context")

    def test_text_automation_skills(self):
        agent = Agent()
        self.assertEqual(
            agent.use_skill("normalize", "  one\n two  "),
            "Normalized: one two",
        )
        self.assertEqual(
            agent.use_skill("outline", "First\n\nSecond"),
            "Outline:\n1. First\n2. Second",
        )
        self.assertEqual(
            agent.use_skill("stats", "one two\nthree"),
            "Stats: lines=2, words=3, characters=13.",
        )

    def test_security_and_routing_automation_skills(self):
        agent = Agent()
        self.assertEqual(
            agent.use_skill("redact", "API_KEY=abc123 password: secret"),
            "API_KEY=<REDACTED> password: <REDACTED>",
        )
        self.assertEqual(
            agent.use_skill("urls", "See https://example.com/a. https://example.com/a"),
            "URLs:\n- https://example.com/a",
        )
        self.assertEqual(
            agent.use_skill("sort_tasks", "- normal task\nTODO: urgent production fix"),
            "Sorted tasks:\n- urgent production fix\n- normal task",
        )

    def test_additional_data_automation_skills(self):
        agent = Agent()
        self.assertEqual(agent.use_skill("chunks", "3\nabcdef"), "Chunks:\n1. abc\n2. def")
        self.assertEqual(
            agent.use_skill("emails", "A@EXAMPLE.com a@example.com"),
            "Emails:\n- A@EXAMPLE.com",
        )
        self.assertEqual(agent.use_skill("filename", " report / final "), "Filename: report_final")
        self.assertEqual(
            agent.use_skill("frequency", "One one two"),
            "Frequency:\n- one: 2\n- two: 1",
        )
        self.assertEqual(
            agent.use_skill("groups", "API one\nDB two\napi three"),
            "Groups:\napi: API one | api three\ndb: DB two",
        )
        self.assertTrue(agent.use_skill("hash", "hello").startswith("SHA-256: "))

    def test_key_value_mention_and_checklist_automation_skills(self):
        agent = Agent()
        self.assertEqual(
            agent.use_skill("kv", "z=last\na=first"),
            "Key values:\n- a: first\n- z: last",
        )
        self.assertEqual(
            agent.use_skill("mentions", "@Alice and @alice with @bob"),
            "Mentions:\n- @Alice\n- @bob",
        )
        self.assertEqual(
            agent.use_skill("status", "- [x] Done\n- [ ] Next"),
            "Checklist status: checked=1, unchecked=1.",
        )