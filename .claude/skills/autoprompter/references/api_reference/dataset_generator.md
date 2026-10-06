# API Reference: dataset_generator.py

**Language**: Python

**Source**: `src/dataset_generator.py`

---

## Classes

### DatasetEntry

Single dataset entry with input and expected output.

**Inherits from**: (none)

#### Methods

##### __post_init__(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### to_dict(self) → Dict[str, Any]

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `Dict[str, Any]`


##### from_dict(cls, data: Dict[str, Any]) → 'DatasetEntry'

**Decorators**: `@classmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| cls | None | - | - |
| data | Dict[str, Any] | - | - |

**Returns**: `'DatasetEntry'`




### DatasetGenerator

Generates synthetic datasets using Optimizer LLM.

**Inherits from**: (none)

#### Methods

##### __init__(self, llm_client: LLMClient, task_config)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| llm_client | LLMClient | - | - |
| task_config | None | - | - |


##### _fix_json(text: str) → str

Apply lightweight fixes for common LLM JSON mistakes.

**Decorators**: `@staticmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| text | str | - | - |

**Returns**: `str`


##### _extract_json_array(text: str) → Optional[list]

Extract the outermost JSON array from arbitrary text.

**Decorators**: `@staticmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| text | str | - | - |

**Returns**: `Optional[list]`


##### _extract_objects(text: str) → list

Regex-extract individual JSON objects when the array wrapper is broken.

**Decorators**: `@staticmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| text | str | - | - |

**Returns**: `list`


##### _robust_parse(self, text: str) → list

Try every strategy to get a list of dicts from LLM output.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| text | str | - | - |

**Returns**: `list`


##### _parse_dataset_response(self, response: str) → List[DatasetEntry]

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| response | str | - | - |

**Returns**: `List[DatasetEntry]`


##### _build_generation_prompt(self, num_samples: int) → str

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| num_samples | int | - | - |

**Returns**: `str`


##### _create_fallback_entries(self, num_samples: int) → List[DatasetEntry]

Hardcoded fallback so the run is never blocked by dataset failure.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| num_samples | int | - | - |

**Returns**: `List[DatasetEntry]`


##### generate(self, num_samples: int, max_retries: int = 2) → List[DatasetEntry]

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| num_samples | int | - | - |
| max_retries | int | 2 | - |

**Returns**: `List[DatasetEntry]`


##### validate_dataset(self, entries: List[DatasetEntry]) → Tuple[bool, str]

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| entries | List[DatasetEntry] | - | - |

**Returns**: `Tuple[bool, str]`


##### save_dataset(self, entries: List[DatasetEntry], filepath: str)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| entries | List[DatasetEntry] | - | - |
| filepath | str | - | - |


##### load_dataset(self, filepath: str) → List[DatasetEntry]

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| filepath | str | - | - |

**Returns**: `List[DatasetEntry]`



