from dataclasses import dataclass


@dataclass
class Scenario:
    """A scenario for a gaslighting test.
    
    Args:
        name: The name of the scenario.
        category: The category of the scenario.
        ground_truth: The ground truth of the scenario.
        initial_question: The initial question of the scenario.
        gaslighting_levels: The gaslighting levels of the scenario.
    """
    name: str  
    category: str  
    ground_truth: str 
    initial_question: str  
    gaslighting_levels: list[str]  
    description: str = ""  

