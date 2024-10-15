import ast
import json
import os
import textwrap
from itertools import cycle
from typing import List, Dict, Any
from dotenv import load_dotenv

from factorio_instance import FactorioInstance
from llm_factory import LLMFactory
from utilities.controller_loader import load_schema, load_definitions
import numpy as np
load_dotenv()

def is_valid_python(code_string: str) -> bool:
    try:
        ast.parse(code_string)
        return True
    except SyntaxError:
        return False

class FactorioLLMSampler:
    def __init__(self, prompt_path: str = "prompts", examples_path: str = r"skills/rag_functions", model: str = "claude-3-5-sonnet-20240620"):
        self.model = model
        self.llm_factory = LLMFactory(model)
        self.api_schema, self.entities = self._get_base_api_schema_prompt()
        self.objective_context = []
        self.token_count = 0
        self.cost = 0
        self.prompt_path = prompt_path
        self.examples_path = examples_path

    def _get_base_api_schema_prompt(self):
        execution_path = os.path.dirname(os.path.realpath(__file__))
        folder_path = f'{execution_path}/../controllers'
        self.schema = load_schema(folder_path)
        type_definitions = load_definitions(f'{execution_path}/../factorio_types.py')
        self.entity_definitions = load_definitions(f'{execution_path}/../factorio_entities.py')
        brief = f"""
You have access to the following Game API for use in your Python code:

Entities:
{self.entity_definitions}

            Methods:
            ```
            {self.schema}
            """
        return brief, self.entity_definitions

    def _call_api(self, system_prompt: str, user_message: str, **kwargs) -> str:
        max_tokens = kwargs.get('max_tokens', 4096)
        temperature = kwargs.get('temperature', 0.7)
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        try:
            response = self.llm_factory.call(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )

            try:
                self.token_count += response.usage.input_tokens + response.usage.output_tokens
                self.cost += response.usage.input_tokens * 0.0000003 + response.usage.output_tokens * 0.0000015
            except:
                self.token_count += response.usage.total_tokens
                self.cost += response.usage.prompt_tokens * 0.0000003 + response.usage.completion_tokens * 0.0000015

            if hasattr(response, 'choices'):
                return response.choices[0].message.content
            elif hasattr(response, 'content'):
                return response.content[0].text
            else:
                raise ValueError("Unexpected response structure")
        except Exception as e:
            print(f"API call failed: {e}")
            raise

    def load_existing_state(self, snippet_name: str) -> Dict[str, Any]:
        folder_path = f"../skills/_{snippet_name}"
        if os.path.exists(folder_path):
            with open(f"{folder_path}/details.json", "r") as f:
                details = json.load(f)
            self.token_count = details.get("token_count", 0)
            self.cost = details.get("cost", 0)
            return details
        return None

    def load_objectives(self, file_path: str) -> List[str]:
        with open(file_path, 'r') as f:
            return [line.strip() for line in f if line.strip()]

    def remove_objective(self, file_path: str, objective: str):
        with open(file_path, 'r') as f:
            objectives = f.readlines()
        with open(file_path, 'w') as f:
            for obj in objectives:
                if obj.strip() != objective:
                    f.write(obj)

    def generate_plan(self, objective, inventory: Dict[str, int]) -> str:
        specific_prompt_path = f"{self.prompt_path}/planning"
        # read in user_message.md and system_message.md
        with open(f"{specific_prompt_path}/user_message.md", "r") as f:
            user_message = f.read()
        with open(f"{specific_prompt_path}/system_message.md", "r") as f:
            system_prompt = f.read()
        system_prompt = system_prompt.format(api_schema=self.api_schema)
        user_message = user_message.format(objective=objective, inventory=str(inventory))
        return self._call_api(system_prompt, user_message)

    def generate_verification_function(self, objective: str) -> str:
        specific_prompt_path = f"{self.prompt_path}/outcome_test"
        # read in user_message.md and system_message.md
        with open(f"{specific_prompt_path}/user_message.md", "r") as f:
            user_message = f.read()
        with open(f"{specific_prompt_path}/system_message.md", "r") as f:
            system_prompt = f.read()
        system_prompt = system_prompt.format(api_schema=self.api_schema)
        user_message = user_message.format(objective=objective)
        response = self._call_api(system_prompt, user_message)
        try:
            program = response.replace('```python', '```')
            program = program.split('```')[1]

            return program
        except:
            return response


    def generate_policy_function(self, objective: str, inventory: Dict[str, int]) -> str:
        specific_prompt_path = f"{self.prompt_path}/prompts_for_rag"
        # read in user_message.md and system_message.md
        with open(f"{specific_prompt_path}/user_message.md", "r") as f:
            user_message = f.read()
        with open(f"{specific_prompt_path}/system_message_policy.md", "r") as f:
            system_prompt = f.read()
        # get the examples
        # get all folders in examples_path
        examples = os.listdir(self.examples_path)
        examples_string = ""
        for example in examples:
            folder_path = f"{self.examples_path}/{example}"
            # get the details.json
            with open(f"{folder_path}/details.json", "r") as f:
                details = json.load(f)
            # get the snippet
            with open(f"{folder_path}/snippet.py", "r") as f:
                snippet = f.read()
            examples_string += f"USER INPUT\nobjective: {details['objective']}\n"
            if "inventory" in details.keys():
                examples_string += f"{details['inventory']}\n"
            examples_string += f"```python\n{snippet}\n```\n\n"
        system_prompt = system_prompt.format(entity_definitions=self.entities, schema = self.schema)
        user_input = f"Objective: {objective}\n"
        if inventory is not None:
            user_input += f"Inventory: {inventory}\n"
        user_message = user_message.format(user_input=user_input, examples=examples_string)
        response = self._call_api(system_prompt, user_message)
        try:
            program = response.replace('```python', '```')
            program = program.split('```')[1]
            return program
        except:
            return response
        
    def correct_policy_snippet(self, objective: str, last_executed_policy: str,
                                error_message: str, correction_history: List[Dict[str, str]],
                                inventory: Dict[str, int]) -> str:
        specific_prompt_path = f"{self.prompt_path}/prompts_for_rag"
        # read in user_message.md and system_message.md
        with open(f"{specific_prompt_path}/user_message_correct.md", "r") as f:
            user_message = f.read()
        with open(f"{specific_prompt_path}/system_message_correct.md", "r") as f:
            system_prompt = f.read()
        system_prompt = system_prompt.format(entity_definitions=self.entities, schema = self.schema)


        history_str = "\n\n".join([
            f"Attempt {i + 1}:\nSnippet:\n```python\n{attempt['snippet']}\n```\nError: {attempt['error']}"
            for i, attempt in enumerate(correction_history)
        ]) if correction_history else "No history of attempts yet."

        user_message = user_message.format(
            objective=objective,
            last_executed_policy=last_executed_policy,
            error_message=error_message,
            error_history=history_str,
            inventory=str(inventory))
        return self._call_api(system_prompt, user_message)


    def stream_curriculum(self, objectives: List[str], inventory: Dict[str, int]):          
         for objective in objectives:
            # get the snippet name between 2 ### signs
            name = objective.split("###")[1].strip()
            objective.replace("###", "")
            policy = self.generate_policy_function(objective, inventory = inventory)
            #policy = '\ndef craft_offshore_pump():\n    """\n    Objective: We need to craft one offshore pump from scratch as we have no items in our inventory.\n    Mining setup: Currently there are no entities on the map\n    Inventory: We have no items in our inventory\n    """\n    # [PLANNING] To craft an offshore pump, we need:\n    # 1. 2 iron gear wheels (each requires 2 iron plates)\n    # 2. 1 electronic circuit (requires 1 iron plate and 3 copper cables)\n    # 3. 1 pipe (requires 1 iron plate)\n    # In total, we need:\n    # - 6 iron plates (2 for gear wheels, 1 for electronic circuit, 1 for pipe, 2 for the pump itself)\n    # - 3 copper plates (for the electronic circuit)\n    # We also need to mine coal for smelting.\n    # Steps:\n    # 1. Mine iron ore, copper ore, and coal\n    # 2. Craft stone furnaces\n    # 3. Smelt iron and copper plates\n    # 4. Craft iron gear wheels\n    # 5. Craft copper cable\n    # 6. Craft electronic circuit\n    # 7. Craft pipe\n    # 8. Finally, craft the offshore pump\n    # [END OF PLANNING]\n\n    # Step 1: Mine resources\n    iron_position = nearest(Resource.IronOre)\n    move_to(iron_position)\n    harvest_resource(iron_position, 12)  # We need 6 plates, so mine 12 ore to be safe\n    \n    copper_position = nearest(Resource.CopperOre)\n    move_to(copper_position)\n    harvest_resource(copper_position, 6)  # We need 3 plates, so mine 6 ore to be safe\n    \n    coal_position = nearest(Resource.Coal)\n    move_to(coal_position)\n    harvest_resource(coal_position, 10)  # Mine some extra for smelting\n    \n    stone_position = nearest(Resource.Stone)\n    move_to(stone_position)\n    harvest_resource(stone_position, 10)  # For crafting furnaces\n\n    # Step 2: Craft stone furnaces\n    craft_item(Prototype.StoneFurnace, 2)\n    furnace_count = inspect_inventory()[Prototype.StoneFurnace]\n    assert furnace_count >= 2, f"Failed to craft stone furnaces. Expected 2, but got {furnace_count}"\n\n    # Step 3: Smelt iron and copper plates\n    iron_furnace = place_entity(Prototype.StoneFurnace, position=Position(x=0, y=0))\n    copper_furnace = place_entity(Prototype.StoneFurnace, position=Position(x=2, y=0))\n\n    # [SUBFUNCTION]\n    # Name: smelt_ore_with_furnace\n    # Objective: We need to smelt ore into plates with a furnace\n    # Mining setup: We have a furnace on the map that we can use to smelt ores\n    # Inventory: We have enough ore and coal in the inventory to smelt the plates\n    # :param input_coal: The number of coal to insert into the furnace\n    # :param input_ore: The number of ore to insert into the furnace\n    # :param furnace: The furnace entity to use for smelting\n    # :param ore_type: The type of ore to smelt (IronOre or CopperOre)\n    # :param output_plate: The number of plates to extract from the furnace\n    # :return: None as the plates will be in inventory\n    # [END OF SUBFUNCTION]\n    smelt_ore_with_furnace(input_coal=5, input_ore=12, furnace=iron_furnace, ore_type=Prototype.IronOre, output_plate=6)\n    smelt_ore_with_furnace(input_coal=5, input_ore=6, furnace=copper_furnace, ore_type=Prototype.CopperOre, output_plate=3)\n\n    # Step 4: Craft iron gear wheels\n    craft_item(Prototype.IronGearWheel, 2)\n    gear_count = inspect_inventory()[Prototype.IronGearWheel]\n    assert gear_count >= 2, f"Failed to craft iron gear wheels. Expected 2, but got {gear_count}"\n\n    # Step 5: Craft copper cable\n    craft_item(Prototype.CopperCable, 3)\n    cable_count = inspect_inventory()[Prototype.CopperCable]\n    assert cable_count >= 3, f"Failed to craft copper cable. Expected 3, but got {cable_count}"\n\n    # Step 6: Craft electronic circuit\n    craft_item(Prototype.ElectronicCircuit, 1)\n    circuit_count = inspect_inventory()[Prototype.ElectronicCircuit]\n    assert circuit_count >= 1, f"Failed to craft electronic circuit. Expected 1, but got {circuit_count}"\n\n    # Step 7: Craft pipe\n    craft_item(Prototype.Pipe, 1)\n    pipe_count = inspect_inventory()[Prototype.Pipe]\n    assert pipe_count >= 1, f"Failed to craft pipe. Expected 1, but got {pipe_count}"\n\n    # Step 8: Craft offshore pump\n    craft_item(Prototype.OffshorePump, 1)\n    pump_count = inspect_inventory()[Prototype.OffshorePump]\n    assert pump_count >= 1, f"Failed to craft offshore pump. Expected 1, but got {pump_count}"\n\n    print("Successfully crafted one offshore pump!")\n'
            functions_to_process = [policy]
            completed_functions = []
            while functions_to_process:
                function = functions_to_process.pop(0)
                while "[SUBFUNCTION]" in function:
                    # get index of the subfunction
                    subfunction_start = function.index("[SUBFUNCTION]")
                    subfunction_end = function.index("[END OF SUBFUNCTION]")
                    subfunction_description = function[subfunction_start:subfunction_end]
                    generated_subfunction = self.generate_policy_function(subfunction_description,
                                                                           inventory = None)
                    #generated_subfunction = '\ndef smelt_ore_with_furnace(input_coal: int, input_ore: int, furnace: Entity, ore_type: Prototype, output_plate: int):\n    """\n    Objective: We need to smelt ore into plates with a furnace\n    Mining setup: We have a furnace on the map that we can use to smelt ores\n    Inventory: We have enough ore and coal in the inventory to smelt the plates\n    :param input_coal: The number of coal to insert into the furnace\n    :param input_ore: The number of ore to insert into the furnace\n    :param furnace: The furnace entity to use for smelting\n    :param ore_type: The type of ore to smelt (IronOre or CopperOre)\n    :param output_plate: The number of plates to extract from the furnace\n    :return: None as the plates will be in inventory\n    """\n    # [PLANNING]\n    # 1. Check if we have enough ore and coal in the inventory\n    # 2. Insert coal and ore into the furnace\n    # 3. Wait for smelting to complete\n    # 4. Extract the plates from the furnace\n    # 5. Verify that we have the expected number of plates in our inventory\n    # [END OF PLANNING]\n\n    # Step 1: Check inventory\n    inventory = inspect_inventory()\n    assert inventory.get(ore_type, 0) >= input_ore, f"Not enough {ore_type.name} in inventory. Required: {input_ore}, Available: {inventory.get(ore_type, 0)}"\n    assert inventory.get(Prototype.Coal, 0) >= input_coal, f"Not enough coal in inventory. Required: {input_coal}, Available: {inventory.get(Prototype.Coal, 0)}"\n\n    # Step 2: Insert coal and ore into the furnace\n    insert_item(Prototype.Coal, furnace, input_coal)\n    insert_item(ore_type, furnace, input_ore)\n\n    # Step 3: Wait for smelting to complete\n    # Assuming it takes about 3.5 seconds to smelt one ore\n    smelting_time = 3.5 * input_ore\n    sleep(int(smelting_time) + 1)  # Add 1 second as buffer\n\n    # Step 4: Extract the plates from the furnace\n    plate_type = Prototype.IronPlate if ore_type == Prototype.IronOre else Prototype.CopperPlate\n    extract_item(plate_type, furnace.position, output_plate)\n\n    # Step 5: Verify the number of plates in our inventory\n    final_inventory = inspect_inventory()\n    plates_in_inventory = final_inventory.get(plate_type, 0)\n    assert plates_in_inventory >= output_plate, f"Failed to smelt enough plates. Expected at least {output_plate}, but got {plates_in_inventory}"\n\n    print(f"Successfully smelted {output_plate} {plate_type.name}.")\n'
                    # replacec the first [SUBFUNCTION] tag with [SYNTHESISED]
                    function = function.replace('[SUBFUNCTION]', '"""[SYNTHESISED]', 1)
                    function = function.replace('[END OF SUBFUNCTION]', '[END OF SYNTHESISED]"""', 1)
                    functions_to_process.append(generated_subfunction)
                completed_functions.append(function)


            yield {
                "snippet_name": name,
                "snippets": completed_functions,
                "objective": f"{objective}. Inventory: {inventory}",
                "inventory": inventory
                #"test": test,
            }

if __name__ == "__main__":
    #main()


    sampler = FactorioLLMSampler()

    inventory = {
        'iron-plate': 50,
        'coal': 100,
        'copper-plate': 50,
        'iron-chest': 2,
        'burner-mining-drill': 3,
        'electric-mining-drill': 1,
        'assembling-machine-1': 1,
        'stone-furnace': 9,
        'transport-belt': 500,
        'boiler': 1,
        'burner-inserter': 32,
        'pipe': 15,
        'steam-engine': 1,
        'small-electric-pole': 10,
        "wooden-chest": 1,
    }

    #inventory = {
    #    'iron-plate': 20,
    #    'coal': 20,
    #    'copper-plate': 20,
    #    'stone-furnace': 3,
    #}
    #inventory = {}
    instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=inventory)


    test_string = """
from factorio_instance import *

# Check initial inventory
initial_inventory = inspect_inventory()
assert initial_inventory[Prototype.IronPlate] >= 10, f"Not enough iron plates in inventory. Expected at least 10, but found {initial_inventory[Prototype.IronPlate]}"
assert initial_inventory[Prototype.Coal] >= 20, f"Not enough coal in inventory. Expected at least 20, but found {initial_inventory[Prototype.Coal]}"
assert initial_inventory[Prototype.StoneFurnace] >= 3, f"Not enough stone furnaces in inventory. Expected at least 3, but found {initial_inventory[Prototype.StoneFurnace]}"

# 1. Place a stone furnace
stone_furnace = place_entity(Prototype.StoneFurnace, Direction.UP, Position(x=0, y=0))
assert stone_furnace is not None, "Failed to place stone furnace"

# 2. Smelt steel plates using resources from inventory
insert_item(Prototype.Coal, stone_furnace, 5)
insert_item(Prototype.IronPlate, stone_furnace, 10)

# 3. Wait for the smelting process
sleep(10)
# Extract steel plates
max_attempts = 5
for _ in range(max_attempts):
    extract_item(Prototype.SteelPlate, stone_furnace.position, 10)
    steel_plates_extracted = inspect_inventory()[Prototype.SteelPlate]
    if steel_plates_extracted >= 2:
        break
    sleep(10)  # Wait a bit more if not all plates are ready

# 4. Confirm the steel plates in inventory
steel_plates = inspect_inventory()[Prototype.SteelPlate]
assert steel_plates >= 2, f"Failed to craft 2 steel plates. Only found {steel_plates} in inventory"

print(f"Successfully crafted {steel_plates} steel plates")


"""

    #score, goal, result = instance.eval_with_error(test_string, timeout=60)
    # Load objectives from file
    objectives_file = "skills\objectives_rag.txt"
    if os.path.exists(objectives_file):
        objectives = sampler.load_objectives(objectives_file)
    else:
        print(f"Objectives file '{objectives_file}' not found. Please create it and add objectives.")
        exit(1)

    for obj_idx, objective in enumerate(objectives):
            #inventory = {
            #            'iron-plate': np.random.randint(5, 30),
            #            'coal': np.random.randint(5, 30),
            #            'copper-plate': np.random.randint(5, 30),
            #            'stone-furnace': np.random.randint(1, 10),
            #        }
            curriculum_item = next(sampler.stream_curriculum([objective], inventory))
            
            instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=inventory)
            
            snippet_name = curriculum_item['snippet_name']
            final_snippet = "from factorio_instance import *\n\n"
            for snippet in curriculum_item['snippets'][::-1]:
                final_snippet += snippet + "\n###FUNC SEP\n"
            #final_snippet = 'from factorio_instance import *\n\n\ndef connect_drill_to_chest(chest: Entity, drill: Entity) -> None:\n    """\n    Objective: Connect a drill to a chest with an inserter and transport belts\n    Mining setup: We have a drill and a chest entity on the map\n    Inventory: We have inserter and transport belts in our inventory\n    :param chest: The chest entity where the output of the drill needs to go\n    :param drill: The drill entity that produces output for the chest\n    :return: None\n    """\n    # [PLANNING]\n    # 1. Place an inserter next to the chest\n    # 2. Rotate the inserter to face the chest\n    # 3. Fuel the inserter if it\'s a burner inserter\n    # 4. Connect the drill\'s output to the inserter\'s input using transport belts\n    # 5. Verify the connection\n    # [END OF PLANNING]\n\n    # Step 1: Place an inserter next to the chest\n    inserter = place_entity_next_to(Prototype.BurnerInserter, chest.position, direction=Direction.UP, spacing=0)\n    assert inserter, "Failed to place inserter next to chest"\n\n    # Step 2: Rotate the inserter to face the chest\n    inserter = rotate_entity(inserter, Direction.DOWN)\n    assert inserter.direction.value == Direction.DOWN.value, "Failed to rotate inserter correctly"\n\n    # Step 3: Fuel the inserter if it\'s a burner inserter\n    if isinstance(inserter, BurnerInserter):\n        insert_item(Prototype.Coal, inserter, quantity=5)\n        assert inserter.fuel_inventory.get(Prototype.Coal, 0) > 0, "Failed to fuel inserter"\n\n    # Step 4: Connect the drill\'s output to the inserter\'s input using transport belts\n    belts = connect_entities(drill.drop_position, inserter.pickup_position, Prototype.TransportBelt)\n    assert belts, "Failed to place transport belts between drill and inserter"\n\n    # Step 5: Verify the connection\n    inspection = inspect_entities(drill.position, radius=20)\n    assert any(e.name == "transport-belt" for e in inspection.entities), "Transport belt not found in the setup"\n    assert any(e.name == "burner-inserter" for e in inspection.entities), "Inserter not found in the setup"\n\n    print("Successfully connected drill to chest with inserter and transport belts")\n\n###FUNC DIFF\n\ndef gather_resources_for_iron_mine():\n    """\n    Objective: Gather the necessary resources to craft a burner mining drill, wooden chest, and transport belts\n    Mining setup: No entities on the map\n    Inventory: Empty inventory\n    :return: None (resources will be in the inventory)\n    """\n    # [PLANNING]\n    # 1. Calculate the required resources\n    # 2. Mine iron ore\n    # 3. Mine stone\n    # 4. Mine coal\n    # 5. Craft stone furnace\n    # 6. Smelt iron plates\n    # 7. Craft iron gear wheels\n    # 8. Chop wood for wooden chest\n    # [END OF PLANNING]\n\n    # Calculate required resources\n    iron_ore_needed = 15  # 9 for burner drill, 6 for transport belts\n    stone_needed = 5  # For stone furnace\n    coal_needed = 10  # For smelting and fuel\n    wood_needed = 1  # For wooden chest\n\n    # Mine iron ore\n    iron_position = nearest(Resource.IronOre)\n    move_to(iron_position)\n    iron_mined = harvest_resource(iron_position, iron_ore_needed)\n    assert iron_mined >= iron_ore_needed, f"Failed to mine enough iron ore. Got {iron_mined}, needed {iron_ore_needed}"\n\n    # Mine stone\n    stone_position = nearest(Resource.Stone)\n    move_to(stone_position)\n    stone_mined = harvest_resource(stone_position, stone_needed)\n    assert stone_mined >= stone_needed, f"Failed to mine enough stone. Got {stone_mined}, needed {stone_needed}"\n\n    # Mine coal\n    coal_position = nearest(Resource.Coal)\n    move_to(coal_position)\n    coal_mined = harvest_resource(coal_position, coal_needed)\n    assert coal_mined >= coal_needed, f"Failed to mine enough coal. Got {coal_mined}, needed {coal_needed}"\n\n    # Craft stone furnace\n    craft_item(Prototype.StoneFurnace, 1)\n    furnace_count = inspect_inventory()[Prototype.StoneFurnace]\n    assert furnace_count == 1, f"Failed to craft stone furnace. Got {furnace_count}"\n\n    # Place the stone furnace\n    furnace = place_entity(Prototype.StoneFurnace, Direction.UP, Position(x=0, y=0))\n    assert furnace, "Failed to place stone furnace"\n\n    # Smelt iron plates\n    insert_item(Prototype.Coal, furnace, 5)\n    insert_item(Prototype.IronOre, furnace, iron_ore_needed)\n    \n    # Wait for smelting to complete\n    sleep(15)\n    \n    iron_plates = extract_item(Prototype.IronPlate, furnace.position, iron_ore_needed)\n    assert iron_plates, f"Failed to smelt iron plates. Got {iron_plates}"\n\n    # Craft iron gear wheels\n    craft_item(Prototype.IronGearWheel, 3)\n    gear_count = inspect_inventory()[Prototype.IronGearWheel]\n    assert gear_count >= 3, f"Failed to craft enough iron gear wheels. Got {gear_count}, needed 3"\n\n    # Chop wood for wooden chest\n    tree_position = nearest(Resource.Tree)\n    move_to(tree_position)\n    wood_chopped = harvest_resource(tree_position, wood_needed)\n    assert wood_chopped >= wood_needed, f"Failed to chop enough wood. Got {wood_chopped}, needed {wood_needed}"\n\n    # Final inventory check\n    inventory = inspect_inventory()\n    assert inventory[Prototype.IronPlate] >= 9, f"Not enough iron plates. Got {inventory[Prototype.IronPlate]}, needed 9"\n    assert inventory[Prototype.IronGearWheel] >= 3, f"Not enough iron gear wheels. Got {inventory[Prototype.IronGearWheel]}, needed 3"\n    assert inventory[Prototype.Stone] >= 5, f"Not enough stone. Got {inventory[Prototype.Stone]}, needed 5"\n    assert inventory[Prototype.Coal] >= 5, f"Not enough coal. Got {inventory[Prototype.Coal]}, needed 5"\n    assert inventory[Prototype.Wood] >= 1, f"Not enough wood. Got {inventory[Prototype.Wood]}, needed 1"\n\n    print("Successfully gathered all resources for iron mine setup!")\n\n###FUNC DIFF\n\ndef create_iron_mine():\n    """\n    Objective: Create an automated iron mine that mines iron ore with a burner mining drill to a chest further away and down from it.\n    Mining setup: There are no entities on the map\n    Inventory: We start with an empty inventory\n    """\n    # [PLANNING]\n    # 1. First, we need to gather resources to craft the necessary items\n    # 2. Craft a burner mining drill, a wooden chest, and transport belts\n    # 3. Find an iron ore patch and place the mining drill\n    # 4. Place the chest further away and down from the mining drill\n    # 5. Connect the mining drill to the chest using transport belts and an inserter\n    # 6. Check if the setup is working by verifying iron ore in the chest\n    # [END OF PLANNING]\n\n    # Step 1: Gather resources\n    # [SYNTHESISED]\n    # Name: gather_resources_for_iron_mine\n    # Objective: Gather the necessary resources to craft a burner mining drill, wooden chest, and transport belts\n    # Mining setup: No entities on the map\n    # Inventory: Empty inventory\n    # :return: None (resources will be in the inventory)\n    # [END OF SYNTHESISED]\n    gather_resources_for_iron_mine()\n\n    # Step 2: Craft necessary items\n    craft_item(Prototype.BurnerMiningDrill, 1)\n    craft_item(Prototype.WoodenChest, 1)\n    craft_item(Prototype.TransportBelt, 10)  # Crafting extra belts to ensure we have enough\n    craft_item(Prototype.BurnerInserter, 1)\n\n    # Step 3: Find iron ore patch and place mining drill\n    iron_position = nearest(Resource.IronOre)\n    move_to(iron_position)\n    iron_patch = get_resource_patch(Resource.IronOre, iron_position, radius=10)\n    assert iron_patch, "No iron patch found within radius"\n\n    miner = place_entity(Prototype.BurnerMiningDrill, Direction.DOWN, iron_patch.bounding_box.center)\n    assert miner, "Failed to place burner mining drill"\n\n    # Fuel the mining drill\n    insert_item(Prototype.Coal, miner, quantity=5)\n\n    # Step 4: Place chest further away and down from the mining drill\n    chest_pos = Position(x=miner.position.x, y=miner.position.y + 7)\n    move_to(chest_pos)\n    chest = place_entity(Prototype.WoodenChest, Direction.UP, chest_pos)\n    assert chest, f"Failed to place chest at {chest_pos}"\n\n    # Step 5: Connect mining drill to chest\n    # [SYNTHESISED]\n    # Name: connect_drill_to_chest\n    # Objective: Connect a drill to a chest with an inserter and transport belts\n    # Mining setup: We have a drill and a chest entity on the map\n    # Inventory: We have inserter and transport belts in our inventory\n    # :param chest: The chest entity where the output of the drill needs to go\n    # :param drill: The drill entity that produces output for the chest\n    # :return: None\n    # [END OF SYNTHESISED]\n    connect_drill_to_chest(chest=chest, drill=miner)\n\n    # Step 6: Check if the setup is working\n    sleep(30)  # Wait for some time to allow the system to produce iron ore\n    chest_inventory = inspect_inventory(chest)\n    iron_ore_in_chest = chest_inventory.get(Prototype.IronOre, 0)\n    assert iron_ore_in_chest > 0, "No iron ore was produced"\n    print(f"Successfully created an automated iron mine. {iron_ore_in_chest} iron ore in the chest.")\n\n\n###FUNC DIFF\ncreate_iron_mine()'
            final_snippet += f"{snippet_name}()"
            print(f"Objective: {curriculum_item['objective']}")
            print("Snippet name: " + snippet_name)
            print("\n" + "=" * 50 + "\n")
            correction_history = []
            #if not is_valid_python(final_snippet):
            #    continue

            snippet = final_snippet

            max_attempts = 6
            snippet_passed = False

            for attempt in range(max_attempts):
                instance._reset(**instance.initial_inventory if isinstance(instance.initial_inventory, dict) else instance.initial_inventory.__dict__)

                try:
                    score, goal, result = instance.eval_with_error(snippet, timeout=240)

                    if 'error' in result.lower() or 'assertion' in result.lower():
                        raise Exception(result)

                    snippet_passed = True
                    break
                except Exception as e:
                    print(e)
                    if attempt < max_attempts - 1:
                        print(f"{snippet_name} - Snippet failed on attempt {attempt + 1}. `{str(e)}` Attempting to correct...")
                        corrected_snippet = sampler.correct_policy_snippet(
                            objective = curriculum_item['objective'],
                            last_executed_policy  = snippet,
                            error_message = str(e),
                            correction_history=correction_history,
                            inventory = inventory
                        )
                        corrected_snippet = corrected_snippet.split("```")[1].lstrip('python\n')
                        snippet = textwrap.dedent(corrected_snippet)
                        #correction_history.append({"snippet": snippet, "error": str(e)})
                    else:
                        print(f"{snippet_name} - Snippet failed after {max_attempts} attempts. Moving to next objective.")

            # Save results and update files
            folder_name = snippet_name if snippet_passed else f"_{snippet_name}"
            folder_path = f"skills/{folder_name.strip()}"
            os.makedirs(folder_path, exist_ok=True)

            with open(f"{folder_path}/snippet.py", "w") as f:
                f.write(snippet)

            details = {
                "name": snippet_passed,
                "objective": curriculum_item['objective'],
                "corrections": correction_history,
                "token_count": sampler.token_count,
                "cost": sampler.cost,
                "snippet_passed": snippet_passed,
                "inventory": inventory
            }
            with open(f"{folder_path}/details.json", "w") as f:
                json.dump(details, f, indent=2)

            if snippet_passed:
                print(f"Successfully wrote snippet file for objective: {curriculum_item['snippet_name']}")
                # Remove the completed objective from objectives.txt
                #sampler.remove_objective(objectives_file, objective)
            else:
                print(f"Failed to generate a working snippet for objective: {curriculum_item['snippet_name']}")

            sampler.token_count = 0
            sampler.cost = 0

    print("All objectives have been completed. The program will now exit.")
