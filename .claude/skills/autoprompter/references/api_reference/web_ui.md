# API Reference: web_ui.py

**Language**: Python

**Source**: `web_ui.py`

---

## Classes

### AppState

**Inherits from**: (none)

#### Methods

##### __init__(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |


##### reset(self)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |




### SSELogHandler

**Inherits from**: logging.Handler

#### Methods

##### __init__(self, log_queue: queue.Queue)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| log_queue | queue.Queue | - | - |


##### emit(self, record)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| self | None | - | - |
| record | None | - | - |




## Functions

### progress_callback(iteration: int, best_score: float, best_prompt: str, current_score, current_prompt: str = '')

Callback called by the optimizer.

When current_score is None it is a 'pre-run' signal (iteration just started,
experiment not yet evaluated) — we update current_test_prompt but do NOT add
to score_history so the chart gets no duplicate points.
When current_score is a float the experiment is finished and we record results.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| iteration | int | - | - |
| best_score | float | - | - |
| best_prompt | str | - | - |
| current_score | None | - | - |
| current_prompt | str | '' | - |

**Returns**: (none)



### run_optimization_in_thread(config: Config)

Run optimization in background thread.

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| config | Config | - | - |

**Returns**: (none)



### load_state_from_files()

Reconstruct dashboard state from checkpoint/report files written by main.py.
Called when no live web-started run is active in app_state.

**Returns**: (none)



### generate_status_stream()

Generate SSE stream for status updates.

**Returns**: (none)



### generate_log_stream()

Generate SSE stream for log entries.

**Returns**: (none)



### index()

Main page - redirects to dashboard.

**Returns**: (none)



### get_config()

Get current configuration.

**Returns**: (none)



### save_config()

Save configuration from form data.

**Returns**: (none)



### get_status()

Get current optimization status (HTTP polling fallback).

**Returns**: (none)



### status_stream()

Server-Sent Events stream for real-time status updates.

**Returns**: (none)



### logs_stream()

Server-Sent Events stream for real-time log updates.

**Returns**: (none)



### get_logs()

Return recent log entries for polling fallback (when SSE is unavailable).

**Returns**: (none)



### start_optimization()

Start optimization with current config.

**Returns**: (none)



### stop_optimization()

Stop current optimization.

**Returns**: (none)



### list_checkpoints()

List available checkpoints from all results directories.

**Returns**: (none)



### load_checkpoint()

Load a checkpoint and resume from it.

**Returns**: (none)



### get_results()

Get final results.

**Returns**: (none)



### export_results()

Export results to file.

**Returns**: (none)



### export_full_state()

Export full optimization state including all iterations.

**Returns**: (none)



### import_full_state()

Import full optimization state.

**Returns**: (none)


