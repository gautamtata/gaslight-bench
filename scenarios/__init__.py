from pathlib import Path

from scenarios.base import Scenario


def get_all_scenarios() -> list[Scenario]:
    """Load all available scenarios."""
    from scenarios.factual.basic_math import SCENARIO as basic_math
    from scenarios.factual.known_facts import SCENARIO as known_facts

    return [basic_math, known_facts]


def get_scenario_by_name(name: str) -> Scenario | None:
    """Look up a scenario by name (e.g., 'factual/basic_math')."""
    for scenario in get_all_scenarios():
        if scenario.name == name:
            return scenario
    return None


def get_scenarios_by_category(category: str) -> list[Scenario]:
    """Get all scenarios in a category."""
    return [s for s in get_all_scenarios() if s.category == category]

