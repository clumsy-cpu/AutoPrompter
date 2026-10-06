"""
Test doubles shared by the loop tests. No real LLM is called.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from llm_client import LLMResponse


class FakeLLM:
    """Answers each query with responder(prompt, system_message) and records every call.

    responder returns a string (success) or None (failed call).
    """

    def __init__(self, responder):
        self.responder = responder
        self.calls = []

    def query(self, prompt, system_message=None):
        self.calls.append((prompt, system_message))
        content = self.responder(prompt, system_message)
        if content is None:
            return LLMResponse(content="", model="fake", usage={}, latency_ms=0.0,
                               success=False, error="fake failure")
        return LLMResponse(content=content, model="fake", usage={}, latency_ms=0.0, success=True)
