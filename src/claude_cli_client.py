"""
Claude Code CLI backend.
Runs `claude -p` headless so the Optimizer or Target LLM can use the logged-in
Claude Code session (no API key). Exposes the same query() interface as LLMClient.
"""

import json
import logging
import shutil
import subprocess
import time
from typing import Optional

from llm_client import LLMResponse

logger = logging.getLogger(__name__)

DEFAULT_SYSTEM_MESSAGE = "You are a helpful assistant."


class ClaudeCLIClient:
    """Sends each prompt to `claude -p` and parses its JSON result."""

    def __init__(self, config):
        self.config = config
        self.model = config.model
        self.timeout = config.timeout
        self.min_request_interval = config.min_request_interval
        self.last_request_time = 0.0
        if shutil.which(config.command) is None:
            raise RuntimeError(
                f"'{config.command}' not found on PATH. Install Claude Code or set 'command' in the config."
            )

    def _rate_limit(self):
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_request_interval:
            time.sleep(self.min_request_interval - elapsed)
        self.last_request_time = time.time()

    def _command(self, system_message: Optional[str]) -> list:
        # --safe-mode drops CLAUDE.md, hooks, skills and MCP but keeps the Claude Code login
        # (--bare would need an API key). --tools "" makes the model answer only, never act.
        return [
            self.config.command, "-p", "--safe-mode", "--tools", "",
            "--no-session-persistence", "--output-format", "json",
            "--system-prompt", system_message or DEFAULT_SYSTEM_MESSAGE,
            "--model", self.model,
        ]

    @staticmethod
    def _parse_result(stdout: str) -> dict:
        data = json.loads(stdout)
        if isinstance(data, list):  # newer CLI versions print the event stream as an array
            data = next((e for e in reversed(data) if isinstance(e, dict) and e.get("type") == "result"), None)
        if not isinstance(data, dict):
            raise ValueError("no result object in claude output")
        return data

    def _make_request(self, prompt: str, system_message: Optional[str],
                      max_retries: int = 3) -> LLMResponse:
        start_time = time.time()
        last_error = "unknown error"
        for attempt in range(max_retries):
            self._rate_limit()
            try:
                proc = subprocess.run(
                    self._command(system_message), input=prompt,
                    capture_output=True, text=True, timeout=self.timeout,
                )
                if proc.returncode != 0:
                    raise RuntimeError(f"claude exited {proc.returncode}: {proc.stderr.strip()[-300:]}")
                data = self._parse_result(proc.stdout)
                if data.get("is_error"):
                    raise RuntimeError(data.get("result") or "claude reported an error")
                usage = data.get("usage") or {}
                prompt_tokens = (usage.get("input_tokens", 0) + usage.get("cache_read_input_tokens", 0)
                                 + usage.get("cache_creation_input_tokens", 0))
                completion_tokens = usage.get("output_tokens", 0)
                return LLMResponse(
                    content=data.get("result", ""),
                    model=next(iter(data.get("modelUsage") or {}), self.model),
                    usage={"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens,
                           "total_tokens": prompt_tokens + completion_tokens},
                    latency_ms=(time.time() - start_time) * 1000,
                    success=True,
                )
            except (subprocess.TimeoutExpired, RuntimeError, ValueError) as e:
                last_error = f"{type(e).__name__}: {e}"
                logger.warning(f"claude CLI attempt {attempt + 1}/{max_retries} failed: {last_error}")
                if attempt < max_retries - 1:
                    time.sleep(2 * (attempt + 1))
        return LLMResponse(content="", model=self.model, usage={},
                           latency_ms=(time.time() - start_time) * 1000,
                           success=False, error=last_error)

    def query(self, prompt: str, system_message: Optional[str] = None) -> LLMResponse:
        """Send a single prompt to Claude through the CLI."""
        return self._make_request(prompt, system_message)
