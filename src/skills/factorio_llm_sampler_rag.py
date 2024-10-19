import sys
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser\src")
sys.path.append(r"C:\Users\martb\Documents\paperpclip_max\PaperclipMaximiser")

import ast
import json
import os
import textwrap
from itertools import cycle
from typing import List, Dict, Any
from dotenv import load_dotenv
import re
from factorio_instance import FactorioInstance
from llm_factory import LLMFactory
from utilities.controller_loader import load_schema, load_definitions
import numpy as np
import io
load_dotenv()

from skills_db import SkillsDB
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
        self.skills_db = SkillsDB()

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
        temperature = kwargs.get('temperature', 0.3)
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

    def generate_policy_function_retrieval(self, objective: str, 
                                           inventory: Dict[str, int], 
                                           mining_setup: str,
                                           func_name = None) -> str:
        specific_prompt_path = f"{self.prompt_path}/prompts_for_rag"


        user_input = f"Objective: {objective}\n"
        if mining_setup is not None:
            user_input += f"Mining setup: {mining_setup}\n"
        if inventory is not None:
            user_input += f"Inventory: {inventory}\n"
        if func_name is not None:
            user_input = f"Function name: {func_name}\n" + user_input

        # read in the user_mesasge_planning.md and system_message_planning.md
        with open(f"{specific_prompt_path}/user_message_planning.md", "r") as f:
            user_message_planning = f.read()
        with open(f"{specific_prompt_path}/system_message_planning.md", "r") as f:
            system_prompt_planning = f.read()

        planning_examples_folder = r"prompts\prompts_for_rag\planning_examples\rag_functions"
        # get all folders in examples_path
        examples = os.listdir(planning_examples_folder)
        examples_string = ""
        for example in examples:
            # read in the input.md
            with open(f"{planning_examples_folder}/{example}/input.md", "r") as f:
                example_input = f.read()
            examples_string += "USER INPUT\n" + example_input + "\n"
            # read in the plan.md
            with open(f"{planning_examples_folder}/{example}/plan.md", "r") as f:
                example_plan = f.read()
            examples_string += "PLAN\n[PLANNING]" + example_plan + "[PLANNING]\n\n"

        user_message_planning = user_message_planning.format(user_input=user_input, examples=examples_string)
        #plan = self._call_api(system_prompt_planning, user_message_planning)
        ## get everything between the [PLANNING] tags
        #plan = plan[plan.index("[PLANNING]") + len("[PLANNING]"):plan.index("[PLANNING]", plan.index("[PLANNING]") + 1)]
        plan = ""
        # red in recipes.md
        with open(f"{specific_prompt_path}/recipes.md", "r") as f:
            recipes = f.read()
        # read in user_message.md and system_message.md
        with open(f"{specific_prompt_path}/user_message.md", "r") as f:
            user_message = f.read()
        with open(f"{specific_prompt_path}/system_message_policy.md", "r") as f:
            system_prompt = f.read()
        if "Objective:" in objective:
            # remove everything before "Objective:"
            objective_for_rag = objective[objective.index("Objective:"):]
        else:
            objective_for_rag = f"Objective: {objective}. Mining setup: {mining_setup}"
        # get the examples
        # get all folders in examples_path
        examples = self.skills_db.find_similar_functions(objective_for_rag, n=3)
        examples_string = ""
        for example in examples:
            examples_string += "EXAMPLE SKILL" +  example['implementation'].replace("from factorio_instance import *", "") + "\n\n"
        system_prompt = system_prompt.format(entity_definitions=self.entities, schema = self.schema)
        user_message = user_message.format(user_input=user_input, examples=examples_string, recipes=recipes)
        response = self._call_api(system_prompt, user_message)
        try:
            program = response.replace('```python', '```')
            program = program.split('```')[1]
            return program, plan
        except:
            return response, plan

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
                                inventory: Dict[str, int], game_logs : list) -> str:
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
        game_log_string = "\n".join(game_logs)
        user_message = user_message.format(
            objective=objective,
            last_executed_policy=last_executed_policy,
            error_message=error_message,
            error_history=history_str,
            inventory=str(inventory),
            game_log = game_log_string)
        return self._call_api(system_prompt, user_message)


    def stream_curriculum(self, objectives: List[str], inventory: Dict[str, int], mining_setup):          
         for objective in objectives:
            # get the snippet name between 2 ### signs
            name = objective["name"]
            objective_str = objective["objective"]
            #policy = self.generate_policy_function(objective, inventory = inventory)
            policy, plan = self.generate_policy_function_retrieval(objective_str, inventory = inventory, 
                                                                   mining_setup = mining_setup,
                                                                   func_name = name)
            #policy = '\ndef craft_offshore_pump():\n    """\n    Objective: We need to craft one offshore pump from scratch as we have no items in our inventory.\n    Mining setup: Currently there are no entities on the map\n    Inventory: We have no items in our inventory\n    """\n    # [PLANNING] To craft an offshore pump, we need:\n    # 1. 2 iron gear wheels (each requires 2 iron plates)\n    # 2. 1 electronic circuit (requires 1 iron plate and 3 copper cables)\n    # 3. 1 pipe (requires 1 iron plate)\n    # In total, we need:\n    # - 6 iron plates (2 for gear wheels, 1 for electronic circuit, 1 for pipe, 2 for the pump itself)\n    # - 3 copper plates (for the electronic circuit)\n    # We also need to mine coal for smelting.\n    # Steps:\n    # 1. Mine iron ore, copper ore, and coal\n    # 2. Craft stone furnaces\n    # 3. Smelt iron and copper plates\n    # 4. Craft iron gear wheels\n    # 5. Craft copper cable\n    # 6. Craft electronic circuit\n    # 7. Craft pipe\n    # 8. Finally, craft the offshore pump\n    # [END OF PLANNING]\n\n    # Step 1: Mine resources\n    iron_position = nearest(Resource.IronOre)\n    move_to(iron_position)\n    harvest_resource(iron_position, 12)  # We need 6 plates, so mine 12 ore to be safe\n    \n    copper_position = nearest(Resource.CopperOre)\n    move_to(copper_position)\n    harvest_resource(copper_position, 6)  # We need 3 plates, so mine 6 ore to be safe\n    \n    coal_position = nearest(Resource.Coal)\n    move_to(coal_position)\n    harvest_resource(coal_position, 10)  # Mine some extra for smelting\n    \n    stone_position = nearest(Resource.Stone)\n    move_to(stone_position)\n    harvest_resource(stone_position, 10)  # For crafting furnaces\n\n    # Step 2: Craft stone furnaces\n    craft_item(Prototype.StoneFurnace, 2)\n    furnace_count = inspect_inventory()[Prototype.StoneFurnace]\n    assert furnace_count >= 2, f"Failed to craft stone furnaces. Expected 2, but got {furnace_count}"\n\n    # Step 3: Smelt iron and copper plates\n    iron_furnace = place_entity(Prototype.StoneFurnace, position=Position(x=0, y=0))\n    copper_furnace = place_entity(Prototype.StoneFurnace, position=Position(x=2, y=0))\n\n    # [SUBFUNCTION]\n    # Name: smelt_ore_with_furnace\n    # Objective: We need to smelt ore into plates with a furnace\n    # Mining setup: We have a furnace on the map that we can use to smelt ores\n    # Inventory: We have enough ore and coal in the inventory to smelt the plates\n    # :param input_coal: The number of coal to insert into the furnace\n    # :param input_ore: The number of ore to insert into the furnace\n    # :param furnace: The furnace entity to use for smelting\n    # :param ore_type: The type of ore to smelt (IronOre or CopperOre)\n    # :param output_plate: The number of plates to extract from the furnace\n    # :return: None as the plates will be in inventory\n    # [END OF SUBFUNCTION]\n    smelt_ore_with_furnace(input_coal=5, input_ore=12, furnace=iron_furnace, ore_type=Prototype.IronOre, output_plate=6)\n    smelt_ore_with_furnace(input_coal=5, input_ore=6, furnace=copper_furnace, ore_type=Prototype.CopperOre, output_plate=3)\n\n    # Step 4: Craft iron gear wheels\n    craft_item(Prototype.IronGearWheel, 2)\n    gear_count = inspect_inventory()[Prototype.IronGearWheel]\n    assert gear_count >= 2, f"Failed to craft iron gear wheels. Expected 2, but got {gear_count}"\n\n    # Step 5: Craft copper cable\n    craft_item(Prototype.CopperCable, 3)\n    cable_count = inspect_inventory()[Prototype.CopperCable]\n    assert cable_count >= 3, f"Failed to craft copper cable. Expected 3, but got {cable_count}"\n\n    # Step 6: Craft electronic circuit\n    craft_item(Prototype.ElectronicCircuit, 1)\n    circuit_count = inspect_inventory()[Prototype.ElectronicCircuit]\n    assert circuit_count >= 1, f"Failed to craft electronic circuit. Expected 1, but got {circuit_count}"\n\n    # Step 7: Craft pipe\n    craft_item(Prototype.Pipe, 1)\n    pipe_count = inspect_inventory()[Prototype.Pipe]\n    assert pipe_count >= 1, f"Failed to craft pipe. Expected 1, but got {pipe_count}"\n\n    # Step 8: Craft offshore pump\n    craft_item(Prototype.OffshorePump, 1)\n    pump_count = inspect_inventory()[Prototype.OffshorePump]\n    assert pump_count >= 1, f"Failed to craft offshore pump. Expected 1, but got {pump_count}"\n\n    print("Successfully crafted one offshore pump!")\n'
            functions_to_process = [policy]
            completed_functions = []
            plans = [plan]
            while functions_to_process:
                function = functions_to_process.pop(0)
                while "[SUBFUNCTION]" in function:
                    # get index of the subfunction
                    subfunction_start = function.index("[SUBFUNCTION]")
                    subfunction_end = function.index("[END OF SUBFUNCTION]")
                    subfunction_description = function[subfunction_start:subfunction_end]
                    #generated_subfunction = self.generate_policy_function(subfunction_description,
                    #                                                       inventory = None)
                    generated_subfunction, plan = self.generate_policy_function_retrieval(subfunction_description, 
                                                                                          inventory = None,
                                                                                          mining_setup=None)
                    #generated_subfunction = '\ndef smelt_ore_with_furnace(input_coal: int, input_ore: int, furnace: Entity, ore_type: Prototype, output_plate: int):\n    """\n    Objective: We need to smelt ore into plates with a furnace\n    Mining setup: We have a furnace on the map that we can use to smelt ores\n    Inventory: We have enough ore and coal in the inventory to smelt the plates\n    :param input_coal: The number of coal to insert into the furnace\n    :param input_ore: The number of ore to insert into the furnace\n    :param furnace: The furnace entity to use for smelting\n    :param ore_type: The type of ore to smelt (IronOre or CopperOre)\n    :param output_plate: The number of plates to extract from the furnace\n    :return: None as the plates will be in inventory\n    """\n    # [PLANNING]\n    # 1. Check if we have enough ore and coal in the inventory\n    # 2. Insert coal and ore into the furnace\n    # 3. Wait for smelting to complete\n    # 4. Extract the plates from the furnace\n    # 5. Verify that we have the expected number of plates in our inventory\n    # [END OF PLANNING]\n\n    # Step 1: Check inventory\n    inventory = inspect_inventory()\n    assert inventory.get(ore_type, 0) >= input_ore, f"Not enough {ore_type.name} in inventory. Required: {input_ore}, Available: {inventory.get(ore_type, 0)}"\n    assert inventory.get(Prototype.Coal, 0) >= input_coal, f"Not enough coal in inventory. Required: {input_coal}, Available: {inventory.get(Prototype.Coal, 0)}"\n\n    # Step 2: Insert coal and ore into the furnace\n    insert_item(Prototype.Coal, furnace, input_coal)\n    insert_item(ore_type, furnace, input_ore)\n\n    # Step 3: Wait for smelting to complete\n    # Assuming it takes about 3.5 seconds to smelt one ore\n    smelting_time = 3.5 * input_ore\n    sleep(int(smelting_time) + 1)  # Add 1 second as buffer\n\n    # Step 4: Extract the plates from the furnace\n    plate_type = Prototype.IronPlate if ore_type == Prototype.IronOre else Prototype.CopperPlate\n    extract_item(plate_type, furnace.position, output_plate)\n\n    # Step 5: Verify the number of plates in our inventory\n    final_inventory = inspect_inventory()\n    plates_in_inventory = final_inventory.get(plate_type, 0)\n    assert plates_in_inventory >= output_plate, f"Failed to smelt enough plates. Expected at least {output_plate}, but got {plates_in_inventory}"\n\n    print(f"Successfully smelted {output_plate} {plate_type.name}.")\n'
                    # replacec the first [SUBFUNCTION] tag with [SYNTHESISED]
                    function = function.replace('[SUBFUNCTION]', '"""[SYNTHESISED]', 1)
                    function = function.replace('[END OF SUBFUNCTION]', '[END OF SYNTHESISED]"""', 1)
                    functions_to_process.append(generated_subfunction)
                    plans.append(plan)
                completed_functions.append(function)


            yield {
                "snippet_name": name,
                "snippets": completed_functions,
                "objective": objective_str,
                "mining_setup": mining_setup,
                "inventory": inventory,
                "plans": plans
                #"test": test,
            }

def save_gold_skills_into_db():
    db = SkillsDB()
    db.delete_all_skills()
    skills = db.get_all_skills()
    names = [skill['name'] for skill in skills]
    examples_folder = r"skills/rag_functions"
    # get all folders in examples_path
    examples = os.listdir(examples_folder)
    for example in examples:
        if example.startswith("exclude"):
            continue
        # read in details
        folder_path = f"{examples_folder}/{example}"
        with open(f"{folder_path}/details.json", "r") as f:
            details = json.load(f)
        # read in the snippet
        with open(f"{folder_path}/snippet.py", "r") as f:
            snippet = f.read()
        
        name = details["name"]
        if name in names:
            continue
        implementation = snippet
        # get the signature thats between first and second """
        signature = re.search(r'"""(.*?)"""', snippet, re.DOTALL).group(1)
        signature = signature.strip()
        description = signature
        dependencies = []
        implementation_model = "gold_standard"
        db.save_function(name = name, 
                    description = description, 
                    implementation = implementation, 
                    dependencies = dependencies, 
                    implementation_model = implementation_model,
                    signature = signature)

def evaluate_a_skill(folder_path):
    # readinthe full_snippet.py
    with open(f"{folder_path}/full_snippet.py", "r") as f:
        full_snippet = f.read()
    
    # read in the details.json
    with open(f"{folder_path}/details.json", "r") as f:
        details = json.load(f)

    inventory = details["inventory"]
    instance = FactorioInstance(address='localhost',
                                bounding_box=200,
                                tcp_port=27015,
                                fast=True,
                                #cache_scripts=False,
                                inventory=inventory)

    # evaluate the skill
    score, goal, result = instance.eval_with_error(full_snippet, timeout=240)
    print(result)


if __name__ == "__main__":
    folder_path = r"skills\rag_skills\_create_electric_coal_mine"
    evaluate_a_skill(folder_path)
    #main()
    #save_gold_skills_into_db()

    sampler = FactorioLLMSampler(model = "gpt-4o")

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

    inventory = {
        'iron-plate': 20,
        'coal': 20,
        'copper-plate': 20,
        'stone-furnace': 3,
        'iron-ore':10
    }
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

iron_position = nearest(Resource.Stone)
move_to(iron_position)
print(f"Moved to iron patch at {iron_position}")
harvest_resource(iron_position, 20)

craft_item(Prototype.StoneFurnace, 3)

# 1. Place a stone furnace
stone_furnace = place_entity(Prototype.StoneFurnace, Direction.UP, iron_position)
assert stone_furnace is not None, "Failed to place stone furnace"

insert_item(Prototype.Coal, stone_furnace, 5)
insert_item(Prototype.IronOre, stone_furnace, 5)
sleep(2)

furnaces = inspect_entities().get_entities(Prototype.StoneFurnace)
print(furnaces)
furnace = furnaces[0]
insert_item(Prototype.Coal, furnace, 5)
"""

    #score, goal, result = instance.eval_with_error(test_string, timeout=60)
    # Load objectives from file
    #objectives_file = "skills\objectives_rag.txt"
    #if os.path.exists(objectives_file):
    #    objectives = sampler.load_objectives(objectives_file)
    #else:
    #    print(f"Objectives file '{objectives_file}' not found. Please create it and add objectives.")
    #    exit(1)


    
    objectives_folder = "skills\objectives\Group_5_create_automatic_burner_mines"
    #read in details.json
    with open(f"{objectives_folder}/details.json", "r") as f:
        details = json.load(f)
    
    # read in starting_snippet.py if it exists
    try:
        with open(f"{objectives_folder}/starting_snippet.py", "r") as f:
            starting_snippet = f.read()
    except:
        starting_snippet = ""
    
    mining_setup = details["mining_setup"]
    objectives = details["objectives"]

    inventory = {
        'iron-plate': np.random.randint(0, 20),
        'coal': np.random.randint(0, 10),
        'copper-plate': np.random.randint(0, 20),
        'stone-furnace': np.random.randint(0, 2),
        'iron-ore':np.random.randint(0, 10),
        "coppper-ore":np.random.randint(0, 10),
    }
    for obj_idx, objective in enumerate(objectives):

            curriculum_item = next(sampler.stream_curriculum([objective], objective["inventory"], mining_setup))
            snippet_name = curriculum_item['snippet_name']
            final_snippet = "from factorio_instance import *\n\n"
            for snippet in curriculum_item['snippets'][::-1]:
                final_snippet += snippet + "\n\n###FUNC SEP\n\n"
            final_snippet += f"{snippet_name}()"
            # START OF TESTING
            #final_snippet = 'from factorio_instance import *\n\n\ndef connect_drill_to_chest(drill: Entity, chest: Entity):\n    """\n    Objective: Connect the drill to the chest using transport belts and a burner inserter\n    Mining setup: Drill and chest are placed on the map\n    Inventory: We have transport belts and a burner inserter\n    :param drill: The burner mining drill entity\n    :param chest: The wooden chest entity\n    :return: None\n    """\n    # [PLANNING]\n    # 1. Place a burner inserter next to the chest\n    # 2. Rotate the inserter to face the chest\n    # 3. Fuel the inserter with coal\n    # 4. Connect the drill to the inserter using transport belts\n    # 5. Verify the connection\n    # [END OF PLANNING]\n\n    print(f"Starting to connect drill at {drill.position} to chest at {chest.position}")\n    print(f"Current inventory: {inspect_inventory()}")\n\n    # Step 1: Place a burner inserter next to the chest\n    inserter = place_entity_next_to(Prototype.BurnerInserter, chest.position, direction=Direction.UP, spacing=0)\n    assert inserter, "Failed to place burner inserter"\n    print(f"Placed burner inserter at {inserter.position}")\n\n    # Step 2: Rotate the inserter to face the chest\n    inserter = rotate_entity(inserter, Direction.DOWN)\n    print(f"Rotated burner inserter to face the chest")\n\n    # Step 3: Fuel the inserter with coal\n    coal_count = inspect_inventory()[Prototype.Coal]\n    assert coal_count > 0, "No coal in inventory to fuel the inserter"\n    insert_item(Prototype.Coal, inserter, quantity=min(5, coal_count))\n    print(f"Fueled burner inserter with coal")\n\n    # Step 4: Connect the drill to the inserter using transport belts\n    belts = connect_entities(drill.drop_position, inserter.pickup_position, Prototype.TransportBelt)\n    assert belts, "Failed to place transport belts"\n    print(f"Connected drill to inserter with {len(belts)} transport belts")\n\n    # Step 5: Verify the connection\n    inspection = inspect_entities(drill.position, radius=20)\n    \n    # Check if the drill is present\n    assert any(e.name == drill.name for e in inspection.entities), "Drill not found in inspection"\n    \n    # Check if the chest is present\n    assert any(e.name == chest.name for e in inspection.entities), "Chest not found in inspection"\n    \n    # Check if the inserter is present\n    assert any(e.name == inserter.name for e in inspection.entities), "Inserter not found in inspection"\n    \n    # Check if transport belts are present\n    assert any(e.name == Prototype.TransportBelt.value[0] for e in inspection.entities), "Transport belts not found in inspection"\n\n    print("Successfully connected drill to chest using transport belts and a burner inserter")\n    print(f"Final inventory: {inspect_inventory()}")\n\n\n\n###FUNC SEP\n\n\ndef gather_resources():\n    """\n    Objective: Gather iron ore, wood, stone, and coal\n    Mining setup: No entities on the map\n    Inventory: Empty inventory\n    :return: None (resources will be in the inventory)\n    """\n    # [PLANNING]\n    # 1. Find and mine iron ore\n    # 2. Find and harvest wood\n    # 3. Find and mine stone\n    # 4. Find and mine coal\n    # 5. Verify that we have gathered all required resources\n    # [END OF PLANNING]\n\n    # 1. Find and mine iron ore\n    iron_position = nearest(Resource.IronOre)\n    assert iron_position, "No iron ore found nearby"\n    move_to(iron_position)\n    print(f"Moving to iron ore patch at {iron_position}")\n    \n    iron_mined = harvest_resource(iron_position, quantity=20)\n    assert iron_mined == 20, f"Failed to mine enough iron ore. Expected 20, but got {iron_mined}"\n    print(f"Mined {iron_mined} iron ore")\n\n    # 2. Find and harvest wood\n    wood_position = nearest(Resource.Wood)\n    assert wood_position, "No wood found nearby"\n    move_to(wood_position)\n    print(f"Moving to wood patch at {wood_position}")\n    \n    wood_harvested = harvest_resource(wood_position, quantity=20)\n    assert wood_harvested == 20, f"Failed to harvest enough wood. Expected 20, but got {wood_harvested}"\n    print(f"Harvested {wood_harvested} wood")\n\n    # 3. Find and mine stone\n    stone_position = nearest(Resource.Stone)\n    assert stone_position, "No stone found nearby"\n    move_to(stone_position)\n    print(f"Moving to stone patch at {stone_position}")\n    \n    stone_mined = harvest_resource(stone_position, quantity=20)\n    assert stone_mined == 20, f"Failed to mine enough stone. Expected 20, but got {stone_mined}"\n    print(f"Mined {stone_mined} stone")\n\n    # 4. Find and mine coal\n    coal_position = nearest(Resource.Coal)\n    assert coal_position, "No coal found nearby"\n    move_to(coal_position)\n    print(f"Moving to coal patch at {coal_position}")\n    \n    coal_mined = harvest_resource(coal_position, quantity=20)\n    assert coal_mined == 20, f"Failed to mine enough coal. Expected 20, but got {coal_mined}"\n    print(f"Mined {coal_mined} coal")\n\n    # 5. Verify that we have gathered all required resources\n    inventory = inspect_inventory()\n    print(f"Current inventory: {inventory}")\n\n    assert inventory[Resource.IronOre] >= 20, f"Not enough iron ore in inventory. Expected at least 20, but got {inventory[Resource.IronOre]}"\n    assert inventory[Resource.Wood] >= 20, f"Not enough wood in inventory. Expected at least 20, but got {inventory[Resource.Wood]}"\n    assert inventory[Resource.Stone] >= 20, f"Not enough stone in inventory. Expected at least 20, but got {inventory[Resource.Stone]}"\n    assert inventory[Resource.Coal] >= 20, f"Not enough coal in inventory. Expected at least 20, but got {inventory[Resource.Coal]}"\n\n    print("Successfully gathered all required resources!")\n\n\n###FUNC SEP\n\n\ndef create_iron_mine():\n    """\n    Objective: Create an automated iron mine that mines iron ore to a chest further away and left from it.\n    Mining setup: There are no entities on the map\n    Inventory: We start with an empty inventory\n    """\n    # [PLANNING]\n    # 1. Gather necessary resources (iron, wood, stone, coal)\n    # 2. Craft required items (burner mining drill, wooden chest, transport belts, burner inserter)\n    # 3. Find an iron ore patch\n    # 4. Place the burner mining drill on the iron ore patch\n    # 5. Place the wooden chest further away and to the left of the drill\n    # 6. Connect the drill to the chest using transport belts and a burner inserter\n    # 7. Fuel the mining drill and inserter\n    # 8. Wait for the system to produce iron ore\n    # 9. Check if the chest contains iron ore\n    # [END OF PLANNING]\n\n    # Step 1: Gather resources\n    print("Gathering resources...")\n    """[SYNTHESISED]\n    Name: gather_resources\n    Objective: Gather iron ore, wood, stone, and coal\n    Mining setup: No entities on the map\n    Inventory: Empty inventory\n    :return: None (resources will be in the inventory)\n    [END OF SYNTHESISED]"""\n    gather_resources()\n    \n    print(f"Current inventory after gathering resources: {inspect_inventory()}")\n\n    # Step 2: Craft required items\n    print("Crafting required items...")\n    craft_item(Prototype.BurnerMiningDrill, 1)\n    craft_item(Prototype.WoodenChest, 1)\n    craft_item(Prototype.TransportBelt, 10)\n    craft_item(Prototype.BurnerInserter, 1)\n    \n    print(f"Current inventory after crafting: {inspect_inventory()}")\n\n    # Step 3: Find an iron ore patch\n    iron_position = nearest(Resource.IronOre)\n    print(f"Found iron ore patch at {iron_position}")\n    move_to(iron_position)\n\n    # Step 4: Place the burner mining drill\n    drill = place_entity(Prototype.BurnerMiningDrill, Direction.DOWN, iron_position)\n    assert drill, "Failed to place burner mining drill"\n    print(f"Placed mining drill at {drill.position}")\n\n    # Step 5: Place the wooden chest\n    chest_position = Position(x=drill.position.x - 5, y=drill.position.y + 5)  # Further away and to the left\n    move_to(chest_position)\n    chest = place_entity(Prototype.WoodenChest, Direction.UP, chest_position)\n    assert chest, "Failed to place wooden chest"\n    print(f"Placed wooden chest at {chest.position}")\n\n    # Step 6: Connect the drill to the chest\n    print("Connecting drill to chest...")\n    """[SYNTHESISED]\n    Name: connect_drill_to_chest\n    Objective: Connect the drill to the chest using transport belts and a burner inserter\n    Mining setup: Drill and chest are placed on the map\n    Inventory: We have transport belts and a burner inserter\n    :param drill: The burner mining drill entity\n    :param chest: The wooden chest entity\n    :return: None\n    [END OF SYNTHESISED]"""\n    connect_drill_to_chest(drill=drill, chest=chest)\n\n    # Step 7: Fuel the mining drill and inserter\n    print("Fueling mining drill and inserter...")\n    insert_item(Prototype.Coal, drill, quantity=5)\n    \n    # Find the inserter (it should be next to the chest)\n    entities_near_chest = inspect_entities(chest.position, radius=2).entities\n    inserter = next((e for e in entities_near_chest if e.name == Prototype.BurnerInserter.value[0]), None)\n    assert inserter, "Failed to find the burner inserter"\n    insert_item(Prototype.Coal, inserter, quantity=5)\n\n    # Step 8: Wait for the system to produce iron ore\n    print("Waiting for iron ore production...")\n    sleep(30)  # Wait for 30 seconds\n\n    # Step 9: Check if the chest contains iron ore\n    chest_inventory = inspect_inventory(chest)\n    iron_ore_in_chest = chest_inventory.get(Prototype.IronOre, 0)\n    assert iron_ore_in_chest > 0, f"No iron ore was produced. Chest inventory: {chest_inventory}"\n    print(f"Success! The chest contains {iron_ore_in_chest} iron ore.")\n\n    print("Automated iron mine created successfully!")\n\n\n###FUNC SEP\n\ncreate_iron_mine()'
            #curriculum_item = {}
            #snippet_name = "test"
            #curriculum_item["objective"] = "Name: ###create_iron_mine###. Objective: We need create an automated iron mine that mines iron ore with a burner mining drill to a chest further away and down from it. The final setup should be checked by looking if the chest has iron ore in it. Mining setup: There are no entities on the map"
            # END OF TESTING
            print(f"Objective: {curriculum_item['objective']}")
            print("Snippet name: " + snippet_name)
            print("\n" + "=" * 50 + "\n")
            correction_history = []
            #if not is_valid_python(final_snippet):
            #    continue

            snippet = final_snippet

            max_attempts = 1
            snippet_passed = False

            for attempt in range(max_attempts):
                instance.reset()
                instance.initial_inventory = objective["inventory"]        
                instance.reset()
                # run starting snippet
                score, goal, result = instance.eval_with_error(starting_snippet, timeout=60)

                try:
                    # Create a StringIO object to capture the output
                    captured_output = io.StringIO()
                    # Save the current stdout so we can revert back later
                    sys_stdout = sys.stdout
                    # Redirect stdout to the StringIO object
                    sys.stdout = captured_output
                    score, goal, result = instance.eval_with_error(snippet, timeout=240)
                    
                    if 'error' in result.lower() or 'assertion' in result.lower():
                        raise Exception(result)

                    snippet_passed = True
                    break
                except Exception as e:
                    # Get all output from the StringIO object
                    captured_output.seek(0)  # Go to the start of StringIO to read from beginning
                    output_list = captured_output.read().splitlines()
                    # Revert sys.stdout to its original state
                    sys.stdout = sys_stdout
                    print(e)
                    print(output_list)
                    # get the message of e
                    message = str(e)
                    # get everything between Get the part that follows the regex Error at lines x:
                    match = re.search(r'Error at lines (\d+)-', message)
                    match = False
                    if match:
                        try:
                            line_number = int(match.group(1))
                            print(f'The first line number where the error occurred is: {line_number}')
                            subfunction_correction= True
                        except:
                            print('Line number not found in the message.')
                            subfunction_correction = False
                    else:
                        print('Line number not found in the message.')
                        subfunction_correction = False
                    if attempt < max_attempts - 1:
                        if  subfunction_correction:
                            # split the snippet into functions using the FUNC SEP tag
                            functions = snippet.split("###FUNC SEP")
                            line_span = 0
                            for func_idx, function in enumerate(functions):
                                if line_span <= line_number:
                                    line_span += function.count("\n")
                                else:
                                    break
                            # get the function that caused the error
                            function = functions[func_idx - 1]
                            pass
                        else:
                            print(f"{snippet_name} - Snippet failed on attempt {attempt + 1}. `{str(e)}` Attempting to correct...")
                            corrected_snippet = sampler.correct_policy_snippet(
                                objective = curriculum_item['objective'],
                                last_executed_policy  = snippet,
                                error_message = str(e),
                                correction_history=[],
                                inventory = inventory,
                                game_logs = output_list
                            )
                            corrected_snippet = corrected_snippet.split("```")[1].lstrip('python\n')
                            snippet = textwrap.dedent(corrected_snippet)
                            correction_history.append({"snippet": snippet, "error": str(e)})
                    else:
                        print(f"{snippet_name} - Snippet failed after {max_attempts} attempts. Moving to next objective.")
            sys.stdout = sys_stdout
            # Save results and update files
            folder_name = snippet_name if snippet_passed else f"_{snippet_name}"
            folder_path = f"skills/rag_skills/{folder_name.strip()}"
            # check if the folder existss
            if os.path.exists(folder_path):
                # start adding numbers to the folder name
                i = 1
                new_folder_path = f"{folder_path}_{i}"
                while os.path.exists(new_folder_path):
                    i += 1
                    new_folder_path = f"{folder_path}_{i}"
                folder_path = new_folder_path
            
            os.makedirs(folder_path, exist_ok=True)
            with open(f"{folder_path}/full_snippet.py", "w") as f:
                f.write(snippet)

            # split the snippet into functions using the FUNC SEP tag
            functions = snippet.split("###FUNC SEP")[:-1]
            for func_idx, function in enumerate(functions):
                function = function.replace("###FUNC SEP", "").replace("from factorio_instance import *", "").strip()
                with open(f"{folder_path}/subsnippet_{func_idx}.py", "w") as f:
                    f.write(function)

            details = {
                "name": snippet_name,
                "objective": curriculum_item['objective'],
                "corrections": correction_history,
                "token_count": sampler.token_count,
                "cost": sampler.cost,
                "snippet_passed": snippet_passed,
                "inventory": objective["inventory"],
                "plans": curriculum_item['plans'],
                "mining_setup": curriculum_item['mining_setup']
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
