# API Reference: local_llm_client.py

**Language**: Python

**Source**: `src/local_llm_client.py`

---

## Classes

### LLMResponse

Standardized response from LLM.

**Inherits from**: (none)



### LocalLLMClient

Client for interacting with local LLM backends (Ollama, llama.cpp).

**Inherits from**: (none)

#### Methods

##### __init__(self, config)

Initialize with configuration.

Args:
    config: Configuration object with backend, model, host, and other parameters

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| config | None | - | - |


##### _detect_backend(self) → str

Auto-detect available backend by probing endpoints.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `str`


##### _rate_limit(self)

Apply rate limiting.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _make_ollama_request(self, messages: List[Dict[str, str]], max_retries: int = 3) → LLMResponse

Make request to Ollama API.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| messages | List[Dict[str, str]] | - | - |
| max_retries | int | 3 | - |

**Returns**: `LLMResponse`


##### _make_llama_cpp_request(self, messages: List[Dict[str, str]], max_retries: int = 3) → LLMResponse

Make request to llama.cpp API (OpenAI-compatible).

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| messages | List[Dict[str, str]] | - | - |
| max_retries | int | 3 | - |

**Returns**: `LLMResponse`


##### _make_request(self, messages: List[Dict[str, str]], max_retries: int = 3) → LLMResponse

Make API request with retry logic.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| messages | List[Dict[str, str]] | - | - |
| max_retries | int | 3 | - |

**Returns**: `LLMResponse`


##### query(self, prompt: str, system_message: Optional[str] = None) → LLMResponse

Send a single prompt to the LLM.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |
| system_message | Optional[str] | None | - |

**Returns**: `LLMResponse`


##### query_with_history(self, messages: List[Dict[str, str]]) → LLMResponse

Send a conversation with history.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| messages | List[Dict[str, str]] | - | - |

**Returns**: `LLMResponse`


##### batch_query(self, prompts: List[str], system_message: Optional[str] = None) → List[LLMResponse]

Process multiple prompts sequentially.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompts | List[str] | - | - |
| system_message | Optional[str] | None | - |

**Returns**: `List[LLMResponse]`


##### list_models(self) → List[str]

List available models on the backend.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `List[str]`


##### check_connection(self) → bool

Check if the backend server is reachable.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |

**Returns**: `bool`




### TestConfig

**Inherits from**: (none)



## Functions

### get_available_backends() → List[str]

Get list of supported backend types.

**Returns**: `List[str]`


