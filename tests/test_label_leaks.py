"""
Tests for experiment.hide_expected and experiment.label_guard. No real LLM is called.
"""

import os
import sys

import pytest

pytest.importorskip("scipy")  # optimization_system imports scipy at module level
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fakes import make_system, scripted_optimizer, target_parts, write_json
from label_guard import guarded_labels, find_leaked_labels

TRAIN = [("q1", "alphaword"), ("q2", "betaword"), ("q3", "gammaword")]
VAL = [("v1", "deltaword")]


def always_wrong(full_prompt, system_message):
    return "no idea"


def optimizer_text(opt):
    return "\n".join(prompt + (system or "") for prompt, system in opt.calls)


@pytest.mark.parametrize("hide", [False, True])
def test_hide_expected_keeps_answers_out_of_every_optimizer_request(tmp_path, hide):
    system, opt, _ = make_system(tmp_path, scripted_optimizer(["P1", "P2", "P3"]), always_wrong, TRAIN,
                                 experiment={"hide_expected": hide}, metric="contains")
    system.run()
    seen = optimizer_text(opt)
    leaked = [label for _, label in TRAIN if label in seen]
    assert (leaked == []) == hide
    assert "q1" in seen  # inputs and outputs are still shown


def test_label_guard_refuses_train_and_val_answers_before_testing(tmp_path):
    proposals = ["Answer alphaword when unsure", "Always say deltaword", "Read the question carefully"]
    system, opt, tgt = make_system(tmp_path, scripted_optimizer(proposals), always_wrong, TRAIN,
                                   experiment={"label_guard": True, "hide_expected": True, "max_iterations": 2},
                                   storage={"val_file": write_json(tmp_path / "val.json", VAL)})
    report = system.run()
    tested = {target_parts(p)[0] for p, _ in tgt.calls}
    assert tested == {"P0", "Read the question carefully"}
    assert report["skipped_proposals"] == {"label_leak": 1}
    retry_request = opt.calls[1][0]
    assert "must never list answers" in retry_request
    assert "alphaword" not in optimizer_text(opt).replace(proposals[0], "")


def test_guarded_labels_skip_short_labels_and_class_names_in_the_initial_prompt():
    labels = ["positive", "negative", "positive", "a1", "observer.pid"]
    assert guarded_labels(labels, "Reply with positive or negative.") == ["observer.pid"]


def test_find_leaked_labels_matches_whole_words_after_normalization():
    assert find_leaked_labels("Check the .observer.PID file", ["observer.pid"]) == ["observer.pid"]
    assert find_leaked_labels("the betawordy thing", ["betaword"]) == []
