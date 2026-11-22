"""Exercise environment checks without provider requests."""

import importlib.util
import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
HELPERS = [
    path
    for path in (
        ROOT / "env_utils/env_utils.py",
        ROOT / "python/env_utils.py",
        ROOT / "python_local/env_utils.py",
    )
    if path.exists()
]
EXAMPLE = """# Chat providers: OPENAI_API_KEY
OPENAI_API_KEY='your_openai_api_key_here'
ANTHROPIC_API_KEY=your_anthropic_api_key_here
# Required for search tools
TAVILY_API_KEY='your_tavily_api_key_here'
# Optional tracing
LANGSMITH_API_KEY=your_langsmith_api_key_here
LANGSMITH_TRACING=false
LANGSMITH_GATEWAY=false
"""


class EnvironmentTests(unittest.TestCase):
    def check_output(self, env, **kwargs):
        outputs = []
        for path in HELPERS:
            spec = importlib.util.spec_from_file_location("env_utils", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            with tempfile.TemporaryDirectory() as directory:
                example = Path(directory) / "example.env"
                example.write_text(EXAMPLE)
                output = io.StringIO()
                with patch.dict(os.environ, env, clear=True), redirect_stdout(output):
                    module.doublecheck_env(str(example), **kwargs)
                outputs.append(output.getvalue())
        self.assertTrue(outputs)
        self.assertTrue(all(output == outputs[0] for output in outputs))
        return outputs[0]

    def test_direct_modes_require_selected_provider_only(self):
        for flag in ("", "false", "FALSE", "0", "no"):
            with self.subTest(flag=flag):
                output = self.check_output(
                    {"LANGSMITH_GATEWAY": flag, "TAVILY_API_KEY": "search-secret"}
                )
                self.assertIn("OPENAI_API_KEY is required", output)
                self.assertNotIn("ANTHROPIC_API_KEY is required", output)
                self.assertNotIn("LANGSMITH_API_KEY is required", output)

    def test_gateway_modes_do_not_require_local_chat_keys(self):
        for flag in (
            "true",
            "TRUE",
            "1",
            "yes",
            "https://eu.gateway.smith.langchain.com",
        ):
            with self.subTest(flag=flag):
                output = self.check_output(
                    {
                        "LANGSMITH_GATEWAY": flag,
                        "LANGSMITH_API_KEY": "gateway-secret",
                        "TAVILY_API_KEY": "search-secret",
                    }
                )
                self.assertIn("LangSmith Gateway enabled", output)
                self.assertNotIn("Issues found", output)
                self.assertNotIn("gateway-secret", output)

    def test_gateway_credential_validation_and_precedence(self):
        for value in (
            None,
            "",
            "   ",
            "your_langsmith_api_key_here",
            "<key>",
            "changeme",
        ):
            env = {"LANGSMITH_GATEWAY": "true", "TAVILY_API_KEY": "search-secret"}
            if value is not None:
                env["LANGSMITH_API_KEY"] = value
            self.assertIn(
                "LANGSMITH_API_KEY", self.check_output(env).split("Issues found:")[1]
            )
        output = self.check_output(
            {
                "LANGSMITH_GATEWAY": "true",
                "LANGSMITH_API_KEY": "valid-secret",
                "LANGSMITH_GATEWAY_API_KEY": "your_override",
                "TAVILY_API_KEY": "search-secret",
            }
        )
        self.assertIn("LANGSMITH_GATEWAY_API_KEY still has", output)

    def test_tools_and_explicit_direct_keys_are_not_exempt(self):
        env = {
            "LANGSMITH_GATEWAY": "true",
            "LANGSMITH_GATEWAY_API_KEY": "gateway-secret",
        }
        output = self.check_output(env, direct_api_keys=("OPENAI_API_KEY",))
        self.assertIn("OPENAI_API_KEY is required", output)
        self.assertIn("TAVILY_API_KEY is required", output)
        self.assertNotIn("LANGSMITH_API_KEY is required", output)

    def test_quoted_example_and_empty_provider_keys(self):
        for value in ("", " ", "your_openai_api_key_here"):
            output = self.check_output(
                {"OPENAI_API_KEY": value, "TAVILY_API_KEY": "search-secret"}
            )
            self.assertIn("Issues found", output)

    def test_other_providers_and_base_overrides_stay_direct(self):
        env = {
            "LANGSMITH_GATEWAY": "true",
            "LANGSMITH_API_KEY": "gateway-secret",
            "TAVILY_API_KEY": "search-secret",
            "OPENAI_API_BASE": "https://other.example/v1",
        }
        self.assertIn("OPENAI_API_KEY is required", self.check_output(env))
        self.assertIn(
            "OTHER_API_KEY is required",
            self.check_output(env, chat_provider_keys=("OTHER_API_KEY",)),
        )

    def test_no_chat_provider_keeps_local_models_local(self):
        output = self.check_output(
            {"TAVILY_API_KEY": "search-secret"}, chat_provider_keys=()
        )
        self.assertNotIn("Issues found", output)

    def test_loaded_dotenv_and_shell_precedence(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            patch.dict(os.environ, {"LANGSMITH_GATEWAY": "false"}, clear=True),
        ):
            env_file = Path(directory) / ".env"
            env_file.write_text(
                "LANGSMITH_GATEWAY=true\nOPENAI_API_KEY=direct-secret\nTAVILY_API_KEY=search-secret\n"
            )
            load_dotenv(env_file)
            output = self.check_output(dict(os.environ))
            self.assertNotIn("LangSmith Gateway enabled", output)
            self.assertNotIn("Issues found", output)

    def test_tracing_credentials_are_independent(self):
        env = {
            "LANGSMITH_GATEWAY": "true",
            "LANGSMITH_GATEWAY_API_KEY": "gateway-secret",
            "TAVILY_API_KEY": "search-secret",
        }
        for flag in (
            "LANGSMITH_TRACING",
            "LANGSMITH_TRACING_V2",
            "LANGCHAIN_TRACING_V2",
        ):
            output = self.check_output({**env, flag: "true"})
            self.assertIn("LANGSMITH_API_KEY is required", output)
            self.assertNotIn("Issues found", self.check_output({**env, flag: "false"}))
        self.assertNotIn(
            "Issues found",
            self.check_output(
                {
                    **env,
                    "LANGSMITH_TRACING": "true",
                    "LANGCHAIN_API_KEY": "tracing-secret",
                }
            ),
        )

    def test_gateway_override_placeholders_without_example_entry(self):
        for key in ("your-key", "****", "lsv2_..."):
            output = self.check_output(
                {
                    "LANGSMITH_GATEWAY": "true",
                    "LANGSMITH_GATEWAY_API_KEY": key,
                    "TAVILY_API_KEY": "search-secret",
                }
            )
            self.assertIn("LANGSMITH_GATEWAY_API_KEY still has", output)


if __name__ == "__main__":
    unittest.main()
