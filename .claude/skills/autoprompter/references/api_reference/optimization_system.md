# API Reference: optimization_system.py

**Language**: Python

**Source**: `src/optimization_system.py`

---

## Classes

### PromptOptimizationSystem

Main system for autonomous prompt optimization.

**Inherits from**: (none)

#### Methods

##### __init__(self, config: Config, progress_callback = None)

Initialize the optimization system.

Args:
    config: Configuration object
    progress_callback: Optional callback function(iteration, best_score, best_prompt, current_score)
                      called after each iteration to report progress.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| config | Config | - | - |
| progress_callback | None | None | - |


##### generate_dataset(self, force_refresh: bool = False) → List[DatasetEntry]

Generate or load the test dataset.

Args:
    force_refresh: If True, always regenerate dataset regardless of existing file

Returns:
    List of dataset entries matching batch_size from config

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| force_refresh | bool | False | - |

**Returns**: `List[DatasetEntry]`


##### run_experiment(self, prompt: str, test_entries: List[DatasetEntry]) → Experiment

Run a single experiment with the given prompt.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |
| test_entries | List[DatasetEntry] | - | - |

**Returns**: `Experiment`


##### run_experiment_parallel(self, prompt: str, test_entries: List[DatasetEntry], worker_id: int = 0) → Experiment

Run a single experiment with the given prompt (thread-safe version for parallel execution).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |
| test_entries | List[DatasetEntry] | - | - |
| worker_id | int | 0 | - |

**Returns**: `Experiment`


##### evaluate_candidates_parallel(self, candidates: List[str], test_entries: List[DatasetEntry]) → List[Tuple[str, Experiment]]

Evaluate multiple prompt candidates in parallel using ThreadPoolExecutor.

Args:
    candidates: List of prompt candidates to evaluate
    test_entries: Dataset entries to test on
    
Returns:
    List of (prompt, experiment) tuples with results

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| candidates | List[str] | - | - |
| test_entries | List[DatasetEntry] | - | - |

**Returns**: `List[Tuple[str, Experiment]]`


##### run_experiment_with_robustness(self, prompt: str, test_entries: List[DatasetEntry]) → Tuple[Experiment, Optional[RobustnessResult]]

Run experiment with robustness testing on input variants.

Args:
    prompt: Prompt to test
    test_entries: Dataset entries to test
    
Returns:
    Tuple of (experiment, robustness_result)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |
| test_entries | List[DatasetEntry] | - | - |

**Returns**: `Tuple[Experiment, Optional[RobustnessResult]]`


##### check_convergence(self, current_score: float, previous_score: float) → bool

Check if optimization has converged.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| current_score | float | - | - |
| previous_score | float | - | - |

**Returns**: `bool`


##### _is_significant_improvement(self, current_scores: List[float], best_scores: List[float], current_mean: float, best_mean: float, alpha: float = 0.05) → bool

Check if score improvement is statistically significant.

Uses t-test to compare current scores against best scores.
Falls back to bootstrap test if t-test assumptions are violated.

Args:
    current_scores: List of scores from current experiment
    best_scores: List of scores from best experiment
    current_mean: Mean of current scores
    best_mean: Mean of best scores
    alpha: Significance level (default 0.05)

Returns:
    True if improvement is statistically significant

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| current_scores | List[float] | - | - |
| best_scores | List[float] | - | - |
| current_mean | float | - | - |
| best_mean | float | - | - |
| alpha | float | 0.05 | - |

**Returns**: `bool`


##### _bootstrap_significance_test(self, current_scores: List[float], best_scores: List[float], current_mean: float, best_mean: float, alpha: float = 0.05, n_bootstrap: int = 1000) → bool

Bootstrap-based significance test as fallback.

Args:
    current_scores: Current experiment scores
    best_scores: Best experiment scores
    current_mean: Mean of current scores
    best_mean: Mean of best scores
    alpha: Significance level
    n_bootstrap: Number of bootstrap samples

Returns:
    True if improvement is statistically significant

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| current_scores | List[float] | - | - |
| best_scores | List[float] | - | - |
| current_mean | float | - | - |
| best_mean | float | - | - |
| alpha | float | 0.05 | - |
| n_bootstrap | int | 1000 | - |

**Returns**: `bool`


##### _build_feedback_summary(self, experiment) → str

Build detailed feedback summary from experiment results.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| experiment | None | - | - |

**Returns**: `str`


##### save_checkpoint(self)

Save checkpoint of current state.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### generate_summary_report(self) → Dict[str, Any]

Generate final summary report.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `Dict[str, Any]`


##### run(self) → Dict[str, Any]

Run the full optimization loop.

max_iterations now represents the TOTAL number of improvement experiments
to run, not the number of batch cycles.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `Dict[str, Any]`




## Functions

### create_llm_client(llm_config)

Return the client that matches the config class (OpenRouter, local, or Claude CLI).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| llm_config | None | - | - |

**Returns**: (none)


