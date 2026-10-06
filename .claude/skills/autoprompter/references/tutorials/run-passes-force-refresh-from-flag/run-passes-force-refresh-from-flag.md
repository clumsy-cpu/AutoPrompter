# How To: Run Passes Force Refresh From Flag

**Difficulty**: Intermediate
**Estimated Time**: 10 minutes
**Tags**: pytest, workflow, integration

## Overview

Workflow: test run passes force refresh from flag

## Prerequisites

- [ ] Setup code must be executed first

**Required Modules:**
- `json`
- `os`
- `sys`
- `types`
- `unittest.mock`
- `pytest`
- `config_manager`
- `dataset_generator`
- `optimization_system`

**Setup Required:**
```Python
# Fixtures: reuse, expected_force_refresh
```

## Step-by-Step Guide

### Step 1: Assign system = PromptOptimizationSystem.__new__(...)

```Python
system = PromptOptimizationSystem.__new__(PromptOptimizationSystem)
```

### Step 2: Assign system.auto_metric = False

```Python
system.auto_metric = False
```

### Step 3: Assign system.config = SimpleNamespace(...)

```Python
system.config = SimpleNamespace(experiment=SimpleNamespace(reuse_dataset=reuse))
```

### Step 4: Assign calls = value

```Python
calls = []
```

### Step 5: Assign system.generate_dataset = value

```Python
system.generate_dataset = lambda force_refresh=False: calls.append(force_refresh) or []
```

**Verification:**
```Python
assert system.run()['status'] == 'failed'
```


## Complete Example

```Python
# Setup
# Fixtures: reuse, expected_force_refresh

# Workflow
system = PromptOptimizationSystem.__new__(PromptOptimizationSystem)
system.auto_metric = False
system.config = SimpleNamespace(experiment=SimpleNamespace(reuse_dataset=reuse))
calls = []
system.generate_dataset = lambda force_refresh=False: calls.append(force_refresh) or []
assert system.run()['status'] == 'failed'
assert calls == [expected_force_refresh]
```

## Next Steps


---

*Source: test_reuse_dataset.py:31 | Complexity: Intermediate | Last updated: 2026-10-05*