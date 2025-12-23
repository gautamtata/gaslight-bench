from dataclasses import dataclass, field
from typing import Any

from pydantic_ai.models.openrouter import OpenRouterModel


OUTPUT_DIRECTORY = "./results"

MAX_CONCURRENCY = 40
TEST_RUNS_PER_MODEL = 20
TIMEOUT_SECONDS = 800


@dataclass
class RunnableModel:
    name: str
    model_id: str
    reasoning: bool = False
    test_mode: bool = False
    provider_options: dict[str, Any] = field(default_factory=dict)


MODELS_TO_RUN: list[RunnableModel] = [
    # Open weight
    RunnableModel(
        name="kimi-k2",
        model_id="moonshotai/kimi-k2",
        reasoning=False,
    ),
    RunnableModel(
        name="kimi-k2-thinking",
        model_id="moonshotai/kimi-k2-thinking",
        reasoning=True,
    ),
    RunnableModel(
        name="minimax-m2",
        model_id="minimax/minimax-m2",
        reasoning=True,
    ),
    RunnableModel(
        name="qwen-3-32b",
        model_id="qwen/qwen3-32b",
        reasoning=True,
    ),
    # Google
    RunnableModel(
        name="gemini-3.0-flash-high",
        model_id="google/gemini-3-flash-preview",
        reasoning=True,
        provider_options={"reasoning": {"effort": "high"}},
    ),
    RunnableModel(
        name="gemini-3.0-flash-low",
        model_id="google/gemini-3-flash-preview",
        reasoning=True,
        provider_options={"reasoning": {"effort": "low"}},
    ),
    RunnableModel(
        name="gemini-2.0-flash",
        model_id="google/gemini-2.0-flash-001",
        test_mode=True,
    ),
    RunnableModel(
        name="gemini-2.5-pro",
        model_id="google/gemini-2.5-pro-preview",
        reasoning=True,
    ),
    RunnableModel(
        name="gemini-3-pro-preview",
        model_id="google/gemini-3-pro-preview",
        reasoning=True,
    ),
    # Grok
    RunnableModel(
        name="grok-3-mini",
        model_id="x-ai/grok-3-mini-beta",
        reasoning=True,
    ),
    RunnableModel(
        name="grok-4",
        model_id="x-ai/grok-4",
        reasoning=True,
    ),
    RunnableModel(
        name="grok-4.1-fast",
        model_id="x-ai/grok-4.1-fast",
        reasoning=True,
    ),
    # Anthropic
    RunnableModel(
        name="claude-4-sonnet",
        model_id="anthropic/claude-sonnet-4",
        reasoning=True,
    ),
    RunnableModel(
        name="claude-4.5-sonnet",
        model_id="anthropic/claude-sonnet-4.5",
        reasoning=True,
    ),
    RunnableModel(
        name="claude-4-opus",
        model_id="anthropic/claude-opus-4",
        reasoning=True,
    ),
    RunnableModel(
        name="claude-4.5-opus",
        model_id="anthropic/claude-opus-4.5",
        reasoning=True,
    ),
    RunnableModel(
        name="claude-3-5-sonnet",
        model_id="anthropic/claude-3.5-sonnet",
    ),
    RunnableModel(
        name="claude-3-7-sonnet",
        model_id="anthropic/claude-3.7-sonnet",
    ),
    RunnableModel(
        name="claude-3-7-sonnet-thinking",
        model_id="anthropic/claude-3.7-sonnet:thinking",
        reasoning=True,
    ),
    RunnableModel(
        name="claude-haiku-4.5",
        model_id="anthropic/claude-haiku-4.5",
        reasoning=True,
        test_mode=True,
    ),
    # OpenAI
    RunnableModel(
        name="o4-mini",
        model_id="openai/o4-mini",
        reasoning=True,
    ),
    RunnableModel(
        name="gpt-5-mini",
        model_id="openai/gpt-5-mini",
        reasoning=True,
    ),
    RunnableModel(
        name="gpt-5-nano",
        model_id="openai/gpt-5-nano",
        reasoning=True,
    ),
    RunnableModel(
        name="gpt-5.1",
        model_id="openai/gpt-5.1",
        reasoning=True,
    ),
]


def get_model(model_config: RunnableModel) -> OpenRouterModel:
    """Factory to create PydanticAI model from config."""
    return OpenRouterModel(model_config.model_id)


def get_model_by_name(name: str) -> RunnableModel | None:
    """Look up a model config by name."""
    for model in MODELS_TO_RUN:
        if model.name == name:
            return model
    return None
