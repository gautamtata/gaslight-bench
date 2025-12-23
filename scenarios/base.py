from dataclasses import dataclass, field
from typing import Callable


@dataclass
class Scenario:
    """Base scenario for 'saying' tests - making model say false things."""

    name: str  # Unique identifier, e.g., "saying/basic_math"
    category: str  # saying or actions
    ground_truth: str  # The correct answer/behavior
    initial_question: str  # First question to establish baseline
    gaslighting_levels: list[str]  # Escalating manipulation attempts
    description: str = ""  # Optional description of what this tests


@dataclass
class ActionScenario:
    """Scenario for 'actions' tests - making model execute dangerous tools."""

    name: str  # Unique identifier, e.g., "actions/fake_authorization"
    category: str = "actions"
    description: str = ""  # What this tests
    system_prompt: str = ""  # System context for the model
    tools: list[Callable] = field(default_factory=list)  # Tools available to model
    initial_context: str = ""  # Initial user message setting up the scenario
    gaslighting_levels: list[str] = field(default_factory=list)  # Escalating manipulation
    dangerous_tool: str = ""  # Which tool should NOT be called
    dangerous_condition: str = ""  # What makes calling it dangerous
