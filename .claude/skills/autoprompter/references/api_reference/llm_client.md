# API Reference: llm_client.py

**Language**: Python

**Source**: `src/llm_client.py`

---

## Classes

### LLMResponse

Standardized response from LLM.

**Inherits from**: (none)



### LLMClient

Client for interacting with OpenRouter API.

**Inherits from**: (none)

#### Methods

##### __init__(self, config)

Initialize with configuration.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| config | None | - | - |


##### _rate_limit(self)

Apply rate limiting.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


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



