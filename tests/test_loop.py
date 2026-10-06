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


def by_strategy(**prompts):
    """Optimizer that answers generate_candidates by strategy name (in its system message)."""
    def respond(prompt, system_message):
        for strategy, answer in prompts.items():
            if f"'{strategy}'" in (system_message or ""):
                return answer
        return "FALLBACK"
    return respond


BATCH = by_strategy(structured_step_by_step="WORSE", minimal_directive="GOOD", expert_roleplay="LOOKUP")


def test_batch_keeps_the_train_leader_in_legacy_mode(tmp_path):
    system, opt, tgt = make_system(tmp_path, BATCH, GATE_TARGET, TRAIN,
                                   experiment={"candidates_per_step": 3, "max_iterations": 1})
    report = system.run()
    assert prompts_tested(tgt, TRAIN) == ["P0", "WORSE", "GOOD", "LOOKUP"]
    assert report["best_prompt"] == "LOOKUP" and report["experiments_count"] == 4


def test_batch_leader_still_has_to_pass_the_val_gate(tmp_path):
    system, opt, tgt = gated_system(tmp_path, ["unused"], candidates_per_step=3, max_iterations=1)
    opt.responder = BATCH
    report = system.run()
    assert report["best_prompt"] == "P0" and report["rejection_reasons"] == {"val": 1}
    assert prompts_tested(tgt, VAL) == ["P0", "LOOKUP"]  # only the train leader costs val calls


def test_batch_drops_leaking_candidates_before_testing(tmp_path):
    optimizer = by_strategy(structured_step_by_step="Say alphaword", minimal_directive="GOOD",
                            expert_roleplay="P0")
    train = [("q1", "alphaword"), ("q2", "betaword")]
    system, opt, tgt = make_system(tmp_path, optimizer, lambda p, s: "x", train,
                                   experiment={"candidates_per_step": 3, "max_iterations": 1,
                                               "label_guard": True})
    report = system.run()
    # generate_candidates itself drops "P0" (the current prompt) and adds its fallback proposal
    assert {target_parts(p)[0] for p, _ in tgt.calls} == {"P0", "GOOD", "FALLBACK"}
    assert report["skipped_proposals"] == {"label_leak": 1}


def demo_target(examples_help):
    """Target that knows v1, v2 and t1 only when the prompt carries examples (or never, if they don't help)."""
    def respond(full_prompt, system_message):
        prompt, inp = target_parts(full_prompt)
        has_examples = "\n\nExamples:\n\n" in prompt
        if has_examples == examples_help and inp in {"v1", "v2", "t1"}:
            return ANSWERS[inp]
        return "x"
    return respond


def demo_system(tmp_path, examples_help):
    storage = {"val_file": write_json(tmp_path / "val.json", VAL),
               "test_file": write_json(tmp_path / "test.json", TEST)}
    return make_system(tmp_path, scripted_optimizer(["P1"]), demo_target(examples_help), TRAIN,
                       experiment={"max_iterations": 1, "demo_count": 2, "demo_trials": 3}, storage=storage)


def test_examples_are_kept_when_they_beat_the_prompt_alone_on_val(tmp_path):
    system, opt, tgt = demo_system(tmp_path, examples_help=True)
    report = system.run()
    assert (report["val_without_demos"], report["val_with_demos"]) == (0.0, 0.5)
    assert len(report["demos"]) == 2
    assert {d["input"] for d in report["demos"]} <= {i for i, _ in TRAIN}  # train only
    assert report["final_prompt"].startswith(report["best_prompt"] + "\n\nExamples:\n\n")
    assert report["test_best"] == 0.5  # the test set sees the prompt with its examples
    assert not any("Examples:" in p for p, _ in opt.calls)  # examples never pass through the Optimizer


def test_examples_are_dropped_when_they_do_not_help(tmp_path):
    report = demo_system(tmp_path, examples_help=False)[0].run()
    assert report["demos"] == [] and report["val_with_demos"] is None
    assert report["final_prompt"] == report["best_prompt"]


def test_demo_count_requires_val_file(tmp_path):
    from config_manager import load_config
    cfg = tmp_path / "c.yaml"
    cfg.write_text("optimizer_llm: {backend: claude_cli}\ntarget_llm: {backend: claude_cli}\n"
                   "experiment: {demo_count: 2}\n")
    with pytest.raises(ValueError, match="demo_count"):
        load_config(str(cfg))
