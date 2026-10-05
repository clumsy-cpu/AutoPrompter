"""
Tests for experiment.reuse_dataset. No LLM is called.
"""

import json
import os
import sys
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

pytest.importorskip("scipy")  # optimization_system imports scipy at module level
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from config_manager import Config, ExperimentConfig
from dataset_generator import DatasetEntry
from optimization_system import PromptOptimizationSystem


def test_flag_defaults_off_and_loads_from_yaml(tmp_path):
    assert ExperimentConfig().reuse_dataset is False
    cfg_file = tmp_path / "c.yaml"
    cfg_file.write_text("optimizer_llm: {backend: claude_cli, model: opus}\n"
                        "target_llm: {backend: claude_cli, model: haiku}\n"
                        "experiment: {reuse_dataset: true, batch_size: 3}\n")
    assert Config.from_yaml(str(cfg_file)).experiment.reuse_dataset is True


@pytest.mark.parametrize("reuse, expected_force_refresh", [(False, True), (True, False)])
def test_run_passes_force_refresh_from_flag(reuse, expected_force_refresh):
    system = PromptOptimizationSystem.__new__(PromptOptimizationSystem)  # skip client setup
    system.auto_metric = False
    system.config = SimpleNamespace(experiment=SimpleNamespace(reuse_dataset=reuse))
    calls = []
    system.generate_dataset = lambda force_refresh=False: calls.append(force_refresh) or []
    assert system.run()["status"] == "failed"  # empty dataset stops the run right after the call
    assert calls == [expected_force_refresh]


def test_generate_dataset_loads_first_batch_size_entries_without_generating(tmp_path):
    path = tmp_path / "train.json"
    path.write_text(json.dumps([{"input": f"q{i}", "expected_output": f"a{i}"} for i in range(3)]))
    system = PromptOptimizationSystem.__new__(PromptOptimizationSystem)
    system.config = SimpleNamespace(storage=SimpleNamespace(dataset_file=str(path)),
                                    experiment=SimpleNamespace(batch_size=2))
    system.dataset_generator = Mock()
    system.dataset_generator.load_dataset.side_effect = lambda p: [DatasetEntry(**e) for e in json.load(open(p))]
    entries = system.generate_dataset(force_refresh=False)
    assert [e.input for e in entries] == ["q0", "q1"]
    system.dataset_generator.generate.assert_not_called()
