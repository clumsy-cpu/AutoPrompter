"""
Tests for the strict_contains metric, including the 'contains' gotchas it closes.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from metrics import MetricsEvaluator

strict = MetricsEvaluator("strict_contains").evaluate
lenient = MetricsEvaluator("contains").evaluate


@pytest.mark.parametrize("predicted, expected", [
    ("Not documented in v2.1", "exit 2"),                                    # digit found elsewhere
    ("The observer is not running", "is running"),                           # token-overlap partial credit
    ("I don't see the specific Python expression, maybe 12 chars", "hexdigest()[:12]"),  # refusal + digit
])
def test_contains_gotchas_score_zero(predicted, expected):
    assert lenient(predicted, expected) > 0  # the old metric gave credit
    assert strict(predicted, expected) == 0.0


@pytest.mark.parametrize("predicted, expected, score", [
    ("It uses hexdigest()[:12] for the id", "hexdigest()[:12]", 1.0),
    ("The script exits with exit 2.", "exit 2", 1.0),
    ("Look in .observer.PID", "observer.pid", 1.0),
    ("Answer: running", "is running", 0.0),
    ("subrunning", "running", 0.0),                                  # whole words only
    ("Not documented, but probably observer.pid", "observer.pid", 0.0),  # guess after a refusal
    ("", "observer.pid", 0.0),
])
def test_strict_contains(predicted, expected, score):
    assert strict(predicted, expected) == score


def test_feedback_names_the_refusal():
    feedback = MetricsEvaluator("strict_contains").get_feedback("I do not know", "observer.pid")
    assert any("refuses" in issue for issue in feedback["issues"])


def test_config_accepts_strict_contains(tmp_path):
    from config_manager import load_config
    cfg = tmp_path / "c.yaml"
    cfg.write_text("optimizer_llm: {backend: claude_cli}\ntarget_llm: {backend: claude_cli}\n"
                   "metric: {type: strict_contains}\n")
    assert load_config(str(cfg)).metric.type == "strict_contains"
