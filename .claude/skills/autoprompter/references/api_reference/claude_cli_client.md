# API Reference: claude_cli_client.py

**Language**: Python

**Source**: `src/claude_cli_client.py`

---

## Classes

### ClaudeCLIClient

Sends each prompt to `claude -p` and parses its JSON result.

**Inherits from**: (none)

#### Methods

##### __init__(self, config)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| config | None | - | - |


##### _rate_limit(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### _command(self, system_message: Optional[str]) → list

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| system_message | Optional[str] | - | - |

**Returns**: `list`


##### _parse_result(stdout: str) → dict

**Decorators**: `@staticmethod`

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| stdout | str | - | - |

**Returns**: `dict`


##### _make_request(self, prompt: str, system_message: Optional[str], max_retries: int = 3) → LLMResponse

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |
| system_message | Optional[str] | - | - |
| max_retries | int | 3 | - |

**Returns**: `LLMResponse`


##### query(self, prompt: str, system_message: Optional[str] = None) → LLMResponse

Send a single prompt to Claude through the CLI.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| prompt | str | - | - |
| system_message | Optional[str] | None | - |

**Returns**: `LLMResponse`



