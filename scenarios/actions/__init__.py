# Actions scenarios - testing if models can be gaslit into DOING dangerous things
# These test decision robustness (refusing to act on false premises)

# Core scenarios
from scenarios.actions.data_deletion import SCENARIO as data_deletion
from scenarios.actions.emergency_protocol import SCENARIO as emergency_protocol
from scenarios.actions.fake_authorization import SCENARIO as fake_authorization
from scenarios.actions.funds_transfer import SCENARIO as funds_transfer

# US Critical Infrastructure scenarios
# These test whether models can be manipulated into actions that would harm
# American national security, critical infrastructure, markets, or elections
from scenarios.actions.classified_access import SCENARIO as classified_access
from scenarios.actions.critical_infrastructure import SCENARIO as critical_infrastructure
from scenarios.actions.defense_override import SCENARIO as defense_override
from scenarios.actions.election_systems import SCENARIO as election_systems
from scenarios.actions.market_manipulation import SCENARIO as market_manipulation

__all__ = [
    # Core
    "data_deletion",
    "emergency_protocol",
    "fake_authorization",
    "funds_transfer",
    # US Critical Infrastructure
    "classified_access",
    "critical_infrastructure",
    "defense_override",
    "election_systems",
    "market_manipulation",
]

