# AutoPrompter: Autonomous Prompt Optimization System

<p align="center">
  <a href="https://heyneo.so" target="_blank">
    <img src="https://img.shields.io/badge/Made%20by-NEO-ff3b30?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJjdXJyZW50Q29sb3IiIHN0cm9rZS13aWR0aD0iMiI+PHBhdGggZD0iTTEyIDJMNCA3djZsOCA1IDgtNXYtNmwtOC01eiIvPjxwYXRoIGQ9Ik00IDEzbDggNSA4LTUiLz48L3N2Zz4=&logoColor=white" alt="Made by NEO">
  </a>
</p>

AutoPrompter is an autonomous system designed to iteratively improve LLM prompts through a closed-loop optimization process. It merges the validation and metrics capabilities of tools like `promptfoo` with the iterative improvement logic of `autoresearch`.

## System Architecture

The system operates in a continuous loop where an **Optimizer LLM** refines prompts for a **Target LLM** based on empirical performance data.

1.  **Dataset Generation**: The Optimizer LLM (Gemini 3.1 Flash - customizable through config.yaml) generates a synthetic dataset of input/output pairs based on the task description.
2.  **Iterative Improvement**:
    *   The Target LLM (Qwen 3.5 9b) is tested against the current prompt using the generated dataset.
    *   Performance is measured using a defined metric (Accuracy, F1, Semantic Similarity, etc.).
    *   The Optimizer LLM analyzes failures and successes to generate a refined prompt.
3.  **Experiment Ledger**: Every iteration is recorded in a persistent ledger to prevent duplicate experiments and track progress.
4.  **Context Management**: The system manages the history of experiments to provide the Optimizer LLM with relevant context without exceeding window limits.

### Core Components
- **Optimizer LLM**: `google/gemini-3.1-flash-lite-preview` (via OpenRouter)
- **Target LLM**: `qwen/qwen3.5-9b` (via OpenRouter)
- **Metrics**: Automated evaluation against expected outputs.
- **Ledger**: JSON-based tracking of all experiments.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/gauravvij/AutoPrompter.git
    cd AutoPrompter
    ```

2.  Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4.  Configure API Key (for OpenRouter backend):
    Set the `OPENROUTER_API_KEY` environment variable or add it to `/root/.config/openrouter/config`.

    **Note:** API key is only required when using OpenRouter backend. Local backends (Ollama, llama.cpp) do not require API keys.

## Configuration

The system is configured via YAML files. Key fields include:

- `optimizer_llm`: Model ID and parameters for the optimizer.
- `target_llm`: Model ID and parameters for the target.
- `experiment`: `max_iterations` (number of new prompts proposed after the baseline), `batch_size`, and convergence thresholds. Set `reuse_dataset: true` to test on your own saved `storage.dataset_file` (a JSON list of `{input, expected_output}`; the first `batch_size` entries are used). By default every run generates a fresh dataset.
- `task`: `name`, `description`, and `initial_prompt`.
- `metric`: `type` (e.g., `accuracy`, `semantic_similarity`, `strict_contains`) and `target_score`.
- `storage`: Paths for the ledger, dataset, and results.

### Supported Backends

AutoPrompter supports multiple LLM backends:

1. **OpenRouter** (default): Cloud-based LLM access via OpenRouter API
2. **Ollama**: Local LLM inference using Ollama server
3. **llama.cpp**: Local LLM inference using llama.cpp server
4. **Claude Code CLI** (`claude_cli`): Claude through `claude -p`, using your Claude Code login (no API key)

#### OpenRouter Configuration (Default)

```yaml
optimizer_llm:
  backend: "openrouter"
  model: "google/gemini-3.1-flash-lite-preview"
  api_base: "https://openrouter.ai/api/v1"
  temperature: 0.7
  max_tokens: 4096
```

#### Ollama Configuration

```yaml
optimizer_llm:
  backend: "ollama"
  model: "llama3.2"
  host: "http://localhost"
  port: 11434
  temperature: 0.7
  max_tokens: 4096
```

#### llama.cpp Configuration

```yaml
optimizer_llm:
  backend: "llama_cpp"
  model: "llama-3.2-3b"
  host: "http://localhost"
  port: 8080
  temperature: 0.7
  max_tokens: 4096
```

#### Claude Code CLI Configuration

```yaml
optimizer_llm:
  backend: "claude_cli"
  model: "sonnet"      # alias (sonnet, opus, haiku) or full model id
  timeout: 300
target_llm:
  backend: "claude_cli"
  model: "haiku"
```

Requires the `claude` CLI on `PATH`, already logged in. Each call runs
`claude -p --safe-mode --tools ""`: no `CLAUDE.md`, hooks, skills, MCP or tools, so the model only answers.
`temperature` and `max_tokens` are accepted but ignored (the CLI has no sampling flags). Calls are slower
than API calls and count against your Claude Code usage. See `config_claude.yaml`:
`python main.py --config config_claude.yaml`.

### Setting Up Local Backends

#### Ollama Setup

1. Install Ollama: https://ollama.ai
2. Pull a model:
   ```bash
   ollama pull llama3.2
   ```
3. Start the server:
   ```bash
   ollama serve
   ```
4. Use `config_ollama.yaml` or configure your own with `backend: "ollama"`

#### llama.cpp Setup

1. Build llama.cpp from source: https://github.com/ggerganov/llama.cpp
2. Download a GGUF model (e.g., from https://huggingface.co/TheBloke)
3. Start the server:
   ```bash
   ./llama-server -m llama-3.2-3b.Q4_K_M.gguf -c 4096 --host 0.0.0.0 --port 8080
   ```
4. Use `config_llama_cpp.yaml` or configure your own with `backend: "llama_cpp"`

#### Auto-Detection

You can also use `backend: "auto"` to automatically detect the available backend:

```yaml
optimizer_llm:
  backend: "auto"
  model: "llama3.2"
  host: "http://localhost"
  port: 11434
```

The system will probe both Ollama and llama.cpp endpoints to determine which is available.

## Usage

### Command Line Interface

Run the optimization process using the main entry point:

```bash
python main.py --config config.yaml
```

### Web UI (New!)

AutoPrompter now includes a web-based dashboard for real-time monitoring and control:

```bash
python web_ui.py
```

Then open http://localhost:5000 in your browser.

**Web UI Features:**
- **Real-time Dashboard**: Live updates of optimization progress with score history charts
- **Configuration Builder**: Interactive form to create and edit optimization configs
- **Checkpoint Management**: Save, load, and manage optimization checkpoints
- **Prompt Diff Visualization**: Compare prompt iterations side-by-side with highlighted changes
- **Export/Import**: Save complete optimization runs to JSON and reload them later
- **Log Streaming**: Real-time log output via Server-Sent Events

### Specific Task Examples

The repository includes pre-configured tasks:

- **Blogging**: Optimize prompts for high-quality blog post generation.
  ```bash
  python main.py --config config_blogging.yaml
  ```
- **Math**: Optimize prompts for solving complex mathematical problems.
  ```bash
  python main.py --config config_math.yaml
  ```
- **Reasoning**: Optimize prompts for logical reasoning and chain-of-thought tasks.
  ```bash
  python main.py --config config_reasoning.yaml
  ```

### Using Local Backends

- **Ollama**: Use the Ollama backend for local inference
  ```bash
  python main.py --config config_ollama.yaml
  ```

- **llama.cpp**: Use the llama.cpp backend for local inference
  ```bash
  python main.py --config config_llama_cpp.yaml
  ```

**Note:** Make sure your local backend server is running before starting the optimization process.

### Command Line Overrides

You can override configuration values directly from the CLI:

```bash
python main.py --config config.yaml --max-iterations 50 --override experiment.batch_size=10
```

## Honest Evaluation (opt-in)

By default the loop shows the Optimizer the expected answers of failing items, adopts every new
prompt, and picks the best prompt on the same items it learned from. A capable Optimizer can then
paste the answers into the prompt: the score reaches 1.0 and nothing carries over to new questions.
The keys below separate learning from selection. All are off by default; old configs run as before.

| Key | What it does |
|---|---|
| `experiment.acceptance: val` | A new prompt is kept only if it does not lose on train and beats the current prompt on `storage.val_file`. Otherwise it is rejected, the prompt reverts, and the Optimizer sees the attempt marked REJECTED. Val items never reach the Optimizer. Needs `storage.val_file` and `storage.test_file`. |
| `experiment.val_significance: true` | Also require a statistically significant val improvement. |
| `storage.test_file` | Scored once at the end for the initial and final prompts (`test_initial`, `test_best` in the report). Never used for decisions. |
| `experiment.hide_expected: true` | The Optimizer never sees expected outputs (feedback and history). |
| `experiment.label_guard: true` | A proposal that contains a train or val expected output is refused before testing; the Optimizer is asked once more. Labels under 4 characters and labels the initial prompt already names (class names) are not guarded. |
| `metric.type: strict_contains` | 1.0 only if the expected text appears as whole words in the answer. No partial credit, no number fallback; refusals ("not documented", "I don't know") score 0. |
| `experiment.candidates_per_step: 4` | Propose up to 5 prompts per iteration (one per strategy), score all on train, send the leader on to the decision. |
| `experiment.demo_count: 3` | After the loop, try `demo_trials` random sets of train examples in an `Examples:` block after the best prompt; keep a set only if it beats the prompt alone on val. Needs `storage.val_file`. |
| `<<<KEEP>>>` … `<<<END KEEP>>>` in `task.initial_prompt` | Protected section: a proposal that changes or drops it is refused. The markers are stripped from what the Target receives. |
| `task.context_files: [a.md, b.md]` | Files given to the Target before the prompt as reference material. The Optimizer sees only their names, so it has no facts to copy into the prompt. |

Use datasets with labels the Optimizer did not write (an Optimizer-generated dataset is reported as
self-graded). `scripts/split_dataset.py` splits one JSON file into disjoint train/val/test files:

```bash
python3 scripts/split_dataset.py grounded.json --out-dir data/ --val 30 --test 30
python main.py --config config_claude_gated.yaml
```

The report adds `val_initial`, `val_best`, `accepted`, `rejected`, `rejection_reasons`,
`skipped_proposals`, `final_prompt` (best prompt plus any examples) and `warnings` (small sets,
self-graded data). Val and test sets under 30 items are flagged: one item moves the score by 0.03 or more.

## Recent Enhancements

### Robustness & Stability Improvements
- **Baseline Evaluation Fix**: `best_score` now initializes from actual baseline prompt evaluation instead of 0.0
- **Statistical Significance Testing**: Welch's t-test with bootstrap fallback prevents noise-driven prompt switches (p<0.05 threshold)
- **Stagnation Detection**: Increased threshold from 2 to 5 iterations before triggering diversification
- **Semantic Duplicate Detection**: Embedding-based similarity check (SentenceTransformer, 0.95 threshold) prevents re-evaluating near-identical prompts
- **Prompt Complexity Tracking**: Monitors length, word count, and instruction count to detect "longer but not better" patterns

### Parallel Execution & Robustness Testing
- **Parallel Experiment Executor**: ThreadPoolExecutor for simultaneous candidate evaluation (max_workers=3)
- **Robustness Testing Framework**: Adversarial input generation (typos, ambiguity, format variations) with consistency scoring

### Web UI (New)
- Flask-based web interface with REST API and Server-Sent Events
- Real-time dashboard with Chart.js visualization
- Checkpoint management and configuration builder
- Prompt diff visualization with syntax highlighting
- Export/import functionality for saving optimization runs

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

## License

MIT

---

<p align="center">
  <a href="https://heyneo.so" target="_blank">
    <img src="https://img.shields.io/badge/Made%20by-NEO-ff3b30?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgc3Ryb2tlPSJjdXJyZW50Q29sb3IiIHN0cm9rZS13aWR0aD0iMiI+PHBhdGggZD0iTTEyIDJMNCA3djZsOCA1IDgtNXYtNmwtOC01eiIvPjxwYXRoIGQ9Ik00IDEzbDggNSA4LTUiLz48L3N2Zz4=&logoColor=white" alt="Made by NEO">
  </a>
</p>

<p align="center">
  <em>NEO - A fully autonomous AI Engineer</em>
</p>
