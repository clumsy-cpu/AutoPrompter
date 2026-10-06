# Test Example Extraction Report

**Total Examples**: 27  
**High Value Examples** (confidence > 0.7): 27  
**Average Complexity**: 0.31  

## Examples by Category

- **instantiation**: 20
- **method_call**: 3
- **workflow**: 4

## Examples by Language

- **Python**: 27

## Extracted Examples

### test_success_parses_event_array_and_object

**Category**: workflow  
**Description**: Workflow: test success parses event array and object  
**Expected**: assert run.call_args.args[0][run.call_args.args[0].index('--system-prompt') + 1] == 'You are a helpful assistant.'  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: run

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

*Source: ~/AutoPrompter/tests/test_claude_cli_client.py:33*

### test_failures_retry_then_recover_or_give_up

**Category**: workflow  
**Description**: Workflow: test failures retry then recover or give up  
**Expected**: assert client.query('hi').success is False  
**Confidence**: 0.90  
**Tags**: mock, workflow, integration  

```python
# Setup
# Fixtures: run, _sleep

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

*Source: ~/AutoPrompter/tests/test_claude_cli_client.py:53*

### test_config_routes_by_backend_and_round_trips

**Category**: workflow  
**Description**: Workflow: test config routes by backend and round trips  
**Expected**: assert cfg.validate() == []  
**Confidence**: 0.90  
**Tags**: workflow, integration  

```python
# Setup
# Fixtures: tmp_path

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

*Source: ~/AutoPrompter/tests/test_claude_cli_client.py:80*

### test_run_passes_force_refresh_from_flag

**Category**: workflow  
**Description**: Workflow: test run passes force refresh from flag  
**Expected**: assert calls == [expected_force_refresh]  
**Confidence**: 0.90  
**Tags**: pytest, workflow, integration  

```python
# Setup
# Fixtures: reuse, expected_force_refresh

system = PromptOptimizationSystem.__new__(PromptOptimizationSystem)
system.auto_metric = False
system.config = SimpleNamespace(experiment=SimpleNamespace(reuse_dataset=reuse))
calls = []
system.generate_dataset = lambda force_refresh=False: calls.append(force_refresh) or []
assert system.run()['status'] == 'failed'
assert calls == [expected_force_refresh]
```

*Source: ~/AutoPrompter/tests/test_reuse_dataset.py:31*

### test_connection_check

**Category**: method_call  
**Description**: Test connection check method (should fail gracefully without server).  
**Expected**: print(f'  (Expected False since no Ollama server is running)')  
**Confidence**: 0.85  

```python
print(f'✓ Connection check completed (connected: {is_connected})')
print(f'  (Expected False since no Ollama server is running)')
```

*Source: ~/AutoPrompter/tests/test_integration.py:232*

### test_list_models

**Category**: method_call  
**Description**: Test list models method (should fail gracefully without server).  
**Expected**: print(f'  (Expected empty list since no Ollama server is running)')  
**Confidence**: 0.85  

```python
print(f'✓ List models completed (models: {models})')
print(f'  (Expected empty list since no Ollama server is running)')
```

*Source: ~/AutoPrompter/tests/test_integration.py:251*

### test_flag_defaults_off_and_loads_from_yaml

**Category**: method_call  
**Description**: test flag defaults off and loads from yaml  
**Expected**: assert Config.from_yaml(str(cfg_file)).experiment.reuse_dataset is True  
**Confidence**: 0.85  

```python
# Setup
# Fixtures: tmp_path

cfg_file.write_text('optimizer_llm: {backend: claude_cli, model: opus}\ntarget_llm: {backend: claude_cli, model: haiku}\nexperiment: {reuse_dataset: true, batch_size: 3}\n')
assert Config.from_yaml(str(cfg_file)).experiment.reuse_dataset is True
```

*Source: ~/AutoPrompter/tests/test_reuse_dataset.py:24*

### test_success_parses_event_array_and_object

**Category**: instantiation  
**Description**: Instantiate proc: test success parses event array and object  
**Expected**: assert (resp.success, resp.content, resp.model) == (True, 'OK', 'claude-haiku-4-5-20251001')  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: run

run.return_value = proc(json.dumps(events))
```

*Source: ~/AutoPrompter/tests/test_claude_cli_client.py:36*

### test_success_parses_event_array_and_object

**Category**: instantiation  
**Description**: Instantiate query: test success parses event array and object  
**Expected**: assert (resp.success, resp.content, resp.model) == (True, 'OK', 'claude-haiku-4-5-20251001')  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: run

resp = client.query('hi', system_message='be brief')
```

*Source: ~/AutoPrompter/tests/test_claude_cli_client.py:37*

### test_success_parses_event_array_and_object

**Category**: instantiation  
**Description**: Instantiate proc: test success parses event array and object  
**Expected**: assert client.query('hi').content == 'OK'  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: run

run.return_value = proc(json.dumps(RESULT))
```

*Source: ~/AutoPrompter/tests/test_claude_cli_client.py:46*

### test_failures_retry_then_recover_or_give_up

**Category**: instantiation  
**Description**: Instantiate proc: test failures retry then recover or give up  
**Expected**: assert resp.success is False and 'rate limited' in resp.error and (run.call_count == 3)  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: run, _sleep

run.return_value = proc(json.dumps({**RESULT, 'is_error': True, 'result': 'rate limited'}))
```

*Source: ~/AutoPrompter/tests/test_claude_cli_client.py:60*

### test_failures_retry_then_recover_or_give_up

**Category**: instantiation  
**Description**: Instantiate query: test failures retry then recover or give up  
**Expected**: assert resp.success is False and 'rate limited' in resp.error and (run.call_count == 3)  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: run, _sleep

resp = client.query('hi')
```

*Source: ~/AutoPrompter/tests/test_claude_cli_client.py:61*

### test_failures_retry_then_recover_or_give_up

**Category**: instantiation  
**Description**: Instantiate TimeoutExpired: test failures retry then recover or give up  
**Expected**: assert 'TimeoutExpired' in client.query('hi').error  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: run, _sleep

run.side_effect = subprocess.TimeoutExpired(cmd='claude', timeout=1)
```

*Source: ~/AutoPrompter/tests/test_claude_cli_client.py:65*

### test_failures_retry_then_recover_or_give_up

**Category**: instantiation  
**Description**: Instantiate proc: test failures retry then recover or give up  
**Expected**: assert client.query('hi').success is False  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: run, _sleep

run.return_value = proc('not json')
```

*Source: ~/AutoPrompter/tests/test_claude_cli_client.py:70*

### test_ollama_client_query

**Category**: instantiation  
**Description**: Instantiate LocalLLMConfig: Test Ollama client with mocked response.  
**Confidence**: 0.80  
**Tags**: mock  

```python
config = LocalLLMConfig(backend='ollama', model='llama3.2', host='http://localhost', port=11434)
```

*Source: ~/AutoPrompter/tests/test_integration.py:20*

### test_ollama_client_query

**Category**: instantiation  
**Description**: Instantiate LocalLLMClient: Test Ollama client with mocked response.  
**Confidence**: 0.80  
**Tags**: mock  

```python
client = LocalLLMClient(config)
```

*Source: ~/AutoPrompter/tests/test_integration.py:27*

### test_ollama_client_query

**Category**: instantiation  
**Description**: Instantiate query: Test Ollama client with mocked response.  
**Confidence**: 0.80  
**Tags**: mock  

```python
response = client.query('Say hello')
```

*Source: ~/AutoPrompter/tests/test_integration.py:40*

### test_llama_cpp_client_query

**Category**: instantiation  
**Description**: Instantiate LocalLLMConfig: Test llama.cpp client with mocked response.  
**Confidence**: 0.80  
**Tags**: mock  

```python
config = LocalLLMConfig(backend='llama_cpp', model='llama-3.2-3b', host='http://localhost', port=8080)
```

*Source: ~/AutoPrompter/tests/test_integration.py:54*

### test_llama_cpp_client_query

**Category**: instantiation  
**Description**: Instantiate LocalLLMClient: Test llama.cpp client with mocked response.  
**Confidence**: 0.80  
**Tags**: mock  

```python
client = LocalLLMClient(config)
```

*Source: ~/AutoPrompter/tests/test_integration.py:61*

### test_llama_cpp_client_query

**Category**: instantiation  
**Description**: Instantiate query: Test llama.cpp client with mocked response.  
**Confidence**: 0.80  
**Tags**: mock  

```python
response = client.query('Test prompt')
```

*Source: ~/AutoPrompter/tests/test_integration.py:84*

### test_query_with_history

**Category**: instantiation  
**Description**: Instantiate LocalLLMConfig: Test conversation with history.  
**Confidence**: 0.80  
**Tags**: mock  

```python
config = LocalLLMConfig(backend='ollama', model='llama3.2', host='http://localhost', port=11434)
```

*Source: ~/AutoPrompter/tests/test_integration.py:98*

### test_query_with_history

**Category**: instantiation  
**Description**: Instantiate LocalLLMClient: Test conversation with history.  
**Confidence**: 0.80  
**Tags**: mock  

```python
client = LocalLLMClient(config)
```

*Source: ~/AutoPrompter/tests/test_integration.py:105*

### test_run_passes_force_refresh_from_flag

**Category**: instantiation  
**Description**: Instantiate __new__: test run passes force refresh from flag  
**Expected**: assert system.run()['status'] == 'failed'  
**Confidence**: 0.80  
**Tags**: pytest  

```python
# Setup
# Fixtures: reuse, expected_force_refresh

system = PromptOptimizationSystem.__new__(PromptOptimizationSystem)
```

*Source: ~/AutoPrompter/tests/test_reuse_dataset.py:32*

### test_run_passes_force_refresh_from_flag

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test run passes force refresh from flag  
**Expected**: assert system.run()['status'] == 'failed'  
**Confidence**: 0.80  
**Tags**: pytest  

```python
# Setup
# Fixtures: reuse, expected_force_refresh

system.config = SimpleNamespace(experiment=SimpleNamespace(reuse_dataset=reuse))
```

*Source: ~/AutoPrompter/tests/test_reuse_dataset.py:34*

### test_generate_dataset_loads_first_batch_size_entries_without_generating

**Category**: instantiation  
**Description**: Instantiate __new__: test generate dataset loads first batch size entries without generating  
**Expected**: assert [e.input for e in entries] == ['q0', 'q1']  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path

system = PromptOptimizationSystem.__new__(PromptOptimizationSystem)
```

*Source: ~/AutoPrompter/tests/test_reuse_dataset.py:44*

### test_generate_dataset_loads_first_batch_size_entries_without_generating

**Category**: instantiation  
**Description**: Instantiate SimpleNamespace: test generate dataset loads first batch size entries without generating  
**Expected**: assert [e.input for e in entries] == ['q0', 'q1']  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path

system.config = SimpleNamespace(storage=SimpleNamespace(dataset_file=str(path)), experiment=SimpleNamespace(batch_size=2))
```

*Source: ~/AutoPrompter/tests/test_reuse_dataset.py:45*

### test_generate_dataset_loads_first_batch_size_entries_without_generating

**Category**: instantiation  
**Description**: Instantiate generate_dataset: test generate dataset loads first batch size entries without generating  
**Expected**: assert [e.input for e in entries] == ['q0', 'q1']  
**Confidence**: 0.80  
**Tags**: mock  

```python
# Setup
# Fixtures: tmp_path

entries = system.generate_dataset(force_refresh=False)
```

*Source: ~/AutoPrompter/tests/test_reuse_dataset.py:49*

