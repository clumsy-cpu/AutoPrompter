"""
Configuration Management Module for Autonomous Prompt Optimization System.
Handles loading, validation, and dynamic overrides of configuration parameters.
"""

import yaml
import os
import json
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass, field, asdict


@dataclass
class LLMConfig:
    """Configuration for LLM models (OpenRouter backend)."""
    model: str
    api_base: str = "https://openrouter.ai/api/v1"
    temperature: float = 0.7
    max_tokens: int = 4096
    api_key: Optional[str] = None
    backend: str = "openrouter"  # Backend type: openrouter, ollama, llama_cpp
    
    def __post_init__(self):
        # Only require API key for OpenRouter backend
        if self.backend == "openrouter" and self.api_key is None:
            self.api_key = self._load_api_key()
    
    def _load_api_key(self) -> str:
        """Load API key from config file or environment."""
        config_path = "/root/.config/openrouter/config"
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('api_key', '')
            except (json.JSONDecodeError, IOError):
                pass
        
        # Fallback to environment variable
        api_key = os.getenv('OPENROUTER_API_KEY', '')
        if api_key:
            return api_key
        
        raise ValueError(
            "OpenRouter API key not found. Please set it in /root/.config/openrouter/config "
            "or as OPENROUTER_API_KEY environment variable."
        )


@dataclass
class LocalLLMConfig:
    """Configuration for local LLM backends (Ollama, llama.cpp)."""
    model: str
    backend: str = "ollama"  # ollama, llama_cpp, or auto
    host: str = "http://localhost"
    port: Optional[int] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: int = 120
    min_request_interval: float = 0.1
    
    def __post_init__(self):
        # Set default port if not specified
        if self.port is None:
            if self.backend == "ollama":
                self.port = 11434
            elif self.backend == "llama_cpp":
                self.port = 8080


@dataclass
class ClaudeCLIConfig:
    """Configuration for the Claude Code CLI backend (`claude -p`, uses your Claude Code login)."""
    model: str = "sonnet"  # alias or full model id passed to --model
    backend: str = "claude_cli"
    command: str = "claude"
    timeout: int = 300
    min_request_interval: float = 0.0
    temperature: float = 0.7  # accepted for config compatibility; the CLI has no sampling flags
    max_tokens: int = 4096  # accepted for config compatibility; ignored
    api_key: Optional[str] = None  # unused; Config.to_yaml writes this key into every LLM block


def _build_llm_config(data: Dict[str, Any]):
    """Pick the config class for an optimizer_llm / target_llm block by its backend."""
    backend = data.get('backend', 'openrouter')
    if backend == 'claude_cli':
        return ClaudeCLIConfig(**data)
    if backend in ['ollama', 'llama_cpp', 'auto']:
        return LocalLLMConfig(**data)
    return LLMConfig(**data)


@dataclass
class ExperimentConfig:
    """Configuration for experiment parameters."""
    max_iterations: int = 100
    convergence_threshold: float = 0.95
    min_improvement: float = 0.01
    batch_size: int = 5
    parallel_enabled: bool = False
    parallel_workers: int = 3
    parallel_candidates: int = 3
    reuse_dataset: bool = False  # True: load the first batch_size entries of storage.dataset_file instead of regenerating


@dataclass
class TaskConfig:
    """Configuration for the optimization task."""
    name: str = "text_classification"
    description: str = "Classify text into positive or negative sentiment"
    initial_prompt: str = "Analyze the sentiment of the following text and respond with only 'positive' or 'negative'."


@dataclass
class MetricConfig:
    """Configuration for evaluation metrics."""
    type: str = "accuracy"  # accuracy, f1, exact_match, contains, semantic_similarity
    target_score: float = 0.95


@dataclass
class ContextConfig:
    """Configuration for context management."""
    max_experiments_in_context: int = 20
    compression_threshold: int = 50


@dataclass
class StorageConfig:
    """Configuration for storage paths."""
    ledger_file: str = "experiment_ledger.json"
    dataset_file: str = "generated_dataset.json"
    results_dir: str = "results"
    checkpoint_interval: int = 10


@dataclass
class Config:
    """Main configuration container."""
    optimizer_llm: Union[LLMConfig, LocalLLMConfig]
    target_llm: Union[LLMConfig, LocalLLMConfig]
    experiment: ExperimentConfig
    task: TaskConfig
    metric: MetricConfig
    context: ContextConfig
    storage: StorageConfig
    
    @classmethod
    def from_yaml(cls, filepath: str) -> 'Config':
        """Load configuration from YAML file."""
        with open(filepath, 'r') as f:
            data = yaml.safe_load(f)
        
        # Determine which config class to use based on backend
        optimizer_data = data.get('optimizer_llm', {})
        target_data = data.get('target_llm', {})
        
        # The backend field of each block picks its config class
        
        # Create appropriate config objects
        optimizer_llm = _build_llm_config(optimizer_data)
        
        target_llm = _build_llm_config(target_data)
        
        return cls(
            optimizer_llm=optimizer_llm,
            target_llm=target_llm,
            experiment=ExperimentConfig(**data.get('experiment', {})),
            task=TaskConfig(**data.get('task', {})),
            metric=MetricConfig(**data.get('metric', {})),
            context=ContextConfig(**data.get('context', {})),
            storage=StorageConfig(**data.get('storage', {}))
        )
    
    def to_yaml(self, filepath: str):
        """Save configuration to YAML file."""
        data = {
            'optimizer_llm': asdict(self.optimizer_llm),
            'target_llm': asdict(self.target_llm),
            'experiment': asdict(self.experiment),
            'task': asdict(self.task),
            'metric': asdict(self.metric),
            'context': asdict(self.context),
            'storage': asdict(self.storage)
        }
        # Remove API keys from saved config for security (only blocks that have the field:
        # LocalLLMConfig has none and would not load back with an api_key key)
        for block in ('optimizer_llm', 'target_llm'):
            if 'api_key' in data[block]:
                data[block]['api_key'] = None
        
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    def override_from_dict(self, overrides: Dict[str, Any]):
        """Apply dynamic overrides to configuration."""
        for key, value in overrides.items():
            if '.' in key:
                # Nested override (e.g., 'experiment.max_iterations')
                parts = key.split('.')
                obj = self
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                setattr(obj, parts[-1], value)
            else:
                # Top-level override
                if hasattr(self, key):
                    setattr(self, key, value)
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        # Validate LLM configs
        if not self.optimizer_llm.model:
            errors.append("optimizer_llm.model is required")
        if not self.target_llm.model:
            errors.append("target_llm.model is required")
        
        # Only require API key for OpenRouter backend
        if isinstance(self.optimizer_llm, LLMConfig) and self.optimizer_llm.backend == "openrouter":
            if not self.optimizer_llm.api_key:
                errors.append("optimizer_llm.api_key is required for OpenRouter backend")
        if isinstance(self.target_llm, LLMConfig) and self.target_llm.backend == "openrouter":
            if not self.target_llm.api_key:
                errors.append("target_llm.api_key is required for OpenRouter backend")
        
        # Validate local backend configs
        if isinstance(self.optimizer_llm, LocalLLMConfig):
            if not self.optimizer_llm.model:
                errors.append("optimizer_llm.model is required for local backend")
            if self.optimizer_llm.backend not in ['ollama', 'llama_cpp', 'auto']:
                errors.append(f"optimizer_llm.backend must be one of ['ollama', 'llama_cpp', 'auto'], got '{self.optimizer_llm.backend}'")
        if isinstance(self.target_llm, LocalLLMConfig):
            if not self.target_llm.model:
                errors.append("target_llm.model is required for local backend")
            if self.target_llm.backend not in ['ollama', 'llama_cpp', 'auto']:
                errors.append(f"target_llm.backend must be one of ['ollama', 'llama_cpp', 'auto'], got '{self.target_llm.backend}'")
        
        # Validate experiment config
        if self.experiment.max_iterations < 1:
            errors.append("experiment.max_iterations must be >= 1")
        if self.experiment.batch_size < 1:
            errors.append("experiment.batch_size must be >= 1")
        
        # Validate task config
        if not self.task.name:
            errors.append("task.name is required")
        if not self.task.initial_prompt:
            errors.append("task.initial_prompt is required")
        
        # Validate metric config - now supports 'auto' for optimizer-defined metrics
        valid_metrics = ['accuracy', 'f1', 'exact_match', 'contains', 'semantic_similarity', 'auto']
        if self.metric.type not in valid_metrics:
            errors.append(f"metric.type must be one of {valid_metrics}")
        
        return errors


def load_config(filepath: str = "config.yaml", overrides: Optional[Dict[str, Any]] = None) -> Config:
    """Load and validate configuration with optional overrides."""
    config = Config.from_yaml(filepath)
    
    if overrides:
        config.override_from_dict(overrides)
    
    errors = config.validate()
    if errors:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(errors))
    
    return config


if __name__ == "__main__":
    # Test configuration loading
    import sys
    
    # Create test config
    config = Config(
        optimizer_llm=LLMConfig(
            model="qwen/qwen3.5-9b",
            api_key="test-key"
        ),
        target_llm=LLMConfig(
            model="qwen/qwen3.5-9b",
            api_key="test-key"
        ),
        experiment=ExperimentConfig(max_iterations=10),
        task=TaskConfig(
            name="test_task",
            initial_prompt="Test prompt"
        ),
        metric=MetricConfig(type="accuracy"),
        context=ContextConfig(),
        storage=StorageConfig()
    )
    
    # Test validation
    errors = config.validate()
    if errors:
        print("Validation errors:", errors)
        sys.exit(1)
    
    print("Configuration validation passed!")
    print(f"Optimizer LLM: {config.optimizer_llm.model}")
    print(f"Target LLM: {config.target_llm.model}")
    print(f"Max iterations: {config.experiment.max_iterations}")
