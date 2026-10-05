"""
Tests for the Claude Code CLI backend. `claude` is never called: subprocess.run is mocked.
"""

import json
import os
import subprocess
import sys
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from claude_cli_client import ClaudeCLIClient
from config_manager import Config, ClaudeCLIConfig, LLMConfig, LocalLLMConfig

RESULT = {"type": "result", "is_error": False, "result": "OK",
          "usage": {"input_tokens": 600, "cache_read_input_tokens": 2, "output_tokens": 4},
          "modelUsage": {"claude-haiku-4-5-20251001": {}}}


def proc(stdout="", returncode=0, stderr=""):
    return Mock(stdout=stdout, returncode=returncode, stderr=stderr)


def make_client():
    with patch("claude_cli_client.shutil.which", return_value="/bin/claude"):
        return ClaudeCLIClient(ClaudeCLIConfig(model="haiku"))


@patch("claude_cli_client.subprocess.run")
def test_success_parses_event_array_and_object(run):
    client = make_client()
    events = [{"type": "system"}, {"type": "assistant"}, RESULT]
    run.return_value = proc(json.dumps(events))
    resp = client.query("hi", system_message="be brief")
    assert (resp.success, resp.content, resp.model) == (True, "OK", "claude-haiku-4-5-20251001")
    assert resp.usage == {"prompt_tokens": 602, "completion_tokens": 4, "total_tokens": 606}
    cmd = run.call_args.args[0]
    assert run.call_args.kwargs["input"] == "hi"  # prompt goes on stdin
    assert cmd[cmd.index("--system-prompt") + 1] == "be brief"
    assert cmd[cmd.index("--model") + 1] == "haiku"
    assert "--safe-mode" in cmd and cmd[cmd.index("--tools") + 1] == ""

    run.return_value = proc(json.dumps(RESULT))  # single-object output
    assert client.query("hi").content == "OK"
    assert run.call_args.args[0][run.call_args.args[0].index("--system-prompt") + 1] == "You are a helpful assistant."


@patch("claude_cli_client.time.sleep")
@patch("claude_cli_client.subprocess.run")
def test_failures_retry_then_recover_or_give_up(run, _sleep):
    client = make_client()
    run.side_effect = [proc(returncode=1, stderr="boom"), proc(json.dumps(RESULT))]
    assert client.query("hi").success is True and run.call_count == 2  # recovers on retry

    run.reset_mock()
    run.side_effect = None
    run.return_value = proc(json.dumps({**RESULT, "is_error": True, "result": "rate limited"}))
    resp = client.query("hi")
    assert resp.success is False and "rate limited" in resp.error and run.call_count == 3

    run.reset_mock()
    run.side_effect = subprocess.TimeoutExpired(cmd="claude", timeout=1)
    assert "TimeoutExpired" in client.query("hi").error

    run.reset_mock()
    run.side_effect = None
    run.return_value = proc("not json")
    assert client.query("hi").success is False


def test_missing_binary_raises():
    with patch("claude_cli_client.shutil.which", return_value=None):
        with pytest.raises(RuntimeError, match="not found on PATH"):
            ClaudeCLIClient(ClaudeCLIConfig())


def test_config_routes_by_backend_and_round_trips(tmp_path):
    cfg_file = tmp_path / "c.yaml"
    cfg_file.write_text(
        "optimizer_llm: {backend: claude_cli, model: sonnet}\n"
        "target_llm: {model: x, api_key: k}\n")
    cfg = Config.from_yaml(str(cfg_file))
    assert isinstance(cfg.optimizer_llm, ClaudeCLIConfig) and isinstance(cfg.target_llm, LLMConfig)

    cfg_file.write_text("optimizer_llm: {backend: ollama, model: m}\ntarget_llm: {backend: claude_cli, model: haiku}\n")
    cfg = Config.from_yaml(str(cfg_file))
    assert isinstance(cfg.optimizer_llm, LocalLLMConfig) and isinstance(cfg.target_llm, ClaudeCLIConfig)

    cfg_file.write_text("optimizer_llm: {backend: claude_cli, model: sonnet}\ntarget_llm: {backend: claude_cli, model: haiku}\n")
    cfg = Config.from_yaml(str(cfg_file))
    out = tmp_path / "saved.yaml"
    cfg.to_yaml(str(out))  # writes api_key: null into each block; must load back
    reloaded = Config.from_yaml(str(out))
    assert isinstance(reloaded.optimizer_llm, ClaudeCLIConfig) and reloaded.target_llm.model == "haiku"
    assert cfg.validate() == []
