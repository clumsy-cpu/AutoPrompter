"""
Tests for the independent-label checks: required val/test sets, the self-graded warning,
and scripts/split_dataset.py. No real LLM is called.
"""

import json
import os
import subprocess
import sys

import pytest

pytest.importorskip("scipy")  # optimization_system imports scipy at module level
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fakes import make_system, scripted_optimizer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(ROOT, "scripts", "split_dataset.py")


def test_acceptance_val_requires_a_test_file_too(tmp_path):
    from config_manager import load_config
    cfg = tmp_path / "c.yaml"
    cfg.write_text("optimizer_llm: {backend: claude_cli}\ntarget_llm: {backend: claude_cli}\n"
                   "experiment: {acceptance: val}\nstorage: {val_file: v.json}\n")
    with pytest.raises(ValueError, match="test_file"):
        load_config(str(cfg))


def test_generated_dataset_is_flagged_as_self_graded(tmp_path):
    def optimizer(prompt, system_message):
        if "Generate" in prompt or "dataset" in (system_message or "").lower():
            return json.dumps([{"input": "q", "expected_output": "a"}])
        return "P1"
    system = make_system(tmp_path, optimizer, lambda p, s: "a", [("q", "a")],
                         experiment={"reuse_dataset": False, "max_iterations": 1})[0]
    report = system.run()
    assert any(w.startswith("Self-graded dataset") for w in report["warnings"])


def test_loaded_dataset_has_no_self_graded_warning(tmp_path):
    report = make_system(tmp_path, scripted_optimizer(["P1"]), lambda p, s: "a", [("q", "a")],
                         experiment={"max_iterations": 1})[0].run()
    assert "warnings" not in report


def run_split(tmp_path, *args):
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True)


def test_split_dataset_dedupes_and_is_repeatable(tmp_path):
    data = [{"input": f"q{i}", "expected_output": f"a{i}"} for i in range(10)]
    data.append({"input": "q3", "expected_output": "other"})  # duplicate input
    src = tmp_path / "all.json"
    src.write_text(json.dumps(data))
    for out in ("a", "b"):
        result = run_split(tmp_path, str(src), "--out-dir", str(tmp_path / out), "--val", "3", "--test", "0.2")
        assert result.returncode == 0, result.stderr
    assert "1 duplicate inputs dropped" in result.stdout
    sets = {name: json.load(open(tmp_path / "a" / f"{name}.json")) for name in ("train", "val", "test")}
    assert [len(sets[n]) for n in ("train", "val", "test")] == [5, 3, 2]
    inputs = [e["input"] for items in sets.values() for e in items]
    assert sorted(inputs) == sorted(f"q{i}" for i in range(10))  # disjoint and complete
    assert {e["expected_output"] for e in sum(sets.values(), []) if e["input"] == "q3"} == {"a3"}
    for name in sets:  # same seed, same split
        assert open(tmp_path / "a" / f"{name}.json").read() == open(tmp_path / "b" / f"{name}.json").read()


def test_split_dataset_refuses_an_empty_train_set(tmp_path):
    src = tmp_path / "all.json"
    src.write_text(json.dumps([{"input": "q", "expected_output": "a"}] * 1))
    result = run_split(tmp_path, str(src), "--out-dir", str(tmp_path / "o"), "--val", "1", "--test", "0")
    assert result.returncode == 1 and "no train entries" in result.stderr
