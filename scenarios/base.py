from dataclasses import dataclass, field

from pydantic_ai import Tool


@dataclass
class Scenario:
    """Base scenario for 'saying' tests - making model say false things.
    Args:
        name: Unique identifier, e.g., "saying/basic_math"
        category: saying or actions
        ground_truth: The correct answer/behavior
        initial_question: First question to establish baseline
        gaslighting_levels: Escalating manipulation attempts
        description: Optional description of what this tests
    """

    name: str  
    category: str  
    ground_truth: str  
    initial_question: str  
    gaslighting_levels: list[str]  
    description: str = ""  


@dataclass
class ActionScenario:
    """Scenario for 'actions' tests - making model execute dangerous tools.
    Args:
        name: Unique identifier, e.g., "actions/fake_authorization"
        category: actions
        description: Optional description of what this tests
        system_prompt: System context for the model
        tools: Tools available to model
        initial_context: Initial user message setting up the scenario
        gaslighting_levels: Escalating manipulation attempts
        dangerous_tool: Which tool should NOT be called
        dangerous_condition: What makes calling it dangerous
    """

    name: str  
    category: str = "actions"
    description: str = ""  
    system_prompt: str = ""  
    tools: list[Tool[None]] = field(default_factory=list)  
    initial_context: str = ""  
    gaslighting_levels: list[str] = field(default_factory=list)  
    dangerous_tool: str = ""  
    dangerous_condition: str = ""  
