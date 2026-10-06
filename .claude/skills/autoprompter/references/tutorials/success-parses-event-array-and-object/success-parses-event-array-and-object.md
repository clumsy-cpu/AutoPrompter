# How To: Success Parses Event Array And Object

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test success parses event array and object

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
# Fixtures: run
```

## Step-by-Step Guide

### Step 1: Assign client = make_client(...)

```Python
client = make_client()
```

### Step 2: Assign events = value

```Python
events = [{'type': 'system'}, {'type': 'assistant'}, RESULT]
```

### Step 3: Assign run.return_value = proc(...)

```Python
run.return_value = proc(json.dumps(events))
```

### Step 4: Assign resp = client.query(...)

```Python
resp = client.query('hi', system_message='be brief')
```

**Verification:**
```Python
assert (resp.success, resp.content, resp.model) == (True, 'OK', 'claude-haiku-4-5-20251001')
```

### Step 5: Assign cmd = value

```Python
cmd = run.call_args.args[0]
```

**Verification:**
```Python
assert run.call_args.kwargs['input'] == 'hi'
```

### Step 6: Assign run.return_value = proc(...)

```Python
run.return_value = proc(json.dumps(RESULT))
```

**Verification:**
```Python
assert client.query('hi').content == 'OK'
```


## Complete Example

```Python
# Setup
# Fixtures: run

# Workflow
client = make_client()
events = [{'type': 'system'}, {'type': 'assistant'}, RESULT]
run.return_value = proc(json.dumps(events))
resp = client.query('hi', system_message='be brief')
assert (resp.success, resp.content, resp.model) == (True, 'OK', 'claude-haiku-4-5-20251001')
assert resp.usage == {'prompt_tokens': 602, 'completion_tokens': 4, 'total_tokens': 606}
cmd = run.call_args.args[0]
assert run.call_args.kwargs['input'] == 'hi'
assert cmd[cmd.index('--system-prompt') + 1] == 'be brief'
assert cmd[cmd.index('--model') + 1] == 'haiku'
assert '--safe-mode' in cmd and cmd[cmd.index('--tools') + 1] == ''
run.return_value = proc(json.dumps(RESULT))
assert client.query('hi').content == 'OK'
assert run.call_args.args[0][run.call_args.args[0].index('--system-prompt') + 1] == 'You are a helpful assistant.'
```

## Next Steps


---

*Source: test_claude_cli_client.py:33 | Complexity: Intermediate | Last updated: 2026-10-05*