# API Reference: experiment_ledger.py

**Language**: Python

**Source**: `src/experiment_ledger.py`

---

## Classes

### ExperimentRecord

Single experiment record.

**Inherits from**: (none)

#### Methods

##### __post_init__(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _compute_hash(self) → str

Compute unique hash for this experiment to detect duplicates.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### to_dict(self) → Dict[str, Any]

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `Dict[str, Any]`


##### from_dict(cls, data: Dict[str, Any]) → 'ExperimentRecord'

**Decorators**: `@classmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| cls | None | - | - |
| data | Dict[str, Any] | - | - |

**Returns**: `'ExperimentRecord'`




### ExperimentLedger

Persistent storage for experiment records with duplicate detection.

Includes both exact hash-based deduplication and semantic similarity detection
using sentence embeddings to catch near-duplicate prompts.

**Inherits from**: (none)

#### Methods

##### __init__(self, storage_config, semantic_similarity_threshold: float = 0.95)

Initialize ledger with storage configuration.

Args:
    storage_config: Storage configuration
    semantic_similarity_threshold: Cosine similarity threshold for semantic duplicates (0.0-1.0)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| storage_config | None | - | - |
| semantic_similarity_threshold | float | 0.95 | - |


##### _init_embedding_model(self)

Initialize the embedding model for semantic duplicate detection.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _compute_embedding(self, prompt: str) → Optional[List[float]]

Compute embedding for a prompt.

Args:
    prompt: The prompt text to embed

Returns:
    Embedding vector as list of floats, or None if model unavailable

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |

**Returns**: `Optional[List[float]]`


##### _cosine_similarity(self, vec1: List[float], vec2: List[float]) → float

Compute cosine similarity between two vectors.

Args:
    vec1: First vector
    vec2: Second vector

Returns:
    Cosine similarity in range [-1, 1]

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| vec1 | List[float] | - | - |
| vec2 | List[float] | - | - |

**Returns**: `float`


##### is_semantic_duplicate(self, prompt: str, threshold: Optional[float] = None) → bool

Check if a prompt is semantically similar to any existing prompt.

Args:
    prompt: The prompt to check
    threshold: Optional override for similarity threshold

Returns:
    True if a semantic duplicate is found

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |
| threshold | Optional[float] | None | - |

**Returns**: `bool`


##### add_prompt_embedding(self, prompt: str, prompt_hash: str)

Compute and store embedding for a prompt.

Args:
    prompt: The prompt text
    prompt_hash: The hash identifier for the prompt

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |
| prompt_hash | str | - | - |


##### _load_ledger(self)

Load existing ledger from file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _save_ledger(self)

Save ledger to file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### is_duplicate(self, record: ExperimentRecord) → bool

Check if experiment is a duplicate (exact or semantic).

First checks exact hash match, then falls back to semantic similarity.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| record | ExperimentRecord | - | - |

**Returns**: `bool`


##### is_duplicate_experiment(self, record: ExperimentRecord) → bool

Alias for is_duplicate for compatibility.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| record | ExperimentRecord | - | - |

**Returns**: `bool`


##### add_experiment(self, record: ExperimentRecord) → bool

Alias for add_record for compatibility.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| record | ExperimentRecord | - | - |

**Returns**: `bool`


##### add_record(self, record: ExperimentRecord) → bool

Add record to ledger if not duplicate. Returns True if added.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| record | ExperimentRecord | - | - |

**Returns**: `bool`


##### get_records(self, iteration: Optional[int] = None) → List[ExperimentRecord]

Get records, optionally filtered by iteration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| iteration | Optional[int] | None | - |

**Returns**: `List[ExperimentRecord]`


##### get_all_experiments(self) → List[ExperimentRecord]

Get all experiment records.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `List[ExperimentRecord]`


##### get_all_records(self) → List[ExperimentRecord]

Alias for get_all_experiments.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `List[ExperimentRecord]`


##### get_best_record(self) → Optional[ExperimentRecord]

Get record with highest metric score.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `Optional[ExperimentRecord]`


##### get_statistics(self) → Dict[str, Any]

Get ledger statistics.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `Dict[str, Any]`


##### close(self)

Save ledger and cleanup.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |



