import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib import request

from agent import Agent, _get_api_key, _load_env_file
from tokenrouter_client import TokenRouterClient


class FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(
            {"choices": [{"message": {"content": "TokenRouter response"}}]}
        ).encode("utf-8")


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

    def test_agent_run_builds_plan_and_history(self):
        output = Agent(name="test").run("goal")
        self.assertEqual(output["goal"], "goal")
        self.assertEqual(len(output["plan"]), 5)
        self.assertTrue(output["history"])