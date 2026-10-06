# API Reference: prompt_optimizer.py

**Language**: Python

**Source**: `src/prompt_optimizer.py`

---

## Classes

### PromptOptimizer

Optimizes prompts using an LLM based on experiment results.

**Inherits from**: (none)

#### Methods

##### __init__(self, llm_client: LLMClient, task_config)

Initialize with LLM client and task configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| llm_client | LLMClient | - | - |
| task_config | None | - | - |


##### _build_optimization_prompt(self, context: str, current_prompt: str, current_score: float, metric_name: str, feedback_summary: str = '') → str

Build prompt for optimization with chain-of-thought requirements.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| context | str | - | - |
| current_prompt | str | - | - |
| current_score | float | - | - |
| metric_name | str | - | - |
| feedback_summary | str | '' | - |

**Returns**: `str`


##### optimize(self, context: str, current_prompt: str, current_score: float, metric_name: str, feedback_summary: str = '') → Optional[str]

Generate an improved prompt based on context and results.

Implements diversification strategy: if score remains same for 2+ iterations,
generates 3 diverse candidates and selects the one with highest predicted potential.

Args:
    context: Context from previous experiments
    current_prompt: Current prompt being optimized
    current_score: Current performance score
    metric_name: Name of the metric being used
    feedback_summary: Detailed feedback about failures (optional)
    
Returns:
    Improved prompt string, or None if optimization failed

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| context | str | - | - |
| current_prompt | str | - | - |
| current_score | float | - | - |
| metric_name | str | - | - |
| feedback_summary | str | '' | - |

**Returns**: `Optional[str]`


##### generate_candidates(self, context: str, current_prompt: str, current_score: float, metric_name: str, feedback_summary: str = '', num_candidates: int = 3) → List[str]

Generate multiple prompt candidates for parallel evaluation.

This method generates N diverse candidates that can be evaluated in parallel
by the optimization system, selecting the actual best based on real scores.

Args:
    context: Context from previous experiments
    current_prompt: Current prompt being optimized
    current_score: Current performance score
    metric_name: Name of the metric being used
    feedback_summary: Detailed feedback about failures
    num_candidates: Number of candidates to generate (default 3)
    
Returns:
    List of prompt candidate strings

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| context | str | - | - |
| current_prompt | str | - | - |
| current_score | float | - | - |
| metric_name | str | - | - |
| feedback_summary | str | '' | - |
| num_candidates | int | 3 | - |

**Returns**: `List[str]`


##### _optimize_single(self, context: str, current_prompt: str, current_score: float, metric_name: str, feedback_summary: str = '') → Optional[str]

Generate a single improved prompt.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| context | str | - | - |
| current_prompt | str | - | - |
| current_score | float | - | - |
| metric_name | str | - | - |
| feedback_summary | str | '' | - |

**Returns**: `Optional[str]`


##### _optimize_diverse(self, context: str, current_prompt: str, current_score: float, metric_name: str, feedback_summary: str = '') → Optional[str]

Generate 3 diverse prompt candidates and select the best.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| context | str | - | - |
| current_prompt | str | - | - |
| current_score | float | - | - |
| metric_name | str | - | - |
| feedback_summary | str | '' | - |

**Returns**: `Optional[str]`


##### _build_diverse_prompt(self, context: str, current_prompt: str, current_score: float, metric_name: str, strategy: str, feedback_summary: str = '') → str

Build a diversification prompt for a specific strategy.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| context | str | - | - |
| current_prompt | str | - | - |
| current_score | float | - | - |
| metric_name | str | - | - |
| strategy | str | - | - |
| feedback_summary | str | '' | - |

**Returns**: `str`


##### _select_best_candidate(self, candidates: List[Tuple[str, str]], context: str, current_score: float) → str

Select the best prompt candidate based on predicted potential.

Uses the Optimizer LLM to evaluate which candidate has the highest
predicted potential for success.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| candidates | List[Tuple[str, str]] | - | - |
| context | str | - | - |
| current_score | float | - | - |

**Returns**: `str`


##### _clean_prompt_response(self, content: str) → str

Clean up the prompt response by removing markdown and whitespace.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| content | str | - | - |

**Returns**: `str`


##### compute_complexity_metrics(self, prompt: str) → Dict[str, Any]

Compute complexity metrics for a prompt to detect "longer but not better" patterns.

Tracks:
- Character length
- Word count
- Instruction count (imperative verbs, numbered steps)
- Average sentence length
- Structural complexity indicators

Args:
    prompt: The prompt text to analyze

Returns:
    Dictionary with complexity metrics

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |

**Returns**: `Dict[str, Any]`


##### log_prompt_complexity(self, prompt: str, score: float, iteration: int)

Log complexity metrics for a prompt to track "longer but not better" patterns.

Args:
    prompt: The prompt to analyze
    score: The performance score of this prompt
    iteration: Current iteration number

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |
| score | float | - | - |
| iteration | int | - | - |


##### generate_metric_prompt(self) → str

Generate prompt for metric definition based on task.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### generate_metric(self) → Optional[Dict[str, Any]]

Generate a custom metric definition using the Optimizer LLM.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `Optional[Dict[str, Any]]`


##### generate_initial_dataset_prompt(self, num_samples: int) → str

Generate prompt for initial dataset generation.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| num_samples | int | - | - |

**Returns**: `str`



