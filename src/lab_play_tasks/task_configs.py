from typing import Any, Dict, Type


class TaskConfig:
    """Configuration for a task"""
    def __init__(self,
                 task: str,
                 check_for_completion = True,
                 check_dicts = {},
                 starting_inventory = {}):
        self.task = task
        self.check_for_completion = check_for_completion
        self.check_dicts = check_dicts
        self.starting_inventory = starting_inventory

class OpenEndedTaskConfig:
    """Configuration for a task"""
    def __init__(self,
                 task: str,
                 throughput_entity: str,
                 quota: int,
                 trace_length: int,
                 starting_inventory = {},
                 starting_setup_code_location = None):
        self.task = task
        self.throughput_entity = throughput_entity
        self.starting_inventory = starting_inventory
        self.quota = quota
        self.trace_length = trace_length
        self.starting_setup_code_location = starting_setup_code_location
        self.starting_game_state = None
        self.starting_scenario_code = ""
        self.starting_scenario_logs = "" 

    def _to_dict(self) -> Dict[str, Any]:
        return {
            "task": self.task,
            "throughput_entity": self.throughput_entity,
            "quota": self.quota,
            "trace_length": self.trace_length,
            "starting_inventory": self.starting_inventory,
            "starting_setup_code_location": self.starting_setup_code_location,
            "initial_state": self.starting_game_state.to_raw()
        }

LAB_PLAY_POPULATED_STARTING_INVENTORY = {"coal": 500, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 500,
                                "stone-furnace": 10, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 500, "pipe": 100,
                                "assembling-machine-1": 5}
