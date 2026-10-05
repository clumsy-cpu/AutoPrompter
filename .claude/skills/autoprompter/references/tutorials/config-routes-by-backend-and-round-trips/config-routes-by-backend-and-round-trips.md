# How To: Config Routes By Backend And Round Trips

**Difficulty**: Advanced
**Estimated Time**: 15 minutes
**Tags**: workflow, integration

## Overview

Workflow: test config routes by backend and round trips

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `os`
- `subprocess`
- `sys`
- `unittest.mock`
- `pytest`
- `claude_cli_client`
- `config_manager`

**Setup Required:**
```Python
# Fixtures: tmp_path
```

## Step-by-Step Guide

### Step 1: Assign cfg_file = value

```Python
cfg_file = tmp_path / 'c.yaml'
```

### Step 2: Call cfg_file.write_text()

```Python
cfg_file.write_text('optimizer_llm: {backend: claude_cli, model: sonnet}\ntarget_llm: {model: x, api_key: k}\n')
```

### Step 3: Assign cfg = Config.from_yaml(...)

```Python
cfg = Config.from_yaml(str(cfg_file))
```

**Verification:**
```Python
assert isinstance(cfg.optimizer_llm, ClaudeCLIConfig) and isinstance(cfg.target_llm, LLMConfig)
```

### Step 4: Call cfg_file.write_text()

```Python
cfg_file.write_text('optimizer_llm: {backend: ollama, model: m}\ntarget_llm: {backend: claude_cli, model: haiku}\n')
```

### Step 5: Assign cfg = Config.from_yaml(...)

```Python
cfg = Config.from_yaml(str(cfg_file))
```

**Verification:**
```Python
assert isinstance(cfg.optimizer_llm, LocalLLMConfig) and isinstance(cfg.target_llm, ClaudeCLIConfig)
```

### Step 6: Call cfg_file.write_text()

```Python
cfg_file.write_text('optimizer_llm: {backend: claude_cli, model: sonnet}\ntarget_llm: {backend: claude_cli, model: haiku}\n')
```

### Step 7: Assign cfg = Config.from_yaml(...)

```Python
cfg = Config.from_yaml(str(cfg_file))
```

### Step 8: Assign out = value

```Python
out = tmp_path / 'saved.yaml'
```

### Step 9: Call cfg.to_yaml()

```Python
cfg.to_yaml(str(out))
```

### Step 10: Assign reloaded = Config.from_yaml(...)

```Python
reloaded = Config.from_yaml(str(out))
```

**Verification:**
```Python
assert isinstance(reloaded.optimizer_llm, ClaudeCLIConfig) and reloaded.target_llm.model == 'haiku'
```


## Complete Example

```Python
# Setup
# Fixtures: tmp_path

# Workflow
cfg_file = tmp_path / 'c.yaml'
cfg_file.write_text('optimizer_llm: {backend: claude_cli, model: sonnet}\ntarget_llm: {model: x, api_key: k}\n')
cfg = Config.from_yaml(str(cfg_file))
assert isinstance(cfg.optimizer_llm, ClaudeCLIConfig) and isinstance(cfg.target_llm, LLMConfig)
cfg_file.write_text('optimizer_llm: {backend: ollama, model: m}\ntarget_llm: {backend: claude_cli, model: haiku}\n')
cfg = Config.from_yaml(str(cfg_file))
assert isinstance(cfg.optimizer_llm, LocalLLMConfig) and isinstance(cfg.target_llm, ClaudeCLIConfig)
cfg_file.write_text('optimizer_llm: {backend: claude_cli, model: sonnet}\ntarget_llm: {backend: claude_cli, model: haiku}\n')
cfg = Config.from_yaml(str(cfg_file))
out = tmp_path / 'saved.yaml'
cfg.to_yaml(str(out))
reloaded = Config.from_yaml(str(out))
assert isinstance(reloaded.optimizer_llm, ClaudeCLIConfig) and reloaded.target_llm.model == 'haiku'
assert cfg.validate() == []
```

## Next Steps


---

*Source: test_claude_cli_client.py:80 | Complexity: Advanced | Last updated: 2026-10-05*