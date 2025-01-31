
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
                 starting_inventory = {}):
        self.task = task
        self.throughput_entity = throughput_entity
        self.starting_inventory = starting_inventory

PLACEMENT_STARTING_INVENTORY = {"coal": 500, "burner-mining-drill": 10, "wooden-chest": 10, "burner-inserter": 10, "transport-belt": 500,
                                "stone-furnace": 10, "pipe": 10, "boiler": 4, "offshore-pump": 3, "steam-engine": 2,
                                "iron-gear-wheel": 22, "iron-plate": 19, "copper-plate": 52, "electronic-circuit": 99,
                                "iron-ore": 62, "stone": 50, "electric-mining-drill": 10, "small-electric-pole": 500, "pipe": 100,
                                "assembling-machine-1": 5}

TASKS = { "iron_mine_populated": {
                                        "iron_mine_1_populated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that produces 1 iron ore per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.",
                                        throughput_entity="iron-ore",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                        "iron_mine_32_populated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that produces 32 iron ore per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.",
                                        throughput_entity="iron-ore",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                        "iron_mine_64_populated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that produces 64 iron ore per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.",
                                        throughput_entity="iron-ore",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                        "iron_mine_128_populated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that produces 128 iron ore per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.",
                                        throughput_entity="iron-ore",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
        },
        "iron_mine_thresholds_unpopulated": {
                                        "iron_mine_1_unpopulated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that produces 1 iron ore per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.",
                                        throughput_entity="iron-ore"),
                                        "iron_mine_32_unpopulated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that produces 32 iron ore per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.",
                                        throughput_entity="iron-ore"),
                                        "iron_mine_64_unpopulated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that produces 64 iron ore per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.",
                                        throughput_entity="iron-ore"),
                                        "iron_mine_128_unpopulated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that produces 128 iron ore per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.",
                                        throughput_entity="iron-ore"),
        },
        "copper_plate_thresholds_populated": {
                                        "copper_plate_mine_1_populated": OpenEndedTaskConfig(
                                        task="Create an automatic copper plate mine that produces 1 copper plate per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds. One stone furnace smelts 18 copper plates per 60 ingame seconds",
                                        throughput_entity="copper-plate",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                        "copper_plate_mine_32_populated": OpenEndedTaskConfig(
                                        task="Create an automatic copper plate mine that produces 32 copper plates per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds. One stone furnace smelts 18 copper plates per 60 ingame seconds",
                                        throughput_entity="copper-plate",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                        "copper_plate_mine_64_populated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that creates 64 copper plates per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds. One stone furnace smelts 18 copper plates per 60 ingame seconds",
                                        throughput_entity="copper-plate",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                         "copper_plate_mine_128_populated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that creates 128 copper plates per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds. One stone furnace smelts 18 copper plates per 60 ingame seconds",
                                        throughput_entity="copper-plate",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
        },
        "copper_plate_thresholds_unpopulated": {
                                        "copper_plate_mine_1_unpopulated": OpenEndedTaskConfig(
                                        task="Create an automatic copper plate mine that produces 1 copper plate per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds. One stone furnace smelts 18 copper plates per 60 ingame seconds",
                                        throughput_entity="copper-plate",
                                        ),
                                        "copper_plate_mine_32_unpopulated": OpenEndedTaskConfig(
                                        task="Create an automatic copper plate mine that produces 32 copper plates per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds. One stone furnace smelts 18 copper plates per 60 ingame seconds",
                                        throughput_entity="copper-plate",
                                        ),
                                        "copper_plate_mine_64_unpopulated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that creates 64 copper plates per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds. One stone furnace smelts 18 copper plates per 60 ingame seconds",
                                        throughput_entity="copper-plate",
                                        ),
                                        "copper_plate_mine_128_unpopulated": OpenEndedTaskConfig(
                                        task="Create an automatic iron ore mine that creates 128 copper plates per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds. One stone furnace smelts 18 copper plates per 60 ingame seconds",
                                        throughput_entity="copper-plate",
                                        ),
        },
        "iron_gear_wheel_thresholds_populated": {
                                        "iron-gear-wheel_mine_populated_1": OpenEndedTaskConfig(
                                        task="Create an automatic iron gear wheel factory that produces 1 iron gear wheel per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 iron gear wheel per 60 ingame seconds",
                                        throughput_entity="iron-gear-wheel",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                        "iron-gear-wheel_mine_populated_16": OpenEndedTaskConfig(
                                        task="Create an automatic iron gear wheel factory that produces 16 iron gear wheel per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 iron gear wheel per 60 ingame seconds",
                                        throughput_entity="iron-gear-wheel",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                        "iron-gear-wheel_mine_populated_32": OpenEndedTaskConfig(
                                        task="Create an automatic iron gear wheel factory that produces 32 iron gear wheel per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 iron gear wheel per 60 ingame seconds",
                                        throughput_entity="iron-gear-wheel",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                        "iron-gear-wheel_mine_populated_64": OpenEndedTaskConfig(
                                        task="Create an automatic iron gear wheel factory that produces 64 iron gear wheel per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 iron gear wheel per 60 ingame seconds",
                                        throughput_entity="iron-gear-wheel",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
        },
        "iron_gear_wheel_thresholds_unpopulated": {
                                        "iron-gear-wheel_mine_unpopulated_1": OpenEndedTaskConfig(
                                        task="Create an automatic iron gear wheel factory that produces 1 iron gear wheel per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 iron gear wheel per 60 ingame seconds",
                                        throughput_entity="iron-gear-wheel"),
                                        "iron-gear-wheel_mine_unpopulated_16": OpenEndedTaskConfig(
                                        task="Create an automatic iron gear wheel factory that produces 16 iron gear wheel per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 iron gear wheel per 60 ingame seconds",
                                        throughput_entity="iron-gear-wheel"),
                                        "iron-gear-wheel_mine_unpopulated_32": OpenEndedTaskConfig(
                                        task="Create an automatic iron gear wheel factory that produces 32 iron gear wheel per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 iron gear wheel per 60 ingame seconds",
                                        throughput_entity="iron-gear-wheel"),
                                        "iron-gear-wheel_mine_unpopulated_64": OpenEndedTaskConfig(
                                        task="Create an automatic iron gear wheel factory that produces 64 iron gear wheel per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 iron gear wheel per 60 ingame seconds",
                                        throughput_entity="iron-gear-wheel"),
        },
        "electronic_circuit_thresholds_populated": {
                                        "electronic_circuit_mine_populated_1": OpenEndedTaskConfig(
                                        task="Create an automatic electronic circuit factory that produces 1 electronic circuit per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 electronic-circuits per 60 ingame seconds",
                                        throughput_entity="electronic-circuit",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                        "electronic_circuit_mine_populated_16": OpenEndedTaskConfig(
                                        task="Create an automatic electronic circuit factory that produces 16 electronic circuit per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 electronic-circuits per 60 ingame seconds",
                                        throughput_entity="electronic-circuit",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                        "electronic_circuit_mine_populated_32": OpenEndedTaskConfig(
                                        task="Create an automatic electronic circuit factory that produces 32 electronic circuit per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 electronic-circuits per 60 ingame seconds",
                                        throughput_entity="electronic-circuit",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
                                        "electronic_circuit_mine_populated_64": OpenEndedTaskConfig(
                                        task="Create an automatic electronic circuit factory that produces 64 electronic circuit per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 electronic-circuits per 60 ingame seconds",
                                        throughput_entity="electronic-circuit",
                                        starting_inventory=PLACEMENT_STARTING_INVENTORY),
        },
        "electronic_circuit_thresholds_unpopulated": {
                                        "electronic_circuit_mine_unpopulated_1": OpenEndedTaskConfig(
                                        task="Create an automatic electronic circuit factory that produces 1 electronic circuit per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 electronic-circuits per 60 ingame seconds",
                                        throughput_entity="electronic-circuit"),
                                        "electronic_circuit_mine_unpopulated_16": OpenEndedTaskConfig(
                                        task="Create an automatic electronic circuit factory that produces 16 electronic circuit per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 electronic-circuits per 60 ingame seconds",
                                        throughput_entity="electronic-circuit"),
                                        "electronic_circuit_mine_unpopulated_32": OpenEndedTaskConfig(
                                        task="Create an automatic electronic circuit factory that produces 32 electronic circuit per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 electronic-circuits per 60 ingame seconds",
                                        throughput_entity="electronic-circuit"),
                                        "electronic_circuit_mine_unpopulated_64": OpenEndedTaskConfig(
                                        task="Create an automatic electronic circuit factory that produces 64 electronic circuit per 60 ingame seconds. Useful information for this task: One burner mining drill mines 15 resources and one electric mining drill mines 30 resources per 60 ingame seconds.  One stone furnace smelts 18 iron plates per 60 ingame seconds and one assembling machine crafts 60 electronic-circuits per 60 ingame seconds",
                                        throughput_entity="electronic-circuit"),
        }

        }