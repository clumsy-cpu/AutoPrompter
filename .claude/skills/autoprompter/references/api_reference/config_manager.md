# API Reference: config_manager.py

**Language**: Python

**Source**: `src/config_manager.py`

---

## Classes

### LLMConfig

Configuration for LLM models (OpenRouter backend).

**Inherits from**: (none)

#### Methods

##### __post_init__(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _load_api_key(self) → str

Load API key from config file or environment.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`




### LocalLLMConfig

Configuration for local LLM backends (Ollama, llama.cpp).

**Inherits from**: (none)

#### Methods

##### __post_init__(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### ClaudeCLIConfig

Configuration for the Claude Code CLI backend (`claude -p`, uses your Claude Code login).

**Inherits from**: (none)



### ExperimentConfig

Configuration for experiment parameters.

**Inherits from**: (none)



### TaskConfig

Configuration for the optimization task.

**Inherits from**: (none)



### MetricConfig

Configuration for evaluation metrics.

**Inherits from**: (none)



### ContextConfig

Configuration for context management.

**Inherits from**: (none)



### StorageConfig

Configuration for storage paths.

**Inherits from**: (none)



### Config

Main configuration container.

**Inherits from**: (none)

#### Methods

##### from_yaml(cls, filepath: str) → 'Config'

Load configuration from YAML file.

**Decorators**: `@classmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| cls | None | - | - |
| filepath | str | - | - |

**Returns**: `'Config'`


##### to_yaml(self, filepath: str)

Save configuration to YAML file.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| filepath | str | - | - |


##### override_from_dict(self, overrides: Dict[str, Any])

Apply dynamic overrides to configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| overrides | Dict[str, Any] | - | - |


##### validate(self) → List[str]

Validate configuration and return list of errors.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `List[str]`




## Functions

### _build_llm_config(data: Dict[str, Any])

Pick the config class for an optimizer_llm / target_llm block by its backend.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| data | Dict[str, Any] | - | - |

**Returns**: (none)



### load_config(filepath: str = 'config.yaml', overrides: Optional[Dict[str, Any]] = None) → Config

Load and validate configuration with optional overrides.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| filepath | str | 'config.yaml' | - |
| overrides | Optional[Dict[str, Any]] | None | - |

**Returns**: `Config`


