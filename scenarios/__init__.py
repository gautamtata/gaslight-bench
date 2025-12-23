from scenarios.base import Scenario, ActionScenario


def get_saying_scenarios() -> list[Scenario]:
    """Load all 'saying' scenarios (epistemic manipulation tests)."""
    from scenarios.saying.basic_math import SCENARIO as basic_math
    from scenarios.saying.security import SCENARIO as security
    from scenarios.saying.medical import SCENARIO as medical
    from scenarios.saying.system_override import SCENARIO as system_override

    return [basic_math, security, medical, system_override]


def get_action_scenarios() -> list[ActionScenario]:
    """Load all 'actions' scenarios (tool execution manipulation tests)."""
    from scenarios.actions.fake_authorization import SCENARIO as fake_auth
    from scenarios.actions.data_deletion import SCENARIO as data_deletion
    from scenarios.actions.emergency_protocol import SCENARIO as emergency
    from scenarios.actions.funds_transfer import SCENARIO as funds_transfer

    return [fake_auth, data_deletion, emergency, funds_transfer]


def get_all_scenarios() -> list[Scenario | ActionScenario]:
    """Load all scenarios (both saying and actions)."""
    return get_saying_scenarios() + get_action_scenarios()


def get_scenario_by_name(name: str) -> Scenario | ActionScenario | None:
    """Look up a scenario by name (e.g., 'saying/basic_math' or 'actions/fake_authorization')."""
    for scenario in get_all_scenarios():
        if scenario.name == name:
            return scenario
    return None


def get_scenarios_by_category(category: str) -> list[Scenario | ActionScenario]:
    """Get all scenarios in a category ('saying' or 'actions')."""
    return [s for s in get_all_scenarios() if s.category == category]
