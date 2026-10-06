"""
End-to-end tests of PromptOptimizationSystem.run() with fake LLMs. No real LLM is called.
"""

import json
import os
import sys

import pytest

pytest.importorskip("scipy")  # optimization_system imports scipy at module level
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fakes import make_system, scripted_optimizer, target_parts, write_json
from config_manager import Config, LocalLLMConfig, LLMConfig

TRAIN = [("q1", "a1"), ("q2", "a2"), ("q3", "a3"), ("q4", "a4")]
VAL = [("v1", "b1"), ("v2", "b2"), ("v3", "b3"), ("v4", "b4")]
TEST = [("t1", "c1"), ("t2", "c2")]
ANSWERS = dict(TRAIN + VAL + TEST)


def knows(answers_by_prompt):
    """Target that answers correctly the inputs listed for its prompt, 'x' otherwise."""
    def respond(full_prompt, system_message):
        prompt, inp = target_parts(full_prompt)
        return ANSWERS[inp] if inp in answers_by_prompt.get(prompt, ()) else "x"
    return respond


def prompts_tested(target_fake, inputs):
    """Prompts the target was called with on the first input of a set, in call order."""
    return [target_parts(p)[0] for p, _ in target_fake.calls if target_parts(p)[1] == inputs[0][0]]


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


# A lookup-table prompt memorises train and knows nothing held out; GOOD generalises a little.
GATE_TARGET = knows({
    "P0": {"q1", "v1"},
    "LOOKUP": {"q1", "q2", "q3", "q4"},
    "WORSE": set(),
    "GOOD": {"q1", "q2", "v1", "v2", "t1"},
})


def gated_system(tmp_path, proposals, **experiment):
    storage = {"val_file": write_json(tmp_path / "val.json", VAL),
               "test_file": write_json(tmp_path / "test.json", TEST)}
    return make_system(tmp_path, scripted_optimizer(proposals), GATE_TARGET, TRAIN,
                       experiment={"acceptance": "val", "max_iterations": len(proposals), **experiment},
                       storage=storage)


def test_val_gate_rejects_lookup_table_and_accepts_prompt_that_generalises(tmp_path):
    system, opt, tgt = gated_system(tmp_path, ["LOOKUP", "WORSE", "GOOD"])
    report = system.run()
    assert report["acceptance"] == "val"
    assert report["best_prompt"] == "GOOD" and report["stat_best_prompt"] == "GOOD"
    assert (report["accepted"], report["rejected"]) == (1, 2)
    assert report["rejection_reasons"] == {"val": 1, "train": 1}
    assert (report["val_initial"], report["val_best"]) == (0.25, 0.5)
    assert (report["test_initial"], report["test_best"]) == (0.0, 0.5)
    # WORSE lost on train, so it never cost val calls; test is scored once per prompt at the end
    assert prompts_tested(tgt, VAL) == ["P0", "LOOKUP", "GOOD"]
    assert prompts_tested(tgt, TEST) == ["P0", "GOOD"]


def test_rejected_prompt_is_reverted_and_shown_to_optimizer_as_rejected(tmp_path):
    system, opt, tgt = gated_system(tmp_path, ["LOOKUP", "GOOD"])
    system.run()
    second_request = opt.calls[1][0]
    assert "Current Prompt:\n```\nP0\n```" in second_request  # reverted to the incumbent
    assert "REJECTED" in second_request and "LOOKUP" in second_request
    assert "v1" not in second_request and "b1" not in second_request  # val never reaches the Optimizer


def test_legacy_mode_still_adopts_the_lookup_table(tmp_path):
    storage = {"test_file": write_json(tmp_path / "test.json", TEST)}
    system = make_system(tmp_path, scripted_optimizer(["LOOKUP", "GOOD"]), GATE_TARGET, TRAIN,
                         experiment={"max_iterations": 2}, storage=storage)[0]
    report = system.run()
    assert report["acceptance"] == "always" and report["best_prompt"] == "LOOKUP"
    assert (report["test_initial"], report["test_best"]) == (0.0, 0.0)
    assert "val_best" not in report


def test_acceptance_val_requires_val_file(tmp_path):
    from config_manager import load_config
    cfg = tmp_path / "c.yaml"
    cfg.write_text("optimizer_llm: {backend: claude_cli}\ntarget_llm: {backend: claude_cli}\n"
                   "experiment: {acceptance: val}\n")
    with pytest.raises(ValueError, match="val_file"):
        load_config(str(cfg))
