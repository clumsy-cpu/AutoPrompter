# How To: Failures Retry Then Recover Or Give Up

**Difficulty**: Advanced
**Estimated Time**: 20 minutes
**Tags**: mock, workflow, integration

## Overview

Workflow: test failures retry then recover or give up

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
# Fixtures: run, _sleep
```

## Step-by-Step Guide

### Step 1: Assign client = make_client(...)

```Python
client = make_client()
```

### Step 2: Assign run.side_effect = value

```Python
run.side_effect = [proc(returncode=1, stderr='boom'), proc(json.dumps(RESULT))]
```

**Verification:**
```Python
assert client.query('hi').success is True and run.call_count == 2
```

### Step 3: Call run.reset_mock()

```Python
run.reset_mock()
```

### Step 4: Assign run.side_effect = None

```Python
run.side_effect = None
```

### Step 5: Assign run.return_value = proc(...)

```Python
run.return_value = proc(json.dumps({**RESULT, 'is_error': True, 'result': 'rate limited'}))
```

### Step 6: Assign resp = client.query(...)

```Python
resp = client.query('hi')
```

**Verification:**
```Python
assert resp.success is False and 'rate limited' in resp.error and (run.call_count == 3)
```

### Step 7: Call run.reset_mock()

```Python
run.reset_mock()
```

### Step 8: Assign run.side_effect = subprocess.TimeoutExpired(...)

```Python
run.side_effect = subprocess.TimeoutExpired(cmd='claude', timeout=1)
```

**Verification:**
```Python
assert 'TimeoutExpired' in client.query('hi').error
```

### Step 9: Call run.reset_mock()

```Python
run.reset_mock()
```

### Step 10: Assign run.side_effect = None

```Python
run.side_effect = None
```

### Step 11: Assign run.return_value = proc(...)

```Python
run.return_value = proc('not json')
```

**Verification:**
```Python
assert client.query('hi').success is False
```


## Complete Example

```Python
# Setup
# Fixtures: run, _sleep

# Workflow
client = make_client()
run.side_effect = [proc(returncode=1, stderr='boom'), proc(json.dumps(RESULT))]
assert client.query('hi').success is True and run.call_count == 2
run.reset_mock()
run.side_effect = None
run.return_value = proc(json.dumps({**RESULT, 'is_error': True, 'result': 'rate limited'}))
resp = client.query('hi')
assert resp.success is False and 'rate limited' in resp.error and (run.call_count == 3)
run.reset_mock()
run.side_effect = subprocess.TimeoutExpired(cmd='claude', timeout=1)
assert 'TimeoutExpired' in client.query('hi').error
run.reset_mock()
run.side_effect = None
run.return_value = proc('not json')
assert client.query('hi').success is False
```

## Next Steps


---

*Source: test_claude_cli_client.py:53 | Complexity: Advanced | Last updated: 2026-10-05*