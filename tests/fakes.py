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


def target_parts(full_prompt):
    """Split a target call 'PROMPT\\n\\nInput: X\\n\\nOutput:' into (prompt, input)."""
    head, _, tail = full_prompt.rpartition("\n\nInput: ")
    return head, tail[: -len("\n\nOutput:")] if tail.endswith("\n\nOutput:") else tail


def scripted_optimizer(prompts):
    """Optimizer that returns the given prompts in order, then repeats the last one."""
    queue = list(prompts)

    def respond(prompt, system_message):
        return queue.pop(0) if len(queue) > 1 else queue[0]
    return respond


def write_json(path, entries):
    import json
    path.write_text(json.dumps([{"input": i, "expected_output": o} for i, o in entries]))
    return str(path)


def make_system(tmp_path, optimizer, target, train, experiment=None, task=None,
                metric="exact_match", storage=None):
    """Build a real PromptOptimizationSystem whose two LLMs are FakeLLMs.

    optimizer/target are responder functions; train is a list of (input, expected) pairs.
    Returns (system, optimizer_fake, target_fake).
    """
    from unittest.mock import patch
    from config_manager import (Config, ClaudeCLIConfig, ExperimentConfig, TaskConfig,
                                MetricConfig, ContextConfig, StorageConfig)
    import optimization_system

    exp = dict(max_iterations=3, batch_size=len(train), reuse_dataset=True)
    exp.update(experiment or {})
    tsk = dict(name="t", description="answer", initial_prompt="P0")
    tsk.update(task or {})
    sto = dict(ledger_file=str(tmp_path / "ledger.json"),
               dataset_file=write_json(tmp_path / "train.json", train),
               results_dir=str(tmp_path / "results"))
    sto.update(storage or {})
    config = Config(
        optimizer_llm=ClaudeCLIConfig(model="opus"),
        target_llm=ClaudeCLIConfig(model="haiku"),
        experiment=ExperimentConfig(**exp),
        task=TaskConfig(**tsk),
        metric=MetricConfig(type=metric),
        context=ContextConfig(),
        storage=StorageConfig(**sto),
    )
    opt, tgt = FakeLLM(optimizer), FakeLLM(target)
    clients = iter([opt, tgt])
    with patch.object(optimization_system, "create_llm_client", lambda cfg: next(clients)):
        system = optimization_system.PromptOptimizationSystem(config)
    return system, opt, tgt
