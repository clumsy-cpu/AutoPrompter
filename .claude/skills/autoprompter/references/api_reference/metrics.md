# API Reference: metrics.py

**Language**: Python

**Source**: `src/metrics.py`

---

## Classes

### MetricsEvaluator

Evaluates model outputs against expected outputs using various metrics.

**Inherits from**: (none)

#### Methods

##### __init__(self, metric_type: str = 'accuracy')

Initialize with metric type.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| metric_type | str | 'accuracy' | - |


##### _get_evaluator(self) → Callable[[str, str], float]

Get the appropriate evaluation function.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `Callable[[str, str], float]`


##### _normalize_text(self, text: str) → str

Normalize text for comparison.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |

**Returns**: `str`


##### _accuracy(self, predicted: str, expected: str) → float

Calculate accuracy (exact match after normalization).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| predicted | str | - | - |
| expected | str | - | - |

**Returns**: `float`


##### _exact_match(self, predicted: str, expected: str) → float

Calculate exact match (case-insensitive).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| predicted | str | - | - |
| expected | str | - | - |

**Returns**: `float`


##### _extract_math_answer(self, text: str) → str

Extract the final numerical answer from math problem output.

Looks for patterns like:
- "Final Answer: 47"
- "Final Answer: 47 muffins"
- "The answer is 47"
- Just "47" at the end

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |

**Returns**: `str`


##### _normalize_number(self, text: str) → str

Normalize a number for comparison.

Handles:
- "47" == "47 muffins"
- "2.4" == "2.40"
- "120 mph" == "120"
- "129.60" == "129.6"

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |

**Returns**: `str`


##### _contains(self, predicted: str, expected: str) → float

Check if expected content is contained in prediction with granular feedback.

For math problems, this extracts and compares the final numerical answers
rather than requiring the full step-by-step solution to be contained.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| predicted | str | - | - |
| expected | str | - | - |

**Returns**: `float`


##### get_feedback(self, predicted: str, expected: str) → Dict[str, Any]

Get detailed feedback about why a prediction failed or succeeded.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| predicted | str | - | - |
| expected | str | - | - |

**Returns**: `Dict[str, Any]`


##### _f1_score(self, predicted: str, expected: str) → float

Calculate F1 score based on token overlap.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| predicted | str | - | - |
| expected | str | - | - |

**Returns**: `float`


##### _semantic_similarity(self, predicted: str, expected: str) → float

Calculate semantic similarity using sequence matcher.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| predicted | str | - | - |
| expected | str | - | - |

**Returns**: `float`


##### evaluate(self, predicted: str, expected: str) → float

Evaluate a single prediction against expected output.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| predicted | str | - | - |
| expected | str | - | - |

**Returns**: `float`


##### evaluate_with_feedback(self, predicted: str, expected: str) → Tuple[float, Dict[str, Any]]

Evaluate and return detailed feedback about the prediction.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| predicted | str | - | - |
| expected | str | - | - |

**Returns**: `Tuple[float, Dict[str, Any]]`


##### evaluate_batch(self, predictions: List[str], expected: List[str]) → Dict[str, Any]

Evaluate a batch of predictions.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| predictions | List[str] | - | - |
| expected | List[str] | - | - |

**Returns**: `Dict[str, Any]`


##### get_metric_name(self) → str

Get the name of the metric.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`




### MetricDefinition

Defines a metric for the optimization process.

**Inherits from**: (none)

#### Methods

##### __init__(self, metric_type: str, target_score: float = 0.95, custom_evaluator: Callable = None, metric_description: str = None)

Initialize metric definition.

Args:
    metric_type: Type of metric ('accuracy', 'f1', 'exact_match', etc. or 'auto')
    target_score: Target score to reach
    custom_evaluator: Custom evaluation function
    metric_description: Description of how to evaluate (for auto-generated metrics)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| metric_type | str | - | - |
| target_score | float | 0.95 | - |
| custom_evaluator | Callable | None | - |
| metric_description | str | None | - |


##### set_custom_metric(self, description: str, evaluator_func: Callable = None)

Set a custom metric based on optimizer-generated description.

Args:
    description: Description of how to evaluate responses
    evaluator_func: Optional custom evaluation function

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| description | str | - | - |
| evaluator_func | Callable | None | - |


##### evaluate(self, predicted: str, expected: str) → float

Evaluate using the defined metric.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| predicted | str | - | - |
| expected | str | - | - |

**Returns**: `float`


##### is_target_reached(self, score: float) → bool

Check if target score is reached.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| score | float | - | - |

**Returns**: `bool`



