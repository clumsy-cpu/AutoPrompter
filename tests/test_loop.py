"""
End-to-end tests of PromptOptimizationSystem.run() with fake LLMs. No real LLM is called.
"""

import json
import os
import sys

import pytest

pytest.importorskip("scipy")  # optimization_system imports scipy at module level
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fakes import make_system, scripted_optimizer, target_parts
from config_manager import Config, LocalLLMConfig, LLMConfig

TRAIN = [("q1", "a1"), ("q2", "a2"), ("q3", "a3"), ("q4", "a4")]


def knows(answers_by_prompt):
    """Target that answers correctly the inputs listed for its prompt, 'x' otherwise."""
    def respond(full_prompt, system_message):
        prompt, inp = target_parts(full_prompt)
        return dict(TRAIN)[inp] if inp in answers_by_prompt.get(prompt, ()) else "x"
    return respond


def test_first_iteration_tests_a_new_prompt_and_report_uses_this_runs_baseline(tmp_path):
    target = knows({"P0": {"q1"}, "P1": {"q1", "q2"}, "P2": {"q1", "q2", "q3"}, "P3": set()})
    system, opt, tgt = make_system(tmp_path, scripted_optimizer(["P1", "P2", "P3"]), target, TRAIN)
    report = system.run()
    tested = [target_parts(p)[0] for p, _ in tgt.calls[::len(TRAIN)]]
    assert tested == ["P0", "P1", "P2", "P3"]  # baseline, then 3 new prompts (none wasted)
    assert report["initial_score"] == 0.25
    assert report["final_score"] == 0.75 and report["best_prompt"] == "P2"
    assert report["experiments_count"] == 4


def test_second_run_reports_its_own_baseline_not_the_ledgers_first_record(tmp_path):
    make_system(tmp_path, scripted_optimizer(["P1"]), knows({"P0": {"q1"}}), TRAIN,
                experiment={"max_iterations": 1})[0].run()
    system = make_system(tmp_path, scripted_optimizer(["P9"]), knows({"P0": {"q1"}, "P9": {"q1", "q2"}}),
                         TRAIN, experiment={"max_iterations": 1}, task={"initial_prompt": "P9"})[0]
    assert system.run()["initial_score"] == 0.5


def test_ledger_is_written_on_a_short_run(tmp_path):
    system = make_system(tmp_path, scripted_optimizer(["P1", "P2"]), knows({}), TRAIN,
                         experiment={"max_iterations": 2})[0]
    system.run()
    records = json.load(open(tmp_path / "ledger.json"))["records"]
    assert [r["prompt"] for r in records] == ["P0", "P1", "P2"]


def test_repeated_prompt_is_skipped_without_target_calls(tmp_path):
    system, opt, tgt = make_system(tmp_path, scripted_optimizer(["P0", "P0", "P1"]), knows({}), TRAIN,
                                   experiment={"max_iterations": 2})
    system.run()
    tested = [target_parts(p)[0] for p, _ in tgt.calls[::len(TRAIN)]]
    assert tested == ["P0", "P1"]  # iteration 1 asked twice, got P0 twice, skipped


def test_to_yaml_round_trips_local_and_openrouter_blocks(tmp_path, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    src = tmp_path / "c.yaml"
    src.write_text("optimizer_llm: {model: m}\n"
                   "target_llm: {backend: ollama, model: qwen}\n")
    out = tmp_path / "out.yaml"
    Config.from_yaml(str(src)).to_yaml(str(out))
    loaded = Config.from_yaml(str(out))
    assert isinstance(loaded.target_llm, LocalLLMConfig)
    assert isinstance(loaded.optimizer_llm, LLMConfig)
