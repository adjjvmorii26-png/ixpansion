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
        self.assertEqual(payload["model"], "moonshotai/kimi-k3-free")
        self.assertEqual(payload["messages"][1]["content"], "hello")

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
                "dedupe",
                "export_memory",
                "find",
                "priority",
                "recycle",
                "summarize",
                "tasks",
                "usage",
                "validate",
            ],
        )
        self.assertEqual(
            agent.use_skill("summarize", "Inspect the API. Then run tests."),
            "Summary: Inspect the API.",
        )
        self.assertIn("Used skill: summarize", agent.history)

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