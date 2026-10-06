# API Reference: app.js

**Language**: JavaScript

**Source**: `static/js/app.js`

---

## Functions

### init()

**Returns**: (none)



### updateModelOptions(llmType)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| llmType | None | - | - |

**Returns**: (none)



### cleanupEventSources()

**Returns**: (none)



### handleVisibilityChange()

**Returns**: (none)



### setupTabs()

**Returns**: (none)



### setupLLMTabs()

**Returns**: (none)



### setupFormHandlers()

**Returns**: (none)



### setupButtonHandlers()

**Returns**: (none)



### initChart()

**Returns**: (none)



### clearChart()

**Returns**: (none)



### updateChartThrottled(labels, bestScores, currentScores)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| labels | None | - | - |
| bestScores | None | - | - |
| currentScores | None | - | - |

**Returns**: (none)



### updateChartImmediate()

**Returns**: (none)



### loadConfig()

**Async function**

**Returns**: (none)



### populateForm(config)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| config | None | - | - |

**Returns**: (none)



### getFormData()

**Returns**: (none)



### saveConfig()

**Async function**

**Returns**: (none)



### loadConfigFromFile(file)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| file | None | - | - |

**Returns**: (none)



### parseYAML(content)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| content | None | - | - |

**Returns**: (none)



### startOptimization()

**Async function**

**Returns**: (none)



### stopOptimization()

**Async function**

**Returns**: (none)



### debounce(func, wait)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| func | None | - | - |
| wait | None | - | - |

**Returns**: (none)



### executedFunction(...args)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| ...args | None | - | - |

**Returns**: (none)



### updateDashboard(data)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| data | None | - | - |

**Returns**: (none)



### formatElapsedTime(seconds)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| seconds | None | - | - |

**Returns**: (none)



### startElapsedTimer()

**Returns**: (none)



### stopElapsedTimer()

**Returns**: (none)



### escapeHtml(text)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| text | None | - | - |

**Returns**: (none)



### updateStatusIndicator(status)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| status | None | - | - |

**Returns**: (none)



### startStatusStream()

**Returns**: (none)



### startStatusPolling()

**Returns**: (none)



### startLogPolling()

**Returns**: (none)



### startLogStream()

**Returns**: (none)



### renderRecentLogs(logs)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| logs | None | - | - |

**Returns**: (none)



### stripAnsi(str)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| str | None | - | - |

**Returns**: (none)



### appendLogEntry(entry)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| entry | None | - | - |

**Returns**: (none)



### renderCheckpoints(checkpoints)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| checkpoints | None | - | - |

**Returns**: (none)



### loadCheckpoint(path)

**Async function**

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| path | None | - | - |

**Returns**: (none)



### renderResults(report)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| report | None | - | - |

**Returns**: (none)



### exportResults(format)

**Async function**

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| format | None | - | - |

**Returns**: (none)



### exportFullState()

**Async function**

**Returns**: (none)



### importFullState()

**Returns**: (none)



### showPromptDiff()

**Returns**: (none)



### closePromptDiff()

**Returns**: (none)



### computeDiff(oldText, newText)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| oldText | None | - | - |
| newText | None | - | - |

**Returns**: (none)



### showToast(message, type = 'info')

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| message | None | - | - |
| type | None | 'info' | - |

**Returns**: (none)



### setValue(name, value)

**Parameters**:

| Name | Type | Default | Description |
|------|------|---------|-------------|
| name | None | - | - |
| value | None | - | - |

**Returns**: (none)



### later()

**Returns**: (none)



### poll()

**Async function**

**Returns**: (none)



### poll()

**Async function**

**Returns**: (none)


