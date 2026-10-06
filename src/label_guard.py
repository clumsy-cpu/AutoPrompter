"""
Label guard: detects evaluation answers copied into a candidate prompt.

An Optimizer that sees failing items can paste their expected answers into the prompt
(a lookup table). That raises the train score without teaching anything. The guard
rejects such prompts before they are tested.
"""

import re
from typing import Iterable, List

from metrics import MetricsEvaluator

_normalize = MetricsEvaluator('exact_match')._normalize_text


def _contains_phrase(normalized_text: str, normalized_phrase: str) -> bool:
    return re.search(rf'(?<!\w){re.escape(normalized_phrase)}(?!\w)', normalized_text) is not None


def guarded_labels(labels: Iterable[str], initial_prompt: str, min_len: int = 4) -> List[str]:
    """Labels worth guarding: long enough to be specific, and not already in the initial prompt.

    Labels the initial prompt already names (class names such as 'positive') are format,
    not leaked facts, so they are left out.
    """
    initial = _normalize(initial_prompt)
    kept = []
    for label in dict.fromkeys(labels):  # dedupe, keep order
        norm = _normalize(label)
        if len(norm) >= min_len and not _contains_phrase(initial, norm):
            kept.append(label)
    return kept


def find_leaked_labels(prompt: str, labels: Iterable[str]) -> List[str]:
    """Labels that appear in the prompt as whole words, after the metrics' text normalization."""
    text = _normalize(prompt)
    return [label for label in labels if _contains_phrase(text, _normalize(label))]
