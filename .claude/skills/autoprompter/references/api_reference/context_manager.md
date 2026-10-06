# API Reference: context_manager.py

**Language**: Python

**Source**: `src/context_manager.py`

---

## Classes

### ExperimentSummary

Summary of an experiment for context.

**Inherits from**: (none)



### ContextManager

Manages context for Optimizer LLM to handle growing experiment history.

**Inherits from**: (none)

#### Methods

##### __init__(self, max_experiments: int = 20, compression_threshold: int = 50)

Initialize context manager.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| max_experiments | int | 20 | - |
| compression_threshold | int | 50 | - |


##### add_experiment(self, experiment: Dict[str, Any])

Add an experiment to history.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| experiment | Dict[str, Any] | - | - |


##### _compress_history(self)

Compress older experiments into summary.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### get_context_for_optimizer(self, current_prompt: str, current_score: float) → str

Generate context string for Optimizer LLM.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| current_prompt | str | - | - |
| current_score | float | - | - |

**Returns**: `str`


##### _format_experiment(self, exp: Dict[str, Any]) → str

Format a single experiment for context.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| exp | Dict[str, Any] | - | - |

**Returns**: `str`


##### get_experiment_count(self) → int

Get total number of experiments.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `int`


##### get_recent_experiments(self, n: int = 5) → List[Dict[str, Any]]

Get the n most recent experiments.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| n | int | 5 | - |

**Returns**: `List[Dict[str, Any]]`


##### get_best_experiment(self) → Optional[Dict[str, Any]]

Get the experiment with highest score.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `Optional[Dict[str, Any]]`


##### clear(self)

Clear all history.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |



