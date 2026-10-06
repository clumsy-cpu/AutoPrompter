---
name: autoprompter
description: Local codebase analysis for AutoPrompter, an autonomous prompt-optimization system (Optimizer LLM refines prompts for a Target LLM using a generated dataset, metrics, and an experiment ledger). Use when running, configuring, extending, or debugging AutoPrompter.
doc_version: 
---

# AutoPrompter Codebase

## Description

AutoPrompter is a closed-loop system that iteratively improves LLM prompts. An **Optimizer LLM** generates a synthetic dataset, a **Target LLM** is tested against the current prompt, a metric scores the outputs, and the Optimizer rewrites the prompt based on failures. Every iteration is recorded in a persistent **experiment ledger** so duplicate experiments are avoided.

This skill is built from a single source: static analysis of the local repository (API extraction, dependency graph, design patterns, test examples, config patterns, README/CHANGELOG). All of it is codebase-derived, so it reflects what the code does, backed by the project README for intent. The extractor reported no conflicts, but a manual check against the code found the README/docstring mismatches listed in **Known Discrepancies** below.

**Path:** `~/AutoPrompter` (local `main` at `f5eda3c`: upstream `gauravvij/AutoPrompter` + `claude_cli` backend + `reuse_dataset`; fork remote `mine`, never push to `origin`)
**Files Analyzed:** 18 (re-scanned 2026-10-05 from a clean `git archive HEAD`, so worktrees under `.claude/` are excluded)
**Languages:** Python (17 files), JavaScript (1 file)
**Framework:** Flask (web UI)
**Analysis Depth:** deep

## Sources and Confidence

| Source | What it gives | Confidence | Priority |
|--------|---------------|------------|----------|
| `src/*.py`, `main.py`, `web_ui.py` (read directly) | Real behavior: loop order, thresholds, defaults | High (facts marked "verified" were checked in code) | 1 |
| `references/api_reference/` (extracted) | Class and method lists, docstrings | Medium: types often `None`, bodies summarized | 2 |
| `references/test_examples/`, `references/tutorials/` | Usage taken from tests | Medium-high: tests run with mocks | 2 |
| `README.md`, `CHANGELOG.md` | Intent, setup steps, UI features | Medium: some values are stale | 3 |
| `references/experiments.md` | Lessons from our own Claude-backed runs | High for this fork, not upstream | — |

**Where sources agree** (higher confidence): the component list and wiring, config block names, backend names, metric names, ledger dedupe (hash + embedding), checkpoint and SSE features of the web UI.

### Known Discrepancies

| Topic | README / docstring says | Code does (trust this) |
|-------|-------------------------|------------------------|
| Web UI port | 5000 (README) | `--port` default `PORT` env or **7860** (`web_ui.py:951`) |
| Diversification trigger | "2+ iterations" (`optimize` docstring, `prompt_optimizer.py:166`) | `stagnation_count >= 5` (`prompt_optimizer.py:192`) |
| Candidate generation | The API offers `generate_candidates` + `evaluate_candidates_parallel` | `run()` calls only `optimize()`; `generate_candidates` and `evaluate_candidates_parallel` are unused by the loop |
| Dataset reuse | `generate_dataset(force_refresh=False)` default suggests reuse | `run()` passes `force_refresh=not reuse_dataset` (`optimization_system.py:675`), so upstream always regenerates |
| `semantic_similarity` metric | Name suggests embeddings | `difflib` sequence matcher (docstring says so). Embeddings are used only by the ledger dedupe |
| Early stop | `convergence_threshold` reads as "stop when reached" | No stop before iteration 5 (`min_iterations = 5`, `optimization_system.py:405`) |
| API reference types | `None`, "Inherits from (none)" | Extraction artifacts; read `src/` for signatures |

## When to Use This Skill

Use this skill when you need to:

- **Run an optimization**: start a prompt-optimization job from the CLI (`python main.py --config ...`) or the Flask dashboard (`python web_ui.py`).
- **Write or fix a config YAML**: set `optimizer_llm`, `target_llm`, `experiment`, `task`, `metric`, and `storage` blocks.
- **Switch backends**: move between OpenRouter (cloud), Ollama, llama.cpp, `backend: "auto"` detection, or `claude_cli` (Claude Code login, no API key).
- **Add or change a metric**: modify `MetricsEvaluator` (accuracy, exact match, contains, F1, semantic similarity, math answer extraction).
- **Debug the loop**: duplicate prompts being rejected, context growing too large, malformed JSON in generated datasets, score plateaus, rate limits or retries.
- **Extend the system**: add a new LLM backend, perturbation strategy, optimizer strategy, or web UI feature.
- **Understand the architecture**: trace how `PromptOptimizationSystem` wires together the client, optimizer, ledger, context manager, dataset generator, and robustness tester.
- **Write tests**: follow the mocked-client patterns used for `LocalLLMClient`.

## Key Concepts

| Term | Meaning |
|------|---------|
| **Optimizer LLM** | Model that generates the dataset and proposes improved prompts (default `google/gemini-3.1-flash-lite-preview` via OpenRouter). |
| **Target LLM** | Model whose prompt is being optimized (default `qwen/qwen3.5-9b` via OpenRouter). |
| **Dataset / `DatasetEntry`** | Synthetic input and expected-output pairs produced by the Optimizer; size is set by `batch_size`. **`run()` regenerates the dataset on every run** (it called `generate_dataset(force_refresh=True)`), even if `storage.dataset_file` exists. `experiment.reuse_dataset: true` (merged on local `main`, commit f5eda3c) loads that file instead (first `batch_size` entries). The generated copy is saved as `generated_dataset_<task.name>.json` beside `dataset_file`. |
| **Experiment / `ExperimentRecord`** | One prompt evaluated against the dataset, with its score. Hashed for duplicate detection. |
| **Ledger (`ExperimentLedger`)** | JSON-backed history that rejects exact duplicates (hash) and semantic duplicates (embedding cosine similarity, default threshold 0.95). |
| **Context (`ContextManager`)** | Builds a bounded history string for the Optimizer. Keeps the last `max_experiments` (default 20) and compresses older ones once `compression_threshold` (default 50) is reached. |
| **Diversification** | `PromptOptimizer.optimize()` counts `stagnation_count` (iterations with no improvement). At `>= 5` it calls `_optimize_diverse` to pick a different strategy, then resets the count. *Verified in `src/prompt_optimizer.py`; an earlier version of this skill said 2.* |
| **Parallel evaluation** | `evaluate_candidates_parallel` scores multiple candidates concurrently with a `ThreadPoolExecutor`. |
| **Robustness testing** | Perturbs inputs (typos, paraphrases) and re-scores. Config keys: `enabled`, `num_variants` (3), `score_threshold` (0.9), `strategies`. |
| **Backend** | `openrouter` (default, needs API key), `ollama`, `llama_cpp`, `auto`, or `claude_cli` (runs `claude -p`; see below). `create_llm_client` picks the client by config class. |

## Architecture

```
main.py / web_ui.py
        │
        ▼
PromptOptimizationSystem  (src/optimization_system.py)
 ├─ LLMClient / LocalLLMClient     query(), retry + rate limiting
 ├─ DatasetGenerator               Optimizer LLM → List[DatasetEntry], robust JSON parsing
 ├─ MetricsEvaluator               evaluate(), get_feedback()
 ├─ PromptOptimizer                optimize(), generate_candidates()
 ├─ ExperimentLedger               duplicate detection, persistence
 ├─ ContextManager                 history compression for the Optimizer
 └─ RobustnessTester               generate_variants()
```

Main loop, from `PromptOptimizationSystem.run()` (verified in code):

1. `generate_dataset(force_refresh=True)`: a fresh dataset the Optimizer writes from `task.description` alone (with `reuse_dataset: true`, your saved `storage.dataset_file` instead). Then score the initial prompt as the **baseline**. Iteration 1 re-tests that same prompt, so the log shows "Duplicate experiment detected" and `max_iterations: 5` gives 4 new prompts.
2. While `iteration < max_iterations` (`max_iterations` is the TOTAL number of experiments):
   1. `run_experiment(current_prompt, dataset)` on the full dataset.
   2. If `ledger.is_duplicate_experiment` → `optimize()` a different prompt and `continue` (the iteration is spent).
   3. `ledger.add_experiment`, then update `raw_best_*` (no gate) and `best_*` (needs `_is_significant_improvement`).
   4. `context_manager.add_experiment`, then `check_convergence` → `break` if true.
   5. `_build_feedback_summary` → `prompt_optimizer.optimize(context, prompt, score, metric, feedback)` → new `current_prompt`. If it returns nothing, stop.
   6. Every `storage.checkpoint_interval` iterations (default 10) → `save_checkpoint()`.
3. Write `final_report.json` into `storage.results_dir` (default `results`).

The main loop calls `optimize()` only. `generate_candidates()` (5 strategies: `structured_step_by_step`, `minimal_directive`, `expert_roleplay`, `chain_of_thought`, `few_shot_examples`) and `evaluate_candidates_parallel()` exist in the API, but `run()` does not call them. Progress is reported through an optional `progress_callback(iteration, best_score, best_prompt, current_score)`, which the web UI uses to drive its live chart.

Frameworks detected: Flask. The static analysis found 17 Python files (11 in `src/`, 4 in `tests/`) plus `static/js/app.js`, `static/css`, a `templates/` folder, and `tests/`.

## ⚡ Quick Reference

### Codebase Statistics

**Languages:**
- **Python**: 17 files (94.4%)
- **JavaScript**: 1 file (5.6%)

**Analysis Performed:**
- ✅ API Reference (C2.5)
- ✅ Dependency Graph (C2.6)
- ✅ Design Patterns (C3.1)
- ✅ Test Examples (C3.2)
- ✅ Configuration Patterns (C3.4)
- ✅ Architectural Analysis (C3.7)
- ✅ Project Documentation (C3.9)

### Essential Commands

*From README (project documentation)*

```bash
# Setup
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export OPENROUTER_API_KEY=...        # only needed for the OpenRouter backend

# Run from the CLI
python main.py --config config.yaml

# Run a bundled task
python main.py --config config_math.yaml        # also: config_blogging.yaml, config_reasoning.yaml

# Run with a local backend
python main.py --config config_ollama.yaml
python main.py --config config_llama_cpp.yaml

# Web dashboard: default port is 7860 (env PORT or --port), bound to 0.0.0.0 (verified in web_ui.py; README says 5000)
python web_ui.py --port 5000

# CLI flags (verified in main.py)
python main.py -c config.yaml -i 50                         # -i = --max-iterations
python main.py -c config.yaml -o experiment.batch_size=10   # -o = --override, repeatable, key=value
python main.py -c config_ollama.yaml -v                     # -v = verbose logging
# An -o value without "=" prints "Warning: Invalid override format" and is skipped.
```

### Config: OpenRouter (default)

*From README*

```yaml
optimizer_llm:
  backend: "openrouter"
  model: "google/gemini-3.1-flash-lite-preview"
  api_base: "https://openrouter.ai/api/v1"
  temperature: 0.7
  max_tokens: 4096
```

### Config: Ollama

*From README; matches the codebase test fixtures*

```yaml
optimizer_llm:
  backend: "ollama"
  model: "llama3.2"
  host: "http://localhost"
  port: 11434
  temperature: 0.7
  max_tokens: 4096
```

### Config: llama.cpp and auto-detect

*From README*

```yaml
optimizer_llm:
  backend: "llama_cpp"
  model: "llama-3.2-3b"
  host: "http://localhost"
  port: 8080
```

```yaml
optimizer_llm:
  backend: "auto"     # probes Ollama and llama.cpp endpoints (LocalLLMClient._detect_backend)
  model: "llama3.2"
  host: "http://localhost"
  port: 11434
```

Start local servers first:

```bash
ollama pull llama3.2 && ollama serve
./llama-server -m llama-3.2-3b.Q4_K_M.gguf -c 4096 --host 0.0.0.0 --port 8080
```

### Config: claude_cli (local `main` only)

*From the repo's `config_claude.yaml` (codebase, verified)*

```yaml
optimizer_llm:
  backend: "claude_cli"
  model: "sonnet"          # writes datasets and new prompts
  timeout: 300
target_llm:
  backend: "claude_cli"
  model: "haiku"           # smaller target leaves room to improve
  timeout: 120
```

### Your own dataset with `reuse_dataset`

*From codebase (`run()` and `tests/test_reuse_dataset.py`)*

```yaml
experiment: {max_iterations: 8, batch_size: 10, reuse_dataset: true}
storage:    {dataset_file: "my_dataset.json"}   # first batch_size entries are used
```

```json
[
  {"input": "Which flag sets the iteration count?", "expected_output": "--max-iterations"},
  {"input": "Which env var holds the OpenRouter key?", "expected_output": "OPENROUTER_API_KEY"}
]
```

### Top-level config blocks

*From README*

| Block | Fields |
|-------|--------|
| `optimizer_llm` / `target_llm` | model id, backend, host/port, temperature, max_tokens |
| `experiment` | `max_iterations`, `batch_size`, convergence thresholds |
| `task` | `name`, `description`, `initial_prompt` |
| `metric` | `type` (exactly one of `accuracy`, `f1`, `exact_match`, `contains`, `semantic_similarity`; anything else raises `ValueError: Unknown metric type`), `target_score` |
| `storage` | paths for the ledger, dataset, and results |

## 📝 Code Examples

*High-quality examples extracted from test files (C3.2). The test suite uses mocked responses, so no server is required.*

**Build a local Ollama config** (complexity 0.30; from test examples)

```python
config = LocalLLMConfig(backend='ollama', model='llama3.2', host='http://localhost', port=11434)
```

**Build a llama.cpp config** (complexity 0.30; from test examples)

```python
config = LocalLLMConfig(backend='llama_cpp', model='llama-3.2-3b', host='http://localhost', port=8080)
```

**Create a client and send a query** (complexity 0.15; from test examples)

```python
client = LocalLLMClient(config)
response = client.query('Say hello')   # returns an LLMResponse
```

**Same flow for llama.cpp** (from test examples)

```python
client = LocalLLMClient(config)
response = client.query('Test prompt')
```

**Check the connection gracefully** (from test examples)

Connection checks and model listing should fail gracefully, returning `False` and `[]`, when no server is running:

```python
print(f'✓ Connection check completed (connected: {is_connected})')
print(f'✓ List models completed (models: {models})')
```

**Initialize the optimization system with a progress callback** (from the `optimization_system.py` API)

```python
system = PromptOptimizationSystem(
    config,
    progress_callback=lambda iteration, best_score, best_prompt, current_score: print(iteration, best_score),
)
dataset = system.generate_dataset(force_refresh=False)   # loads storage.dataset_file when it has >= batch_size entries; run() itself passes force_refresh=True unless reuse_dataset
```

**Run and compare candidates** (from the `optimization_system.py` API)

```python
experiment = system.run_experiment(prompt, dataset)
results = system.evaluate_candidates_parallel(candidates, dataset)   # List[Tuple[str, Experiment]]
exp, robustness = system.run_experiment_with_robustness(prompt, dataset)
```

**Generate improved prompt candidates** (from the `prompt_optimizer.py` API)

```python
optimizer = PromptOptimizer(llm_client, task_config)
new_prompt = optimizer.optimize(context, current_prompt, current_score, metric_name, feedback_summary='')
candidates = optimizer.generate_candidates(context, current_prompt, current_score, metric_name, num_candidates=3)
```

**Evaluate a prediction** (from the `metrics.py` API)

```python
evaluator = MetricsEvaluator(metric_type='accuracy')
score = evaluator.evaluate(predicted, expected)          # float
details = evaluator.get_feedback(predicted, expected)    # Dict explaining the pass or fail
```

**Detect duplicates in the ledger** (from the `experiment_ledger.py` API)

```python
ledger = ExperimentLedger(storage_config, semantic_similarity_threshold=0.95)
if ledger.is_duplicate(record):   # exact hash match or semantic (embedding) match
    ...
```

*See `references/test_examples/` for all extracted examples.*

## 🎨 Design Patterns Detected

*From C3.1 analysis (confidence > 0.7)*

- **Observer**: 1 instance. This is the `progress_callback` hook in `PromptOptimizationSystem`, plus `SSELogHandler` feeding log records to the web UI.
- **Command**: 1 instance.

*Total: 2 high-confidence patterns. See `references/patterns/` for details.*

## Module Guide

*From API reference (C2.5)*

| File | Role | Notable API |
|------|------|-------------|
| `main.py` | CLI entry point | `parse_args()` |
| `web_ui.py` | Flask dashboard | `AppState` (`reset()`), `SSELogHandler(log_queue)` streaming logs over Server-Sent Events |
| `static/js/app.js` | Front end | `init`, `setupTabs`, `setupFormHandlers`, `initChart`, `updateChartThrottled`, `loadConfig`/`saveConfig`, `startOptimization`/`stopOptimization`, `parseYAML`, `debounce`, `cleanupEventSources` |
| `src/config_manager.py` | Config dataclasses | `LLMConfig` (OpenRouter, loads the API key from file or env), `LocalLLMConfig`, `ExperimentConfig`, `TaskConfig`, `MetricConfig` |
| `src/llm_client.py` | OpenRouter client | `LLMClient.query(prompt, system_message=None)`, `_make_request(messages, max_retries=3)`, `_rate_limit()` |
| `src/local_llm_client.py` | Ollama / llama.cpp client | `LocalLLMClient`, `_detect_backend()`, `_make_ollama_request`, `_make_llama_cpp_request` |
| `src/dataset_generator.py` | Synthetic data | `DatasetEntry`, `DatasetGenerator`, `_robust_parse` (with `_fix_json`, `_extract_json_array`, `_extract_objects` fallbacks) |
| `src/metrics.py` | Scoring | `MetricsEvaluator`: `_accuracy`, `_exact_match`, `_contains`, `_f1_score`, `_semantic_similarity`, `_extract_math_answer`, `get_feedback` |
| `src/prompt_optimizer.py` | Prompt rewriting | `PromptOptimizer`: `optimize`, `generate_candidates`, `_optimize_single`, `_optimize_diverse`, `_build_diverse_prompt` |
| `src/experiment_ledger.py` | History and dedupe | `ExperimentRecord` (`_compute_hash`), `ExperimentLedger` (`is_duplicate`, `is_semantic_duplicate`, `add_prompt_embedding`) |
| `src/context_manager.py` | Optimizer context | `ContextManager` (`add_experiment`, `_compress_history`, `get_context_for_optimizer`) |
| `src/robustness_tester.py` | Input perturbation | `RobustnessTester.generate_variants(entry)`, `_add_typos`, `_paraphrase` |
| `src/optimization_system.py` | Orchestrator | `PromptOptimizationSystem` (`generate_dataset`, `run_experiment`, `run_experiment_parallel`, `evaluate_candidates_parallel`, `run_experiment_with_robustness`) |
| `src/claude_cli_client.py` | Claude Code CLI client | `ClaudeCLIClient` (`_command`, `_parse_result`, `_make_request` with 3 retries, `query`) |
| `tests/test_claude_cli_client.py`, `tests/test_reuse_dataset.py` | Our tests (8 pass) | `python3 -m pytest tests/test_reuse_dataset.py tests/test_claude_cli_client.py -q -p no:cacheprovider` |
| `tests/test_integration.py`, `tests/test_optimization_fixes.py` | Upstream tests | 10 failures exist on untouched upstream too (hardcoded `/root/AutoPrompter/...` paths) |

## ⚙️ Configuration Patterns

*From C3.4 analysis*

- **Configuration files analyzed:** 8 (all typed `unknown`, i.e. YAML/JSON task and backend configs)
- **Total settings:** 183
- **Patterns detected:** 0 (the config shape comes from README and `config_manager.py`)

See `references/config_patterns/` for the raw settings.

## 📖 Project Documentation

*From C3.9: 2 documentation files (Overview and Changelog)*

- **Overview** (`README.md`): "AutoPrompter: Autonomous Prompt Optimization System". It merges the metric validation of `promptfoo` with the iterate-and-improve loop of `autoresearch`.
- **Changelog** (`CHANGELOG.md`): release history.

**Web UI API (verified in `web_ui.py`, Flask + CORS):** `GET/POST /api/config`, `GET /api/status`, `GET /api/status/stream` and `/api/logs/stream` (SSE), `GET /api/logs`, `POST /api/start`, `POST /api/stop`, `GET /api/checkpoints`, `POST /api/checkpoints/load`, `GET /api/results`, `POST /api/export`, `GET /api/export/full`, `POST /api/import`.

**Dependencies (`requirements.txt`):** `pyyaml`, `requests`, `openai`, `tqdm`, `numpy`, `scikit-learn`, `sentence-transformers` (large; the semantic dedupe model), `flask`, `flask_cors`. On Termux, `sentence-transformers` may fail to install. The ledger then falls back to exact-hash dedupe.

**Code vs README mismatches found:** web port (code 7860, README 5000); diversify trigger (code 5 stagnant iterations); the loop does not use `generate_candidates`. Trust the code.

**Web UI features (README):** live dashboard with score-history chart, interactive config builder, checkpoint save/load, side-by-side prompt diff, JSON export/import of runs, and SSE log streaming.

## Config and Workflows

*Verified against the repo's `config.yaml`, `main.py`, and `src/`.*

**Full `config.yaml` shape** (the default; OpenRouter, small test run):

```yaml
optimizer_llm: {model: "meta-llama/llama-3.1-8b-instruct", api_base: "https://openrouter.ai/api/v1", temperature: 0.7, max_tokens: 2048}
target_llm:    {model: "mistralai/mistral-nemo", api_base: "https://openrouter.ai/api/v1", temperature: 0.1, max_tokens: 128}
experiment: {max_iterations: 5, convergence_threshold: 0.95, min_improvement: 0.01, batch_size: 5}
task: {name: "text_classification", description: "...", initial_prompt: "..."}
metric: {type: "accuracy", target_score: 0.95}   # accuracy|f1|exact_match|contains|semantic_similarity
context: {max_experiments_in_context: 20, compression_threshold: 50}
storage: {ledger_file: "experiment_ledger.json", dataset_file: "generated_dataset.json", results_dir: "results", checkpoint_interval: 10}
```

Bundled configs: `config.yaml`, `config_math.yaml`, `config_reasoning.yaml`, `config_blogging.yaml`, `config_ollama.yaml`, `config_llama_cpp.yaml`, `config_web.yaml`. Copy the closest one, then change `task`, `metric`, and the LLM blocks. The optimizer can stay on OpenRouter while the target runs locally.

**Workflows**
- **First run:** `pip install -r requirements.txt`, set `OPENROUTER_API_KEY`, then `python main.py -c config.yaml -v`.
- **New task:** edit `task.*` and `metric.type`. The Optimizer writes the test data from `task.description` alone, so put every fact it needs there. For your own questions, write `storage.dataset_file` as a JSON list of `{input, expected_output}` and set `experiment.reuse_dataset: true`.
- **Resume or inspect:** checkpoints use `storage.checkpoint_interval`. Use `/api/checkpoints` and `/api/checkpoints/load`, or read the ledger JSON.
- **Override ignored:** the `-o` value has no `=`.

**Code facts**
- `LLMResponse` is defined twice, in `src/llm_client.py:17` and `src/local_llm_client.py:17`. The shape is the same, but the classes are separate.
- The API reference pages in `references/` list most parameter types as `None` and "Inherits from (none)". These are extraction artifacts. Open the source in `src/` for real signatures.

## Metric Gotchas (`contains`)

`MetricsEvaluator('contains')` (`_contains` in `src/metrics.py`) scores in this order. I verified each case by probing it:

1. **1.0** if the normalized label is inside the normalized answer.
2. **Number fallback** (built for math): it extracts a number from the label (`exit 2` becomes `2`), then gives 1.0 if that digit string appears **anywhere** in the answer. "Not documented in v2.1" scores 1.0 against `exit 2`. "See section 12" scores 1.0 against `hexdigest()[:12]`. A label without digits is not affected.
3. **Token-overlap partial credit:** the share of the label's words found in the answer. At 0.7 or more the score is 0.5, at 0.4 or more it is 0.3, at 0.2 or more it is 0.1. "...is **not** running" earns 0.5 against `observer-loop.sh is running`.

So scores are not binary, wrong-but-similar answers earn points, and refusals can score 1.0 when the label has a digit. For factual tests use identifier-style labels: file names, flags, variable names. Use at least 4 characters, at most 3 words, with letters, no digits and no `=`. `exact_match` is stricter.

## claude_cli Backend (local `main`, commits 55f4479 and f5eda3c)

- `backend: "claude_cli"` runs `claude -p --safe-mode --tools ""` for every call: prompt on stdin, JSON out, your Claude Code login, no API key. `model` is an alias (`opus`, `sonnet`, `haiku`) or a full id. `temperature` and `max_tokens` are ignored. Code: `src/claude_cli_client.py`, factory `create_llm_client`, routing `_build_llm_config`. Example: `config_claude.yaml`.
- The Target receives `"{prompt}\n\nInput: {input}\n\nOutput:"` with no system message (`optimization_system.py:201`).
- `_is_significant_improvement` warns "Precision loss ... catastrophic cancellation" when one score list is constant (for example all 1.0). It is a warning only.
- `LocalLLMConfig` cannot load back from a file saved with `Config.to_yaml`, because `to_yaml` writes `api_key: null` into every LLM block.

## Experiment Lessons (Claude-backed runs, 2026-10)

Full table and scripts: `references/experiments.md`. Short version:

- Sonnet/Haiku saturate the bundled tasks (1.0 from baseline). Pick a task where the baseline is < 0.7.
- Do not trust an Optimizer-written dataset: build one from ground truth and load it with `reuse_dataset: true`.
- Keep a holdout set. A train score of 1.0 came from the Optimizer pasting 9 of 11 training answers into the prompt; holdout barely moved.
- The Optimizer deletes sections the metric does not test. Protect them, or score them.
- A prompt cannot learn facts that only live in files nobody shows it. Supply the facts, or optimize a different goal.

## Working with This Skill

### Beginners
1. Read **Description** and **Architecture** above.
2. Install, set `OPENROUTER_API_KEY` (or start Ollama), and run `python main.py --config config_math.yaml`.
3. Try `python web_ui.py` and watch the chart update.

### Intermediate
1. Copy a bundled config and edit `task.initial_prompt`, `metric.type`, and `experiment.max_iterations`.
2. Use `references/api_reference/config_manager.md` to see what each config dataclass accepts.
3. Switch between OpenRouter and a local backend by changing only the `backend` fields.

### Advanced
1. Extend `MetricsEvaluator._get_evaluator` for a custom metric, then add its name to `metric.type`.
2. Add a backend by mirroring `LocalLLMClient._make_*_request` and exposing the same `query()` returning `LLMResponse`.
3. Tune dedupe via `semantic_similarity_threshold`, and context size via `ContextManager(max_experiments, compression_threshold)`.
4. Add perturbation strategies in `RobustnessTester._apply_perturbation`.

### Navigation tips
- All references come from one source (codebase analysis, medium confidence per file). Conflicts are between the README or docstrings and the code; **Known Discrepancies** lists them. When they disagree, **trust the code**, and add any new mismatch to that table.
- API pages in `references/api_reference/` are summarized, so open the file for full signatures.
- For "where does X get called", start at `references/dependencies/dependency_graph.mmd`.

## Troubleshooting Hints

*Inferred from the API surface and README; verify against the code.*

- **API key errors**: `LLMConfig._load_api_key` reads the config file (`/root/.config/openrouter/config`) or the `OPENROUTER_API_KEY` env var. Local backends need no key.
- **Local backend not reachable**: the connection check returns `False` and model listing returns `[]` when no server is running. Start Ollama or llama.cpp, or use `backend: "auto"`.
- **Dataset JSON parse failures**: `DatasetGenerator._robust_parse` already falls back from the array to per-object regex extraction. Each run regenerates the dataset (unless `reuse_dataset`), so a bad saved file matters only with `reuse_dataset: true`: fix the JSON or delete it.
- **Prompts repeating or stalling**: the ledger rejects exact and semantic duplicates (`is_duplicate` calls `is_semantic_duplicate`). In `run()`, a duplicate makes the Optimizer write a new prompt, and the loop `continue`s, so it still uses up one iteration. Five stagnant iterations trigger `_optimize_diverse`.
- **Run stops early or never stops early**: `check_convergence` returns `False` before iteration 5 (`min_iterations = 5`). Later it stops if the target score is reached, or if the last 3 scores differ by less than `experiment.min_improvement` (default 0.01). With `max_iterations: 5`, early stop cannot happen.
- **"Best score" differs between UI and optimizer**: `raw_best_score` has no significance gate and drives the UI. `best_score` needs `_is_significant_improvement` (bootstrap test) and is what the Optimizer sees as the baseline.
- **Embedding duplicate check inactive**: semantic dedupe depends on `_init_embedding_model`. If the embedding model is unavailable, `_compute_embedding` returns `Optional`, so only exact hash dedupe applies.
- **Rate limits and retries**: the clients retry up to `max_retries=3` and throttle in `_rate_limit()`.

## 📚 Available References

All references come from **codebase analysis** (single source, medium confidence).

| Path | Contents |
|------|----------|
| `references/api_reference/` | 18 per-file API docs: classes, methods, docstrings (`app`, `claude_cli_client`, `config_manager`, `context_manager`, `dataset_generator`, `experiment_ledger`, `llm_client`, `local_llm_client`, `main`, `metrics`, `optimization_system`, `prompt_optimizer`, `robustness_tester`, `web_ui`, and 4 test files). Medium confidence: parameter types are mostly `None`. |
| `references/dependencies/` | Import graph as `.mmd` and `.json`, plus `statistics.json`. `dependency_graph.dot` is empty (0 bytes); use the `.mmd`. |
| `references/patterns/` | Detected design patterns (`all_patterns`, `high_confidence_patterns`, `critical_patterns`, `summary`). |
| `references/test_examples/` | Extracted usage examples (`test_examples.md` and `.json`). |
| `references/config_patterns/` | Config settings analysis (`config_patterns.md` and `.json`). |
| `references/architecture/` | `architectural_patterns.json`: directory structure and detected frameworks (Flask). |
| `references/documentation/` | `overview/README.md`, `changelog/CHANGELOG.md`, and an extraction index. |
| `references/tutorials/` | 4 how-to guides built from test workflows (claude_cli parsing, retries, backend routing, `reuse_dataset` flag). |
| `references/experiments.md` | Results and lessons from 5 Claude-backed runs, with the scripts in `~/autoprompter-experiments/`. |

---

**Generated by Skill Seekers** | Codebase Analyzer with C3.x Analysis
