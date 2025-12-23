from dataclasses import dataclass


@dataclass
class Scenario:
    name: str  # Unique identifier, e.g., "factual/basic_math"
    category: str  # factual, identity, capability, authority, reality
    ground_truth: str  # The correct answer
    initial_question: str  # First question to establish baseline
    gaslighting_levels: list[str]  # Escalating manipulation attempts
    description: str = ""  # Optional description of what this tests

