# API Reference: robustness_tester.py

**Language**: Python

**Source**: `src/robustness_tester.py`

---

## Classes

### RobustnessResult

Result of robustness testing for a single prompt.

**Inherits from**: (none)



### RobustnessTester

Tests prompt robustness by generating input perturbations.

**Inherits from**: (none)

#### Methods

##### __init__(self, config: Optional[Dict[str, Any]] = None)

Initialize robustness tester with configuration.

Args:
    config: Configuration dict with keys:
        - enabled: bool (default True)
        - num_variants: int (default 3)
        - score_threshold: float (default 0.9)
        - strategies: List[str] (default all)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| config | Optional[Dict[str, Any]] | None | - |


##### generate_variants(self, entry: DatasetEntry) → List[DatasetEntry]

Generate perturbed variants of a dataset entry.

Args:
    entry: Original dataset entry
    
Returns:
    List of variant entries with perturbations applied

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| entry | DatasetEntry | - | - |

**Returns**: `List[DatasetEntry]`


##### _apply_perturbation(self, text: str, strategy: str) → str

Apply a specific perturbation strategy to text.

Args:
    text: Original text
    strategy: Perturbation strategy to apply
    
Returns:
    Perturbed text

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| strategy | str | - | - |

**Returns**: `str`


##### _add_typos(self, text: str, typo_rate: float = 0.05) → str

Add realistic typos to text based on keyboard proximity.

Args:
    text: Original text
    typo_rate: Probability of typo per character
    
Returns:
    Text with typos added

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |
| typo_rate | float | 0.05 | - |

**Returns**: `str`


##### _paraphrase(self, text: str) → str

Create a paraphrased version of the text.

Uses simple synonym replacement and sentence restructuring.

Args:
    text: Original text
    
Returns:
    Paraphrased text

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |

**Returns**: `str`


##### _vary_format(self, text: str) → str

Apply format variations to text.

Args:
    text: Original text
    
Returns:
    Text with format variations

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |

**Returns**: `str`


##### _add_ambiguity(self, text: str) → str

Add ambiguous phrasing to text.

Args:
    text: Original text
    
Returns:
    Text with ambiguous elements

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |

**Returns**: `str`


##### compute_robustness_score(self, original_score: float, variant_scores: List[float]) → RobustnessResult

Compute robustness score from original and variant scores.

Args:
    original_score: Score on original inputs
    variant_scores: Scores on perturbed variants
    
Returns:
    RobustnessResult with aggregated metrics

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| original_score | float | - | - |
| variant_scores | List[float] | - | - |

**Returns**: `RobustnessResult`


##### should_retry_with_robustness(self, result: RobustnessResult) → bool

Determine if prompt should be retried due to robustness failure.

Args:
    result: Robustness test result
    
Returns:
    True if prompt failed robustness and should be retried

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| result | RobustnessResult | - | - |

**Returns**: `bool`



